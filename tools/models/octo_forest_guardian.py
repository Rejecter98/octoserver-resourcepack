"""숲의 수호자 BetterModel .bbmodel 생성기 (큐브·텍스처·애니메이션)."""
import base64, io, json, random, sys, uuid
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "models/octo_forest_guardian.bbmodel"
TEX_W, TEX_H = 128, 64
NS = uuid.UUID("6f6f6f6f-0000-4000-8000-00000000f9a1")
uid = lambda s: str(uuid.uuid5(NS, s))

# ---------------- 뼈대 (이름, pivot, 부모) — 앞 = 북쪽(-Z)
BONES = [
    ("body", [0, 0, 0], None),
    ("left_leg", [-3.5, 10, 0], "body"),
    ("right_leg", [3.5, 10, 0], "body"),
    ("torso", [0, 10, 0], "body"),
    ("h_head", [0, 25, 0], "torso"),
    ("sprout", [0, 34, 0], "h_head"),
    ("glow_eyes", [0, 29, -4], "h_head"),
    ("right_arm", [8.5, 23, 0], "torso"),
    ("right_forearm", [8.5, 13, 0], "right_arm"),
    ("hammer", [8.5, 8.5, 0], "right_forearm"),
    ("left_arm", [-8.5, 23, 0], "torso"),
    ("left_forearm", [-8.5, 13, 0], "left_arm"),
]

# ---------------- 큐브 (이름, 뼈, from, to, 재질)
CUBES = [
    ("leg_l", "left_leg", [-6, 2, -2.5], [-1, 10, 2.5], "bark"),
    ("foot_l", "left_leg", [-6.5, 0, -4], [-0.5, 2, 3], "root"),
    ("leg_r", "right_leg", [1, 2, -2.5], [6, 10, 2.5], "bark"),
    ("foot_r", "right_leg", [0.5, 0, -4], [6.5, 2, 3], "root"),
    ("trunk", "torso", [-6, 10, -4.5], [6, 23, 4.5], "trunk"),
    ("mantle", "torso", [-7, 21, -5.5], [7, 25, 5.5], "moss"),
    ("mush_stem1", "torso", [2, 14, 4.5], [4, 16, 6.5], "mush_stem"),
    ("mush_cap1", "torso", [1, 16, 4.5], [5, 18, 8.5], "mush_cap"),
    ("mush_stem2", "torso", [-4, 12, 4.5], [-3, 13, 5.5], "mush_stem"),
    ("mush_cap2", "torso", [-5, 13, 4.5], [-2, 14, 7.5], "mush_cap"),
    ("head", "h_head", [-4.5, 25, -4], [4.5, 33, 4], "head"),
    ("crown", "h_head", [-5, 32, -4.5], [5, 34, 4.5], "leaf"),
    ("tuft_l", "h_head", [-5.5, 33, -2], [-2.5, 35, 2], "leaf"),
    ("tuft_r", "h_head", [2.5, 33, -2], [5.5, 35, 2], "leaf"),
    ("sprout_stem", "sprout", [-0.5, 34, -0.5], [0.5, 37, 0.5], "stem"),
    ("sprout_leaf_l", "sprout", [-3, 36, -1], [-0.5, 37, 1], "leaf_bright"),
    ("sprout_leaf_r", "sprout", [0.5, 37, -1], [3, 38, 1], "leaf_bright"),
    ("eye_l", "glow_eyes", [-3.5, 28, -4.1], [-1.5, 30, -4.0], "eye"),
    ("eye_r", "glow_eyes", [1.5, 28, -4.1], [3.5, 30, -4.0], "eye"),
    ("pad_r", "right_arm", [6, 22, -3], [11, 25, 3], "moss"),
    ("arm_r", "right_arm", [6.5, 13, -2], [10.5, 22, 2], "bark"),
    ("twig_r", "right_arm", [10.5, 17, -0.5], [12.5, 18, 0.5], "stem"),
    ("twig_leaf_r", "right_arm", [12, 18, -1], [14, 19, 1], "leaf_bright"),
    ("fist_r", "right_forearm", [6, 6, -2.5], [11, 13, 2.5], "bark_dark"),
    ("handle", "hammer", [7.5, 7.5, -13], [9.5, 9.5, 1], "handle"),
    ("hammer_head", "hammer", [5, 3.5, -19], [12, 13.5, -13], "log"),
    ("pad_l", "left_arm", [-11, 22, -3], [-6, 25, 3], "moss"),
    ("arm_l", "left_arm", [-10.5, 13, -2], [-6.5, 22, 2], "bark"),
    ("twig_l", "left_arm", [-12.5, 18, -0.5], [-10.5, 19, 0.5], "stem"),
    ("fist_l", "left_forearm", [-11, 6, -2.5], [-6, 13, 2.5], "bark_dark"),
    ("flower_l", "left_forearm", [-10, 13, -1], [-7, 14, 1], "flower"),
]

