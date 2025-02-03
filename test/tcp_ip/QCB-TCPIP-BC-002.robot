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

QCB-TCPIP-BC-002
    [Documentation]    Send command after testserver closed the connection !!! needs to be adapted after bugfix !!!

    conn_manager.connect    conn_name=QCB-TCPIP-BC-002-Connection
    ...                     conn_type=TCPIPClient
    ...                     conn_conf=${TCPIPClientParam}

    # let the testserver close the connection
    conn_manager.send_command    conn_name=QCB-TCPIP-BC-002-Connection    command=CLOSE_CONNECTION-BC-002

    # try to send a command without connection
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.send_command    conn_name=QCB-TCPIP-BC-002-Connection    command=BC-002

    log    TCPIP-BC-002 'send_command' status: ${status}    console=yes
    log    TCPIP-BC-002 'send_command' result: ${result}    console=yes

    # (does this make a difference in this case? -> extra testcase)
    # conn_manager.disconnect    QCB-TCPIP-BC-002-Connection

    ## current issue: QConnectBase does not react on this; status is PASS
    ## should_be_equal    ${status}    FAIL

    ## current issue: result is None
    # should_be_equal    ${result}    Unable to send command to 'QCB-TCPIP-BC-002-Connection' connection. Exception: Connection has been broken. Details: [WinError 10054] Eine vorhandene Verbindung wurde vom Remotehost geschlossen



