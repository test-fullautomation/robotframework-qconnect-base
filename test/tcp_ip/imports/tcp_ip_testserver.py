#  Copyright 2020-2025 Robert Bosch GmbH
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
#
# --------------------------------------------------------------------------------------------------------------
#
# TCP/IP test server for component 'QConnectBase'
#
# XC-HWP/ESW3-Queckenstedt
#
VERSION = "v. 0.5.0 / 23.01.2025"
#
# --------------------------------------------------------------------------------------------------------------

import sys
import os
import psutil
import socket
import threading

from rf_log import rf_log       # interface to Robot Framework logging
from threadlog import threadlog # thread specific logging in separate files (independent from RF infrastructure)

from PythonExtensionsCollection.String.CString import CString

DICT_ANSWERS = {}
# >> used later do define specific answers deviating from standard (used e.g. for badcase tests)
# DICT_ANSWERS['VERIFY PING 1'] = "VERIFY PING 1 ACK"
# DICT_ANSWERS['VERIFY PING 2'] = "VERIFY PING 2 ACK"
# DICT_ANSWERS[''] = ""

CHAR_END_OF_MESSAGE = "*" # TODO: command line parameter

STOP_EVENT = threading.Event()

# --------------------------------------------------------------------------------------------------------------

def handle_client(client_socket, client_address):
    msg = f"Client connected: {client_address}"
    rf_log.info(msg)
    tcp_ip_testserver_log.tlog("handle_client", msg)
    try:
        end_of_communication = False
        while True: # next incoming message
            data_received = ""
            while True: # next byte of current message
                # data received from client
                byte_received = client_socket.recv(1).decode("utf-8")
                if not byte_received:
                    # possibly caused by a broken connection (empty byte b""?), or end of message?
                    msg = f"'not byte_received'"
                    tcp_ip_testserver_log.tlog("handle_client", msg)
                    end_of_communication = True
                    break
                    # continue
                data_received = f"{data_received}{byte_received}"
                if data_received == "":
                    msg = f"empty 'data_received'"
                    tcp_ip_testserver_log.tlog("handle_client", msg)
                    end_of_communication = True
                    break
                    # continue
                if ( (data_received[-1] == "\n") or (data_received[-1] == "\r") ):
                    # received standard 'end of message' character
                    break # continue with computing the current message (before getting bytes of next message)
                if CHAR_END_OF_MESSAGE is not None:
                    if data_received[-1] == CHAR_END_OF_MESSAGE:
                        # received specific 'end of message' character
                        break # continue with computing the current message (before getting bytes of next message)
            # eof while True: # next byte of current message

            if end_of_communication is True:
                msg = f"end of communication with this client"
                tcp_ip_testserver_log.tlog("handle_client", msg)
                break # break outer loop => end of communication with this client

            data_received = data_received.strip() # remove trailing and leading blanks and line breaks
            if data_received == "":
                continue # continue with waiting for next message

            msg = f"[{client_address}] (REC) '{data_received}'"
            rf_log.info(msg)
            tcp_ip_testserver_log.tlog("handle_client", msg)

            # send answer to client
            if data_received in DICT_ANSWERS:
                response = DICT_ANSWERS[data_received] # specific answer
            elif data_received == "GET_SERVER_PID":
                current_pid = str(os.getpid())
                response = f"PID={current_pid}"
            else:
                response = f"{data_received} ACK" # common answer
            msg = f"[{client_address}] (SEND) '{response}'"
            rf_log.info(msg)
            tcp_ip_testserver_log.tlog("handle_client", msg)
            response = f"{response}\n"
            client_socket.send(response.encode('utf-8'))

            # special comands
            if data_received.startswith("CLOSE_CONNECTION"):
                break
            elif data_received.startswith("QUIT_TESTSERVER"):
                STOP_EVENT.set()
                break
            # >> currently not used
            # elif data_received.startswith("SET_TEST_NAME="):
                # current_test_name = data_received[len("SET_TEST_NAME="):]
                # current_test_name = current_test_name.replace(" ", "_")
                # tcp_ip_testserver_log.tlog("handle_client", current_test_name)

        # eof while True: # next incoming message
    # eof try:

    except ConnectionResetError:
        msg = f"TCP/IP testserver detected ConnectionResetError ({client_address})"
        rf_log.info(msg)
        tcp_ip_testserver_log.tlog("handle_client", msg)

    except ConnectionAbortedError:
        msg = f"TCP/IP testserver detected ConnectionAbortedError ({client_address})"
        rf_log.info(msg)
        tcp_ip_testserver_log.tlog("handle_client", msg)

    finally:
        client_socket.close()
        msg = f"TCP/IP testserver closed client connection: {client_address}"
        rf_log.info(msg)
        tcp_ip_testserver_log.tlog("handle_client", msg)

