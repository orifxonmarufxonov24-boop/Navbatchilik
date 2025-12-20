' Face Recognition Server - Quick Start
' ======================================
' Bu faylni ikki marta bosing va server ishga tushadi
' Fon rejimida ishlaydi, oyna ko'rinmaydi

Set WshShell = CreateObject("WScript.Shell")
currentDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
serverPath = currentDir & "\yangi\face_server.py"

' Serverni fon rejimida ishga tushirish
WshShell.Run "pythonw """ & serverPath & """", 0, False

' Xabar ko'rsatish
MsgBox "Face Recognition Server ishga tushdi!" & vbCrLf & vbCrLf & _
       "Server manzili: http://localhost:5000" & vbCrLf & vbCrLf & _
       "Endi telefondan yo'qlama olishingiz mumkin!", _
       vbInformation, "Server Tayyor"
