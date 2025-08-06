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
# File: constants.py
#
# Initially created by Cuong Nguyen (RBVH/ECM11) / May 2021
#
# Description:
#   Provide the service manager for managing all connection.
#
# History:
#
# 12.05.2021 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
import platform

OS_LINUX_STR = "linux"
OS_WINDOWS_STR = "windows"
NOT_SUPPORTED_STR = "NotSupported"
UNKNOWN_STR = "unknown"

LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_ERROR = 'ERROR'
LOG_LEVEL_WARNING = 'WARN'

LOG_FORMATTER = "%(asctime)s [%(threadName)-.128s] [%(levelname)-5.5s]  %(message)s"
platform_ = platform.system().lower()
if platform_.startswith(OS_WINDOWS_STR):
   SLASH = "\\"
elif platform_.startswith(OS_LINUX_STR):
   SLASH = "/"


class SocketType:
   UNKNOWN = "unknown"
   ASF = "ASF"
   JSRPC = "JSRPC"
   MQTT = "MQTT"
   ANDROID_ADB = "ANDROID_ADB"
   File = "File"
   Serial = "Serial"

   def __init__(self):
      pass


class String:
   CONNECTION_NAME_EXIST = "The connection name '%s' has already existed! Please use other name"
   CONNECTION_TYPE_UNSUPPORTED = "The %s connection type hasn't been supported"
   CONNECTION_TYPE_CONFUSED = "Mismatch: 'conn_type' (%s) and 'con_conf[\"conn_type\"]' (%s) both set but differ. Expected: set in only one or identical in both."
   CONNECTION_MODE_CONFUSED = "Mismatch: 'conn_mode' (%s) and 'con_conf[\"conn_mode\"]' (%s) both set but differ. Expected: set in only one or identical in both."
