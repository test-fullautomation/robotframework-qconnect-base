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
# File: ssh_client.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / May 2021.
# Based on lib/TCP/SSH/CSSHClient.py in TML Framework.
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
from robot.libraries.BuiltIn import BuiltIn
import threading
from inspect import currentframe
import QConnectBase.constants as constants
import time
import queue
import paramiko
from QConnectBase.tcp.tcp_base import BrokenConnError, TCPBaseClient, TCPBase, TCPConfig
import os
import re

class AuthenticationType:
   KEYFILE = 'keyfile'
   PASSWORD = 'password'
   PASSWORDKEYFILE = 'passwordkeyfile'


class SSHConfig(TCPConfig):
   """
Class to store the configuration for SSH connection.
   """
   address = 'localhost'
   port = 22
   username = 'root'
   password = ''
   authentication = 'password'
   key_filename = None


class SSHClient(TCPBase, TCPBaseClient):
   """
SSH client connection class.
   """
   _CONNECTION_TYPE = "SSHClient"

   def __init__(self, _mode, config):
      """
Constructor for SSHClient class.

**Arguments:**

* ``_mode``

  / *Condition*: required / *Type*: str /

  Unused

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Configurations for SSH Client.
      """
      # paramiko.SSHClient.__init__(self)
      # CVirtualSocket.__init__(self, address, port)
      self._llrecv_thrd_obj = None
      self.chan = None
      self.client = None

      self.config = SSHConfig(**config)
      config_tcp = {
         'address': self.config.address,
         'port': self.config.port,
         'logfile': self.config.logfile
      }

      self._username = self.config.username
      self._password = self.config.password
      self._key_filename = self.config.key_filename
      self._authentication = self.config.authentication

      # create the queue for this connection
      self.SSHq = queue.Queue()

      # configure and initialize the low-level receiver thread
      self._llrecv_thrd_term = threading.Event()
      super(SSHClient, self).__init__(_mode, config_tcp)
      self._init_thrd_llrecv(TCPBase._socket_instance)


   def _thrd_llrecv_from_connection_interface(self):
      """
Implementation the thread for getting data from ssh connection.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log("%s: low-level receiver thread started." % _mident, constants.LOG_LEVEL_DEBUG)
      while self.chan is None and not self._llrecv_thrd_term.isSet():
         time.sleep(TCPBase.RECV_MSGS_POLLING_INTERVAL)

      while self.chan is not None and not self._llrecv_thrd_term.isSet():
         data = ''
         while len(data) == 0:
            while self.chan.recv_ready() and not self.chan.closed:
               # data = data + self.chan.recv(1)
               recv = self.chan.recv(1)
               data = data + recv.decode(self.config.encoding, 'ignore')

            for character in data:
               self.SSHq.put(character)

            if self.chan.closed is True:
               break

            time.sleep(TCPBase.RECV_MSGS_POLLING_INTERVAL)

      # _read must have chance to terminate, too,therefore
      # wait here 5 times polling interval
      time.sleep(TCPBase.RECV_MSGS_POLLING_INTERVAL * 5)
      self._llrecv_thrd_term.clear()
      BuiltIn().log("%s: lowlevel receiver thread terminated." % _mident, constants.LOG_LEVEL_DEBUG)


   def connect(self):
      """
