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
# File: grpc_client.py
#
# Initially created by Nguyen Huynh Tri Cuong (MS/EMC51) / May 2026.
#
# Description:
#   QConnectBase connection type for invoking gRPC services.  Mirrors
#   the request/response shape of `rabbitmq_client.py` but uses
#   MicroserviceBase's GrpcReflectClient (gRPC server reflection) with
#   an automatic fallback to LocalProtoClient when reflection is not
#   available on the server side.
#
#   Two ways to address the target:
#     1. Direct host:port (config field `target`)
#     2. Consul service name (config fields `service_name` + `consul_addr`)
#
#   The send command is a JSON object describing the call:
#     {"method": "Greet", "args": {"name": "World"}}
#   When `full_service_name` is set in the config, just the args dict
#   may be sent without the wrapper.
#
#   Unlike text-stream connections (TCP, Serial, SSH), gRPC returns a
#   structured object.  `wait_4_trace` is overridden to ignore the
#   regex `search_obj` argument (forced to '.*') and to return the
#   response as a Python dict, which `ConnectionManager.verify` then
#   surfaces unchanged to the test author.
#
# History:
#
# 10.05.2026 / V 1.0.0 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from __future__ import with_statement
from robot.libraries.BuiltIn import BuiltIn
from QConnectBase.connection_base import ConnectionBase, BrokenConnError
from QConnectBase.utils import DictToClass
from inspect import currentframe
import QConnectBase.constants as constants
import json
import queue
import re
import threading
import time

# MicroserviceBase carries the actual gRPC plumbing — reflection client,
# Consul resolver, and the optional .proto-fallback client.  These imports
# only succeed when MicroserviceBase is installed alongside QConnectBase;
# the connection_manager auto-loader catches ImportError silently, so this
# module is a no-op on environments that don't have MicroserviceBase
# (rather than breaking the manager's discovery pass).
from MicroserviceBase.adapters.grpc_bridge.reflect_client import (
   GrpcReflectClient,
   GrpcReflectError,
)
try:
   from MicroserviceBase.adapters.grpc_bridge.local_proto_client import (
      LocalProtoClient,
   )
   _HAS_LOCAL_PROTO = True
except ImportError:
   LocalProtoClient = None
   _HAS_LOCAL_PROTO = False


class GrpcClientConfig(DictToClass):
   """
Class to store the configuration for gRPC client connection.

Either ``target`` (direct host:port) or both ``service_name`` and
``consul_addr`` must be provided.  When both are given, ``target`` wins.
   """
   # Direct mode
   target = ""
   # Consul-resolved mode
   service_name = ""
   consul_addr = "http://localhost:8500"
   # Default servicer used when the send command doesn't include one
   full_service_name = ""
   # Optional .proto directory for the LocalProtoClient fallback (used
   # when the server doesn't ship grpc++_reflection — e.g. C++ services
   # built against vcpkg's grpc port).
   proto_dir = ""
   # Per-call timeout in seconds
   timeout_seconds = 30.0


