"""한정 S 스킨 홍보 이미지 (1920x1080) 생성기.
사용: python3 tools/promo/make_promo.py tools/promo/<스킨id>.json [출력.png]
설정 json 예: tools/promo/pumpkin_ghost_hoe.json
- skin: 스킨 id (pack 텍스처 사용, 16x16 아이콘을 픽셀 그대로 크게)
- name / name_color / tagline / chips / period / event_badge / tool_label
- tool_icon: 도구 종류 배지 아이콘 PNG 경로 (바닐라 아이템 텍스처, 예: 미러 에셋의 diamond_hoe.png)
- theme: sky_top, sky_bottom, glow, accent, badge, chip_bg, chip_line  /  decor: "halloween" 이면 호박·박쥐
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-"
W, H = 1920, 1080


def main(cfg_path, out=None):
    c = json.load(open(cfg_path, encoding="utf-8"))
    th = {"sky_top": [28, 16, 52], "sky_bottom": [92, 44, 96], "glow": [255, 140, 40], "accent": [255, 170, 60],
          "badge": [255, 120, 40], "chip_bg": [60, 34, 86], "chip_line": [200, 150, 255], "sub": [240, 226, 255]}
    th.update(c.get("theme", {}))
    T = lambda k: tuple(th[k])
    font = lambda w, s: ImageFont.truetype(FONT + w + ".ttc", s)
    rnd = random.Random(7)
    sk = Image.open(f"{ROOT}/pack/assets/cosmetics/textures/item/{c['skin']}.png").convert("RGBA")

    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    top, bot = T("sky_top"), T("sky_bottom")
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)) + (255,))
    for _ in range(220):
        x, y = rnd.randint(0, W), rnd.randint(0, int(H * 0.7)); s = rnd.choice([2, 2, 3, 4])
        d.rectangle([x, y, x + s, y + s], fill=(255, 244, 220, rnd.randint(120, 255)))
    # 달
    mx, my = 1650, 190
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    for r, a in ((330, 30), (250, 45), (190, 70)):
        g.ellipse([mx - r, my - r, mx + r, my + r], fill=(255, 210, 150, a))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(im)
    d.ellipse([mx - 140, my - 140, mx + 140, my + 140], fill=(255, 236, 190, 255))
    for x, y, r in ((mx - 40, my - 30, 26), (mx + 50, my + 40, 18), (mx - 10, my + 70, 12)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 214, 166, 255))
    # 아이템 뒤 빛
    cx, cy = 560, 560
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    for r, a in ((420, 40), (320, 60), (230, 80)):
        g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=T("glow") + (a,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    # 언덕
    hill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pts = [(0, H)] + [(x, 900 + int(40 * math.sin(x / 260) + 25 * math.sin(x / 97))) for x in range(0, W + 20, 20)] + [(W, H)]
    ImageDraw.Draw(hill).polygon(pts, fill=(26, 16, 36, 255)); im.alpha_composite(hill)
    d = ImageDraw.Draw(im)
    if c.get("decor") == "halloween":
        def pumpkin(x, y, s):
            rows = ["...gg...", "..oooo..", ".oooooo.", "oo.oo.oo", "oooooooo", "oo....oo", ".oooooo.", "..oooo.."]
            for j, r in enumerate(rows):
                for i, ch in enumerate(r):
                    col = {"o": (240, 130, 40), "g": (90, 150, 60)}.get(ch)
                    if ch == "." and 2 <= j <= 6 and 0 < i < 7:
                        col = (255, 220, 90)
                    if col:
                        d.rectangle([x + i * s, y + j * s, x + i * s + s - 1, y + j * s + s - 1], fill=col)
        for x, y, s in ((1180, 868, 14), (1330, 900, 10), (1720, 880, 12), (140, 905, 9), (980, 910, 8)):
            pumpkin(x, y, s)
        BODY, WING, WING2, EYE = (52, 36, 66), (92, 60, 118), (122, 86, 150), (255, 170, 60)
        WINGS = [["w.....w", "ww...ww", ".......", "......."], [".......", "ww...ww", ".w...w.", "......."],
                 [".......", ".......", "ww...ww", "w.....w"]]
        def bat(x, y, s, ph):
            px = lambda i, j, col: d.rectangle([x + i * s, y + j * s, x + i * s + s - 1, y + j * s + s - 1], fill=col)
            for j, row in enumerate(WINGS[ph]):
                for i, ch in enumerate(row):
                    if ch == "w":
                        px(i, j, WING2 if j == 0 else WING)
            for (i, j) in ((2, 1), (3, 1), (4, 1), (2, 2), (3, 2), (4, 2), (3, 3), (2, 0), (4, 0)):
                px(i, j, BODY)
            px(2, 1, EYE); px(4, 1, EYE)
        for x, y, s, ph in ((1080, 120, 16, 0), (1290, 215, 11, 1), (880, 60, 10, 2), (260, 110, 13, 1), (70, 400, 10, 0), (1760, 720, 12, 2)):
            bat(x, y, s, ph)
    # 아이템
    big = sk.resize((720, 720), Image.NEAREST)
    sh = Image.new("RGBA", big.size, (0, 0, 0, 0)); sh.putalpha(big.split()[3].point(lambda a: 120 if a else 0))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (cx - 360 + 18, cy - 360 + 24))
    im.alpha_composite(big, (cx - 360, cy - 360))
    # 글자
    d = ImageDraw.Draw(im)
    def text(xy, s, f, fill, anchor="la", stroke=0, sc=(20, 10, 30)):
        d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sc)
    tx = 1020
    bw = int(d.textlength(c["event_badge"], font=font("Bold", 30))) + 60
    d.rounded_rectangle([tx, 330, tx + bw, 392], 30, fill=T("badge"))
    text((tx + bw // 2, 361), c["event_badge"], font("Bold", 30), (255, 255, 255), "mm")
    x = tx + bw + 16
    d.rounded_rectangle([x, 330, x + 84, 392], 30, fill=(150, 90, 220))
    text((x + 42, 361), c.get("rarity", "S"), font("Black", 38), (255, 240, 140), "mm")
    x += 100
    tw = int(d.textlength(c["tool_label"], font=font("Bold", 30))) + 100
    d.rounded_rectangle([x, 330, x + tw, 392], 30, fill=(40, 26, 60), outline=(170, 220, 140), width=3)
    if c.get("tool_icon") and os.path.exists(c["tool_icon"]):
        im.alpha_composite(Image.open(c["tool_icon"]).convert("RGBA").resize((40, 40), Image.NEAREST), (x + 20, 341))
    text((x + 70, 361), c["tool_label"], font("Bold", 30), (210, 240, 190), "lm")
    text((tx, 420), c["name"], font("Black", 118), tuple(c.get("name_color", th["accent"])), "la", stroke=8)
    text((tx + 4, 580), c["tagline"], font("Medium", 34), T("sub"), "la", stroke=3)
    x = tx
    for ch in c.get("chips", []):
        w = int(d.textlength(ch, font=font("Bold", 28))) + 48
        d.rounded_rectangle([x, 650, x + w, 702], 26, fill=T("chip_bg"), outline=T("chip_line"), width=3)
        text((x + w // 2, 676), ch, font("Bold", 28), (235, 220, 255), "mm"); x += w + 16
    d.rounded_rectangle([tx, 760, tx + 640, 850], 20, fill=(20, 12, 32, 220), outline=T("accent"), width=4)
    text((tx + 30, 805), "픽업 기간", font("Bold", 34), (255, 200, 120), "lm")
    text((tx + 215, 805), c["period"], font("Black", 54), (255, 255, 255), "lm")
    out = out or f"promo_{c['skin']}.png"
    im.convert("RGB").save(out)
    print("saved", out, im.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
