@echo off

REM Set proxy server details
set "proxyServer=localhost"
set "proxyPort=3128"
set "proxyUsername=user"
set "proxyPassword=password"

REM URL of the executable file to download
set "erlang_exe=https://github.com/erlang/otp/releases/download/OTP-26.2.1/otp_win64_26.2.1.exe"

REM URL of the ZIP file to download
set "rabbitmq_zip=https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.12.10/rabbitmq-server-windows-3.12.10.zip"

REM Destination paths for downloaded files
set "downloadPath_exe=%CD%\otp_win64_26.2.1.exe"
set "downloadPath_zip=%CD%\rabbitmq-server-windows-3.12.10.zip"

REM Download the executable file using bitsadmin
REM bitsadmin /transfer "DownloadingExeFile" /download /priority normal /proxy %proxyServer%:%proxyPort% "%erlang_exe%" "%downloadPath_exe%"
powershell -command "& {Invoke-WebRequest -Uri '%erlang_exe%' -OutFile '%downloadPath_exe%' -Proxy 'http://%proxyServer%:%proxyPort%' -UseBasicParsing}"

REM Check if the download was successful
if %errorlevel% neq 0 (
    echo Downloading executable failed.
    exit /b 1
)

REM Install the downloaded executable file (change the command as per your installer)
start "" "%downloadPath_exe%"

REM Download the ZIP file using bitsadmin
REM bitsadmin /transfer "DownloadingZipFile" /download /priority normal /proxy %proxyServer%:%proxyPort% "%rabbitmq_zip%" "%downloadPath_zip%"
powershell -command "& {Invoke-WebRequest -Uri '%rabbitmq_zip%' -OutFile '%downloadPath_zip%' -Proxy 'http://%proxyServer%:%proxyPort%' -UseBasicParsing}"

REM Check if the download was successful
if %errorlevel% neq 0 (
    echo Downloading ZIP file failed.
    exit /b 1
)

REM Prompt user to choose extraction path
set /p extractDefault="Do you want to extract to the default path? (Y/N): "
if /i "%extractDefault%"=="Y" (
    set "extractPath=%CD%\rabbitmq-server-windows-3.12.10"
) else (
    set /p extractPath="Enter the full path to extract the files: "
)

REM Create the extraction directory if it doesn't exist
if not exist "%extractPath%" (
    mkdir "%extractPath%"
)

REM Extract the ZIP file to the specified path
powershell Expand-Archive -Path "%downloadPath_zip%" -DestinationPath "%extractPath%"

REM Ask user if they want to set an environment variable
set /p setEnvVar="Do you want to set HOMEDRIVE variable to the extraction path (HOMEDRIVE="%extractPath%\env")? (Y/N): "
if /i "%setEnvVar%"=="Y" (
	REM echo "%extractPath%\env"
    set HOMEDRIVE="%extractPath%\env"
) else (
    set /p customEnvPath="Enter the path to set as HOMEDRIVE variable (if not, leave blank): "
    if not "%customEnvPath%"=="" (
        set HOMEDRIVE="%customEnvPath%"
    )
)

set /p setEnvVar="Do you want to set ERLANG_HOME variable as default (C:\Program Files\Erlang OTP)? (Y/N): "
if /i "%setEnvVar%"=="Y" (
	REM echo "%extractPath%\env"
    set "ERLANG_HOME=C:\Program Files\Erlang OTP"
) else (
    set /p customEnvPath="Enter the path to set as ERLANG_HOME variable (if not, leave blank): "
    if not "%customEnvPath%"=="" (
        set ERLANG_HOME="%customEnvPath%"
    )
)

REM set "ERLANG_HOME=C:\Program Files\Erlang OTP"

REM Run rabbitmq-service.bat with specified arguments
if exist "%ExtractPath%\rabbitmq_server-3.12.10\sbin\rabbitmq-service.bat" (
    call "%ExtractPath%\rabbitmq_server-3.12.10\sbin\rabbitmq-service.bat" install
    call "%ExtractPath%\rabbitmq_server-3.12.10\sbin\rabbitmq-service.bat" enable
    call "%ExtractPath%\rabbitmq_server-3.12.10\sbin\rabbitmq-service.bat" start
) else (
    echo %ExtractPath%\rabbitmq_server-3.12.10\sbin\rabbitmq-service.bat not found in the specified path.
)

exit /b 0
