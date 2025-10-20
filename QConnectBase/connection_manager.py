#  Copyright 2020-2023 Robert Bosch GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# *******************************************************************************
#
# File: connection_manager.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / May 2021
#
# Description:
#   Provide the manager class for managing all connection.
#
# History:
#
# 12.05.2021 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from QConnectBase.utils import *
from QConnectBase.connection_base import ConnectionBase
from robot.libraries.BuiltIn import BuiltIn
from os.path import dirname
from QConnectBase.utils import DictToClass
from robot.api.deco import keyword
from robot.utils import timestr_to_secs
import os
import importlib
import pkgutil
import QConnectBase.constants as constants
import site
import inspect
import importlib.util
import pkgutil
import sys


class InputParam(DictToClass):
   @classmethod
   def get_attr_list(cls):
      return [k for k, v in cls.__dict__.items() if not k.startswith('__')]


class ConnectParam(InputParam):
   """
Class for storing parameters for connect action.
   """
   id = 0
   conn_name = 'default_conn'
   conn_type = 'TCPIP'
   conn_mode = ''
   conn_conf = {}
   exclude_list = ['conn_conf']

   def __init__(self, **dictionary):
      super(InputParam, self).__init__(**dictionary)
      if self.conn_name == 'default_conn':
         self.conn_name += str(ConnectParam.id)
         ConnectParam.id += 1


class SendCommandParam(InputParam):
   """
Class for storing parameters for send command action.
   """
   conn_name = 'default_conn'
   command = ''
   element_def = {}
   args = None


class VerifyParam(InputParam):
   """
Class for storing parameters for verify action.
   """
   conn_name = 'default_conn'
   search_pattern = None
   timeout = 5
   match_try = 1
   fetch_block = False
   eob_pattern = '.*'
   filter_pattern = '.*'
   send_cmd = ''
   element_def = {}
   args = None


