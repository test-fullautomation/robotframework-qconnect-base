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
#################################################################################

# --------------------------------------------------------------------------------------------------------------
#
# test server for component 'QConnectBase'
#
# XC-HWP/ESW3-Queckenstedt
#
# v. 0.1.0 / 13.01.2025
# --------------------------------------------------------------------------------------------------------------

import sys
import os
import psutil
import socket
import threading

from PythonExtensionsCollection.String.CString import CString

dict_answers = {}
# >> used later do define specific answers deviating from standard (used e.g. for badcase tests)
# dict_answers['VERIFY PING 1']    = "VERIFY PING 1 ACK"
# dict_answers['VERIFY PING 2']    = "VERIFY PING 2 ACK"
# dict_answers['CLOSE_CONNECTION'] = "CLOSE_CONNECTION ACK"
# dict_answers['QUIT_TESTSERVER']  = "QUIT_TESTSERVER ACK"
# dict_answers[''] = ""

char_end_of_message = "*" # TODO: command line parameter

stop_event = threading.Event()

def handle_client(client_socket, client_address):
    print(f"Client connected: {client_address}")
    try:
        while True:
            # data received from client1
            data_received = ""
            while True:
                byte_received = client_socket.recv(1).decode("utf-8")
                if not byte_received:
                    print(f"[WARN] not 'byte_received'")        # TODO: usecase?
                    break
                data_received = f"{data_received}{byte_received}"
                if data_received == "":
                    print(f"[WARN] empty 'data_received' (1)")        # TODO: usecase?
                    break
                if ( (data_received[-1] == "\n") or (data_received[-1] == "\r") ):
                    # received standard 'end of message' character
                    break
                if char_end_of_message is not None:
                    if data_received[-1] == char_end_of_message:
                        # received specific 'end of message' character
                        break

            data_received = data_received.strip() # remove trailing and leading blanks and line breaks
            if data_received == "":
                continue

            print(f"[{client_address}] (REC) '{data_received}'")

            # send answer to client
            if data_received in dict_answers:
                response = dict_answers[data_received] # specific answer
            else:
                response = f"{data_received} ACK" # common answer
            print(f"[{client_address}] (SEND) '{response}'")
            response = f"{response}\n"
            client_socket.send(response.encode('utf-8'))

            # special comands
            if data_received == "CLOSE_CONNECTION":
                break
            elif data_received == "QUIT_TESTSERVER":
                stop_event.set()
                break

    except ConnectionResetError:
        print(f"TCP/IP testserver detected broken client connection: {client_address}")      # TODO: print this to Robot Framework log (use rf_log.py)
    finally:
        client_socket.close()
        print(f"TCP/IP testserver closed client connection: {client_address}")      # TODO: print this to Robot Framework log (use rf_log.py)

def start_server(host="localhost", port=4000): # TODO: host/port: command line parameter
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
    except Exception as ex:
        print(f"Exception: Socket already in use: {host}:{port}\n{ex}")      # TODO: print this to Robot Framework log (use rf_log.py)
        server_socket.close()
        return # TODO: introduce error code

    server_socket.settimeout(1.0)
    server_socket.listen(5)  # maximum number of connections  # TODO: command line parameter
    print(f"<<< TCP/IP testserver running on {host}:{port} >>>")      # TODO: print this to Robot Framework log (use rf_log.py)
    while not stop_event.is_set():
        try:
            # wait for incoming connections
            client_socket, client_address = server_socket.accept()
            # create new thread for new client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True  # automatically end thread at quit of testserver
            client_thread.start()
        except socket.timeout:
            continue

    stop_event.clear()
    server_socket.close()
    print(f"\nTCP/IP testserver closed socket\n")
    return 0

if __name__ == "__main__":
    tcp_ip_testserver_file_path = os.path.dirname(CString.NormalizePath(__file__))
    lock_file = f"{tcp_ip_testserver_file_path}/tcp_ip_testserver.lock"
    stored_pid = None
    if os.path.exists(lock_file): # TODO: maybe lock file is not required, because already socket is checked if in use
        with open(lock_file, "r") as lock_file_handle:
            stored_pid = lock_file_handle.read()
            list_pids = psutil.pids()
            if stored_pid in list_pids:
                print("TCP/IP testserver is already running!")
                sys.exit(1)
            else:
                # stored pid not in pid list; seems to be an outdated one and process not running any more
                lock_file_handle.close()
                os.remove(lock_file)

    with open(lock_file, "w") as lock_file_handle:
        lock_file_handle.write(str(os.getpid()))

    try:
        start_server()
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)
    # TODO: In case of a crash 'tcp_ip_testserver.lock' remains. But also PID is checked.
    # Also the socket is checked. Do we need the lock file?

    print(f"<<< TCP/IP testserver finished>>>\n")
    sys.exit(0)
