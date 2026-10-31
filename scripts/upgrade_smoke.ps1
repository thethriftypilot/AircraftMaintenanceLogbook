$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$projectPath = (Get-Location).Path
$trialRoot = Join-Path $projectPath ('build/upgrade-' + [guid]::NewGuid().ToString())
$appPath = Join-Path $trialRoot 'app'
$dataPath = Join-Path $trialRoot 'data'
New-Item -ItemType Directory -Path $trialRoot | Out-Null
function Run-Checked([string]$File,[string[]]$Arguments) {
 $process = Start-Process -FilePath $File -ArgumentList $Arguments -PassThru -WindowStyle Hidden
 if (!$process.WaitForExit(120000)) { $process.Kill();throw "Timeout: $File" }
 if ($process.ExitCode -ne 0) { throw "Exit $($process.ExitCode): $File" }
}
$old = (Resolve-Path 'dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Setup-1.0.0.exe').Path
$new = (Resolve-Path 'dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Setup-1.1.0-rc1.exe').Path
Run-Checked $old @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="'+$appPath+'"'))
$executable = Join-Path $appPath 'AircraftMaintenanceLogbook.exe'
Run-Checked $executable @('--smoke-test',('"'+$dataPath+'"'))
& .\.venv\Scripts\python.exe scripts/upgrade_fixture.py seed $dataPath
if ($LASTEXITCODE -ne 0) { throw 'Legacy fixture failed' }
Run-Checked $new @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',('/DIR="'+$appPath+'"'))
Run-Checked $executable @('--smoke-test',('"'+$dataPath+'"'))
Run-Checked $executable @('--data-dir',('"'+$dataPath+'"'),'--screenshot',('"'+$projectPath+'\docs\rc-evidence\installed-upgrade.png"'))
& .\.venv\Scripts\python.exe scripts/upgrade_fixture.py check $dataPath
if ($LASTEXITCODE -ne 0) { throw 'Upgrade preservation check failed' }
Run-Checked $executable @('--smoke-test',('"'+$dataPath+'"'))
$beforeUninstall = (Get-FileHash (Join-Path $dataPath 'logbook.db')).Hash
Run-Checked (Join-Path $appPath 'unins000.exe') @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART')
$afterUninstall = (Get-FileHash (Join-Path $dataPath 'logbook.db')).Hash
if ($beforeUninstall -ne $afterUninstall) { throw 'Uninstall altered test database' }
@{old_version='1.0.0';new_version='1.1.0-rc1';installed_old=$true;upgraded_same_app_folder=$true;installed_smoke=$true;native_ui=$true;restart=$true;uninstall_preserved_data=$true;data_path=$dataPath;clean_vm_without_python=$false;physical_printer=$false} | ConvertTo-Json | Set-Content docs/upgrade-installer-evidence.json
