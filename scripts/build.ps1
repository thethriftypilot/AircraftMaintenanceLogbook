param([string]$Python = '.venv\Scripts\python.exe', [string]$Iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe")
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
& $Python -m pytest -q --junitxml=docs/test-results.xml
if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
& $Python scripts/make_assets.py
$licensePackages = Get-Content requirements-lock.txt | ForEach-Object { ($_ -split '==')[0] }
& $Python -m piplicenses --packages $licensePackages --format=markdown --with-urls --with-license-file --no-license-path --output-file=THIRD_PARTY_LICENSES.md
Copy-Item USER_GUIDE.md resources/USER_GUIDE.md
New-Item -ItemType Directory -Force resources/licenses | Out-Null
Copy-Item LICENSE,THIRD_PARTY_LICENSES.md resources/licenses/
$buildOriginalPath = $env:PATH
try {
    # Do not collect unrelated ICU/UCRT DLLs from image/PDF tools on the caller's PATH.
    $pythonFolder = Split-Path (Resolve-Path $Python) -Parent
    $env:PATH = "$pythonFolder;$env:SystemRoot\System32;$env:SystemRoot"
    & $Python -m PyInstaller --noconfirm --clean --windowed --onedir --name AircraftMaintenanceLogbook --icon resources/app.ico --version-file scripts/version_info.txt --add-data 'resources;resources' --collect-data reportlab launch.py
} finally { $env:PATH = $buildOriginalPath }
if ($LASTEXITCODE -ne 0) { throw 'Executable build failed.' }
# CPython 3.13.7 ships an older VC runtime than Qt 6.10. Use Qt's newer,
# backward-compatible redistributable at the bootloader's search root.
$qtFolder = & $Python -c "import pathlib, PySide6; print(pathlib.Path(PySide6.__file__).parent)"
Copy-Item (Join-Path $qtFolder 'vcruntime140.dll'),(Join-Path $qtFolder 'vcruntime140_1.dll') dist/AircraftMaintenanceLogbook/_internal/ -Force
$smokeDir = Join-Path (Get-Location) 'build/packaged-smoke-rc1'
$process = Start-Process -FilePath 'dist/AircraftMaintenanceLogbook/AircraftMaintenanceLogbook.exe' -ArgumentList @('--smoke-test', ('"' + $smokeDir + '"')) -PassThru -WindowStyle Hidden
if (!$process.WaitForExit(60000)) { $process.Kill(); throw 'Packaged smoke timed out.' }
if ($process.ExitCode -ne 0 -or !(Test-Path "$smokeDir/result.json")) { throw 'Packaged smoke failed.' }
if (!(Test-Path $Iscc)) { $Iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" }
if (!(Test-Path $Iscc)) { throw 'Install Inno Setup 6 or pass -Iscc.' }
& $Iscc scripts/installer.iss
if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed.' }
Compress-Archive -Path dist/AircraftMaintenanceLogbook -DestinationPath dist/release/TheThriftyPilot-AircraftMaintenanceLogbook-Portable-1.1.0-rc1.zip -Force
Get-ChildItem dist/release/* | Get-FileHash -Algorithm SHA256 | Format-Table -AutoSize | Out-String | Set-Content dist/release/SHA256SUMS.txt
