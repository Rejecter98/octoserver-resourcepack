"""A급 갑옷 입은 모습 고해상도 (64x32 → 128x64). 모양(투명 마스크)은 그대로, 그림만 2배 디테일.
기존 64x32 를 2배로 키운 뒤 털결·단추·주머니·얼굴 등 디테일을 그린다.
UV(64x32 기준): 몸 앞 (20,20)-(28,32), 몸 뒤 (32,20)-(40,32), 팔 (40,16)~(56,32), 다리 (0,16)~(16,32), 다리 앞 (4,20)-(8,32), 발바닥 (8,16)-(12,20)."""
import random, shutil, os
from PIL import Image

E = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..") + "/pack/assets/cosmetics/textures/entity/equipment"
BK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orig")


def load2x(rel):
    src = f"{BK}/{rel}.png"
    if not os.path.exists(src):
        os.makedirs(os.path.dirname(src), exist_ok=True)
        shutil.copy(f"{E}/{rel}.png", src)          # 원본 64x32 보관 (다시 돌려도 같은 결과)
    im = Image.open(src).convert("RGBA")
    assert im.size == (64, 32), im.size
    return im.resize((128, 64), Image.NEAREST)


class Pen:
    def __init__(self, im):
        self.im, self.px = im, im.load()

    def alive(self, x, y):
        return 0 <= x < 128 and 0 <= y < 64 and self.px[x, y][3] > 0

    def dot(self, x, y, c, only_alive=True):
        if 0 <= x < 128 and 0 <= y < 64 and (not only_alive or self.alive(x, y)):
            self.px[x, y] = tuple(c) + (255,)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1):
            for x in range(x0, x1):
                self.dot(x, y, c)

    def circle(self, cx, cy, r, c, edge=None):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
                if d <= r:
                    self.dot(x, y, edge if edge and d > r - 1 else c)

    def texture(self, box, base_test, light, dark, seed, rate=(0.08, 0.08)):
        rnd = random.Random(seed)
        x0, y0, x1, y1 = box
        for y in range(y0, y1):
            for x in range(x0, x1):
                if self.alive(x, y) and base_test(self.px[x, y]):
                    k = rnd.random()
                    if k < rate[0]:
                        self.dot(x, y, light)
                    elif k < rate[0] + rate[1]:
                        self.dot(x, y, dark)


FUR_L, FUR_D = (214, 164, 122), (184, 132, 94)
CREAM, CREAM_D = (246, 232, 208), (220, 200, 170)
INK = (66, 46, 38)
is_fur = lambda p: p[0] > p[2] + 40 and p[0] < 235


def bear_humanoid():
    im = load2x("humanoid/bear_pajama"); p = Pen(im)
    p.texture((0, 0, 128, 64), is_fur, FUR_L, FUR_D, 11)
    # 몸 앞 (40..56, 40..58): 칼라·단추·주머니
    for x in range(40, 56):
        d = abs(x - 47.5)
        for y in range(40, 42 + int(max(0, 3 - d * 0.5))):
            p.dot(x, y, CREAM if y < 42 + int(max(0, 3 - d * 0.5)) - 1 else CREAM_D)
    for by in (45, 50, 55):
        p.circle(47.5, by + 0.5, 1.6, CREAM, (126, 86, 58))
    p.rect(50, 49, 55, 55, CREAM); [p.dot(x, 49, CREAM_D) for x in range(50, 55)]
    p.dot(50, 48, FUR_D); p.dot(54, 48, FUR_D); p.dot(51, 51, INK); p.dot(53, 51, INK); p.dot(52, 53, (240, 150, 160))
    # 몸 뒤 (64..80, 40..58): 하트 자수
    for (x, y) in ((70, 46), (71, 46), (73, 46), (74, 46), (69, 47), (70, 47), (71, 47), (72, 47), (73, 47), (74, 47), (75, 47),
                   (70, 48), (71, 48), (72, 48), (73, 48), (74, 48), (71, 49), (72, 49), (73, 49), (72, 50)):
        p.dot(x, y, (246, 170, 186))
    # 소매 끝 크림 밴드 (팔 아래 두 줄)
    for x in range(80, 112):
        for y in range(54, 56):
            p.dot(x, y, CREAM)
    # 슬리퍼 (다리 아래 52..64): 위 테두리 크림, 앞에 곰 얼굴, 발바닥 크림
    for x in range(0, 32):
        p.dot(x, 52, CREAM); p.dot(x, 53, CREAM_D)
    p.rect(8, 54, 16, 64, (200, 148, 106))
    p.rect(10, 58, 14, 62, CREAM); p.dot(9, 59, CREAM); p.dot(14, 59, CREAM)
    p.dot(9, 56, INK); p.dot(14, 56, INK); p.dot(11, 58, INK); p.dot(12, 58, INK); p.dot(11, 60, (240, 150, 160)); p.dot(12, 60, (240, 150, 160))
    p.dot(8, 54, FUR_D); p.dot(15, 54, FUR_D)
    p.rect(16, 32, 24, 40, CREAM_D)
    for (x, y) in ((19, 35), (20, 35), (18, 34), (21, 34), (19, 37), (20, 37)):
        p.dot(x, y, (200, 150, 120))
    return im


