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

*** Variables ***

&{TCPIPClientParam_1}    address=${HOST}
...                      port=${PORT}
...                      logfile=./tcp_ip_incoming_1.log

&{TCPIPClientParam_2}    address=${HOST}
...                      port=${PORT}
# ...                      logfile=./tcp_ip_incoming_2.log

&{TCPIPClientParam_3}    address=${HOST}
...                      port=${PORT}
...                      INVALID=UNKNOWN
...                      logfile=./tcp_ip_incoming_3.log

&{TCPIPClientParam_4}    address=${HOST}
...                      port=12345
...                      logfile=./tcp_ip_incoming_4.log


&{TCPIPClientParam_q}    address=${HOST}
...                      port=${PORT}
...                      logfile=./tcp_ip_incoming_q.log

&{TCPIPClientParam_q2}    conn_type=TCPIPClient
...                       address=${HOST}
...                       port=${PORT}
...                       logfile=./tcp_ip_incoming_q2.log



*** Test Cases ***

QCB-TCPIP-QUICKTEST
    [Tags]    quicktest
    [Documentation]    QUICKTEST


    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      GOODCASE

    set_test_variable    ${connection_name}    TEST-CONNECTION

    # connection parameter for this test
    &{TCPIPClientParam}=    Create Dictionary    conn_type=${connection_type}
    ...                                          address=${HOST}
    ...                                          port=${PORT}
    ...                                          logfile=./tcp_ip_incoming.log
    # ...                                          logfile=${None}
    # ...                                          logfile=

    conn_manager.connect    conn_name=${connection_name}
    ...                     conn_conf=${TCPIPClientParam}

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    fetch_block=${False}
                                                               ...                    timeout=4
                                                               ...                    match_try=20
                                                               ...                    send_cmd=TESTMESSAGE
    Sleep    2s

    conn_manager.disconnect    ${connection_name}

