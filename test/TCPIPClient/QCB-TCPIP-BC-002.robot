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
    ...                !!! needs to be completed (currently fails under Linux; reason unclear) !!!
    ...                !!! test not in final version !!!

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      BADCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-BC-002-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParamTS}

    # let the testserver close the connection
    conn_manager.verify    conn_name=${connection_name}
    ...                    search_pattern=QCB-TCPIP-BC-002 ACK
    ...                    timeout=2
    ...                    match_try=4
    ...                    send_cmd=CLOSE_CONNECTION-QCB-TCPIP-BC-002

    # give the testserver some time to send the answer 'QCB-TCPIP-BC-002 ACK' and close the connection
    Sleep    4s

    # # version 1 (send_command)
    # # try to send a command with the connection already closed by testserver
    # ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.send_command
    # ...                                                        conn_name=${connection_name}
    # ...                                                        command=TCPIP-BC-002-SHOULDNOTBESENT

    # log    TCPIP-BC-002 'send_command' status: ${status}    console=yes
    # log    TCPIP-BC-002 'send_command' result: ${result}    console=yes

    # # to be verified: currently fails under Linux; reason unclear
    # should_be_equal    ${status}    FAIL
    # should_contain    ${result}    Unable to send command to 'QCB-TCPIP-BC-002-Connection' connection. Exception: Connection has been broken.

    # Sleep    1s

    # !!! TODO: divide into two tests (version 1 and version 2) !!!

    # version 2 (verify)
    # try to verify with the connection already closed by testserver
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=NEVER_WILL_BE_RECEIVED
                                                               ...                    send_cmd=TCPIP-BC-002

    log    TCPIP-BC-002 'verify' status: ${status}    console=yes
    log    TCPIP-BC-002 'verify' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_be_equal    ${result}    Connection has been broken while trying to match the pattern.

    Sleep    1s

    # this shouldn't matter (because of connection alread closed by testserver):
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.disconnect    ${connection_name}

    log    TCPIP-BC-002 'disconnect' status: ${status}    console=yes
    log    TCPIP-BC-002 'disconnect' result: ${result}    console=yes

    should_be_equal    ${status}    PASS
    should_be_equal    ${result}    ${None}

