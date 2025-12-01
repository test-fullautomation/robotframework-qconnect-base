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

QCB-TCPIP-BC-005
    [Documentation]    Invalid connection type in keyword 'connect'

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      BADCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-BC-005-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=INVALID_CONNECTION_TYPE
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.connect    conn_name=${connection_name}
                                                               ...                     conn_conf=${TCPIPClientParam}

    log    TCPIP-BC-005 'connect' status: ${status}    console=yes
    log    TCPIP-BC-005 'connect' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_match_regexp    ${result}    The connection type 'INVALID_CONNECTION_TYPE' is not supported. Please choose one of: (DLT, DLTConnector, GoepelClient, )?RabbitmqClient, SSHClient, SerialClient, TCPIPClient, TCPIPServer, (TTFisclient, )?Winapp\.$
