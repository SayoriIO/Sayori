@echo off
echo Retrieving resources.zip
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://owo.whats-th.is/d7c9fe.zip  ', 'resources.zip')"

echo Extracting resources.zip
set vbs="%~dp0%\_.vbs"
if exist %vbs% del /f /q %vbs%
>%vbs%  echo Set fso = CreateObject("Scripting.FileSystemObject")
>>%vbs% echo If NOT fso.FolderExists("%~dp0") Then
>>%vbs% echo fso.CreateFolder("%~dp0")
>>%vbs% echo End If
>>%vbs% echo set objShell = CreateObject("Shell.Application")
>>%vbs% echo set FilesInZip=objShell.NameSpace("%~dp0resources.zip").items
>>%vbs% echo objShell.NameSpace("%~dp0").CopyHere(FilesInZip)
>>%vbs% echo Set fso = Nothing
>>%vbs% echo Set objShell = Nothing
cscript //nologo %vbs%
if exist %vbs% del /f /q %vbs%