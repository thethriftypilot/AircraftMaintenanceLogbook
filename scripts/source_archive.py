"""Create a source distribution from non-ignored project files; no remote publishing."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

root=Path(__file__).resolve().parents[1]
release=root/'dist'/'release';release.mkdir(parents=True,exist_ok=True)
files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=root).decode().split('\0')
target=release/'TheThriftyPilot-AircraftMaintenanceLogbook-Source-1.1.0-rc1.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for name in sorted(set(files)):
        if not name or name.endswith(('.log','.db','.db-wal','.db-shm','.zip','.exe','.pyc')) or any(part in {'.venv','.git','build','dist','__pycache__','.pytest_cache','.audit','testdata'} for part in Path(name).parts):continue
        if any(name.startswith(prefix) for prefix in ['docs/rc-evidence/','docs/screenshots/','docs/v1-evidence/']):continue
        path=root/name
        if path.is_file():archive.write(path,'thrifty-pilot-aircraft-maintenance/'+name)
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in release.iterdir() if p.suffix in ['.exe','.zip']}
(release/'SHA256SUMS.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in sorted(hashes.items())),encoding='utf-8')
print(json.dumps({p.name:p.stat().st_size for p in release.iterdir()},indent=2))
