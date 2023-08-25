> Licensed under the Apache License, Version 2.0 (the \"License\"); you
> may not use this file except in compliance with the License. You may
> obtain a copy of the License at
>
> <http://www.apache.org/licenses/LICENSE-2.0>
>
> Unless required by applicable law or agreed to in writing, software
> distributed under the License is distributed on an \"AS IS\" BASIS,
> WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
> implied. See the License for the specific language governing
> permissions and limitations under the License.

# QConnectBase Library

QConnectBaseLibrary is a connection testing library for [Robot
Framework](https://robotframework.org). Library will be supported to
downloaded from PyPI soon. It provides a mechanism to handle trace log
continously receiving from a connection (such as Raw TCP, SSH, Serial,
etc.) besides sending data back to the other side. It's especially
efficient for monitoring the overflood response trace log from an
asynchronous trace systems. It is supporting Python 3.7+ and
RobotFramework 3.2+.

## Table of Contents

-   [Getting Started](#getting-started)
-   [Usage](#building-and-testing)
-   [Example](#example)
-   [Contribution Guidelines](#contribution-guidelines)
-   [Configure Git and correct EOL
    handling](#configure-Git-and-correct-EOL-handling)
-   [Sourcecode Documentation](#documentation)
-   [Feedback](#feedback)
-   [About](#about)
    -   [Maintainers](#maintainers)
    -   [Contributors](#contributors)
    -   [3rd Party Licenses](#3rd-party-licenses)
    -   [Used Encryption](#used-encryption)
    -   [License](#license)

## Getting Started

We have a plan to publish all the sourcecode as OSS in the near future
so that you can downloaded from PyPI. For the current period, you can
checkout

[QConnectBaseLibrary](https://github.com/test-fullautomation/robotframework-qconnect-base)

After checking out the source completely, you can install by running
below command inside **robotframework-qconnect-base** directory.

    python setup.py install

## Usage

QConnectBase Library support following keywords for testing connection
in RobotFramework.

### **connect**

> **Use for establishing a connection.**
>
> **Syntax**:
>
> > **connect** `[conn_name]   [conn_type]   [conn_mode]   [conn_conf]`
> > *(All parameters are required to be in order)* or
> >
> > **connect**
> > `conn_name=[conn_name]   conn_type=[conn_type]   conn_mode=[conn_mode]   conn_conf=[conn_conf]`
> > *(All parameters are assigned by name)*
>
> **Arguments**:
>
> > **conn_name**: Name of the connection.
> >
> > **conn_type**: Type of the connection. QConnectBaseLibrary has
> > supported below connection types:
> >
> > > -   **TCPIPClient**: Create a Raw TCPIP connection to TCP Server.
> > > -   **SSHClient**: Create a client connection to a SSH server.
> > > -   **SerialClient**: Create a client connection via Serial Port.
> >
> > **conn_mode**: (unused) Mode of a connection type.
> >
> > **conn_conf**: Configurations for making a connection. Depend on
> > **conn_type** (Type of Connection), there is a suitable
> > configuration in JSON format as below.
> >
> > > -   **TCPIPClient**
> > >
> > > ```{=html}
> > > <!-- -->
> > > ```
> > >     {
> > >         "address": [server host], # Optional. Default value is "localhost".
> > >         "port": [server port]     # Optional. Default value is 1234.
> > >         "logfile": [Log file path. Possible values: 'nonlog', 'console', <user define path>]
> > >      }
> > >
> > > -   **SSHClient**
> > >
> > > ```{=html}
> > > <!-- -->
> > > ```
> > >     {
> > >         "address" : [server host],  # Optional. Default value is "localhost".
> > >         "port" : [server host],     # Optional. Default value is 22.
> > >         "username" : [username],    # Optional. Default value is "root".
> > >         "password" : [password],    # Optional. Default value is "".
> > >         "authentication" : "password" | "keyfile" | "passwordkeyfile",  # Optional. Default value is "".
> > >         "key_filename" : [filename or list of filenames], # Optional. Default value is null.
> > >         "logfile": [Log file path. Possible values: 'nonlog', 'console', <user define path>]
> > >      }
> > >
> > > -   **SerialClient**
> > >
> > > ```{=html}
> > > <!-- -->
> > > ```
> > >     {
> > >         "port" : [comport or null],
> > >         "baudrate" : [Baud rate such as 9600 or 115200 etc.],
> > >         "bytesize" : [Number of data bits. Possible values: 5, 6, 7, 8],
> > >         "stopbits" : [Number of stop bits. Possible values: 1, 1.5, 2],
> > >         "parity" : [Enable parity checking. Possible values: 'N', 'E', 'O', 'M', 'S'],
> > >         "rtscts" : [Enable hardware (RTS/CTS) flow control.],
> > >         "xonxoff" : [Enable software flow control.],
> > >         "logfile": [Log file path. Possible values: 'nonlog', 'console', <user define path>]
> > >      }

### **disconnect**

> **Use for disconnect a connection by name.**
>
> **Syntax**:
>
> > **disconnect** `conn_name`
>
> **Arguments**:
>
> > **conn_name**: Name of the connection.

### **send command**

> **Use for sending a command to the other side of connection.**
>
> **Syntax**:
>
> > **send command** `[conn_name]   [command]` *(All parameters are
> > required to be in order)* or
> >
> > **send command** `conn_name=[conn_name]   command=[command]` *(All
> > parameters are assigned by name)* \##### *Arguments*:

-   **conn_name**: Name of the connection.
-   **command**: Command to be sent.

### **verify**

> **Use for verifying a response from the connection if it matched a
> pattern.**
>
> **Syntax**:
>
> > **verify**
> > `[conn_name]   [search_pattern]   [timeout]   [fetch_block]  [eob_pattern] [filter_pattern]  [send_cmd]`*(All
> > parameters are required to be in order)* or
> >
> > **verify**
> > `conn_name=[conn_name]   search_pattern=[search_pattern]  timeout=[timeout]  fetch_block=[fetch_block]  eob_pattern=[eob_pattern] filter_pattern=[filter_pattern]  send_cmd=[send_cmd]`
> > *(All parameters are assigned by name)*
>
> **Arguments**:
>
> > **conn_name**: Name of the connection.
> >
> > **search_pattern**: Regular expression for matching with the
> > response.
> >
> > **timeout**: Timeout for waiting response matching pattern.
> >
> > **fetch_block**: If this value is true, every response line will be
> > put into a block untill a line match **eob_pattern** pattern.
> >
> > **eob_pattern**: Regular expression for matching the endline when
> > using **fetch_block**.
> >
> > **filter_pattern**: Regular expression for filtering every line of
> > block when using **fetch_block**.
> >
> > **send_cmd**: Command to be sent to the other side of connection and
> > waiting for response.
>
> **Return value**:
>
> > **A corresponding match object if it is found.**
> >
> > **E.g.**
> >
> >     ${result} = verify  conn_name=SSH_Connection
> >                          search_pattern=(?<=\s).*([0-9]..).*(command).$
> >                          send_cmd=*echo This is the 1st test command.*
> >
> > -   \${result}\[0\] will be **\"This is the 1st test command.\"**
> >     which is the matched string.
> > -   \${result}\[1\] will be **\"1st\"** which is the first captured
> >     string.
> > -   \${result}\[2\] will be **\"command\"** which is the second
> >     captured string.

## Example

    *** Settings ***
    Documentation    Suite description
    Library     QConnectionLibrary.ConnectionManager

    *** Test Cases ***
    Test SSH Connection
        # Create config for connection.
        ${config_string}=    catenate
        ...  {
        ...   "address": "127.0.0.1",
        ...   "port": 8022,
        ...   "username": "root",
        ...   "password": "",
        ...   "authentication": "password",
        ...   "key_filename": null
        ...  }
        log to console       \nConnecting with configurations:\n${config_string}
        ${config}=             evaluate        json.loads('''${config_string}''')    json

        # Connect to the target with above configurations.
        connect             conn_name=test_ssh
        ...                 conn_type=SSHClient
        ...                 conn_conf=${config}

        # Send command 'cd ..' and 'ls' then wait for the response '.*' pattern.
        send command                conn_name=test_ssh
        ...                         command=cd ..

        ${res}=     verify                  conn_name=test_ssh
        ...                                 search_pattern=.*
        ...                                 send_cmd=ls
        log to console     ${res}

        # Disconnect
        disconnect  test_ssh

## Contribution Guidelines

QConnectBaseLibrary is designed for ease of making an extension library.
By that way you can take advantage of the QConnectBaseLibrary's
infrastructure for handling your own connection protocal. For creating
an extension library for QConnectBaseLibrary, please following below
steps.

1.  Create a library package which have the prefix name is
    **robotframework-qconnect-***\[your specific name\]*.
2.  Your hadling connection class should be derived from
    **QConnectionLibrary.connection_base.ConnectionBase** class.
3.  In your *Connection Class*, override below attributes and methods:

> -   **\_CONNECTION_TYPE**: name of your connection type. It will be
>     the input of the conn_type argument when using **connect**
>     keyword. Depend on the type name, the library will detemine the
>     correct connection handling class.
> -   **\_\_init\_\_(self, \_mode, config)**: in this constructor
>     method, you should:
>
> > -   Prepare resource for your connection.
> >
> > -   Initialize receiver thread by calling
> >     **self.\_init_thread_receiver(cls.\_socket_instance,
> >     mode=\"\")** method.
> >
> > -   Configure and initialize the lowlevel receiver thread (if it's
> >     necessary) as below
> >
> >         self._llrecv_thrd_obj = None
> >          self._llrecv_thrd_term = threading.Event()
> >          self._init_thrd_llrecv(cls._socket_instance)
> >
> > -   Incase you use the lowlevel receiver thread. You should
> >     implement the **thrd_llrecv_from_connection_interface()**
> >     method. This method is a mediate layer which will receive the
> >     data from connection at the very beginning, do some process then
> >     put them in a queue for the **receiver thread** above getting
> >     later.
> >
> > -   Create the queue for this connection (use Queue.Queue).
>
> -   **connect()**: implement the way you use to make your own
>     connection protocol.
> -   **\_read()**: implement the way to receive data from connection.
> -   **\_write()**: implement the way to send data via connection.
> -   **disconnect()**: implement the way you use to disconnect your own
>     connection protocol.
> -   **quit()**: implement the way you use to quit connection and clean
>     resource.

## Configure Git and correct EOL handling

Here you can find the references for [Dealing with line
endings](https://help.github.com/articles/dealing-with-line-endings/).

Every time you press return on your keyboard you're actually inserting
an invisible character called a line ending. Historically, different
operating systems have handled line endings differently. When you view
changes in a file, Git handles line endings in its own way. Since you're
collaborating on projects with Git and GitHub, Git might produce
unexpected results if, for example, you're working on a Windows machine,
and your collaborator has made a change in OS X.

To avoid problems in your diffs, you can configure Git to properly
handle line endings. If you are storing the .gitattributes file directly
inside of your repository, than you can asure that all EOL are manged by
git correctly as defined.

## Sourcecode Documentation

For investigating sourcecode, please refer to [QConnectBase library
documentation](docs/html/index.html)

A detailed documentation of the QConnectBase package can also be found
here:
[QConnectBase.pdf](https://github.com/test-fullautomation/robotframework-qconnect-base/blob/develop/QConnectBase/QConnectBase.pdf)

## Feedback

If you have any problem when using the library or think there is a
better solution for any part of the library, I'd love to know it, as
this will all help me to improve the library. Please don\'t hesitate to
contact me.

Do share your valuable opinion, I appreciate your honest feedback!

## About

### Maintainers

[Nguyen Huynh Tri Cuong](mailto:Cuong.NguyenHuynhTri@vn.bosch.com)

### Contributors

[Nguyen Huynh Tri Cuong](mailto:Cuong.NguyenHuynhTri@vn.bosch.com)

[Thomas Pollerspöck](mailto:Thomas.Pollerspoeck@de.bosch.com)

## License

Copyright 2020-2023 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the \"License\"); you
may not use this file except in compliance with the License. You may
obtain a copy of the License at

> <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an \"AS IS\" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
