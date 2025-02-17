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
VERSION = "v. 0.10.0 / 17.02.2025"
#
# --------------------------------------------------------------------------------------------------------------

import sys
import os
import time
import argparse
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

TIME_WAIT_BEFORE_CLOSE_SOCKET = 2

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

            # ----------------------------------------------------------------------------------
            # send answer(s) to client
            # ----------------------------------------------------------------------------------
            if data_received in DICT_ANSWERS:
                #
                # specific answer (currently not used)
                #
                response = DICT_ANSWERS[data_received]
                msg = f"[{client_address}] (SEND) '{response}'"
                rf_log.info(msg)
                tcp_ip_testserver_log.tlog("handle_client", msg)
                response = f"{response}\n"
                client_socket.send(response.encode('utf-8'))
            elif data_received.startswith("GET_SERVER_PID"):
                #
                # send the pid of this server
                #
                current_pid = str(os.getpid())
                response = f"PID={current_pid}"
                msg = f"[{client_address}] (SEND) '{response}'"
                rf_log.info(msg)
                tcp_ip_testserver_log.tlog("handle_client", msg)
                response = f"{response}\n"
                client_socket.send(response.encode('utf-8'))
            elif data_received.startswith("DELAY"):
                #
                # send standard answer with delay
                #
                list_data_received = data_received.split()
                delay = 6
                idend = "DELAY"
                if len(list_data_received) > 1:
                    delay = int(list_data_received[1])
                if len(list_data_received) > 2:
                    idend = list_data_received[2]
                msg = f"Now TCP/IP testserver is waiting for {delay} seconds until sending the answer"
                rf_log.info(msg)
                tcp_ip_testserver_log.tlog("handle_client", msg)
                time.sleep(delay)
                response = f"DELAY {delay} {idend} ACK"
                msg = f"[{client_address}] (SEND) '{response}'"
                rf_log.info(msg)
                tcp_ip_testserver_log.tlog("handle_client", msg)
                response = f"{response}\n"
                client_socket.send(response.encode('utf-8'))
            elif data_received.startswith("FETCHBLOCK"):
                #
                # send several answers (test of 'fetch_block' parameter of keyxword 'verify')
                #
                msg = "Now TCP/IP testserver sends several answers ('fetch_block' test)"
                rf_log.info(msg)
                tcp_ip_testserver_log.tlog("handle_client", msg)
                list_messages = [f"{data_received} ACK",
                                 f"{data_received} ACK [COND-1] [FETCHBLOCK_START]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [COND-2] [FETCHBLOCK_MIDDLE]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [COND-3] [FETCHBLOCK_MIDDLE]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [COND-4] [FETCHBLOCK_MIDDLE]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [COND-5] [FETCHBLOCK_END]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [COND-6] [OUTSIDE_FETCHBLOCK]",
                                 f"{data_received} ACK"]
                for index, message in enumerate(list_messages):
                    time.sleep(1)
                    response = f"{message} ({index+1})"
                    msg = f"[{client_address}] (SEND) '{response}'"
                    rf_log.info(msg)
                    tcp_ip_testserver_log.tlog("handle_client", msg)
                    response = f"{response}\n"
                    client_socket.send(response.encode('utf-8'))
            elif data_received.startswith("FETCHNESTEDBLOCKS"):
                #
                # send nested blocks of messages
                #
                msg = "Now TCP/IP testserver sends nested blocks of messages"
                rf_log.info(msg)
                tcp_ip_testserver_log.tlog("handle_client", msg)
                list_messages = [f"{data_received} ACK",
                                 f"{data_received} ACK [BLOCK-1] [FETCHNESTEDBLOCKS_START]",
                                 f"{data_received} ACK [BLOCK-2] [FETCHNESTEDBLOCKS_START]",
                                 f"{data_received} ACK [BLOCK-3] [FETCHNESTEDBLOCKS_START]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [BLOCK-1] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK [BLOCK-2] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK [BLOCK-3] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [BLOCK-1] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK [BLOCK-2] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK [BLOCK-3] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [BLOCK-1] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK [BLOCK-2] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK [BLOCK-3] [FETCHNESTEDBLOCKS_MIDDLE]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [BLOCK-1] [FETCHNESTEDBLOCKS_END]",
                                 f"{data_received} ACK [BLOCK-2] [FETCHNESTEDBLOCKS_END]",
                                 f"{data_received} ACK [BLOCK-3] [FETCHNESTEDBLOCKS_END]",
                                 f"{data_received} ACK",
                                 f"{data_received} ACK [BLOCK-1] [OUTSIDE_FETCHNESTEDBLOCKS]",
                                 f"{data_received} ACK [BLOCK-2] [OUTSIDE_FETCHNESTEDBLOCKS]",
                                 f"{data_received} ACK [BLOCK-3] [OUTSIDE_FETCHNESTEDBLOCKS]",
                                 f"{data_received} ACK"]
                for index, message in enumerate(list_messages):
                    time.sleep(1)
                    response = f"{message} ({index+1})"
                    msg = f"[{client_address}] (SEND) '{response}'"
                    rf_log.info(msg)
                    tcp_ip_testserver_log.tlog("handle_client", msg)
                    response = f"{response}\n"
                    client_socket.send(response.encode('utf-8'))
            elif data_received.startswith("GETNOTIFICATIONS"):
                #
                # send notifications back to client
                #
                msg = "Now TCP/IP testserver sends notifications back to client"
                rf_log.info(msg)
                tcp_ip_testserver_log.tlog("handle_client", msg)
                list_data_received = data_received.split()
                max_notifications = 10
                idend = "NOTIFICATION"
                if len(list_data_received) > 1:
                    max_notifications = int(list_data_received[1])
                if len(list_data_received) > 2:
                    idend = list_data_received[2]
                for iteration_number in range(1, max_notifications+1):
                    time.sleep(1)
                    response = f"NOTIFICATION ACK [{idend}-{iteration_number}/{max_notifications}]"
                    msg = f"[{client_address}] (SEND) '{response}'"
                    rf_log.info(msg)
                    tcp_ip_testserver_log.tlog("handle_client", msg)
                    response = f"{response}\n"
                    client_socket.send(response.encode('utf-8'))
                if len(list_data_received) > 3:
                    if list_data_received[3] == "CLOSE_CONNECTION":
                        time.sleep(TIME_WAIT_BEFORE_CLOSE_SOCKET) # giving the client a chance to receive the response before the socket is closed
                        break
            else:
                #
                # send standard answer (default)
                #
                response = f"{data_received} ACK"
                msg = f"[{client_address}] (SEND) '{response}'"
                rf_log.info(msg)
                tcp_ip_testserver_log.tlog("handle_client", msg)
                response = f"{response}\n"
                client_socket.send(response.encode('utf-8'))

            # special comands
            if data_received.startswith("CLOSE_CONNECTION"):
                time.sleep(TIME_WAIT_BEFORE_CLOSE_SOCKET) # giving the client a chance to receive the response before the socket is closed
                break
            elif data_received.startswith("QUIT_TESTSERVER"):
                STOP_EVENT.set()
                break

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

