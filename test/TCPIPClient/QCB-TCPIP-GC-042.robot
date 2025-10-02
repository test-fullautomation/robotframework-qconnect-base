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

QCB-TCPIP-GC-042
    [Documentation]    Two connections with same connection parameter, but different names.

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      GOODCASE

    set_test_variable    ${connection_name_1}    QCB-TCPIP-GC-042-Connection-1
    set_test_variable    ${connection_name_2}    QCB-TCPIP-GC-042-Connection-2

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    # connection with first name
    conn_manager.connect    conn_name=${connection_name_1}
    ...                     conn_conf=${TCPIPClientParam}

    # connection with second name
    conn_manager.connect    conn_name=${connection_name_2}
    ...                     conn_conf=${TCPIPClientParam}

    # using the first name
    ${status1}    ${result1}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name_1}
                                                                 ...                    search_pattern=GC-042 ACK
                                                                 ...                    send_cmd=GC-042

    log    TCPIP-GC-042 'verify' status 1: ${status1}    console=yes
    log    TCPIP-GC-042 'verify' result 1: ${result1}    console=yes

    should_be_equal    ${status1}    PASS
    should_be_equal    ${result1}    ${None}

    # using the second name
    ${status2}    ${result2}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name_2}
                                                                 ...                    search_pattern=GC-042 ACK
                                                                 ...                    send_cmd=GC-042

    log    TCPIP-GC-042 'verify 2' status 2: ${status2}    console=yes
    log    TCPIP-GC-042 'verify 2' result 2: ${result2}    console=yes

    should_be_equal    ${status2}    PASS
    should_be_equal    ${result1}    ${None}

    # disconnect the first connection
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.disconnect    ${connection_name_1}

    log    TCPIP-GC-042 'disconnect' status: ${status}    console=yes
    log    TCPIP-GC-042 'disconnect' result: ${result}    console=yes

    should_be_equal    ${status}    PASS
    should_be_equal    ${result}    ${None}

    # the second connection must still be usable
    ${status2}    ${result2}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name_2}
                                                                 ...                    search_pattern=GC-042 ACK
                                                                 ...                    send_cmd=GC-042

    log    TCPIP-GC-042 'verify 2' status 2: ${status2}    console=yes
    log    TCPIP-GC-042 'verify 2' result 2: ${result2}    console=yes

    should_be_equal    ${status2}    PASS
    should_be_equal    ${result1}    ${None}

    # disconnect the second connection
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.disconnect    ${connection_name_2}

    log    TCPIP-GC-042 'disconnect' status: ${status}    console=yes
    log    TCPIP-GC-042 'disconnect' result: ${result}    console=yes

    should_be_equal    ${status}    PASS
    should_be_equal    ${result}    ${None}