def bear_leggings():
    im = load2x("humanoid_leggings/bear_pajama"); p = Pen(im)
    p.texture((0, 0, 128, 64), is_fur, FUR_L, FUR_D, 12)
    for x in range(32, 80):                     # 허리 고무줄
        for y in range(54, 57):
            p.dot(x, y, CREAM if y < 56 else CREAM_D)
    for (x, y) in ((45, 56), (46, 57), (47, 57), (48, 57), (49, 57), (50, 56), (46, 58), (49, 58), (47, 59), (48, 59)):
        p.dot(x, y, (246, 160, 180))            # 리본 끈
    p.circle(72, 59.5, 2.6, CREAM, CREAM_D)      # 엉덩이 꼬리
    for x in range(0, 32):                       # 바짓단
        p.dot(x, 62, CREAM); p.dot(x, 63, CREAM_D)
    for (x, y) in ((10, 50), (13, 46), (2, 44), (26, 48)):   # 무릎 작은 발자국 무늬
        p.circle(x, y, 1.1, (186, 134, 96))
    return im


def duck_humanoid():
    im = load2x("humanoid/duck"); p = Pen(im)
    YL, YD, OR, ORD = (255, 240, 160), (230, 184, 60), (255, 160, 70), (214, 120, 40)
    p.texture((0, 48, 32, 64), lambda q: q[0] > 200 and q[1] > 150 and q[2] < 140, YL, YD, 21, (0.12, 0.06))
    for x in range(0, 32):                       # 장화 위 흰 테두리
        p.dot(x, 52, (255, 255, 255)); p.dot(x, 53, (236, 236, 244))
    p.dot(9, 55, INK); p.dot(14, 55, INK); p.dot(9, 54, (255, 255, 255)); p.dot(14, 54, (255, 255, 255))
    p.rect(9, 58, 15, 61, OR); p.rect(10, 61, 14, 62, ORD); [p.dot(x, 58, (255, 196, 120)) for x in range(10, 14)]
    for (x, y) in ((2, 56), (3, 57), (4, 57), (5, 58), (18, 56), (19, 57), (20, 57), (21, 58)):   # 옆 날개 깃
        p.dot(x, y, YL)
    p.rect(16, 32, 24, 40, OR)                   # 물갈퀴 밑창
    for (x0, y0) in ((17, 33), (20, 33), (22, 33)):
        for i in range(5):
            p.dot(x0 + (i // 3), y0 + i, ORD)
    return im


if __name__ == "__main__":
    for rel, fn in (("humanoid/bear_pajama", bear_humanoid), ("humanoid_leggings/bear_pajama", bear_leggings),
                    ("humanoid/duck", duck_humanoid)):
        im = fn()
        im.save(f"{E}/{rel}.png")
        print(rel, im.size)
