import json
import os
import zipfile
from datetime import datetime


def _safe(s):
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in str(s)).lower()


def export_resource_pack(project, out_dir):
    ns = _safe(project.namespace)
    root = os.path.join(out_dir, f"{ns}_资源包")
    models = os.path.join(root, "assets", ns, "models", "item")
    animations = os.path.join(root, "assets", ns, "animations")
    os.makedirs(models, exist_ok=True)
    os.makedirs(animations, exist_ok=True)
    pack_meta = {
        "pack": {
            "pack_format": 15,
            "description": f"{project.name} - 由 MC模组编辑器 生成",
        }
    }
    with open(os.path.join(root, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump(pack_meta, f, ensure_ascii=False, indent=2)

    for item in project.items:
        iid = _safe(item.id)
        model = item.model.to_mc_json(ns, iid)
        with open(os.path.join(models, f"{iid}.json"), "w", encoding="utf-8") as f:
            json.dump(model, f, ensure_ascii=False, indent=2)
        if item.animation.tracks:
            with open(os.path.join(animations, f"{iid}.animation.json"), "w", encoding="utf-8") as f:
                json.dump(item.animation.to_mc_json(), f, ensure_ascii=False, indent=2)
    return root


def export_data_pack(project, out_dir):
    ns = _safe(project.namespace)
    root = os.path.join(out_dir, f"{ns}_数据包")
    functions = os.path.join(root, "data", ns, "functions")
    os.makedirs(functions, exist_ok=True)
    pack_meta = {
        "pack": {
            "pack_format": 10,
            "description": f"{project.name} 命令 - 由 MC模组编辑器 生成",
        }
    }
    with open(os.path.join(root, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump(pack_meta, f, ensure_ascii=False, indent=2)

    all_lines = [f"# {project.name} - 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    for item in project.items:
        iid = _safe(item.id)
        all_lines.append(f"\n# 物品: {item.name}")
        for cmd in item.commands:
            all_lines.append(cmd)
        for script in item.scripts:
            all_lines.extend(script.to_commands())
    with open(os.path.join(functions, "generated.mcfunction"), "w", encoding="utf-8") as f:
        f.write("\n".join(all_lines))
    return root


def export_ui_json(project, out_dir):
    ns = _safe(project.namespace)
    root = os.path.join(out_dir, f"{ns}_界面")
    os.makedirs(root, exist_ok=True)
    for item in project.items:
        data = {
            "item": item.id,
            "display": {
                "name": item.name,
                "lore": item.lore.split("\n") if item.lore else [],
                "rarity": item.rarity,
                "glowing": item.glowing,
            },
            "inventory": {
                "stack_size": item.stack_size,
                "max_damage": item.max_damage,
            },
        }
        with open(os.path.join(root, f"{_safe(item.id)}_ui.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return root


def export_all(project, out_dir):
    rp = export_resource_pack(project, out_dir)
    dp = export_data_pack(project, out_dir)
    ui = export_ui_json(project, out_dir)
    return [rp, dp, ui]


def zip_pack(folder, zip_path=None):
    zip_path = zip_path or folder + ".zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            for fn in files:
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, os.path.dirname(folder)))
    return zip_path
