class Animation:
    def __init__(self, name="idle", duration=40, loop=True):
        self.name = name
        self.duration = duration
        self.loop = loop
        self.tracks = {}

    def add_keyframe(self, part, time, pos=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
        if part not in self.tracks:
            self.tracks[part] = []
        frames = self.tracks[part]
        frames = [f for f in frames if f["time"] != time]
        frames.append({"time": time, "pos": list(pos), "rot": list(rot), "scale": scale})
        frames.sort(key=lambda f: f["time"])
        self.tracks[part] = frames

    def remove_keyframe(self, part, time):
        if part in self.tracks:
            self.tracks[part] = [f for f in self.tracks[part] if f["time"] != time]

    def keyframes_at(self, time):
        result = {}
        for part, frames in self.tracks.items():
            for f in frames:
                if f["time"] == time:
                    result[part] = f
                    break
        return result

    def sample(self, tick):
        result = {}
        for part, frames in self.tracks.items():
            if not frames:
                continue
            if tick <= frames[0]["time"]:
                result[part] = frames[0]
                continue
            if tick >= frames[-1]["time"]:
                result[part] = frames[-1]
                continue
            for i in range(len(frames) - 1):
                a, b = frames[i], frames[i + 1]
                if a["time"] <= tick <= b["time"]:
                    t = (tick - a["time"]) / float(b["time"] - a["time"]) if b["time"] != a["time"] else 0
                    ease = t * t * (3 - 2 * t)
                    result[part] = {
                        "time": tick,
                        "pos": [a["pos"][k] + (b["pos"][k] - a["pos"][k]) * ease for k in range(3)],
                        "rot": [a["rot"][k] + (b["rot"][k] - a["rot"][k]) * ease for k in range(3)],
                        "scale": a["scale"] + (b["scale"] - a["scale"]) * ease,
                    }
                    break
        return result

    def all_times(self):
        times = set()
        for frames in self.tracks.values():
            for f in frames:
                times.add(f["time"])
        return sorted(times)

    def to_mc_json(self):
        return {
            "animation": {
                "frametime": 1,
                "duration": self.duration,
                "loop": self.loop,
                "bones": {
                    part: {
                        "rotation": {
                            "vector": [0, 0, 0],
                            "keyframes": [
                                {"time": f["time"], "value": f["rot"]} for f in frames
                            ],
                        },
                        "position": {
                            "keyframes": [
                                {"time": f["time"], "value": [p / 16.0 for p in f["pos"]]} for f in frames
                            ],
                        },
                        "scale": {
                            "keyframes": [
                                {"time": f["time"], "value": [f["scale"], f["scale"], f["scale"]]} for f in frames
                            ],
                        },
                    }
                    for part, frames in self.tracks.items()
                },
            }
        }

    def to_dict(self):
        return {
            "name": self.name,
            "duration": self.duration,
            "loop": self.loop,
            "tracks": {k: list(v) for k, v in self.tracks.items()},
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("name", "idle"), data.get("duration", 40), data.get("loop", True))
        obj.tracks = {k: list(v) for k, v in data.get("tracks", {}).items()}
        return obj
