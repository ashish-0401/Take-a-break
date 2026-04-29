<#
.SYNOPSIS
    Install or remove the take-a-break Startup-folder shortcut.

.PARAMETER Uninstall
    Remove the shortcut instead of installing it.
#>
[CmdletBinding()]
param(
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$vbs = Join-Path $projectRoot 'run.vbs'
$startup = [Environment]::GetFolderPath('Startup')
$lnk = Join-Path $startup 'Take-a-break.lnk'

if ($Uninstall) {
    if (Test-Path $lnk) {
        Remove-Item $lnk -Force
        Write-Host "Removed: $lnk"
    } else {
        Write-Host "Not installed (no shortcut at $lnk)."
    }
    return
}

if (-not (Test-Path $vbs)) {
    throw "Launcher not found: $vbs"
}

$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnk)
$s.TargetPath = $vbs
$s.WorkingDirectory = $projectRoot
$s.WindowStyle = 7
$s.Description = 'Take a break reminder'
$s.Save()
Write-Host "Installed: $lnk"
