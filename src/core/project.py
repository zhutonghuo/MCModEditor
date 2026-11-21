import json
import os
from datetime import datetime
from .model import VoxelModel
from .animation import Animation
from .blocks import BlockProgram


class Item:
    def __init__(self, item_id="my_item", name="我的物品"):
        self.id = item_id
        self.name = name
        self.lore = ""
        self.stack_size = 64
        self.max_damage = 0
        self.rarity = "common"
        self.glowing = False
        self.model = VoxelModel(item_id)
        self.animation = Animation("idle")
        self.scripts = []
        self.commands = []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lore": self.lore,
            "stack_size": self.stack_size,
            "max_damage": self.max_damage,
            "rarity": self.rarity,
            "glowing": self.glowing,
            "model": self.model.to_dict(),
            "animation": self.animation.to_dict(),
            "scripts": [s.to_dict() for s in self.scripts],
            "commands": list(self.commands),
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("id", "my_item"), data.get("name", "我的物品"))
        obj.lore = data.get("lore", "")
        obj.stack_size = data.get("stack_size", 64)
        obj.max_damage = data.get("max_damage", 0)
        obj.rarity = data.get("rarity", "common")
        obj.glowing = data.get("glowing", False)
        obj.model = VoxelModel.from_dict(data.get("model", {}))
        obj.animation = Animation.from_dict(data.get("animation", {}))
        obj.scripts = [BlockProgram.from_dict(s) for s in data.get("scripts", [])]
        obj.commands = list(data.get("commands", []))
        return obj


class Project:
    def __init__(self, name="未命名模组", namespace="mymod"):
        self.name = name
        self.namespace = namespace
        self.author = ""
        self.description = ""
        self.created = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.items = []
        self.path = None

    def add_item(self, item_id=None, name=None):
        idx = len(self.items) + 1
        item = Item(item_id or f"my_item_{idx}", name or f"我的物品 {idx}")
        self.items.append(item)
        return item

    def current_item(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def to_dict(self):
        return {
            "format": "mcme-project-v1",
            "name": self.name,
            "namespace": self.namespace,
            "author": self.author,
            "description": self.description,
            "created": self.created,
            "items": [i.to_dict() for i in self.items],
        }

    def save(self, path):
        self.path = path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return path

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        obj = cls(data.get("name", "未命名模组"), data.get("namespace", "mymod"))
        obj.author = data.get("author", "")
        obj.description = data.get("description", "")
        obj.created = data.get("created", obj.created)
        obj.items = [Item.from_dict(d) for d in data.get("items", [])]
        obj.path = path
        return obj

    @classmethod
    def demo(cls):
        obj = cls("演示模组", "demomod")
        obj.author = "MC模组编辑器"
        obj.description = "一个自动生成的演示工程"
        item = obj.add_item("magic_sword", "魔法剑")
        item.lore = "由模组编辑器打造的传奇之剑\n右键释放魔法"
        item.rarity = "epic"
        item.glowing = True
        item.stack_size = 1
        item.max_damage = 500
        for x in range(-1, 2):
            item.model.add(x, 0, 0, "#c9a227", "blade")
        item.model.add(0, 1, 0, "#8b5cf6", "blade")
        item.model.add(0, -1, 0, "#5a3d1e", "handle")
        item.animation.add_keyframe("blade", 0, rot=(0, 0, -10))
        item.animation.add_keyframe("blade", 20, rot=(0, 0, 10))
        item.animation.add_keyframe("blade", 40, rot=(0, 0, -10))
        script = item.scripts[0] if item.scripts else None
        if script is None:
            from .blocks import BlockProgram
            script = BlockProgram("魔法剑脚本")
            item.scripts.append(script)
        script.add_block("on_right_click")
        script.add_block("play_sound", ["minecraft:entity.player.levelup"])
        script.add_block("summon_entity", ["minecraft:firework_rocket"])
        item.commands.append("give @a demomod:magic_sword 1")
        return obj
