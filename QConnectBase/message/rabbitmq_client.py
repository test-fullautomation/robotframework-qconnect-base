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
# *******************************************************************************
#
# File: rabitmq_client.py
#
# Initially created by Nguyen Huynh Tri Cuong (MS/EMC51) / Nov 2023.
#
# Description:
#   Provide the class for handling Rabitmq connection.
#
# History:
#
# 20.11.2023 / V 1.0.0 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from __future__ import with_statement
from robot.libraries.BuiltIn import BuiltIn
from QConnectBase.connection_base import ConnectionBase, BrokenConnError
from QConnectBase.utils import DictToClass
from inspect import currentframe
import QConnectBase.constants as constants
import time
import threading
import uuid
import json
import pika
import queue


class RabbitmqClientConfig(DictToClass):
   """
Class to store the configuration for SSH connection.
   """
   address = 'localhost'
   port = 5672
   routing_key = ''


class RabbitmqClient(ConnectionBase):
   """
SSH client connection class.
   """
   _CONNECTION_TYPE = "RabbitmqClient"

   _rabbit_instance = 0

   def __init__(self, _mode, config):
      """
Constructor for SSHClient class.

**Arguments:**

* ``_mode``

  / *Condition*: required / *Type*: str /

  Unused

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Configurations for rabbitmq Client.
      """
      self.config = RabbitmqClientConfig(**config)
      self.connection = None
      self.channel = None
      self.exchange_name = 'services_request'
      self.queue_name = "RabbitmqClient" + str(uuid.uuid4())
      self._host = self.config.address
      self._port = self.config.port
      self._routing_key = self.config.routing_key
      self.respQueue = queue.Queue()
      self._is_connected = False
      self.callback_queue = None
      # configure and initialize the low-level receiver thread
      RabbitmqClient._rabbit_instance += 1
      self._init_thread_receiver(RabbitmqClient._rabbit_instance)
      self._llrecv_thrd_obj = None
      self._llrecv_thrd_term = threading.Event()
      self._llrecv_thrd_stopTransfer = threading.Event()
      self._init_thrd_llrecv(RabbitmqClient._rabbit_instance)

   def _thrd_llrecv_from_connection_interface(self):
         """
   Implementation the thread for getting data from rabbitmq connection.

   **Returns:**

   (*no returns*)
         """
         _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
         BuiltIn().log("%s: low-level receiver thread started." % _mident, constants.LOG_LEVEL_INFO)
         while self.callback_queue is None and not self._llrecv_thrd_term.isSet():
            time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)
         self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)
         self.channel.start_consuming()

   def on_response(self, ch, method, properties, body):
      # program_information = json.loads(body)
      # print(program_information)
      if isinstance(body, bytes):
            body = body.decode('utf-8')
      self.respQueue.put(body)

   def connect(self):
      """
Implementation for creating a rabbitmq connection.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      try:
         self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._host, port=self._port))
         self.channel = self.connection.channel()
         queue = self.channel.queue_declare(queue=self.queue_name, durable=False)
         self.callback_queue = queue.method.queue

         # self.channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

         # self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)


         BuiltIn().log("%s: successfully established connection to Rabitmq Broker." % _mident, constants.LOG_LEVEL_INFO)
         self._is_connected = True

      except Exception as reason:
         BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_ERROR)
         raise BrokenConnError("Not possible to connect. Reason: '%s'" % reason)

   def _send(self, msg, _cr):
      """
Send message to rabbitmq connection.

**Arguments:**

* ``msg``

  / *Condition*: required / *Type*: str /

  Message to be sent.

* ``_cr``

  / *Condition*: required / *Type*: str /

  Unused.

**Returns:**

(*no returns*)
      """
      # noinspection PyBroadException
      try:
         _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
         BuiltIn().log("%s: sending: '%s'" % (_mident, msg), constants.LOG_LEVEL_DEBUG)
         connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._host, port=self._port))
         channel = connection.channel()
         channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self._routing_key,
            properties=pika.BasicProperties(
               correlation_id=str(uuid.uuid4()),
               reply_to=self.callback_queue
            ),
            body=msg
         )
         connection.close()
      except Exception as _reason:
         self._is_connected = False

   def _read(self):
      """
Read data from rabbitmq connection.

**Returns:**

  / *Type*: str /

  Data from rabbitmq connection.
      """
      response = None
      try:
         response = self.respQueue.get(block=False)
      except queue.Empty:
         time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)
      return response

   def close(self):
      """
Close rabbitmq connection.

**Returns:**

(*no returns*)
      """
      if self.channel is not None:
         self.channel.stop_consuming()
         if self.callback_queue is not None:
            self.channel.queue_delete(queue=self.callback_queue)
         self.channel.close()

      # Execute parents close()
      # super(RabbitmqClient, self).close()

   def quit(self):
      """
Quit and stop receiver thread.

**Returns:**

(*no returns*)
      """
      # Execute parents Quit() first
      super(RabbitmqClient, self).quit()

      # stop the low-level receiver thread
      if self._llrecv_thrd_obj and self._llrecv_thrd_obj.is_alive():
         self._llrecv_thrd_term.set()

      self._llrecv_thrd_obj = None
      self.close()


if __name__ == "__main__":
   _DEFAULT_CONFIG = {
      'address': 'localhost',
      'port': 5672,
      'routing_key': 'ServiceClewareKey'
   }
   # a = rabbitmqConfig(**_DEFAULT_CONFIG)
   # print(a)
   rabbitclient = RabbitmqClient(None, _DEFAULT_CONFIG)
   rabbitclient.connect()
   jsonData = {
      'method': 'svc_api_get_all_devices_state',
      'args': None
   }
   rabbitclient.send_obj(json.dumps(jsonData))
   while True:
      time.sleep(10)

