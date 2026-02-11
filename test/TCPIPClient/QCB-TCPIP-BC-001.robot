#  Copyright 2020-2026 Robert Bosch GmbH
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

Resource    ../imports/resources.resource

*** Test Cases ***

QCB-TCPIP-BC-001
    [Documentation]    Send command without connection

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      BADCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-BC-001-Connection

    # connection parameter for this test
    # (! in this test not used !)
    # &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    # ...                                          address=${HOST}
    # ...                                          port=${PORT}
    # ...                                          logfile=./tcp_ip_incoming.log

    # try to send a command without connection
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.send_command    conn_name=${connection_name}    command=BC-001

    log    TCPIP-BC-001 'send_command' status: ${status}    console=yes
    log    TCPIP-BC-001 'send_command' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_be_equal    ${result}    The '${connection_name}' connection hasn't been established. Please connect first.

