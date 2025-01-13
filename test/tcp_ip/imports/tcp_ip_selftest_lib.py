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

# -- import standard Python modules
import os
import sys
import shlex
import subprocess

# -- import Robotframework API
from robot.api.deco import keyword, library # required when using @keyword, @library decorators
from robot.libraries.BuiltIn import BuiltIn
from robot.conf import RobotSettings

from PythonExtensionsCollection.String.CString import CString

# --------------------------------------------------------------------------------------------------------------

sThisModuleName    = "tcp_ip_selftest_lib.py"
sThisModuleVersion = "0.1.0"
sThisModuleDate    = "13.01.2025"
sThisModule        = f"{sThisModuleName} v. {sThisModuleVersion} / {sThisModuleDate}"

# --------------------------------------------------------------------------------------------------------------

@library
class tcp_ip_selftest_lib():
    """ tcp_ip_selftest_lib keywords
    """

    ROBOT_AUTO_KEYWORDS   = False # only decorated methods are keywords
    ROBOT_LIBRARY_VERSION = sThisModuleVersion
    ROBOT_LIBRARY_SCOPE   = 'GLOBAL'

    # --------------------------------------------------------------------------------------------------------------
    #TM***

    def __init__(self, sThisModule=sThisModule):

        self.__sThisModule = sThisModule
        self.__process_testserver = None

    def __del__(self):
        pass

    def _close(self):
        pass

    @keyword
    def start_tcpip_testserver(self):
        BuiltIn().log(f"This is '{self.__sThisModule}'", "INFO")
        python = sys.executable
        this_library_file_path = os.path.dirname(CString.NormalizePath(__file__))
        # While computing the path to the TCP/IP testserver, the position of this file is the reference.
        # The TCP/IP testserver is placed in the same folder.
        tcpip_testserver = f"{this_library_file_path}/tcp_ip_testserver.py"
        BuiltIn().log(f"TCP/IP testserver is '{tcpip_testserver}'", "INFO")
        if not os.path.isfile(tcpip_testserver):
            raise Exception(f"Exception: TCP/IP testserver '{tcpip_testserver}' not found.")
        list_cmd_line_parts = []
        list_cmd_line_parts.append(f"'{python}'")
        list_cmd_line_parts.append(f"'{tcpip_testserver}'")
        cmd_line = " ".join(list_cmd_line_parts)
        list_cmd_line_parts = shlex.split(cmd_line)
        self.__process_testserver = subprocess.Popen(list_cmd_line_parts) # do not wait for process finished

    @keyword
    def terminate_tcpip_testserver(self):
        # mostly to get the command prompt back when executed in console
        # (usually executed in suite teardown)
        self.__process_testserver.terminate()


