#  Copyright 2020-2026 Robert Bosch GmbH
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
import json
import pika
import queue

from MicroserviceBase.adapters.config.rabbitmq_config import RabbitMQConfig
from MicroserviceBase.adapters.transport.rabbitmq_adapter import RabbitMQTransportAdapter


class RabbitmqClientConfig(DictToClass):
   """
Class to store the configuration for SSH connection.
   """
   address = 'localhost'
   port = 5672
   routing_key = ''


class RabbitmqClient(ConnectionBase):
   """
Rabbitmq client connection class.
   """
   _CONNECTION_TYPE = "RabbitmqClient"

   _rabbit_instance = 0

   def __init__(self, _mode, config):
      """
Constructor for RabbitmqClient class.

**Arguments:**

* ``_mode``

  / *Condition*: required / *Type*: str /

  Unused

* ``config``

  / *Condition*: required / *Type*: DictToClass /

  Configurations for rabbitmq Client.
      """
      self.config = RabbitmqClientConfig(**config)
      self.exchange_name = 'services_request'
      self._host = self.config.address
      self._port = self.config.port
      self._routing_key = self.config.routing_key
      self.resp_queue = queue.Queue()
      self._is_connected = False
      self._transport = None
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

   With the transport adapter, rpc_call() handles its own response consumption,
   so this thread simply stays alive until termination is requested.

   **Returns:**

   (*no returns*)
         """
         _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
         BuiltIn().log("%s: low-level receiver thread started." % _mident, constants.LOG_LEVEL_DEBUG)
         while not self._llrecv_thrd_term.is_set():
            time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)

   def connect(self):
      """
Implementation for creating a rabbitmq connection.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      try:
         config = RabbitMQConfig(host=self._host, port=self._port)
         self._transport = RabbitMQTransportAdapter(config)
         self._transport.connect()

         BuiltIn().log(f"connected to Rabbitmq Broker {self._host}:{self._port} (connection type '{self._CONNECTION_TYPE}' with name '{self.conn_name}')",
               constants.LOG_LEVEL_INFO)
         self._is_connected = True

      except Exception as reason:
         BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_ERROR)
         raise BrokenConnError("Not possible to connect. Reason: '%s'" % reason) from None

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
      try:
         _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
         BuiltIn().log("%s: sending: '%s'" % (_mident, msg), constants.LOG_LEVEL_DEBUG)
         request_data = json.loads(msg) if isinstance(msg, str) else msg
         resp = self._transport.rpc_call(
            request_data,
            self.exchange_name,
            self._routing_key,
            timeout=30
         )
         self.resp_queue.put(json.dumps(resp))
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
         response = self.resp_queue.get(block=False)
      except queue.Empty:
         time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)
      return response

   def close(self):
      """
Close rabbitmq connection.

**Returns:**

(*no returns*)
      """
      if self._transport is not None:
         try:
            self._transport.disconnect()
         except Exception:
            pass
         self._transport = None
      self._is_connected = False

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
      BuiltIn().log(f"disconnected from Rabbitmq Broker '{self._host}':'{self._port}' (connection type '{self._CONNECTION_TYPE}' with name '{self.conn_name}')",
               constants.LOG_LEVEL_INFO)


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