class ConnectionManager(Singleton):
   """
Class to manage all connections.
   """
   ROBOT_LIBRARY_SCOPE = 'GLOBAL'
   ROBOT_AUTO_KEYWORDS = False
   LIBRARY_EXTENSION_PREFIX = 'robotframework_qconnect'
   LIBRARY_EXTENSION_PREFIX2 = 'QConnect'
   DEFAULT_VERIFY_TIMEOUT = 5
   DEFAULT_EMERGENCY_TIMEOUT = 60 * 30

   id = 0

   def __init__(self):
      """
Constructor for ConnectionManager class.
      """
      # Avoid re-initialize when calling the singleton ConnectionManager class
      if getattr(self, "_initialized", False):
         return
      self._initialized = True

      self.connection_manage_dict = {}
      main_lib_path = dirname(os.path.realpath(__file__))
      site_package_dirs = site.getsitepackages()
      extension_lib_paths = []
      for site_package_dir in site_package_dirs:
         try:
            walk_iter = os.walk(site_package_dir)
            curr_dir, subdirs, files = next(walk_iter)
            lib_path = [constants.SLASH.join([curr_dir, lib_ext]) for lib_ext in subdirs
                        if (ConnectionManager.LIBRARY_EXTENSION_PREFIX in lib_ext) or lib_ext.startswith(ConnectionManager.LIBRARY_EXTENSION_PREFIX2)]
            extension_lib_paths.extend(lib_path)
         except (StopIteration, OSError):
            # Skip if site package directory doesn't exist or is inaccessible
            continue

      all_libs = [main_lib_path]
      all_libs.extend(extension_lib_paths)
      all_libs = list(set(all_libs))
      for path in all_libs:
         if path not in sys.path:
            sys.path.append(path)
      for module_loader, name, is_pkg in pkgutil.walk_packages(all_libs):
         # noinspection PyBroadException
         try:
            if not is_pkg and not name.startswith("setup"):
               importlib.import_module(name)
            else:
               # _module = module_loader.find_module(name).load_module(name)
               spec = importlib.util.find_spec(name)
               if spec and spec.loader:
                  module = importlib.util.module_from_spec(spec)
                  spec.loader.exec_module(module)
               else:
                  print(f"⚠️ Could not load module: {name}")
         except Exception as _ex:
            pass

      supported_connection_classes_list = Utils.get_all_descendant_classes(ConnectionBase)
      self.supported_connection_classes_dict = {cls._CONNECTION_TYPE: cls for cls in supported_connection_classes_list}

      self.set_default_emergency_timeout(ConnectionManager.DEFAULT_EMERGENCY_TIMEOUT)
      self.set_default_verify_timeout(ConnectionManager.DEFAULT_VERIFY_TIMEOUT)
      self.ROBOT_LIBRARY_LISTENER = self
      self.ROBOT_LISTENER_API_VERSION = 3


   def __del__(self):
      """
Destructor for ConnectionManager class.

**Returns:**
         None.
      """
      pass
      # self.quit()

   def end_suite(self, data, result):
      self.quit()

   def quit(self):
      """
Quit connection manager.

**Returns:**

(*no returns*)
      """
      for connection in self.connection_manage_dict.values():
         connection.quit()
      self.connection_manage_dict.clear()

   def add_connection(self, name, conn):
      """
Add a connection to managed dictionary.

**Arguments:**

* ``name``

  / *Condition*: required / *Type*: str /

  Connection's name.

* ``conn``

  / *Condition*: required / *Type*: socket.socket /

  Connection object.

**Returns:**

(*no returns*)
      """
      if name not in self.connection_manage_dict.keys():
         self.connection_manage_dict[name] = conn

   def remove_connection(self, connection_name):
      """
Remove a connection by name.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Connection's name.

**Returns:**

(*no returns*)
      """
      if connection_name in self.connection_manage_dict.keys():
         del self.connection_manage_dict[connection_name]


   def get_connection_by_name(self, connection_name):
      """
Get an exist connection by name.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Connection's name.

**Returns:**

* ``conn``

  / *Type*: socket.socket /

  Connection object.
      """
      conn = None
      if connection_name in self.connection_manage_dict.keys():
         conn = self.connection_manage_dict[connection_name]
      return conn

   @keyword
   def disconnect(self, conn_name):
      """
Keyword for disconnecting a connection by name.

**Arguments:**

* ``conn_name``

  / *Condition*: required / *Type*: str /

  Connection's name.

**Returns:**

(*no returns*)
      """
      if conn_name in self.connection_manage_dict.keys():
         self.connection_manage_dict[conn_name].quit()
         del self.connection_manage_dict[conn_name]
      else:
         raise Exception(f"Invalid operation: Attempted to disconnect '{conn_name}', but no such connection exists.")

   @keyword
   def connect(self, conn_name='default_conn', conn_conf=None, conn_type='', conn_mode=''):
      """
Making a connection.

**Arguments:**

* ``conn_name``

  / *Condition*: optional / *Type*: str / *Default*: 'default_conn' /

  Name of connection. It can be specified in ``conn_conf`` dictionary.

* ``conn_conf``

  / *Condition*: optional / *Type*: dictionary / *Default*: None /

  A dictionary containing configurations for the connection.

  It must include ``conn_type``, and optionally ``conn_mode`` and other connection-specific fields (depending on type).

  Example ``conn_conf`` for ``TCPIPClient``:

  ```
  {
    "conn_type": "TCPIPClient",
    "address": [server host], # Optional. Default value is "localhost".
    "port": [server port]     # Optional. Default value is 1234.
  }
  ```

* ``conn_type`` (deprecated)

  / *Condition*: optional / *Type*: str / *Default*: 'TCPIPClient' /

  Type of connection. It can be specified in ``conn_conf`` dictionary.

  Supported connection types:
  - ``TCPIPClient``: Create a Raw TCP/IP connection to TCP Server.
  - ``SSHClient``: Create a client connection to a SSH server.
  - ``SerialClient``: Create a client connection via Serial Port.

  In addition to the connection types listed above, other types are also available through classes inheriting from ``QConnectBase``.

* ``conn_mode`` (deprecated)

  / *Condition*: optional / *Type*: str / *Default*: '' /

  Connection mode. It can be specified in ``conn_conf`` dictionary.

**Returns:**

(*no returns*)
      """
      if not conn_conf:
         if not conn_type:
            # conn_conf is required for new version which
            # conn_type (and conn_mode) is specified with conn_conf dictionary
            raise Exception("The configurations 'conn_conf' for connection have to be provided")
         else:
            # to be compatible with previous version
            # conn_type is provided and default conn_conf is used if not provided
            conn_conf = {}
      else:
         if not isinstance(conn_conf, dict):
            raise Exception("The configurations 'conn_conf' must be a dictionary")

      if 'conn_type' in conn_conf:
         if conn_conf['conn_type'] != conn_type and conn_type != '':
            raise Exception(constants.String.CONNECTION_TYPE_CONFUSED % (conn_type, conn_conf['conn_type']))
         else:
            conn_type = conn_conf['conn_type']
            conn_conf.pop('conn_type', None)

      if conn_type == '':
         conn_type = "TCPIPClient"

      conn_conf['connection_name'] = conn_name

      if conn_type not in self.supported_connection_classes_dict.keys():
         raise Exception(constants.String.CONNECTION_TYPE_UNSUPPORTED %
                         (conn_type, ', '.join(sorted(k for k in self.supported_connection_classes_dict.keys() if not k.endswith('Base')))))

      if 'conn_mode' in conn_conf:
         if conn_conf['conn_mode'] != conn_mode and conn_mode != '':
            raise Exception(constants.String.CONNECTION_MODE_CONFUSED % (conn_mode, conn_conf['conn_mode']))
         else:
            conn_mode = conn_conf['conn_mode']
            conn_conf.pop('conn_mode', None)

      if conn_name in self.connection_manage_dict.keys():
         raise AssertionError(constants.String.CONNECTION_NAME_EXIST % conn_name)

      if conn_name == 'default_conn':
         conn_name += str(ConnectionManager.id)
         ConnectionManager.id += 1

      try:
         connection_obj = self.supported_connection_classes_dict[conn_type](conn_mode, conn_conf)
      except Exception as ex:
         # BuiltIn().log("Unable to create connection. Exception: %s" % ex, constants.LOG_LEVEL_ERROR)
         raise Exception("Connection Error: %s" % ex)

      if connection_obj is not None:
         setattr(connection_obj, 'connection_name', conn_name)
         if hasattr(connection_obj, "real_obj"):
            setattr(connection_obj.real_obj, 'connection_name', conn_name)
         self.add_connection(conn_name, connection_obj)

      try:
         connection_obj.connect()
      except Exception as ex:
         self.remove_connection(conn_name)
         # BuiltIn().log("Unable to create connection. Exception: %s" % ex, constants.LOG_LEVEL_ERROR)
         raise Exception("Connection Error: %s" % ex)

   @keyword
   def send_command(self, conn_name, command, **kwargs):
      """
Send command to a connection.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Name of connection.

* ``command``

  / *Condition*: required / *Type*: str /

  Command to be sent.

* ``kwargs``

  / *Condition*: optional / *Type*: dict / *Default*: {} /

  The optional arguments depend on the connection type used in the '``connect``' keyword.

**Returns:**

(*no returns*)
      """
      if conn_name not in self.connection_manage_dict.keys():
         raise AssertionError("The '%s' connection hasn't been established. Please connect first." % conn_name)
      connection_obj = self.connection_manage_dict[conn_name]
      try:
         connection_obj.send_obj(command, **kwargs)
         BuiltIn().log(f"command '{command}' is sent to '{conn_name}'", constants.LOG_LEVEL_INFO)
      except Exception as ex:
         raise Exception("Unable to send command to '%s' connection. Exception: %s" % (conn_name, str(ex)))

   @keyword
   def transfer_file(self, conn_name, src, dest, type):
      """
DEPRECATED!! Use keyword transfer_item instead.
Transfer file from local to remote and vice versa.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Name of connection.

* ``src``

  / *Condition*: required / *Type*: str /

  Source file path.

* ``dest``

  / *Condition*: required / *Type*: str /

  Destination file path.

* ``type``

  / *Condition*: required / *Type*: str /

  Transfer file type.

      '``get``' - Copy a remote file from the SFTP server to the local host.

      '``put``' - Copy a local file to the SFTP server.

**Returns:**

(*no returns*)
      """
      if conn_name not in self.connection_manage_dict.keys():
         raise AssertionError(f"The '{conn_name}' connection  hasn't been established. Please connect first.")
      connection_obj = self.connection_manage_dict[conn_name]
      try:
         connection_obj.transfer_file(src, dest, type)
      except AttributeError as attrErr:
         raise Exception(f"'{connection_obj._CONNECTION_TYPE}' connection type has not been supported for transferring file.")
      except Exception as ex:
         raise Exception(f"Unable to transfer file to '{conn_name}' connection. Exception: '{ex}'")

   @keyword
   def transfer_item(self, conn_name, src, dest, type):
      """
Transfer item from local to remote and vice versa.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Name of connection.

* ``src``

  / *Condition*: required / *Type*: str /

  Source item path.

* ``dest``

  / *Condition*: required / *Type*: str /

  Destination item path.

* ``type``

  / *Condition*: required / *Type*: str /

  Transfer item type.

      '``get``' - Copy a remote item from the SFTP server to the local host.

      '``put``' - Copy a local item to the SFTP server.

**Returns:**

(*no returns*)
      """
      if conn_name not in self.connection_manage_dict.keys():
         raise AssertionError(f"The '{conn_name}' connection  hasn't been established. Please connect first.")
      connection_obj = self.connection_manage_dict[conn_name]
      try:
         connection_obj.transfer_item(src, dest, type)
      except AttributeError as attrErr:
         raise Exception(f"'{connection_obj._CONNECTION_TYPE}' connection type has not been supported for transferring item.")
      except Exception as ex:
         raise Exception(f"Unable to transfer item to '{conn_name}' connection. Exception: '{ex}'")


   @keyword
   def execute_script(self, conn_name, script_path):
      """
Executes a script file by sending commands to a device through the provided connection.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Name of connection.

* ``script_path``

  / *Condition*: required / *Type*: str /

  Script file path.

**Returns:**

(*no returns*)
      """
      if conn_name not in self.connection_manage_dict.keys():
         raise AssertionError("The '%s' connection hasn't been established. Please connect first." % conn_name)
      connection_obj = self.connection_manage_dict[conn_name]
      try:
         connection_obj.execute_script(script_path)
      except AttributeError as attrErr:
         test = inspect.getfile(connection_obj.__class__)
         raise Exception("'%s' connection type has not been supported for execute script." % connection_obj._CONNECTION_TYPE)
      except Exception as ex:
         raise Exception("Unable to execute script path '%s'. Exception: %s" % (script_path, str(ex)))

   @keyword
   def set_default_verify_timeout(self, time_out):
      """
Set the default verify timeout value for the connection.

Supports flexible input formats such as:
- Duration with units (e.g. '1h 10s', '2m30s', '500ms')
- HH:MM:SS format (e.g. '01:00:10' for 1 hour, 0 minutes, 10 seconds)
- Plain numeric values (e.g. '42') interpreted as seconds

**Arguments:**

* ``time_str``

  / *Condition*: required / *Type*: str or float or int /

  A string representing the duration. Units supported include:
    - ``h``  for hours
    - ``m``  for minutes (or ``ms`` for milliseconds)
    - ``s``  for seconds
    - ``ms`` for milliseconds
  If no unit is specified, the value is interpreted as seconds.
      """
      time_second = timestr_to_secs(time_out)
      if time_second > self.default_emergency_timeout:
         raise Exception(f"Default verify timeout must not exceed the emergency timeout of {self.default_emergency_timeout} seconds!")
      self.default_verify_timeout = time_out

   @keyword
   def set_default_emergency_timeout(self, time_out):
      """
Set the default emergency timeout value for the connection.

Supports flexible input formats such as:
- Duration with units (e.g. '1h 10s', '2m30s', '500ms')
- HH:MM:SS format (e.g. '01:00:10' for 1 hour, 0 minutes, 10 seconds)
- Plain numeric values (e.g. '42') interpreted as seconds

**Arguments:**

* ``time_out``

  / *Condition*: required / *Type*: str or float or int /

  A string representing the duration. Units supported include:
    - ``h``  for hours
    - ``m``  for minutes (or ``ms`` for milliseconds)
    - ``s``  for seconds
    - ``ms`` for milliseconds
  If no unit is specified, the value is interpreted as seconds.
      """
      time_second = timestr_to_secs(time_out)
      if time_second > (60 * 60) or time_second < 60:
         raise Exception(f"Emergency timeout must be >= 1 minute and <= 1 hour!")
      self.default_emergency_timeout = time_second

   @keyword
   def verify(self, conn_name, search_pattern='.*', timeout=5, match_try=1, fetch_block=False, eob_pattern='.*', filter_pattern='.*', send_cmd='', **kwargs):
      """
Verify a pattern from connection response after sending a command.

**Arguments:**

* ``conn_name``

  / *Condition*: required / *Type*: str /

  Name of connection.

* ``search_pattern``

  / *Condition*: optional / *Type*: str / *Default*: .* /

  Expectation expressed as a **regular expression pattern** (more robust than a plain string comparison).

  It will match:
  - a single line by default (``fetch_block`` not used)
  - multiple lines if ``fetch_block`` is enabled

  Default value: ``.*``, which means "match any character (``.``) repeated zero or more times (``*``)".

  In practice, this will always match the response, regardless of its content, unless you specify a stricter pattern.

* ``timeout``

  / *Condition*: optional / *Type*: float / *Default*: 5 /

  Timeout parameter specified as a floating point number in the unit 'seconds'.

* ``match_try``

  / *Condition*: optional / *Type*: int / *Default*: 1 /

  Number of time for trying to match the pattern.

* ``fetch_block``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  Determine if 'fetch block' feature is used.

  If ``True``, every single line of received message will be put into a block until a line match ``eob_pattern`` pattern.

* ``eob_pattern``

  / *Condition*: optional / *Type*: str / *Default*: '.*' /

  Applicable only when ``fetch_block`` is ``True``.

  Regular expression for matching the endline when using ``fetch_block``.

* ``filter_pattern``

  / *Condition*: optional / *Type*: str / *Default*: '.*' /

  Applicable only when ``fetch_block`` is ``True``.

  Regular expression for filtering every line to put into the block of response when using ``fetch_block``.

* ``send_cmd``

  / *Condition*: optional / *Type*: str / *Default*: '' /

  Command to be sent.

* ``kwargs``

  / *Condition*: optional / *Type*: Dict / *Default*: None /

  The optional arguments depend on the connection type used in the '``connect``' keyword.

  Supported options:

  =====================   ================   ==================================
  Connection Type         Argument           Explanation
  =====================   ================   ==================================
  Winapp                  element_def        Definition for detecting GUI item:
                                             *Type*: str / *Default*: ''
  =====================   ================   ==================================

**Returns:**

* ``res``

  / *Type*: list /

  List of captured string from ``search_pattern``

  For example, if ``search_pattern`` is ``(?<=\s).*([0-9]..)..*(command).$``,
  and the response from connection is ``This is the 1st test command.``,
  then the returned list will be ``['1st', 'command']``.

  Thus:
  - ``${res}[0]`` will be **1st**,
  i.e. the first *captured string* defined in the pattern ``([0-9]..)``.

  - ``${res}[1]`` will be **command**,
  i.e. the second *captured string* defined in the pattern ``(command)``.

      """
      # Parameter validation: eob_pattern and filter_pattern are only valid when fetch_block is True
      if not fetch_block:
         if eob_pattern != '.*':
            raise Exception("Parameter 'eob_pattern' is only applicable when 'fetch_block' is True. "
                           f"Current values: fetch_block={fetch_block}, eob_pattern='{eob_pattern}'")
         if filter_pattern != '.*':
            raise Exception("Parameter 'filter_pattern' is only applicable when 'fetch_block' is True. "
                           f"Current values: fetch_block={fetch_block}, filter_pattern='{filter_pattern}'")
      else:
         if eob_pattern and has_capturing_groups(eob_pattern):
            BuiltIn().log(f"Warning: Capturing groups are not supported within the eob_pattern '{eob_pattern}'.", constants.LOG_LEVEL_WARNING)
         if filter_pattern and has_capturing_groups(filter_pattern):
            BuiltIn().log(f"Warning: Capturing groups are not supported within the filter_pattern '{filter_pattern}'.", constants.LOG_LEVEL_WARNING)

      if conn_name not in self.connection_manage_dict.keys():
         raise AssertionError("The '%s' connection hasn't been established. Please connect first." % conn_name)

      # if search_pattern is None:
      #    raise Exception("The 'search_pattern' have to be a regex string instead of None.")

      if send_cmd is None:
         send_cmd = ''

      connection_obj = self.connection_manage_dict[conn_name]
      if connection_obj.get_connection_type() in ["DLT", "DLTConnector", "TTFisclient"]:
         match_try = 5

      # if 'verify_timeout' not in kwargs:
      kwargs['default_verify_timeout'] = self.default_verify_timeout

      kwargs['emergency_timeout'] = self.default_emergency_timeout

      BuiltIn().log(f"sending command '{send_cmd}' to '{conn_name}' ...", constants.LOG_LEVEL_INFO)
      res = None
      for i in range(1, match_try+1):
         kwargs['send_cmd'] = send_cmd
         res = connection_obj.wait_4_trace(search_pattern, int(timeout), fetch_block, eob_pattern, filter_pattern, **kwargs)
         if res is None:
            log_level = constants.LOG_LEVEL_WARNING if (i == match_try) else constants.LOG_LEVEL_INFO
            BuiltIn().log(f"[{conn_name}] Match try {i}/{match_try} timed out ('{search_pattern}')", log_level)
         else:
            break

      if not res:
         raise AssertionError(f"Failed to match the pattern '{search_pattern}' within '{match_try}' {'try' if match_try == 1 else 'tries'} ({conn_name}).")

      # Determine if the pattern has capturing groups
      has_groups = has_capturing_groups(search_pattern) if search_pattern else False

      if hasattr(res, "groups"):
         if has_groups:
            match_res = [str(g) for g in res.groups()]
         else:
            match_res = None
      elif isinstance(res, dict):
         match_res = res
      else:
         match_res = [str(res)]

      BuiltIn().log(f"Search pattern '{search_pattern}' matched (try {i}) on connection '{conn_name}'", constants.LOG_LEVEL_INFO)

      return match_res


