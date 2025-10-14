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

QCB-TCPIP-BC-033
    [Documentation]    Verify parameter validation (4)
    ...                filter_pattern defined with capturing groups, but this is not supported.
    ...                Detected properly: Warning: filter_pattern 'IN(VAL)ID' contains capturing groups, which may not work as expected for filtering message.
    ...                Because filter_pattern does not match, the status is PASS. But an error would be better.
    ...                Error message itself has unfavorable wording.
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/183
    ...                !!! TEST NOT IN FINAL VERSION !!!

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      BADCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-BC-033-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    filter_pattern=IN(VAL)ID
                                                               ...                    eob_pattern=ACK
                                                               ...                    fetch_block=${True}
                                                               ...                    send_cmd=PING

    log    TCPIP-BC-033 'verify' status: ${status}    console=yes
    log    TCPIP-BC-033 'verify' result: ${result}    console=yes

    # Because filter_pattern does not match, the status is PASS
    # should_be_equal    ${status}    FAIL
    # should_be_equal    ${result}    !!! NEEDS TO BE DEFINED AFTER FIX !!!

    conn_manager.disconnect    ${connection_name}

