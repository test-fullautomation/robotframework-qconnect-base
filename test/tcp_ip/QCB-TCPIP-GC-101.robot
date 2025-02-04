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

QCB-TCPIP-GC-101
    [Tags]    threading
    [Documentation]    Communication in two threads.
    ...                Answer from server in thread 2 has a delay of 10 seconds
    ...                while thread 1 verifies several messages in a loop.

    conn_manager.connect    conn_name=QCB-TCPIP-GC-101-Connection
    ...                     conn_type=TCPIPClient
    ...                     conn_conf=${TCPIPClientParam}

    THREAD    VERIFY-THREAD-1     False
        FOR    ${index}    IN RANGE    1    21
            conn_manager.verify    conn_name=QCB-TCPIP-GC-101-Connection    search_pattern=GC-101-T1-${index}    match_try=6    send_cmd=GC-101-T1-${index}
        END
        send_thread_notification    VERIFY_THREAD_2_DONE
    END

    sleep    0.6s

    THREAD    VERIFY-THREAD-2     False
        conn_manager.verify    conn_name=QCB-TCPIP-GC-101-Connection    search_pattern=DELAY10-GC-101-T2    match_try=30    send_cmd=DELAY10-GC-101-T2
        send_thread_notification    VERIFY_THREAD_1_DONE
    END

    wait_thread_notification    VERIFY_THREAD_1_DONE    timeout=150
    wait_thread_notification    VERIFY_THREAD_2_DONE    timeout=150

    conn_manager.disconnect    QCB-TCPIP-GC-101-Connection
