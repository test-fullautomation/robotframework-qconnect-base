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
# File: connection_base.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / May 2021.
# Based on \lib\TCP\CTCPMultiQueued.py in TML Framework.
#
# Description:
#   Provide the infrastructure for sending commands and getting traces from connection continuously.
#
# History:
#
# 12.05.2021 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from abc import ABCMeta
from inspect import currentframe
from collections import deque
from robot.libraries.BuiltIn import BuiltIn
from QConnectBase.qlogger import QLogger
import QConnectBase.constants as constants
import queue
import abc
import time
import platform
import threading
import re

_platform = platform.system().lower()


class BrokenConnError(Exception):
   pass


class ConnectionBase(object):
   """
Base class for all connection classes.
   """
   __metaclass__ = ABCMeta
   _SUPPORTED_PLATFORM_LIST = [constants.OS_WINDOWS_STR,
                               constants.OS_LINUX_STR]
   _CONNECTION_TYPE = "NotSupported"
   _ERROR_INSTRUCTION = constants.UNKNOWN_STR

   MAX_LEN_BACKTRACE = 500  # Lines

   RECV_MSGS_POLLING_INTERVAL = 0.005

   _call_thrd_obj = None
   _call_thrd_init = threading.Event()
   _call_thrd_term = threading.Event()

   _recv_thrd_obj = None
   # _recv_thrd_term = threading.Event()
   _recv_thrd_term = None

   _force_seq_lock = threading.RLock()
   _start_dlt_lock = threading.RLock()

   _traceq_handle = 0
   supported_devices = []

   # # for continuous processing
   # _msgq_c_handle = 0
   # _msgq_c_obj = {}
   # _msgq_c_lock = threading.Lock()


   _is_precondition_valid = True
   _should_check_timeout = False

   _logger = None
   _logger_handler = None
   config = None
   def __new__(cls, *args, **kwargs):
      """
Override creating instance method to check for conditions.

**Arguments:**

* ``args``

  / *Condition*: require / *Type*: tuple /

  Non-Keyword Arguments.

* ``kwargs``

  / *Condition*: require / *Type*: dict /

  Keyword Arguments.

**Returns:**

  / *Type*: ConnectionBase /

  ConnectionBase instance if passing the conditions.\
  None if failing the conditions.
      """
      if (not cls.is_supported_platform()) or (not cls.is_precondition_pass()):
         return None
      return super(ConnectionBase, cls).__new__(cls)

   # region GENERAL METHODS
   @classmethod
   def is_supported_platform(cls):
      """
Check if current platform is supported.

**Returns:**

  / *Type*: bool /

  True if platform is supported.

  False if platform is not supported.
      """
      return _platform in cls._SUPPORTED_PLATFORM_LIST

   @classmethod
   def is_precondition_pass(cls):
      """
Check for precondition.

**Returns:**

  / *Type*: bool /

  True if passing the precondition.

  False if failing the precondition.
      """
      return cls._is_precondition_valid

   @classmethod
   def get_connection_type(cls):
      """
Get the connection type.

**Returns:**

  / *Type*: str /

  The connection type.
      """
      return cls._CONNECTION_TYPE

   def error_instruction(self):
      """
Get the error instruction.

**Returns:**

  / *Type*: str /

  Error instruction string.
      """
      return self._ERROR_INSTRUCTION
   # endregion

   # region MUST BE OVERRIDE METHODS
   @abc.abstractmethod
   def quit(self, is_disconnect_all=True):
      """
>> This method MUST be overridden in derived class <<

Abstract method for quiting the connection.

**Arguments:**

* ``is_disconnect_all``

  / *Condition*: optional / *Type*: bool /

  Determine if it's necessary to disconnect all connections.

**Returns:**

(*no returns*)
      """
      if self._logger:
         self._logger.removeHandler(self._logger_handler)

   @abc.abstractmethod
   def connect(self, device, files=None, test_connection=False):
      """
>> This method MUST be overridden in derived class <<

Abstract method for quiting the connection.

**Arguments:**

* ``device``

  / *Condition*: required / *Type*: str /

  Device name.

* ``files``

  / *Condition*: optional / *Type*: list /

  Trace file list if using dlt connection.

* ``test_connection``

  / *Condition*: optional / *Type*: bool /

  Deternmine if it's necessary for testing the connection.

**Returns:**

(*no returns*)
      """
      pass


   @abc.abstractmethod
   def disconnect(self, device):
      """
>> This method MUST be overridden in derived class <<

Abstract method for disconnecting connection.

**Arguments:**

* ``device``

  / *Condition*: required / *Type*: str /

  Device's name.

**Returns:**

(*no returns*)
      """
      pass
   # endregion

   # region RECEIVER THREAD METHODS
   def _init_thrd_llrecv(self, n_thrd_id):
      """
Start a thread which receive message from connection continuously.

**Arguments:**


         n_thrd_id: thread id.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      self._llrecv_thrd_obj = threading.Thread(target=self._thrd_llrecv_from_connection_interface)
      self._llrecv_thrd_obj.setDaemon(True)
      self._llrecv_thrd_obj.name = str(self._CONNECTION_TYPE) + "-" + str(n_thrd_id)
      BuiltIn().log("%s: starting low-level receiver thread '%s'" % (_mident, self._llrecv_thrd_obj.name), constants.LOG_LEVEL_DEBUG)
      self._llrecv_thrd_obj.start()

   def _thrd_llrecv_from_connection_interface(self):
      """
