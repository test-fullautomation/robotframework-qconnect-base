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

*** Variables ***

&{TCPIPClientParam_err}    address=${HOST}
...                        port=${PORT}
...                        INVALID=UNKNOWN
...                        logfile=./tcp_ip_incoming_BC-007.log

*** Test Cases ***

QCB-TCPIP-BC-007
    [Documentation]    Invalid connection configuration parameter
    ...                !!! The invalid parameter is ignored. No error thrown. Rework required !!!

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.connect    conn_name=QCB-TCPIP-BC-007-Connection
                                                               ...                     conn_type=TCPIPClient
                                                               ...                     conn_conf=${TCPIPClientParam_err}

    log    TCPIP-BC-007 'connect' status: ${status}    console=yes
    log    TCPIP-BC-007 'connect' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    # should_be_equal    ${result}    to be defined

    conn_manager.disconnect    conn_name=QCB-TCPIP-BC-007-Connection



    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.disconnect    conn_name=UNKNOWN_CONNECTION_NAME

    log    result: '${result}'    console=yes

    # this curtrently fails
    should_be_equal    ${status}    FAIL
    # after fix: # should_be_equal    ${result}    ....


