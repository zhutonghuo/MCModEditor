from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QGroupBox, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QLineEdit, QLabel, QMessageBox,
    QSplitter, QComboBox,
)
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QPainterPath, QPolygonF, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from core.blocks import BLOCK_LIBRARY, block_info
from ui import icons
from ui.theme import theme


class BlockItem(QGraphicsItem):
    def __init__(self, op, args=None, block_id=None):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.op = op
        self.info = block_info(op)
        self.args = list(args or [""] * len(self.info.get("args", [])))
        self.block_id = block_id
        self.w = max(150, 46 + len(self.info["label"]) * 13)
        self.h = 34 + len(self.args) * 28
        self.edits = []
        self.rebuild()

    def rebuild(self):
        for ed in self.edits:
            if ed.scene(): ed.scene().removeItem(ed)
        self.edits = []
        self.prepareGeometryChange()
        f = QFont("Microsoft YaHei", 10, QFont.Bold)
        for i, arg in enumerate(self.args):
            ed = QLineEdit()
            ed.setText(str(arg))
            ed.setPlaceholderText(self.info.get("args", [])[i] if i < len(self.info.get("args", [])) else "值")
            ed.setStyleSheet("font-size:11px; padding:2px;")
            ed.textChanged.connect(lambda t, idx=i: self.on_arg(idx, t))
            proxy = self.scene().addWidget(ed) if self.scene() else None
            if proxy:
                proxy.setParentItem(self)
                proxy.setPos(12, 30 + i * 28)
                ed.setFixedSize(self.w - 24, 24)
                self.edits.append(proxy)

    def on_arg(self, idx, text):
        if idx < len(self.args):
            self.args[idx] = text

    def boundingRect(self):
        return QRectF(0, 0, self.w, self.h)

    def paint(self, p, option, widget=None):
        t = theme()
        col = QColor(self.info["color"])
        p.setRenderHint(QPainter.Antialiasing)
        shape = self.info.get("shape", "stack")
        path = QPainterPath()
        if shape == "hat":
            path.moveTo(0, 10); path.lineTo(14, 0); path.lineTo(self.w, 0)
            path.lineTo(self.w, self.h); path.lineTo(0, self.h); path.closeSubpath()
        elif shape == "if":
            path.moveTo(0, 6); path.lineTo(18, 6); path.lineTo(24, 0); path.lineTo(30, 6)
            path.lineTo(self.w - 18, 6); path.lineTo(self.w - 12, self.h); path.lineTo(self.w - 6, 6)
            path.lineTo(self.w, 6); path.lineTo(self.w, self.h - 6); path.lineTo(0, self.h - 6)
            path.closeSubpath()
        else:
            path.addRoundedRect(QRectF(0, 0, self.w, self.h), 6, 6)
        p.setBrush(QBrush(col.lighter(115) if self.isSelected() else col))
        p.setPen(QPen(col.darker(130), 1.5))
        p.drawPath(path)

        label_rect = QRectF(8, 4, self.w - 16, 24)
        f = QFont("Microsoft YaHei", 10, QFont.Bold)
        p.setFont(f)
        p.setPen(QPen(QColor("#ffffff")))
        p.drawText(label_rect, Qt.AlignVCenter | Qt.AlignLeft, self.info["label"])

    def to_data(self):
        return {"op": self.op, "args": self.args, "block_id": self.block_id}


