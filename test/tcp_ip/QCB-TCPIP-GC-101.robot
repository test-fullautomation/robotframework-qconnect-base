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

QCB-TCPIP-GC-101
    [Tags]    threading
    [Documentation]    Communication in three threads. Three observer threads wait for certain blocks of incoming messages.
    ...                These messages are triggered by a command that is sent to the testserver after the observer threads
    ...                have been started.
    ...                !!! return values need to be defined after bugfix !!!
    ...                https://github.com/test-fullautomation/robotframework-qconnect-base/issues/101
    ...                !!! temporarily 'verify' replaced by 'send_command' !!!
    ...                !!! test not in final version !!!

    set_test_variable    ${connection_type}    tcp_ip
    set_test_variable    ${test_category}    GOODCASE

    conn_manager.connect    conn_name=QCB-TCPIP-GC-101-Connection
    ...                     conn_type=TCPIPClient
    ...                     conn_conf=${TCPIPClientParam}

    THREAD    OBSERVER-THREAD-1     False
        # listening only; no command sent to server
        ${result_1}=    conn_manager.verify    conn_name=QCB-TCPIP-GC-101-Connection
                        ...                    search_pattern=(\\[BLOCK-1\\])
                        ...                    eob_pattern=FETCHNESTEDBLOCKS_END
                        ...                    fetch_block=${True}
                        ...                    timeout=3
                        ...                    match_try=40
        log    QCB-TCPIP-GC-101 OBSERVER-THREAD-1 result: ${result_1}[0]    console=yes
        send_thread_notification    OBSERVER-THREAD-1-DONE    params=${result_1}
    END

    THREAD    OBSERVER-THREAD-2     False
        # listening only; no command sent to server
        ${result_2}=    conn_manager.verify    conn_name=QCB-TCPIP-GC-101-Connection
                        ...                    search_pattern=(\\[BLOCK-2\\])
                        ...                    eob_pattern=FETCHNESTEDBLOCKS_END
                        ...                    fetch_block=${True}
                        ...                    timeout=3
                        ...                    match_try=40
        log    QCB-TCPIP-GC-101 OBSERVER-THREAD-2 result: ${result_2}[0]    console=yes
        send_thread_notification    OBSERVER-THREAD-2-DONE    params=${result_2}
    END

    THREAD    OBSERVER-THREAD-3     False
        # listening only; no command sent to server
        ${result_3}=    conn_manager.verify    conn_name=QCB-TCPIP-GC-101-Connection
                        ...                    search_pattern=(\\[BLOCK-3\\])
                        ...                    eob_pattern=FETCHNESTEDBLOCKS_END
                        ...                    fetch_block=${True}
                        ...                    timeout=3
                        ...                    match_try=40
        log    QCB-TCPIP-GC-101 OBSERVER-THREAD-3 result: ${result_3}[0]    console=yes
        send_thread_notification    OBSERVER-THREAD-3-DONE    params=${result_3}
    END

    # trigger for testserver to start sending nested blocks of messages

    # TODO: sometimes runs into timeout; reason unclear
    # => temporary 'verify' replaced by 'send_command'
    # ${result_4}=    conn_manager.verify    conn_name=QCB-TCPIP-GC-101-Connection
                    # ...                    search_pattern=FETCHNESTEDBLOCKS ACK
                    # ...                    timeout=1
                    # ...                    match_try=12
                    # ...                    send_cmd=FETCHNESTEDBLOCKS
    # log    QCB-TCPIP-GC-101 FETCHNESTEDBLOCKS trigger result: ${result_4}[0]    console=yes

    # alternative version:
    conn_manager.send_command    conn_name=QCB-TCPIP-GC-101-Connection    command=FETCHNESTEDBLOCKS

    wait_thread_notification    OBSERVER-THREAD-1-DONE    timeout=160
    set_test_variable    ${thread_1_return}    ${payloads}[0]

    wait_thread_notification    OBSERVER-THREAD-2-DONE    timeout=160
    set_test_variable    ${thread_2_return}    ${payloads}[0]

    wait_thread_notification    OBSERVER-THREAD-3-DONE    timeout=160
    set_test_variable    ${thread_3_return}    ${payloads}[0]

    # testserver sends a fix sequence; wait until sequence has been finished
    Sleep    6s

    conn_manager.disconnect    QCB-TCPIP-GC-101-Connection

    # TODO: !!! return values need to be defined after bugfix !!!
    # (currently a single value is returned only; but expected is a list of values)
    # !!! To be clarified: Is it allowed to access ${payloads} outside the notification also? !!!

    log    QCB-TCPIP-GC-101 thread_1_return: ${thread_1_return}    console=yes
    log    QCB-TCPIP-GC-101 thread_2_return: ${thread_2_return}    console=yes
    log    QCB-TCPIP-GC-101 thread_3_return: ${thread_3_return}    console=yes

    # TODO:
    # should_be_equal    ${thread_1_return}    ...
    # should_be_equal    ${thread_2_return}    ...
    # should_be_equal    ${thread_3_return}    ...

