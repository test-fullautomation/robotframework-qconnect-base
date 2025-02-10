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

QCB-TCPIP-BC-004
    [Documentation]    Duplicate connection name
    ...                !!! Wording of error message needs to be maintained !!! 
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/57
    ...                !!! test not in final version !!!

    set_test_variable    ${connection_type}    tcp_ip
    set_test_variable    ${test_category}    BADCASE

    conn_manager.connect    conn_name=QCB-TCPIP-BC-004-Connection
    ...                     conn_type=TCPIPClient
    ...                     conn_conf=${TCPIPClientParam}

    conn_manager.verify    conn_name=QCB-TCPIP-BC-004-Connection    search_pattern=BC-004 ACK    send_cmd=BC-004

    # same connection name again
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.connect    conn_name=QCB-TCPIP-BC-004-Connection
                                                               ...                     conn_type=TCPIPClient
                                                               ...                     conn_conf=${TCPIPClientParam}

    log    TCPIP-BC-004 'connect' status: ${status}    console=yes
    log    TCPIP-BC-004 'connect' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    # !!! Wording of error message needs to be maintained !!! 
    should_be_equal    ${result}    The connection name 'QCB-TCPIP-BC-004-Connection' has already existed! Please use other name


