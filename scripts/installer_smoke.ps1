param([string]$Installer = 'dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Setup-1.1.0-rc1.exe')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$workspacePath = (Get-Location).Path
$installPath = Join-Path $workspacePath 'build/installation-test/app'
$testDataPath = Join-Path $workspacePath 'build/installation-test/data'
$evidencePath = Join-Path $workspacePath 'docs/installer-smoke.json'
New-Item -ItemType Directory -Force (Split-Path $installPath -Parent) | Out-Null
function Run-Checked([string]$File, [string[]]$Arguments) {
    $launched = Start-Process -FilePath $File -ArgumentList $Arguments -PassThru -WindowStyle Hidden
    if (!$launched.WaitForExit(120000)) { $launched.Kill(); throw "Timed out: $File" }
    if ($launched.ExitCode -ne 0) { throw "Exit $($launched.ExitCode): $File" }
}
Run-Checked (Resolve-Path $Installer) @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="'+$installPath+'"'),('/LOG="'+$workspacePath+'\docs\install-test.log"'))
$exePath = Join-Path $installPath 'AircraftMaintenanceLogbook.exe'
Run-Checked $exePath @('--smoke-test',('"'+$testDataPath+'"'))
$first = Get-Content (Join-Path $testDataPath 'result.json') | ConvertFrom-Json
$before = (Get-FileHash (Join-Path $testDataPath 'logbook.db')).Hash
# Reinstall to the same application folder; it must not touch the external test database.
Run-Checked (Resolve-Path $Installer) @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="'+$installPath+'"'))
$after = (Get-FileHash (Join-Path $testDataPath 'logbook.db')).Hash
if ($before -ne $after) { throw 'Reinstall changed external user data.' }
Run-Checked $exePath @('--smoke-test',('"'+$testDataPath+'"'))
# Validate the installed native UI in a separate, fictional demo workspace.
Run-Checked $exePath @('--data-dir',('"'+$testDataPath+'"'),'--demo','--screenshot',('"'+$workspacePath+'\docs\screenshots\installed.png"'))
Run-Checked (Join-Path $installPath 'unins000.exe') @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART')
$preserved = Test-Path (Join-Path $testDataPath 'logbook.db')
if (!$preserved) { throw 'Uninstall removed external test data.' }
@{install_passed=$true;installed_smoke=$first;reinstall_preserved_database=($before -eq $after);restart_passed=$true;native_screenshot='docs/screenshots/installed.png';uninstall_preserved_external_data=$preserved;clean_machine_without_python_tested=$false;physical_printer_tested=$false} | ConvertTo-Json -Depth 4 | Set-Content $evidencePath
