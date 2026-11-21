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
    src = r'''
import os, sys, shutil, subprocess
from PyQt5.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
import win32com.client
from win32com.shell import shell, shellcon

APP = "MC模组编辑器"
VER = "1.0"

def res_dir():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "_res")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "_res")

def payload_dir():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "_payload")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "_payload")

class InstallThread(QThread):
    progress = pyqtSignal(int, str)
    done = pyqtSignal(bool, str)
    def __init__(self, target, desktop, startmenu):
        super().__init__()
        self.target = target; self.desktop = desktop; self.startmenu = startmenu
    def run(self):
        try:
            os.makedirs(self.target, exist_ok=True)
            payload = payload_dir()
            files = []
            for root, dirs, fs in os.walk(payload):
                for f in fs: files.append(os.path.join(root, f))
            total = len(files)
            for i, f in enumerate(files):
                rel = os.path.relpath(f, payload)
                dst = os.path.join(self.target, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(f, dst)
                self.progress.emit(int((i+1)/total*100), rel)
            exe = os.path.join(self.target, APP + ".exe")
            self.make_shortcut(exe)
            self.progress.emit(100, "完成")
            self.done.emit(True, self.target)
        except Exception as e:
            self.done.emit(False, str(e))
    def make_shortcut(self, exe):
        sh = win32com.client.Dispatch("WScript.Shell")
        targets = []
        if self.desktop:
            try:
                targets.append(os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0), APP + ".lnk"))
            except Exception: pass
        if self.startmenu:
            try:
                sm = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0), APP)
                os.makedirs(sm, exist_ok=True)
                targets.append(os.path.join(sm, APP + ".lnk"))
            except Exception: pass
        ico = os.path.join(res_dir(), "setup.ico")
        for lnk in targets:
            try:
                s = sh.CreateShortCut(lnk)
                s.TargetPath = exe
                s.WorkingDirectory = os.path.dirname(exe)
                s.Description = APP + " - 我的世界模组创作工坊"
                if os.path.exists(ico): s.IconLocation = ico + ",0"
                s.save()
            except Exception: pass

class Page1(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("欢迎使用 " + APP + " 安装包")
        self.setSubTitle("版本 " + VER + " · 点击下一步开始安装")
        l = QVBoxLayout()
        head = QHBoxLayout()
        ico = os.path.join(res_dir(), "setup.png")
        if os.path.exists(ico):
            pm = QPixmap(ico).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lb = QLabel(); lb.setPixmap(pm); head.addWidget(lb)
        head.addWidget(QLabel("六合一我的世界模组创作工坊"))
        l.addLayout(head)
        l.addWidget(QLabel("本向导将安装："))
        for t in ["模型 / 动画 / 物品栏 / 积木编程 / 命令 / UI 六大工坊",
                  "桌面与开始菜单快捷方式", "完整的离线运行环境"]:
            l.addWidget(QLabel("  * " + t))
        self.setLayout(l)

class Page2(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("选择安装位置")
        default = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), APP)
        self.edit = QLineEdit(default)
        l = QVBoxLayout(); l.addWidget(QLabel("安装目录："))
        h = QHBoxLayout(); h.addWidget(self.edit)
        b = QPushButton("浏览..."); b.clicked.connect(self.browse); h.addWidget(b)
        l.addLayout(h); self.setLayout(l)
    def browse(self):
        d = QFileDialog.getExistingDirectory(self, "选择目录", self.edit.text())
        if d: self.edit.setText(os.path.join(d, APP))
    def validatePage(self):
        return bool(self.edit.text().strip())

class Page3(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("安装选项")
        self.cb_desktop = QCheckBox("创建桌面快捷方式"); self.cb_desktop.setChecked(True)
        self.cb_menu = QCheckBox("创建开始菜单快捷方式"); self.cb_menu.setChecked(True)
        self.cb_open = QCheckBox("打开编辑器"); self.cb_open.setChecked(True)
        l = QVBoxLayout()
        l.addWidget(QLabel("快捷方式："))
        l.addWidget(self.cb_desktop); l.addWidget(self.cb_menu)
        l.addWidget(QLabel("安装完成后："))
        l.addWidget(self.cb_open)
        self.setLayout(l)

class Page4(QWizardPage):
    def __init__(self, wizard):
        super().__init__(); self.w = wizard
        self.setTitle("正在安装")
        self.bar = QProgressBar(); self.label = QLabel("准备中...")
        l = QVBoxLayout(); l.addWidget(self.label); l.addWidget(self.bar); self.setLayout(l)
        self.setFinalPage(True)
    def setVisible(self, v):
        super().setVisible(v)
        if v and not getattr(self, "_started", False):
            self._started = True
            self.thread = InstallThread(self.w.edit.text(), self.w.cb_desktop.isChecked(), self.w.cb_menu.isChecked())
            self.thread.progress.connect(self.on_progress)
            self.thread.done.connect(self.on_done)
            self.thread.start()
    def on_progress(self, v, msg):
        self.bar.setValue(v); self.label.setText("正在安装: " + msg)
    def on_done(self, ok, msg):
        self.w.install_ok = ok
        if ok:
            self.w.installed_exe = os.path.join(self.w.edit.text(), APP + ".exe")
            self.label.setText("安装完成，点击「完成」结束")
        else:
            self.label.setText("安装失败: " + msg)

class Wizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP + " 安装向导")
        self.resize(560, 400)
        self.install_ok = False
        self.installed_exe = ""
        ico = os.path.join(res_dir(), "setup.ico")
        if os.path.exists(ico): self.setWindowIcon(QIcon(ico))
        self.p1 = Page1(); self.p2 = Page2(); self.p3 = Page3(); self.p4 = Page4(self)
        self.addPage(self.p1); self.addPage(self.p2); self.addPage(self.p3); self.addPage(self.p4)
        self.edit = self.p2.edit; self.cb_desktop = self.p3.cb_desktop
        self.cb_menu = self.p3.cb_menu; self.cb_open = self.p3.cb_open
    def accept(self):
        do_open = self.install_ok and self.cb_open.isChecked() and os.path.exists(self.installed_exe)
        exe = self.installed_exe
        super().accept()
        if do_open:
            try:
                subprocess.Popen([exe], cwd=os.path.dirname(exe))
            except Exception: pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ico = os.path.join(res_dir(), "setup.ico")
    if os.path.exists(ico): app.setWindowIcon(QIcon(ico))
    w = Wizard(); w.show()
    sys.exit(app.exec_())
'''
    path = os.path.join(ROOT, "安装程序", "installer_src.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
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