Implementation for creating a SSH connection.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      TCPBaseClient.connect(self)

      # for debugging
      # paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
      # Connects to the SSH service (address, port)
      # The socket is created by CVirtualClient.connect
      # If authentication mode is 'publickey', the list of key files is used. If the key files are encrypted with a pass phrase, password is used as the pass phrase

      self.client = paramiko.SSHClient()
      BuiltIn().log("%s: starting SSHClient..." % _mident, constants.LOG_LEVEL_DEBUG)
      self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      BuiltIn().log("%s: setting SSH policy..." % _mident, constants.LOG_LEVEL_DEBUG)

      # To reset the flag set by CVirtualClient.connect
      self._is_connected = False
      try:
         max_try = 5
         while max_try > 0:
            try:
               if self._authentication == AuthenticationType.KEYFILE:
                  BuiltIn().log("%s: trying to establish keyfile based SSH connection..." % _mident, constants.LOG_LEVEL_DEBUG)
                  self.client.connect(sock=self.socket, hostname=self._address, username=self._username, key_filename=self._key_filename, timeout=30.0, allow_agent=False)
               elif self._authentication == AuthenticationType.PASSWORD:
                  BuiltIn().log("%s: trying to establish password based SSH connection..." % _mident, constants.LOG_LEVEL_DEBUG)
                  self.client.connect(sock=self.socket, hostname=self._address, username=self._username, password=self._password, timeout=30.0, allow_agent=False)
               elif self._authentication == AuthenticationType.PASSWORDKEYFILE:
                  BuiltIn().log("%s: trying to establish password and keyfile based SSH connection..." % _mident, constants.LOG_LEVEL_DEBUG)
                  # From http://docs.paramiko.org/en/1.13/api/client.html
                  # Authentication is attempted in the following order of priority:
                  # 1. The pkey or key_filename passed in (if any)
                  # 2. Any key we can find through an SSH agent
                  # 3. Any "id_rsa" or "id_dsa" key discoverable in ~/.ssh/
                  # 4. Plain username/password auth, if a password was given
                  #
                  # If a private key requires a password to unlock it, and a password is passed in,
                  # that password will be used to attempt to unlock the key.
                  self.client.connect(sock=self.socket, hostname=self._address, username=self._username, password=self._password, key_filename=self._key_filename, timeout=30.0,
                                      allow_agent=False)
               else:  # other authentication
                  raise BrokenConnError("Authentication '%s' is not supported." % self._authentication)
            except Exception as e:
               if str(e) == 'Error reading SSH protocol banner':
                  max_try -= 1
                  if max_try == 0:
                     raise e
                  time.sleep(1)
               else:
                  raise e
            else:
               break

         BuiltIn().log("%s: successfully established SSH connection on existing TCPIP socket." % _mident, constants.LOG_LEVEL_DEBUG)
         self._is_connected = True

      except Exception as reason:
         BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_ERROR)
         raise BrokenConnError("Not possible to connect. Reason: '%s'" % reason)

      # per default a SSH connection is only usesd for one command, then
      # it will be reset.
      # for TML we need a permanent session that we can do e.g.
      # cd /to/somewhere
      # and then the next command will start in /to/somewhere.
      # Therefore we need to open a shell.
      self.chan = self.client.invoke_shell()
      BuiltIn().log("%s: successfully invoked SSH shell for secure communication." % _mident, constants.LOG_LEVEL_DEBUG)

      # switch echo off for this terminal
      # echo disturbs when the command contains part of the exepcted reponse, then regexp filtering will
      # fetch the command instead of the response.
      # Therefore remove echo of the terminal.
      # Sporadically still echo was active. Repeating the command stopped this behaviour.
      self.chan.send("stty -echo\n")
      self.chan.send("stty -echo\n")
      self.chan.send("stty -echo\n")
      self.chan.send("echo Echo Is Deactivated Now\n")
      # give echo deactivation a little time
      time.sleep(0.05)


   def transfer_file(self, src, dest, transfer_type):
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

* ``transfer_type``

  / *Condition*: required / *Type*: str /

  Transfer file type.

      'get' - Copy a remote file from the SFTP server to the local host

      'put' - Copy a local file to the SFTP server

**Returns:**

(*no returns*)
      """
      try:
         sftp = self.client.open_sftp()
         self._transfer_file(sftp, src, dest, transfer_type)
         sftp.close()
      except Exception as ex:
         raise Exception(f"Exception occurs while transferring '{src}'. Details: '{ex}'")

   def _transfer_file(self, sftp, src, dest, transfer_type):
      """
Performs the actual file transfer between the local file system and the SFTP server.

**Arguments:**

* ``sftp``

  / *Condition*: required / *Type*: paramiko.SFTPClient /

  An active SFTP client instance used to perform file operations on the remote server.

* ``src``

  / *Condition*: required / *Type*: str /

  Source file path.

* ``dest``

  / *Condition*: required / *Type*: str /

  Destination file path.

* ``transfer_type``

  / *Condition*: required / *Type*: str /

  Transfer file type.

      'get' - Copy a remote file from the SFTP server to the local host

      'put' - Copy a local file to the SFTP server

**Returns:**

(*no returns*)
      """
      try:
         method_dict = {
            'put': sftp.put,
            'get': sftp.get
         }
         method_dict[transfer_type](src, dest)
      except Exception as ex:
         raise Exception(f"Exception occurs while transferring '{src}'. Details: '{ex}'")

   def transfer_item(self, src, dest, transfer_type):
      """
