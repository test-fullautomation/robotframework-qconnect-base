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

QCB-TCPIP-BC-005
    [Documentation]    Invalid connection type in keyword 'connect'
    ...                !!! The 'Please choose one of' list differs in every test execution. Rework required. !!!
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/92
    ...                !!! test not in final version !!!

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.connect    conn_name=QCB-TCPIP-BC-005-Connection
                                                               ...                     conn_type=INVALID_CONNECTION_TYPE
                                                               ...                     conn_conf=${TCPIPClientParam}

    log    TCPIP-BC-005 'connect' status: ${status}    console=yes
    log    TCPIP-BC-005 'connect' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL

    # !!! need to be implemented and activated after fix !!!
    # The 'Please choose one of' list differs in every test execution!
    # should_be_equal    ${result}    The connection type 'INVALID_CONNECTION_TYPE' is not supported. Please choose one of: SerialClient, Winapp, RabbitmqClient, TCPIPBase, SerialBase, TCPIPClient, TCPIPServer, SSHClient.

