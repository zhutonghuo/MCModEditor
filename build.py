import os
import sys
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def clean():
    for name in ["build", "dist/MC模组编辑器"]:
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            shutil.rmtree(p)
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
