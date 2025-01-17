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

Documentation    Common settings for TCP/IP self tests of component 'QConnectBase'

Resource    ./imports/resources.resource

Suite Setup       qconnectbase_suite_setup
Suite Teardown    qconnectbase_suite_teardown

Test Setup       qconnectbase_test_setup
Test Teardown    qconnectbase_test_teardown

