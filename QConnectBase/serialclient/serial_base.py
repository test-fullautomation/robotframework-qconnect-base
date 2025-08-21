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
# File: serial_base.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / May 2021.
# Based on lib/TCP/Serial/CSerialClient.py in TML Framework.
#
# Description:
#   Provide the class for handling SSH connection.
#
# History:
#
# 12.05.2021 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from __future__ import with_statement
from QConnectBase.connection_base import ConnectionBase, BrokenConnError
from QConnectBase.utils import DictToClass
from robot.libraries.BuiltIn import BuiltIn
import QConnectBase.constants as constants
import threading
from inspect import currentframe
import time
import serial
import queue


class SerialConfig(DictToClass):
   """
Class to store the configuration for Serial connection.
   """
   port = 'COM1'
   baudrate = 115200
   bytesize = 8
   stopbits = serial.STOPBITS_ONE
   parity = serial.PARITY_NONE
   rtscts = False
   xonxoff = False


class SerialSocket(ConnectionBase):
   """
Class for handling serial connection.
   """
   _CONNECTION_TYPE = "SerialBase"
   _socket_instance = 0

   def __init__(self, _mode, config):
      """
Constructor for SerialSocket class.

**Arguments:**

* ``_mode``

  / *Condition*: required / *Type*: str /

  Unused

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Configurations for Serial Client.
      """
      self.config = SerialConfig(**config)
      ConnectionBase.__init__(self)
      self.socket = None
      self._port = self.config.port
      self._baudrate = int(self.config.baudrate)
      self._bytesize = int(self.config.bytesize)
      self._stopbits = self.config.stopbits
      self._parity = self.config.parity
      self._rtscts = self.config.rtscts
      self._xonxoff = self.config.xonxoff
      self._timeout = None  # protected: None is required to run in blocking mode.

      self._send_lock = threading.RLock()
      self._read_lock = threading.RLock()

      SerialSocket._socket_instance += 1
      self._is_connected = False

      # initialize receiver thread
      self._init_thread_receiver(SerialSocket._socket_instance, mode="SER-")


      # configure and initialize the lowlevel receiver thread
      self._llrecv_thrd_obj = None
      self._llrecv_thrd_term = threading.Event()  # initialize the lowlevel receiver thread
      self._init_thrd_llrecv(SerialSocket._socket_instance)
      # create the queue for this connection
      self.serial_queue = queue.Queue()

   def _thrd_llrecv_from_connection_interface(self):
      """
Receive and process data from serial connection in low-level.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log("%s: lowlevel receiver thread started." % _mident, constants.LOG_LEVEL_DEBUG)
      while self._is_connected is False and not self._llrecv_thrd_term.isSet():
         time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)

      while not self._llrecv_thrd_term.isSet():
         # noinspection PyBroadException
         # implementation from here:
         # http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/rfc2217_server.py
         try:
            data = self.socket.read(1).decode(self.config.encoding, 'ignore')  # read one, blocking
            n = self.socket.in_waiting  # look if there is more
            if n:
               read_data = self.socket.read(n)
               data = data + read_data.decode(self.config.encoding, 'ignore')  # and get as much as possible
            if data:
               for character in data:
                  self.serial_queue.put(character)
         except Exception as _reason:
            # ignore all errors.
            pass

         time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)

      # _read must have chance to terminate, too,therefore
      # wait here 5 times polling interval
      time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL * 5)

      self._llrecv_thrd_term.clear()
      BuiltIn().log("%s: lowlevel receiver thread terminated." % _mident, constants.LOG_LEVEL_DEBUG)

   def connect(self):
      """
Connect to serial port.

**Returns:**

(*no returns*)
      """
      pass

   def disconnect(self, _device):
      """
Disconnect serial port.

**Arguments:**

* ``_device``

  / *Condition*: required / *Type*: str /

  Unused

**Returns:**

(*no returns*)
      """
      self.socket.close()
      self._is_connected = False
      BuiltIn().log(f"disconnected from COM{self._port}@{self._baudrate} (connection type '{self._CONNECTION_TYPE}' with name '{self.connection_name}')",
                    constants.LOG_LEVEL_INFO)

   def _send(self, msg, _cr):
      """