Transfer item from local to remote and vice versa.

**Arguments:**

* ``src``

  / *Condition*: required / *Type*: str /

  Source item path.

* ``dest``

  / *Condition*: required / *Type*: str /

  Destination item path.

* ``transfer_type``

  / *Condition*: required / *Type*: str /

  Transfer item type.

      'get' - Copy a remote item from the SFTP server to the local host

      'put' - Copy a local item to the SFTP server

**Returns:**

(*no returns*)
      """
      try:
         sftp = self.client.open_sftp()
         self._transfer(sftp, src, dest, transfer_type)
      except Exception as ex:
         raise Exception(f"Exception occurs while transferring '{src}'. Details: '{ex}'")
      finally:
         sftp.close()

   def _transfer(self, sftp, src, dest, transfer_type):
      """
Performs the actual file or folder transfer between the local file system and the SFTP server.

This function is a helper for `transfer_item` and handles the low-level operations
for transferring individual files or directories.
It ensures that files are copied correctly and directories are created as needed.

**Arguments:**

* ``sftp``

  / *Condition*: required / *Type*: paramiko.SFTPClient /

  An active SFTP client instance used to perform file and folder operations on the remote server.

* ``src``

  / *Condition*: required / *Type*: str /

  Source item path.

* ``dest``

  / *Condition*: required / *Type*: str /

  Destination item path.

* ``transfer_type``

  / *Condition*: required / *Type*: str /

  Transfer type.

      'get' - Copy a remote item from the SFTP server to the local host

      'put' - Copy a local item to the SFTP server

**Returns:**

(*no returns*)
      """
      if transfer_type not in ['get', 'put']:
         raise Exception(f"Unknown transfer type '{transfer_type}'.")

      stat_ifmt = 0o170000  # File type mask
      stat_ifdir = 0o040000  # Directory type
      folder_name_pattern = r'[^/\\]+(?=[/\\]*$)'
      folder_name = ''
      match = re.search(folder_name_pattern, src)
      if match:
         folder_name = match.group(0)
      BuiltIn().log(f"Transfer from '{src}' to '{dest}' with transfer type '{transfer_type}'", constants.LOG_LEVEL_DEBUG)
      if transfer_type == 'put':
         # Check if it's a directory
         if os.path.isdir(src):
            dest_folder_path = os.path.normpath(f"{dest}{os.sep}{folder_name}").replace('\\', '/')
            try:
               sftp.stat(dest_folder_path)
            except FileNotFoundError:
               BuiltIn().log(f"Creating destination folder: '{dest_folder_path}'", constants.LOG_LEVEL_DEBUG)
               try:
                  # Create destination directory on the remote server
                  sftp.mkdir(dest_folder_path)
               except Exception as ex:
                  raise Exception(f"Failed to create destination folder '{dest_folder_path}'. Details: '{ex}'")
            for item in os.listdir(src):
               src_item_path = os.path.normpath(f"{src}{os.sep}{item}").replace('\\', '/')
               if os.path.isdir(src_item_path):
                  BuiltIn().log(f"Transferring folder: '{src_item_path}' to '{dest_folder_path}'", constants.LOG_LEVEL_DEBUG)
                  self._transfer(sftp, src_item_path, dest_folder_path, transfer_type)
               else:
                  BuiltIn().log(f"Transferring file: '{src_item_path}' to '{dest_folder_path}'", constants.LOG_LEVEL_DEBUG)
                  dest_item_path = f"{dest_folder_path}{os.sep}{item}".replace('\\', '/')
                  self._transfer_file(sftp, src_item_path, dest_item_path, transfer_type)
         else:
            # Transfer a single file
            item = folder_name
            dest_item_path = f"{dest}{os.sep}{item}".replace('\\', '/')
            BuiltIn().log(f"Transferring file: '{src}' to '{dest}'", constants.LOG_LEVEL_DEBUG)
            self._transfer_file(sftp, src, dest_item_path, transfer_type)
      elif transfer_type == 'get':
         # Check if it's a directory
         if sftp.stat(src).st_mode & stat_ifmt == stat_ifdir:
            match = re.search(folder_name_pattern, src)
            if match:
               folder_name = match.group(0)
            dest_folder_path = os.path.normpath(f"{dest}{os.sep}{folder_name}").replace('\\', '/')
            if not os.path.exists(dest_folder_path):
               BuiltIn().log(f"Creating destination folder: '{dest_folder_path}'", constants.LOG_LEVEL_DEBUG)
               try:
                  # Create destination directory on the local
                  os.makedirs(dest_folder_path, exist_ok=True)
               except Exception as ex:
                  raise Exception(f"Failed to create destination folder '{dest_folder_path}'. Details '{ex}'")
            for item in sftp.listdir(src):
               src_item_path = os.path.normpath(f"{src}{os.sep}{item}").replace('\\', '/')
               if sftp.stat(src_item_path).st_mode & stat_ifmt == stat_ifdir:
                  BuiltIn().log(f"Transferring folder: '{src_item_path}' to '{dest_folder_path}'", constants.LOG_LEVEL_DEBUG)
                  self._transfer(sftp, src_item_path, dest_folder_path, transfer_type)
               else:
                  BuiltIn().log(f"Transferring file: '{src_item_path}' to '{dest_folder_path}'", constants.LOG_LEVEL_DEBUG)
                  dest_item_path = f"{dest_folder_path}{os.sep}{item}".replace('\\', '/')
                  self._transfer_file(sftp, src_item_path, dest_item_path, transfer_type)
         else:
            item = folder_name
            dest_item_path = f"{dest}{os.sep}{item}".replace('\\', '/')
            BuiltIn().log(f"Transferring file: '{src}' to '{dest}'", constants.LOG_LEVEL_DEBUG)
            self._transfer_file(sftp, src, dest_item_path, transfer_type)

   def _send(self, msg, _cr):
      """
