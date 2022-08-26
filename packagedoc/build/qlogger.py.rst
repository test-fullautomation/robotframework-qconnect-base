Class: ColorFormatter
=====================

.. code::python

   QConnectBase.qlogger

Custom formatter class for setting log color.
   
Method: format
--------------

Set the color format for the log.

**Arguments:**

* ``record``

  / *Condition*: optional / *Type*: str /

  Log record.

**Returns:**
         Log with color formatter.
      
Class: QFileHandler
===================

.. code::python

   QConnectBase.qlogger

Handler class for user defined file in config.
   
Method: get_log_path
--------------------

Get the log file path for this handler.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**
         Log file path.
      
Method: get_config_supported
----------------------------

Check if the connection config is supported by this handler.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

         True if the config is supported.

         False if the config is not supported.
      
Class: QDefaultFileHandler
==========================

.. code::python

   QConnectBase.qlogger

Handler class for default log file path.
   
Method: get_log_path
--------------------

Get the log file path for this handler.

**Arguments:**

* ``logger_name``

  / *Condition*: required / *Type*: str /

  Name of the logger.

**Returns:**
         Log file path.
      
Method: get_config_supported
----------------------------

Check if the connection config is supported by this handler.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

         True if the config is supported.

         False if the config is not supported.
      
Class: QConsoleHandler
======================

.. code::python

   QConnectBase.qlogger

Handler class for console log.
   
Method: get_config_supported
----------------------------

Check if the connection config is supported by this handler.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

         True if the config is supported.

         False if the config is not supported.
      
Class: QLogger
==============

.. code::python

   QConnectBase.qlogger

Logger class for QConnect Libraries.
   
Method: get_logger
------------------

Get the logger object.

**Arguments:**

* ``logger_name``

  / *Condition*: required / *Type*: str /

  Name of the logger.

**Returns:**

* ``logger``

  / *Type*: Logger /

  Logger object.         .
      
Method: set_handler
-------------------

Set handler for logger.

**Arguments:**

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Connection configurations.

**Returns:**

         None if no handler is set.

         Handler object.
      
