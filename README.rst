.. Copyright 2020-2026 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Package Description
===================

Table of Contents
-----------------

-  `Getting Started <#getting-started>`__

   -  `How to install <#how-to-install>`__
-  `Usage <#building-and-testing>`__
-  `Example <#example>`__
-  `Contribution Guidelines <#contribution-guidelines>`__
-  `Configure Git and correct EOL
   handling <#configure-Git-and-correct-EOL-handling>`__
-  `Sourcecode Documentation <#documentation>`__
-  `Feedback <#feedback>`__
-  `About <#about>`__

   -  `Maintainers <#maintainers>`__
   -  `Contributors <#contributors>`__
   -  `3rd Party Licenses <#3rd-party-licenses>`__
   -  `Used Encryption <#used-encryption>`__
   -  `License <#license>`__

Getting Started
---------------

**QConnectBase** is a library that enables `Robot Framework <https://robotframework.org>`__
to establish and manage connections to external systems.

**QConnectBase** provides a mechanism for continuously receiving trace logs from a connection (such as Raw TCP,
SSH, Serial, etc.) while sending data back to the remote side. It's especially efficient for monitoring
overflood response trace logs from asynchronous trace systems.
It supports Python 3.7+ and Robot Framework 6.1+.

How to install
--------------

**QConnectBase** can be installed in two different ways.

1. Installation via PyPi (recommended for users)

   .. code::

      pip install robotframework-qconnect-base

   `QConnectBase in PyPi <https://pypi.org/project/robotframework-qconnect-base/>`_

2. Installation via GitHub (recommended for developers)

   * Clone the **robotframework-qconnect-base** repository to your machine.

     .. code::

        git clone https://github.com/test-fullautomation/robotframework-qconnect-base.git

     `QConnectBase in GitHub <https://github.com/test-fullautomation/robotframework-qconnect-base>`_

   * Use the following command to install **QConnectBase** (executed in repository main folder):

     .. code::

        python -m pip install .

     Or:

     .. code::

        python -m pip install --proxy <proxy> .

     This command will also download and install all dependencies that are required to work with the source files in the current repository.
     After the initial installation of **QConnectBase** is done, you have the following two possibilities:

     1. *Clean the previous installation*:

        .. code::

           python "./cleanup_installation.py"

        ``cleanup_installation.py`` explicitly deletes all files and folders within the component installation folder under
        ``site-packages`` and also deletes local build artefacts.

     2. *Render the component documentation*:

        .. code::

           python "./genpackagedoc.py"

        This would e.g. be required in case of changes in the interface of **QConnectBase**.

        The documentation is rendered by a separate application called **GenPackageDoc**, that is part
        of the build dependencies and runtime dependencies of **QConnectBase**.

        **GenPackageDoc** needs to be configured. Details about how to do this, can be found in the
        `README.rst <https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/README.rst>`_
        (sections *Install dependencies* and *Configure dependencies*).

   * Use the following command to build **QConnectBase** (executed in repository main folder):

     .. code::

        python -m build .

     Or:

     .. code::

        python -m pip config set global.proxy <proxy>
        python -m build .


Usage
-----

**QConnectBase** supports the following Robot Framework keywords to establish and manage connections to external systems:

