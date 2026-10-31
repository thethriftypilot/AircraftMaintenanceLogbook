from pathlib import Path
import pefile
root=Path('dist/AircraftMaintenanceLogbook/_internal')
paths=[root,root/'shiboken6',root/'PySide6',Path('C:/Windows/System32')]
for file in [root/'PySide6'/'QtCore.pyd',root/'PySide6'/'Qt6Core.dll',root/'PySide6'/'pyside6.abi3.dll']:
    pe=pefile.PE(str(file))
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        name=entry.dll.decode();target=next((p/name for p in paths if (p/name).exists()),None)
        if not target or name.startswith('api-'):continue
        exported=pefile.PE(str(target))
        symbols={s.name for s in exported.DIRECTORY_ENTRY_EXPORT.symbols}
        missing=[i.name for i in entry.imports if i.name and i.name not in symbols]
        if missing:print(file.name,name,str(target),missing)
