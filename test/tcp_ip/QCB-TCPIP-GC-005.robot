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

Resource    ./imports/resources.resource

*** Test Cases ***

QCB-TCPIP-GC-005
    [Documentation]    Fetch block
    ...                !!! several clarifications required !!!
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/99
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/100
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/101
    ...                !!! test not in final version !!!

    conn_manager.connect    conn_name=QCB-TCPIP-GC-005-Connection
    ...                     conn_type=TCPIPClient
    ...                     conn_conf=${TCPIPClientParam}

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=QCB-TCPIP-GC-005-Connection
                                                               ...                    search_pattern=.+(\\[COND-\\d+?\\])
                                                             # ...                    filter_pattern=COND            # !!! meaning unclear !!!
                                                               ...                    eob_pattern=FETCHBLOCK_END
                                                               ...                    fetch_block=${True}
                                                               ...                    timeout=2
                                                               ...                    match_try=20
                                                               ...                    send_cmd=FETCHBLOCK-QUICKTEST

    log    TCPIP-GC-005 'verify' status: ${status}    console=yes
    log    TCPIP-GC-005 'verify' result: ${result}    console=yes
    log    TCPIP-GC-005 'verify' result[0]: ${result}[0]    console=yes
    log    TCPIP-GC-005 'verify' result[1]: ${result}[1]    console=yes

    should_be_equal    ${status}    PASS

    # !! not final version !!
    should_be_equal    ${result[0]}    FETCHBLOCK-QUICKTEST ACK [COND-5]
    should_be_equal    ${result[1]}    [COND-5]

    conn_manager.disconnect    QCB-TCPIP-GC-005-Connection