>> This method will be override in derived class << \
The thread which receive message from connection continuously.

**Returns:**

(*no returns*)
      """
      pass

   def _init_thread_receiver(self, thread_id, mode=None, sync_with_start=False):
      """
Initialize a thread for receiving data from connection.

**Arguments:**

* ``thread_id``

  / *Condition*: required / *Type*: int /

  Thread ID number.

* ``mode``

  / *Condition*: optional / *Type*: str /

  Connection's mode.

* ``sync_with_start``

  / *Condition*: optional / *Type*: bool /

  Determine if receiving thread needs to wait for start event.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      thread_name = self._CONNECTION_TYPE
      if mode is not None:
         thread_name = mode

      if hasattr(self, 'connection_name'):
         thread_name = self.connection_name


      conn_id_name = str(thread_name) + '-' + str(thread_id)
      self._logger = QLogger().get_logger(conn_id_name)
      self._logger_handler = QLogger().set_handler(self.config)

      self._traceq_obj = {}
      self._traceq_lock = threading.Lock()


      self._recv_thrd_term = threading.Event()
      self._recv_thrd_obj = threading.Thread(target=self._thread_receive_from_connection, kwargs=dict(sync_with_start=sync_with_start))
      self._recv_thrd_obj.setDaemon(True)

      self._recv_thrd_obj.name = conn_id_name
      BuiltIn().log("%s: starting receiver thread '%s'" % (_mident, self._recv_thrd_obj.name), constants.LOG_LEVEL_DEBUG)
      self._recv_thrd_obj.start()

   def _thread_receive_from_connection(self, sync_with_start=False):
      """
Thread to receive data from connection continuously.

**Arguments:**

* ``sync_with_start``

  / *Condition*: optional / *Type*: bool /

  Determine if receiving thread needs to wait for start event.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      if sync_with_start is True:
         BuiltIn().log("%s: receiver thread is waiting to start." % _mident, constants.LOG_LEVEL_DEBUG)
         while not self._recv_thrd_start.isSet():
            time.sleep(self.__class__.RECV_MSGS_POLLING_INTERVAL)

      BuiltIn().log("%s: receiver thread started." % _mident, constants.LOG_LEVEL_DEBUG)
      while not self._recv_thrd_term.isSet():
         try:
            msg = self.read_obj()
            if self._should_check_timeout:
               self.check_timeout(msg)

            if msg is not None:
               self._should_check_timeout = False
               self.pre_msg_check(msg)
               BuiltIn().log(msg, constants.LOG_LEVEL_INFO)
               if self._logger:
                  self._logger.info(msg)
               # with self._msgq_c_lock:
               #    now = time.time()
               #    for q in self._msgq_c_obj.values():
               #       q.put((now, msg), False)

               with self._traceq_lock:
                  if self._traceq_obj:
                     for (regex_filter, msg_queue, back_trace_queue, use_fetch_block, regex_end_block_pattern, regex_line_filter) in self._traceq_obj.values():
                        is_hit = False
                        result_obj = None
                        if use_fetch_block is True:
                           matchObj = regex_line_filter.search(msg)
                           if matchObj is not None:
                              back_trace_queue.append(msg)
                              # BuiltIn().log_to_console(msg)
                              if regex_end_block_pattern and regex_end_block_pattern.pattern != ".*":
                                (is_hit, result_obj) = self._filter_msg(regex_end_block_pattern, msg)
                              else:
                                # BuiltIn().log_to_console(regex_filter.pattern)
                                # BuiltIn().log_to_console(msg)
                                # BuiltIn().log_to_console("\r\n".join(back_trace_queue))
                                (is_hit, result_obj) = self._filter_msg(regex_filter, "\n".join(back_trace_queue))
                        else:
                           (is_hit, result_obj) = self._filter_msg(regex_filter, msg)
                        if is_hit:
                           now = time.time()
                           if use_fetch_block is True and regex_end_block_pattern.pattern != ".*":
                              result_obj = regex_filter.search("\r\n".join(back_trace_queue))
                              back_trace_queue.clear()
                           msg_queue.put((now, result_obj), False)
               self.post_msg_check(msg)
         except BrokenConnError as reason:
            BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_DEBUG)
            self._broken_conn.set()
            break
         except Exception as reason:
            BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_WARNING)
         time.sleep(self.__class__.RECV_MSGS_POLLING_INTERVAL)

      self._recv_thrd_term.clear()
      BuiltIn().log("%s: receiver thread terminated." % _mident, constants.LOG_LEVEL_DEBUG)


   def send_obj(self, send_cmd, cr=True, **kwargs):
      """
