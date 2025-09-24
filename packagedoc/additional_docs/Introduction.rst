.. Copyright 2020-2023 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

The **QConnectBase** package provides Robot Framework keywords for interacting
with devices, servers, or services through various communication protocols such
as *TCP/IP*, *SSH*, or *Serial*.
It enables users to establish (multiple) connections, send commands, and verify
responses with ease.

Key features include:

- Support for multiple simultaneous connections.
- Built-in keywords for sending and receiving data.
- Protocol abstraction for TCP/IP, SSH, and Serial.
- Flexible connection management and session handling.
- Extensible architecture for custom protocols or behaviors.

Developers can also extend the **QConnectBase** class to support additional
connection types or specialized behaviors, ensuring the library remains
adaptable for diverse automation needs.