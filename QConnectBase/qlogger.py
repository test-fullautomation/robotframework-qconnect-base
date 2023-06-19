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
# File: qlogger.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / Sep 2021
#
# Description:
#   Provide the logging system for QConnect Library.
#
# History:
#
# 30.09.2021 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from robot.libraries.BuiltIn import BuiltIn
from QConnectBase.utils import *
import QConnectBase.constants as constants
import logging
import os


class ColorFormatter(logging.Formatter):
   """
Custom formatter class for setting log color.
   """
   grey = "\x1b[38;21m"
   yellow = "\x1b[33;21m"
   red = "\x1b[31;21m"
   bold_red = "\x1b[31;1m"
   reset = "\x1b[0m"
   format = constants.LOG_FORMATTER

   FORMATS = {
      logging.DEBUG: grey + format + reset,
      logging.INFO: grey + format + reset,
      logging.WARNING: yellow + format + reset,
      logging.ERROR: red + format + reset,
      logging.CRITICAL: bold_red + format + reset
   }

   def format(self, record):
      """
Set the color format for the log.

**Arguments:**

* ``record``

  / *Condition*: required / *Type*: str /

  Log record.

**Returns:**

  / *Type*: logging.Formatter /

  Log with color formatter.
      """
      log_fmt = self.FORMATS.get(record.levelno)
      formatter = logging.Formatter(log_fmt)
      return formatter.format(record)


class QFileHandler(logging.FileHandler):
   """
Handler class for user defined file in config.
   """
   def __init__(self, config, _logger_name, formatter):
      """
Constructor for QFileHandler class.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

* ``_logger_name``

  / *Condition*: required / *Type*: str /

  Unused.

* ``formatter``

  / *Condition*: required / *Type*: ColorFormatter /

  Log's formatter.
      """
      path = self.get_log_path(config)
      super(QFileHandler, self).__init__(path)
      self.setFormatter(formatter)

   @staticmethod
   def get_log_path(config):
      """
Get the log file path for this handler.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

  / *Type*: str /

  Log file path.
      """
      out_dir = BuiltIn()._context.output._settings.output_directory
      dir_log = os.path.dirname(config.logfile)
      if not os.path.isabs(dir_log):
         dir_log = out_dir + '/' + dir_log
      if not os.path.exists(dir_log):
         os.makedirs(dir_log)
      return "{0}/{1}".format(dir_log, os.path.basename(config.logfile))

   @staticmethod
   def get_config_supported(config):
      """
Check if the connection config is supported by this handler.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

  / *Type*: bool /

  True if the config is supported.

  False if the config is not supported.
      """
      return config.logfile is not None and config.logfile != 'nonlog' and config.logfile != 'console'


class QDefaultFileHandler(logging.FileHandler):
   """
Handler class for default log file path.
   """
   def __init__(self, _config, logger_name, formatter):
      """
Constructor for QDefaultFileHandler class.

**Arguments:**

* ``_config``

  / *Condition*: required / *Type*: None /

  Unused.

* ``logger_name``

  / *Condition*: required / *Type*: str /

  Name of the logger.

* ``formatter``

  / *Condition*: required / *Type*: ColorFormatter /

  Log's formatter.


**Returns:**

(*no returns*)
      """
      path = self.get_log_path(logger_name)
      super(QDefaultFileHandler, self).__init__(path, mode='w')
      self.setFormatter(formatter)

   @staticmethod
   def get_log_path(logger_name):
      """
Get the log file path for this handler.

**Arguments:**

* ``logger_name``

  / *Condition*: required / *Type*: str /

  Name of the logger.

**Returns:**

  / *Type*: str /

  Log file path.
      """
      out_dir = BuiltIn()._context.output._settings.output_directory
      return "{0}/{1}.log".format(out_dir, logger_name + "_trace")

   @staticmethod
   def get_config_supported(config):
      """
Check if the connection config is supported by this handler.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

  / *Type*: bool /

  True if the config is supported.

  False if the config is not supported.
      """
      return config.logfile is None


class QConsoleHandler(logging.StreamHandler):
   """
Handler class for console log.
   """
   def __init__(self, _config, _logger_name, _formatter):
      """
Constructor for QDefaultFileHandler class.

**Arguments:**

* ``_config``

  / *Condition*: required / *Type*: None /

  Unused.

* ``_logger_name``

  / *Condition*: required / *Type*: str /

  Unused.

* ``_formatter``

  / *Condition*: required / *Type*: ColorFormatter /

  Unused.

**Returns:**

(*no returns*)
      """
      super(QConsoleHandler, self).__init__()
      self.setFormatter(ColorFormatter())

   @staticmethod
   def get_config_supported(config):
      """
Check if the connection config is supported by this handler.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

  / *Type*: bool /

  True if the config is supported.

  False if the config is not supported.
      """
      return config.logfile == 'console'


class QLogger(Singleton):
   """
Logger class for QConnect Libraries.
   """
   NAME_2_LEVEL_DICT = {
      'TRACE': logging.NOTSET,
      'NONE': logging.CRITICAL + 1
   }

   def get_logger(self, logger_name):
      """
Get the logger object.

**Arguments:**

* ``logger_name``

  / *Condition*: required / *Type*: str /

  Name of the logger.

**Returns:**

* ``logger``

  / *Type*: Logger /

  Logger object.         .
      """
      self.logger_name = logger_name
      self.logger = logging.getLogger(logger_name)
      self.logger.setLevel(logging.DEBUG)
      self.formatter = logging.Formatter(constants.LOG_FORMATTER)
      return self.logger

   def set_handler(self, config):
      """
Set handler for logger.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

* ``handler_ins``

  / *Type*: logging.handler /


  None if no handler is set.

  Handler object.
      """
      # noinspection PyBroadException
      try:
         log_level = BuiltIn()._context.output._settings.log_level
         if log_level in QLogger.NAME_2_LEVEL_DICT:
            log_level = QLogger.NAME_2_LEVEL_DICT[log_level]
      except:
         log_level = logging.INFO

      supported_handler_classes_list = Utils.get_all_descendant_classes(logging.StreamHandler)
      for handler in supported_handler_classes_list:
         # noinspection PyBroadException
         try:
            if handler.get_config_supported(config):
               handler_ins = handler(config, self.logger_name, self.formatter)
               handler_ins.setLevel(log_level)
               self.logger.addHandler(handler_ins)
               return handler_ins
         except:
            pass
      return None
