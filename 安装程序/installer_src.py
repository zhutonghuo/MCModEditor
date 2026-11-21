
import os, sys, shutil, subprocess, winreg
from PyQt5.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
import win32com.client
from win32com.shell import shell, shellcon

APP = "MC模组编辑器"
VER = "1.0"
VERSION_FILE = "version.txt"


def res_dir():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "_res")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "_res")


def payload_dir():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "_payload")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "_payload")


def read_version(folder):
    """读取已安装版本；优先版本文件，其次 exe 文件属性。"""
    vf = os.path.join(folder, VERSION_FILE)
    try:
        if os.path.exists(vf):
            with open(vf, encoding="utf-8") as f:
                return f.read().strip()
    except Exception:
        pass
    exe = os.path.join(folder, APP + ".exe")
    try:
        import win32api
        info = win32api.GetFileVersionInfo(exe, "\\")
        ms = info["FileVersionMS"]
        return f"{(ms >> 16) & 0xFFFF}.{(ms) & 0xFFFF}"
    except Exception:
        return ""


def _is_installed(folder):
    return os.path.isfile(os.path.join(folder, APP + ".exe"))


def detect_existing():
    """扫描注册表 / 常见目录 / 快捷方式，返回已安装目录（或 None）。"""
    candidates = []

    # 1) 注册表卸载项
    try:
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for sub in (r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
                        r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"):
                try:
                    key = winreg.OpenKey(hive, sub)
                except Exception:
                    continue
                i = 0
                while True:
                    try:
                        name = winreg.EnumKey(key, i); i += 1
                    except OSError:
                        break
                    try:
                        sk = winreg.OpenKey(key, name)
                        disp = ""
                        try:
                            disp = winreg.QueryValueEx(sk, "DisplayName")[0]
                        except Exception:
                            pass
                        if APP in str(disp):
                            try:
                                loc = winreg.QueryValueEx(sk, "InstallLocation")[0]
                                if loc:
                                    candidates.append(loc)
                            except Exception:
                                pass
                        winreg.CloseKey(sk)
                    except Exception:
                        pass
                winreg.CloseKey(key)
    except Exception:
        pass

    # 2) 常见安装目录
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"),
                 os.environ.get("LOCALAPPDATA"), os.environ.get("ProgramData")):
        if base:
            candidates.append(os.path.join(base, APP))

    # 3) 快捷方式目标
    try:
        sh = win32com.client.Dispatch("WScript.Shell")
        dirs = []
        try:
            dirs.append(shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0))
        except Exception:
            pass
        try:
            dirs.append(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0))
            dirs.append(os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0), APP))
        except Exception:
            pass
        for d in dirs:
            if not d or not os.path.isdir(d):
                continue
            try:
                for fn in os.listdir(d):
                    if fn.lower().endswith(".lnk") and APP in fn:
                        try:
                            s = sh.CreateShortCut(os.path.join(d, fn))
                            tp = getattr(s, "TargetPath", "")
                            wd = getattr(s, "WorkingDirectory", "")
                            if tp:
                                candidates.append(os.path.dirname(tp))
                            if wd:
                                candidates.append(wd)
                        except Exception:
                            pass
            except Exception:
                pass
    except Exception:
        pass

    # 去重并校验
    seen = set()
    for c in candidates:
        c = os.path.normpath(c)
        key = c.lower()
        if key in seen:
            continue
        seen.add(key)
        if _is_installed(c):
            return c
    return None


class InstallThread(QThread):
    progress = pyqtSignal(int, str)
    done = pyqtSignal(bool, str)

    def __init__(self, target, desktop, startmenu):
        super().__init__()
        self.target = target
        self.desktop = desktop
        self.startmenu = startmenu

    def run(self):
        try:
            os.makedirs(self.target, exist_ok=True)
            payload = payload_dir()
            files = []
            for root, dirs, fs in os.walk(payload):
                for f in fs:
                    files.append(os.path.join(root, f))
            total = len(files)
            for i, f in enumerate(files):
                rel = os.path.relpath(f, payload)
                dst = os.path.join(self.target, rel)
                # 覆盖同名文件，但保留目标目录里不属于安装包的文件（如工程文件）
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(f, dst)
                self.progress.emit(int((i + 1) / total * 100), rel)
            # 写入版本标记，供下次覆盖更新检测
            try:
                with open(os.path.join(self.target, VERSION_FILE), "w", encoding="utf-8") as vf:
                    vf.write(VER)
            except Exception:
                pass
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
            except Exception:
                pass
        if self.startmenu:
            try:
                sm = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0), APP)
                os.makedirs(sm, exist_ok=True)
                targets.append(os.path.join(sm, APP + ".lnk"))
            except Exception:
                pass
        ico = os.path.join(res_dir(), "setup.ico")
        for lnk in targets:
            try:
                s = sh.CreateShortCut(lnk)
                s.TargetPath = exe
                s.WorkingDirectory = os.path.dirname(exe)
                s.Description = APP + " - 我的世界模组创作工坊"
                if os.path.exists(ico):
                    s.IconLocation = ico + ",0"
                s.save()
            except Exception:
                pass


