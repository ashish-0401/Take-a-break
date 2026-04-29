# PyInstaller spec for take-a-break.
# Build with:  pyinstaller packaging\take-a-break.spec --clean

# -*- mode: python ; coding: utf-8 -*-
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
        # stdlib we don't need
        "tkinter", "test", "unittest", "pydoc", "doctest",
        "email", "html", "http", "urllib", "xml", "xmlrpc",
        # Unused PySide6 / Qt modules (big savings)
        "PySide6.QtWebEngine", "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets", "PySide6.QtWebChannel",
        "PySide6.QtWebSockets",
        "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DInput",
        "PySide6.Qt3DLogic", "PySide6.Qt3DAnimation", "PySide6.Qt3DExtras",
        "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
        "PySide6.QtBluetooth", "PySide6.QtNfc",
        "PySide6.QtPositioning", "PySide6.QtLocation",
        "PySide6.QtSensors", "PySide6.QtSerialPort", "PySide6.QtSerialBus",
        "PySide6.QtSql", "PySide6.QtTest",
        "PySide6.QtCharts", "PySide6.QtDataVisualization",
        "PySide6.QtPdf", "PySide6.QtPdfWidgets",
        "PySide6.QtQuick", "PySide6.QtQuickWidgets", "PySide6.QtQuickControls2",
        "PySide6.QtQml", "PySide6.QtRemoteObjects",
        "PySide6.QtVirtualKeyboard", "PySide6.QtScxml",
        "PySide6.QtNetwork", "PySide6.QtNetworkAuth",
        "PySide6.QtXml", "PySide6.QtConcurrent",
        "PySide6.QtHelp", "PySide6.QtDesigner", "PySide6.QtUiTools",
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
    name="take-a-break",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,                 # GUI app: no console window
    disable_windowed_traceback=False,
    icon=str(ROOT / "assets" / "chubby-cat.png"),
    version=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    # Strip Qt translation (.qm) files — app is English-only, saves ~6 MB.
    [d for d in a.datas if not d[0].endswith('.qm')],
    strip=False,
    upx=False,
    upx_exclude=[],
    name="take-a-break",
)
