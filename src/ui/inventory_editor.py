from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QSpinBox,
    QComboBox, QCheckBox, QTextEdit, QGroupBox, QLabel,
)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt5.QtCore import Qt
from ui.theme import theme
from ui.voxel_view import VoxelView

RARITY_COLORS = {
    "common": "#ffffff", "uncommon": "#55ff55", "rare": "#5555ff",
    "epic": "#aa00aa", "legendary": "#ffaa00",
}


class SlotPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.item = None
        self.view = VoxelView()
        self.setFixedSize(180, 200)

    def set_item(self, item):
        self.item = item
        if item:
            self.view.set_data(item.model, item.animation)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(theme()["panel"]))
        t = theme()
        slot = self.rect().adjusted(24, 16, -24, -44)
        p.setBrush(QBrush(QColor(t["panel_alt"])))
        p.setPen(QPen(QColor(t["border"]), 2))
        p.drawRect(slot)
        p.setPen(QPen(QColor(t["border"]), 1))
        for i in range(1, 3):
            x = slot.left() + slot.width() * i / 3
            y = slot.top() + slot.height() * i / 3
            p.drawLine(x, slot.top(), x, slot.bottom())
            p.drawLine(slot.left(), y, slot.right(), y)

        if self.item:
            f = QFont("Microsoft YaHei", 9, QFont.Bold)
            p.setFont(f)
            rc = RARITY_COLORS.get(self.item.rarity, "#ffffff")
            p.setPen(QColor("#1a1a1a"))
            p.drawText(slot.adjusted(1, 1, 1, 1), Qt.AlignBottom | Qt.AlignHCenter, self.item.name)
            p.setPen(QColor(rc).darker(150) if rc == "#ffffff" else QColor(rc))
            p.drawText(slot, Qt.AlignBottom | Qt.AlignHCenter, self.item.name)
            p.setPen(QColor(t["text_dim"]))
            f2 = QFont("Microsoft YaHei", 8)
            p.setFont(f2)
            p.drawText(self.rect().adjusted(0, -10, 0, 0), Qt.AlignBottom | Qt.AlignHCenter,
                       f"x{self.item.stack_size}  ·  {self.item.rarity}")
        p.end()


class InventoryEditor(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        form = QGroupBox("物品属性")
        fl = QFormLayout(form)
        self.e_id = QLineEdit(); self.e_id.textChanged.connect(self.on_change)
        self.e_name = QLineEdit(); self.e_name.textChanged.connect(self.on_change)
        self.e_lore = QTextEdit(); self.e_lore.setMaximumHeight(80); self.e_lore.textChanged.connect(self.on_change)
        self.s_stack = QSpinBox(); self.s_stack.setRange(1, 64); self.s_stack.valueChanged.connect(self.on_change)
        self.s_damage = QSpinBox(); self.s_damage.setRange(0, 2000); self.s_damage.valueChanged.connect(self.on_change)
        self.c_rarity = QComboBox(); self.c_rarity.addItems(RARITY_COLORS.keys()); self.c_rarity.currentTextChanged.connect(self.on_change)
        self.chk_glow = QCheckBox("发光（附魔光晕）"); self.chk_glow.stateChanged.connect(self.on_change)
        fl.addRow("物品ID:", self.e_id)
        fl.addRow("显示名称:", self.e_name)
        fl.addRow("描述(Lore):", self.e_lore)
        fl.addRow("最大堆叠:", self.s_stack)
        fl.addRow("最大耐久:", self.s_damage)
        fl.addRow("稀有度:", self.c_rarity)
        fl.addRow("", self.chk_glow)

        right = QGroupBox("物品栏预览")
        vl = QVBoxLayout(right)
        self.preview = SlotPreview()
        vl.addWidget(self.preview, alignment=Qt.AlignCenter)
        note = QLabel("预览会随属性实时更新\n模型外观来自「模型工坊」")
        note.setAlignment(Qt.AlignCenter)
        note.setStyleSheet(f"color:{theme()['text_dim']};")
        vl.addWidget(note)

        root.addWidget(form, 3)
        root.addWidget(right, 1)

    def current(self):
        return self.main.current_item()

    def refresh(self):
        item = self.current()
        if not item:
            for w in [self.e_id, self.e_name, self.e_lore]: w.blockSignals(True); w.clear(); w.blockSignals(False)
            self.preview.set_item(None); return
        self.e_id.blockSignals(True); self.e_name.blockSignals(True); self.e_lore.blockSignals(True)
        self.s_stack.blockSignals(True); self.s_damage.blockSignals(True); self.c_rarity.blockSignals(True); self.chk_glow.blockSignals(True)
        self.e_id.setText(item.id)
        self.e_name.setText(item.name)
        self.e_lore.setPlainText(item.lore)
        self.s_stack.setValue(item.stack_size)
        self.s_damage.setValue(item.max_damage)
        idx = self.c_rarity.findText(item.rarity)
        if idx >= 0: self.c_rarity.setCurrentIndex(idx)
        self.chk_glow.setChecked(item.glowing)
        for w in [self.e_id, self.e_name, self.e_lore, self.s_stack, self.s_damage, self.c_rarity, self.chk_glow]: w.blockSignals(False)
        self.preview.set_item(item)

    def on_change(self):
        item = self.current()
        if not item: return
        item.id = self.e_id.text() or item.id
        item.name = self.e_name.text()
        item.lore = self.e_lore.toPlainText()
        item.stack_size = self.s_stack.value()
        item.max_damage = self.s_damage.value()
        item.rarity = self.c_rarity.currentText()
        item.glowing = self.chk_glow.isChecked()
        self.main.mark_dirty()
        self.preview.set_item(item)
