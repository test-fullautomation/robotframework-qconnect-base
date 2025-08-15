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

QCB-TCPIP-GC-100
    [Tags]    threading
    [Documentation]    Communication in two threads. The first thread waits for an incoming message
    ...                that is triggered by a command sent within the second thread.

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      GOODCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-GC-100-Connection

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    THREAD    VERIFY-THREAD-1     False
        # no own send_cmd in this thread, simply waiting; search_pattern 'GC-100-T2-6' triggered by VERIFY-THREAD-2
        conn_manager.verify    conn_name=${connection_name}    search_pattern=GC-100-T2-6    match_try=12
        send_thread_notification    VERIFY_THREAD_1_DONE
    END

    THREAD    VERIFY-THREAD-2     False
        FOR    ${index}    IN RANGE    1    11
            conn_manager.verify    conn_name=${connection_name}    search_pattern=GC-100-T2-${index}    match_try=6    send_cmd=GC-100-T2-${index}
        END
        send_thread_notification    VERIFY_THREAD_2_DONE
    END

    wait_thread_notification    VERIFY_THREAD_1_DONE    timeout=120
    wait_thread_notification    VERIFY_THREAD_2_DONE    timeout=120

    conn_manager.disconnect    ${connection_name}

