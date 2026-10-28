"""OctoPet 교감 메뉴 배경 · 버튼 아이콘 · 감정 말풍선 (리소스팩 assets/octopet)"""
import json, os, sys
from PIL import Image, ImageDraw

OUT = sys.argv[1]
A = os.path.join(OUT, 'assets/octopet')
for d in ['textures/gui', 'textures/item/ui', 'textures/font', 'models/item/ui', 'items/ui', 'font']:
    os.makedirs(os.path.join(A, d), exist_ok=True)

def C(h, a=255):
    h = h.lstrip('#'); return (int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16), a)

CREAM, CREAM2, PINK, PINK2, PINKD, BROWN, BROWNL, MINT, WHITE = map(C, ['#fbf4e8', '#f4e9d6', '#f9cfd8', '#f5b6c6', '#e58aa3', '#5a4038', '#b8987d', '#dcefe2', '#fffdf8'])

# ---------------------------------------------------------------- 배경 176x74 (3줄)
W, H = 176, 74
bg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(bg)
d.rectangle([0, 0, W - 1, H - 1], fill=BROWN)
d.rectangle([1, 1, W - 2, H - 2], fill=CREAM)
d.rectangle([3, 3, W - 4, 14], fill=PINK)          # 제목 띠
d.line([3, 14, W - 4, 14], fill=PINK2)
for x in range(140, 170, 9):                      # 띠 오른쪽 발바닥
    d.ellipse([x, 6, x + 4, 10], fill=WHITE); d.point([x, 5], fill=WHITE); d.point([x + 4, 5], fill=WHITE)
# 1줄: 펫 액자 (가운데) + 양옆 민트 띠
d.rectangle([3, 17, W - 4, 34], fill=MINT)
# 2줄: 버튼 칸 7개 (10~16)
d.rectangle([3, 35, W - 4, 52], fill=CREAM2)
# 3줄: 하트 리본 (19~25) + 양끝 칸 (18 레벨, 26 뒤로)
d.rectangle([3, 53, W - 4, 70], fill=MINT)
d.rectangle([25, 56, 150, 67], fill=PINK)
d.line([25, 56, 150, 56], fill=PINK2); d.line([25, 67, 150, 67], fill=PINK2)

def frame(c, r, fill=WHITE, edge=BROWNL, round_=True):
    x, y = 7 + 18 * c, 17 + 18 * r
    d.rectangle([x, y, x + 17, y + 17], fill=edge)
    d.rectangle([x + 1, y + 1, x + 16, y + 16], fill=fill)
    if round_:
        for px, py in [(x, y), (x + 17, y), (x, y + 17), (x + 17, y + 17)]:
            d.point([px, py], fill=(0, 0, 0, 0) if False else bg.getpixel((px - (1 if px > x else -1), py)))

frame(4, 0, fill=WHITE, edge=PINKD)          # 펫 얼굴 액자
for dx in (-1, 18):                            # 액자 리본
    x = 7 + 18 * 4 + dx
    d.rectangle([x - (2 if dx < 0 else 0), 22, x + (0 if dx < 0 else 2), 28], fill=PINK2)
for c in range(1, 8):
    frame(c, 1)
frame(0, 2, fill=CREAM, edge=PINKD)            # 레벨
frame(8, 2, fill=CREAM, edge=BROWNL)           # 뒤로
# 꽃 장식
for x, y in [(14, 24), (30, 21), (46, 26), (125, 24), (141, 21), (157, 26)]:
    d.point([x, y - 1], fill=PINKD); d.point([x - 1, y], fill=PINKD); d.point([x + 1, y], fill=PINKD); d.point([x, y + 1], fill=PINKD); d.point([x, y], fill=WHITE)
bg.save(os.path.join(A, 'textures/gui/interact.png'))

# ---------------------------------------------------------------- 16x16 아이콘
def icon(name, draw):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw(ImageDraw.Draw(im))
    im.save(os.path.join(A, f'textures/item/ui/{name}.png'))
    json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": f"octopet:item/ui/{name}"}},
              open(os.path.join(A, f'models/item/ui/{name}.json'), 'w'), indent=2)
    json.dump({"model": {"type": "minecraft:model", "model": f"octopet:item/ui/{name}"}},
              open(os.path.join(A, f'items/ui/{name}.json'), 'w'), indent=2)

