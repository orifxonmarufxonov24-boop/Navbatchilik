' Face Recognition Server - Quick Start
' ======================================
' Bu faylni ikki marta bosing va server ishga tushadi

Set WshShell = CreateObject("WScript.Shell")
currentDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
serverPath = currentDir & "\yangi\face_server.py"

' So'rash: ngrok ishlatishni xohlaysizmi?
result = MsgBox("Internet orqali kirish kerakmi?" & vbCrLf & vbCrLf & _
                "HA - Internet orqali (telefondan)" & vbCrLf & _
                "YO'Q - Faqat lokal (bir WiFi)", _
                vbYesNo + vbQuestion, "Server Sozlamalari")

If result = vbYes Then
    ' ngrok bilan ishga tushirish (oyna ko'rinadi)
    WshShell.Run "cmd /k python """ & serverPath & """ --ngrok", 1, False
    MsgBox "Server internet rejimida ishga tushdi!" & vbCrLf & vbCrLf & _
           "Konsol oynasida INTERNET MANZIL ko'rsatiladi." & vbCrLf & _
           "Shu manzilni telefondan oching!", _
           vbInformation, "Ngrok Server"
Else
    ' Oddiy lokal server (fon rejimida)
    WshShell.Run "pythonw """ & serverPath & """", 0, False
    MsgBox "Lokal server ishga tushdi!" & vbCrLf & vbCrLf & _
           "Manzil: http://localhost:5000" & vbCrLf & vbCrLf & _
           "Telefon bir xil WiFi da bo'lishi kerak!", _
           vbInformation, "Lokal Server"
End If
