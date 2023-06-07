#  Copyright 2020-2022 Robert Bosch GmbH
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
import os
import importlib
import pkgutil
import QConnectBase.constants as constants
import site


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

   id = 0

   def __init__(self):
      """
Constructor for ConnectionManager class.
      """
      self.connection_manage_dict = {}
      main_lib_path = dirname(os.path.realpath(__file__))
      site_package_dirs = site.getsitepackages()
      extension_lib_paths = []
      for site_package_dir in site_package_dirs:
         curr_dir = os.walk(site_package_dir).__next__()[0]
         lib_path = [constants.SLASH.join([curr_dir, lib_ext]) for lib_ext in os.walk(site_package_dir).__next__()[1]
                     if (ConnectionManager.LIBRARY_EXTENSION_PREFIX in lib_ext) or lib_ext.startswith(ConnectionManager.LIBRARY_EXTENSION_PREFIX2)]
         extension_lib_paths.extend(lib_path)

      all_libs = [main_lib_path]
      all_libs.extend(extension_lib_paths)
      all_libs = list(set(all_libs))
      for module_loader, name, is_pkg in pkgutil.walk_packages(all_libs):
         # noinspection PyBroadException
         try:
            if not is_pkg and not name.startswith("setup"):
               importlib.import_module(name)
            else:
               _module = module_loader.find_module(name).load_module(name)
         except Exception as _ex:
            pass

      supported_connection_classes_list = Utils.get_all_descendant_classes(ConnectionBase)
      self.supported_connection_classes_dict = {cls._CONNECTION_TYPE: cls for cls in supported_connection_classes_list}

   def __del__(self):
      """
Destructor for ConnectionManager class.

**Returns:**
         None.
      """
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
   def disconnect(self, connection_name):
      """
Keyword for disconnecting a connection by name.
      
**Arguments:**   

* ``connection_name``   

  / *Condition*: required / *Type*: str /

  Connection's name.

**Returns:**

(*no returns*)
      """
      if connection_name in self.connection_manage_dict.keys():
         self.connection_manage_dict[connection_name].quit()
         del self.connection_manage_dict[connection_name]

#    @keyword
#    def connect(self, *args, **kwargs):
#       """
# Keyword for making a connection.
      
# **Arguments:**   

# (*refer to connect_unnamed_args method for details*)

# * ``args``    

#   / *Condition*: required / *Type*: tuple /

#   Non-Keyword Arguments.

# * ``kwargs``   

#   / *Condition*: required / *Type*: dict /

#   Keyword Arguments.

# **Returns:**

# (*no returns*)
#       """
#       if len(args) > 0 and len(kwargs) > 0:
#          raise AssertionError("Getting both Non-Keyword Arguments and Keyword Arguments. Please select to use only Non-Keyword Arguments or Keyword Arguments.")

#       if len(args) > 0:
#          self.connect_unnamed_args(*args)
#       elif len(kwargs) > 0:
#          self.connect_named_args(**kwargs)
#       else:
#          raise Exception("Not received any input param.")

#    def connect_named_args(self, **kwargs):
#       """
# Making a connection with name arguments.
      
# **Arguments:**   

# (*refer to connect_unnamed_args method for details*)

#   * ``kwargs``   

#   / *Condition*: required / *Type*: dict /
  
#   Keyword Arguments.

# **Returns:**

