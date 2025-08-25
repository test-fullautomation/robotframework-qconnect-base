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
# File: utils.py
#
# Initially created by Cuong Nguyen (RBVH/ENG22) / July 2019
#
# Description:
#   Provide the utilities for supporting development.
#
# History:
#
# 22.07.2019 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from robot.libraries.BuiltIn import BuiltIn
import QConnectBase.constants as constants
import inspect
import threading
import platform
import json
import collections
import subprocess
from ctypes import *
sPlatform = platform.system().lower()


class Singleton(object):  # pylint: disable=R0903
   """
   Class to implement Singleton Design Pattern. This class is used to derive the TTFisClientReal as only a single
   instance of this class is allowed.

   Disabled pyLint Messages:
   R0903:  Too few public methods (%s/%s)
            Used when class has too few public methods, so be sure it's really worth it.

            This base class implements the Singleton Design Pattern required for the TTFisClientReal.
            Adding further methods does not make sense.
   """
   _instance = None
   _lock = threading.Lock()

   def __new__(cls, *args, **kwargs):
      with cls._lock:
         if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
      return cls._instance


class DictToClass:
   """
Class for converting dictionary to class object.
   """
   exclude_list = []
   logfile = None
   encoding = 'utf-8'

   def __init__(self, **dictionary):
      try:
         for k, v in dictionary.items():
            if isinstance(v, dict) and k not in self.__class__.exclude_list:
               self.__dict__[k] = DictToClass(**v)
            else:
               type_obj = type(None)
               if k in self.__class__.__dict__:
                  type_obj = type(self.__class__.__dict__[k])

               if type_obj is not type(None):
                  self.__dict__[k] = type_obj(v)
               else:
                  self.__dict__[k] = v
      except Exception as ex:
         raise Exception(f"The configuration 'conn_conf' is invalid. Details: {ex}")
      self.validate()

   def validate(self):
      pass