# ---------------- 텍스처
R = random.Random(7)
C = lambda *a: tuple(a) + (255,)
PAL = {
    "bark": [C(118, 88, 60), C(96, 70, 48), C(140, 106, 72)],
    "bark_dark": [C(104, 76, 52), C(82, 60, 42), C(126, 94, 64)],
    "trunk": [C(124, 92, 62), C(98, 72, 50), C(146, 110, 76)],
    "root": [C(108, 80, 56), C(86, 62, 44), C(130, 98, 68)],
    "moss": [C(110, 168, 78), C(80, 132, 58), C(146, 202, 104)],
    "leaf": [C(92, 172, 90), C(64, 134, 68), C(134, 212, 114)],
    "leaf_bright": [C(132, 214, 108), C(98, 178, 86), C(176, 236, 140)],
    "stem": [C(120, 170, 80), C(96, 140, 64), C(150, 196, 104)],
    "head": [C(176, 136, 92), C(150, 112, 74), C(198, 158, 110)],
    "mush_cap": [C(236, 128, 138), C(206, 100, 112), C(250, 160, 168)],
    "mush_stem": [C(240, 228, 206), C(216, 200, 176), C(250, 244, 230)],
    "handle": [C(198, 162, 112), C(164, 128, 84), C(220, 188, 140)],
    "log": [C(122, 90, 60), C(96, 70, 48), C(146, 110, 74)],
    "flower": [C(255, 186, 210), C(240, 150, 186), C(255, 226, 120)],
    "eye": [C(200, 255, 150), C(170, 240, 120), C(240, 255, 214)],
}
PINK, YEL, WHITE, DARK = C(255, 176, 200), C(255, 226, 120), C(255, 248, 240), C(58, 40, 28)