# (*no returns*)
#       """
#       org_args = ConnectParam.get_attr_list()
#       if set(kwargs.keys()).issubset(set(org_args)):
#          params = ConnectParam(**kwargs)
#          self.connect_unnamed_args(params.conn_name,
#                                    params.conn_type,
#                                    params.conn_mode,
#                                    params.conn_conf)
#       else:
#          raise Exception("Input parameter are invalid.")

   @keyword
   def connect(self, conn_name='default_conn', conn_type='TCPIP', conn_mode='', conn_conf={}):
      """
Making a connection.
      
**Arguments:**   

* ``conn_name``    

  / *Condition*: optional / *Type*: str / *Default*: 'default_conn' /
  
  Name of connection.

* ``conn_type``    

  / *Condition*: optional / *Type*: str / *Default*: 'TCPIP' /
  
  Type of connection.

* ``conn_mode``    

  / *Condition*: optional / *Type*: str / *Default*: '' /
  
  Connection mode.

* ``conn_conf``    

  / *Condition*: optional / *Type*: json / *Default*: {} /
  
  Configuration for connection.

**Returns:**

(*no returns*)
      """
      if conn_type not in self.supported_connection_classes_dict.keys():
         raise AssertionError("The '%s' connection type hasn't been supported" % conn_type)

      if conn_name in self.connection_manage_dict.keys():
         raise AssertionError(constants.String.CONNECTION_NAME_EXIST % conn_name)

      if conn_name == 'default_conn':
         conn_name += str(ConnectionManager.id)
         ConnectionManager.id += 1

      try:
         connection_obj = self.supported_connection_classes_dict[conn_type](conn_mode, conn_conf)
      except Exception as ex:
         # BuiltIn().log("Unable to create connection. Exception: %s" % ex, constants.LOG_LEVEL_ERROR)
         raise AssertionError("Unable to create connection. Exception: %s" % ex)

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
         raise Exception("Unable to create connection. Exception: %s" % ex)

#    @keyword
#    def send_command(self, *args, **kwargs):
#       """
# Keyword for sending command to a connection.
#
# **Arguments:**
#
# (*refer to send_unnamed_args method for details*)
#
# * ``args``
#
#   / *Condition*: require / *Type*: tuple /
#
#   Non-Keyword Arguments.
#
# * ``kwargs``
#
#   / *Condition*: require / *Type*: dict /
#
#   Keyword Arguments.
#
# **Returns:**
#
# (*no returns*)
#       """
#       if len(args) > 0 and len(kwargs) > 0:
#          raise AssertionError("Getting both Non-Keyword Arguments and Keyword Arguments. Please select to use only Non-Keyword Arguments or Keyword Arguments.")
#
#       if len(args) > 0:
#          self.send_command_unnamed_args(*args)
#       elif len(kwargs) > 0:
#          self.send_command_named_args(**kwargs)
#       else:
#          raise Exception("Not received any input param.")
#
#    def send_command_named_args(self, **args):
#       """
# Send command to a connection with name arguments.
#
# **Arguments:**
#
# (*refer to send_unnamed_args method for details*)
#
#   * ``kwargs``
#
#   / *Condition*: required / *Type*: dict /
#
#   Keyword Arguments.
#
# **Returns:**
#
# (*no returns*)
#       """
#       org_args = SendCommandParam.get_attr_list()
#       if set(args.keys()).issubset(set(org_args)):
#          params = SendCommandParam(**args)
#          self.send_command_unnamed_args(params.conn_name,
#                                         params.command,
#                                         params.element_def.__dict__,
#                                         params.args)
#       else:
#          raise Exception("Input parameter are invalid.")

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

  Keyword Arguments.
  
**Returns:**