Wrapper method to send message to a tcp connection.

**Arguments:**

* ``send_cmd``

  / *Condition*: required / *Type*: str /

  Data to be sent.

* ``cr``

  / *Condition*: optional / *Type*: str /

  Determine if it's necessary to add newline character at the end of command.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      msg = send_cmd
      if self._is_connected:
         # noinspection PyBroadException
         try:
            BuiltIn().log("%s: sending: '%s'" % (_mident, msg), constants.LOG_LEVEL_DEBUG)
            self._send(msg, cr)
         except Exception as ex:
            self._is_connected = False
            raise BrokenConnError(f"Connection has been broken. Details: {ex}")

   def read_obj(self):
      """
Wrapper method to get the response from connection.

**Returns:**

* ``msg``

  / *Type*: str /

  Responded message.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('%s' % _mident, constants.LOG_LEVEL_DEBUG)
      msg = None
      if self._is_connected:
         try:
            BuiltIn().log("%s: reading..." % _mident, constants.LOG_LEVEL_DEBUG)
            msg = self._read()
            BuiltIn().log("%s: read: '%s'" % (_mident, msg), constants.LOG_LEVEL_DEBUG)
         except BrokenConnError as reason:
            BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_ERROR)
            self._is_connected = False
            raise reason
         except Exception as reason:
            BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_DEBUG)
      return msg
   # endregion

   # region TRACE INFRASTRUCTURE METHODS
   def wait_4_trace(self, search_obj, timeout=0, use_fetch_block=False, end_of_block_pattern=".*", filter_pattern=".*", **fct_args):
      """
Suspend the control flow until a Trace message is received which matches to a specified regular expression.

**Arguments:**

* ``search_obj``

  / *Condition*: required / *Type*: str /

  Regular expression all received trace messages are compare to.
  Can be passed either as a string or a regular expression object. Refer to Python documentation for module 're'.

* ``use_fetch_block``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  Determine if 'fetch block' feature is used.

* ``end_of_block_pattern``

  / *Condition*: optional / *Type*: str / *Default*: '.*' /

  The end of block pattern.

* ``filter_pattern``

  / *Condition*: optional / *Type*: str / *Default*: '.*' /

  Pattern to filter message line by line.

* ``timeout``

  / *Condition*: optional / *Type*: int / *Default*: 0 /

  Timeout parameter specified as a floating point number in the unit 'seconds'.

* ``fct_args``

  / *Condition*: optional / *Type*: Tuple /  *Default*: None /

  List of function arguments passed to be sent.

**Returns:**

