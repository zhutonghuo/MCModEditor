# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

SRC = os.path.join(os.getcwd(), "src")

a = Analysis(
    [os.path.join(SRC, "main.py")],
    pathex=[SRC],
    binaries=[],
    datas=[(os.path.join(SRC, "resources"), "resources")],
    hiddenimports=[
        "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "QtQuick", "QtQml", "QtWebEngine", "QtWebEngineCore", "QtWebChannel",
        "QtBluetooth", "QtNfc", "QtPositioning", "QtSensors", "QtSerialPort",
        "QtMultimedia", "QtMultimediaWidgets", "QtOpenGL", "QtSql", "QtTest",
        "QtDesigner", "QtHelp", "QtPrintSupport", "QtSvg", "QtXml", "QtXmlPatterns",
        "matplotlib", "numpy", "PIL", "tkinter",
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
    name="MC模组编辑器",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(SRC, "resources", "app.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="MC模组编辑器",
)
