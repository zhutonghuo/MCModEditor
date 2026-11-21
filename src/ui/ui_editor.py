import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QGroupBox, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QLineEdit, QSpinBox,
    QLabel, QMessageBox, QSplitter, QFormLayout, QColorDialog, QComboBox,
)
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QPainter
from PyQt5.QtCore import Qt, QRectF
from ui import icons
from ui.theme import theme

WIDGETS = [
    {"type": "button", "label": "按钮", "w": 120, "h": 36, "color": "#4a6cf7"},
    {"type": "label", "label": "文本", "w": 140, "h": 28, "color": "#8b5cf6"},
    {"type": "input", "label": "输入框", "w": 160, "h": 32, "color": "#2fa871"},
    {"type": "panel", "label": "面板", "w": 200, "h": 140, "color": "#e8912d"},
    {"type": "image", "label": "图片框", "w": 96, "h": 96, "color": "#e05555"},
    {"type": "checkbox", "label": "复选框", "w": 110, "h": 26, "color": "#5b8def"},
]


class UIElement(QGraphicsItem):
    def __init__(self, wtype, label, w, h, color):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.wtype = wtype
        self.label = label
        self.w = w
        self.h = h
        self.color = color
        self.text = label

    def boundingRect(self):
        return QRectF(0, 0, self.w, self.h)

    def paint(self, p, option, widget=None):
        p.setRenderHint(QPainter.Antialiasing)
        col = QColor(self.color)
        p.setBrush(QBrush(col.lighter(160)))
        p.setPen(QPen(col.darker(120), 2 if self.isSelected() else 1))
        if self.wtype == "panel":
            p.drawRoundedRect(self.boundingRect(), 8, 8)
        elif self.wtype == "image":
            p.drawRect(self.boundingRect())
            p.setPen(QPen(col, 1))
            p.drawLine(0, 0, self.w, self.h); p.drawLine(self.w, 0, 0, self.h)
        elif self.wtype == "checkbox":
            p.drawRect(0, 0, 18, 18)
            p.setPen(QPen(QColor("#1c2333")))
            f = QFont("Microsoft YaHei", 10); p.setFont(f)
            p.drawText(26, 14, self.text)
            return
        else:
            p.drawRoundedRect(self.boundingRect(), 5, 5)
        p.setPen(QPen(QColor("#1c2333")))
        f = QFont("Microsoft YaHei", 10, QFont.Bold); p.setFont(f)
        p.drawText(self.boundingRect(), Qt.AlignCenter, self.text)

    def to_dict(self):
        return {
            "type": self.wtype, "text": self.text, "color": self.color,
            "w": self.w, "h": self.h,
            "x": int(self.pos().x()), "y": int(self.pos().y()),
        }


class UIEditor(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.elements = []
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        lib = QGroupBox("控件库 (双击添加)")
        ll = QVBoxLayout(lib)
        self.lib_list = QListWidget(); self.lib_list.itemDoubleClicked.connect(self.add_widget)
        for w in WIDGETS:
            self.lib_list.addItem(w["label"])
        ll.addWidget(self.lib_list)

        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        bar = QHBoxLayout()
        bdel = QPushButton("删除选中"); bdel.setIcon(icons.get("delete", 20)); bdel.clicked.connect(self.delete_selected)
        bexp = QPushButton("导出界面 JSON"); bexp.setIcon(icons.get("export", 20)); bexp.clicked.connect(self.export_ui)
        bar.addWidget(bdel); bar.addWidget(bexp)
        cl.addLayout(bar)
        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(QBrush(QColor(theme()["panel"])))
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setMinimumHeight(380)
        cl.addWidget(self.view)

        prop = QGroupBox("属性")
        pl = QFormLayout(prop)
        self.e_text = QLineEdit(); self.e_text.textChanged.connect(self.apply_prop)
        self.s_w = QSpinBox(); self.s_w.setRange(20, 800); self.s_w.valueChanged.connect(self.apply_prop)
        self.s_h = QSpinBox(); self.s_h.setRange(20, 600); self.s_h.valueChanged.connect(self.apply_prop)
        self.btn_color = QPushButton("选择颜色"); self.btn_color.clicked.connect(self.pick_color)
        pl.addRow("文本:", self.e_text)
        pl.addRow("宽:", self.s_w)
        pl.addRow("高:", self.s_h)
        pl.addRow("", self.btn_color)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(lib); splitter.addWidget(center); splitter.addWidget(prop)
        splitter.setStretchFactor(0, 0); splitter.setStretchFactor(1, 1); splitter.setStretchFactor(2, 0)
        splitter.setSizes([150, 480, 190])
        root.addWidget(splitter)

    def selected(self):
        sel = self.scene.selectedItems()
        return sel[0] if sel else None

    def add_widget(self, item):
        label = item.text()
        spec = next((w for w in WIDGETS if w["label"] == label), None)
        if not spec: return
        el = UIElement(spec["type"], spec["label"], spec["w"], spec["h"], spec["color"])
        x = 40 + (len(self.elements) % 5) * 130
        y = 40 + (len(self.elements) // 5) * 100
        el.setPos(x, y)
        self.scene.addItem(el)
        self.elements.append(el)
        self.mark()

    def delete_selected(self):
        el = self.selected()
        if el and el in self.elements:
            self.scene.removeItem(el); self.elements.remove(el); self.mark()

    def pick_color(self):
        el = self.selected()
        if not el: return
        c = QColorDialog.getColor(QColor(el.color), self)
        if c.isValid():
            el.color = c.name(); el.update(); self.mark()

    def apply_prop(self):
        el = self.selected()
        if not el: return
        el.text = self.e_text.text()
        el.w = self.s_w.value(); el.h = self.s_h.value()
        el.prepareGeometryChange()
        el.update(); self.mark()

    def on_select(self):
        el = self.selected()
        if not el: return
        self.e_text.blockSignals(True); self.s_w.blockSignals(True); self.s_h.blockSignals(True)
        self.e_text.setText(el.text); self.s_w.setValue(el.w); self.s_h.setValue(el.h)
        self.e_text.blockSignals(False); self.s_w.blockSignals(False); self.s_h.blockSignals(False)

    def mark(self):
        self.main.mark_dirty()

    def refresh(self):
        for el in self.elements:
            if el.scene(): el.scene().removeItem(el)
        self.elements = []

    def export_ui(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "导出界面", "ui_layout.json", "JSON (*.json)")
        if not path: return
        data = {"elements": [el.to_dict() for el in self.elements]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "完成", f"界面已导出到:\n{path}")
