import os
import sys
import json
import base64
import urllib.request
import urllib.parse
import ssl
import subprocess
import paramiko

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("GH_TOKEN", "")
REPO = "MCModEditor"
SERVER = "47.95.246.166"
USER = "administrator"
PW = os.environ.get("SRV_PW", "")
REMOTE_DIR = "/C:/inetpub/wwwroot/mcmodeditor"

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
OPENER = urllib.request.build_opener(urllib.request.HTTPSHandler(context=CTX))


def api(path, method="GET", data=None):
    url = "https://api.github.com" + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": "token " + TOKEN,
        "Accept": "application/vnd.github+json",
        "User-Agent": "MCME-Publisher",
        "Content-Type": "application/json",
    })
    with OPENER.open(req, timeout=60) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def github():
    print("=== GitHub ===")
    try:
        api("/user/repos?per_page=100")
    except Exception as e:
        print("list repos fail", e)
    repos = api("/user/repos?per_page=100")
    exists = any(r["name"].lower() == REPO.lower() for r in repos)
    if not exists:
        api("/user/repos", "POST", {
            "name": REPO,
            "description": "我的世界模组编辑器 - 模型/动画/物品栏/积木编程/命令/UI 六合一图形化工坊",
            "private": False,
            "auto_init": True,
            "license_template": "mit",
        })
        print("created repo", REPO)
    else:
        print("repo exists")

    gitdir = os.path.join(ROOT, ".git")
    if not os.path.exists(gitdir):
        subprocess.run(["git", "init"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "zhutonghuo@users.noreply.github.com"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.name", "zhutonghuo"], cwd=ROOT, check=True)

    remote_url = f"https://{TOKEN}@github.com/zhutonghuo/{REPO}.git"
    r = subprocess.run(["git", "remote"], cwd=ROOT, capture_output=True, text=True)
    if "origin" in r.stdout:
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=ROOT, check=True)
    else:
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=ROOT, check=True)

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", "MC模组编辑器 v1.0 初始发布"], cwd=ROOT)
    subprocess.run(["git", "branch", "-M", "main"], cwd=ROOT, check=True)
    push = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("push rc:", push.returncode)
    if push.returncode != 0:
        print("push stderr:", push.stderr.decode("utf-8", "ignore")[-800:])
    else:
        print("pushed to GitHub")

    installer = find_installer()
    if installer:
        try:
            rel = api("/repos/zhutonghuo/" + REPO + "/releases", "POST", {
                "tag_name": "v1.0", "name": "MC模组编辑器 v1.0",
                "body": "六合一我的世界模组编辑器：模型/动画/物品栏/积木编程/命令/UI",
                "draft": False, "prerelease": False,
            })
            with open(installer, "rb") as f:
                data = f.read()
            req = urllib.request.Request(
                rel.get("upload_url", "").split("{")[0] + "?name=" +
                urllib.parse.quote(os.path.basename(installer)),
                data=data, method="POST", headers={
                    "Authorization": "token " + TOKEN,
                    "Content-Type": "application/octet-stream",
                    "User-Agent": "MCME-Publisher",
                })
            with OPENER.open(req, timeout=180) as r:
                print("release asset uploaded:", r.status)
        except Exception as e:
            print("release upload note:", e)
    return f"https://github.com/zhutonghuo/{REPO}"


def find_installer():
    d = os.path.join(ROOT, "安装包")
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.lower().endswith(".exe") and "安装包" in f:
                return os.path.join(d, f)
    return None


def server():
    print("=== Server ===")
    t = paramiko.Transport((SERVER, 22))
    t.connect(username=USER, password=PW)
    sftp = paramiko.SFTPClient.from_transport(t)

    def mkdirs(path):
        cur = ""
        for part in path.strip("/").split("/"):
            cur += "/" + part
            try:
                sftp.stat(cur)
            except IOError:
                sftp.mkdir(cur)

    mkdirs(REMOTE_DIR)
    count = 0
    for root, dirs, files in os.walk(ROOT):
        if any(x in root for x in [".git", "build", "__pycache__"]):
            continue
        rel = os.path.relpath(root, ROOT)
        if rel != ".":
            mkdirs(REMOTE_DIR + "/" + rel.replace("\\", "/"))
        for fn in files:
            if fn.endswith(".pyc"):
                continue
            local = os.path.join(root, fn)
            rem = REMOTE_DIR + "/" + (os.path.relpath(local, ROOT)).replace("\\", "/")
            try:
                sftp.put(local, rem)
                count += 1
            except Exception as e:
                print("upload fail", fn, e)
    print("uploaded files:", count)

    installer = find_installer()
    if installer:
        rem = REMOTE_DIR + "/下载/" + os.path.basename(installer)
        mkdirs(REMOTE_DIR + "/下载")
        sftp.put(installer, rem)
        print("installer uploaded:", os.path.basename(installer),
              os.path.getsize(installer) // 1024, "KB")
    sftp.close()

    chan = t.open_session()
    chan.exec_command(f'powershell -NoProfile -Command "Get-ChildItem \'{REMOTE_DIR}\' | Select-Object Name,Length"')
    out = chan.makefile("r").read().decode("utf-8", "ignore")
    print("remote listing:\n", out[:1200])
    t.close()
    return f"http://{SERVER}/mcmodeditor/"


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("github", "all"):
        try:
            print("GitHub URL:", github())
        except Exception as e:
            print("GitHub publish FAILED:", repr(e))
    if mode in ("server", "all"):
        try:
            print("Server URL:", server())
        except Exception as e:
            print("Server publish FAILED:", repr(e))
