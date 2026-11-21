# -*- mode: python ; coding: utf-8 -*-
a = Analysis(["D:\一些小项目\MC模组编辑器\安装程序\installer_src.py"], pathex=[], binaries=[],
    datas=[(r"D:\一些小项目\MC模组编辑器\_payload_tmp_1795239892", "_payload"), (r"D:\一些小项目\MC模组编辑器\src\resources", "_res")],
    hiddenimports=["win32com.client","win32com.shell","pythoncom","pywintypes"],
    excludes=["QtQuick","QtQml","QtWebEngine","QtMultimedia","PIL","numpy","matplotlib"],
    noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="MC模组编辑器_安装包_v1.0",
    debug=False, console=False, upx=False, icon=r"D:\一些小项目\MC模组编辑器\src\resources\setup.ico")
