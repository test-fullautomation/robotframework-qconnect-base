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

QCB-TCPIP-BC-006
    [Documentation]    Unknown connection name in keyword 'disconnect' (no corresponding 'connect')
    ...                !!! The 'UNKNOWN_CONNECTION_NAME' is ignored. No error thrown. Rework required !!!
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/93
    ...                !!! test not in final version !!!

    set_test_variable    ${connection_type}    tcp_ip
    set_test_variable    ${test_category}    BADCASE

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.disconnect    conn_name=UNKNOWN_CONNECTION_NAME

    log    TCPIP-BC-006 'disconnect' status: ${status}    console=yes
    log    TCPIP-BC-006 'disconnect' result: ${result}    console=yes

    # !!! need to be implemented and activated after fix !!!
    # should_be_equal    ${status}    FAIL
    # should_be_equal    ${result}    ....


