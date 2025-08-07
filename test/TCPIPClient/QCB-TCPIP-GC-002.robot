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

QCB-TCPIP-GC-002
    [Documentation]    Send simple command to testserver (send_command)

    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}    GOODCASE

    conn_manager.connect    conn_name=QCB-TCPIP-GC-002-Connection
    ...                     conn_type=${connection_type}
    ...                     conn_conf=${TCPIPClientParam}

    conn_manager.send_command    conn_name=QCB-TCPIP-GC-002-Connection    command=GC-002

    Sleep    2s

    conn_manager.disconnect    QCB-TCPIP-GC-002-Connection

