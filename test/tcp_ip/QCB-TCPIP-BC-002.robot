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

QCB-TCPIP-BC-002
    [Documentation]    A command is sent that forces the testserver to close the connection. After this the test tries to send another command
    ...                (that uses the connection that has already been closed by the testserver).

    set_test_variable    ${connection_type}    tcp_ip
    set_test_variable    ${test_category}    BADCASE

    conn_manager.connect    conn_name=QCB-TCPIP-BC-002-Connection
    ...                     conn_type=TCPIPClient
    ...                     conn_conf=${TCPIPClientParam}

    # let the testserver close the connection
    conn_manager.verify    conn_name=QCB-TCPIP-BC-002-Connection
    ...                    search_pattern=QCB-TCPIP-BC-002 ACK
    ...                    timeout=2
    ...                    match_try=4
    ...                    send_cmd=CLOSE_CONNECTION-QCB-TCPIP-BC-002

    # give the testserver some time to send the answer 'QCB-TCPIP-BC-002 ACK' and close the connection
    Sleep    4s

    # try to send a command with the already closed connection
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.send_command
    ...                                                        conn_name=QCB-TCPIP-BC-002-Connection
    ...                                                        command=TCPIP-BC-002-SHOULDNOTBESENT

    Sleep    1s

    conn_manager.disconnect    QCB-TCPIP-BC-002-Connection

    log    TCPIP-BC-002 'send_command' status: ${status}    console=yes
    log    TCPIP-BC-002 'send_command' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_contain    ${result}    Unable to send command to 'QCB-TCPIP-BC-002-Connection' connection. Exception: Connection has been broken.


