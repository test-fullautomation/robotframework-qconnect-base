Class: Singleton
================

.. code::python

   QConnectBase.utils

Class to implement Singleton Design Pattern. This class is used to derive the TTFisClientReal as only a single
instance of this class is allowed.

Disabled pyLint Messages:
R0903:  Too few public methods (%s/%s)
         Used when class has too few public methods, so be sure it's really worth it.

         This base class implements the Singleton Design Pattern required for the TTFisClientReal.
         Adding further methods does not make sense.
Class: DictToClass
==================

.. code::python

   QConnectBase.utils

Class for converting dictionary to class object.
Method: validate
----------------

Class: Utils
============

.. code::python

   QConnectBase.utils

Class to implement utilities for supporting development.
Method: get_all_descendant_classes
----------------------------------

Get all descendant classes of a class

**Arguments:**
         cls: Input class for finding descendants.

**Returns:**
         Array of descendant classes.
      
Method: get_all_sub_classes
---------------------------

Get all children classes of a class

**Arguments:**

* ``cls``

  / *Condition*: required / *Type*: class /

  Input class for finding children.

**Returns:**
         Array of children classes.
      
Method: is_valid_host
---------------------

Method: execute_command
-----------------------

Method: kill_process
--------------------

Method: caller_name
-------------------

Get a name of a caller in the format module.class.method

**Arguments:**

* ``skip``

  / *Condition*: required / *Type*: int /

  Specifies how many levels of stack to skip while getting caller
         name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

**Returns:**
         An empty string is returned if skipped levels exceed stack height
      
Method: load_library
--------------------

Load native library depend on the calling convention.

**Arguments:**
         path: library path.
         is_stdcall: determine if the library's calling convention is stdcall or cdecl.

**Returns:**
         Loaded library object.
      
Method: is_ascii_or_unicode
---------------------------

Check if the string is ascii or unicode

**Arguments:**
         str_check: string for checking
         codecs: encoding type list

**Returns:**
         True : if checked string is ascii or unicode
         False : if checked string is not ascii or unicode
      
Class: Job
==========

.. code::python

   QConnectBase.utils

Method: stop
------------

Method: run
-----------

Class: ResultType
=================

.. code::python

   QConnectBase.utils

Result Types.
Class: ResponseMessage
======================

.. code::python

   QConnectBase.utils

Response message class
   
Method: get_json
----------------

Convert response message to json

**Returns:**
         Response message in json format
      
Method: get_data
----------------

Get string data result

**Returns:**
         String result
      
Method: create_from_string
--------------------------