Send data to serial port.

**Arguments:**

* ``msg``

  / *Condition*: required / *Type*: str /

  Message to be sent.

* ``_cr``

  / *Condition*: required / *Type*: str /

  Unused.

**Returns:**

(*no returns*)
      """
      try:
         _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
         BuiltIn().log("%s: sending: '%s'" % (_mident, msg), constants.LOG_LEVEL_DEBUG)
         with self._send_lock:
            send_byte = (self._rm_q_dollar(str(msg)) + "\n").encode('utf-8')
            self.socket.write(send_byte)
      except Exception as reason:
         BuiltIn().log("%s: could not send: '%s'. Reason: '%s'" % (_mident, msg, str(reason)), constants.LOG_LEVEL_WARNING)
         self._is_connected = False


   def _read(self):
      """
Receive data from serial connection.

**Returns:**

  / *Type*: str /

  Data received from connection.
      """
      data = ''
      #  usually \r\n or \n is sent to terminate a line,
      #  but U-Boot sends \n\r, therefore try to fit to all
      #  possible line endings and return the identified line.

      # We read the data here from the queue filled by the
      # low-level receiver thread.
      while (data[-1:] != '\n') and not self._llrecv_thrd_term.isSet():
         try:
            d = self.serial_queue.get(block=False)
            data = data + d
         except queue.Empty:
            # non blocking get from serq causes that
            # Queue.Empty exception. In this case wait some milliseconds before
            # retry
            time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)

      # remove the \n
      data = data[:-1]

      # if we filter for \n, then
      # if a \r\n was sent, we need to remove the remaining \r
      if data[-1:] == '\r':
         data = data[:-1]
      # if \n\r was sent, then the next line starts with a \r which
      # need to be removed.
      # Disadvantage: If somebody uses \r to overwrite an existing line,
      # this will not work because the in this case intended \r will be filtered,
      # too.
      if data[:1] == '\r':
         data = data[1:]

      #   SerialSocket decodes all characters from UTF-8 to unicode with mode "replace".
      #   This avoids that data waste caused e.g. by startup/shutdown of the target can bring corrupt data into
      #   the TML Framework.
      return self._q_dollar(data)


   def quit(self):
      """
Quit serial connection.

**Returns:**

(*no returns*)
      """
      self.disconnect(None)
      if self._llrecv_thrd_obj and self._llrecv_thrd_obj.is_alive():
         self._llrecv_thrd_term.set()
         while self._llrecv_thrd_obj.is_alive():
            time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)
         self._llrecv_thrd_obj = None

      if self._recv_thrd_obj and self._recv_thrd_obj.is_alive():
         self._recv_thrd_term.set()
         while self._recv_thrd_obj.is_alive():
            time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)
         self._recv_thrd_obj = None
      super(SerialSocket, self).quit()



class SerialClient(SerialSocket):
   """
Serial client class.
   """
   _CONNECTION_TYPE = "SerialClient"

   def __init__(self, _mode, config):
      """
Constructor for SerialClient class.

**Arguments:**

* ``_mode``

  / *Condition*: required / *Type*: str /

  Unused

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Configurations for Serial Client.
      """
      super(SerialClient, self).__init__(_mode, config)

   def connect(self):
      """
Connect to the Serial port.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)

      try:
         # ports are counted from 0, therefore it is self._port-1
         self.socket = serial.Serial(port=self._port,
                                     baudrate=self._baudrate,
                                     bytesize=self._bytesize,
                                     stopbits=self._stopbits,
                                     parity=self._parity,
                                     rtscts=self._rtscts,
                                     xonxoff=self._xonxoff,
                                     timeout=self._timeout)
         self._is_connected = True
      except Exception as reason:
         # BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_ERROR)
         raise BrokenConnError("Not possible to connect. Reason: '%s'" % (str(reason)))

      BuiltIn().log("connected to COM%s@%s (%s,%s,%s) rtscts=%s xonxoff=%s" % (self._port,
                                                                              self._baudrate,
                                                                              self._bytesize,
                                                                              self._parity,
                                                                              self._stopbits,
                                                                              self._rtscts,
                                                                              self._xonxoff), constants.LOG_LEVEL_INFO)
