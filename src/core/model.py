import json


class VoxelModel:
    def __init__(self, name="model"):
        self.name = name
        self.voxels = []

    def add(self, x, y, z, color="#8b5cf6", part="main"):
        self.voxels = [v for v in self.voxels if not (v["x"] == x and v["y"] == y and v["z"] == z)]
        self.voxels.append({"x": x, "y": y, "z": z, "color": color, "part": part})
        return self.voxels[-1]

    def remove_at(self, x, y, z):
        before = len(self.voxels)
        self.voxels = [v for v in self.voxels if not (v["x"] == x and v["y"] == y and v["z"] == z)]
        return len(self.voxels) < before

    def at(self, x, y, z):
        for v in self.voxels:
            if v["x"] == x and v["y"] == y and v["z"] == z:
                return v
        return None

    def parts(self):
        return sorted(set(v["part"] for v in self.voxels))

    def bounds(self):
        if not self.voxels:
            return (0, 0, 0, 0, 0, 0)
        xs = [v["x"] for v in self.voxels]
        ys = [v["y"] for v in self.voxels]
        zs = [v["z"] for v in self.voxels]
        return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))

    def to_mc_json(self, namespace="mod", item_id="item"):
        elements = []
        for v in self.voxels:
            x, y, z = v["x"], v["y"], v["z"]
            elements.append({
                "from": [x, y, z],
                "to": [x + 1, y + 1, z + 1],
                "faces": {
                    "up": {"texture": "#all", "cullface": "up"},
                    "down": {"texture": "#all", "cullface": "down"},
                    "north": {"texture": "#all", "cullface": "north"},
                    "south": {"texture": "#all", "cullface": "south"},
                    "west": {"texture": "#all", "cullface": "west"},
                    "east": {"texture": "#all", "cullface": "east"},
                },
            })
        return {
            "parent": "item/generated",
            "textures": {"all": f"{namespace}:item/{item_id}"},
            "elements": elements,
            "_editor_parts": {p: [v for v in self.voxels if v["part"] == p] for p in self.parts()},
        }

    def to_dict(self):
        return {"name": self.name, "voxels": list(self.voxels)}

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("name", "model"))
        obj.voxels = list(data.get("voxels", []))
        return obj
