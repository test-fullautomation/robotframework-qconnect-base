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

QCB-TCPIP-GC-052
    [Documentation]    Fetch block (3)
    ...                No filter pattern defined, search pattern defined (with single capturing group).
    ...                Default value '.*' is active for filter pattern only.
    ...                Expected result is a list containing one single element containing the captured content.

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      GOODCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-GC-052-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    eob_pattern=transmission\\sended
                                                               ...                    search_pattern=^transmission\\sstarted\\r\\n(.*)
                                                               ...                    fetch_block=${True}
                                                               ...                    timeout=12
                                                               ...                    match_try=1
                                                               ...                    send_cmd=FETCHBLOCK-1

    log    TCPIP-GC-052 'verify' status: ${status}    console=yes
    log    TCPIP-GC-052 'verify' result: ${result}    console=yes

    should_be_equal     ${status}       PASS
    length_should_be    ${result}       1
    should_be_equal     ${result}[0]    transmission point 1 passed\r\nany noise message\r\ntransmission point 2 passed\r\nany noise message\r\ntransmission point 3 passed\r\nany noise message\r\ntransmission ended with code '0'

    conn_manager.disconnect    ${connection_name}

