"""生成服务器版本清单 version.json 与绿色版更新包 zip。

用法：python make_version.py
产出：
  安装包/MCModEditor-Update-v1.0.zip   绿色版更新包（主程序自动更新下载它）
  version.json                          服务器清单（含 sha1/大小）
"""
import os
import json
import hashlib
import zipfile
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist", "MC模组编辑器")
OUT = os.path.join(ROOT, "安装包")
BASE = "http://47.95.246.166/mcmodeditor"

VERSION = "1.0"
CODE = 100
ZIP_NAME = "MCModEditor-Update-v1.0.zip"


def sha1(path, chunk=1 << 20):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def make_zip():
    os.makedirs(OUT, exist_ok=True)
    zpath = os.path.join(OUT, ZIP_NAME)
    count = 0
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for root, dirs, files in os.walk(DIST):
            dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
            for fn in files:
                if fn.endswith(".pyc"):
                    continue
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, DIST)
                z.write(full, rel)
                count += 1
    print("zip:", zpath, "| files:", count, "|", os.path.getsize(zpath) // 1024 // 1024, "MB")
    return zpath


def main():
    zpath = make_zip()
    size = os.path.getsize(zpath)
    digest = sha1(zpath)
    info = {
        "version": VERSION,
        "version_code": CODE,
        "date": datetime.date.today().isoformat(),
        "changelog": [
            "新增「检查更新」按钮，支持一键自动更新",
            "安装程序自动检测已装版本并覆盖更新（不卸载、保留工程）",
            "支持选择其他目录全新安装",
            "修复启动崩溃，新增程序与安装包图标",
        ],
        "package_url": f"{BASE}/%E4%B8%8B%E8%BD%BD/{ZIP_NAME}",
        "package_size": size,
        "sha1": digest,
        "setup_url": f"{BASE}/%E4%B8%8B%E8%BD%BD/MCModEditor-Setup-v1.0.exe",
        "green_url": f"{BASE}/dist/",
    }
    vpath = os.path.join(ROOT, "version.json")
    with open(vpath, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print("version.json:", vpath)
    print("sha1:", digest)
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
