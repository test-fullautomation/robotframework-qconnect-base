#  Copyright 2020-2026 Robert Bosch GmbH
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

QCB-TCPIP-GC-040
    [Documentation]    Subsequent connections, commands (verify) and disconnections to same server
    ...                (always the same connection name)

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      GOODCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-GC-040-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    FOR    ${connection_count}    IN RANGE    1    6
        log    TCPIP-GC-040 connection count ${connection_count}    console=yes

        conn_manager.connect    conn_name=${connection_name}
        ...                     conn_conf=${TCPIPClientParam}

        conn_manager.verify    conn_name=${connection_name}    search_pattern=TCPIP-GC-040 ACK    send_cmd=TCPIP-GC-040

        conn_manager.disconnect    ${connection_name}

        Sleep    1s

    END

