# --------------------------------------------------------------------------------------------------------------
# threadlog
# XC-HWP/ESW3-Queckenstedt
# 23.01.2025
# --------------------------------------------------------------------------------------------------------------

import os, sys, time
import threading

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.Folder.CFolder import CFolder

# --------------------------------------------------------------------------------------------------------------
# TM***

class threadlog:
    """Simple class to write content to thread specific log files
    """
   
    def __init__(self, dest_folder=None):
        if dest_folder is None:
            self.__dest_folder = CString.NormalizePath(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.__dest_folder = CString.NormalizePath(dest_folder)
        self.__execution_timestamp = time.strftime('%y-%m-%d_%H-%M-%S')
        handle_dest_folder = CFolder(self.__dest_folder)
        handle_dest_folder.Create(bOverwrite=False, bRecursive=True)
        del handle_dest_folder
        self.__dict_logfile_handles = {}
        self.__dict_print_count     = {}
        print(f"Log files will be written to '{self.__dest_folder}'")

    def __del__(self):
        for file_handle in self.__dict_logfile_handles.values():
            file_handle.close()
            del file_handle
        del self.__dict_logfile_handles
        del self.__dict_print_count

    # --------------------------------------------------------------------------------------------------------------

    def tlog(self, ident=None, message=None):
        ident = str(ident) # integers are accepted as input, but internally we only work with strings
        thread_id = threading.get_ident()
        full_ident = f"{ident}_{thread_id}"
        if full_ident not in self.__dict_logfile_handles:
            file = f"{self.__dest_folder}/{self.__execution_timestamp}_[{thread_id}]_[{ident}].log"
            file_handle = open(file, 'w', encoding='utf-8')
            self.__dict_logfile_handles[full_ident] = file_handle
            self.__dict_print_count[full_ident] = 0
        timestamp = time.strftime('%y%m%d-%H%M%S')
        current_time_high_res = time.perf_counter()
        current_time_milliseconds_high_res = int(current_time_high_res * 1000)
        current_time_milliseconds_high_res = str(current_time_milliseconds_high_res).rjust(5, '0')
        log_timestamp = f"{timestamp}-{current_time_milliseconds_high_res}"
        self.__dict_print_count[full_ident] = self.__dict_print_count[full_ident] + 1
        tlog_count = str(self.__dict_print_count[full_ident]).rjust(3, '0')
        out = f"{log_timestamp} [{thread_id}] [{ident}] ({tlog_count}) : {message}"
        self.__dict_logfile_handles[full_ident].write(f"{out}\n")
        self.__dict_logfile_handles[full_ident].flush()
    # eof def tlog(self, ident=None, message=None):

# --------------------------------------------------------------------------------------------------------------



