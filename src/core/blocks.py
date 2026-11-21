BLOCK_LIBRARY = [
    {"op": "on_right_click", "label": "当右键物品时", "cat": "事件", "color": "#e0a63a", "shape": "hat"},
    {"op": "on_left_click", "label": "当左键物品时", "cat": "事件", "color": "#e0a63a", "shape": "hat"},
    {"op": "on_use_tick", "label": "每帧更新时", "cat": "事件", "color": "#e0a63a", "shape": "hat"},
    {"op": "on_craft", "label": "当合成物品时", "cat": "事件", "color": "#e0a63a", "shape": "hat"},
    {"op": "if_equals", "label": "如果 {变量} 等于 {值}", "cat": "条件", "color": "#3aa0c9", "shape": "if", "args": ["变量", "值"]},
    {"op": "if_greater", "label": "如果 {变量} 大于 {值}", "cat": "条件", "color": "#3aa0c9", "shape": "if", "args": ["变量", "值"]},
    {"op": "if_has_item", "label": "如果玩家拥有 {物品}", "cat": "条件", "color": "#3aa0c9", "shape": "if", "args": ["物品"]},
    {"op": "repeat", "label": "重复 {次数} 次", "cat": "条件", "color": "#3aa0c9", "shape": "if", "args": ["次数"]},
    {"op": "say", "label": "发送提示 {文本}", "cat": "动作", "color": "#41a86a", "shape": "stack", "args": ["文本"]},
    {"op": "give_item", "label": "给予物品 {物品} x{数量}", "cat": "动作", "color": "#41a86a", "shape": "stack", "args": ["物品", "数量"]},
    {"op": "play_sound", "label": "播放声音 {声音}", "cat": "动作", "color": "#41a86a", "shape": "stack", "args": ["声音"]},
    {"op": "summon_entity", "label": "召唤实体 {实体}", "cat": "动作", "color": "#41a86a", "shape": "stack", "args": ["实体"]},
    {"op": "set_var", "label": "设置 {变量} 为 {值}", "cat": "动作", "color": "#41a86a", "shape": "stack", "args": ["变量", "值"]},
    {"op": "add_var", "label": "令 {变量} 增加 {值}", "cat": "动作", "color": "#41a86a", "shape": "stack", "args": ["变量", "值"]},
    {"op": "teleport", "label": "传送到 {坐标}", "cat": "动作", "color": "#41a86a", "shape": "stack", "args": ["坐标"]},
]


def block_info(op):
    for b in BLOCK_LIBRARY:
        if b["op"] == op:
            return b
    return {"op": op, "label": op, "cat": "动作", "color": "#41a86a", "shape": "stack", "args": []}


class BlockProgram:
    def __init__(self, name="脚本"):
        self.name = name
        self.blocks = []

    def add_block(self, op, args=None, parent=-1):
        info = block_info(op)
        block = {
            "id": len(self.blocks),
            "op": op,
            "label": info["label"],
            "args": list(args or [info["args"][i] if i < len(info["args"]) else "" for i in range(len(info["args"]))]) if args is not None else ["" for _ in info.get("args", [])],
            "parent": parent,
        }
        self.blocks.append(block)
        return block

    def remove_block(self, block_id):
        self.blocks = [b for b in self.blocks if b["id"] != block_id and b["parent"] != block_id]

    def update_arg(self, block_id, index, value):
        for b in self.blocks:
            if b["id"] == block_id and index < len(b["args"]):
                b["args"][index] = value

    def to_commands(self):
        from .commands import build
        lines = []
        events = {"on_right_click": "右键", "on_left_click": "左键", "on_use_tick": "使用更新", "on_craft": "合成"}
        for b in self.blocks:
            op = b["op"]
            args = b["args"]
            if op in events:
                lines.append(f"# 事件: {events[op]}")
            elif op == "say":
                lines.append(build("say", {"message": args[0] if args else ""}))
            elif op == "give_item":
                lines.append(build("give", {"target": "@s", "item": args[0] if args else "minecraft:diamond", "count": args[1] if len(args) > 1 else 1}))
            elif op == "play_sound":
                lines.append(build("play sound", {"sound": args[0] if args else "minecraft:entity.player.levelup", "target": "@a"}))
            elif op == "summon_entity":
                lines.append(build("summon", {"entity": args[0] if args else "minecraft:armor_stand", "x": "~", "y": "~", "z": "~"}))
            elif op == "teleport":
                lines.append(build("tp", {"target": "@s", "x": args[0] if args else "~", "y": "~", "z": "~"}))
            elif op == "set_var":
                lines.append(f"scoreboard players set @s {args[0] if args else 'var'} {args[1] if len(args)>1 else 0}")
            elif op == "add_var":
                lines.append(f"scoreboard players add @s {args[0] if args else 'var'} {args[1] if len(args)>1 else 0}")
            elif op.startswith("if_"):
                lines.append(f"# 条件: {b['label']}")
        return lines

    def to_dict(self):
        return {"name": self.name, "blocks": list(self.blocks)}

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("name", "脚本"))
        obj.blocks = list(data.get("blocks", []))
        return obj