class Page1(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.w = wizard
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
        if self.w.existing_dir:
            note = QLabel("✓ 检测到已安装版本 v" + (self.w.existing_ver or "?")
                          + "\n　位于：" + self.w.existing_dir
                          + "\n　下一步将自动覆盖更新（不卸载、保留工程文件）。")
            note.setStyleSheet("color:#0a7;" )
            l.addWidget(note)
        else:
            l.addWidget(QLabel("未检测到已有安装，将进行全新安装。"))
        l.addWidget(QLabel("本向导将安装："))
        for t in ["模型 / 动画 / 物品栏 / 积木编程 / 命令 / UI 六大工坊",
                  "桌面与开始菜单快捷方式", "完整的离线运行环境"]:
            l.addWidget(QLabel("  * " + t))
        self.setLayout(l)


class Page2(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.w = wizard
        self.setTitle("选择安装位置")
        default = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), APP)
        if self.w.existing_dir:
            default = self.w.existing_dir
        self.edit = QLineEdit(default)
        l = QVBoxLayout()
        l.addWidget(QLabel("安装目录："))
        h = QHBoxLayout(); h.addWidget(self.edit)
        b = QPushButton("浏览..."); b.clicked.connect(self.browse); h.addWidget(b)
        l.addLayout(h)
        if self.w.existing_dir:
            tip = QLabel("检测到已安装版本，已为你定位到现有目录，继续即覆盖更新。\n"
                         "如需安装到其他文件夹做全新安装，请点「浏览」选择另一个目录。")
            tip.setWordWrap(True)
            tip.setStyleSheet("color:#0a7;")
            l.addWidget(tip)
            # 一键恢复为已装目录
            btn = QPushButton("恢复为已安装目录")
            btn.clicked.connect(lambda: self.edit.setText(self.w.existing_dir))
            l.addWidget(btn)
        self.setLayout(l)

    def browse(self):
        d = QFileDialog.getExistingDirectory(self, "选择目录", self.edit.text())
        if d:
            self.edit.setText(os.path.join(d, APP))

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
            self.thread = InstallThread(self.w.edit.text(), self.w.cb_desktop.isChecked(),
                                        self.w.cb_menu.isChecked())
            self.thread.progress.connect(self.on_progress)
            self.thread.done.connect(self.on_done)
            self.thread.start()

    def on_progress(self, v, msg):
        self.bar.setValue(v); self.label.setText("正在安装: " + msg)

    def on_done(self, ok, msg):
        self.w.install_ok = ok
        if ok:
            self.w.installed_exe = os.path.join(self.w.edit.text(), APP + ".exe")
            mode = "覆盖更新" if self.w.existing_dir and os.path.normcase(
                self.w.edit.text()) == os.path.normcase(self.w.existing_dir) else "安装"
            self.label.setText(mode + "完成，点击「完成」结束")
        else:
            self.label.setText("安装失败: " + msg)


class Wizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP + " 安装向导")
        self.resize(600, 430)
        self.install_ok = False
        self.installed_exe = ""
        self.existing_dir = detect_existing()
        self.existing_ver = read_version(self.existing_dir) if self.existing_dir else ""
        ico = os.path.join(res_dir(), "setup.ico")
        if os.path.exists(ico):
            self.setWindowIcon(QIcon(ico))
        self.p1 = Page1(self); self.p2 = Page2(self); self.p3 = Page3(); self.p4 = Page4(self)
        self.addPage(self.p1); self.addPage(self.p2); self.addPage(self.p3); self.addPage(self.p4)
        self.edit = self.p2.edit
        self.cb_desktop = self.p3.cb_desktop
        self.cb_menu = self.p3.cb_menu
        self.cb_open = self.p3.cb_open

    def accept(self):
        do_open = self.install_ok and self.cb_open.isChecked() and os.path.exists(self.installed_exe)
        exe = self.installed_exe
        super().accept()
        if do_open:
            try:
                subprocess.Popen([exe], cwd=os.path.dirname(exe))
            except Exception:
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ico = os.path.join(res_dir(), "setup.ico")
    if os.path.exists(ico):
        app.setWindowIcon(QIcon(ico))
    w = Wizard(); w.show()
    sys.exit(app.exec_())