* ``match``

  / *Type*: re.Match /

  If no trace message matched to the specified regular expression and a timeout occurred, return None.

  If a trace message has matched to the specified regular expression, a match object is returned as the result.The complete trace message can be accessed by the 'string' attribute of the match object. For access to groups within the regular expression, use the group() method. For more information, refer to Python documentation for module 're'.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('Execute %s' % _mident, constants.LOG_LEVEL_DEBUG)
      if search_obj is None:
         raise Exception("The 'search_pattern' have to be a regex string instead of None.")
      search_regex = re.compile(search_obj, re.M | re.S | re.U)
      regex_obj_filter = re.compile(filter_pattern)
      trq_handle, trace_queue = self.create_and_activate_trace_queue(search_regex, use_fetch_block, end_of_block_pattern, regex_obj_filter)

      try:
         self.send_obj(**fct_args)
      except BrokenConnError:
         raise Exception("Connection has been broken while trying to match the pattern.")
      except Exception as err_msg:  # pylint: disable=W0703
         BuiltIn().log('%s: An Exception occurred executing function object: %s' % (_mident, repr(self.send_obj)), 'ERROR')
         BuiltIn().log('Function Arguments: %s' % repr(fct_args), 'ERROR')
         BuiltIn().log('Error Message: %s' % repr(err_msg), 'ERROR')
      success = True
      match = None
      try:
         (dummy, match) = trace_queue.get(True, timeout)
      except queue.Empty:
         success = False
      finally:
         self.deactivate_and_delete_trace_queue(trq_handle, trace_queue)

      BuiltIn().log('Completed %s' % _mident, constants.LOG_LEVEL_DEBUG)
      if success:
         return match
      else:
         return None


   def wait_4_trace_continuously(self, trace_queue, timeout=0, *fct_args):
      """
Getting trace log continuously without creating a new trace queue.

**Arguments:**


* ``trace_queue``

  / *Condition*: required / *Type*: Queue /

  Queue to store the traces.

* ``timeout``

  / *Condition*: optional / *Type*: int / *Default*: 0 /

  Timeout for waiting a matched log.

* ``fct_args``

  / *Condition*: optional / *Type*: Tuple / *Default*: None /

  Arguments to be sent to connection.

**Returns:**

* ``None``

  / *Type*: None /

  If no trace message matched to the specified regular expression and a timeout occurred.

* ``match``

  / *Type*: re.Match /

  If a trace message has matched to the specified regular expression, a match object is returned as the result.The complete trace message can be accessed by the 'string' attribute of the match object. For access to groups within the regular expression, use the group() method. For more information, refer to Python documentation for module 're'.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('Execute %s' % _mident, constants.LOG_LEVEL_DEBUG)
      try:
         self.send_obj(*fct_args)
      except Exception as err_msg:  # pylint: disable=W0703
         BuiltIn().log('%s: An Exception occurred executing function object: %s' % (_mident, repr(self.send_obj)), 'ERROR')
         BuiltIn().log('Function Arguments: %s' % repr(fct_args), 'ERROR')
         BuiltIn().log('Error Message: %s' % repr(err_msg), 'ERROR')

      success = True
      match = None
      try:
         if trace_queue is not None:
            (dummy, match) = trace_queue.get(True, timeout)
      except queue.Empty:
         success = False

      BuiltIn().log('Completed %s' % _mident, constants.LOG_LEVEL_DEBUG)
      if success:
         return match
      else:
         return None

   # @classmethod
   def create_and_activate_trace_queue(self, search_element, use_fetch_block=False, end_of_block_pattern='.*', regex_line_filter_pattern=None):
      """
Create Queue and assign it to _trace_queue object and activate the queue with the search element.

**Arguments:**

* ``search_element``

  / *Condition*: required / *Type*: str /

  Regular expression all received trace messages are compare to.

  Can be passed either as a string or a regular expression object. Refer to Python documentation for module 're'.#

* ``use_fetch_block``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  Determine if 'fetch block' feature is used.

* ``end_of_block_pattern``

  / *Condition*: optional / *Type*: str / *Default*: '.*' /

  The end of block pattern.

* ``regex_line_filter_pattern``

  / *Condition*: optional / *Type*: re.Pattern / *Default*: None /

  Regular expression object to filter message line by line.

**Returns:**

* ``trq_handle, trace_queue``

  / *Type*: tuple /

  The handle and search object
      """
      trace_queue = queue.Queue()
      trq_handle = self.activate_trace_queue(search_element, trace_queue, use_fetch_block, end_of_block_pattern, regex_line_filter_pattern)
      return trq_handle, trace_queue

   # @classmethod
   def deactivate_and_delete_trace_queue(self, trq_handle, trace_queue):
      """
Deactivate trace queue and delete.

**Arguments:**

* ``trq_handle``

  / *Condition*: required / *Type*: int /

  Trace queue handle.

* ``trace_queue``

  / *Condition*: required / *Type*: Queue /

  Trace queue object.

**Returns:**

(*no returns*)
      """
      self.deactivate_trace_queue(trq_handle)
      del trace_queue

   # @classmethod
   def activate_trace_queue(self, search_obj, trace_queue, use_fetch_block=False, end_of_block_pattern='.*', line_filter_pattern=None):
      """
Activates a trace message filter specified as a regular expression. All matching trace messages are put in the specified queue object.

**Arguments:**

* ``search_obj``

  / *Condition*: required / *Type*: str /

  Regular expression all received trace messages are compare to. \

  Can be passed either as a string or a regular expression object. Refer to Python documentation for module 're'.

* ``trace_queue``

  / *Condition*: required / *Type*: Queue /

  A queue object all trace message which matches the regular expression are put in. \

  The using application must assure, that the queue is emptied or deleted.

* ``use_fetch_block``

  / *Condition*: optional / *Type*: bool /  *Default*: False /

  Determine if 'fetch block' feature is used.