def heart(g, col, outline=C('#7a2b3e'), half=False, empty=False):
    pts = ["..XX...XX..", ".XXXX.XXXX.", "XXXXXXXXXXX", "XXXXXXXXXXX", "XXXXXXXXXXX", ".XXXXXXXXX.", "..XXXXXXX..", "...XXXXX...", "....XXX....", ".....X....."]
    ox, oy = 2, 3
    for y, row in enumerate(pts):
        for x, ch in enumerate(row):
            if ch != 'X': continue
            edge = (y == 0 or x == 0 or x == len(row) - 1 or row[x - 1] != 'X' or (x + 1 < len(row) and row[x + 1] != 'X')
                    or y == len(pts) - 1 or pts[y + 1][x] != 'X' or (y > 0 and pts[y - 1][x] != 'X'))
            if edge: c = outline
            elif empty or (half and x > 5): c = C('#e9dfe3')
            else: c = col
            g.point([ox + x, oy + y], fill=c)
    if not empty:
        g.point([ox + 2, oy + 2], fill=WHITE); g.point([ox + 3, oy + 2], fill=WHITE)

icon('heart_full', lambda g: heart(g, C('#ff6f91')))
icon('heart_half', lambda g: heart(g, C('#ff6f91'), half=True))
icon('heart_empty', lambda g: heart(g, C('#ff6f91'), empty=True))

def paw(g):  # 쓰다듬기
    P, D = C('#ff9fb4'), C('#b85a72')
    g.ellipse([4, 7, 11, 13], fill=D); g.ellipse([5, 8, 10, 12], fill=P)
    for x, y in [(2, 5), (5, 2), (9, 2), (12, 5)]:
        g.ellipse([x, y, x + 2, y + 2], fill=D); g.point([x + 1, y + 1], fill=P)
icon('pet', paw)

def ball(g):  # 놀아주기 (비치볼)
    g.ellipse([1, 1, 14, 14], fill=C('#5a4038'))
    g.pieslice([2, 2, 13, 13], 200, 320, fill=C('#ff6f91'))
    g.pieslice([2, 2, 13, 13], 320, 80, fill=WHITE)
    g.pieslice([2, 2, 13, 13], 80, 200, fill=C('#6fc3ff'))
    g.ellipse([6, 6, 9, 9], fill=C('#ffd25a'))
    g.point([4, 5], fill=WHITE)
icon('play', ball)

def cushion(g):  # 기다려
    g.rounded_rectangle([1, 7, 14, 13], 3, fill=C('#6b4e8a')); g.rounded_rectangle([2, 8, 13, 12], 2, fill=C('#b49ae0'))
    g.line([4, 10, 11, 10], fill=C('#d8c8f5'))
    for x in (2, 13): g.point([x, 7], fill=C('#ffd25a')); g.point([x, 13], fill=C('#ffd25a'))
    g.text((5, 0), 'z', fill=C('#6b4e8a'))
icon('stay', cushion)

def feet(g):  # 따라와
    for x, y in [(3, 9), (9, 3)]:
        g.ellipse([x, y + 2, x + 4, y + 6], fill=C('#8a5a3c'))
        for dx in (0, 2, 4): g.point([x + dx, y], fill=C('#8a5a3c'))
icon('follow', feet)

def camera(g):  # 포즈
    g.rounded_rectangle([1, 4, 14, 13], 2, fill=C('#3c3448')); g.rectangle([2, 5, 13, 12], fill=C('#8fd3ff'))
    g.rectangle([5, 2, 9, 4], fill=C('#3c3448')); g.ellipse([5, 6, 10, 11], fill=C('#3c3448')); g.ellipse([6, 7, 9, 10], fill=C('#c9ecff'))
    g.point([12, 6], fill=C('#ffd25a'))
icon('pose', camera)

def star(g):  # 특기
    pts = [(8, 1), (10, 6), (15, 6), (11, 9), (13, 14), (8, 11), (3, 14), (5, 9), (1, 6), (6, 6)]
    g.polygon(pts, fill=C('#ffd25a'), outline=C('#b8862a')); g.point([7, 5], fill=WHITE); g.point([7, 6], fill=WHITE)
icon('trick', star)

def saddle(g):  # 타기
    g.rounded_rectangle([1, 5, 14, 11], 3, fill=C('#7a4a2a')); g.rounded_rectangle([3, 6, 12, 9], 2, fill=C('#b8743e'))
    g.rectangle([7, 11, 8, 14], fill=C('#4a2a14')); g.rectangle([6, 14, 9, 15], fill=C('#c0c0c8'))
    g.rectangle([3, 3, 5, 5], fill=C('#7a4a2a'))
