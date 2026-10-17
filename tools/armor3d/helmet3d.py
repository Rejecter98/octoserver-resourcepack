"""A급 투구 2종 입체 모델 (머리에 쓴 모습 전용).
좌표: 아이템 모델 0~16 이 머리에서 10px(=호박 크기) → 머리 8px = 1.6~14.4, 모자 레이어 0.8~15.2.
앞 = 북쪽(-Z). 32x32 텍스처에 8x8 재질 칸(swatch) 16개, 면마다 재질 칸 하나를 씀."""
import json, os, random, sys
from PIL import Image

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
P = f"{REPO}/pack/assets"
TOOL = ["leather", "chainmail", "copper", "iron", "golden", "diamond", "netherite"]


def swatch_tex(path, mats, seed=7):
    """mats: {name: (slot, fn(x,y,rnd)->rgba)}"""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (32, 32))
    for name, (slot, fn) in mats.items():
        sx, sy = slot % 4, slot // 4
        for y in range(8):
            for x in range(8):
                img.putpixel((sx * 8 + x, sy * 8 + y), fn(x, y, rnd))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def knit(base, dark):
    return lambda x, y, r: (dark if (x % 2 == 0 and y % 3 == 0) or (x % 2 == 1 and y % 3 == 1) else base) + (255,)


def fur(base, light, dark):
    def f(x, y, r):
        k = r.random()
        return (light if k < 0.18 else dark if k < 0.32 else base) + (255,)
    return f


def flat(c, hi=None):
    return lambda x, y, r: (hi if hi and (x + y) % 7 == 0 else c) + (255,)


def uv(slot):
    sx, sy = slot % 4, slot // 4
    return [sx * 4 + 0.25, sy * 4 + 0.25, sx * 4 + 3.75, sy * 4 + 3.75]


def box(frm, to, slot, side_slot=None):
    faces = {}
    for f in ("north", "south", "east", "west", "up", "down"):
        s = slot if side_slot is None or f in ("north", "up") else side_slot
        faces[f] = {"uv": uv(s), "texture": "#0"}
    return {"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to], "faces": faces}


def mirror(e):
    a, b = e["from"], e["to"]
    m = json.loads(json.dumps(e))
    m["from"] = [round(16 - b[0], 3), a[1], a[2]]
    m["to"] = [round(16 - a[0], 3), b[1], b[2]]
    m["faces"]["east"], m["faces"]["west"] = e["faces"]["west"], e["faces"]["east"]
    return m


def model(sid, elements):
    d = {"textures": {"0": f"cosmetics:item/{sid}_head", "particle": f"cosmetics:item/{sid}_head"},
         "elements": elements,
         "display": {"head": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}}}
    with open(f"{P}/cosmetics/models/item/{sid}_head.json", "w") as f:
        json.dump(d, f, indent=1)
        f.write("\n")


# ---------------------------------------------------------------- 냥이 모자: 분홍 니트 비니 + 고양이 귀 + 방울
CAT = {"knit": (0, knit((255, 204, 222), (246, 180, 204))), "band": (1, knit((238, 160, 190), (224, 140, 172))),
       "ear": (2, fur((255, 204, 222), (255, 226, 238), (240, 186, 208))), "inner": (3, flat((255, 150, 182), (255, 180, 204))),
       "bell": (4, flat((255, 214, 90), (255, 244, 180))), "bell_d": (5, flat((214, 160, 50)))}
def cat():
    K, BAND, EAR, IN, BELL, BELLD = 0, 1, 2, 3, 4, 5
    e = [box([0.6, 8.6, 0.6], [15.4, 15.6, 15.4], K),
         box([0.3, 7.6, 0.3], [15.7, 9.4, 15.7], BAND)]
    ear = [box([2.0, 15.6, 6.5], [6.5, 17.1, 9.5], EAR),
           box([2.6, 17.1, 6.8], [5.9, 18.6, 9.2], EAR),
           box([3.2, 18.6, 7.1], [5.2, 19.8, 8.9], EAR),
           box([2.8, 15.7, 6.2], [5.6, 17.4, 6.5], IN),
           box([3.3, 17.4, 6.5], [5.2, 18.4, 6.8], IN)]
    e += ear + [mirror(x) for x in ear]
    e += [box([6.9, 6.6, -0.4], [9.1, 8.8, 0.3], BELL), box([7.6, 6.2, -0.5], [8.4, 6.8, 0.0], BELLD)]
    return e


# ---------------------------------------------------------------- 곰돌이 모자: 갈색 털 후드 + 둥근 귀 + 크림 얼굴 테두리
BEAR = {"fur": (0, fur((200, 148, 106), (222, 178, 138), (176, 122, 84))),
        "cream": (1, fur((244, 228, 204), (252, 244, 228), (232, 210, 180))),
        "inner": (2, flat((246, 186, 170), (252, 206, 192))), "nose": (3, flat((90, 60, 50)))}
def bear():
    F, C, IN = 0, 1, 2
    e = [box([0.6, 14.6, 0.6], [15.4, 15.8, 15.4], F),          # 정수리
         box([0.6, 1.8, 14.4], [15.4, 14.6, 15.4], F),          # 뒤
         box([0.6, 1.8, 0.6], [1.6, 14.6, 14.4], F),            # 왼쪽
         box([14.4, 1.8, 0.6], [15.4, 14.6, 14.4], F),          # 오른쪽
         box([1.0, 11.6, 0.2], [15.0, 14.6, 1.2], C),           # 얼굴 테두리 위
         box([0.6, 1.8, 0.2], [3.0, 11.6, 1.2], C),             # 테두리 왼쪽
         box([13.0, 1.8, 0.2], [15.4, 11.6, 1.2], C)]           # 테두리 오른쪽
    ear = [box([1.0, 14.0, 5.4], [5.6, 18.6, 8.6], F),
           box([2.0, 15.0, 5.1], [4.6, 17.6, 5.4], IN)]
    e += ear + [mirror(x) for x in ear]
    e += [box([6.5, 1.0, 14.6], [9.5, 3.6, 16.2], C)]           # 뒤 아래 동그란 꼬리 방울(후드 끈)
    return e


def item_entries(sid, th):
    for m in TOOL:
        p = f"{P}/minecraft/items/{m}_helmet.json"
        d = json.load(open(p))
        for e in d["model"]["entries"]:
            if e["threshold"] == th:
                old = e["model"]
                if old.get("type") == "minecraft:select":
                    break             # 이미 바뀜 (다시 돌려도 같은 결과)
                e["model"] = {"type": "minecraft:select", "property": "minecraft:display_context",
                              "cases": [{"when": "head", "model": {"type": "minecraft:model", "model": f"cosmetics:item/{sid}_head"}}],
                              "fallback": old}
                break
        else:
            raise SystemExit(f"{sid} entry missing in {m}_helmet")
        with open(p, "w") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    for sid, th, mats, fn in (("cat_ear_helmet", 100076, CAT, cat), ("bear_helmet", 100144, BEAR, bear)):
        swatch_tex(f"{P}/cosmetics/textures/item/{sid}_head.png", mats)
        els = fn()
        model(sid, els)
        if "--no-items" not in sys.argv:
            item_entries(sid, th)
        print(sid, len(els), "elements")
