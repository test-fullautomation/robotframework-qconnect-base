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

QCB-TCPIP-GC-102
    [Documentation]    Communication in two threads, using their own connection established inside the threads.
    ...                Answer from server in thread 1 has a delay of 10 seconds.

    THREAD    VERIFY-THREAD-1     False
        conn_manager.connect    conn_name=QCB-TCPIP-GC-102-Connection-T1
        ...                     conn_type=TCPIPClient
        ...                     conn_conf=${TCPIPClientParam}
        conn_manager.verify    conn_name=QCB-TCPIP-GC-102-Connection-T1    search_pattern=DELAY10-GC-102-T1    match_try=30    send_cmd=DELAY10-GC-102-T1
        conn_manager.disconnect    QCB-TCPIP-GC-102-Connection-T1
        send_thread_notification    VERIFY_THREAD_1_DONE
    END

    THREAD    VERIFY-THREAD-2     False
        conn_manager.connect    conn_name=QCB-TCPIP-GC-102-Connection-T2
        ...                     conn_type=TCPIPClient
        ...                     conn_conf=${TCPIPClientParam}
        FOR    ${index}    IN RANGE    1    21
            conn_manager.verify    conn_name=QCB-TCPIP-GC-102-Connection-T2    search_pattern=GC-102-T2-${index}    match_try=4    send_cmd=GC-102-T2-${index}
        END
        conn_manager.disconnect    QCB-TCPIP-GC-102-Connection-T2
        send_thread_notification    VERIFY_THREAD_2_DONE
    END

    wait_thread_notification    VERIFY_THREAD_1_DONE    timeout=120
    wait_thread_notification    VERIFY_THREAD_2_DONE    timeout=120

