# Face Recognition Server - Start Script
# =======================================
# Bu skriptni PowerShell'da ishga tushiring

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   FACE RECOGNITION SERVER - Local" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server ishga tushmoqda..." -ForegroundColor Yellow
Write-Host ""

# Yangi papkaga o'tish
Set-Location -Path "$PSScriptRoot\yangi"

# Serverni ishga tushirish
python face_server.py