# eof def handle_client(client_socket, client_address):

# --------------------------------------------------------------------------------------------------------------

def start_server(host="localhost", port=4000): # TODO: host/port: command line parameter
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
    except Exception as ex:
        msg = f"Exception: Socket already in use: {host}:{port}\n{ex}"
        rf_log.error(msg)
        tcp_ip_testserver_log.tlog("start_server", msg)
        server_socket.close()
        return # TODO: introduce error code

    server_socket.settimeout(1.0)
    server_socket.listen(5)  # maximum number of connections  # TODO: command line parameter
    msg = f"<<< TCP/IP testserver {VERSION} is running on {host}:{port} >>>"
    rf_log.info(msg)
    tcp_ip_testserver_log.tlog("start_server", msg)

    while not STOP_EVENT.is_set():
        try:
            # wait for incoming connections
            client_socket, client_address = server_socket.accept()
            # create new thread for new client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True  # automatically end thread at quit of testserver
            client_thread.start()
        except socket.timeout:
            continue

    STOP_EVENT.clear()
    server_socket.close()
    msg = f"TCP/IP testserver closed socket"
    rf_log.info(msg)
    tcp_ip_testserver_log.tlog("start_server", msg)
    return 0

# --------------------------------------------------------------------------------------------------------------

# This module is independent from Robot Framework; no access to Robot Framework Output_Dir.
# Therefore the reference for all further files and folders is per default the position of this file.
# In command line this can be changed.

tcp_ip_testserver_file_path = os.path.dirname(CString.NormalizePath(__file__))
arguments = sys.argv
if len(arguments) > 1:
    tcp_ip_testserver_log_files = f"{arguments[1]}/testserver_logfiles"
else:
    tcp_ip_testserver_log_files = f"{tcp_ip_testserver_file_path}/testserver_logfiles"

# activate logging
tcp_ip_testserver_log = threadlog(tcp_ip_testserver_log_files)
tcp_ip_testserver_log.tlog("tcp_ip_testserver", f"This is TCP/IP testserver v. {VERSION}")
tcp_ip_testserver_log.tlog("tcp_ip_testserver", f"Log files: '{tcp_ip_testserver_log_files}'")
lock_file = f"{tcp_ip_testserver_file_path}/tcp_ip_testserver.lock"
tcp_ip_testserver_log.tlog("tcp_ip_testserver", f"Lock file '{lock_file}'")

stored_pid = None
if os.path.exists(lock_file): # TODO: maybe lock file is not required, because already socket is checked if in use
    with open(lock_file, "r") as lock_file_handle:
        stored_pid = lock_file_handle.read()
        list_pids = psutil.pids()
        if stored_pid in list_pids:
            msg = f"TCP/IP testserver is already running (with PID: {stored_pid})!"
            rf_log.warn(msg)
            tcp_ip_testserver_log.tlog("tcp_ip_testserver", msg)
            sys.exit(1)
        else:
            # stored pid not in pid list; seems to be an outdated one and process not running any more
            lock_file_handle.close()
            os.remove(lock_file)

current_pid = str(os.getpid())
with open(lock_file, "w") as lock_file_handle:
    lock_file_handle.write(current_pid)
tcp_ip_testserver_log.tlog("tcp_ip_testserver", f"current PID: {current_pid}")

try:
    start_server()
finally:
    if os.path.exists(lock_file):
        os.remove(lock_file)
# TODO: In case of a crash 'tcp_ip_testserver.lock' remains. But also PID is checked.
# Also the socket is checked. Do we need the lock file?

msg = f"<<< TCP/IP testserver finished>>>"
rf_log.info(f"\n{msg}\n")
tcp_ip_testserver_log.tlog("tcp_ip_testserver", msg)

sys.exit(0)
