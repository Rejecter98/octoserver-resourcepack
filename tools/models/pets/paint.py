"""면 그리기 도우미 — 블록형 펫 텍스처 (PX=2 기준)"""
import random
from PIL import Image, ImageDraw
from petmodel import hexc, shade


def noise_fill(w, h, base, amt=0.06, seed=0, grad=0.0):
    """base 색 + 약한 픽셀 노이즈, grad>0 이면 아래로 갈수록 어두움"""
    rnd = random.Random(seed)
    im = Image.new('RGBA', (w, h))
    px = im.load()
    for y in range(h):
        g = 1 - grad * (y / max(1, h - 1))
        for x in range(w):
            f = g * (1 + rnd.uniform(-amt, amt))
            px[x, y] = shade(base, f)
    return im


def rect(im, x, y, w, h, c):
    ImageDraw.Draw(im).rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def dots(im, c, n, seed=1, margin=1, size=2):
    rnd = random.Random(seed)
    w, h = im.size
    for _ in range(n):
        x = rnd.randrange(margin, max(margin + 1, w - margin - size + 1))
        y = rnd.randrange(margin, max(margin + 1, h - margin - size + 1))
        rect(im, x, y, size, size, c)


def eye(im, x, y, w=4, h=6, white=True):
    """큰 반짝 눈: 검은 바탕 + 왼쪽 위 흰 하이라이트 + 아래 작은 하이라이트"""
    rect(im, x, y, w, h, hexc('#1b1420'))
    if white:
        rect(im, x, y, 2, 2, hexc('#ffffff'))
        rect(im, x + w - 2, y + h - 2, 1, 1, hexc('#bfb6d6'))


def blush(im, x, y, w=4, h=2, c='#ff9fb8'):
    rect(im, x, y, w, h, hexc(c, 200))


def outline_bottom(im, c, t=1):
    w, h = im.size
    rect(im, 0, h - t, w, t, c)
