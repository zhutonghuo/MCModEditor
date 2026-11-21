from PIL import Image, ImageDraw
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "src", "resources")
os.makedirs(RES, exist_ok=True)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rounded_bg(size, c1, c2, radius_ratio=0.22):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    r = int(size * radius_ratio)
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            col = lerp(c1, c2, t)
            cx = min(max(x, r), size - r)
            cy = min(max(y, r), size - r)
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= r * r:
                px[x, y] = col + (255,)
    return img


def cube(draw, cx, cy, s, top, left, right, outline):
    h = s * 0.5
    top_pts = [(cx, cy - s), (cx + s, cy - h), (cx, cy), (cx - s, cy - h)]
    left_pts = [(cx - s, cy - h), (cx, cy), (cx, cy + s), (cx - s, cy + h)]
    right_pts = [(cx + s, cy - h), (cx, cy + s + h - s), (cx, cy + s), (cx + s, cy - h)]
    right_pts = [(cx + s, cy - h), (cx + s, cy + h), (cx, cy + s), (cx, cy)]
    draw.polygon(left_pts, fill=left, outline=outline)
    draw.polygon(right_pts, fill=right, outline=outline)
    draw.polygon(top_pts, fill=top, outline=outline)
    w = max(2, int(s * 0.04))
    draw.line(top_pts + [top_pts[0]], fill=outline, width=w)
    draw.line(left_pts + [left_pts[0]], fill=outline, width=w)
    draw.line(right_pts + [right_pts[0]], fill=outline, width=w)


def pixel_sword(draw, cx, cy, s, blade, blade_shade, hilt, gold):
    w = max(3, int(s * 0.13))
    draw.polygon([(cx, cy - s), (cx + w, cy - s + w * 2), (cx + w, cy + w), (cx - w, cy + w), (cx - w, cy - s + w * 2)], fill=blade)
    draw.polygon([(cx, cy - s), (cx + w, cy - s + w * 2), (cx + w, cy + w), (cx, cy + w)], fill=blade_shade)
    gy = cy + w
    draw.rectangle([cx - w * 2, gy, cx + w * 2, gy + w], fill=gold)
    draw.rectangle([cx - w // 2, gy + w, cx + w // 2, gy + s // 2], fill=hilt)
    draw.ellipse([cx - w, gy + s // 2 - w, cx + w, gy + s // 2 + w], fill=gold)


def down_arrow(draw, cx, cy, s, color, outline):
    w = max(4, int(s * 0.22))
    draw.rectangle([cx - w // 2, cy - s // 2, cx + w // 2, cy + s // 6], fill=color, outline=outline, width=2)
    draw.polygon([(cx - s // 2, cy), (cx + s // 2, cy), (cx, cy + s // 2)], fill=color, outline=outline)


def make_editor(size=512):
    img = rounded_bg(size, (58, 44, 120), (28, 34, 78))
    d = ImageDraw.Draw(img)
    cube(d, size * 0.5, size * 0.46, size * 0.30,
         (168, 139, 250), (124, 92, 246), (92, 63, 214), (24, 20, 56))
    pixel_sword(d, size * 0.5, size * 0.30, size * 0.26,
                (233, 240, 255), (176, 196, 240), (139, 90, 43), (224, 166, 58))
    return img


def make_installer(size=512):
    img = rounded_bg(size, (28, 84, 128), (20, 40, 92))
    d = ImageDraw.Draw(img)
    cube(d, size * 0.5, size * 0.50, size * 0.32,
         (96, 200, 224), (56, 152, 196), (36, 110, 160), (16, 44, 76))
    down_arrow(d, size * 0.5, size * 0.46, size * 0.34, (245, 250, 255), (20, 60, 100))
    return img


def save_ico(img, path, sizes=(16, 24, 32, 48, 64, 128, 256)):
    base = img.resize((256, 256), Image.LANCZOS)
    base.save(path, format="ICO", sizes=[(s, s) for s in sizes])
    print("saved", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    ed = make_editor()
    ed.save(os.path.join(RES, "app_icon.png"))
    save_ico(ed, os.path.join(RES, "app.ico"))

    ins = make_installer()
    ins.save(os.path.join(RES, "setup_icon.png"))
    save_ico(ins, os.path.join(RES, "setup.ico"))
    print("icons done")
