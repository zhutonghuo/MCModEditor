import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from core.animation import Animation
from ui.theme import theme


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except Exception:
        return (140, 92, 246)


def shade(rgb, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)


class VoxelView(QWidget):
    clicked = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.animation = None
        self.tick = 0
        self.rot_x = -28
        self.rot_y = 38
        self.dragging = False
        self.last = None
        self.setMinimumSize(320, 300)
        self.setMouseTracking(True)

    def set_data(self, model, animation=None):
        self.model = model
        self.animation = animation or Animation()
        self.update()

    def set_tick(self, tick):
        self.tick = tick
        self.update()

    def _project(self, x, y, z, cx, cy, scale, sampled):
        part_key = "main"
        for v in (self.model.voxels if self.model else []):
            if v["x"] == x and v["y"] == y and v["z"] == z:
                part_key = v["part"]
                break
        px = py = pz = 0.0
        rx = ry = rz = 0.0
        sc = 1.0
        if part_key in sampled:
            f = sampled[part_key]
            px, py, pz = f["pos"]
            rx, ry, rz = f["rot"]
            sc = f["scale"]
        x, y, z = x + px, y + py, z + pz
        ax = math.radians(self.rot_x)
        ay = math.radians(self.rot_y)
        xr = x * math.cos(ay) - z * math.sin(ay)
        zr = x * math.sin(ay) + z * math.cos(ay)
        yr = y * math.cos(ax) - zr * math.sin(ax)
        zrr = y * math.sin(ax) + zr * math.cos(ax)
        return (cx + xr * scale, cy - yr * scale, zrr)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(theme()["canvas"]))
        if not self.model or not self.model.voxels:
            p.setPen(QColor("#9aa3ba"))
            f = QFont("Microsoft YaHei", 12)
            p.setFont(f)
            p.drawText(self.rect(), Qt.AlignCenter, "在模型工坊添加方块，这里会显示 3D 预览")
            p.end()
            return

        mn_x, mn_y, mn_z, mx_x, mx_y, mx_z = self.model.bounds()
        cxv = (mn_x + mx_x + 1) / 2.0
        cyv = (mn_y + mx_y + 1) / 2.0
        czv = (mn_z + mx_z + 1) / 2.0
        span = max(mx_x - mn_x + 1, mx_y - mn_y + 1, mx_z - mn_z + 1, 1)
        scale = min(self.width(), self.height()) / (span * 2.4 + 2)
        cx, cy = self.width() / 2.0, self.height() / 2.0 + span * scale * 0.15
        sampled = self.animation.sample(self.tick) if self.animation else {}

        cubes = []
        for v in self.model.voxels:
            x, y, z = v["x"] - cxv, v["y"] - cyv, v["z"] - czv
            rgb = hex_to_rgb(v["color"])
            center = self._project(x + cxv, y + cyv, z + czv, cx, cy, scale, {})
            cubes.append((center[2], v, rgb, x, y, z))
        cubes.sort(key=lambda c: c[0])

        for depth, v, rgb, x, y, z in cubes:
            faces = [
                ([(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)], shade(rgb, 0.72)),
                ([(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)], shade(rgb, 0.92)),
                ([(-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)], shade(rgb, 1.12)),
                ([(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5)], shade(rgb, 0.55)),
                ([(0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5)], shade(rgb, 0.84)),
                ([(-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5)], shade(rgb, 0.66)),
            ]
            for verts, col in faces:
                proj = [self._project(x + vx + cxv, y + vy + cyv, z + vz + czv, cx, cy, scale, sampled) for vx, vy, vz in verts]
                polygon = QPolygonF([QPointF(pp[0], pp[1]) for pp in proj])
                p.setBrush(QBrush(QColor(*col)))
                p.setPen(QPen(QColor(0, 0, 0, 40), 1))
                p.drawPolygon(polygon)
        p.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.last = e.pos()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self.dragging and self.last:
            dx = e.pos().x() - self.last.x()
            dy = e.pos().y() - self.last.y()
            self.rot_y += dx * 0.5
            self.rot_x = max(-85, min(85, self.rot_x + dy * 0.5))
            self.last = e.pos()
            self.update()
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self.dragging = False
        self.last = None
        super().mouseReleaseEvent(e)

    def wheelEvent(self, e):
        super().wheelEvent(e)
