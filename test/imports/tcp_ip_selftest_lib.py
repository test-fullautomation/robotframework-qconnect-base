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
THISMODULEVERSION = "0.11.0"
THISMODULEDATE    = "22.07.2025"
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
        self.__process_testserver     = None
        self.__process_testserver_pid = None
        self.__can_be_connected       = False

        self.__testcounter = 0

        output_dir = CString.NormalizePath(BuiltIn().get_variable_value('${OUTPUT DIR}'))
        self.__testresultsoverview = threadlog(f"{output_dir}/overview_tables")
        self.__testcasesoverview   = threadlog(f"{output_dir}/overview_tables", extension="html")

        # failed only (this summary file is independent from '${OUTPUT DIR}')
        this_library_file_path = os.path.dirname(CString.NormalizePath(__file__))
        self.__testresultsoverview_failedonly = threadlog(f"{this_library_file_path}/../aiotestlogfiles/failed")

    def __del__(self):
        del self.__testresultsoverview
        del self.__testcasesoverview
        del self.__testresultsoverview_failedonly

    def _close(self):
        timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
        msg = f"Executing '_close' method of {self.__sThisModule}"
        BuiltIn().log(msg, level="INFO")

    # --------------------------------------------------------------------------------------------------------------
    #TM***

    # == keyword methods

    @keyword
    def start_tcpip_testserver(self, host="localhost", port=4000, max_connections=1):
        timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
        BuiltIn().log(f"This is '{self.__sThisModule}' at '{timestamp}'", level="INFO", console=True)
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
        list_cmd_line_parts.append(f"--output_dir='{output_dir}/testserver_logfiles'") # currently not a keyword parameter
        list_cmd_line_parts.append(f"--host={host}")
        list_cmd_line_parts.append(f"--port={port}")
        list_cmd_line_parts.append(f"--max_connections={max_connections}")
        cmd_line = " ".join(list_cmd_line_parts)
        BuiltIn().log(f"cmd_line '{cmd_line}'", level="INFO", console=True)
        list_cmd_line_parts = shlex.split(cmd_line)
        self.__process_testserver = subprocess.Popen(list_cmd_line_parts) # do not wait for process finished

        max_tries = 6
        max_try_wait_time = 1
        for i in range(max_tries):
            time.sleep(max_try_wait_time)
            if self.__process_testserver.poll() is None:
                timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
                BuiltIn().log(f"TCP/IP testserver started at '{timestamp}'.", level="INFO", console=True)
                break
            else:
                timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
                # TODO: change to DEBUG level
                BuiltIn().log(f"TCP/IP testserver not yet started at '{timestamp}'.", level="INFO", console=True)
        else:
            BuiltIn().log(f"Timeout while trying to start the TCP/IP testserver.", level="ERROR", console=True)
            self.__process_testserver.terminate()
            raise Exception("Test execution aborted because of the TCP/IP testserver could not be started.")

        self.__process_testserver_pid = self.__process_testserver.pid
        BuiltIn().log(f"PID '{self.__process_testserver_pid}'", level="INFO", console=True)

        # wait for TCP/IP testserver is ready (= accepts a connection)
        TCPIPClientParam = BuiltIn().get_variable_value('${TCPIPClientParam}')
        conn_manager = BuiltIn().get_library_instance("conn_manager") # the name of the library like defined during import ("WITH NAME" option)
        max_tries         = 5
        max_try_wait_time = 1
        for cnt_tries in range(1, max_tries+1):
            connection_name = f"WAIT_FOR_TESTSERVER_READY_{cnt_tries}"
            try:
                conn_manager.connect(conn_name=connection_name, conn_type="TCPIPClient", conn_conf=TCPIPClientParam)
                conn_manager.disconnect(connection_name)
                self.__can_be_connected = True
                BuiltIn().log(f"TCP/IP testserver is ready for being connected.", level="INFO", console=True)
                break
            except Exception as ex:
                conn_manager.disconnect(connection_name)
                exception = f"[connect] try {cnt_tries}/{max_tries} : '{ex}'"
                BuiltIn().log(exception, level="INFO", console=True)
                time.sleep(max_try_wait_time)
        if self.__can_be_connected is False:
            BuiltIn().log(f"Not possible to connect to test server within {max_tries} tries ({max_tries} seconds).", level="INFO", console=True)
            raise Exception("Test execution aborted because of failed precondition.")
    # eof def start_tcpip_testserver(self, host="localhost", port=4000, max_connections=1):


    @keyword
    def quit_tcpip_testserver(self):
        timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
        msg = f"Entering keyword 'quit_tcpip_testserver' at '{timestamp}'"
        BuiltIn().log(msg, level="INFO")
        TCPIPClientParam  = BuiltIn().get_variable_value('${TCPIPClientParam}')
        conn_manager      = BuiltIn().get_library_instance("conn_manager") # the name of the library like defined during import ("WITH NAME" option)
        connection_name   = "TESTSERVER_QUIT_CONNECTION"
        try:
            conn_manager.connect(conn_name=connection_name, conn_type="TCPIPClient", conn_conf=TCPIPClientParam)
            conn_manager.send_command(conn_name=connection_name, command="QUIT_TESTSERVER")
        except Exception as ex:
            msg = f"Problems with command 'QUIT_TESTSERVER'. Reason: {ex}"
            self.__testresultsoverview.tlog("testresults_overview", msg)
            BuiltIn().log(msg, level="ERROR")
            msg = f"Now terminating process with PID {self.__process_testserver_pid}."
            self.__testresultsoverview.tlog("testresults_overview", msg)
            BuiltIn().log(msg, level="WARN")
            self.__process_testserver.terminate()
            raise Exception("The TCP/IP testserver had to be terminated forcibly.")

        # Now the TCP/IP testserver needs some time to quit (send confirmation, disconnect, write final log file entries).
        # We need to wait a bit before we disconnect.
        # We use the PID of the testserver to get to know about his status (non blocking poll()).
        max_tries         = 10
        max_try_wait_time = 1
        is_testserver     = True

        for cnt_tries in range(1, max_tries+1):
            # loop to wait gently for end of testserver (before terminate() is used finally)
            timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
            msg = f"Waiting for testserver finished, try {cnt_tries}/{max_tries} at '{timestamp}'"
            BuiltIn().log(msg, level="INFO", console=True)
            if self.__process_testserver.poll() is not None: # poll() is not blocking!
                # testserver finished
                is_testserver = False
                break
            time.sleep(max_try_wait_time)
        # eof for cnt_tries in range(1, max_tries+1):

        if is_testserver is True:
            timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
            msg = f"Timeout while waiting for testserver finished, try {cnt_tries}/{max_tries} at '{timestamp}'"
            BuiltIn().log(msg, level="INFO", console=True)

        # try to get more clarity
        list_pids = psutil.pids()
        if not self.__process_testserver_pid in list_pids:
            # no testserver is running any more
            msg = f"Latest testserver PID not existing any more => testserver finished"
            BuiltIn().log(msg, level="INFO", console=True)
        else:
            msg = f"Emergency: Latest testserver PID still found => testserver process still running!"
            BuiltIn().log(msg, level="INFO", console=True)

        timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
        BuiltIn().log(f"Finally terminating process with PID {self.__process_testserver_pid} - at {timestamp}", level="INFO")
        self.__process_testserver.terminate()

        conn_manager.disconnect(connection_name)

        timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
        msg = f"Leaving keyword 'quit_tcpip_testserver' at '{timestamp}'"
        BuiltIn().log(msg, level="INFO")

    # eof def quit_tcpip_testserver(self):


    @keyword
    def write_html_header_of_overview_file(self):

        html_header = """<html><head>
<meta http-equiv="content-type" content="text/html; charset=windows-1252">
   <meta name="QConnectBase" content="QConnectBase">
   <title>QConnectBase Test Overview</title>
</head>
<body vlink="#000000" text="#000000" link="#000000" bgcolor="#FFFFFF" alink="#000000">
<hr width="100%" color="#FF8C00" align="center">
<div align="center">
<font size="6" face="Arial" color="#595959">
<b>
QConnectBase<br>Test Cases
</b></font>
</div>
<hr width="100%" color="#FF8C00" align="center">

<div>&nbsp;</div>

<div align="center">

<table frame="box" rules="all" valign="middle" width="100%" cellspacing="0" cellpadding="6" border="1" align="center">
<colgroup>
   <col width="4%" span="1">
   <col width="16%" span="1">
   <col width="8%" span="1">
   <col width="9%" span="1">
   <col width="63%" span="1">
</colgroup>
<tbody>"""
        self.__testcasesoverview.tlog("testcases_overview", f"{html_header}", log_prefix=False)

    @keyword
    def write_html_footer_of_overview_file(self):
        timestamp = time.strftime('%d.%m.%Y - %H:%M:%S')
        html_footer = f"""</tbody></table></div>
<div>&nbsp;</div>
<hr width="100%" color="#FF8C00" align="center">
<div align="center"><font size="2" color="#27408B">Generated: {timestamp}</font></div>
<div>&nbsp;</div>
</body></html>"""
        self.__testcasesoverview.tlog("testcases_overview", f"{html_footer}", log_prefix=False)


    @keyword
    def add_test_to_overview(self):
        suite_source       = BuiltIn().get_variable_value('${SUITE SOURCE}')
        test_name          = BuiltIn().get_variable_value('${TEST NAME}')
        test_tags          = BuiltIn().get_variable_value('${TEST TAGS}')
        test_documentation = BuiltIn().get_variable_value('${TEST DOCUMENTATION}')
        test_status        = BuiltIn().get_variable_value('${TEST STATUS}')
        test_message       = BuiltIn().get_variable_value('${TEST MESSAGE}')
        output_dir         = BuiltIn().get_variable_value('${OUTPUT DIR}')
        # own ones
        connection_type    = BuiltIn().get_variable_value('${connection_type}')
        test_category = BuiltIn().get_variable_value('${test_category}')

        self.__testcounter = self.__testcounter + 1

        # 1. test results overview
        self.__testresultsoverview.tlog("testresults_overview", f"* [{self.__testcounter}] Test '{test_name}' : {test_status}", log_prefix=False)
        self.__testresultsoverview.tlog("testresults_overview", f"{test_documentation}", log_prefix=False)
        if test_status != "PASS":
            self.__testresultsoverview.tlog("testresults_overview", f"!!! {test_message} !!!", log_prefix=False)
            self.__testresultsoverview_failedonly.tlog("testresults_overview_failedonly", f"* [{self.__testcounter}] Test '{test_name}' : {test_status}", log_prefix=False)
            self.__testresultsoverview_failedonly.tlog("testresults_overview_failedonly", f"{test_documentation}", log_prefix=False)
            self.__testresultsoverview_failedonly.tlog("testresults_overview_failedonly", f"!!! {test_message} !!!", log_prefix=False)
            self.__testresultsoverview_failedonly.tlog("testresults_overview_failedonly", f"{suite_source}", log_prefix=False)
            self.__testresultsoverview_failedonly.tlog("testresults_overview_failedonly", f"{output_dir}\n", log_prefix=False)

        self.__testresultsoverview.tlog("testresults_overview", f"{suite_source}\n", log_prefix=False)

        # 2. testcases overview

        github_basepath = "https://github.com/test-fullautomation/robotframework-qconnect-base/tree/develop/test"
        github_link = f"{github_basepath}/{connection_type}/{test_name}.robot"
        if test_category == "GOODCASE":
            textcolor = "#008000"
        elif test_category == "BADCASE":
            textcolor = "#FF0000"
        else:
            textcolor = "#000000"

        list_lines_stripped = []
        list_lines = test_documentation.splitlines()
        for line in list_lines:
            list_lines_stripped.append(line.strip())
        test_documentation_info = "<br>\n".join(list_lines_stripped)

        test_tag_info = ""
        if len(test_tags) > 0:
            test_tag_info = f"<br>Test tags: {test_tags}"

        html_table_row = f"""<tr valign="middle" align="left">
<td colspan="1" valign="center" bgcolor="#F5F5F5" align="right">
<font size="2" face="Arial" color="#FF0000">
<b>
{self.__testcounter}
</b></font></td>
<td colspan="1" valign="center" bgcolor="#F5F5F5" align="middle">
<font size="2" face="Arial" color="#595959">
<b>
<a target="_blank" href="{github_link}">{test_name}</a>
</b></font></td>
<td colspan="1" valign="center" bgcolor="#F5F5F5" align="middle">
<font size="2" face="Arial" color="#4169E1">
{connection_type}
</font></td>
<td colspan="1" valign="center" bgcolor="#F5F5F5" align="middle">
<font size="2" face="Arial" color="{textcolor}">
{test_category}
</font></td>
<td colspan="1" valign="center" bgcolor="#F5F5F5" align="left">
<font size="2" face="Arial" color="#595959"><i>
<b>{test_documentation_info}</b>{test_tag_info}
</i></font></td>
</tr>"""
        self.__testcasesoverview.tlog("testcases_overview", f"{html_table_row}", log_prefix=False)




