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
# File: tcp_base.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / May 2021.
# Based on \lib\TCP\CVirtualSocket.py in TML Framework.
#
# Description:
#   Provide the base class for all TCP client and server connection.
#
# History:
#
# 12.05.2021 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from robot.libraries.BuiltIn import BuiltIn
from QConnectBase.connection_base import ConnectionBase, BrokenConnError
from QConnectBase.utils import DictToClass
from QConnectBase.utils import Utils
from inspect import currentframe
import QConnectBase.constants as constants
import socket
import threading
import time


class TCPConfig(DictToClass):
   """
Class to store configurations for TCP connection.
   """
   address = "localhost"
   port = 0

   def validate(self):
      if not self.port:
         raise Exception(f"Port number is not provided")
      if not Utils.is_valid_host(self.address, self.port):
         raise Exception(f"There is no available server at {self.address}:{self.port}")


class TCPBase(ConnectionBase, object):
   """
Base class for a tcp connection.
   """
   RECV_MSGS_POLLING_INTERVAL = 0.005
   _socket_instance = 0
   _CONNECTION_TYPE = "TCPIPBase"


   def __init__(self, mode=None, config=None):
      """
Constructor for TCPBase class.

**Arguments:**

* ``mode``

  / *Condition*: optional / *Type*: str / *Default*: None /

  TCP mode.

* ``config``

  / *Condition*: optional / *Type*: dict / *Default*: None /

  Configuration for TCP connection in dictionary format.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      self.config = TCPConfig(**config)
      address = self.config.address
      port = self.config.port
      BuiltIn().log("%s: Creating socket for '%s':'%s'" % (_mident, address, port), constants.LOG_LEVEL_DEBUG)
      ConnectionBase.__init__(self)
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self._timeout = self.socket.gettimeout()
      self._address = address
      self._port = port
      self._mode = mode
      self.conn = None
      if 'connection_name' in config:
         self.connection_name = config['connection_name']

      # default timeout for send/receive is 10 seconds
      self._conn_timeout = 10
      self._is_connected = False
      self._send_lock = threading.RLock()
      self._read_lock = threading.RLock()
      TCPBase._socket_instance += 1

      # initialize receiver thread
      self._init_thread_receiver(TCPBase._socket_instance)
      self.socketType = constants.SocketType.UNKNOWN

      self._recv_thrd_term = threading.Event()
      self._recv_thrd_start = threading.Event()
      self._broken_conn = threading.Event()

      self._recv_thrd_term.clear()
      self._recv_thrd_start.clear()

   def __del__(self):
      """
Destructor for TCPBase class.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log("%s" % _mident, constants.LOG_LEVEL_DEBUG)
      self.quit()

   def _send(self, msg, cr=True):
      """
>> Should be override in derived class.

Actual method to send message to a tcp connection.

**Arguments:**

* ``msg``

  / *Condition*: required / *Type*: str /

  Message to be sent.

* ``cr``

  / *Condition*: required / *Type*: str /

  Determine if it's necessary to add newline character at the end of command.

**Returns:**

(*no returns*)
      """
      pass

   def _read(self):
      """
>> Should be override in derived class.

Actual method to read message from a tcp connection.

**Returns:**
         Empty string.
      """
      return ''

   def close(self):
      """
Close connection.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)

      # close listener thread
      # self.quit()

      # SSH made problems here, therefore ignore possible exceptions.
      # noinspection PyBroadException
      try:
         self.conn.shutdown(socket.SHUT_RDWR)
      except:
         # ignore, if not possible
         pass

      # noinspection PyBroadException
      try:
         self.disconnect()
      except:
         # ignore, if not possible
         pass
      # 23.07.2014 Pollerspoeck
      # self.socket.close was in case of tcpip client redundant,
      # and in case of tcpip service not required.
      # commented it out
      # self.socket.close()

   def _get_timeout(self):
      """
Get connection timeout value.

**Returns:**
         Value of connection timeout.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      return self._timeout

   def _set_timeout(self, timeout):
      """
Set the connection timeout.

**Arguments:**

* ``timeout``

  / *Condition*: required / *Type*: int /

  Timeout value in second.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log("%s: set timeout to '%d'" % (_mident, timeout), constants.LOG_LEVEL_DEBUG)
      self._timeout = timeout
      self.socket.settimeout(timeout)

   def _get_conn_timeout(self):
      """
Get connection timeout.

**Returns:**

  / *Type*: int /

  Connection timeout.
      """
      return self._conn_timeout

   def _set_conn_timeout(self, timeout):
      """
Set connection timeout.

**Arguments:**

* ``timeout``

  / *Condition*: required / *Type*: int /

  Timeout value in second.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log("%s: set timeout to '%d'" % (_mident, timeout), constants.LOG_LEVEL_DEBUG)

      self._conn_timeout = timeout
      if self.conn is not None:
         self.conn.settimeout(timeout)

   def _get_address(self):
      """
Get connection address.

**Returns:**

  / *Type*: str /

  Connection address.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      return self._address

   def _set_address(self, address):
      """