**connect**
~~~~~~~~~~~

  **Establishes a connection.**

  **Syntax**:

   **connect**  ``[conn_name]   [conn_conf]``
   *(All parameters are required to be in order)*\

   or

   **connect**
   ``conn_name=[conn_name]   conn_conf=[conn_conf]``
   *(All parameters are assigned by name)*

  **Note**: Although previous syntax with 4 arguments is still supported for backward compatibility, only **conn_name** and **conn_conf** are now required.
  **conn_type** and **conn_mode** can be provided inside **conn_conf**.

  **Arguments**:

    **conn_name**: Name of the connection.

    **conn_conf**: A dictionary containing configurations for the connection.

      It must include **conn_type**, and optionally **conn_mode** and other connection-specific fields (depending on type).

      This replaces the need to pass **conn_type** and **conn_mode** as separate arguments.

      Each **conn_type** requires a specific structure in **conn_conf**. Below are examples for each supported type:

        *  **TCPIPClient**: Create a Raw TCPIP connection to TCP Server.

        ::

         {
             "conn_type": "TCPIPClient",
             "address": [server host], # Optional. Default value is "localhost".
             "port": [server port],     # Optional. Default value is 1234.
             "logfile": [Log file path. Possible values: 'nonlog', 'console', <user define path>]
          }

        *  **SSHClient**: Create a client connection to a SSH server.

        ::

          {
              "conn_type": "SSHClient",
              "address" : [server host],  # Optional. Default value is "localhost".
              "port" : [server host],     # Optional. Default value is 22.
              "username" : [username],    # Optional. Default value is "root".
              "password" : [password],    # Optional. Default value is "".
              "authentication" : "password" | "keyfile" | "passwordkeyfile",  # Optional. Default value is "".
              "key_filename" : [filename or list of filenames], # Optional. Default value is null.
              "logfile": [Log file path. Possible values: 'nonlog', 'console', <user define path>]
           }

        *  **SerialClient**: Create a client connection via Serial Port.

        ::

          {
              "conn_type": "SerialClient",
              "port" : [comport or null],
              "baudrate" : [Baud rate such as 9600 or 115200 etc.],
              "bytesize" : [Number of data bits. Possible values: 5, 6, 7, 8],
              "stopbits" : [Number of stop bits. Possible values: 1, 1.5, 2],
              "parity" : [Enable parity checking. Possible values: 'N', 'E', 'O', 'M', 'S'],
              "rtscts" : [Enable hardware (RTS/CTS) flow control.],
              "xonxoff" : [Enable software flow control.],
              "logfile": [Log file path. Possible values: 'nonlog', 'console', <user define path>]
           }

  **Legacy Syntax** (Still Supported):

   **connect**  ``[conn_name]   [conn_type]   [conn_conf]   [conn_mode]``
   *(All parameters are required to be in order)*\

   or

   **connect**
   ``conn_name=[conn_name]   conn_type=[conn_type]   conn_conf=[conn_conf]   conn_mode=[conn_mode]``
   *(All parameters are assigned by name)*


**disconnect**
~~~~~~~~~~~~~~

  **Disconnects a connection by name.**

  **Syntax**:

   **disconnect** ``conn_name``

  **Arguments**:

    **conn_name**: Name of the connection.

**send command**
~~~~~~~~~~~~~~~~

  **Sends a command to the other side of the connection.**

  **Syntax**:

   **send command** ``[conn_name]   [command]`` *(All parameters are
   required to be in order)*\

   or

   **send command**
   ``conn_name=[conn_name]   command=[command]`` *(All parameters are
   assigned by name)*

  **Arguments**:

   **conn_name**: Name of the connection.

   **command**: Command to be sent.

**verify**
~~~~~~~~~~

  **Verifies a response from the connection if it matched a pattern.**

  **Syntax**:

   **verify**
   ``[conn_name]   [search_pattern]   [timeout]   [fetch_block]  [eob_pattern] [filter_pattern]  [send_cmd]``\ *(All
   parameters are required to be in order)*\

   or

   **verify**  ``conn_name=[conn_name]   search_pattern=[search_pattern]  timeout=[timeout]  fetch_block=[fetch_block]  eob_pattern=[eob_pattern] filter_pattern=[filter_pattern]  send_cmd=[send_cmd]``
   *(All parameters are assigned by name)*

  **Arguments**:

    **conn_name**: Name of the connection.

    **search_pattern**: Regular expression for matching with the response.

    **timeout**: Timeout for waiting response matching pattern.

    **fetch_block**: If this value is true, every response line will be put into a block untill a line match **eob_pattern** pattern.

    **eob_pattern**: Regular expression for matching the endline when using **fetch_block**.

    **filter_pattern**: Regular expression for filtering every line of block when using **fetch_block**.

    **send_cmd**: Command to be sent to the other side of connection and waiting for response.

  **Return value**:

   **List of captured string from search_pattern**

   **E.g.**
   The message from connection is **This is the 1st test command.**

   The `verify` keyword of RobotFramework test case is defined as below:

   ::

       ${result} = verify  conn_name=SSH_Connection
                            search_pattern=(?<=\s).*([0-9]..).*(command).$
                            send_cmd=*echo This is the 1st test command.*

   The result will be a list of 2 strings:

   - **${result}[0]** will be **"1st"** which is the first captured string.
   - **${result}[1]** will be **"command"** which is the second captured string.