class Utils:
   """
Class to implement utilities for supporting development.
   """
   LINUX_OS = "linux"
   WINDOWS_OS = "windows"

   def __init__(self):
      """
Empty constructor.
      """
      pass

   @staticmethod
   def get_all_descendant_classes(cls, should_include_root_class=False):
      """
Get all descendant classes of a class

**Arguments:**
         cls: Input class for finding descendants.

**Returns:**

  / *Type*: list /

  Array of descendant classes.
      """
      trace_class_list = cls.__subclasses__()
      descendant_classes_list = []
      if should_include_root_class:
         descendant_classes_list.append(cls)
      for subclass in trace_class_list:
         descendant_classes_list.append(subclass)
         if len(subclass.__subclasses__()) > 0:
            trace_class_list.extend(subclass.__subclasses__())
      return set(descendant_classes_list)

   @staticmethod
   def get_all_sub_classes(cls):
      """
Get all children classes of a class

**Arguments:**

* ``cls``

  / *Condition*: required / *Type*: class /

  Input class for finding children.

**Returns:**

  / *Type*: list /

  Array of children classes.
      """
      return set(cls.__subclasses__()).union(
         [s for s in cls.__subclasses__()])

   @staticmethod
   def is_valid_host(address, port):
      import socket
      is_valid = False
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      result = sock.connect_ex((address, port))
      if result == 0:
         is_valid = True
      sock.close()
      return is_valid

   @staticmethod
   def execute_command(sCmd):
      if sPlatform.startswith(constants.OS_WINDOWS_STR):
         p = subprocess.Popen(sCmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      elif sPlatform.startswith(constants.OS_LINUX_STR):
         p = subprocess.Popen(sCmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
      (stdout, stderr) = p.communicate()
      return str(stdout)

   @staticmethod
   def kill_process(sProcessName):
      if sPlatform.startswith(constants.OS_WINDOWS_STR):
         res = Utils.execute_command("taskkill /im %s /f" % sProcessName)
      elif sPlatform.startswith(constants.OS_LINUX_STR):
         res = Utils.execute_command("kill -9 $(pgrep %s)" % sProcessName)

      sExt = ""
      if "error" in res.lower():
         sExt = " Most likely " + sProcessName + " was already shut down."

      BuiltIn().log("kill: '%s'" % (res.strip() + sExt), constants.LOG_LEVEL_INFO)

   @staticmethod
   def caller_name(skip=2):
      """
Get a name of a caller in the format module.class.method

**Arguments:**

* ``skip``

  / *Condition*: required / *Type*: int /

  Specifies how many levels of stack to skip while getting caller
         name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

**Returns:**

  / *Type*: str /

  An empty string is returned if skipped levels exceed stack height
      """
      stack = inspect.stack()
      start = 0 + skip
      if len(stack) < start + 1:
         return ''
      parent_frame = stack[start][0]

      name = []
      module = inspect.getmodule(parent_frame)
      # `modname` can be None when frame is executed directly in console
      # TODO(techtonik): consider using __main__
      if module:
         name.append(module.__name__)
      # detect classname
      if 'self' in parent_frame.f_locals:
         # I don't know any way to detect call from the object method
         # XXX: there seems to be no way to detect static method call - it will
         #      be just a function call
         name.append(parent_frame.f_locals['self'].__class__.__name__)
      codename = parent_frame.f_code.co_name
      if codename != '<module>':  # top level usually
         name.append(codename)  # function or a method
      del parent_frame
      return ".".join(name)

   @staticmethod
   def load_library(path, is_stdcall=True):
      """
Load native library depend on the calling convention.

**Arguments:**

* ``path``

  / *Condition*: required / *Type*: str /

  Library path.

* ``is_stdcall``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  Determine if the library's calling convention is stdcall or cdecl.

**Returns:**

*Loaded library object.*
      """
      try:
         if is_stdcall:
            res_dll = windll.LoadLibrary(path)
         else:
            res_dll = cdll.LoadLibrary(path)
      except Exception as ex:
         res_dll = None
         print("Unable load '%s'. Reason: %s" % (path, ex))
      finally:
         return res_dll

   @staticmethod
   def is_ascii_or_unicode(str_check, codecs=['utf8', 'utf16', 'utf32', 'ascii']):
      """
Check if the string is ascii or unicode

**Arguments:**
         str_check: string for checking
         codecs: encoding type list

**Returns:**

  / *Type*: bool /

  True : if checked string is ascii or unicode

  False : if checked string is not ascii or unicode
      """
      res = False
      for i in codecs:
         try:
            str_check.decode(i)
            res = True
            break
         except Exception:
            pass
      return res


class Job(threading.Thread):
   def __init__(self, interval, execute, *args, **kwargs):
      threading.Thread.__init__(self)
      self.daemon = False
      self.stopped = threading.Event()
      self.interval = interval
      self.execute = execute
      self.args = args
      self.kwargs = kwargs

   def stop(self):
      self.stopped.set()
      self.join()

   def run(self):
      while not self.stopped.wait(self.interval.total_seconds()):
         self.execute(*self.args, **self.kwargs)


class ResultType:
   """
Result Types.
   """
   PASS = "pass"
   FAIL = "fail"
   EXCEPT = "exception"

   def __init__(self):
      pass


class ResponseMessage(object):
   """
Response message class
   """
   def __init__(self, request="", result=ResultType.PASS, result_data=""):
      self.request = request
      self.result = result
      self.result_data = result_data

   def get_json(self):
      """
Convert response message to json

**Returns:**

*Response message in json format*
      """
      return json.dumps(collections.OrderedDict(sorted(self.__dict__.items())))

   def get_data(self):
      """
Get string data result

**Returns:**

*String result*
      """
      return self.result_data

   @staticmethod
   def create_from_string(str):
      res = None
      try:
         data = json.loads(str)
         res = ResponseMessage(data['request'], data['result'], data['result_data'])
      except Exception as _ex:
         pass
      return res
