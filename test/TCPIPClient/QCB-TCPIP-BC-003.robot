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

QCB-TCPIP-BC-003
    [Documentation]    Testserver stops sending notifications and closes the socket while the test still waits for a certain notification ('verify')
    ...                that not yet has been sent. The broken connection causes a premature end of the mytch_try loop.

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      BADCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-BC-003-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    # 'verify' waits 11 seconds for a 'search_pattern' that never will be received.
    # Testserver sends 3 notifications (within 3 seconds), then closes the connection while verify is still waiting.
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=NEVER_WILL_BE_RECEIVED
                                                               ...                    timeout=1
                                                               ...                    match_try=11
                                                               ...                    send_cmd=GETNOTIFICATIONS 3 TCPIP-BC-003 CLOSE_CONNECTION

    log    TCPIP-BC-003 'verify' status: ${status}    console=yes
    log    TCPIP-BC-003 'verify' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_contain     ${result}    Connection has been broken while trying to match the pattern.

    Sleep    1s

    # this shouldn't matter (because of connection already closed by testserver):
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.disconnect    ${connection_name}

    log    TCPIP-BC-003 'disconnect' status: ${status}    console=yes
    log    TCPIP-BC-003 'disconnect' result: ${result}    console=yes

    should_be_equal    ${status}    PASS
    should_be_equal    ${result}    ${None}
