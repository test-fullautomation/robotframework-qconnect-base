#  Copyright 2020-2024 Robert Bosch GmbH
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

*** Settings ***

# Robot Framework Built-In libraries
Library    Collections
Library    BuiltIn
Library    Process

# the library under test
Library    QConnectBase.ConnectionManager    WITH NAME    conn_manager

# additional libraries
Library    RobotframeworkExtensions.Collection    WITH NAME    rf.extensions
Library    ./tcp_ip_selftest_lib.py    WITH NAME    tcpip.selftest

*** Variables ***

${HOST}=    localhost
${PORT}=    4000

&{TCPIPClientParam}    address=${HOST}
...                    port=${PORT}
...                    logfile=./tcp_ip_incoming.log

*** Keywords ***

cconnectbase_suite_setup
    [Documentation]    CConnectBase Suite Setup

    log    executing CConnectBase Suite Setup

    start_tcpip_testserver


cconnectbase_suite_teardown
    [Documentation]    CConnectBase Suite Teardown

    log     executing CConnectBase Suite Teardown

    conn_manager.connect    conn_name=QCB-TCPIP-TESTSERVER-EXIT
    ...                     conn_type=TCPIPClient
    ...                     conn_conf=${TCPIPClientParam}

    conn_manager.send_command    conn_name=QCB-TCPIP-TESTSERVER-EXIT    command=QUIT_TESTSERVER

    conn_manager.disconnect    QCB-TCPIP-TESTSERVER-EXIT

    tcpip.selftest.terminate_tcpip_testserver