class GrpcClient(ConnectionBase):
   """
gRPC client connection class.

Robot Framework usage::

    *** Settings ***
    Library    QConnectBase.connection_manager.ConnectionManager

    *** Test Cases ***
    Greet
        Connect    grpc_hello    conn_conf={'conn_type': 'GrpcClient',
        ...                                  'service_name': 'hello',
        ...                                  'consul_addr': 'http://localhost:8500',
        ...                                  'full_service_name': 'hello.v1.HelloService'}
        ${res}=  Verify    grpc_hello
        ...                send_cmd={"method": "Greet", "args": {"name": "World"}}
        Should Be Equal    ${res}[message]    Hello, World!
        [Teardown]   Disconnect    grpc_hello

The ``send_cmd`` is a JSON document describing the invocation.  Two
shapes are accepted:

1. ``{"method": "<MethodName>", "args": {...}}`` — uses the
   ``full_service_name`` from the connection config.
2. ``{"service": "<pkg.Service>", "method": "<MethodName>", "args": {...}}``
   — overrides the configured service per call (useful for sending
   into a multi-service binary).

The response is captured as a Python dict (the gRPC response message
converted via ``google.protobuf.json_format.MessageToDict``) and
returned to the test author by the standard ``Verify`` keyword.  The
``search_pattern`` argument of ``Verify`` is ignored for this
connection type (gRPC returns structured data, not a text stream); use
Robot's built-in ``Should Be Equal``, ``Dictionary Should Contain``,
``Get From Dictionary``, etc. against the returned dict instead.
   """
   _CONNECTION_TYPE = "GrpcClient"

   # `verify` keyword passes everything not in its named args to the
   # connection via **kwargs.  Empty list = no extra params accepted;
   # the manager will reject any with a clear error.  Add to this if we
   # ever need per-call timeout overrides etc.
   ACCEPT_VERIFY_PARAMS = []

   _grpc_instance = 0

   def __init__(self, _mode, config):
      """
Constructor for GrpcClient class.

**Arguments:**

* ``_mode``

  / *Condition*: required / *Type*: str /

  Unused; kept for QConnectBase contract.

* ``config``

  / *Condition*: required / *Type*: dict /

  Connection configuration.  See :class:`GrpcClientConfig` for the
  full set of fields.
      """
      self.config = GrpcClientConfig(**config)
      self._target = self.config.target
      self._service_name = self.config.service_name
      self._consul_addr = self.config.consul_addr
      self._full_service_name = self.config.full_service_name
      self._proto_dir = self.config.proto_dir
      self._timeout = float(self.config.timeout_seconds)

      # Validate that we have at least one way to address the target.
      if not self._target and not self._service_name:
         raise Exception(
            "GrpcClient: either 'target' (direct host:port) or "
            "'service_name' (for Consul resolution) must be provided in "
            "conn_conf."
         )

      self.resp_queue = queue.Queue()
      self._is_connected = False
      self._client = None             # GrpcReflectClient
      self._fallback_client = None    # LocalProtoClient (lazy)
      self._send_lock = threading.Lock()

      if 'conn_name' in config:
         self.conn_name = config['conn_name']

      # Configure and initialise the receiver thread that pulls
      # responses off the queue and feeds them through the base class's
      # regex/wait_4_trace machinery.
      GrpcClient._grpc_instance += 1
      self._init_thread_receiver(GrpcClient._grpc_instance)

      # Low-level receiver thread — gRPC's call/response is synchronous
      # so this thread has nothing to poll, but the base class expects
      # the lifecycle hooks (start + terminate Event), so we run a
      # minimal sleep loop to keep the contract.
      self._llrecv_thrd_obj = None
      self._llrecv_thrd_term = threading.Event()
      self._init_thrd_llrecv(GrpcClient._grpc_instance)

      # Required by ConnectionBase.wait_4_trace
      self._broken_conn = threading.Event()
      self._recv_thrd_start = threading.Event()

   # ------------------------------------------------------------------
   # ConnectionBase contract
   # ------------------------------------------------------------------

   def connect(self):
      """
Open the gRPC channel.  Resolves via Consul if ``target`` is empty.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)

      try:
         target = self._target
         if not target:
            target = self._resolve_via_consul()

         self._client = GrpcReflectClient(target, timeout=self._timeout)
         self._is_connected = True
         BuiltIn().log(
            "connected to gRPC target %s (connection type '%s' with name '%s')"
            % (target, self._CONNECTION_TYPE, getattr(self, 'conn_name', '?')),
            constants.LOG_LEVEL_INFO,
         )
      except Exception as reason:
         BuiltIn().log("%s: %s" % (_mident, reason), constants.LOG_LEVEL_ERROR)
         raise BrokenConnError(
            "Not possible to connect to gRPC target. Reason: '%s'" % reason
         ) from None

   def _send(self, msg, _cr=False):
      """
Invoke an RPC.

**Arguments:**

