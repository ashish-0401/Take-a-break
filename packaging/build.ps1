# Build script: produces dist\take-a-break\take-a-break.exe (one-folder).
# Usage:   .\packaging\build.ps1
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot\..
try {
    python -m pip install --upgrade pip pyinstaller PySide6 | Out-Host
    if (Test-Path build) { Remove-Item build -Recurse -Force }
    if (Test-Path dist)  { Remove-Item dist  -Recurse -Force }
    pyinstaller packaging\take-a-break.spec --clean --noconfirm
    Write-Host ""
    Write-Host "Built: dist\take-a-break\take-a-break.exe" -ForegroundColor Green
}
finally {
    Pop-Location
}