def paint(mat, face, w, h, name):
    b, d, l = PAL[mat]
    px = [[b] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r = R.random()
            if mat in ("bark", "bark_dark", "trunk", "root", "log") and face not in ("up", "down"):
                # 세로 나뭇결
                px[y][x] = d if (x * 7 + (y // 3) * 3) % 5 == 0 else (l if r < 0.12 else b)
            elif mat in ("moss", "leaf", "leaf_bright", "stem"):
                px[y][x] = l if r < 0.22 else (d if r > 0.85 else b)
            elif mat in ("head", "handle", "mush_stem"):
                px[y][x] = l if r < 0.1 else (d if r > 0.93 else b)
            else:
                px[y][x] = l if r < 0.15 else (d if r > 0.9 else b)
    if mat in ("log", "bark", "trunk", "bark_dark", "root") and face in ("up", "down"):  # 나이테
        cx, cy = (w - 1) / 2, (h - 1) / 2
        for y in range(h):
            for x in range(w):
                rr = max(abs(x - cx), abs(y - cy))
                px[y][x] = C(206, 170, 118) if int(rr) % 2 == 0 else C(176, 138, 92)
                if rr >= max(cx, cy) - 0.1:
                    px[y][x] = d
    if mat == "moss":
        if face not in ("up", "down"):  # 아래로 늘어진 이끼 끝
            for x in range(w):
                if (x * 5) % 3 == 0:
                    px[h - 1][x] = d
        if face == "up":
            for y in range(h):
                for x in range(w):
                    if (x * 3 + y * 5) % 11 == 0:
                        px[y][x] = PINK if (x + y) % 2 else YEL
    if mat == "mush_cap" and face != "down":
        for y in range(h):
            for x in range(w):
                if (x * 2 + y * 3) % 5 == 0:
                    px[y][x] = WHITE
    if mat == "mush_cap" and face == "down":
        px = [[C(240, 210, 196)] * w for _ in range(h)]
    if mat == "flower":
        px = [[PINK] * w for _ in range(h)]
        if face == "up":
            px[h // 2][w // 2] = YEL
    if mat == "eye":
        px = [[PAL["eye"][0]] * w for _ in range(h)]
        px[0][0 if name == "eye_l" else w - 1] = PAL["eye"][2]
    if name == "head" and face == "north":  # 얼굴 (북쪽 면: 열 0 = +X)
        px = [[PAL["head"][0] if R.random() > 0.1 else PAL["head"][2] for _ in range(w)] for _ in range(h)]
        for (c0, c1) in ((1, 3), (6, 8)):  # 눈 구멍 (발광 눈 큐브가 위에 겹침)
            for y in range(2, 6):
                for x in range(c0 - 1, c1 + 1):
                    if 0 <= x < w and not (y in (2, 5) and x in (c0 - 1, c1)):
                        px[y][x] = DARK
        for x in (0, 8):  # 볼터치
            px[6][x] = PINK
        for x in (3, 4, 5):  # 미소
            px[7][x] = DARK
        px[6][2] = px[6][6] = DARK
    if name == "trunk" and face == "north":  # 옹이 + 꽃
        for y in range(5, 9):
            for x in range(5, 8):
                if not (y in (5, 8) and x in (5, 7)):
                    px[y][x] = DARK
        px[2][2] = PINK; px[2][3] = YEL; px[1][2] = PINK; px[3][2] = PINK; px[2][1] = PINK
    return px


FACES = ("north", "east", "south", "west", "up", "down")


def face_size(f, t, face):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy),
            "up": (dx, dz), "down": (dx, dz)}[face]


# 면별 UV 배치 (선반 방식)
img = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
reqs = []
for name, bone, f, t, mat in CUBES:
    for face in FACES:
        w, h = face_size(f, t, face)
        if mat == "eye" and face != "north":
            continue
        reqs.append((name, face, max(1, round(w)), max(1, round(h)), mat))
reqs.sort(key=lambda r: (-r[3], -r[2]))
x = y = rowh = 0
uvs = {}
for name, face, w, h, mat in reqs:
    if x + w > TEX_W:
        x, y, rowh = 0, y + rowh, 0
    if y + h > TEX_H:
        raise SystemExit("텍스처 공간 부족")
    uvs[(name, face)] = [x, y, x + w, y + h]
    for yy, row in enumerate(paint(mat, face, w, h, name)):
        for xx, c in enumerate(row):
            img.putpixel((x + xx, y + yy), c)
    x += w
    rowh = max(rowh, h)
print("텍스처 사용 높이", y + rowh, "/", TEX_H, "· 큐브", len(CUBES))

# ---------------- 애니메이션 (Blockbench 값: 회전 x+ = 앞으로 숙임/팔 뒤로, x- = 팔 앞으로 듦, z+ = 오른팔 바깥)
L = "linear"
ANIMS = {}


def anim(name, length, loop, tracks):
    ANIMS[name] = (length, loop, tracks)


HAM = 8
DY = 6  # 망치 기본 각도 (머리가 아래로)
anim("idle", 2.4, "loop", {
    "torso": {"position": [(0, (0, 0, 0)), (1.2, (0, -0.4, 0)), (2.4, (0, 0, 0))],
              "rotation": [(0, (0, 0, 0)), (1.2, (2, 0, 0)), (2.4, (0, 0, 0))]},
    "h_head": {"rotation": [(0, (0, 0, 0)), (1.2, (-3, 0, 0)), (2.4, (0, 0, 0))]},
    "sprout": {"rotation": [(0, (0, 0, -8)), (1.2, (0, 0, 8)), (2.4, (0, 0, -8))]},
    "right_arm": {"rotation": [(0, (-8, 0, 3)), (1.2, (-10, 0, 5)), (2.4, (-8, 0, 3))]},
    "left_arm": {"rotation": [(0, (0, 0, -3)), (1.2, (-3, 0, -5)), (2.4, (0, 0, -3))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (2.4, (HAM, 0, 0))]},
})
anim("walk", 1.2, "loop", {
    "left_leg": {"rotation": [(0, (-25, 0, 0)), (0.6, (25, 0, 0)), (1.2, (-25, 0, 0))]},
    "right_leg": {"rotation": [(0, (25, 0, 0)), (0.6, (-25, 0, 0)), (1.2, (25, 0, 0))]},
    "torso": {"rotation": [(0, (4, 0, -3)), (0.6, (4, 0, 3)), (1.2, (4, 0, -3))],
              "position": [(0, (0, 0, 0)), (0.3, (0, 0.6, 0)), (0.6, (0, 0, 0)), (0.9, (0, 0.6, 0)), (1.2, (0, 0, 0))]},
    "right_arm": {"rotation": [(0, (5, 0, 3)), (0.6, (-25, 0, 3)), (1.2, (5, 0, 3))]},
    "left_arm": {"rotation": [(0, (-20, 0, -3)), (0.6, (15, 0, -3)), (1.2, (-20, 0, -3))]},
    "sprout": {"rotation": [(0, (0, 0, -10)), (0.6, (0, 0, 10)), (1.2, (0, 0, -10))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (1.2, (HAM, 0, 0))]},
})
anim("attack", 0.8, "once", {
    "right_arm": {"rotation": [(0, (-8, 0, 3)), (0.3, (-150, 0, 5)), (0.45, (-75, 0, 0)), (0.8, (-8, 0, 3))]},
    "right_forearm": {"rotation": [(0, (0, 0, 0)), (0.3, (-30, 0, 0)), (0.45, (0, 0, 0)), (0.8, (0, 0, 0))]},
    "torso": {"rotation": [(0, (0, 0, 0)), (0.3, (-8, -15, 0)), (0.45, (14, 10, 0)), (0.8, (0, 0, 0))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (0.3, (90, 0, 0)), (0.45, (90, 0, 0)), (0.8, (HAM, 0, 0))]},
})
# 내려찍기: 0~0.4 들어올림 → 1.5초까지 예고 유지(떨림) → 1.6 내려찍음 (스킬 delay 32틱과 맞춤)
anim("slam", 2.3, "once", {
    "right_arm": {"rotation": [(0, (-8, 0, 3)), (0.4, (-170, 0, -8)), (1.5, (-172, 0, -8)), (1.62, (-88, 0, 0)), (2.0, (-88, 0, 0)), (2.3, (-8, 0, 3))]},
    "left_arm": {"rotation": [(0, (0, 0, -3)), (0.4, (-170, 0, 8)), (1.5, (-172, 0, 8)), (1.62, (-88, 0, 0)), (2.0, (-88, 0, 0)), (2.3, (0, 0, -3))]},
    "right_forearm": {"rotation": [(0, (0, 0, 0)), (0.4, (-20, 0, 0)), (1.5, (-20, 0, 0)), (1.62, (0, 0, 0)), (2.3, (0, 0, 0))]},
    "left_forearm": {"rotation": [(0, (0, 0, 0)), (0.4, (-20, 0, 0)), (1.5, (-20, 0, 0)), (1.62, (0, 0, 0)), (2.3, (0, 0, 0))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (0.4, (90, 0, 0)), (1.62, (90, 0, 0)), (2.0, (90, 0, 0)), (2.3, (HAM, 0, 0))]},
    "torso": {"rotation": [(0, (0, 0, 0)), (0.4, (-12, 0, 0)), (0.8, (-13, 0, 1.5)), (1.0, (-13, 0, -1.5)), (1.2, (-13, 0, 1.5)), (1.5, (-13, 0, 0)), (1.62, (24, 0, 0)), (2.0, (24, 0, 0)), (2.3, (0, 0, 0))],
              "position": [(0, (0, 0, 0)), (1.5, (0, 0, 0)), (1.62, (0, -2, 0)), (2.0, (0, -2, 0)), (2.3, (0, 0, 0))]},
    "h_head": {"rotation": [(0, (0, 0, 0)), (0.4, (-10, 0, 0)), (1.5, (-10, 0, 0)), (1.62, (10, 0, 0)), (2.3, (0, 0, 0))]},
    "left_leg": {"rotation": [(0, (0, 0, 0)), (1.5, (0, 0, 0)), (1.62, (-20, 0, 0)), (2.0, (-20, 0, 0)), (2.3, (0, 0, 0))]},
    "right_leg": {"rotation": [(0, (0, 0, 0)), (1.5, (0, 0, 0)), (1.62, (12, 0, 0)), (2.0, (12, 0, 0)), (2.3, (0, 0, 0))]},
})
# 뿌리 덫: 웅크리며 두 손을 땅에 꽂음 (0.5) → 1.5 까지 유지(맥동) → 복귀
anim("root_bind", 2.0, "once", {
    "torso": {"rotation": [(0, (0, 0, 0)), (0.5, (30, 0, 0)), (1.0, (33, 0, 0)), (1.5, (30, 0, 0)), (2.0, (0, 0, 0))],
              "position": [(0, (0, 0, 0)), (0.5, (0, -3, 0)), (1.5, (0, -3, 0)), (2.0, (0, 0, 0))]},
    "right_arm": {"rotation": [(0, (-8, 0, 3)), (0.5, (-55, 0, 10)), (1.5, (-55, 0, 10)), (2.0, (-8, 0, 3))]},
    "left_arm": {"rotation": [(0, (0, 0, -3)), (0.5, (-55, 0, -10)), (1.5, (-55, 0, -10)), (2.0, (0, 0, -3))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (0.5, (60, 0, 0)), (1.5, (60, 0, 0)), (2.0, (HAM, 0, 0))]},
    "left_leg": {"rotation": [(0, (0, 0, 0)), (0.5, (-25, 0, 0)), (1.5, (-25, 0, 0)), (2.0, (0, 0, 0))]},
    "right_leg": {"rotation": [(0, (0, 0, 0)), (0.5, (-25, 0, 0)), (1.5, (-25, 0, 0)), (2.0, (0, 0, 0))]},
    "h_head": {"rotation": [(0, (0, 0, 0)), (0.5, (-20, 0, 0)), (1.5, (-20, 0, 0)), (2.0, (0, 0, 0))]},
})
# 새싹 소환: 팔을 벌리고 하늘을 봄, 머리 새싹이 커짐
anim("summon", 1.6, "once", {
    "right_arm": {"rotation": [(0, (-8, 0, 3)), (0.4, (-20, 0, 75)), (1.2, (-20, 0, 80)), (1.6, (-8, 0, 3))]},
    "left_arm": {"rotation": [(0, (0, 0, -3)), (0.4, (-20, 0, -75)), (1.2, (-20, 0, -80)), (1.6, (0, 0, -3))]},
    "h_head": {"rotation": [(0, (0, 0, 0)), (0.4, (-25, 0, 0)), (1.2, (-25, 0, 0)), (1.6, (0, 0, 0))]},
    "torso": {"rotation": [(0, (0, 0, 0)), (0.4, (-8, 0, 0)), (1.2, (-8, 0, 0)), (1.6, (0, 0, 0))]},
    "sprout": {"scale": [(0, (1, 1, 1)), (0.4, (1.6, 1.6, 1.6)), (1.2, (1.6, 1.6, 1.6)), (1.6, (1, 1, 1))],
               "rotation": [(0, (0, 0, 0)), (0.6, (0, 0, 10)), (0.9, (0, 0, -10)), (1.2, (0, 0, 0))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (0.4, (80, 0, 0)), (1.2, (80, 0, 0)), (1.6, (HAM, 0, 0))]},
})
# 페이즈 2 포효
anim("roar", 2.0, "once", {
    "torso": {"rotation": [(0, (0, 0, 0)), (0.3, (10, 0, 0)), (0.6, (-20, 0, 0)), (0.75, (-20, 0, 2)), (0.9, (-20, 0, -2)), (1.05, (-20, 0, 2)), (1.2, (-20, 0, -2)), (1.5, (-20, 0, 0)), (2.0, (0, 0, 0))]},
    "h_head": {"rotation": [(0, (0, 0, 0)), (0.6, (-30, 0, 0)), (1.5, (-30, 0, 0)), (2.0, (0, 0, 0))]},
    "right_arm": {"rotation": [(0, (-8, 0, 3)), (0.3, (10, 0, 10)), (0.6, (-40, 0, 55)), (1.5, (-40, 0, 55)), (2.0, (-8, 0, 3))]},
    "left_arm": {"rotation": [(0, (0, 0, -3)), (0.3, (10, 0, -10)), (0.6, (-40, 0, -55)), (1.5, (-40, 0, -55)), (2.0, (0, 0, -3))]},
    "right_forearm": {"rotation": [(0, (0, 0, 0)), (0.6, (-35, 0, 0)), (1.5, (-35, 0, 0)), (2.0, (0, 0, 0))]},
    "left_forearm": {"rotation": [(0, (0, 0, 0)), (0.6, (-35, 0, 0)), (1.5, (-35, 0, 0)), (2.0, (0, 0, 0))]},
    "sprout": {"scale": [(0, (1, 1, 1)), (0.6, (1.4, 1.4, 1.4)), (1.5, (1.4, 1.4, 1.4)), (2.0, (1, 1, 1))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (0.6, (60, 0, 0)), (1.5, (60, 0, 0)), (2.0, (HAM, 0, 0))]},
})
anim("damage", 0.3, "once", {
    "torso": {"rotation": [(0, (0, 0, 0)), (0.1, (-7, 0, 0)), (0.3, (0, 0, 0))]},
    "h_head": {"rotation": [(0, (0, 0, 0)), (0.1, (-6, 0, 0)), (0.3, (0, 0, 0))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (0.3, (HAM, 0, 0))]},
})
anim("spawn", 1.5, "once", {
    "body": {"position": [(0, (0, -14, 0)), (0.9, (0, 0, 0)), (1.5, (0, 0, 0))]},
    "torso": {"rotation": [(0, (25, 0, 0)), (0.9, (10, 0, 0)), (1.2, (-6, 0, 0)), (1.5, (0, 0, 0))]},
    "h_head": {"rotation": [(0, (20, 0, 0)), (0.9, (0, 0, -8)), (1.1, (0, 0, 8)), (1.3, (0, 0, 0)), (1.5, (0, 0, 0))]},
    "sprout": {"scale": [(0, (0.3, 0.3, 0.3)), (1.1, (0.3, 0.3, 0.3)), (1.4, (1.2, 1.2, 1.2)), (1.5, (1, 1, 1))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (1.5, (HAM, 0, 0))]},
})
# 사망: 비틀 → 무릎 → 앞으로 쓰러짐 (마지막 자세 유지)
anim("death", 2.4, "hold", {
    "body": {"rotation": [(0, (0, 0, 0)), (0.5, (-6, 0, 0)), (1.0, (10, 0, 3)), (1.9, (88, 0, 4)), (2.1, (82, 0, 4)), (2.4, (88, 0, 4))],
             "position": [(0, (0, 0, 0)), (1.0, (0, -2, 0)), (1.9, (0, DY, 0)), (2.4, (0, DY, 0))]},
    "left_leg": {"rotation": [(0, (0, 0, 0)), (1.0, (-30, 0, 0)), (1.9, (0, 0, 0)), (2.4, (0, 0, 0))]},
    "right_leg": {"rotation": [(0, (0, 0, 0)), (1.0, (-20, 0, 0)), (1.9, (0, 0, 0)), (2.4, (0, 0, 0))]},
    "right_arm": {"rotation": [(0, (-8, 0, 3)), (1.0, (10, 0, 15)), (1.9, (-160, 0, 25)), (2.4, (-160, 0, 25))]},
    "left_arm": {"rotation": [(0, (0, 0, -3)), (1.0, (10, 0, -15)), (1.9, (-160, 0, -25)), (2.4, (-160, 0, -25))]},
    "h_head": {"rotation": [(0, (0, 0, 0)), (1.0, (20, 0, 10)), (2.4, (-20, 0, 25))]},
    "sprout": {"rotation": [(0, (0, 0, 0)), (1.9, (0, 0, 0)), (2.4, (0, 0, 70))],
               "scale": [(0, (1, 1, 1)), (1.9, (1, 1, 1)), (2.4, (0.7, 0.7, 0.7))]},
    "hammer": {"rotation": [(0, (HAM, 0, 0)), (1.0, (70, 0, 0)), (1.9, (0, 0, 0)), (2.4, (0, 0, 0))]},
})

# ---------------- bbmodel 출력
buf = io.BytesIO(); img.save(buf, "PNG")
pivot = {b: p for b, p, _ in BONES}
elements = []
for name, bone, f, t, mat in CUBES:
    faces = {}
    for face in FACES:
        if (name, face) in uvs:
            faces[face] = {"uv": uvs[(name, face)], "texture": 0}
        else:
            faces[face] = {"uv": [0, 0, 0, 0], "texture": None}
    elements.append({"name": name, "box_uv": False, "rescale": False, "locked": False, "light_emission": 0,
                     "render_order": "default", "allow_mirror_modeling": True, "from": f, "to": t, "autouv": 0,
                     "color": 0, "origin": pivot[bone], "faces": faces, "type": "cube", "uuid": uid("e:" + name)})


def group(b):
    kids = [uid("e:" + n) for n, bb, *_ in CUBES if bb == b]
    kids += [group(c) for c, _, p in BONES if p == b]
    return {"name": b, "origin": pivot[b], "color": 0, "uuid": uid("g:" + b), "export": True, "mirror_uv": False,
            "isOpen": True, "locked": False, "visibility": True, "autouv": 0, "selected": False, "children": kids}


fmt = lambda v: str(round(v, 4))
animations = []
for an, (length, loop, tracks) in ANIMS.items():
    animators = {}
    for bone, chans in tracks.items():
        kfs = []
        for ch, pts in chans.items():
            for tm, v in pts:
                kfs.append({"channel": ch, "data_points": [{"x": fmt(v[0]), "y": fmt(v[1]), "z": fmt(v[2])}],
                            "uuid": uid(f"k:{an}:{bone}:{ch}:{tm}"), "time": tm, "color": -1, "interpolation": L})
        animators[uid("g:" + bone)] = {"name": bone, "type": "bone", "keyframes": kfs}
    animations.append({"uuid": uid("a:" + an), "name": an, "loop": loop, "override": False, "length": length,
                       "snapping": 20, "selected": False, "anim_time_update": "", "blend_weight": "",
                       "start_delay": "", "loop_delay": "", "animators": animators})

model = {
    "meta": {"format_version": "4.10", "model_format": "free", "box_uv": False},
    "name": "octo_forest_guardian", "model_identifier": "", "visible_box": [2, 3, 0],
    "variable_placeholders": "", "variable_placeholder_buttons": [], "timeline_setups": [],
    "unhandled_root_fields": {}, "resolution": {"width": TEX_W, "height": TEX_H},
    "elements": elements, "outliner": [group("body")],
    "textures": [{"path": "", "name": "octo_forest_guardian.png", "folder": "", "namespace": "", "id": "0",
                  "group": "", "width": TEX_W, "height": TEX_H, "uv_width": TEX_W, "uv_height": TEX_H,
                  "particle": False, "use_as_default": False, "layers_enabled": False, "sync_to_project": "",
                  "render_mode": "default", "render_sides": "auto", "pbr_channel": "color", "frame_time": 1,
                  "frame_order_type": "loop", "frame_order": "", "frame_interpolate": False, "visible": True,
                  "internal": True, "saved": False, "uuid": uid("tex"),
                  "source": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}],
    "animations": animations,
}
json.dump(model, open(OUT, "w"), indent=1, ensure_ascii=False)
print("ok", OUT, "애니메이션", list(ANIMS))
