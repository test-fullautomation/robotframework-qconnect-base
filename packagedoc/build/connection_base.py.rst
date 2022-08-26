Class: BrokenConnError
======================

.. code::python

   QConnectBase.connection_base

Class: ConnectionBase
=====================

.. code::python

   QConnectBase.connection_base

Base class for all connection classes.
   
Method: is_supported_platform
-----------------------------

Check if current platform is supported.

**Returns:**

* ``is_supported``

  / *Type*: bool /

  True if platform is supported.

  False if platform is not supported.
      
Method: is_precondition_pass
----------------------------

Check for precondition.

**Returns:**

         True if passing the precondition.

         False if failing the precondition.
      
Method: error_instruction
-------------------------

Get the error instruction.

**Returns:**

         Error instruction string.
      
Method: quit
------------

>> This method MUST be overridden in derived class <<

Abstract method for quiting the connection.

**Arguments:**

* ``is_disconnect_all``

  / *Condition*: optional / *Type*: bool /

  Determine if it's necessary to disconnect all connections.

**Returns:**

         None.
      
Method: connect
---------------

>> This method MUST be overridden in derived class <<

Abstract method for quiting the connection.

**Arguments:**

* ``device``

  / *Condition*: required / *Type*: str /

  Device name.

* ``device``

  / *Condition*: optional / *Type*: list /

  Trace file list if using dlt connection.

* ``test_connection``

  / *Condition*: optional / *Type*: bool /

  Deternmine if it's necessary for testing the connection.

**Returns:**

         None.
      
Method: disconnect
------------------

>> This method MUST be overridden in derived class <<

Abstract method for disconnecting connection.

**Arguments:**

* ``n_thrd_id``

  / *Condition*: required / *Type*: int /

  Thread id.

**Returns:**

         None.
      
Method: send_obj
----------------

Wrapper method to send message to a tcp connection.

**Arguments:**

* ``obj``

  / *Condition*: optional / *Type*: str /

  Data to be sent.

* ``cr``

  / *Condition*: optional / *Type*: str /

  Determine if it's necessary to add newline character at the end of command.

**Returns:**

         None
      
Method: read_obj
----------------

Wrapper method to get the response from connection.

**Returns:**

         Responded message.
      
Method: wait_4_trace
--------------------

Suspend the control flow until a Trace message is received which matches to a specified regular expression.

**Arguments:**

* ``search_obj``

  / *Condition*: optional / *Type*: str /

  Regular expression all received trace messages are compare to.
  Can be passed either as a string or a regular expression object. Refer to Python documentation for module 're'.

* ``use_fetch_block``

  / *Condition*: optional / *Type*: bool /

  Determine if 'fetch block' feature is used.

* ``end_of_block_pattern``

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

* ``abc``

  / *Type*: re.Match /

  If no trace message matched to the specified regular expression and a timeout occurred.

  If a trace message has matched to the specified regular expression, a match object is returned as the result.                    The complete trace message can be accessed by the 'string' attribute of the match object.                    For access to groups within the regular expression, use the group() method.                    For more information, refer to Python documentation for module 're'.      
Method: wait_4_trace_continuously
---------------------------------

Getting trace log continuously without creating a new trace queue.

**Arguments:**


* ``trace_queue``

  / *Condition*: optional / *Type*: Queue /

  Queue to store the traces.

* ``timeout``

  / *Condition*: optional / *Type*: int /

  Timeout for waiting a matched log.

* ``fct_args``

  / *Condition*: optional / *Type*: Tuple /

  Arguments to be sent to connection.

**Returns:**

* ``None``

  / *Type*: None /

  If no trace message matched to the specified regular expression and a timeout occurred.

* ``match``

  / *Type*: re.Match /

  If a trace message has matched to the specified regular expression, a match object is returned as the result.                    The complete trace message can be accessed by the 'string' attribute of the match object.                    For access to groups within the regular expression, use the group() method.                    For more information, refer to Python documentation for module 're'.      
Method: create_and_activate_trace_queue
---------------------------------------

Create Queue and assign it to _trace_queue object and activate the queue with the search element.

**Arguments:**

* ``search_element``

  / *Condition*: optional / *Type*: str /

  Regular expression all received trace messages are compare to.

  Can be passed either as a string or a regular expression object. Refer to Python documentation for module 're'.#

* ``use_fetch_block``

  / *Condition*: optional / *Type*: bool /

  Determine if 'fetch block' feature is used.

* ``end_of_block_pattern``

  / *Condition*: optional / *Type*: str /

  The end of block pattern.

* ``regex_line_filter_pattern``

  / *Condition*: optional / *Type*: str /

  Regular expression object to filter message line by line.

**Returns:**

* ``trq_handle, trace_queue``

  / *Type*: tuple /

  The handle and search object
      
Method: deactivate_and_delete_trace_queue
-----------------------------------------

Deactivate trace queue and delete.

**Arguments:**

* ``trq_handle``

  / *Condition*: optional / *Type*: int /

  Trace queue handle.

* ``trace_queue``

  / *Condition*: optional / *Type*: Queue /

  Trace queue object.

**Returns:**

         None.
      
Method: activate_trace_queue
----------------------------

Activates a trace message filter specified as a regular expression. All matching trace messages are put in the specified queue object.

**Arguments:**

* ``search_obj``

  / *Condition*: optional / *Type*: str /

  Regular expression all received trace messages are compare to. 
  Can be passed either as a string or a regular expression object. Refer to Python documentation for module 're'.

* ``trace_queue``

  / *Condition*: optional / *Type*: Queue /

  A queue object all trace message which matches the regular expression are put in. 
  The using application must assure, that the queue is emptied or deleted.

* ``use_fetch_block``

  / *Condition*: optional / *Type*: bool /

  Determine if 'fetch block' feature is used.

* ``end_of_block_pattern``

  / *Condition*: optional / *Type*: str /

  The end of block pattern.

* ``line_filter_pattern``

  / *Condition*: optional / *Type*: str /

  Regular expression object to filter message line by line.

**Returns:**

* ``handle_id``

  / *Type*: int /

  Handle to deactivate the message filter.
      
Method: deactivate_trace_queue
------------------------------

Deactivates a trace message filter previously activated by ActivateTraceQ() method.

**Arguments:**

* ``handle``

  / *Condition*: optional / *Type*: int /

  Integer object returned by ActivateTraceQ() method.

**Returns:**

* ``is_success``

  / *Type*: bool /
 .
  False : No trace message filter active with the specified handle (i.e. handle is not in use).

  True :  Trace message filter successfully deleted.
      
Method: check_timeout
---------------------

>> This method will be override in derived class <<

Check if responded message come in cls._RESPOND_TIMEOUT or we will raise a timeout event.

**Arguments:**

* ``timeout``

  / *Condition*: optional / *Type*: int /

  Timeout in seconds.

**Returns:**
         None.
      
Method: pre_msg_check
---------------------

>> This method will be override in derived class <<

Pre-checking message when receiving it from connection.

**Arguments:**

* ``msg``

  / *Condition*: optional / *Type*: str /

  Received message to be checked.

**Returns:**
         None.
      
Method: post_msg_check
----------------------

>> This method will be override in derived class <<

Post-checking message when receiving it from connection.

**Arguments:**

* ``msg``

  / *Condition*: optional / *Type*: str /

  Received message to be checked.

**Returns:**
         None.
      
