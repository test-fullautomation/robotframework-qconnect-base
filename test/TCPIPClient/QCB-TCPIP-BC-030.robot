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

QCB-TCPIP-BC-030
    [Documentation]    Test parameter validation: fetch_block=False with custom eob_pattern should fail

    # supports HTML overview
    set_test_variable    ${connection_type}    TCPIPClient
    set_test_variable    ${test_category}      BADCASE

    set_test_variable    ${connection_name}    QCB-TCPIP-BC-030-Connection

    # Test parameter validation - no connection needed since validation happens first

    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=${connection_name}
                                                               ...                    search_pattern=.*
                                                               ...                    timeout=1
                                                               ...                    fetch_block=${False}
                                                               ...                    eob_pattern=END
                                                               ...                    send_cmd=PING

    log    TCPIP-BC-030 'verify' status: ${status}    console=yes
    log    TCPIP-BC-030 'verify' result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_contain     ${result}    Parameter 'eob_pattern' is only applicable when 'fetch_block' is True