class RMQSignal:
   """
RMQSignal class.
   """
   _BROADCAST_EXCHANGE = 'signal_exchange'
   _DIRECT_EXCHANGE = 'direct_signal_exchange'
   _BROADCAST_ROUTING_KEY = 'broadcast'

   def __init__(self, host='localhost', port="5672"):
      """
Constructor for RMQSignal class.

**Arguments:**

* ``host``

  / *Condition*: optional / *Type*: str / *Default*: 'localhost' /

  Host address of the RabbitMQ broker.

* ``port``

  / *Condition*: optional / *Type*: str / *Default*: '5672' /

  Port of the RabbitMQ broker.
      """
      self.host = host
      self._port = int(port)
      self.signal_receiver_name = ''
      self._config = RabbitMQConfig(host=self.host, port=self._port)
      self._transport = RabbitMQTransportAdapter(self._config)
      self._transport.connect()

      channel = self._transport.connection.channel()
      channel.exchange_declare(exchange=RMQSignal._DIRECT_EXCHANGE, exchange_type='direct')
      channel.exchange_declare(exchange=RMQSignal._BROADCAST_EXCHANGE, exchange_type='fanout')
      channel.close()

   def __del__(self):
      """
Destructor for RMQSignal class.
      """
      self.unset_signal_receiver_name()
      if self._transport is not None:
         self._transport.disconnect()
         self._transport = None

   def send_signal(self, signal_name, payload, receiver=None):
      """
Send sinal to other processes.

**Arguments:**

* ``signal_name``

  / *Condition*: required / *Type*: str /

  Signal to be sent.

* ``payload``

  / *Condition*: required / *Type*: str /

  Payloads for signal.

* ``receiver``

  / *Condition*: optional / *Type*: str / *Default*: None /

  Specific the signal receiver to send signal to.

**Returns:**

(*no returns*)
      """
      send_data = {
         signal_name: payload
      }

      if receiver is not None:
         self._transport.publish(RMQSignal._DIRECT_EXCHANGE, receiver, json.dumps(send_data))
      else:
         self._transport.publish(RMQSignal._BROADCAST_EXCHANGE, '', json.dumps(send_data))

   def unset_signal_receiver_name(self):
      """
Unset siganl receiver.

**Returns:**

(*no returns*)
      """
      if self.signal_receiver_name and self._transport and self._transport.connection and not self._transport.connection.is_closed:
         channel = self._transport.connection.channel()
         try:
            channel.queue_delete(self.signal_receiver_name)
         finally:
            if channel.is_open:
               channel.close()
         self.signal_receiver_name = ''

   def set_signal_receiver_name(self, receiver='', force=True):
      """
Set the signal receiver to be received signal.

**Arguments:**

* ``receiver``

  / *Condition*: optional / *Type*: str / *Default*: '' /

  Name a signal receiver to receive signal.

* ``force``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  Force create the signal receiver (delete the exist signal receiver with the same name).


**Returns:**

(*no returns*)
      """
      if force:
         channel = self._transport.connection.channel()
         try:
            channel.queue_delete(receiver)
            channel.queue_declare(queue=receiver, passive=False)
         except Exception as ex:
             print(ex)
         finally:
            if channel.is_open:
               channel.close()
         self.signal_receiver_name = receiver
      else:
         import logging
         logging.getLogger("pika").setLevel(logging.ERROR)
         try:
            # Attempt to declare the queue — uses a separate connection
            # because passive=True will close the channel on 404.
            connection = pika.BlockingConnection(
               pika.ConnectionParameters(**self._config.to_connection_params())
            )
            channel = connection.channel()
            channel.queue_declare(queue=receiver, passive=True)
            raise Exception(f"Signal '{receiver}' receiver already exists.")
         except pika.exceptions.ChannelClosedByBroker as e:
            if e.reply_code == 404:
               ch = self._transport.connection.channel()
               try:
                  ch.queue_declare(queue=receiver, passive=False)
               except Exception:
                  pass
               finally:
                  if ch.is_open:
                     ch.close()

               print(f"Queue '{receiver}' created.")
               self.signal_receiver_name = receiver
            else:
               raise Exception("Unable to create signal receiver. Exception: %s" % (e))


   def consume_channel(self, exchange, queue_name, routing_key, stop_event, signal_name, messages, queue_delete=False):
      """
Consume the message from specific queue.

**Arguments:**

* ``exchange``

  / *Condition*: required / *Type*: str /

  Name of the exchange.

* ``queue_name``

  / *Condition*: required / *Type*: str /

  Name of the queue.

* ``routing_key``

  / *Condition*: required / *Type*: str /

  Routing key string.

* ``stop_event``

  / *Condition*: required / *Type*: Event /

  Event to notify stopping consumming.

* ``signal_name``

  / *Condition*: required / *Type*: str or list /

  Name of the signal to be wait for.

* ``messages``

  / *Condition*: required / *Type*: list or dict /

  Storage for received messages.

* ``queue_delete``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  Determine if we should delete the queue at the end.


**Returns:**

(*no returns*)
      """
      def callback(ch, method, properties, body):
         print(f"Received message from {queue_name}: {body}")
         # Set the event when a message is received
         # Process the received message
         data = json.loads(body.decode())
         ch.basic_ack(delivery_tag=method.delivery_tag)
         if isinstance(signal_name, str):
            if signal_name in data:
               messages.append(data[signal_name])
               stop_event.set()
               ch.stop_consuming()
         elif isinstance(signal_name, list):
            intersection = set(signal_name).intersection(set(data.keys()))
            if intersection:
               try:
                  sig = intersection.pop()
                  messages[sig] = data[sig]
                  if all(messages.values()):
                     stop_event.set()
                     ch.stop_consuming()
               except Exception as ex:
                  print(ex)

      connection = pika.BlockingConnection(
         pika.ConnectionParameters(**self._config.to_connection_params())
      )

      channel = connection.channel()
      if queue_name=='':
         result = channel.queue_declare(queue='', exclusive=True)
         queue_name = result.method.queue

      channel.queue_bind(  exchange=exchange,
                           queue=queue_name,
                           routing_key=routing_key)
      channel.basic_consume(queue=queue_name, on_message_callback=callback)
      # channel.start_consuming()
      while not stop_event.is_set():
        channel.connection.process_data_events()

      if queue_delete:
         channel.queue_delete(queue_name)
      channel.close()
      connection.close()

   def wait_for_signal(self, signal_name, timeout=10):
      """
Wait for specific signal in timeout.

**Arguments:**

* ``signal_name``

  / *Condition*: optional / *Type*: str /

  Name of the signal to wait for.

* ``timeout``

  / *Condition*: optional / *Type*: int / *Default*: 10 /

  Timeout for waitting the signal. Default is 10 seconds.


**Returns:**

  / *Type*: str /

  Payloads of the watting signal if received.
      """
      messages = []
      stop_event = threading.Event()
      thread_broadcast_consume = threading.Thread( target=self.consume_channel,
                                                   args=(   RMQSignal._BROADCAST_EXCHANGE,
                                                            '',
                                                            RMQSignal._BROADCAST_ROUTING_KEY,
                                                            stop_event,
                                                            signal_name,
                                                            messages,
                                                            True),
                                                   daemon=True)
      if self.signal_receiver_name:
         thread_direct_comsume = threading.Thread( target=self.consume_channel,
                                                   args=(   RMQSignal._DIRECT_EXCHANGE,
                                                            self.signal_receiver_name,
                                                            self.signal_receiver_name,
                                                            stop_event,
                                                            signal_name,
                                                            messages),
                                                   daemon=True)

      # Start threads to consume messages concurrently
      thread_broadcast_consume.start()
      if self.signal_receiver_name:
         thread_direct_comsume.start()

      stop_event.wait(timeout=timeout)
      message_received = stop_event.is_set()
      stop_event.set()

      if not message_received:
         raise TimeoutError(f"Timeout waiting for signal '{signal_name}'")
      elif messages:
         return messages[0]

   def wait_for_signals(self, signal_names, timeout=10):
      """
Wait for multiple specific signals in timeout.

**Arguments:**

* ``signal_name``

  / *Condition*: optional / *Type*: list /

  List of the signals to wait for.

* ``timeout``

  / *Condition*: optional / *Type*: int / *Default*: 10 /

  Timeout for waitting the signal. Default is 10 seconds.


**Returns:**

  / *Type*: str /

  List of payloads of the watting signals if received.
      """
      # queues = [f"{name}_queue" for name in signal_names]
      messages = {name: None for name in signal_names}

      stop_event = threading.Event()
      thread_broadcast_consume = threading.Thread( target=self.consume_channel,
                                                   args=(   RMQSignal._BROADCAST_EXCHANGE,
                                                            '',
                                                            RMQSignal._BROADCAST_ROUTING_KEY,
                                                            stop_event,
                                                            signal_names,
                                                            messages,
                                                            True),
                                                   daemon=True)
      if self.signal_receiver_name:
         thread_direct_comsume = threading.Thread( target=self.consume_channel,
                                                   args=(   RMQSignal._DIRECT_EXCHANGE,
                                                            self.signal_receiver_name,
                                                            self.signal_receiver_name,
                                                            stop_event,
                                                            signal_names,
                                                            messages),
                                                   daemon=True)

      # Start threads to consume messages concurrently
      thread_broadcast_consume.start()
      if self.signal_receiver_name:
         thread_direct_comsume.start()

      stop_event.wait(timeout=timeout)
      message_received = stop_event.is_set()
      stop_event.set()

      if not message_received:
         raise TimeoutError(f"Timeout waiting for signal '{signal_names}'")
      elif messages:
         return [messages[name] for name in signal_names]