icon('ride', saddle)

def bowl(g):  # 먹이
    g.chord([1, 3, 14, 15], 0, 180, fill=C('#e58aa3')); g.line([1, 9, 14, 9], fill=C('#b85a72'))
    g.ellipse([4, 5, 11, 9], fill=C('#ffb36b')); g.point([6, 6], fill=WHITE)
    g.line([3, 13, 12, 13], fill=C('#b85a72'))
icon('feed', bowl)

def lock(g):
    g.arc([4, 1, 11, 10], 180, 360, fill=C('#8a8a96'), width=2); g.rectangle([3, 7, 12, 14], fill=C('#b8b8c4'), outline=C('#6a6a78'))
    g.rectangle([7, 9, 8, 12], fill=C('#4a4a58'))
icon('lock', lock)

def back(g):
    g.polygon([(2, 8), (8, 2), (8, 5), (14, 5), (14, 11), (8, 11), (8, 14)], fill=C('#b8987d'), outline=C('#5a4038'))
icon('back', back)

def level(g):
    g.ellipse([1, 1, 14, 14], fill=C('#e58aa3')); g.ellipse([2, 2, 13, 13], fill=C('#ffd1dc'))
    heart(g, C('#ff6f91'))
icon('level', level)

# ---------------------------------------------------------------- 감정 말풍선 (폰트, 16x16)
EMO = {}
def emote(ch, name, draw):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    g.rounded_rectangle([0, 0, 15, 12], 4, fill=WHITE, outline=C('#5a4038'))
    g.polygon([(5, 12), (8, 15), (9, 12)], fill=WHITE, outline=C('#5a4038')); g.line([6, 12, 8, 12], fill=WHITE)
    draw(g); im.save(os.path.join(A, f'textures/font/emote_{name}.png')); EMO[ch] = name

emote('', 'love', lambda g: [g.polygon([(5, 4), (6, 3), (8, 5), (10, 3), (11, 4), (11, 6), (8, 9), (5, 6)], fill=C('#ff6f91'))])
emote('', 'happy', lambda g: [g.line([5, 3, 5, 8], fill=C('#6b4e8a')), g.line([5, 3, 10, 2], fill=C('#6b4e8a')), g.line([10, 2, 10, 7], fill=C('#6b4e8a')),
                                     g.ellipse([3, 7, 6, 10], fill=C('#6b4e8a')), g.ellipse([8, 6, 11, 9], fill=C('#6b4e8a'))])
emote('', 'sleepy', lambda g: [g.text((3, 0), 'Zz', fill=C('#4a7ab8'))])
emote('', 'hungry', lambda g: [g.line([4, 3, 7, 6], fill=C('#e04848'), width=2), g.line([7, 3, 4, 6], fill=C('#e04848'), width=2),
                                      g.line([9, 5, 12, 8], fill=C('#e04848'), width=2), g.line([12, 5, 9, 8], fill=C('#e04848'), width=2)])
emote('', 'bored', lambda g: [g.point([x, 7], fill=C('#5a4038')) for x in (4, 7, 10)] + [g.point([x, 6], fill=C('#5a4038')) for x in (4, 7, 10)])
emote('', 'sparkle', lambda g: [g.line([8, 2, 8, 10], fill=C('#ffb300')), g.line([4, 6, 12, 6], fill=C('#ffb300')),
                                       g.point([5, 3], fill=C('#ffd25a')), g.point([11, 9], fill=C('#ffd25a')), g.point([8, 6], fill=WHITE)])

font = {"providers": [
    {"type": "space", "advances": {"": -8, "": -169}},
    {"type": "bitmap", "file": "octopet:gui/interact.png", "ascent": 13, "height": 74, "chars": [""]},
]}
json.dump(font, open(os.path.join(A, 'font/gui.json'), 'w'), indent=2)
emo = {"providers": [{"type": "bitmap", "file": f"octopet:font/emote_{n}.png", "ascent": 8, "height": 10, "chars": [ch]} for ch, n in EMO.items()]}
json.dump(emo, open(os.path.join(A, 'font/emote.json'), 'w'), indent=2)
print('ok', len(EMO), 'emotes')
