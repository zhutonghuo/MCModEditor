import os
import json
import tempfile
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QLabel, QStackedWidget, QToolBar, QMenuBar, QMenu, QAction, QFileDialog,
    QMessageBox, QInputDialog, QSplitter, QStatusBar, QLineEdit, QProgressDialog,
    QApplication,
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from core.project import Project
from core import exporter, updater
from core.version import APP_VERSION, VERSION_CODE
from ui import icons, theme as theme_mod
from ui.model_editor import ModelEditor
from ui.animation_editor import AnimationEditor
from ui.inventory_editor import InventoryEditor
from ui.block_editor import BlockEditor
from ui.command_editor import CommandEditor
from ui.ui_editor import UIEditor

WORKSHOPS = [
    ("model", "模型工坊", "堆砌体素，雕刻物品外形"),
    ("animation", "动画工坊", "关键帧让模型动起来"),
    ("inventory", "物品栏工坊", "名称·描述·堆叠·稀有度"),
    ("blocks", "积木编程", "拖拽积木生成行为逻辑"),
    ("command", "命令工坊", "可视化拼装 MC 命令"),
    ("ui", "UI 工坊", "拖拽设计用户界面"),
]


class CheckThread(QThread):
    """后台拉取服务器版本清单。"""
    result = pyqtSignal(object)
    error = pyqtSignal(str)

    def run(self):
        try:
            self.result.emit(updater.fetch_version())
        except Exception as exc:
            self.error.emit(str(exc))