Set connection address.

**Arguments:**

* ``address``

  / *Condition*: required / *Type*: str /

  Address of connection.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      self.address = address

   def _get_port(self):
      """
Get connection port.

**Returns:**

  / *Type*: int /

  Connection port.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      return self._port

   def _set_port(self, port):
      """
Set connection port.

**Arguments:**

* ``port``

  / *Condition*: required / *Type*: int /

  Port number.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      self.port = port

   def _is_connected(self):
      """
Get connected state.

**Returns:**
         True if connection is connected.
         False if connection is not connected.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      return self._is_connected

   def _get_socket_instance(self):
      """
      Get method of socket_instance property.

**Returns:**
         Value of _socket_instance.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      return TCPBase._socket_instance

   ##############################################################
   # properties
   ##############################################################
   is_connected = property(_is_connected)
   timeout = property(_get_timeout, _set_timeout)
   conn_timeout = property(_get_conn_timeout, _set_conn_timeout)
   address = property(_get_address, _set_address)
   port = property(_get_port, _set_port)
   socket_instance = property(_get_socket_instance)

   def quit(self, is_disconnect_all=True):
      """
Quit connection.

**Arguments:**

* ``is_disconnect_all``

  / *Condition*: required / *Type*: bool /

  Determine if it's necessary for disconnect all connection.

**Returns:**

(*no returns*)
      """
      self.close()
      if self._recv_thrd_obj and self._recv_thrd_obj.is_alive():
         self._recv_thrd_term.set()
         while self._recv_thrd_obj.is_alive():
            try:
               time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)
            except Exception as ex:
               break
         self._recv_thrd_obj = None
      super(TCPBase, self).quit()

   def connect(self):
      """
>> Should be override in derived class.

Establish the connection.

**Returns:**

(*no returns*)
      """
      pass

   def disconnect(self, device=None):
      """
>> Should be override in derived class.

Disconnect the connection.

**Returns:**

(*no returns*)
      """
      # super(TCPBase, self).disconnect()
      if self.conn is not None:
         self.conn.close()


class TCPBaseServer:
   """
Base class for TCP server.
   """
   def _bind(self):
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      self.socket.settimeout(self.timeout)
      self.socket.bind((self.address, self.port))

   def _listen(self):
      """
Listen for client socket.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      self.socket.listen(0)

   def _accept(self):
      """
Method for handling socket accept action.

**Returns:**

* ``conn``

  / *Condition*: required / *Type*: socket /

  TCP connection socket object.

* ``addr``

  / *Condition*: required / *Type*: str /

  The address bound to the socket on the other end of the connection.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      try:
         (conn, addr) = self.socket.accept()
      except Exception as reason:
         BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_WARNING)
         raise reason

      return conn, addr

   def accept_connection(self):
      """
Wrapper method for handling accept action of TCP Server.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      self._listen()
      self.conn, addr = self._accept()
      self.conn_timeout = self._conn_timeout
      self._is_connected = True
      BuiltIn().log("%s: connected to '%s':'%d' " % (_mident, addr[0], addr[1]), constants.LOG_LEVEL_DEBUG)

   def connect(self):
      self.accept_connection()

   def disconnect(self):
      self._is_connected = False
      if self.socket is not None:
         self.socket.close()
      if self.conn is not None:
         self.conn.close()
         BuiltIn().log(f"disconnected from '{self.address}':'{self.port}' (connection type '{self._CONNECTION_TYPE}' with name '{self.connection_name}')",
                  constants.LOG_LEVEL_INFO)

class TCPBaseClient:
   """
Base class for TCP client.
   """
   def connect(self):
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      try:
         BuiltIn().log("%s: Try to connect to '%s':'%d'" % (_mident, self.address, self.port), constants.LOG_LEVEL_DEBUG)
         self.socket.connect((self.address, self.port))
         self.conn = self.socket
         self._is_connected = True
      except socket.error as e:
         raise BrokenConnError(f"Socket error: {e}")
      except Exception as reason:
         BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_ERROR)
         # raise BrokenConnError(f"There is no possible server at {address}:{port}'")
         raise reason

      BuiltIn().log(f"connected to '{self.address}':'{self.port}' (connection type '{self._CONNECTION_TYPE}' with name '{self.connection_name}')",
                    constants.LOG_LEVEL_INFO)

   def disconnect(self):
      self._is_connected = False
      if self.conn is not None:
         self.conn.close()
         BuiltIn().log(f"disconnected from '{self.address}':'{self.port}' (connection type '{self._CONNECTION_TYPE}' with name '{self.connection_name}')",
                  constants.LOG_LEVEL_INFO)
