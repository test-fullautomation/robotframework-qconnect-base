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

QCB-TCPIP-GC-050
    [Documentation]    Fetch block
    ...                !!! several clarifications required !!!
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/99
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/100
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/101
    ...                !!! test not in final version !!!

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      GOODCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-GC-050-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=.+(\\[COND-\\d+?\\])
                                                               ...                    eob_pattern=FETCHBLOCK_END
                                                               ...                    fetch_block=${True}
                                                               ...                    timeout=2
                                                               ...                    match_try=20
                                                               ...                    send_cmd=FETCHBLOCK QCB-TCPIP-GC-050

    # testserver sends a fix sequence; wait until sequence has been finished
    Sleep    4s

    conn_manager.disconnect    ${connection_name}

    log    TCPIP-GC-050 'verify' status: ${status}    console=yes
    log    TCPIP-GC-050 'verify' result: ${result}    console=yes
    log    TCPIP-GC-050 'verify' result[0]: ${result}[0]    console=yes
    log    TCPIP-GC-050 'verify' result[1]: ${result}[1]    console=yes

    should_be_equal    ${status}    PASS

    # !! TODO: needs to be defined !!
    # should_be_equal    ${result[0]}    ....
    # should_be_equal    ${result[1]}    ....




