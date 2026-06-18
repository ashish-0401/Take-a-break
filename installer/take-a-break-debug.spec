# Debug PyInstaller spec for take-a-break (console + bootloader debug)
from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT / "installer" / "entry.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=[
        (str(ROOT / "assets"), "assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter", "test", "unittest", "pydoc", "doctest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="take-a-break-debug",
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,                 # show console for debug
    disable_windowed_traceback=False,
    icon=str(ROOT / "assets" / "chubby-cat.png"),
    version=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    [d for d in a.datas if not d[0].endswith('.qm')],
    strip=False,
    upx=False,
    upx_exclude=[],
    name="take-a-break-debug",
)