* ``msg``

  / *Condition*: required / *Type*: str or dict /

  JSON string (or dict) describing the call.  See class docstring for
  the accepted shapes.

* ``_cr``

  / *Condition*: required / *Type*: bool /

  Unused.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log("%s: sending: '%s'" % (_mident, msg), constants.LOG_LEVEL_DEBUG)

      try:
         req = self._parse_send_command(msg)
         service = req['service']
         method = req['method']
         args = req.get('args', {})
         json_payload = json.dumps(args) if not isinstance(args, str) else args

         with self._send_lock:
            resp = self._invoke_unary(service, method, json_payload)

         self.resp_queue.put(json.dumps(resp))
      except Exception as ex:
         # Push the error onto the queue so wait_4_trace surfaces it
         # immediately rather than timing out — easier to debug.
         err_payload = {
            "_grpc_error": True,
            "type": type(ex).__name__,
            "message": str(ex),
         }
         self.resp_queue.put(json.dumps(err_payload))
         BuiltIn().log(
            "%s: gRPC call failed: %s" % (_mident, ex),
            constants.LOG_LEVEL_WARNING,
         )

   def _read(self):
      """
Read data from gRPC connection.

**Returns:**

  / *Type*: str /

  Data from gRPC connection.
      """
      try:
         return self.resp_queue.get(block=False)
      except queue.Empty:
         time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)
         return None

   def _thrd_llrecv_from_connection_interface(self):
      """
Implementation the thread for getting data from gRPC connection.

gRPC unary calls are synchronous, so this thread has nothing to poll
on the wire — it just stays alive until ``quit()`` is called.

**Returns:**

(*no returns*)
      """
      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log(
         "%s: low-level receiver thread started." % _mident,
         constants.LOG_LEVEL_DEBUG,
      )
      while not self._llrecv_thrd_term.is_set():
         time.sleep(ConnectionBase.RECV_MSGS_POLLING_INTERVAL)

   def disconnect(self, device=None):
      """
Disconnect the gRPC channel.

**Arguments:**

* ``device``

  / *Condition*: optional / *Type*: str /

  Unused; kept for QConnectBase contract.

**Returns:**

(*no returns*)
      """
      self.close()

   def close(self):
      """
Close gRPC connection.

**Returns:**

(*no returns*)
      """
      if self._client is not None:
         try:
            self._client.close()
         except Exception:
            pass
         self._client = None
      if self._fallback_client is not None:
         try:
            self._fallback_client.close()
         except Exception:
            pass
         self._fallback_client = None
      self._is_connected = False

   def quit(self, is_disconnect_all=True):
      """
Quit and stop receiver thread.

**Arguments:**

* ``is_disconnect_all``

  / *Condition*: optional / *Type*: bool /

  Forwarded to the base class; kept for the contract.

**Returns:**

(*no returns*)
      """
      # Execute parent's Quit() first
      super(GrpcClient, self).quit(is_disconnect_all)

      # Stop the low-level receiver thread
      if self._llrecv_thrd_obj and self._llrecv_thrd_obj.is_alive():
         self._llrecv_thrd_term.set()
      self._llrecv_thrd_obj = None

      self.close()
      BuiltIn().log(
         "disconnected from gRPC target (connection type '%s' with name '%s')"
         % (self._CONNECTION_TYPE, getattr(self, 'conn_name', '?')),
         constants.LOG_LEVEL_INFO,
      )

   # ------------------------------------------------------------------
   # wait_4_trace override
   # ------------------------------------------------------------------

   def wait_4_trace(self, search_obj=None, timeout=0,
                    use_fetch_block=False, end_of_block_pattern=None,
                    filter_pattern=".*", **fct_args):
      """
gRPC override of :meth:`ConnectionBase.wait_4_trace`.

Unlike text-stream connections (TCP, Serial, SSH), gRPC responses are
**structured objects**, not lines of text.  Searching them line-by-line
with a regex is meaningless.  This override therefore:

  - **Ignores** ``search_obj`` (forced internally to ``'.*'``) so the
    receiver always matches.
  - **Ignores** ``use_fetch_block`` / ``end_of_block_pattern`` /
    ``filter_pattern`` for the same reason.
  - Sends the request via ``send_obj`` (which calls ``_send`` →
    ``GrpcReflectClient.call_unary`` and queues the response).
  - Waits up to ``timeout`` seconds (or the connection's configured
    ``timeout_seconds`` when ``timeout`` is 0) for one response.
  - **Returns the response as a Python dict**, which
    ``ConnectionManager.verify`` then surfaces to the test author
    unchanged.  The test asserts content with Robot Framework's
    built-ins (``Should Be Equal``, ``Dictionary Should Contain``,
    ``Get From Dictionary``, etc.) instead of regex on a text stream.

**Arguments:**

* ``search_obj``

  / *Condition*: optional / *Type*: str / *Default*: None /

  Ignored.  Kept in the signature so the standard ``Verify`` keyword
  call shape stays compatible.

* ``timeout``

  / *Condition*: optional / *Type*: float / *Default*: 0 /

  Maximum time to wait for the gRPC response, in seconds.  0 means
  fall back to the connection's configured ``timeout_seconds``.

* ``use_fetch_block``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  Ignored.

* ``end_of_block_pattern``

  / *Condition*: optional / *Type*: str / *Default*: None /

  Ignored.

* ``filter_pattern``

  / *Condition*: optional / *Type*: str / *Default*: '.*' /

  Ignored.

* ``fct_args``

  / *Condition*: optional / *Type*: dict /

  Forwarded to ``send_obj`` (typically contains ``send_cmd``).

**Returns:**

* ``response``

  / *Type*: dict or None /

  The response message converted to a dict.  ``None`` if no response
  arrived within ``timeout``.  When the gRPC call itself failed, the
  dict has ``{"_grpc_error": True, "type": ..., "message": ...}``.
      """
      if self._broken_conn.is_set():
         raise Exception(constants.String.CONNECTION_BROKEN)

      _mident = '%s.%s()' % (self.__class__.__name__, currentframe().f_code.co_name)
      BuiltIn().log('Execute %s' % _mident, constants.LOG_LEVEL_DEBUG)

      # Force search/filter regex to ".*" — the receiver thread feeds the
      # JSON-serialised response into a re.search() against this; we want
      # it to always match so we get the response straight back.
      search_regex = re.compile('.*', re.M | re.S | re.U)
      regex_obj_filter = re.compile('.*')
      trq_handle, trace_queue = self.create_and_activate_trace_queue(
         search_regex,
         use_fetch_block=False,
         end_of_block_pattern=None,
         regex_line_filter_pattern=regex_obj_filter,
      )

      try:
         self.send_obj(**fct_args)
      except BrokenConnError:
         self.deactivate_and_delete_trace_queue(trq_handle, trace_queue)
         raise Exception(constants.String.CONNECTION_BROKEN) from None
      except Exception as err_msg:
         BuiltIn().log(
            '%s: An Exception occurred executing function object: %s'
            % (_mident, repr(self.send_obj)), 'ERROR'
         )
         BuiltIn().log('Function Arguments: %s' % repr(fct_args), 'ERROR')
         BuiltIn().log('Error Message: %s' % repr(err_msg), 'ERROR')

      effective_timeout = timeout if timeout else self._timeout
      match = None
      try:
         (_, match) = trace_queue.get(True, effective_timeout)
      except queue.Empty:
         match = None
      finally:
         self.deactivate_and_delete_trace_queue(trq_handle, trace_queue)

      BuiltIn().log('Completed %s' % _mident, constants.LOG_LEVEL_DEBUG)

      if match is None:
         return None

      # `match` is a re.Match against ".*" on the JSON the receiver
      # pushed.  Re-parse the original string back into a dict so the
      # caller (typically ConnectionManager.verify) gets structured data.
      payload = match.string if hasattr(match, 'string') else str(match)
      try:
         return json.loads(payload)
      except (ValueError, TypeError):
         # Fall back to the raw string if it isn't valid JSON for some
         # reason.  Verify will wrap it in a list — uncommon path.
         return payload

   # ------------------------------------------------------------------
   # Helpers
   # ------------------------------------------------------------------

   def _parse_send_command(self, msg):
      """
Parse the send command into ``{service, method, args}``.

Accepts either:

  - ``{"method": "<m>", "args": {...}}`` (uses configured
    ``full_service_name``)
  - ``{"service": "<svc>", "method": "<m>", "args": {...}}``

**Arguments:**

* ``msg``

  / *Condition*: required / *Type*: str or dict or bytes /

  Send command as JSON string (or already-parsed dict).

**Returns:**

* ``parsed``

  / *Type*: dict /

  Dict with keys ``service``, ``method``, ``args``.
      """
      if isinstance(msg, dict):
         req = msg
      elif isinstance(msg, (bytes, bytearray)):
         req = json.loads(msg.decode("utf-8"))
      else:
         req = json.loads(str(msg))

      if 'method' not in req or not req['method']:
         raise ValueError(
            "GrpcClient send command requires 'method' field, got: %r" % msg
         )

      service = req.get('service') or self._full_service_name
      if not service:
         raise ValueError(
            "GrpcClient: no service specified in send command and no "
            "'full_service_name' in conn_conf — cannot route the call."
         )

      return {'service': service, 'method': req['method'],
              'args': req.get('args', {})}

   def _invoke_unary(self, service, method, json_payload):
      """
Invoke a unary RPC.  Reflection client first; fall back to
LocalProtoClient when the server returns ``UNIMPLEMENTED`` for the
reflection RPC (typical for C++ services built without
``grpc++_reflection``).

**Arguments:**

* ``service``

  / *Condition*: required / *Type*: str /

  Fully-qualified service name (e.g. ``"hello.v1.HelloService"``).

* ``method``

  / *Condition*: required / *Type*: str /

  Method name within the service (e.g. ``"Greet"``).

* ``json_payload``

  / *Condition*: required / *Type*: str /

  JSON-encoded request message.

**Returns:**

* ``response``

  / *Type*: dict /

  Response message converted to a dict.
      """
      try:
         return self._client.call_unary(service, method, json_payload)
      except GrpcReflectError as ex:
         if not ex.is_unimplemented:
            raise
         if not _HAS_LOCAL_PROTO or not self._proto_dir:
            raise GrpcReflectError(
               "Reflection unsupported by server '%s' and no "
               "LocalProtoClient fallback available "
               "(set 'proto_dir' in conn_conf to enable)." % service
            ) from None

         if self._fallback_client is None:
            target = self._target or self._resolve_via_consul()
            self._fallback_client = LocalProtoClient(
               target=target, proto_dir=self._proto_dir,
               timeout=self._timeout,
            )
         return self._fallback_client.call_unary(service, method, json_payload)

   def _resolve_via_consul(self):
      """
Resolve the configured ``service_name`` to a ``host:port`` via Consul.

Picks the first healthy instance.  Lazy import of
``MicroserviceBase.runtime.consul`` so the direct-mode case never
loads it.

**Returns:**

* ``endpoint``

  / *Type*: str /

  The ``host:port`` string of a healthy instance.
      """
      try:
         # Lazy import — only needed in Consul-resolved mode.
         from MicroserviceBase.runtime.consul import resolve_via_consul
      except ImportError:
         raise Exception(
            "Consul resolution requested but MicroserviceBase.runtime.consul "
            "is not importable.  Either install MicroserviceBase or pass "
            "'target' (host:port) directly in conn_conf."
         ) from None

      endpoint = resolve_via_consul(self._consul_addr, self._service_name)
      if not endpoint:
         raise Exception(
            "Consul lookup failed for service '%s' at %s — no healthy "
            "instances." % (self._service_name, self._consul_addr)
         )
      return endpoint
