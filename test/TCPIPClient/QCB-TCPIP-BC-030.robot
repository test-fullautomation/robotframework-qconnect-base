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

QCB-TCPIP-BC-030
    [Documentation]    Test parameter validation: eob_pattern and filter_pattern only valid when fetch_block=True

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      BADCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-BC-030-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    # Test 1: fetch_block=False with custom eob_pattern should fail
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=.*
                                                               ...                    timeout=1
                                                               ...                    fetch_block=${False}
                                                               ...                    eob_pattern=END
                                                               ...                    send_cmd=PING

    log    TCPIP-BC-030 Test 1 status: ${status}    console=yes
    log    TCPIP-BC-030 Test 1 result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_contain    ${result}    eob_pattern
    should_contain    ${result}    only applicable when 'fetch_block' is True

    # Test 2: fetch_block=False with custom filter_pattern should fail
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=.*
                                                               ...                    timeout=1
                                                               ...                    fetch_block=${False}
                                                               ...                    filter_pattern=test_filter
                                                               ...                    send_cmd=PING

    log    TCPIP-BC-030 Test 2 status: ${status}    console=yes
    log    TCPIP-BC-030 Test 2 result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_contain    ${result}    filter_pattern
    should_contain    ${result}    only applicable when 'fetch_block' is True

    # Test 3: fetch_block=False with default patterns should work
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=PONG
                                                               ...                    timeout=5
                                                               ...                    fetch_block=${False}
                                                               ...                    eob_pattern=.*
                                                               ...                    filter_pattern=.*
                                                               ...                    send_cmd=PING

    log    TCPIP-BC-030 Test 3 status: ${status}    console=yes
    log    TCPIP-BC-030 Test 3 result: ${result}    console=yes

    should_be_equal    ${status}    PASS

    # Test 4: fetch_block=True with custom patterns should work  
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=PONG
                                                               ...                    timeout=5
                                                               ...                    fetch_block=${True}
                                                               ...                    eob_pattern=END
                                                               ...                    filter_pattern=test_filter
                                                               ...                    send_cmd=PING

    log    TCPIP-BC-030 Test 4 status: ${status}    console=yes
    log    TCPIP-BC-030 Test 4 result: ${result}    console=yes

    should_be_equal    ${status}    PASS

    conn_manager.disconnect    ${connection_name}