Send message to SSH connection.

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
      # noinspection PyBroadException
      try:
         _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
         BuiltIn().log("%s: sending: '%s'" % (_mident, msg), constants.LOG_LEVEL_DEBUG)
         with self._send_lock:
            self.chan.send(self._rm_q_dollar(str(msg)) + "\n")
      except Exception as _reason:
         self._is_connected = False

   def _read(self):
      """
Read data from SSH connection.

**Returns:**

  / *Type*: str /

  Data from SSH connection.
      """
      data = ''

      # We read the data here from the queue filled by the
      # low-level receiver thread.
      while data[-2:] != '\r\n' and not self._llrecv_thrd_term.isSet():
         try:
            d = self.SSHq.get(block=False)

            if data[-2:] != '\r\n':
               data = data + d
         except queue.Empty:
            # non blocking get from SSHq causes that
            # Queue.Empty exception. In this case wait some milliseconds before
            # retry
            time.sleep(TCPBase.RECV_MSGS_POLLING_INTERVAL)

      data = data[:-2]

      return self._q_dollar(data)

   def close(self):
      """
Close SSH connection.

**Returns:**

(*no returns*)
      """
      # shutdown SSHClient
      if self.chan is not None:
         self.chan.close()
      if self.client is not None:
         self.client.close()

      # Execute parents close()
      super(SSHClient, self).close()

   def quit(self):
      """
Quit and stop receiver thread.

**Returns:**

(*no returns*)
      """
      # stop the low-level receiver thread
      if self._llrecv_thrd_obj and self._llrecv_thrd_obj.is_alive():
         self._llrecv_thrd_term.set()

      self._llrecv_thrd_obj = None
      self.close()
      super(SSHClient, self).quit()



if __name__ == "__main__":
   # address = "172.17.0.11"
   # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   # sock.connect((address, 22))
   # client = paramiko.SSHClient()
   # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   # try:
   #    client.connect(sock=sock, hostname=address, username='root', password='', timeout=30.0, allow_agent=False)
   #    chan = client.invoke_shell()
   #    chan.send("ls")
   #    a = chan.recv(9999)
   #    a = chan.recv(9999)
   #    print(a)
   # except Exception as ex:
   #    print(ex)
   _DEFAULT_CONFIG = {
      'address': '172.17.0.11',
      'port': 22,
      'username': 'root',
      'password': '',
      'authentication': 'password',
      'key_filename': None
   }
   # a = SSHConfig(**_DEFAULT_CONFIG)
   # print(a)
   ssh = SSHClient(None, _DEFAULT_CONFIG)
   ssh.connect()
   ssh.send_obj("cd ..")
   ssh.send_obj("ls")
   a = ssh.read_obj()
   print(a)
