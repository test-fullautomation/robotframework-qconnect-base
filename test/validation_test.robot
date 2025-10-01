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

# the library under test
Library    QConnectBase.ConnectionManager    WITH NAME    conn_manager

*** Test Cases ***

Test Parameter Validation Without Connection
    [Documentation]    Test parameter validation logic for eob_pattern and filter_pattern
    ...                This test will fail at connection check but should first validate parameters

    # Test 1: fetch_block=False with custom eob_pattern should fail with ValueError before connection check
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=nonexistent
                                                               ...                    search_pattern=.*
                                                               ...                    timeout=1
                                                               ...                    fetch_block=${False}
                                                               ...                    eob_pattern=END

    log    Test 1 status: ${status}    console=yes
    log    Test 1 result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_contain    ${result}    eob_pattern
    should_contain    ${result}    only applicable when 'fetch_block' is True

    # Test 2: fetch_block=False with custom filter_pattern should fail with ValueError before connection check
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=nonexistent
                                                               ...                    search_pattern=.*
                                                               ...                    timeout=1
                                                               ...                    fetch_block=${False}
                                                               ...                    filter_pattern=test_filter

    log    Test 2 status: ${status}    console=yes
    log    Test 2 result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    should_contain    ${result}    filter_pattern
    should_contain    ${result}    only applicable when 'fetch_block' is True

    # Test 3: fetch_block=False with default patterns should fail only at connection check (not parameter validation)
    ${status}    ${result}=    run_keyword_and_ignore_error    conn_manager.verify    conn_name=nonexistent
                                                               ...                    search_pattern=.*
                                                               ...                    timeout=1
                                                               ...                    fetch_block=${False}
                                                               ...                    eob_pattern=.*
                                                               ...                    filter_pattern=.*

    log    Test 3 status: ${status}    console=yes
    log    Test 3 result: ${result}    console=yes

    should_be_equal    ${status}    FAIL
    # Should fail with connection error, not parameter validation error
    should_not_contain    ${result}    only applicable when 'fetch_block' is True
    should_contain    ${result}    connection hasn't been established