class BlockEditor(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.scene_items = []
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        lib = QGroupBox("积木库 (双击添加)")
        ll = QVBoxLayout(lib)
        self.cat = QComboBox()
        self.cat.addItems(["全部", "事件", "条件", "动作"])
        self.cat.currentTextChanged.connect(self.filter_lib)
        ll.addWidget(self.cat)
        self.lib_list = QListWidget()
        self.lib_list.itemDoubleClicked.connect(self.add_from_lib)
        ll.addWidget(self.lib_list)

        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        bar = QHBoxLayout()
        badd = QPushButton("添加选中积木"); badd.setIcon(icons.get("add", 20)); badd.clicked.connect(self.add_selected)
        bdel = QPushButton("删除选中"); bdel.setIcon(icons.get("delete", 20)); bdel.clicked.connect(self.delete_selected)
        bgen = QPushButton("生成命令"); bgen.setIcon(icons.get("command", 20)); bgen.clicked.connect(self.gen_commands)
        bar.addWidget(badd); bar.addWidget(bdel); bar.addWidget(bgen)
        cl.addLayout(bar)
        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(QBrush(QColor(theme()["canvas"])))
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setMinimumHeight(360)
        cl.addWidget(self.view)

        right = QGroupBox("脚本")
        rl = QVBoxLayout(right)
        self.script_list = QListWidget()
        self.script_list.itemClicked.connect(self.load_script)
        rl.addWidget(self.script_list)
        bnew = QPushButton("新建脚本"); bnew.setIcon(icons.get("new", 20)); bnew.clicked.connect(self.new_script)
        bclear = QPushButton("清空画布"); bclear.setIcon(icons.get("trash", 20)); bclear.clicked.connect(self.clear_scene)
        rl.addWidget(bnew); rl.addWidget(bclear)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(lib); splitter.addWidget(center); splitter.addWidget(right)
        splitter.setStretchFactor(0, 0); splitter.setStretchFactor(1, 1); splitter.setStretchFactor(2, 0)
        splitter.setSizes([190, 460, 180])
        root.addWidget(splitter)
        self.filter_lib()

    def current_scripts(self):
        item = self.main.current_item()
        return item.scripts if item else []

    def current_script(self):
        scripts = self.current_scripts()
        row = self.script_list.currentRow()
        return scripts[row] if 0 <= row < len(scripts) else None

    def filter_lib(self):
        cat = self.cat.currentText()
        self.lib_list.clear()
        for b in BLOCK_LIBRARY:
            if cat == "全部" or b["cat"] == cat:
                self.lib_list.addItem(f"[{b['cat']}] {b['label']}")

    def add_from_lib(self, item):
        self.spawn_block(item.text().split(" ", 1)[1] if " " in item.text() else item.text(), None)

    def add_selected(self):
        row = self.lib_list.currentRow()
        if row < 0: return
        text = self.lib_list.item(row).text()
        label = text.split(" ", 1)[1]
        self.spawn_block(label, None)

    def spawn_block(self, label, args, block_id=None, op_hint=None):
        op = op_hint
        if not op:
            for b in BLOCK_LIBRARY:
                if b["label"] == label:
                    op = b["op"]; break
        if not op: return
        bi = block_info(op)
        block = BlockItem(op, args if args is not None else ["" for _ in bi.get("args", [])], block_id)
        x = 40 + (len(self.scene_items) % 4) * 190
        y = 40 + (len(self.scene_items) // 4) * 130
        block.setPos(x, y)
        self.scene.addItem(block)
        block.rebuild()
        self.scene_items.append(block)

    def delete_selected(self):
        for it in list(self.scene.selectedItems()):
            if it in self.scene_items:
                for ed in it.edits:
                    if ed.scene(): ed.scene().removeItem(ed)
                self.scene.removeItem(it)
                self.scene_items.remove(it)

    def clear_scene(self):
        for it in self.scene_items:
            for ed in it.edits:
                if ed.scene(): ed.scene().removeItem(ed)
            self.scene.removeItem(it)
        self.scene_items = []

    def save_scene(self):
        script = self.current_script()
        if not script: return
        script.blocks = []
        for it in self.scene_items:
            d = it.to_data()
            script.blocks.append(d)
        self.main.mark_dirty()

    def refresh(self):
        item = self.main.current_item()
        self.script_list.clear()
        if item:
            for s in item.scripts:
                self.script_list.addItem(s.name)
        self.clear_scene()

    def load_script(self, item):
        self.clear_scene()
        script = self.current_script()
        if not script: return
        for b in script.blocks:
            self.spawn_block(b.get("label", ""), b.get("args", []), b.get("id"), op_hint=b.get("op"))

    def new_script(self, checked=False):
        item = self.main.current_item()
        if not item: return
        from core.blocks import BlockProgram
        s = BlockProgram(f"脚本 {len(item.scripts)+1}")
        item.scripts.append(s)
        self.main.mark_dirty()
        self.refresh()
        self.script_list.setCurrentRow(len(item.scripts) - 1)

    def gen_commands(self):
        self.save_scene()
        script = self.current_script()
        if not script:
            QMessageBox.information(self, "提示", "请先新建或选择一个脚本"); return
        lines = script.to_commands()
        dlg = QMessageBox(self)
        dlg.setWindowTitle("生成的 Minecraft 命令")
        dlg.setText("\n".join(lines) if lines else "（暂无可生成的命令）")
        dlg.exec_()
