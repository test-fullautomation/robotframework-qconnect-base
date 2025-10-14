Dim oWShell
Dim sEditor
Set oWShell = CreateObject("WScript.Shell")
sEditor = "C:\workplace\PCControl\Editor\NotepadPP\Notepad++Portable.exe"
oWShell.Run sEditor & " -lpython " & """C:\workplace\ROBFW\components\robotframework-qconnect-base\test\TCPIPClient\QCB-TCPIP-GC-030.robot""", 5, False