* ``end_of_block_pattern``

  / *Condition*: optional / *Type*: str / *Default*: '.*' /

  The end of block pattern.

* ``line_filter_pattern``

  / *Condition*: optional / *Type*: re.Pattern / *Default*: None /

  Regular expression object to filter message line by line.

**Returns:**

* ``handle_id``

  / *Type*: int /

  Handle to deactivate the message filter.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('Execute %s' % _mident, constants.LOG_LEVEL_DEBUG)
      with self._traceq_lock:
         self.__class__._traceq_handle += 1
         back_trace_queue = deque(maxlen=self.__class__.MAX_LEN_BACKTRACE)
         search_regex_obj = re.compile(search_obj)
         self._traceq_obj[self.__class__._traceq_handle] = (search_regex_obj,
                                                trace_queue,
                                                back_trace_queue,
                                                use_fetch_block,
                                                re.compile(end_of_block_pattern, re.M | re.S | re.U),
                                                line_filter_pattern)
         handle_id = self.__class__._traceq_handle
      BuiltIn().log('Completed %s' % _mident, constants.LOG_LEVEL_DEBUG)
      return handle_id

   # @classmethod
   def deactivate_trace_queue(self, handle):
      """
Deactivates a trace message filter previously activated by ActivateTraceQ() method.

**Arguments:**

* ``handle``

  / *Condition*: required / *Type*: int /

  Integer object returned by ActivateTraceQ() method.

**Returns:**

* ``is_success``

  / *Type*: bool /
 .
  False : No trace message filter active with the specified handle (i.e. handle is not in use).

  True :  Trace message filter successfully deleted.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('Execute %s' % _mident, constants.LOG_LEVEL_DEBUG)
      with self._traceq_lock:
         if handle in self._traceq_obj:
            del self._traceq_obj[handle]
            is_success = True
         else:
            is_success = False
      BuiltIn().log('Completed %s' % _mident, constants.LOG_LEVEL_DEBUG)
      return is_success

   def check_timeout(self, timeout):
      """
>> This method will be override in derived class <<

Check if responded message come in cls._RESPOND_TIMEOUT or we will raise a timeout event.

**Arguments:**

* ``timeout``

  / *Condition*: required / *Type*: int /

  Timeout in seconds.

**Returns:**

(*no returns*)
      """
      pass

   def pre_msg_check(self, msg):
      """
>> This method will be override in derived class <<

Pre-checking message when receiving it from connection.

**Arguments:**

* ``msg``

  / *Condition*: required / *Type*: str /

  Received message to be checked.

**Returns:**

(*no returns*)
      """
      pass

   def post_msg_check(self, msg):
      """
>> This method will be override in derived class <<

Post-checking message when receiving it from connection.

**Arguments:**

* ``msg``

  / *Condition*: required / *Type*: str /

  Received message to be checked.

**Returns:**

(*no returns*)
      """
      pass
   # endregion

   # region UTILITIES METHODS
   @staticmethod
   def _rm_q_dollar(input_):
      # noinspection PyBroadException
      try:
         output = input_.replace(r"\$(", "$(")
         output = output.replace(r"\${", "${")
      except:
         # in case of any issue return input as it is
         output = input_

      return output

   @staticmethod
   def _q_dollar(input_):
      # noinspection PyBroadException
      try:
         output = input_.replace("$(", r"\$(")
         output = output.replace("${", r"\${")
      except:
         # in case of any issue return input as it is
         output = input_

      return output

   def _filter_msg(self, regex_filter_obj, msg):
      """
Filter message by regular expression object.

**Arguments:**

* ``regex_filter_obj``

  / *Condition*: required / *Type*: re.Pattern /

  Regular expression object.

* ``msg``

  / *Condition*: required / *Type*: str /

  Message string to be filtered.

**Returns:**

* ``is_hit, matched_obj``

  / *Type*: tuple /

  is_hit: Determine if there is any matched.

  matched_obj: Matched object if exists.
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log(_mident, constants.LOG_LEVEL_DEBUG)
      matched_obj = None
      try:
         BuiltIn().log("%s: regex_filter_obj '%s'" % (_mident, repr(regex_filter_obj)), constants.LOG_LEVEL_DEBUG)
         BuiltIn().log("%s: msg '%s'" % (_mident, repr(msg)), constants.LOG_LEVEL_DEBUG)
         matched_obj = regex_filter_obj.search(msg)
      except Exception as reason:
         BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_ERROR)

      is_hit = False
      if matched_obj:
         is_hit = True
      return is_hit, matched_obj
   # endregion