# >>>> FOR UNIT TEST FUNCTIONALITY
class TestOption:
   DLT_OPT = 0
   SSH_OPT = 1
   SERIAL_OPT = 2


if __name__ == "__main__":
   conn_manager = ConnectionManager()
   test_opt = TestOption.SSH_OPT
   if test_opt == TestOption.DLT_OPT:
      DLT_CONF_SAMPLE = {
                  'target_ip': '127.0.0.1',
                  'target_port': 3490,
                  'mode': 0,
                  'ecu': 'ECU1',
                  'com_port': 'COM1',
                  'baudrate': 115200,
                  'server_ip': 'localhost',
                  'server_port': 1234
      }
      conn_manager.connect("test_dlt", "DLT", "dltconnector", DLT_CONF_SAMPLE)
      test_res = conn_manager.verify_unnamed_args("test_dlt", "get connection", 5, False, ".*", ".*", "TR_TEST_CONNECTION")
      print(test_res)
   elif test_opt == TestOption.SSH_OPT:
      SSH_CONF_SAMPLE = {
         'address': '127.0.0.1',
         'port': 8022,
         'username': 'root',
         'password': '',
         'authentication': 'password',
         'key_filename': None
      }
      conn_manager.connect("test_ssh", "SSHClient", None, SSH_CONF_SAMPLE)
      # conn_manager.send_command("test_ssh", "cd ..")
      test = conn_manager.verify_unnamed_args(
         "test_ssh",
         r"(?<=\s).*([0-9]..).*(command).$",
         5,
         False,
         ".*",
         ".*",
         "echo This is the 1st test command."
      )
      print(test[0])
      print(test[1])
      print(test[2])
   elif test_opt == TestOption.SERIAL_OPT:
      SERIAL_CONF_SAMPLE = {
         'port' : 'COM8',
         'baudrate' : 115200,
         'bytesize' : 8,
         'stopbits' : 1,
         'parity' : 'N',
         'rtscts' : False,
         'xonxoff' : False,
      }
      conn_manager.connect("test_serial", "SERIAL", None, SERIAL_CONF_SAMPLE)
      test = conn_manager.verify_unnamed_args("test_serial", ".*", 5, False, ".*", ".*", "ASDASFSDFA")
      print(test)
   conn_manager.quit()