class DownloadThread(QThread):
    """后台下载更新包并校验 SHA1。"""
    progress = pyqtSignal(int)
    done = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, dest, sha1=""):
        super().__init__()
        self.url, self.dest, self.sha1 = url, dest, sha1

    def run(self):
        try:
            def cb(done, total):
                if total > 0:
                    self.progress.emit(int(done * 100 / total))
            updater.download_package(self.url, self.dest, cb)
            if self.sha1 and not updater.verify(self.dest, self.sha1):
                raise ValueError("更新包校验失败（SHA1 不匹配），已放弃安装")
            self.done.emit(self.dest)
        except Exception as exc:
            self.error.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project = Project.demo()
        self.dirty = False
        self._updating = False
        self.setWindowTitle("MC模组编辑器 — 我的世界模组创作工坊")
        self.resize(1180, 760)
        self._build()
        self.apply_theme()
        self.refresh_all()

    def _build(self):
        self.setMenuBar(self.build_menu())
        self.build_toolbar()

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        nav = QWidget()
        nav.setFixedWidth(210)
        nv = QVBoxLayout(nav)
        nv.setContentsMargins(10, 10, 10, 10)

        nv.addWidget(QLabel("工坊导航"))
        self.nav_list = QListWidget()
        for key, name, desc in WORKSHOPS:
            self.nav_list.addItem(name)
        self.nav_list.setFixedHeight(190)
        self.nav_list.currentRowChanged.connect(self.switch_workshop)
        nv.addWidget(self.nav_list)

        nv.addWidget(QLabel("物品清单"))
        self.item_list = QListWidget()
        self.item_list.itemClicked.connect(self.on_item)
        nv.addWidget(self.item_list)
        ibar = QHBoxLayout()
        badd = QPushButton(); badd.setIcon(icons.get("add", 22)); badd.clicked.connect(self.add_item); badd.setToolTip("新建物品")
        bdel = QPushButton(); bdel.setIcon(icons.get("delete", 22)); bdel.clicked.connect(self.del_item); bdel.setToolTip("删除物品")
        ibar.addWidget(badd); ibar.addWidget(bdel)
        nv.addLayout(ibar)
        root.addWidget(nav)

        self.stack = QStackedWidget()
        self.editors = {
            "model": ModelEditor(self),
            "animation": AnimationEditor(self),
            "inventory": InventoryEditor(self),
            "blocks": BlockEditor(self),
            "command": CommandEditor(self),
            "ui": UIEditor(self),
        }
        for key, _, _ in WORKSHOPS:
            self.stack.addWidget(self.editors[key])
        root.addWidget(self.stack)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("就绪 · 欢迎来到 MC模组编辑器")

        self.scene = None
        self.nav_list.setCurrentRow(0)

    def build_menu(self):
        mb = QMenuBar()
        mfile = mb.addMenu("文件")
        mfile.addAction(icons.get("new", 20), "新建工程", self.new_project)
        mfile.addAction(icons.get("open", 20), "打开工程", self.open_project)
        mfile.addAction(icons.get("save", 20), "保存工程", self.save_project)
        mfile.addSeparator()
        mfile.addAction("演示工程", self.load_demo)
        mfile.addSeparator()
        mfile.addAction(icons.get("export", 20), "导出全部", self.export_all)
        mfile.addAction("退出", self.close)

        medit = mb.addMenu("编辑")
        medit.addAction("添加物品", self.add_item)
        medit.addAction("重命名物品", self.rename_item)
        medit.addAction("删除物品", self.del_item)

        mview = mb.addMenu("视图")
        mview.addAction("切换明暗主题", self.toggle_theme)

        mhelp = mb.addMenu("帮助")
        mhelp.addAction(icons.get("update", 20), "检查更新...", self.check_update)
        mhelp.addAction("关于", self.about)
        return mb

    def build_toolbar(self):
        tb = QToolBar("主工具栏")
        tb.setIconSize(QSize(22, 22))
        tb.setMovable(False)
        for text, ic, fn in [
            ("新建", "new", self.new_project), ("打开", "open", self.open_project),
            ("保存", "save", self.save_project), ("导出", "export", self.export_all),
        ]:
            act = QAction(icons.get(ic, 22), text, self); act.triggered.connect(fn); tb.addAction(act)
        tb.addSeparator()
        for key, name, _ in WORKSHOPS:
            act = QAction(icons.get(key, 22), name, self)
            act.triggered.connect(lambda checked=False, k=key: self.goto(k))
            tb.addAction(act)
        tb.addSeparator()
        act = QAction(icons.get("theme", 22), "主题", self); act.triggered.connect(self.toggle_theme); tb.addAction(act)
        act = QAction(icons.get("update", 22), "检查更新", self); act.triggered.connect(self.check_update)
        act.setToolTip("检查服务器上的新版本并自动更新"); tb.addAction(act)
        self.addToolBar(tb)

    def goto(self, key):
        for i, (k, _, _) in enumerate(WORKSHOPS):
            if k == key:
                self.nav_list.setCurrentRow(i); break

    def switch_workshop(self, row):
        if row < 0: return
        self.save_current_canvas()
        self.stack.setCurrentIndex(row)
        self.refresh_current()

    def current_item(self):
        row = self.item_list.currentRow()
        return self.project.current_item(row)

    def on_item(self, item, prev=None):
        self.save_current_canvas()
        self.refresh_all_editors()

    def add_item(self):
        name, ok = QInputDialog.getText(self, "新建物品", "物品名称:", text=f"我的物品 {len(self.project.items)+1}")
        if not ok or not name: return
        iid = "".join(c if c.isalnum() or c == "_" else "_" for c in name).lower()
        self.project.add_item(iid, name)
        self.mark_dirty()
        self.refresh_all()
        self.item_list.setCurrentRow(len(self.project.items) - 1)

    def del_item(self):
        row = self.item_list.currentRow()
        if row < 0: return
        if QMessageBox.question(self, "确认", "删除该物品？") == QMessageBox.Yes:
            self.project.items.pop(row)
            self.mark_dirty(); self.refresh_all()

    def rename_item(self):
        item = self.current_item()
        if not item: return
        name, ok = QInputDialog.getText(self, "重命名", "物品名称:", text=item.name)
        if ok and name:
            item.name = name; self.mark_dirty(); self.refresh_item_list(); self.refresh_all_editors()

    def mark_dirty(self):
        self.dirty = True
        self.setWindowTitle("MC模组编辑器 * " + self.project.name)

    def save_current_canvas(self):
        try:
            be = self.editors.get("blocks")
            if be and self.stack.indexOf(be) == self.stack.currentIndex():
                be.save_scene()
        except Exception:
            pass

    def refresh_current(self):
        key = WORKSHOPS[self.stack.currentIndex()][0]
        self.editors[key].refresh()

    def refresh_all_editors(self):
        item = self.current_item()
        if not item:
            for e in self.editors.values():
                if hasattr(e, "refresh"): e.refresh()
            return
        for key in ["model", "animation", "inventory", "command", "ui", "blocks"]:
            self.editors[key].refresh()

    def refresh_item_list(self):
        self.item_list.clear()
        for it in self.project.items:
            self.item_list.addItem(f"{it.name}  [{it.id}]")
        if self.project.items and self.item_list.currentRow() < 0:
            self.item_list.setCurrentRow(0)

    def refresh_all(self):
        self.refresh_item_list()
        self.refresh_all_editors()

    def new_project(self):
        if self.dirty and QMessageBox.question(self, "未保存", "当前工程有未保存的更改，仍要新建？") != QMessageBox.Yes:
            return
        self.project = Project()
        self.dirty = False
        self.refresh_all()
        self.setWindowTitle("MC模组编辑器 — " + self.project.name)

    def load_demo(self):
        self.project = Project.demo()
        self.dirty = False
        self.refresh_all()
        self.statusBar().showMessage("已载入演示工程")

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开工程", "", "模组工程 (*.mcme *.json)")
        if not path: return
        try:
            self.save_current_canvas()
            self.project = Project.load(path)
            self.dirty = False
            self.refresh_all()
            self.statusBar().showMessage(f"已打开: {path}")
        except Exception as ex:
            QMessageBox.critical(self, "打开失败", str(ex))

    def save_project(self):
        path = self.project.path
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "保存工程", self.project.name + ".mcme", "模组工程 (*.mcme)")
        if not path: return
        try:
            self.save_current_canvas()
            self.project.save(path)
            self.dirty = False
            self.setWindowTitle("MC模组编辑器 — " + self.project.name)
            self.statusBar().showMessage(f"已保存: {path}")
        except Exception as ex:
            QMessageBox.critical(self, "保存失败", str(ex))

    def export_all(self):
        path = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not path: return
        try:
            self.save_current_canvas()
            dirs = exporter.export_all(self.project, path)
            names = "\n".join("  • " + os.path.basename(d) for d in dirs)
            QMessageBox.information(self, "导出完成", f"已导出到 {path}:\n{names}")
            self.statusBar().showMessage("导出成功")
        except Exception as ex:
            QMessageBox.critical(self, "导出失败", str(ex))

    def apply_theme(self):
        self.setStyleSheet(theme_mod.qss())

    def toggle_theme(self):
        cur = "dark" if theme_mod.CURRENT == "light" else "light"
        theme_mod.set_theme(cur)
        self.apply_theme()
        icons.clear_cache()
        for e in self.editors.values():
            if hasattr(e, "refresh"):
                try: e.refresh()
                except Exception: pass
        self.statusBar().showMessage("已切换到" + ("暗色" if cur == "dark" else "亮色") + "主题")

    # ---------- 自动更新 ----------
    def check_update(self):
        self.statusBar().showMessage("正在检查更新...")
        self._wait = QProgressDialog("正在连接更新服务器...", "", 0, 0, self)
        self._wait.setWindowTitle("检查更新")
        self._wait.setCancelButton(None)
        self._wait.setModal(True)
        self._wait.show()
        QApplication.processEvents()
        self._check = CheckThread(self)
        self._check.result.connect(self.on_check_result)
        self._check.error.connect(self.on_check_error)
        self._check.start()

    def on_check_error(self, msg):
        if hasattr(self, "_wait"):
            self._wait.close()
        self.statusBar().showMessage("检查更新失败")
        QMessageBox.warning(self, "检查更新失败",
            "无法连接更新服务器，请检查网络后重试。\n\n" + msg[:200])

    def on_check_result(self, info):
        if hasattr(self, "_wait"):
            self._wait.close()
        try:
            new_code = updater.code_of(info.get("version_code"))
            new_ver = info.get("version", "?")
            if new_code <= VERSION_CODE:
                self.statusBar().showMessage(f"已是最新版本 v{APP_VERSION}")
                QMessageBox.information(self, "检查更新",
                    f"当前已是最新版本 v{APP_VERSION}。\n\n无需更新。")
                return
            changes = info.get("changelog", "")
            if isinstance(changes, list):
                changes = "\n".join("  • " + str(c) for c in changes)
            size = updater.human_size(info.get("package_size", 0))
            date = info.get("date", "")
            text = (f"发现新版本 v{new_ver}"
                    + (f"（{date}）" if date else "") + "\n\n"
                    + (f"更新内容：\n{changes}\n\n" if changes else "")
                    + f"更新包大小：{size}\n\n"
                    + "是否立即下载并安装？\n"
                    + "安装过程不会卸载现有程序，也不会删除你的工程文件。")
            reply = QMessageBox.question(self, "发现新版本", text,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.start_download(info)
            else:
                self.statusBar().showMessage(f"发现新版本 v{new_ver}（已跳过）")
        except Exception as exc:
            QMessageBox.critical(self, "检查更新失败", str(exc))

    def start_download(self, info):
        url = info.get("package_url", "")
        if not url:
            QMessageBox.critical(self, "更新失败", "版本清单缺少更新包地址。")
            return
        dest = os.path.join(tempfile.gettempdir(),
                            f"mcme_update_{info.get('version_code', 'x')}.zip")
        self._dlg = QProgressDialog("正在下载更新包...", "取消", 0, 100, self)
        self._dlg.setWindowTitle("下载更新")
        self._dlg.setModal(True)
        self._dlg.setMinimumDuration(0)
        self._dlg.setValue(0)
        self._dlg.canceled.connect(self.on_download_canceled)
        self._dlg.show()
        self._dl = DownloadThread(url, dest, info.get("sha1", ""))
        self._dl.progress.connect(self._dlg.setValue)
        self._dl.done.connect(self.on_download_done)
        self._dl.error.connect(self.on_download_error)
        self._dl.start()

    def on_download_canceled(self):
        if hasattr(self, "_dl") and self._dl.isRunning():
            self._dl.terminate()
        self.statusBar().showMessage("已取消更新")

    def on_download_error(self, msg):
        if hasattr(self, "_dlg"):
            self._dlg.close()
        QMessageBox.critical(self, "下载失败", "更新包下载失败：\n\n" + msg[:300])

    def on_download_done(self, path):
        if hasattr(self, "_dlg"):
            self._dlg.close()
        # 提示后退出：覆盖器会在本进程退出后替换文件并自动重启
        msg = QMessageBox.information(
            self, "准备安装",
            "更新包已下载并校验完成。\n\n"
            "点击「确定」后程序将退出，并在后台自动完成安装与重启。\n"
            "整个过程不会卸载程序，也不会删除你的工程文件。")
        QApplication.processEvents()
        ok, _ = updater.schedule_apply(path)
        if not ok:
            QMessageBox.critical(self, "安装失败", "无法启动更新程序，请手动下载安装程序覆盖更新。")
            return
        # 保存工程提示：若未保存给用户最后机会
        if self.dirty:
            if QMessageBox.question(self, "未保存的更改",
                    "当前工程有未保存的更改，更新会保留程序但不会保存工程。\n仍要继续更新吗？",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
                return
        self._updating = True
        self.close()
        QApplication.quit()

    def about(self):
        QMessageBox.about(self, "关于 MC模组编辑器",
            f"MC模组编辑器 v{APP_VERSION}\n\n一个用于创作我的世界模组的图形化工坊：\n"
            "模型 · 动画 · 物品栏外观 · 积木编程 · 命令 · 界面\n\n"
            "导出资源包 / 数据包 / 界面 JSON，可直接放入 Minecraft 使用。")

    def closeEvent(self, e):
        if getattr(self, "_updating", False):
            e.accept()
            return
        if self.dirty and QMessageBox.question(self, "未保存", "工程有未保存的更改，确定退出？") != QMessageBox.Yes:
            e.ignore()
        else:
            e.accept()
