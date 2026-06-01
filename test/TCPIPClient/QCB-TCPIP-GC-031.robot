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

QCB-TCPIP-GC-031
    [Documentation]    Verify answer from testserver.
    ...                Search pattern defined with two capturing groups.
    ...                Expected result is a list containing two elements containing the captured content.

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      GOODCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-GC-031-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=GC-031-(\\w+)-(\\d+)\\sACK
                                                               ...                    send_cmd=GC-031-ABC-123

    log    TCPIP-BC-031 'verify' status: ${status}    console=yes
    log    TCPIP-BC-031 'verify' result: ${result}    console=yes

    ${expected_result}    Create List    ABC    123

    should_be_equal    ${status}    PASS
    lists_should_be_equal    ${result}    ${expected_result}

    conn_manager.disconnect    ${connection_name}