Example
-------

::

   *** Settings ***
   Documentation    Suite description
   Library     QConnectBase.ConnectionManager

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

Contribution Guidelines
-----------------------

**QConnectBase** is designed for ease of making an extension library. By that way you can take advantage of the
infrastructure of **QConnectBase** for handling your own connection protocol. For creating an extension library
for **QConnectBase**, please following below steps.

1.  Create a library package which have the prefix name is **robotframework-qconnect-**\ *[your specific name]*.

2.  Your hadling connection class should be derived from **QConnectBase.connection_base.ConnectionBase**  class.

3.  In your *Connection Class*, override below attributes and methods:

  -  **_CONNECTION_TYPE**: name of your connection type. It will be the input of the conn\_type argument when using **connect** keyword. Depend on the type name, the library will detemine the correct connection handling class.

  -  **__init__(self, \_mode, config)**: in this constructor method, you should:

    - Prepare resource for your connection.
    - Initialize receiver thread by calling **self._init_thread_receiver(cls._socket_instance, mode="")** method.
    - Configure and initialize the lowlevel receiver thread (if it’s necessary) as below

      ::

        self._llrecv_thrd_obj = None
        self._llrecv_thrd_term = threading.Event()
        self._init_thrd_llrecv(cls._socket_instance)


    - Incase you use the lowlevel receiver thread. You should implement the **thrd_llrecv_from_connection_interface()** method. This method is a mediate layer which will receive the data from connection at the very beginning, do some process then put them in a queue for the **receiver thread** above getting later.
    - Create the queue for this connection (use Queue.Queue).

  - **connect()**: implement the way you use to make your own connection protocol.
  - **_read()**: implement the way to receive data from connection.
  - **_write()**: implement the way to send data via connection.
  - **disconnect()**: implement the way you use to disconnect your own connection protocol.
  - **quit()**: implement the way you use to quit connection and clean resource.

Configure Git and correct EOL handling
--------------------------------------

Here you can find the references for `Dealing with line
endings <https://help.github.com/articles/dealing-with-line-endings/>`__.

Every time you press return on your keyboard you’re actually inserting
an invisible character called a line ending. Historically, different
operating systems have handled line endings differently. When you view
changes in a file, Git handles line endings in its own way. Since you’re
collaborating on projects with Git and GitHub, Git might produce
unexpected results if, for example, you’re working on a Windows machine,
and your collaborator has made a change in OS X.

To avoid problems in your diffs, you can configure Git to properly
handle line endings. If you are storing the .gitattributes file directly
inside of your repository, than you can asure that all EOL are manged by
git correctly as defined.

Sourcecode Documentation
------------------------

A detailed documentation of the QConnectBase package can also be found here: `QConnectBase.pdf <https://github.com/test-fullautomation/robotframework-qconnect-base/blob/develop/QConnectBase/QConnectBase.pdf>`_

Feedback
--------

If you have any problem when using the library or think there is a
better solution for any part of the library, I’d love to know it, as
this will all help me to improve the library. Please don't hesitate
to contact me.

Do share your valuable opinion, I appreciate your honest feedback!

About
-----

Maintainers
~~~~~~~~~~~

`Nguyen Huynh Tri Cuong <mailto:Cuong.NguyenHuynhTri@vn.bosch.com>`_

Contributors
~~~~~~~~~~~~

`Nguyen Huynh Tri Cuong <mailto:Cuong.NguyenHuynhTri@vn.bosch.com>`_

`Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_


License
-------

Copyright 2020-2026 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
