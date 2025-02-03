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

QCB-TCPIP-GC-100
    [Documentation]    Communication in two threads.
    ...                Thread 1 this is an observer thread not sending an own command
    ...                but explicitly waiting for an incoming message that is triggered
    ...                by a command sent from thread 2.

    conn_manager.connect    conn_name=QCB-TCPIP-GC-100-Connection
    ...                     conn_type=TCPIPClient
    ...                     conn_conf=${TCPIPClientParam}

    THREAD    VERIFY-THREAD-1     False
        # now own send_cmd, simply waiting; 'GC-100-T2-6' triggered by VERIFY-THREAD-2
        conn_manager.verify    conn_name=QCB-TCPIP-GC-100-Connection    search_pattern=GC-100-T2-6    match_try=12
        send_thread_notification    VERIFY_THREAD_1_DONE
    END

    THREAD    VERIFY-THREAD-2     False
        FOR    ${index}    IN RANGE    1    11
            conn_manager.verify    conn_name=QCB-TCPIP-GC-100-Connection    search_pattern=GC-100-T2-${index}    match_try=6    send_cmd=GC-100-T2-${index}
        END
        send_thread_notification    VERIFY_THREAD_2_DONE
    END

    wait_thread_notification    VERIFY_THREAD_1_DONE    timeout=120
    wait_thread_notification    VERIFY_THREAD_2_DONE    timeout=120

    conn_manager.disconnect    QCB-TCPIP-GC-100-Connection

