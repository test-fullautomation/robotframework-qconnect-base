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


class VerifyParam(InputParam):
   """
   Class for storing parameters for verify action.
   """
   conn_name = 'default_conn'
   search_pattern = None
   timeout = 5
   fetch_block = False
   eob_pattern = '.*'
   filter_pattern = '.*'
   send_cmd = ''


class ConnectionManager(Singleton):
   """
   Class to manage all connections.
   """
   ROBOT_LIBRARY_SCOPE = 'GLOBAL'
   ROBOT_AUTO_KEYWORDS = False
   LIBRARY_EXTENSION_PREFIX = 'robotframework_qconnect'
   LIBRARY_EXTENSION_PREFIX2 = 'QConnect'

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

      Returns:
         None.
      """
      self.quit()

   def quit(self):
      """
      Quit connection manager.
      
      Returns:
         None.
      """
      for connection in self.connection_manage_dict.values():
         connection.quit()
      self.connection_manage_dict.clear()

   def add_connection(self, name, conn):
      """
      Add a connection to managed dictionary.
      
      Args:
         name: connection's name.
         
         conn: connection object.

      Returns:
         None.
      """
      if name not in self.connection_manage_dict.keys():
         self.connection_manage_dict[name] = conn

   def remove_connection(self, connection_name):
      """
      Remove a connection by name.
      
      Args:
         connection_name: connection name.

      Returns:
         None.
      """
      if connection_name in self.connection_manage_dict.keys():
         del self.connection_manage_dict[connection_name]


   def get_connection_by_name(self, connection_name):
      """
      Get an exist connection by name.
      
      Args:
         connection_name: connection's name.

      Returns:
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
      
      Args:
         connection_name: Name of connection.

      Returns:
         None.
      """
      if connection_name in self.connection_manage_dict.keys():
         self.connection_manage_dict[connection_name].quit()
         del self.connection_manage_dict[connection_name]

   @keyword
   def connect(self, *args, **kwargs):
      """
      Keyword for making a connection.
      
      Args:
         args:   Non-Keyword Arguments.
		 
         kwargs:   Keyword Arguments.

      Returns:
         None.
      """
      if len(args) > 0 and len(kwargs) > 0:
         raise AssertionError("Getting both Non-Keyword Arguments and Keyword Arguments. Please select to use only Non-Keyword Arguments or Keyword Arguments.")

      if len(args) > 0:
         self.connect_unnamed_args(*args)
      elif len(kwargs) > 0:
         self.connect_named_args(**kwargs)
      else:
         raise Exception("Not received any input param.")

   def connect_named_args(self, **kwargs):
      """
      Making a connection with name arguments.
      
      Args:
         kwargs: Dictionary of arguments.

      Returns:
         None.
      """
      org_args = ConnectParam.get_attr_list()
      if set(kwargs.keys()).issubset(set(org_args)):
         params = ConnectParam(**kwargs)
         self.connect_unnamed_args(params.conn_name,
                                   params.conn_type,
                                   params.conn_mode,
                                   params.conn_conf)
      else:
         raise Exception("Input parameter are invalid.")

   def connect_unnamed_args(self, connection_name, connection_type, mode, config):
      """
      Making a connection.
      
      Args:
         connection_name: Name of connection.
		 
         connection_type: Type of connection.
		 
         mode: Connection mode.
		 
         config: Configuration for connection.

      Returns:
         None.
      """
      if connection_type not in self.supported_connection_classes_dict.keys():
         raise AssertionError("The '%s' connection type hasn't been supported" % connection_type)

      if connection_name in self.connection_manage_dict.keys():
         raise AssertionError(constants.String.CONNECTION_NAME_EXIST % connection_name)

      try:
         connection_obj = self.supported_connection_classes_dict[connection_type](mode, config)
      except Exception as ex:
         # BuiltIn().log("Unable to create connection. Exception: %s" % ex, constants.LOG_LEVEL_ERROR)
         raise AssertionError("Unable to create connection. Exception: %s" % ex)

      if connection_obj is not None:
         self.add_connection(connection_name, connection_obj)

      try:
         connection_obj.connect()
      except Exception as ex:
         self.remove_connection(connection_name)
         # BuiltIn().log("Unable to create connection. Exception: %s" % ex, constants.LOG_LEVEL_ERROR)
         raise Exception("Unable to create connection. Exception: %s" % ex)

   @keyword
   def send_command(self, *args, **kwargs):
      """
      Keyword for sending command to a connection.
      
      Args:
         args:   Non-Keyword Arguments.
		 
         kwargs:   Keyword Arguments.

      Returns:
         None.
      """
      if len(args) > 0 and len(kwargs) > 0:
         raise AssertionError("Getting both Non-Keyword Arguments and Keyword Arguments. Please select to use only Non-Keyword Arguments or Keyword Arguments.")

      if len(args) > 0:
         self.send_command_unnamed_args(*args)
      elif len(kwargs) > 0:
         self.send_command_named_args(**kwargs)
      else:
         raise Exception("Not received any input param.")

   def send_command_named_args(self, **args):
      """
      Send command to a connection with name arguments.
      
      Args:
         args: Dictionary of arguments.

      Returns:
         None.
      """
      org_args = SendCommandParam.get_attr_list()
      if set(args.keys()).issubset(set(org_args)):
         params = SendCommandParam(**args)
         self.send_command_unnamed_args(params.conn_name,
                                        params.command)
      else:
         raise Exception("Input parameter are invalid.")

   def send_command_unnamed_args(self, connection_name, command):
      """
      Send command to a connection.
      
      Args:
         connection_name: connection's name.
		 
         command: command.

      Returns:
         None.
      """
      if connection_name not in self.connection_manage_dict.keys():
         raise AssertionError("The '%s' connection  hasn't been established. Please connect first." % connection_name)
      connection_obj = self.connection_manage_dict[connection_name]
      try:
         connection_obj.send_obj(command)
      except Exception as ex:
         BuiltIn().log("Unable to send command to '%s' connection. Exception: %s" % (connection_name, str(ex)))

   @keyword
   def verify(self, *args, **kwargs):
      """
      Keyword uses to verify a pattern from connection response after sending a command.
      
      Args:
         args:   Non-Keyword Arguments.
		 
         kwargs:   Keyword Arguments.

      Returns:
         match_res: matched string.
      """
      if len(args) > 0 and len(kwargs) > 0:
         raise AssertionError("Getting both Non-Keyword Arguments and Keyword Arguments. Please select to use only Non-Keyword Arguments or Keyword Arguments.")

      if len(args) > 0:
         return self.verify_unnamed_args(*args)
      elif len(kwargs) > 0:
         return self.verify_named_args(**kwargs)
      else:
         raise Exception("Not received any input param.")

   def verify_named_args(self, **kwargs):
      """
      Verify a pattern from connection response after sending a command with named arguments.
      
      Args:
         kwargs: Dictionary of arguments.

      Returns:
         match_res: matched string.
      """
      org_args = VerifyParam.get_attr_list()
      if set(kwargs.keys()).issubset(set(org_args)):
         params = VerifyParam(**kwargs)
         return self.verify_unnamed_args(params.conn_name,
                                         params.search_pattern,
                                         params.timeout,
                                         params.fetch_block,
                                         params.eob_pattern,
                                         params.filter_pattern,
                                         params.send_cmd)
      else:
         raise Exception("Input parameter are invalid.")

   def verify_unnamed_args(self, connection_name, search_obj, timeout=0, fetch_block=False, eob_pattern='.*', filter_pattern='.*', *fct_args):
      """
      Verify a pattern from connection response after sending a command.
      
      Args:
         connection_name: connection's name.
		 
         search_obj: search pattern.
		 
         timeout: timeout for waiting result.
		 
         fetch_block: use fetch block feature.
		 
         end_of_block_pattern: pattern for detecting the end of block.
		 
         filter_pattern: line filter pattern.
		 
         fct_args: command to be sent.

      Returns:
         match_res: matched string.
      """
      if connection_name not in self.connection_manage_dict.keys():
         raise AssertionError("The '%s' connection  hasn't been established. Please connect first." % connection_name)
      connection_obj = self.connection_manage_dict[connection_name]
      res = connection_obj.wait_4_trace(search_obj, int(timeout), fetch_block, eob_pattern, filter_pattern, *fct_args)
      if res is None:
         raise AssertionError("Unable to match the pattern after '%s' seconds." % timeout)

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
         # 'dltconnector': {
            'gen3flex@DLTConnector': {
                  'target_ip': '127.0.0.1',
                  'target_port': 3490,
                  'mode': 0,
                  'ecu': 'ECU1',
                  'com_port': 'COM1',
                  'baudrate': 115200,
                  'server_ip': 'localhost',
                  'server_port': 1234
            }
         # }
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
