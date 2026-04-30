# Build script: produces dist\take-a-break\take-a-break.exe (one-folder)
# then wraps it in an Inno Setup installer.
# Usage:   .\packaging\build.ps1
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot\..
try {
    python -m pip install --upgrade pip pyinstaller PySide6 | Out-Host

    if (Test-Path build) { Remove-Item build -Recurse -Force }
    if (Test-Path dist)  { Remove-Item dist  -Recurse -Force }

    # PyInstaller writes progress to stderr — don't let that abort the script.
    $ErrorActionPreference = "Continue"
    python -m PyInstaller installer\take-a-break.spec --clean --noconfirm 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
    $ErrorActionPreference = "Stop"

    # Find ISCC.exe (works for both system-wide and per-user installs)
    $iscc = Get-ChildItem "$env:LOCALAPPDATA\Programs", "C:\Program Files*" `
        -Recurse -Filter "ISCC.exe" -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName

    if (-not $iscc) {
        Write-Warning "Inno Setup not found. Install from https://jrsoftware.org/isdl.php"
        Write-Warning "Skipping installer build. Exe bundle is at dist\take-a-break\"
        return
    }

    New-Item -ItemType Directory -Force -Path dist-installer | Out-Null
    & $iscc installer\installer.iss

    # The PyInstaller `dist\` and `build\` folders are just intermediates
    # used to produce the installer; delete them so only the user-facing
    # one-click installer remains.
    if (Test-Path dist)  { Remove-Item dist  -Recurse -Force }
    if (Test-Path build) { Remove-Item build -Recurse -Force }

    Write-Host ""
    Write-Host "Installer: dist-installer\take-a-break-setup.exe" -ForegroundColor Green
}
finally {
    Pop-Location
}
