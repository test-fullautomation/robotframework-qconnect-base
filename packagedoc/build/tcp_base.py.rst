Class: TCPConfig
================

.. code::python

   QConnectBase.tcp.tcp_base

Class to store configurations for TCP connection.
   
Class: TCPBase
==============

.. code::python

   QConnectBase.tcp.tcp_base

Base class for a tcp connection.
   
Method: close
-------------

      Close connection.

**Returns:**
         None.
      
Method: quit
------------

Quit connection.

**Arguments:**
         is_disconnect_all: Determine if it's necessary for disconnect all connection.

**Returns:**
         None.
      
Method: connect
---------------

>> Should be override in derived class.

Establish the connection.

**Returns:**
         None.
      
Method: disconnect
------------------

>> Should be override in derived class.

Disconnect the connection.

**Returns:**
         None.
      
Class: TCPBaseServer
====================

.. code::python

   QConnectBase.tcp.tcp_base

Base class for TCP server.
   
Method: accept_connection
-------------------------

Wrapper method for handling accept action of TCP Server.

**Returns:**
         None.
      
Method: connect
---------------

Method: disconnect
------------------

Class: TCPBaseClient
====================

.. code::python

   QConnectBase.tcp.tcp_base

Base class for TCP client.
   
Method: connect
---------------

Method: disconnect
------------------

