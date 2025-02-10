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

QCB-TCPIP-GC-006
    [Documentation]    Subsequent connections, commands (verify) and disconnections to same server
    ...                (different connection names)

    set_test_variable    ${connection_type}    tcp_ip
    set_test_variable    ${test_category}    GOODCASE

    FOR    ${connection_count}    IN RANGE    1    6
        log    TCPIP-GC-006 connection count ${connection_count}    console=yes

        conn_manager.connect    conn_name=QCB-TCPIP-GC-006-Connection-${connection_count}
        ...                     conn_type=TCPIPClient
        ...                     conn_conf=${TCPIPClientParam}

        conn_manager.verify    conn_name=QCB-TCPIP-GC-006-Connection-${connection_count}
        ...                    search_pattern=TCPIP-GC-006-${connection_count} ACK
        ...                    send_cmd=TCPIP-GC-006-${connection_count}

        conn_manager.disconnect    QCB-TCPIP-GC-006-Connection-${connection_count}

        Sleep    1s

    END

