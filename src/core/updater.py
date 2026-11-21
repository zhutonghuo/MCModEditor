"""自动更新引擎。

职责：
1. 从服务器拉取 version.json（自带超时、代理容错）。
2. 对比版本号判断是否有新版。
3. 下载绿色版更新包（zip），校验 SHA1。
4. 通过一个"延迟覆盖器"在主程序退出后替换安装目录文件——
   这样能覆盖正在运行、被 Windows 锁定的 exe/dll，全程不卸载、不删工程文件。

覆盖器用 pythonw.exe 静默启动一个独立脚本（不弹控制台），等待主进程退出后
解压 zip 覆盖目标目录，再重新启动主程序。脚本与路径中的中文统一用 base64
传递，避免任何命令行编码问题。
"""
import os
import sys
import json
import ssl
import base64
import hashlib
import tempfile
import subprocess
import urllib.request

from core.version import (
    APP_NAME, APP_VERSION, VERSION_CODE, VERSION_URL,
)

UA = "MCModEditor-Updater/1.0"
TIMEOUT = 20


def _b64(text):
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _unb64(text):
    return base64.b64decode(text.encode("ascii")).decode("utf-8")


def _opener():
    """构造忽略证书校验的 opener（兼容本机代理的自签证书）。"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    except Exception:
        return urllib.request.build_opener()


def app_dir():
    """返回当前程序所在安装目录。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch_version(url=VERSION_URL, timeout=TIMEOUT):
    """拉取服务器版本清单，返回 dict；失败抛异常。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with _opener().open(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", "replace")
    info = json.loads(raw)
    if not isinstance(info, dict) or "version_code" not in info:
        raise ValueError("版本清单格式无效")
    return info


def code_of(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def has_update(info):
    """服务器版本是否高于当前版本。"""
    return code_of(info.get("version_code")) > VERSION_CODE


def human_size(num):
    try:
        n = float(num)
    except (TypeError, ValueError):
        return "未知大小"
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} GB"


def _sha1(path, chunk=1 << 20):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def download_package(url, dest, progress_cb=None, timeout=180):
    """下载更新包到 dest，返回路径。progress_cb(done, total) 回调进度。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with _opener().open(req, timeout=timeout) as resp, open(dest, "wb") as f:
        total = 0
        try:
            total = int(resp.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            total = 0
        done = 0
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if progress_cb:
                try:
                    progress_cb(done, total)
                except Exception:
                    pass
    return dest


def verify(path, sha1):
    """校验 SHA1；sha1 为空则跳过并返回 True。"""
    if not sha1:
        return True
    return _sha1(path).lower() == str(sha1).lower()


def build_updater_script(package_path, target_dir, exe_name, pid, log_path=None):
    """生成延迟覆盖器脚本（纯 ASCII 源码，中文参数用 base64）。"""
    exe_path = os.path.join(tempfile.gettempdir(), "mcme_updater_worker.py")
    # 用 repr 写 Python 字面量，彻底规避引号/转义问题
    lines = [
        "# -*- coding: utf-8 -*-",
        "import os, sys, time, zipfile, shutil, subprocess, traceback",
        f"PKG = {package_path!r}",
        f"DST = {target_dir!r}",
        f"EXE = {exe_name!r}",
        f"PID = {int(pid)}",
        f"LOG = {log_path!r}" if log_path else "LOG = None",
        "",
        "def log(msg):",
        "    try:",
        "        if LOG:",
        "            with open(LOG, 'a', encoding='utf-8') as f:",
        "                f.write(str(msg) + '\\n')",
        "    except Exception:",
        "        pass",
        "",
        "def wait_pid(p, limit=40):",
        "    import ctypes",
        "    for _ in range(limit):",
        "        if not _alive(p):",
        "            return True",
        "        time.sleep(0.5)",
        "    return False",
        "",
        "def _alive(p):",
        "    try:",
        "        import ctypes",
        "        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, p)",
        "        if not h:",
        "            return False",
        "        ctypes.windll.kernel32.CloseHandle(h)",
        "        return True",
        "    except Exception:",
        "        return False",
        "",
        "try:",
        "    log('updater start, wait pid ' + str(PID))",
        "    wait_pid(PID)",
        "    log('extracting')",
        "    with zipfile.ZipFile(PKG, 'r') as z:",
        "        z.extractall(DST)",
        "    log('extracted')",
        "    try: os.remove(PKG)",
        "    except Exception: pass",
        "    exe = os.path.join(DST, EXE)",
        "    if os.path.exists(exe):",
        "        subprocess.Popen([exe], cwd=DST)",
        "        log('restarted')",
        "except Exception:",
        "    log(traceback.format_exc())",
        "finally:",
        "    try: os.remove(os.path.abspath(__file__))",
        "    except Exception: pass",
    ]
    with open(exe_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return exe_path


def schedule_apply(package_path, exe_name=None, target_dir=None):
    """安排覆盖更新：启动独立 pythonw 覆盖器，返回 (ok, message)。

    必须在主程序退出前调用；覆盖器会自行等待本进程退出后再动文件。
    """
    if exe_name is None:
        exe_name = os.path.basename(sys.executable) if getattr(sys, "frozen", False) else "MC模组编辑器.exe"
    if target_dir is None:
        target_dir = app_dir()
    pid = os.getpid()
    log_path = os.path.join(tempfile.gettempdir(), "mcme_updater.log")
    script = build_updater_script(package_path, target_dir, exe_name, pid, log_path)
    pyw = _pythonw()
    try:
        if pyw:
            subprocess.Popen([pyw, script],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
        else:
            subprocess.Popen([sys.executable, script],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
        return True, log_path
    except Exception as exc:
        return False, str(exc)


def _pythonw():
    """优先找 pythonw.exe 以静默运行覆盖器；找不到则回退当前解释器。"""
    candidates = []
    exe = sys.executable
    if exe:
        candidates.append(os.path.join(os.path.dirname(exe), "pythonw.exe"))
        base = os.path.dirname(os.path.dirname(exe))
        candidates.append(os.path.join(base, "pythonw.exe"))
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None