def start_server(host, port, max_connections):
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
    server_socket.listen(MAX_CONNECTIONS)
    msg = f"<<< TCP/IP testserver {VERSION} is running on {host}:{port} >>>"
    rf_log.info(msg)
    tcp_ip_testserver_log.tlog("start_server", msg)

    while not STOP_EVENT.is_set():
        try:
            # wait for incoming connections
            client_socket, client_address = server_socket.accept()
            msg = f"Accepted connection from {client_address}"
            rf_log.info(msg)
            tcp_ip_testserver_log.tlog("start_server", msg)
            # create new thread for new client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True  # automatically end thread at quit of testserver
            client_thread.start()
            msg = f"Started thread {client_thread.name} for {client_address}"
            rf_log.info(msg)
            tcp_ip_testserver_log.tlog("start_server", msg)
        except socket.timeout:
            continue
        except Exception as ex:
            msg = f"Exception in main loop: {ex}"
            rf_log.info(msg)
            tcp_ip_testserver_log.tlog("start_server", msg)
            continue # TODO: verify
    # eof while not STOP_EVENT.is_set():

    STOP_EVENT.clear()
    server_socket.close()
    msg = f"TCP/IP testserver closed socket"
    rf_log.info(msg)
    tcp_ip_testserver_log.tlog("start_server", msg)
    return 0

# --------------------------------------------------------------------------------------------------------------

# get command line
OUTPUT_DIR      = None
HOST            = None
PORT            = None
MAX_CONNECTIONS = 1
cmdline_parser = argparse.ArgumentParser()
cmdline_parser.add_argument('--output_dir', required=True, type=str, help='TCP/IP test server logfiles folder')
cmdline_parser.add_argument('--host', required=True, type=str, help='TCP/IP host name')
cmdline_parser.add_argument('--port', required=True, type=int, help='port number of TCP/IP host')
cmdline_parser.add_argument('--max_connections', required=False, type=int, default=MAX_CONNECTIONS, help='maximum number of connections')
cmdline_args = cmdline_parser.parse_args()
if cmdline_args.output_dir != None:
   OUTPUT_DIR = cmdline_args.output_dir
if cmdline_args.host != None:
   HOST = cmdline_args.host
if cmdline_args.port != None:
   PORT = cmdline_args.port
if cmdline_args.max_connections != None:
   MAX_CONNECTIONS = cmdline_args.max_connections

# activate logging
tcp_ip_testserver_log = threadlog(OUTPUT_DIR)
tcp_ip_testserver_log.tlog("tcp_ip_testserver", f"This is TCP/IP testserver v. {VERSION}")
tcp_ip_testserver_log.tlog("tcp_ip_testserver", f"Log files: '{OUTPUT_DIR}'")
lock_file = f"{OUTPUT_DIR}/tcp_ip_testserver.lock"
tcp_ip_testserver_log.tlog("tcp_ip_testserver", f"Lock file '{lock_file}'")

# log command line
tcp_ip_testserver_log.tlog("command_line", f"OUTPUT_DIR: {OUTPUT_DIR}")
tcp_ip_testserver_log.tlog("command_line", f"HOST: {HOST}")
tcp_ip_testserver_log.tlog("command_line", f"PORT: {PORT}")
tcp_ip_testserver_log.tlog("command_line", f"MAX_CONNECTIONS: {MAX_CONNECTIONS}")

# check lock file
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
    start_server(host=HOST, port=PORT, max_connections=MAX_CONNECTIONS)
finally:
    if os.path.exists(lock_file):
        os.remove(lock_file)
# TODO: In case of a crash 'tcp_ip_testserver.lock' remains. But also PID is checked.
# Also the socket is checked. Do we need the lock file?

msg = f"<<< TCP/IP testserver finished>>>"
rf_log.info(f"\n{msg}\n")
tcp_ip_testserver_log.tlog("tcp_ip_testserver", msg)

sys.exit(0)
