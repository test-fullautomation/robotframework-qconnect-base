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
# XC-HWP/ESW3-Queckenstedt
#
# --------------------------------------------------------------------------------------------------------------

# -- import standard Python modules
import os
import sys
import time
import shlex
import subprocess

# from threadlog import threadlog

# -- import Robotframework API
from robot.api.deco import keyword, library # required when using @keyword, @library decorators
from robot.libraries.BuiltIn import BuiltIn
from robot.conf import RobotSettings

from PythonExtensionsCollection.String.CString import CString

# --------------------------------------------------------------------------------------------------------------

sThisModuleName    = "tcp_ip_selftest_lib.py"
sThisModuleVersion = "0.2.0"
sThisModuleDate    = "16.01.2025"
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
        self.__can_be_connected   = False

        # output_dir = CString.NormalizePath(BuiltIn().get_variable_value('${OUTPUT DIR}'))
        # self.__threadlog = threadlog(f"{output_dir}/test_overview")

    def __del__(self):
        # del self.__threadlog
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

        # wait for TCP/IP testserver is ready (= accepts a connection)
        TCPIPClientParam = BuiltIn().get_variable_value('${TCPIPClientParam}')
        conn_manager = BuiltIn().get_library_instance("conn_manager") # the name of the library like defined during import ("WITH NAME" option)
        max_tries         = 5
        max_try_wait_time = 1
        cnt_tries         = 0
        for cnt_tries in range(1, max_tries+1):
            connection_name = f"WAIT_FOR_TESTSERVER_READY_{cnt_tries}"
            try:
                conn_manager.connect(conn_name=connection_name, conn_type="TCPIPClient", conn_conf=TCPIPClientParam)
                conn_manager.disconnect(connection_name)
                self.__can_be_connected = True
                BuiltIn().log(f"TCP/IP testserver '{tcpip_testserver}' is ready for being connected.", "INFO", console=True)
                break
            except Exception as ex:
                conn_manager.disconnect(connection_name)
                exception = f"[connect] try {cnt_tries}/{max_tries} : '{ex}'"
                BuiltIn().log(exception, "INFO", console=True)
                time.sleep(max_try_wait_time)
        if self.__can_be_connected is False:
            BuiltIn().log(f"Not possible to connect to test server '{tcpip_testserver}' within {max_tries} tries ({max_tries} seconds).", "ERROR")
            raise Exception("Test execution aborted because of failed precondition.")


    @keyword
    def quit_tcpip_testserver(self):
        TCPIPClientParam = BuiltIn().get_variable_value('${TCPIPClientParam}')
        conn_manager = BuiltIn().get_library_instance("conn_manager") # the name of the library like defined during import ("WITH NAME" option)
        connection_name = "TESTSERVER_QUIT"
        try:
            conn_manager.connect(conn_name=connection_name, conn_type="TCPIPClient", conn_conf=TCPIPClientParam)
            conn_manager.send_command(conn_name=connection_name, command="QUIT_TESTSERVER")
            conn_manager.disconnect(connection_name)
            # to get the command prompt back when executed in console
            self.__process_testserver.terminate()
        except:
            pass



