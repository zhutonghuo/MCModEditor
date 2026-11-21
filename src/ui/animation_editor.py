from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider,
    QSpinBox, QComboBox, QListWidget, QGroupBox, QSplitter, QDoubleSpinBox,
    QGridLayout, QCheckBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QCheckBox
from ui.voxel_view import VoxelView
from ui import icons
from ui.theme import theme


class AnimationEditor(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.playing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        self.view = VoxelView()
        ll.addWidget(self.view)

        playbar = QHBoxLayout()
        self.btn_play = QPushButton(); self.btn_play.setIcon(icons.get("play", 20))
        self.btn_play.clicked.connect(self.toggle_play)
        btn_stop = QPushButton(); btn_stop.setIcon(icons.get("stop", 20))
        btn_stop.clicked.connect(self.stop)
        self.tick_label = QLabel("0 / 40")
        playbar.addWidget(self.btn_play); playbar.addWidget(btn_stop); playbar.addWidget(self.tick_label)
        ll.addLayout(playbar)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 40)
        self.slider.valueChanged.connect(self.on_slider)
        ll.addWidget(self.slider)

        right = QGroupBox("关键帧")
        rl = QVBoxLayout(right)
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("部件:"))
        self.part_combo = QComboBox()
        ctrl.addWidget(self.part_combo)
        rl.addLayout(ctrl)

        vec = QGroupBox("位移 / 旋转 / 缩放")
        vg = QGridLayout(vec)
        self.spins = {}
        for i, key in enumerate(["px", "py", "pz", "rx", "ry", "rz", "scale"]):
            vg.addWidget(QLabel(key), i, 0)
            if key == "scale":
                s = QDoubleSpinBox(); s.setRange(0.1, 5); s.setSingleStep(0.1); s.setValue(1)
            else:
                s = QSpinBox(); s.setRange(-180, 180); s.setValue(0)
            self.spins[key] = s
            vg.addWidget(s, i, 1)
        rl.addWidget(vec)

        kfb = QPushButton("在当前帧添加/更新关键帧")
        kfb.setIcon(icons.get("add", 20))
        kfb.clicked.connect(self.add_keyframe)
        rl.addWidget(kfb)
        bdel = QPushButton("删除当前帧关键帧")
        bdel.setIcon(icons.get("delete", 20))
        bdel.clicked.connect(self.del_keyframe)
        rl.addWidget(bdel)

        self.kf_list = QListWidget()
        self.kf_list.itemClicked.connect(self.goto_keyframe)
        rl.addWidget(self.kf_list)

        dur = QHBoxLayout()
        dur.addWidget(QLabel("总时长(帧):"))
        self.duration = QSpinBox(); self.duration.setRange(1, 600); self.duration.setValue(40)
        self.duration.valueChanged.connect(self.on_duration)
        dur.addWidget(self.duration)
        rl.addLayout(dur)
        self.chk_loop = QCheckBox("循环播放")
        self.chk_loop.setChecked(True)
        self.chk_loop.stateChanged.connect(self.on_loop)
        rl.addWidget(self.chk_loop)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left); splitter.addWidget(right)
        splitter.setStretchFactor(0, 1); splitter.setStretchFactor(1, 0)
        splitter.setSizes([420, 280])
        root.addWidget(splitter)

    def current_anim(self):
        item = self.main.current_item()
        return item.animation if item else None

    def refresh(self):
        item = self.main.current_item()
        if not item:
            self.view.set_data(None); return
        anim = item.animation
        self.view.set_data(item.model, anim)
        self.slider.setRange(0, anim.duration)
        self.duration.setValue(anim.duration)
        self.chk_loop.setChecked(anim.loop)
        parts = item.model.parts()
        cur = self.part_combo.currentText()
        self.part_combo.blockSignals(True)
        self.part_combo.clear(); self.part_combo.addItems(parts or ["main"])
        if cur in parts: self.part_combo.setCurrentText(cur)
        self.part_combo.blockSignals(False)
        self.kf_list.clear()
        for t in anim.all_times():
            frames = anim.keyframes_at(t)
            parts_at = ",".join(frames.keys())
            self.kf_list.addItem(f"帧 {t}  [{parts_at}]")
        self.update_display()

    def on_loop(self, state):
        anim = self.current_anim()
        if anim:
            anim.loop = bool(state)
            self.main.mark_dirty()

    def on_duration(self, v):
        anim = self.current_anim()
        if anim:
            anim.duration = v
            self.slider.setRange(0, v)
            self.main.mark_dirty()

    def on_slider(self, v):
        self.view.set_tick(v)
        self.tick_label.setText(f"{v} / {self.slider.maximum()}")

    def update_display(self):
        anim = self.current_anim()
        if not anim: return
        part = self.part_combo.currentText()
        frame = None
        for f in anim.tracks.get(part, []):
            if f["time"] == self.slider.value():
                frame = f; break
        if frame:
            for i, key in enumerate(["px", "py", "pz"]):
                self.spins[key].setValue(int(frame["pos"][i]))
            for i, key in enumerate(["rx", "ry", "rz"]):
                self.spins[key].setValue(int(frame["rot"][i]))
            self.spins["scale"].setValue(frame["scale"])

    def add_keyframe(self):
        anim = self.current_anim()
        if not anim: return
        part = self.part_combo.currentText() or "main"
        pos = [self.spins[k].value() for k in ["px", "py", "pz"]]
        rot = [self.spins[k].value() for k in ["rx", "ry", "rz"]]
        scale = float(self.spins["scale"].value())
        anim.add_keyframe(part, self.slider.value(), pos, rot, scale)
        self.main.mark_dirty(); self.refresh()

    def del_keyframe(self):
        anim = self.current_anim()
        if not anim: return
        anim.remove_keyframe(self.part_combo.currentText(), self.slider.value())
        self.main.mark_dirty(); self.refresh()

    def goto_keyframe(self, item):
        try:
            t = int(item.text().split()[1])
            self.slider.setValue(t)
        except Exception:
            pass

    def toggle_play(self):
        if self.playing:
            self.timer.stop(); self.playing = False
            self.btn_play.setIcon(icons.get("play", 20))
        else:
            self.playing = True
            self.timer.start(80)
            self.btn_play.setIcon(icons.get("pause", 20))

    def step(self):
        anim = self.current_anim()
        if not anim: return
        v = self.slider.value() + 1
        if v > anim.duration:
            v = 0 if anim.loop else anim.duration
        self.slider.setValue(v)

    def stop(self):
        self.timer.stop(); self.playing = False
        self.btn_play.setIcon(icons.get("play", 20))
        self.slider.setValue(0)
