import os
import sys
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def rmtree_batched(path):
    for _ in range(8):
        if not os.path.exists(path):
            break
        for root, dirs, files in os.walk(path, topdown=False):
            for fn in files[:20]:
                try: os.remove(os.path.join(root, fn))
                except Exception: pass
            try: os.rmdir(root)
            except Exception: pass


def clean():
    import time
    stamp = str(int(time.time()))
    for name in ["build", "dist/MC模组编辑器"]:
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            trash = p + "_old_" + stamp
            try:
                os.rename(p, trash)
                print("moved aside", name, "->", os.path.basename(trash))
            except Exception:
                rmtree_batched(p)
                print("cleaned", name)


def build():
    clean()
    cmd = [
        PY, "-m", "PyInstaller",
        "MC模组编辑器.spec",
        "--noconfirm",
        "--distpath", os.path.join(ROOT, "dist"),
        "--workpath", os.path.join(ROOT, "build"),
    ]
    print("running:", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print("BUILD FAILED", r.returncode)
        sys.exit(r.returncode)
    print("BUILD OK")


if __name__ == "__main__":
    build()
