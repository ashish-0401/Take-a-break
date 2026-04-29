' Silently launch take-a-break (no console window).
' Uses a renamed copy of pythonw.exe so it appears as "take-a-break.exe"
' in Task Manager.
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")
projectDir = fso.GetParentFolderName(WScript.ScriptFullName)
srcDir     = projectDir & "\src"
exePath    = projectDir & "\bin\take-a-break.exe"

cmd = "cmd.exe /c set ""PYTHONPATH=" & srcDir & """ && """ & exePath & """ -m take_a_break"
sh.CurrentDirectory = projectDir
sh.Run cmd, 0, False

