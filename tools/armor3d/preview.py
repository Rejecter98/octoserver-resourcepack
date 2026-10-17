"""A급 방어구 입체화 미리보기 (지금 vs 바뀜, 3인칭 앞·뒤). 사용: python3 tools/armor3d/preview.py <출력.png>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from player_render import render
from PIL import Image, ImageDraw, ImageFont
R = os.path.join(HERE, "..", "..")
E = R + '/pack/assets/cosmetics/textures/entity/equipment/'; O = HERE + '/orig/'
M = R + '/pack/assets/cosmetics/models/item/'; T = R + '/pack/assets/cosmetics/textures/item'
F = '/usr/share/fonts/opentype/noto/NotoSansCJK-'
H1 = ImageFont.truetype(F + 'Bold.ttc', 34); H2 = ImageFont.truetype(F + 'Bold.ttc', 24); TX = ImageFont.truetype(F + 'Regular.ttc', 18)
sz = (300, 470)
rows = [
    ('곰돌이 잠옷 세트 (모자 A 입체 · 잠옷·바지·슬리퍼 A 고해상도)',
     dict(humanoid=O + 'humanoid/bear_pajama.png', humanoid_leggings=O + 'humanoid_leggings/bear_pajama.png', parts={'helmet', 'chest', 'legs', 'boots'}), None,
     dict(humanoid=E + 'humanoid/bear_pajama.png', humanoid_leggings=E + 'humanoid_leggings/bear_pajama.png', parts={'chest', 'legs', 'boots'}), M + 'bear_helmet_head.json'),
    ('냥이 모자 (A 입체: 니트 비니 + 고양이 귀 + 방울)',
     dict(humanoid=E + 'humanoid/cat_ear.png', parts={'helmet'}), None, dict(parts=set()), M + 'cat_ear_helmet_head.json'),
    ('오리 장화 (A 고해상도: 오리 얼굴·부리·물갈퀴 밑창)',
     dict(humanoid=O + 'humanoid/duck.png', parts={'boots'}), None, dict(humanoid=E + 'humanoid/duck.png', parts={'boots'}), None),
]
W = 60 + sz[0] * 4 + 60; H = 110 + len(rows) * (sz[1] + 80) + 30
im = Image.new('RGB', (W, H), (250, 244, 250)); d = ImageDraw.Draw(im)
d.text((30, 20), 'A급 방어구 입체화 미리보기 (3인칭 앞·뒤)', font=H1, fill=(120, 60, 110))
d.text((30, 66), '왼쪽 = 지금 · 오른쪽 = 바뀐 모습   |   입체 투구는 플러그인 1.5.0-octo 적용 후 보임', font=TX, fill=(140, 110, 140))
y = 110
for title, a0, h0, a1, h1 in rows:
    d.text((30, y), title, font=H2, fill=(120, 60, 110)); y += 40
    imgs = [render(a0, h0, T, yaw=25, size=sz), render(a0, h0, T, yaw=205, size=sz),
            render(a1, h1, T, yaw=25, size=sz), render(a1, h1, T, yaw=205, size=sz)]
    for i, g in enumerate(imgs):
        x = 30 + i * sz[0] + (60 if i >= 2 else 0); im.paste(g.convert('RGB'), (x, y))
        d.text((x + 10, y + 8), ['지금 · 앞', '지금 · 뒤', '바뀜 · 앞', '바뀜 · 뒤'][i], font=TX, fill=(230, 220, 240))
    d.text((30 + sz[0] * 2 + 12, y + sz[1] // 2 - 20), '→', font=H1, fill=(120, 60, 110))
    y += sz[1] + 40
im.save(sys.argv[1]); print(im.size)
