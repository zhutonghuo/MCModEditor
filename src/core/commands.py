COMMAND_TEMPLATES = [
    {"name": "give", "label": "给予物品", "desc": "给玩家发放物品", "args": [
        {"name": "target", "label": "目标玩家", "default": "@a", "type": "selector"},
        {"name": "item", "label": "物品ID", "default": "minecraft:diamond", "type": "text"},
        {"name": "count", "label": "数量", "default": 1, "type": "int"},
    ]},
    {"name": "summon", "label": "召唤实体", "desc": "在指定位置召唤实体", "args": [
        {"name": "entity", "label": "实体ID", "default": "minecraft:armor_stand", "type": "text"},
        {"name": "x", "label": "X", "default": "~", "type": "text"},
        {"name": "y", "label": "Y", "default": "~", "type": "text"},
        {"name": "z", "label": "Z", "default": "~", "type": "text"},
        {"name": "nbt", "label": "NBT", "default": "", "type": "text"},
    ]},
    {"name": "tp", "label": "传送", "desc": "传送实体到坐标或另一实体", "args": [
        {"name": "target", "label": "目标", "default": "@s", "type": "selector"},
        {"name": "x", "label": "X", "default": "~", "type": "text"},
        {"name": "y", "label": "Y", "default": "~", "type": "text"},
        {"name": "z", "label": "Z", "default": "~", "type": "text"},
    ]},
    {"name": "effect", "label": "给予药水效果", "desc": "为目标添加状态效果", "args": [
        {"name": "target", "label": "目标", "default": "@a", "type": "selector"},
        {"name": "effect", "label": "效果", "default": "speed", "type": "text"},
        {"name": "seconds", "label": "时长(秒)", "default": 30, "type": "int"},
        {"name": "level", "label": "等级", "default": 1, "type": "int"},
    ]},
    {"name": "setblock", "label": "放置方块", "desc": "在指定坐标设置方块", "args": [
        {"name": "x", "label": "X", "default": "~", "type": "text"},
        {"name": "y", "label": "Y", "default": "~", "type": "text"},
        {"name": "z", "label": "Z", "default": "~", "type": "text"},
        {"name": "block", "label": "方块ID", "default": "minecraft:stone", "type": "text"},
    ]},
    {"name": "say", "label": "发送消息", "desc": "向聊天栏广播消息", "args": [
        {"name": "message", "label": "消息", "default": "你好，世界！", "type": "text"},
    ]},
    {"name": "execute", "label": "执行条件指令", "desc": "以特定条件执行子命令", "args": [
        {"name": "as", "label": "作为(as)", "default": "@a", "type": "selector"},
        {"name": "at", "label": "位于(at)", "default": "@s", "type": "selector"},
        {"name": "run", "label": "运行(run)", "default": "say 你好", "type": "text"},
    ]},
    {"name": "scoreboard", "label": "计分板", "desc": "操作计分板目标", "args": [
        {"name": "action", "label": "动作", "default": "players add", "type": "text"},
        {"name": "target", "label": "目标", "default": "@a", "type": "selector"},
        {"name": "objective", "label": "目标名", "default": "score", "type": "text"},
        {"name": "value", "label": "数值", "default": 1, "type": "int"},
    ]},
    {"name": "particle", "label": "生成粒子", "desc": "在位置生成粒子效果", "args": [
        {"name": "name", "label": "粒子", "default": "minecraft:happy_villager", "type": "text"},
        {"name": "x", "label": "X", "default": "~", "type": "text"},
        {"name": "y", "label": "Y", "default": "~", "type": "text"},
        {"name": "z", "label": "Z", "default": "~", "type": "text"},
    ]},
    {"name": "play sound", "label": "播放声音", "desc": "给玩家播放声音", "args": [
        {"name": "sound", "label": "声音ID", "default": "minecraft:entity.player.levelup", "type": "text"},
        {"name": "target", "label": "目标", "default": "@a", "type": "selector"},
    ]},
]


def build(cmd_name, args):
    a = args or {}
    if cmd_name == "give":
        return f"give {a.get('target', '@a')} {a.get('item', 'minecraft:diamond')} {a.get('count', 1)}"
    if cmd_name == "summon":
        nbt = f" {a.get('nbt')}" if a.get("nbt") else ""
        return f"summon {a.get('entity', 'minecraft:armor_stand')} {a.get('x', '~')} {a.get('y', '~')} {a.get('z', '~')}{nbt}"
    if cmd_name == "tp":
        return f"tp {a.get('target', '@s')} {a.get('x', '~')} {a.get('y', '~')} {a.get('z', '~')}"
    if cmd_name == "effect":
        return f"effect give {a.get('target', '@a')} {a.get('effect', 'speed')} {a.get('seconds', 30)} {a.get('level', 1)}"
    if cmd_name == "setblock":
        return f"setblock {a.get('x', '~')} {a.get('y', '~')} {a.get('z', '~')} {a.get('block', 'minecraft:stone')}"
    if cmd_name == "say":
        return f"say {a.get('message', '')}"
    if cmd_name == "execute":
        return f"execute as {a.get('as', '@a')} at {a.get('at', '@s')} run {a.get('run', 'say 你好')}"
    if cmd_name == "scoreboard":
        return f"scoreboard {a.get('action', 'players add')} {a.get('target', '@a')} {a.get('objective', 'score')} {a.get('value', 1)}"
    if cmd_name == "particle":
        return f"particle {a.get('name', 'minecraft:happy_villager')} {a.get('x', '~')} {a.get('y', '~')} {a.get('z', '~')} 0 0 0 0 1 force @a"
    if cmd_name == "play sound":
        return f"playsound {a.get('sound', 'minecraft:entity.player.levelup')} master {a.get('target', '@a')} ~ ~ ~ 1 1"
    return ""


def validate(line):
    if not line or not line.strip():
        return False, "命令为空"
    head = line.strip().split()[0].lower()
    known = {t["name"] for t in COMMAND_TEMPLATES} | {
        "playsound", "teleport", "fill", "clone", "gamerule", "tellraw", "title",
        "bossbar", "advancement", "tag", "data", "item", "loot", "weather", "time",
        "spawnpoint", "gamemode", "xp", "kill", "list", "help", "seed", "function",
    }
    if head not in known:
        return False, f"未知命令 '{head}'，请检查拼写"
    return True, "语法看起来没问题 ✓"


def suggest(prefix):
    names = [t["name"] for t in COMMAND_TEMPLATES]
    p = prefix.strip().lower()
    if not p:
        return names
    return [n for n in names if n.startswith(p)]


def to_mcfunction(lines):
    return "\n".join("# 由 MC模组编辑器 生成" if i == 0 else ln for i, ln in enumerate(lines))
