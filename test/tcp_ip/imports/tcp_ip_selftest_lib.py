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
#
# Already in this file we use keywords of component QConnectBase. These keywords are tested 'officially' durig the execution of
# robot files. Nevertheless we need to use them here too. In case they do not work properly, already the code within this file fails.
# This is also a test result.
#
# --------------------------------------------------------------------------------------------------------------

# -- import standard Python modules
import os
import sys
import time
import shlex
import subprocess
import psutil

from threadlog import threadlog

# -- import Robotframework API
from robot.api.deco import keyword, library # required when using @keyword, @library decorators
from robot.libraries.BuiltIn import BuiltIn
from robot.conf import RobotSettings

from PythonExtensionsCollection.String.CString import CString

# --------------------------------------------------------------------------------------------------------------

THISMODULENAME    = "tcp_ip_selftest_lib.py"
THISMODULEVERSION = "0.5.2"
THISMODULEDATE    = "28.01.2025"
THISMODULE        = f"{THISMODULENAME} v. {THISMODULEVERSION} / {THISMODULEDATE}"

TESTSERVER_TIME_TO_QUIT = 3

# --------------------------------------------------------------------------------------------------------------

@library
class tcp_ip_selftest_lib():
    """ tcp_ip_selftest_lib keywords
    """

    ROBOT_AUTO_KEYWORDS   = False # only decorated methods are keywords
    ROBOT_LIBRARY_VERSION = THISMODULEVERSION
    ROBOT_LIBRARY_SCOPE   = 'GLOBAL'

    # --------------------------------------------------------------------------------------------------------------
    #TM***

    def __init__(self, sThisModule=THISMODULE):

        self.__sThisModule = sThisModule
        self.__process_testserver = None
        self.__can_be_connected   = False

        output_dir = CString.NormalizePath(BuiltIn().get_variable_value('${OUTPUT DIR}'))
        self.__testoverviewlog = threadlog(f"{output_dir}/test_overview")

    def __del__(self):
        del self.__testoverviewlog
        pass

    def _close(self):
        pass

    # --------------------------------------------------------------------------------------------------------------
    #TM***

    # == non keyword methods

    def __get_server_pid(self):
        TCPIPClientParam = BuiltIn().get_variable_value('${TCPIPClientParam}')
        conn_manager = BuiltIn().get_library_instance("conn_manager") # the name of the library like defined during import ("WITH NAME" option)
        connection_name = "GET_SERVER_PID_CONNECTION"
        server_pid = None
        try:
            conn_manager.connect(conn_name=connection_name, conn_type="TCPIPClient", conn_conf=TCPIPClientParam)
            command = f"GET_SERVER_PID"
            response = conn_manager.verify(conn_name=connection_name, search_pattern="PID=(.+)", send_cmd=command)
            server_pid = response[1]
            BuiltIn().log(f"received PID of TCP/IP testserver: {server_pid}", level="INFO")
            conn_manager.disconnect(connection_name)
        except Exception as ex:
            msg = f"Not able to get the TCP/IP server pid. Reason: {ex}"
            self.__testoverviewlog.tlog("test_overview", msg)
            BuiltIn().log(msg, level="ERROR")
            raise Exception("Test execution aborted because of failed information exchange.")
        return server_pid

    # --------------------------------------------------------------------------------------------------------------
    #TM***

    # == keyword methods

    @keyword
    def start_tcpip_testserver(self):
        BuiltIn().log(f"This is '{self.__sThisModule}'", level="INFO", console=True)
        python = sys.executable
        this_library_file_path = os.path.dirname(CString.NormalizePath(__file__))
        # While computing the path to the TCP/IP testserver, the position of this file is the reference.
        # The TCP/IP testserver is placed in the same folder.
        tcpip_testserver = f"{this_library_file_path}/tcp_ip_testserver.py"
        BuiltIn().log(f"TCP/IP testserver is '{tcpip_testserver}'", level="INFO", console=True)
        if not os.path.isfile(tcpip_testserver):
            raise Exception(f"Exception: TCP/IP testserver '{tcpip_testserver}' not found.")
        output_dir = CString.NormalizePath(BuiltIn().get_variable_value('${OUTPUT DIR}'))
        list_cmd_line_parts = []
        list_cmd_line_parts.append(f"'{python}'")
        list_cmd_line_parts.append(f"'{tcpip_testserver}'")
        list_cmd_line_parts.append(f"'{output_dir}'")
        cmd_line = " ".join(list_cmd_line_parts)
        BuiltIn().log(f"cmd_line '{cmd_line}'", level="INFO", console=True)
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
                BuiltIn().log(f"TCP/IP testserver '{tcpip_testserver}' is ready for being connected.", level="INFO", console=True)
                break
            except Exception as ex:
                conn_manager.disconnect(connection_name)
                exception = f"[connect] try {cnt_tries}/{max_tries} : '{ex}'"
                BuiltIn().log(exception, level="INFO", console=True)
                time.sleep(max_try_wait_time)
        if self.__can_be_connected is False:
            BuiltIn().log(f"Not possible to connect to test server '{tcpip_testserver}' within {max_tries} tries ({max_tries} seconds).", level="INFO", console=True)
            raise Exception("Test execution aborted because of failed precondition.")


    @keyword
    def quit_tcpip_testserver(self):
        pid               = self.__get_server_pid() # the PID of the current active TCP/IP testserver we want to quit here
        server_pid        = int(pid)
        TCPIPClientParam  = BuiltIn().get_variable_value('${TCPIPClientParam}')
        conn_manager      = BuiltIn().get_library_instance("conn_manager") # the name of the library like defined during import ("WITH NAME" option)
        connection_name   = "TESTSERVER_QUIT_CONNECTION"
        try:
            conn_manager.connect(conn_name=connection_name, conn_type="TCPIPClient", conn_conf=TCPIPClientParam)
            conn_manager.send_command(conn_name=connection_name, command="QUIT_TESTSERVER")
        except Exception as ex:
            msg = f"Problems with command 'QUIT_TESTSERVER'. Reason: {ex}"
            self.__testoverviewlog.tlog("test_overview", msg)
            BuiltIn().log(msg, level="ERROR")
            msg = f"Now terminating process with PID {server_pid}."
            self.__testoverviewlog.tlog("test_overview", msg)
            BuiltIn().log(msg, level="WARN")
            self.__process_testserver.terminate()
            raise Exception("The TCP/IP testserver had to be terminated forcibly.")

        # Now the TCP/IP testserver needs some time to quit (send confirmation, disconnect, write final log file entries).
        # We need to wait a bit before we disconnect.
        # This is also to get the command prompt back when the entire test is executed in console.
        # And 'self.__process_testserver.terminate()' should be an emergency fallback solution only
        # (because this causes missing log entries, if sent too early).
        # We use the PID of the testserver to get to know about his status.

        max_tries         = 8
        max_try_wait_time = 1
        cnt_tries         = 0
        is_testserver     = True

        for cnt_tries in range(1, max_tries+1):
            finished_pid = None
            if hasattr(os, 'WNOHANG'): # not available in all os, but on Linux this avoids zombie processes, because it forces to catch the status
                try:
                    finished_pid, status = os.waitpid(server_pid, os.WNOHANG) # (why is finished_pid = 0?)
                    msg = f"process {server_pid} finished with status {status}"
                    BuiltIn().log(msg, level="INFO", console=True)
                except ChildProcessError as ex:
                    BuiltIn().log(f"{ex}", level="INFO", console=True)
                    break

            # confirmation
            list_pids = psutil.pids()
            if not server_pid in list_pids:
                # no testserver is running any more
                is_testserver = False
                break

            msg = f"testserver quit try {cnt_tries}/{max_tries}"
            BuiltIn().log(msg, level="INFO", console=True)
            time.sleep(max_try_wait_time)
        # eof for cnt_tries in range(1, max_tries+1):

        if is_testserver is True:
            BuiltIn().log(f"Not possible to quit the TCP/IP testserver within {max_tries} tries ({max_tries} seconds).", level="WARN")
            BuiltIn().log(f"Now terminating process with PID {server_pid}.", level="WARN")
            self.__process_testserver.terminate()
            conn_manager.disconnect(connection_name)
            raise Exception("The TCP/IP testserver had to be terminated forcibly.")
        conn_manager.disconnect(connection_name)


    @keyword
    def add_test_to_overview(self):
        suite_source       = BuiltIn().get_variable_value('${SUITE SOURCE}')
        test_name          = BuiltIn().get_variable_value('${TEST NAME}')
        test_documentation = BuiltIn().get_variable_value('${TEST DOCUMENTATION}')
        test_status        = BuiltIn().get_variable_value('${TEST STATUS}')
        self.__testoverviewlog.tlog("test_overview", f"* Test '{test_name}' : {test_status}", log_prefix=False)
        self.__testoverviewlog.tlog("test_overview", f"{test_documentation}", log_prefix=False)
        self.__testoverviewlog.tlog("test_overview", f"{suite_source}\n", log_prefix=False)


    @keyword
    def get_server_pid(self):
        return self.__get_server_pid()


    # # >> currently not used
    # @keyword
    # def set_test_name(self):
        # test_name        = BuiltIn().get_variable_value('${TEST NAME}')
        # TCPIPClientParam = BuiltIn().get_variable_value('${TCPIPClientParam}')
        # conn_manager = BuiltIn().get_library_instance("conn_manager") # the name of the library like defined during import ("WITH NAME" option)
        # connection_name = "SET_TEST_NAME_CONNECTION"
        # try:
            # conn_manager.connect(conn_name=connection_name, conn_type="TCPIPClient", conn_conf=TCPIPClientParam)
            # command = f"SET_TEST_NAME={test_name}"
            # conn_manager.send_command(conn_name=connection_name, command=command)              # TODO: verify instead of send_command
            # conn_manager.disconnect(connection_name)
        # except Exception as ex:
            # msg = f"Not able to send the Robot Framework test name to testserver. Reason: {ex}"
            # self.__testoverviewlog.tlog("test_overview", msg)
            # BuiltIn().log(msg, level="ERROR")
            # raise Exception("Test execution aborted because of failed information exchange.")



