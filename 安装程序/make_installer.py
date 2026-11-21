import os
import sys
import shutil
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist", "MC模组编辑器")
OUT = os.path.join(ROOT, "安装包")
EXE = os.path.join(OUT, "MC模组编辑器_安装包_v1.0.exe")
PAYLOAD = os.path.join(ROOT, "_payload_tmp_" + str(int(time.time())))
PY = sys.executable


def make_payload():
    if os.path.exists(PAYLOAD):
        for i, (root, dirs, files) in enumerate(os.walk(PAYLOAD, topdown=False)):
            for fn in files[:20]:
                try: os.remove(os.path.join(root, fn))
                except Exception: pass
            try: os.rmdir(root)
            except Exception: pass
    shutil.copytree(DIST, PAYLOAD)
    print("payload ready:", PAYLOAD)


def build_installer_src():
    """安装向导源码以 installer_src.py 为唯一真相源。"""
    path = os.path.join(ROOT, "安装程序", "installer_src.py")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    print("installer source:", path)
    return path


def build():
    make_payload()
    src = build_installer_src()
    res = os.path.join(ROOT, "src", "resources")
    spec = os.path.join(ROOT, "安装程序", "installer.spec")
    with open(spec, "w", encoding="utf-8") as f:
        f.write(f'''# -*- mode: python ; coding: utf-8 -*-
a = Analysis(["{src}"], pathex=[], binaries=[],
    datas=[(r"{PAYLOAD}", "_payload"), (r"{res}", "_res")],
    hiddenimports=["win32com.client","win32com.shell","pythoncom","pywintypes"],
    excludes=["QtQuick","QtQml","QtWebEngine","QtMultimedia","PIL","numpy","matplotlib"],
    noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="MC模组编辑器_安装包_v1.0",
    debug=False, console=False, upx=False, icon=r"{os.path.join(res, 'setup.ico')}")
''')
    os.makedirs(OUT, exist_ok=True)
    cmd = [PY, "-m", "PyInstaller", spec, "--noconfirm",
           "--distpath", OUT,
           "--workpath", os.path.join(ROOT, "安装程序", "build_tmp")]
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print("installer build failed", r.returncode)
        sys.exit(r.returncode)
    print("installer done:", EXE, os.path.getsize(EXE) // 1024 // 1024, "MB")
    en = os.path.join(OUT, "MCModEditor-Setup-v1.0.exe")
    shutil.copy2(EXE, en)
    print("english copy:", en)


if __name__ == "__main__":
    build()
