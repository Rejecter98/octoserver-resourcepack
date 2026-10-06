"""심해의 닻지기 '거품 감옥' 거품 (octo_ak_bubble) BetterModel 모델.
몹(발광 오징어, Scale 2.2) 위에 입혀짐 → 모델 크기는 기본 1블록, 실제로는 약 2.2블록 거품.
테두리만 그리고 가운데는 투명 → 안에 갇힌 플레이어가 보임.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from bblib import build, C

OUT = sys.argv[1] if len(sys.argv) > 1 else "models/octo_ak_bubble.bbmodel"
BONES = [("glow_bubble", [0, 8, 0], None)]
CUBES = [
    ("x", "glow_bubble", [-8, 2, -6], [8, 14, 6], "film"),
    ("z", "glow_bubble", [-6, 2, -8], [6, 14, 8], "film"),
    ("y", "glow_bubble", [-6, 0, -6], [6, 16, 6], "film"),
]
MATS = {"film": (C(170, 230, 255), C(120, 200, 240), C(255, 255, 255), "flat")}
CLEAR = (0, 0, 0, 0)


def deco(n, face, px, w, h, m):
    film, rim, hi = (200, 240, 255, 18), (150, 215, 250, 150), (255, 255, 255, 255)
    out = [[film] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            edge = x in (0, w - 1) or y in (0, h - 1)
            corner = x in (0, w - 1) and y in (0, h - 1)
            if corner:
                out[y][x] = CLEAR
            elif edge:
                out[y][x] = rim
    for (x, y) in ((2, 2), (3, 2), (2, 3)):  # 반짝이
        if x < w - 1 and y < h - 1:
            out[y][x] = hi
    if w > 6 and h > 6:
        out[h - 3][w - 3] = (220, 248, 255, 200)
    return out


ANIMS = {
    "idle": (1.6, "loop", {"glow_bubble": {"scale": [(0, (1, 1, 1)), (0.8, (1.05, 0.96, 1.05)), (1.6, (1, 1, 1))],
                                           "position": [(0, (0, 0, 0)), (0.8, (0, 0.4, 0)), (1.6, (0, 0, 0))]}}),
    "spawn": (0.4, "once", {"glow_bubble": {"scale": [(0, (0.2, 0.2, 0.2)), (0.3, (1.1, 1.1, 1.1)), (0.4, (1, 1, 1))]}}),
    "damage": (0.25, "once", {"glow_bubble": {"scale": [(0, (1, 1, 1)), (0.1, (0.9, 1.1, 0.9)), (0.25, (1, 1, 1))]}}),
    "death": (0.3, "hold", {"glow_bubble": {"scale": [(0, (1, 1, 1)), (0.15, (1.3, 1.3, 1.3)), (0.3, (0.01, 0.01, 0.01))]}}),
}

if __name__ == "__main__":
    build(OUT, "octo_ak_bubble", BONES, CUBES, MATS, ANIMS, deco)
