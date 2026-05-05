# Build script: produces dist\take-a-break\take-a-break.exe (one-folder)
# then wraps it in an Inno Setup installer.
# Usage:   .\packaging\build.ps1
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot\..
try {
    python -m pip install --upgrade pip | Out-Host
    python -m pip install --upgrade -r ..\requirements.txt pyinstaller Pillow | Out-Host

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
        Write-Host "Inno Setup not found. Downloading and installing InnoSetup..." -ForegroundColor Cyan
        
        $tempDir = $env:TEMP
        $innoSetupInstaller = Join-Path $tempDir "innosetup.exe"
        $innoSetupUrl = "https://github.com/jrsoftware/issrc/releases/download/is-6_7_1/innosetup-6.7.1.exe"
        
        try {
            # Download InnoSetup
            Write-Host "Downloading from $innoSetupUrl..." -ForegroundColor Cyan
            Invoke-WebRequest -Uri $innoSetupUrl -OutFile $innoSetupInstaller -ErrorAction Stop
            
            # Silent installation parameters for InnoSetup
            $ErrorActionPreference = "Continue"
            Write-Host "Installing InnoSetup..." -ForegroundColor Cyan
            & $innoSetupInstaller /SILENT /NORESTART | Out-Host
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "InnoSetup installation failed with exit code $LASTEXITCODE"
            }
            $ErrorActionPreference = "Stop"
            
            # Clean up installer
            Remove-Item $innoSetupInstaller -Force -ErrorAction SilentlyContinue
            
            # Wait a moment for installation to complete
            Start-Sleep -Seconds 2
            
            # Try to find ISCC.exe again
            $iscc = Get-ChildItem "$env:LOCALAPPDATA\Programs", "C:\Program Files*" `
                -Recurse -Filter "ISCC.exe" -ErrorAction SilentlyContinue |
                Select-Object -First 1 -ExpandProperty FullName
        }
        catch {
            Write-Warning "Failed to download/install InnoSetup: $_"
        }
        
        if (-not $iscc) {
            Write-Warning "Inno Setup installation failed or ISCC.exe not found."
            Write-Warning "Manual install: https://jrsoftware.org/isdl.php"
            Write-Warning "Skipping installer build. Exe bundle is at dist\take-a-break\"
            return
        }
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
    
    # Offer to install the built setup
    Write-Host ""
    $installNow = Read-Host "Install the app now? (y/n)"
    if ($installNow -eq "y" -or $installNow -eq "yes") {
        $setupExe = Join-Path $PSScriptRoot "..\dist-installer\take-a-break-setup.exe"
        if (Test-Path $setupExe) {
            Write-Host "Installing Take-a-break..." -ForegroundColor Cyan
            & $setupExe
        }
        else {
            Write-Warning "Setup file not found: $setupExe"
        }
    }
}
finally {
    Pop-Location
}
