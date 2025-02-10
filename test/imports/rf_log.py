#  Copyright 2020-2025 Robert Bosch GmbH
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
# --------------------------------------------------------------------------------------------------------------
#
# Wrapper of Robot Framework logging
#
# XC-HWP/ESW3-Queckenstedt
#
# 16.01.2025
#
# --------------------------------------------------------------------------------------------------------------

from robot.libraries.BuiltIn import BuiltIn

class rf_log:

   @staticmethod
   def info(message=""):
      BuiltIn().log(message, "INFO", console=True)

   @staticmethod
   def user(message=""):
      BuiltIn().log(message, "USER", console=True)

   @staticmethod
   def warn(message=""):
      BuiltIn().log(message, "WARN")

   @staticmethod
   def error(message=""):
      BuiltIn().log(message, "ERROR")

