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

# Robot Framework Built-In libraries
Library    Collections
Library    BuiltIn
Library    Process

# the library under test
Library    QConnectBase.ConnectionManager    WITH NAME    conn_manager

# additional libraries
Library    RobotframeworkExtensions.Collection    WITH NAME    rf.extensions
Library    ./tcp_ip_selftest_lib.py    WITH NAME    tcpip.selftest

*** Variables ***

${HOST}=    localhost
${PORT}=    ${4000}

&{TCPIPClientParam}    conn_type=TCPIPClient
...                    saddress=${HOST}
...                    port=${PORT}
...                    logfile=./tcp_ip_incoming.log

*** Keywords ***

qconnectbase_suite_setup
    [Documentation]    QConnectBase Suite Setup

    log    executing QConnectBase Suite Setup

    tcpip.selftest.start_tcpip_testserver    host=${HOST}    port=${PORT}    max_connections=${1}
    tcpip.selftest.write_html_header_of_overview_file


qconnectbase_suite_teardown
    [Documentation]    QConnectBase Suite Teardown

    log     executing QConnectBase Suite Teardown

    tcpip.selftest.quit_tcpip_testserver
    tcpip.selftest.write_html_footer_of_overview_file

    IF    $SUITE_STATUS == 'PASS'
        log    SUITE '${SUITE_NAME}' finished with result '${SUITE_STATUS}'    console=True
    ELSE
        log    SUITE '${SUITE_NAME}' finished with result '${SUITE_STATUS}', reason: ${SUITE_MESSAGE}    console=True
    END

qconnectbase_test_setup
    [Documentation]    QConnectBase Test Setup

    log    executing QConnectBase Test Setup


qconnectbase_test_teardown
    [Documentation]    QConnectBase Test Teardown

    log    executing QConnectBase Test Teardown

    tcpip.selftest.add_test_to_overview

    IF    $TEST_STATUS == 'PASS'
        log    TEST '${TEST_NAME}' finished with result '${TEST_STATUS}'    console=True
    ELSE
        log    TEST '${TEST_NAME}' finished with result '${TEST_STATUS}', reason: ${TEST_MESSAGE}    console=True
    END
