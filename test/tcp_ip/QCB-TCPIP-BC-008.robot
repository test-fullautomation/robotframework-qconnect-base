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

*** Variables ***

&{TCPIPClientParam_err}    address=${HOST}
...                        port=INVALID
...                        logfile=./tcp_ip_incoming_BC-008.log

*** Test Cases ***

QCB-TCPIP-BC-008
    [Documentation]    Invalid type of connection configuration parameter

    set_test_variable    ${connection_type}    tcp_ip
    set_test_variable    ${test_category}    BADCASE

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.connect    conn_name=QCB-TCPIP-BC-008-Connection
                                                               ...                     conn_type=TCPIPClient
                                                               ...                     conn_conf=${TCPIPClientParam_err}

    Sleep    1s

    conn_manager.disconnect    conn_name=QCB-TCPIP-BC-008-Connection

    log    TCPIP-BC-008 'connect' status: ${status}    console=yes
    log    TCPIP-BC-008 'connect' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_be_equal    ${result}    Unable to create connection. Exception: invalid literal for int() with base 10: 'INVALID'

