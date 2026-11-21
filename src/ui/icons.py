from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF
from ui.theme import theme


def _painter(size):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    return pm, p


def _pen(p, color, width=2.0):
    p.setPen(QPen(QColor(color), width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))


def icon(name, size=28, color=None):
    from math import cos, sin, pi
    t = theme()
    c = color or t["accent"]
    pm, p = _painter(size)
    u = size / 24.0

    def P(x, y):
        return QPointF(x * u, y * u)

    def R(x, y, w, h):
        return QRectF(x * u, y * u, w * u, h * u)

    if name == "model":
        _pen(p, c, 1.8)
        p.drawPolygon(QPolygonF([P(12, 2), P(21, 7), P(21, 17), P(12, 22), P(3, 17), P(3, 7)]))
        p.drawLine(P(3, 7), P(12, 12)); p.drawLine(P(12, 12), P(21, 7)); p.drawLine(P(12, 12), P(12, 22))
    elif name == "animation":
        _pen(p, c, 1.8)
        p.drawRoundedRect(R(2, 4, 20, 16), 3 * u, 3 * u)
        p.drawLine(P(8, 4), P(8, 20)); p.drawLine(P(16, 4), P(16, 20))
        p.setBrush(QBrush(QColor(c))); p.setPen(Qt.NoPen)
        for x in [5, 12, 19]:
            p.drawRect(R(x - 1, 6, 2, 2))
    elif name == "inventory":
        _pen(p, c, 1.8)
        p.drawRoundedRect(R(3, 3, 18, 18), 3 * u, 3 * u)
        p.drawRoundedRect(R(6.5, 6.5, 11, 11), 2 * u, 2 * u)
        p.drawEllipse(P(12, 12), 2.2 * u, 2.2 * u)
    elif name == "blocks":
        p.setBrush(QBrush(QColor(c))); p.setPen(Qt.NoPen)
        p.drawRoundedRect(R(2, 3, 9, 7), 2 * u, 2 * u)
        p.drawRoundedRect(R(13, 3, 9, 7), 2 * u, 2 * u)
        p.drawRoundedRect(R(7.5, 14, 9, 7), 2 * u, 2 * u)
    elif name == "command":
        _pen(p, c, 2.2)
        p.drawLine(P(5, 7), P(10, 12)); p.drawLine(P(10, 12), P(5, 17))
        p.drawLine(P(13, 17), P(20, 17))
    elif name == "ui":
        _pen(p, c, 1.8)
        p.drawRoundedRect(R(2, 3, 20, 18), 2 * u, 2 * u)
        p.drawLine(P(2, 8), P(22, 8))
        p.drawRoundedRect(R(4.5, 10, 6, 4), 1.5 * u, 1.5 * u)
        p.drawRoundedRect(R(13, 10, 7, 9), 1.5 * u, 1.5 * u)
    elif name == "save":
        _pen(p, c, 1.8)
        p.drawRoundedRect(R(3, 3, 18, 18), 2 * u, 2 * u)
        p.drawRoundedRect(R(7, 3, 10, 7), u, u)
        p.drawRoundedRect(R(6, 13, 12, 8), u, u)
    elif name == "open":
        _pen(p, c, 1.8)
        path = QPainterPath()
        path.moveTo(P(2, 7)); path.lineTo(P(2, 19)); path.lineTo(P(22, 19)); path.lineTo(P(22, 8))
        path.lineTo(P(11, 8)); path.lineTo(P(8, 5)); path.lineTo(P(2, 5)); path.closeSubpath()
        p.drawPath(path)
    elif name == "new":
        _pen(p, c, 1.8)
        p.drawRoundedRect(R(4, 4, 16, 16), 2 * u, 2 * u)
        p.drawLine(P(12, 8), P(12, 16)); p.drawLine(P(8, 12), P(16, 12))
    elif name == "export":
        _pen(p, c, 1.8)
        p.drawRoundedRect(R(2, 7, 11, 11), 2 * u, 2 * u)
        p.drawLine(P(13, 12), P(22, 12)); p.drawLine(P(18, 8), P(22, 12)); p.drawLine(P(18, 16), P(22, 12))
    elif name == "play":
        p.setBrush(QBrush(QColor(c))); p.setPen(Qt.NoPen)
        pp = QPainterPath(); pp.moveTo(P(7, 4)); pp.lineTo(P(20, 12)); pp.lineTo(P(7, 20)); pp.closeSubpath()
        p.drawPath(pp)
    elif name == "pause":
        p.setBrush(QBrush(QColor(c))); p.setPen(Qt.NoPen)
        p.drawRoundedRect(R(6, 4, 4, 16), u, u)
        p.drawRoundedRect(R(14, 4, 4, 16), u, u)
    elif name == "stop":
        p.setBrush(QBrush(QColor(c))); p.setPen(Qt.NoPen)
        p.drawRoundedRect(R(5, 5, 14, 14), 2 * u, 2 * u)
    elif name == "add":
        _pen(p, c, 2.4)
        p.drawEllipse(P(12, 12), 9 * u, 9 * u)
        p.drawLine(P(12, 7), P(12, 17)); p.drawLine(P(7, 12), P(17, 12))
    elif name == "delete":
        _pen(p, c, 1.8)
        p.drawLine(P(5, 6), P(19, 6)); p.drawLine(P(9, 6), P(9, 4)); p.drawLine(P(15, 6), P(15, 4))
        p.drawRoundedRect(R(6, 6, 12, 14), 2 * u, 2 * u)
        p.drawLine(P(10, 10), P(10, 17)); p.drawLine(P(14, 10), P(14, 17))
    elif name == "undo":
        _pen(p, c, 1.8)
        p.drawLine(P(8, 8), P(3, 13)); p.drawLine(P(3, 13), P(8, 18))
        arc = QPainterPath(); arc.moveTo(P(3, 13)); arc.arcTo(R(3, 4, 18, 18), 180, -140); p.drawPath(arc)
    elif name == "redo":
        _pen(p, c, 1.8)
        p.drawLine(P(16, 8), P(21, 13)); p.drawLine(P(21, 13), P(16, 18))
        arc = QPainterPath(); arc.moveTo(P(21, 13)); arc.arcTo(R(3, 4, 18, 18), 0, 140); p.drawPath(arc)
    elif name == "rotate":
        _pen(p, c, 1.8)
        p.drawEllipse(P(12, 12), 8 * u, 8 * u)
        p.drawLine(P(12, 4), P(12, 2)); p.drawLine(P(12, 22), P(12, 20))
    elif name == "settings":
        _pen(p, c, 1.8)
        p.drawEllipse(P(12, 12), 4 * u, 4 * u)
        for i in range(8):
            a = i * 45 * pi / 180
            p.drawLine(P(12 + 7 * cos(a), 12 + 7 * sin(a)), P(12 + 10 * cos(a), 12 + 10 * sin(a)))
    elif name == "theme":
        _pen(p, c, 1.8)
        p.drawEllipse(P(12, 12), 9 * u, 9 * u)
        p.setBrush(QBrush(QColor(c))); p.setPen(Qt.NoPen)
        pp = QPainterPath(); pp.moveTo(P(12, 3)); pp.arcTo(R(3, 3, 18, 18), 90, -180); pp.closeSubpath()
        p.drawPath(pp)
    elif name == "folder":
        p.setBrush(QBrush(QColor(c))); p.setPen(Qt.NoPen)
        p.drawRoundedRect(R(2, 6, 20, 14), 2 * u, 2 * u)
        p.drawRoundedRect(R(2, 3, 9, 5), 1.5 * u, 1.5 * u)
    elif name == "cube":
        _pen(p, c, 1.8)
        p.drawRect(R(4, 8, 12, 12))
        p.drawLine(P(4, 8), P(9, 3)); p.drawLine(P(16, 8), P(21, 3))
        p.drawLine(P(9, 3), P(21, 3)); p.drawLine(P(21, 3), P(21, 17))
        p.drawLine(P(16, 20), P(21, 17))
    elif name == "copy":
        _pen(p, c, 1.8)
        p.drawRoundedRect(R(8, 8, 13, 13), 2 * u, 2 * u)
        p.drawRoundedRect(R(3, 3, 13, 13), 2 * u, 2 * u)
    elif name == "trash":
        _pen(p, c, 1.8)
        p.drawRoundedRect(R(5, 7, 14, 14), 2 * u, 2 * u)
        p.drawLine(P(9, 11), P(9, 18)); p.drawLine(P(15, 11), P(15, 18))
        p.drawLine(P(3, 7), P(21, 7))
    else:
        _pen(p, c, 1.8)
        p.drawEllipse(P(12, 12), 8 * u, 8 * u)

    p.end()
    return QIcon(pm)


_CACHE = {}


def get(name, size=28, color=None):
    key = (name, size, color)
    if key not in _CACHE:
        _CACHE[key] = icon(name, size, color)
    return _CACHE[key]


def clear_cache():
    _CACHE.clear()
