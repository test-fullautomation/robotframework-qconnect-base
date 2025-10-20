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

*** Settings ***

Resource    ../imports/resources.resource

*** Test Cases ***

QCB-TCPIP-BC-004
    [Documentation]    Duplicate connection name: A second connection uses the same connection name than the first one.
    ...                The first connection has not been disconnected before.
    ...                Expected: Error message that this connection is already in use.

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      BADCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-BC-004-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    conn_manager.verify    conn_name=${connection_name}    search_pattern=BC-004 ACK    send_cmd=BC-004

    # another connect, using the same same connection name again (without previous disconnect)
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.connect    conn_name=${connection_name}
                                                               ...                     conn_conf=${TCPIPClientParam}
    log    TCPIP-BC-004 'connect' status: ${status}    console=yes
    log    TCPIP-BC-004 'connect' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_be_equal    ${result}    This connection name 'QCB-TCPIP-BC-004-Connection' is already in use. Please select another name.

    Sleep    1s

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.disconnect    ${connection_name}

    log    TCPIP-BC-004 'disconnect' status: ${status}    console=yes
    log    TCPIP-BC-004 'disconnect' result: ${result}    console=yes

    should_be_equal    ${status}    PASS
    should_be_equal    ${result}    ${None}
