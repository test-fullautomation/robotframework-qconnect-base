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
# File: raw_tcp.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / May 2021.
# Based on lib/TCP/Base/CSimpleSocket.py in TML Framework.
#
# Description:
#   Provide the class for Raw TCP client and server connection.
#
# History:
#
# 12.05.2021 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from __future__ import with_statement
from QConnectBase.tcp.tcp_base import BrokenConnError, TCPBase, TCPBaseServer, TCPBaseClient


class RawTCPBase(TCPBase):
   """
Base class for a raw tcp connection.
   """
   def _read(self):
      """
Actual method to read message from a tcp connection.

**Returns:**
         Empty string.
      """
      data = ''
      while 1:
         data = data + self.conn.recv(1).decode(self.config.encoding, 'ignore')

         # Simple socket expects \r\n for terminating a message
         if data[(eol:=-2):] == "\r\n" or data[(eol:=-1):] == "\n":
            break

         if data == '':
            raise BrokenConnError("socket connection broken")

      # remove \r\n or \n
      data = data[:eol]
      return data

   def _send(self, msg, cr):
      """
Actual method to send message to a tcp connection.

**Arguments:**

* ``obj``

  / *Condition*: required / *Type*: str /

  Data to be sent.

* ``cr``

  / *Condition*: optional / *Type*: str /

  Determine if it's necessary to add newline character at the end of command.

**Returns:**

(*no returns*)
      """
      sent = 0
      with self._send_lock:
         while sent < len(msg):
            sent += self.conn.send(msg[sent:].encode(self.config.encoding))
         if cr and msg != "":
            self.conn.send("\r\n".encode(self.config.encoding))


class RawTCPServer(TCPBaseServer, RawTCPBase):
   """
Class for a raw tcp connection server.
   """
   _CONNECTION_TYPE = "TCPIPServer"

   def __init__(self, mode=None, config=None):
      """
Constructor of RawTCPServer class.

**Arguments:**

* ``mode``

  / *Condition*: optional / *Type*: str / *Default*: None /

  TCP mode.

* ``config``

  / *Condition*: optional / *Type*: dict / *Default*: None /

  Configuration for TCP connection in dictionary format.
      """
      super(RawTCPServer, self).__init__(mode, config)
      self._bind()


class RawTCPClient(TCPBaseClient, RawTCPBase):
   """
Class for a raw tcp connection client.
   """
   _CONNECTION_TYPE = "TCPIPClient"

   def __init__(self, mode=None, config=None):
      """
Constructor of RawTCPClient class.

**Arguments:**

* ``mode``

  / *Condition*: optional / *Type*: str / *Default*: None /

  TCP mode.

* ``config``

  / *Condition*: optional / *Type*: dict / *Default*: None /

  Configuration for TCP connection in dictionary format.
      """
      super(RawTCPClient, self).__init__(mode, config)
