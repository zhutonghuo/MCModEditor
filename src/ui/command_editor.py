from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QGroupBox, QPushButton,
    QLineEdit, QSpinBox, QLabel, QMessageBox, QSplitter, QFormLayout, QTextEdit,
)
from PyQt5.QtCore import Qt
from core import commands
from ui import icons
from ui.theme import theme


class CommandEditor(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.current_cmd = None
        self.arg_widgets = {}
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        left = QGroupBox("命令模板")
        ll = QVBoxLayout(left)
        self.search = QLineEdit(); self.search.setPlaceholderText("搜索命令..."); self.search.textChanged.connect(self.filter)
        ll.addWidget(self.search)
        self.cmd_list = QListWidget(); self.cmd_list.itemClicked.connect(self.select_cmd)
        ll.addWidget(self.cmd_list)

        mid = QGroupBox("参数")
        ml = QFormLayout(mid)
        self.form_holder = QWidget()
        self.form = QFormLayout(self.form_holder)
        ml.addRow(self.form_holder)
        bgen = QPushButton("生成并添加到列表"); bgen.setIcon(icons.get("add", 20)); bgen.clicked.connect(self.gen_and_add)
        ml.addRow(bgen)

        right = QGroupBox("物品命令列表")
        rl = QVBoxLayout(right)
        self.cmd_output = QListWidget(); self.cmd_output.itemDoubleClicked.connect(self.edit_existing)
        rl.addWidget(self.cmd_output)
        bdel = QPushButton("删除选中"); bdel.setIcon(icons.get("delete", 20)); bdel.clicked.connect(self.delete_cmd)
        bval = QPushButton("校验所有命令"); bval.setIcon(icons.get("settings", 20)); bval.clicked.connect(self.validate_all)
        rl.addWidget(bdel); rl.addWidget(bval)
        self.result = QLabel(""); self.result.setWordWrap(True)
        rl.addWidget(self.result)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left); splitter.addWidget(mid); splitter.addWidget(right)
        splitter.setStretchFactor(0, 0); splitter.setStretchFactor(1, 1); splitter.setStretchFactor(2, 1)
        splitter.setSizes([180, 300, 320])
        root.addWidget(splitter)
        self.filter()

    def filter(self):
        q = self.search.text().strip().lower()
        self.cmd_list.clear()
        for t in commands.COMMAND_TEMPLATES:
            if not q or q in t["name"].lower() or q in t["label"]:
                self.cmd_list.addItem(f"{t['label']}  ({t['name']})")

    def select_cmd(self, item):
        text = item.text()
        name = text.split("(")[-1].rstrip(")")
        tmpl = None
        for t in commands.COMMAND_TEMPLATES:
            if t["name"] == name:
                tmpl = t; break
        if not tmpl: return
        self.current_cmd = tmpl
        self.build_form(tmpl)

    def build_form(self, tmpl, values=None):
        while self.form.rowCount() > 0:
            self.form.removeRow(0)
        self.arg_widgets = {}
        values = values or {}
        for arg in tmpl["args"]:
            w = QLineEdit() if arg["type"] != "int" else QSpinBox()
            if isinstance(w, QSpinBox):
                w.setRange(-99999, 99999)
                w.setValue(int(values.get(arg["name"], arg["default"])) if str(values.get(arg["name"], arg["default"])).lstrip("-").isdigit() else arg["default"])
            else:
                w.setText(str(values.get(arg["name"], arg["default"])))
            self.form.addRow(arg["label"] + ":", w)
            self.arg_widgets[arg["name"]] = w

    def collect_args(self):
        args = {}
        for name, w in self.arg_widgets.items():
            if isinstance(w, QSpinBox):
                args[name] = w.value()
            else:
                args[name] = w.text()
        return args

    def gen_and_add(self):
        if not self.current_cmd:
            QMessageBox.information(self, "提示", "请先选择一个命令模板"); return
        line = commands.build(self.current_cmd["name"], self.collect_args())
        item = self.main.current_item()
        if not item:
            QMessageBox.information(self, "提示", "请先添加一个物品"); return
        item.commands.append(line)
        self.main.mark_dirty()
        self.refresh()

    def delete_cmd(self):
        item = self.main.current_item()
        row = self.cmd_output.currentRow()
        if item and row >= 0 and row < len(item.commands):
            item.commands.pop(row)
            self.main.mark_dirty(); self.refresh()

    def edit_existing(self, item):
        row = self.cmd_output.currentRow()
        item_obj = self.main.current_item()
        if not item_obj: return
        line = item_obj.commands[row]
        head = line.split()[0].lower()
        tmpl = next((t for t in commands.COMMAND_TEMPLATES if t["name"] == head or (head == "playsound" and t["name"] == "play sound")), None)
        if tmpl:
            self.current_cmd = tmpl
            self.build_form(tmpl)
        QMessageBox.information(self, "编辑", "已载入参数模板，修改后点「生成并添加到列表」即可覆盖追加。")

    def validate_all(self):
        item = self.main.current_item()
        if not item: return
        problems = []
        for i, line in enumerate(item.commands):
            ok, msg = commands.validate(line)
            if not ok:
                problems.append(f"第{i+1}条: {msg}")
        if problems:
            self.result.setText("⚠ " + "\n".join(problems))
            self.result.setStyleSheet(f"color:{theme()['orange']};")
        else:
            self.result.setText(f"✓ 全部 {len(item.commands)} 条命令校验通过")
            self.result.setStyleSheet(f"color:{theme()['green']};")

    def refresh(self):
        item = self.main.current_item()
        self.cmd_output.clear()
        if item:
            for c in item.commands:
                self.cmd_output.addItem(c)
