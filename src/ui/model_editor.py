from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel,
    QLineEdit, QSpinBox, QComboBox, QColorDialog, QListWidget, QGroupBox,
    QSplitter, QMessageBox, QCheckBox,
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from ui.voxel_view import VoxelView
from ui import icons
from ui.theme import theme


class ModelEditor(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.color = "#8b5cf6"
        self.part = "main"
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        tools = QGroupBox("方块工具")
        tl = QVBoxLayout(tools)
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.setIcon(icons.get("settings", 20))
        self.color_btn.clicked.connect(self.pick_color)
        tl.addWidget(self.color_btn)
        self.color_swatch = QLabel("    ")
        self.color_swatch.setStyleSheet(f"background:{self.color}; border:1px solid #ccc; border-radius:4px;")
        self.color_swatch.setFixedHeight(28)
        tl.addWidget(self.color_swatch)

        tl.addWidget(QLabel("坐标 X / Y / Z"))
        coord = QHBoxLayout()
        self.sx = QSpinBox(); self.sy = QSpinBox(); self.sz = QSpinBox()
        for s in (self.sx, self.sy, self.sz):
            s.setRange(-16, 16); s.setFixedWidth(58)
        coord.addWidget(self.sx); coord.addWidget(self.sy); coord.addWidget(self.sz)
        tl.addLayout(coord)

        bAdd = QPushButton("添加方块"); bAdd.setIcon(icons.get("add", 20))
        bAdd.clicked.connect(self.add_voxel)
        bDel = QPushButton("删除该位置"); bDel.setIcon(icons.get("delete", 20))
        bDel.clicked.connect(self.del_voxel)
        tl.addWidget(bAdd); tl.addWidget(bDel)

        tl.addWidget(QLabel("所属部件"))
        self.part_combo = QComboBox(); self.part_combo.setEditable(True)
        self.part_combo.addItems(["main"])
        self.part_combo.currentTextChanged.connect(self.on_part)
        tl.addWidget(self.part_combo)

        tl.addWidget(QLabel("快速形状"))
        grid = QGridLayout()
        for i, (label, fn) in enumerate([
            ("剑刃", self.shape_sword), ("人形", self.shape_human),
            ("立方", self.shape_cube), ("十字", self.shape_cross),
        ]):
            b = QPushButton(label); b.clicked.connect(fn)
            grid.addWidget(b, i // 2, i % 2)
        tl.addLayout(grid)
        tl.addStretch()

        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        self.view = VoxelView()
        cl.addWidget(self.view)
        hint = QLabel("拖拽旋转视角 · 体素实时预览")
        hint.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setItalic(True); hint.setFont(f)
        hint.setStyleSheet(f"color:{theme()['text_dim']};")
        cl.addWidget(hint)

        right = QGroupBox("体素列表")
        rl = QVBoxLayout(right)
        self.list = QListWidget()
        self.list.itemClicked.connect(self.select_voxel)
        rl.addWidget(self.list)
        bClear = QPushButton("清空模型"); bClear.setIcon(icons.get("trash", 20))
        bClear.clicked.connect(self.clear_model)
        rl.addWidget(bClear)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(tools); splitter.addWidget(center); splitter.addWidget(right)
        splitter.setStretchFactor(0, 0); splitter.setStretchFactor(1, 1); splitter.setStretchFactor(2, 0)
        splitter.setSizes([190, 420, 200])
        root.addWidget(splitter)

    def current_model(self):
        item = self.main.current_item()
        return item.model if item else None

    def refresh(self):
        model = self.current_model()
        if not model:
            self.view.set_data(None); self.list.clear(); return
        self.view.set_data(model, self.main.current_item().animation)
        parts = model.parts()
        cur = self.part_combo.currentText()
        self.part_combo.blockSignals(True)
        self.part_combo.clear(); self.part_combo.addItems(parts or ["main"])
        if cur in parts:
            self.part_combo.setCurrentText(cur)
        self.part_combo.blockSignals(False)
        self.part = self.part_combo.currentText() or "main"
        self.list.clear()
        for v in model.voxels:
            self.list.addItem(f"[{v['x']},{v['y']},{v['z']}] {v['part']} {v['color']}")

    def pick_color(self):
        c = QColorDialog.getColor(QColor(self.color), self, "选择方块颜色")
        if c.isValid():
            self.color = c.name()
            self.color_swatch.setStyleSheet(f"background:{self.color}; border:1px solid #ccc; border-radius:4px;")

    def on_part(self, text):
        self.part = text or "main"

    def add_voxel(self):
        model = self.current_model()
        if not model:
            QMessageBox.information(self, "提示", "请先添加一个物品"); return
        model.add(self.sx.value(), self.sy.value(), self.sz.value(), self.color, self.part)
        self.main.mark_dirty(); self.refresh()

    def del_voxel(self):
        model = self.current_model()
        if not model: return
        model.remove_at(self.sx.value(), self.sy.value(), self.sz.value())
        self.main.mark_dirty(); self.refresh()

    def select_voxel(self, item):
        txt = item.text()
        try:
            inside = txt.split("]")[0].strip("[")
            xs = inside.split(",")
            self.sx.setValue(int(xs[0])); self.sy.setValue(int(xs[1])); self.sz.setValue(int(xs[2]))
        except Exception:
            pass

    def clear_model(self):
        model = self.current_model()
        if not model: return
        if QMessageBox.question(self, "确认", "清空所有体素？") == QMessageBox.Yes:
            model.voxels = []
            self.main.mark_dirty(); self.refresh()

    def shape_sword(self):
        model = self.current_model()
        if not model: return
        model.voxels = []
        for y in range(4):
            model.add(0, y, 0, "#d8dde6", "blade")
        for x in (-1, 1):
            model.add(x, 3, 0, "#c9a227", "blade")
        model.add(0, -1, 0, "#6b4a2a", "handle")
        self.main.mark_dirty(); self.refresh()

    def shape_human(self):
        model = self.current_model()
        if not model: return
        model.voxels = []
        model.add(0, 3, 0, "#e0b89a", "head")
        for x in (-1, 0, 1):
            model.add(x, 2, 0, "#4a6cf7", "body")
        model.add(0, 1, 0, "#4a6cf7", "body")
        for x in (-1, 1):
            model.add(x, 0, 0, "#333a4a", "legs")
        self.main.mark_dirty(); self.refresh()

    def shape_cube(self):
        model = self.current_model()
        if not model: return
        model.voxels = []
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    model.add(x, y, z, self.color, "main")
        self.main.mark_dirty(); self.refresh()

    def shape_cross(self):
        model = self.current_model()
        if not model: return
        model.voxels = []
        for i in range(5):
            model.add(i - 2, i - 2, 0, self.color, "main")
            model.add(i - 2, 2 - i, 0, self.color, "main")
        self.main.mark_dirty(); self.refresh()
