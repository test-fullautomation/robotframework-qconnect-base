#  Copyright 2020-2023 Robert Bosch GmbH
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
Documentation    Suite description
Library     QConnectionLibrary.ConnectionManager
Suite Teardown  Close Connection

*** Variables ***
${CONNECTION_NAME}  TEST_CONN

*** Test Cases ***
Test SSH Connection
    # Create config for connection.
    ${config_string}=    catenate
    ...  {\n
    ...   "address": "127.0.0.1",\n
    ...   "port": 8022,\n
    ...   "username": "root",\n
    ...   "password": "",\n
    ...   "authentication": "password",\n
    ...   "key_filename": null\n
    ...  }
    log to console       \nConnecting with below configurations:\n${config_string}
    ${config}=             evaluate        json.loads('''${config_string}''')    json

    # Connect to the target with above configurations.
    connect  conn_name=${CONNECTION_NAME}
    ...      conn_type=SSHClient
    ...      conn_conf=${config}

    # Send command 'cd ..' and 'ls' then wait for the response '.*' pattern.
    ${pass_status}=    run keyword and return status
    ...                send command      conn_name=${CONNECTION_NAME}
    ...                                  command=cd ..

    ${res}=     run keyword if      ${pass_status}
    ...         verify     conn_name=${CONNECTION_NAME}
    ...                    search_pattern=(.*)
    ...                    send_cmd=ls

    log to console     ${res}[1]

*** Keyword ***
Close Connection
    disconnect  ${CONNECTION_NAME}


