# **************************************************************************************************************
#
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
#
# **************************************************************************************************************
#
# executerobottest_loop.py
#
# XC-HWP/ESW3-Queckenstedt
#
# Executes robot tests in a loop and recursively, starting in current folder.
#
# Triggers maximum 9999 iterations and can be stopped by deleting the control file
# (./aiotestlogfiles/loopinproccess.ctrl).
#
# --------------------------------------------------------------------------------------------------------------
#
# 26.02.2025
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, shutil, argparse, time

import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Folder.CFolder import CFolder

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBG = col.Style.BRIGHT + col.Fore.GREEN

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
    sys.stderr.write(COLBR + f"Error: {sMsg}!\n")

def printexception(sMsg):
    sys.stderr.write(COLBR + f"Exception: {sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------

# -- some informations about the environment of this script

sThisScript     = sys.argv[0]
sThisScript     = CString.NormalizePath(sThisScript)
sThisScriptPath = os.path.dirname(sThisScript)
sThisScriptName = os.path.basename(sThisScript)

sOSName         = os.name
sPlatformSystem = platform.system()
sPythonPath     = CString.NormalizePath(os.path.dirname(sys.executable))
sPython         = CString.NormalizePath(sys.executable)
sPythonVersion  = sys.version

if sPlatformSystem == "Windows":
    # nothing specific to do
    pass
elif sPlatformSystem == "Linux":
    # nothing specific to do
    pass
else:
   bSuccess = False
   sResult  = f"Operating system {sPlatformSystem} ({sOSName}) not supported"
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   sys.exit(ERROR)

print()
print(f"{sThisScriptName} is running under {sPlatformSystem} ({sOSName})")
print()

# --------------------------------------------------------------------------------------------------------------
# config:
nMaxIterations = 9999
# --------------------------------------------------------------------------------------------------------------
# TM***

nCntSomethingWentWrong = 0
sAIOTestLogfilesPath = CString.NormalizePath(f"./aiotestlogfiles", sReferencePathAbs=sThisScriptPath)
oAIOTestLogfilesPath = CFolder(sAIOTestLogfilesPath)
bSuccess, sResult = oAIOTestLogfilesPath.Create(bOverwrite=False, bRecursive=True)
if bSuccess is not True:
    printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
    sys.exit(ERROR)
sThiscriptLogFile = f"{sAIOTestLogfilesPath}/{sThisScriptName}.log"
oThiscriptLogFile = CFile(sThiscriptLogFile) # at least to know, when the RF returned something different than 0
sStartTimestamp = time.strftime('%Y.%m.%d %H-%M-%S')
oThiscriptLogFile.Write(f"This is {sThisScript}\n")
oThiscriptLogFile.Write(f"Loop execution started at '{sStartTimestamp}'\n")

sCtrlFile = None

for nCntIteration in range(1, nMaxIterations+1):
    print(f"==================================================")
    print(f"=== iteration '{nCntIteration}/{nMaxIterations}'")
    print(f"==================================================")

    # --- loop version

    sRobotCommandLine = "--exclude quicktest"
    sIterationTimestamp = time.strftime('%Y.%m.%d_%H-%M-%S')
    sLogFile = CString.NormalizePath(f"./aiotestlogfiles/{sIterationTimestamp}/aiotestlooplog.xml", sReferencePathAbs=sThisScriptPath)
    sCtrlFile = CString.NormalizePath(f"./aiotestlogfiles/loopinproccess.ctrl", sReferencePathAbs=sThisScriptPath)

    # -- create the log file folder

    oLogFile = CFile(sLogFile)
    dLogFileInfo     = oLogFile.GetFileInfo()
    del oLogFile
    sLogFilePath     = dLogFileInfo['sFilePath']
    sLogFileName     = dLogFileInfo['sFileName']
    sLogFileNameOnly = dLogFileInfo['sFileNameOnly']

    oLogFilePath = CFolder(sLogFilePath)
    bSuccess, sResult = oLogFilePath.Create(bOverwrite=False, bRecursive=True)
    del oLogFilePath
    if bSuccess is not True:
       error = CString.FormatResult(sThisScriptName, bSuccess, sResult)
       printerror(error)
       oThiscriptLogFile.Write(f"{error}\n")
       del oThiscriptLogFile
       sys.exit(ERROR)
    print(sResult)
    print()

    # -- check the control file
    if os.path.isfile(sCtrlFile) is False:
        oCtrlFile = CFile(sCtrlFile)
        oCtrlFile.Write("")
        del oCtrlFile

    # -- prepare the command line for the test execution

    listCmdLineParts = []
    listCmdLineParts.append(f"\"{sPython}\"")
    listCmdLineParts.append("-m robot")
    if sRobotCommandLine is not None:
       listCmdLineParts.append(f"{sRobotCommandLine}")
    listCmdLineParts.append(f"-d \"{sLogFilePath}\"")
    listCmdLineParts.append(f"-o \"{sLogFileName}\"")
    listCmdLineParts.append(f"-l \"{sLogFileNameOnly}_log.html\"")
    listCmdLineParts.append(f"-r \"{sLogFileNameOnly}_report.html\"")
    listCmdLineParts.append(f"-b \"{sLogFileNameOnly}.log\"")
    listCmdLineParts.append(f"\"{sThisScriptPath}\"")
    sCmdLine = " ".join(listCmdLineParts)
    del listCmdLineParts

    # -- execute the tests

    print(f"Now executing command line:\n{sCmdLine}")
    print()

    listCmdLineParts = shlex.split(sCmdLine)

    nReturn = ERROR
    try:
       nReturn = subprocess.call(listCmdLineParts)
       print()
       print(f"[{sThisScriptName}] : Subprocess ROBOT returned {nReturn}")
    except Exception as ex:
       print()
       printexception(str(ex))
       print()
       oThiscriptLogFile.Write(f"{ex}\n")
       del oThiscriptLogFile
       sys.exit(ERROR)
    print()

    if nReturn == SUCCESS:
       print(f"Test results in '{sLogFile}'")
       print()
       print(COLBG + f"{sThisScriptName} done")
    else:
       nCntSomethingWentWrong = nCntSomethingWentWrong + 1
       printerror(f"[{sThisScriptName}] : Subprocess ROBOT has not returned expected value {SUCCESS}")
       oThiscriptLogFile.Write(f"Iteration '{nCntIteration}/{nMaxIterations}' at '{sIterationTimestamp}':")
       oThiscriptLogFile.Write(f"Subprocess ROBOT has returned not expected value {nReturn}")
       oThiscriptLogFile.Write(f"Total number of iterations with errors: {nCntSomethingWentWrong}\n")

    print()

    # -- check the control file
    if os.path.isfile(sCtrlFile) is False:
        print(f"==================================================")
        print(f"=== premature end of loop in iteration '{nCntIteration}/{nMaxIterations}'")
        print(f"==================================================")
        oThiscriptLogFile.Write(f"Premature end of loop in iteration '{nCntIteration}/{nMaxIterations}'\n")

        break

# eof for nCntIteration in range(1, nMaxIterations+1):

sEndTimestamp = time.strftime('%Y.%m.%d %H-%M-%S')
oThiscriptLogFile.Write(f"Loop execution ended at '{sEndTimestamp}'")
del oThiscriptLogFile

if sCtrlFile is not None:
    oCtrlFile = CFile(sCtrlFile)
    oCtrlFile.Delete()
    del oCtrlFile

if nCntSomethingWentWrong > 0:
    sys.exit(nCntSomethingWentWrong)
else:
    sys.exit(SUCCESS)

# --------------------------------------------------------------------------------------------------------------

# ==== obsolete:

# nReturn:
# > 0  : internal error of this script
# < 0  : return value (!= 0) from subprocess
# == 0 : no internal error of this script and no error from subprocess

# sys.exit(nReturn)

# --------------------------------------------------------------------------------------------------------------