(*no returns*)
      """
      if conn_name not in self.connection_manage_dict.keys():
         raise AssertionError("The '%s' connection  hasn't been established. Please connect first." % conn_name)
      connection_obj = self.connection_manage_dict[conn_name]
      try:
         connection_obj.send_obj(command, **kwargs)
      except Exception as ex:
         raise Exception("Unable to send command to '%s' connection. Exception: %s" % (conn_name, str(ex)))

#    @keyword
#    def verify(self, *args, **kwargs):
#       """
# Keyword uses to verify a pattern from connection response after sending a command.
#
# **Arguments:**
#
# (*refer to verify_unnamed_args method for details*)
#
# * ``args``
#
#   / *Condition*: required / *Type*: tuple /
#
#   Non-Keyword Arguments.
#
# * ``kwargs``
#
#   / *Condition*: required / *Type*: dict /
#
#   Keyword Arguments.
#
# **Returns:**
#
# * ``match_res``
#
#   / *Type*: str /
#
#   Matched string.
#       """
#       if len(args) > 0 and len(kwargs) > 0:
#          raise AssertionError("Getting both Non-Keyword Arguments and Keyword Arguments. Please select to use only Non-Keyword Arguments or Keyword Arguments.")
#
#       if len(args) > 0:
#          return self.verify_unnamed_args(*args)
#       elif len(kwargs) > 0:
#          return self.verify_named_args(**kwargs)
#       else:
#          raise Exception("Not received any input param.")
#
#    def verify_named_args(self, **kwargs):
#       """
# Verify a pattern from connection response after sending a command with named arguments.
#
# **Arguments:**
#
# (*refer to verify_unnamed_args method for details*)
#
# * ``kwargs``
#
#   / *Condition*: required / *Type*: dict /
#
#   Keyword Arguments.
#
# **Returns:**
#
# * ``match_res``
#
#   / *Type*: str /
#
#   Matched string.
#       """
#       org_args = VerifyParam.get_attr_list()
#       if set(kwargs.keys()).issubset(set(org_args)):
#          params = VerifyParam(**kwargs)
#          return self.verify_unnamed_args(params.conn_name,
#                                          params.search_pattern,
#                                          params.timeout,
#                                          params.fetch_block,
#                                          params.eob_pattern,
#                                          params.filter_pattern,
#                                          params.send_cmd,
#                                          params.element_def.__dict__,
#                                          params.args)
#       else:
#          raise Exception("Input parameter are invalid.")

   @keyword
   def verify(self, conn_name, search_pattern, timeout=5, match_try=1, fetch_block=False, eob_pattern='.*', filter_pattern='.*', send_cmd='', **kwargs):
      """
Verify a pattern from connection response after sending a command.
      
**Arguments:**   

* ``conn_name``

  / *Condition*: required / *Type*: str /
  
  Name of connection.
		 
* ``search_pattern``

  / *Condition*: required / *Type*: str /
  
  Regular expression all received trace messages are compare to. 
  Can be passed either as a string or a regular expression object. Refer to Python documentation for module 're'.

* ``timeout``

  / *Condition*: optional / *Type*: float / *Default*: 0 /

  Timeout parameter specified as a floating point number in the unit 'seconds'.

* ``match_try``

  / *Condition*: optional / *Type*: int / *Default*: 1 /

  Number of time for trying to match the pattern.
  
* ``fetch_block``    

  / *Condition*: optional / *Type*: bool / *Default*: False /
  
  Determine if 'fetch block' feature is used.
  
* ``eob_pattern``    

  / *Condition*: optional / *Type*: str / *Default*: '.*' /
  
  The end of block pattern.  

* ``filter_pattern``    

  / *Condition*: optional / *Type*: str / *Default*: '.*' /
  
  Pattern to filter message line by line.

* ``send_cmd``    

  / *Condition*: optional / *Type*: str / *Default*: '' /
  
  Command to be sent.
  
* ``kwargs``

  / *Condition*: optional / *Type*: Dict / *Default*: None /
  
  The optional arguments depend on the connection type used in the 'connect' keyword. Here are the supported options:
  
  | Connection Type     | Argument         | Explaination                      |
  | ------------------- | ---------------- | --------------------------------- |
  | Winapp              | element_def      | Definition for detecting GUI item |
  |                     |                  | / *Type*: str / *Default*: '' /   |
  |                     |                  |                                   |
  
**Returns:**

* ``match_res``

  / *Type*: str /
  
  Matched string.
      """
      if conn_name not in self.connection_manage_dict.keys():
         raise AssertionError("The '%s' connection  hasn't been established. Please connect first." % conn_name)
      
      connection_obj = self.connection_manage_dict[conn_name]
      if connection_obj.get_connection_type() in ["DLT", "DLTConnector", "TTFisclient"]:
         match_try = 5
      
      for i in range(1, match_try+1):
         kwargs['send_cmd'] = send_cmd
         res = connection_obj.wait_4_trace(search_pattern, int(timeout), fetch_block, eob_pattern, filter_pattern, **kwargs)
         if res is None:
            # raise AssertionError("Unable to match the pattern after '%s' seconds." % timeout)
            BuiltIn().log("Match try %s/%s timed out" % (i, match_try), constants.LOG_LEVEL_WARNING)
         else:
            break

      if not res:
         raise AssertionError("Unable to match the pattern after '%s' time." % timeout)

      return res


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
      test = conn_manager.verify_unnamed_args("test_ssh", "(?<=\s).*([0-9]..).*(command).$", 5, False, ".*", ".*", "echo This is the 1st test command.")
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
