Class: InputParam
=================

.. code::python

   QConnectBase.connection_manager

Method: get_attr_list
---------------------

Class: ConnectParam
===================

.. code::python

   QConnectBase.connection_manager

Class for storing parameters for connect action.
   
Class: SendCommandParam
=======================

.. code::python

   QConnectBase.connection_manager

Class for storing parameters for send command action.
   
Class: VerifyParam
==================

.. code::python

   QConnectBase.connection_manager

Class for storing parameters for verify action.
   
Class: ConnectionManager
========================

.. code::python

   QConnectBase.connection_manager

Class to manage all connections.
Method: quit
------------

Quit connection manager.

**Returns:**
         None.
      
Method: add_connection
----------------------

Add a connection to managed dictionary.

**Arguments:**

* ``name``

  / *Condition*: require / *Type*: str /

  Connection's name.

* ``conn``

  / *Condition*: require / *Type*: socket.socket /

  Connection object.

**Returns:**
         None.
      
Method: remove_connection
-------------------------

Remove a connection by name.

**Arguments:**

* ``connection_name``

  / *Condition*: require / *Type*: str /

  Connection's name.

**Returns:**
         None.
      
Method: get_connection_by_name
------------------------------

Get an exist connection by name.

**Arguments:**

* ``connection_name``

  / *Condition*: require / *Type*: str /

  Connection's name.

**Returns:**

* ``conn``

  / *Type*: socket.socket /

  Connection object.
      
Method: disconnect
------------------

Keyword for disconnecting a connection by name.

**Arguments:**

* ``connection_name``

  / *Condition*: require / *Type*: str /

  Connection's name.

**Returns:**
         None.
      
Method: connect
---------------

Keyword for making a connection.

**Arguments:**

* ``args``

  / *Condition*: require / *Type*: tuple /

  Non-Keyword Arguments.

* ``kwargs``

  / *Condition*: require / *Type*: dict /

  Keyword Arguments.

**Returns:**
         None.
      
Method: connect_named_args
--------------------------

Making a connection with name arguments.

**Arguments:**

  * ``kwargs``

  / *Condition*: require / *Type*: dict /

  Keyword Arguments.

**Returns:**
         None.
      
Method: connect_unnamed_args
----------------------------

Making a connection.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Name of connection.

* ``connection_type``

  / *Condition*: optional / *Type*: str /

  Type of connection.

* ``mode``

  / *Condition*: optional / *Type*: str /

  Connection mode.

* ``config``

  / *Condition*: optional / *Type*: json /

  Configuration for connection.

**Returns:**
         None.
      
Method: send_command
--------------------

Keyword for sending command to a connection.

**Arguments:**

* ``args``

  / *Condition*: require / *Type*: tuple /

  Non-Keyword Arguments.

* ``kwargs``

  / *Condition*: require / *Type*: dict /

  Keyword Arguments.

**Returns:**
         None.
      
Method: send_command_named_args
-------------------------------

Send command to a connection with name arguments.

**Arguments:**

  * ``kwargs``

  / *Condition*: require / *Type*: dict /

  Keyword Arguments.

**Returns:**
         None.
      
Method: send_command_unnamed_args
---------------------------------

Send command to a connection.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Name of connection.

* ``command``

  / *Condition*: optional / *Type*: str /

  Command to be sent.

**Returns:**
         None.
      
Method: verify
--------------

Keyword uses to verify a pattern from connection response after sending a command.

**Arguments:**

* ``args``

  / *Condition*: require / *Type*: tuple /

  Non-Keyword Arguments.

* ``kwargs``

  / *Condition*: require / *Type*: dict /

  Keyword Arguments.

**Returns:**

* ``match_res``

  / *Type*: str /

  Matched string.
      
Method: verify_named_args
-------------------------

Verify a pattern from connection response after sending a command with named arguments.

**Arguments:**

* ``kwargs``

  / *Condition*: require / *Type*: dict /

  Keyword Arguments.

**Returns:**

* ``match_res``

  / *Type*: str /

  Matched string.
      
Method: verify_unnamed_args
---------------------------

      Verify a pattern from connection response after sending a command.

**Arguments:**

* ``connection_name``

  / *Condition*: required / *Type*: str /

  Name of connection.

* ``search_obj``

  / *Condition*: optional / *Type*: str /

  Regular expression all received trace messages are compare to.
  Can be passed either as a string or a regular expression object. Refer to Python documentation for module 're'.

* ``fetch_block``

  / *Condition*: optional / *Type*: bool /

  Determine if 'fetch block' feature is used.

* ``eob_pattern``

  / *Condition*: optional / *Type*: str /

  The end of block pattern.

* ``filter_pattern``

  / *Condition*: optional / *Type*: str /

  Pattern to filter message line by line.

* ``timeout``

  / *Condition*: optional / *Type*: re.Pattern /

  Timeout parameter specified as a floating point number in the unit 'seconds'.

* ``fct_args``

  / *Condition*: optional / *Type*: Tuple /

  List of function arguments passed to be sent.

**Returns:**

* ``match_res``

  / *Type*: str /

  Matched string.
      
Class: TestOption
=================

.. code::python

   QConnectBase.connection_manager

