"""펫 모델 정의"""
import math, random
from petmodel import Model, Bone, Cube, hexc, shade
from paint import noise_fill, rect, dots, eye, blush


def wave(length, amp, phase=0.0, n=8, axis=(1, 0, 0), offset=(0, 0, 0)):
    """sin 파형 키프레임"""
    pts = []
    for i in range(n + 1):
        t = length * i / n
        s = math.sin(2 * math.pi * (i / n) + phase) * amp
        pts.append((t, [offset[k] + axis[k] * s for k in range(3)]))
    return pts


def bob(length, amp, n=8, phase=0.0):
    return [(length * i / n, [0, (1 - math.cos(2 * math.pi * i / n + phase)) / 2 * amp, 0]) for i in range(n + 1)]


# ======================================================================
# 아기 문어
# ======================================================================
def octopus(name='pet_octopus', body='#ff6f91', light='#ffc2d1', dark='#d94d72', spot='#ee5f86'):
    B, L, D, S = hexc(body), hexc(light), hexc(dark), hexc(spot)

    def head_paint(f, w, h):
        if f == 'down':
            return noise_fill(w, h, shade(B, 0.8), 0.02, 12)
        if f == 'up':
            im = noise_fill(w, h, shade(B, 1.05), 0.025, 11)
            return im
        im = noise_fill(w, h, B, 0.025, len(f), grad=0.12)
        if f == 'north':
            eye(im, 2, 3, 4, 5)
            eye(im, 10, 3, 4, 5)
            blush(im, 0, 9, 3, 2)
            blush(im, 13, 9, 3, 2)
            rect(im, 7, 9, 2, 1, hexc('#8a2a49'))
        else:
            rect(im, 3, 3, 2, 2, S); rect(im, 10, 6, 2, 2, S); rect(im, 6, 1, 2, 2, S)
        return im

    def dome_paint(f, w, h):
        im = noise_fill(w, h, shade(B, 1.04), 0.025, w + h + len(f))
        if f == 'up':
            rect(im, 1, 1, min(4, w - 2), 2, L)
        elif f != 'down' and w >= 8:
            rect(im, w // 3, 1, 2, 2, S)
        return im

    def tent_paint(f, w, h, inner):
        if f in ('down', 'up'):
            return noise_fill(w, h, shade(B, 0.85), 0.02, 5)
        im = noise_fill(w, h, B, 0.025, w * h + len(f), grad=0.15)
        if f in inner:
            for y in range(1, h - 1, 3):
                rect(im, 1, y, 2, 2, L)
        return im

    head = Bone('h_head', [0, 4, 0], cubes=[
        Cube([-4, 4, -4], [4, 10, 4], head_paint, 'head'),
        Cube([-3, 10, -3], [3, 12, 3], dome_paint, 'dome'),
        Cube([-2, 12, -2], [2, 13, 2], dome_paint, 'top'),
    ])
    spots = [(-2.5, -2.5), (2.5, -2.5), (-3.2, 0.8), (3.2, 0.8), (-1.6, 3.0), (1.6, 3.0)]
    tents = []
    for i, (x, z) in enumerate(spots):
        n = math.hypot(x, z)
        ox, oz = round(x / n), round(z / n)
        inner = {'north'} if z < -1 else ({'south'} if z > 2 else ({'east'} if x < 0 else {'west'}))
        p = (lambda inn: (lambda f, w, h: tent_paint(f, w, h, inn)))(inner)
        tip = Bone(f'tip{i}', [x, 1, z], cubes=[Cube([x - 1 + ox, 0, z - 1 + oz], [x + 1 + ox, 1, z + 1 + oz], p, f'tip{i}')])
        tents.append(Bone(f'leg{i}', [x, 4, z], cubes=[Cube([x - 1, 1, z - 1], [x + 1, 4, z + 1], p, f'leg{i}')], bones=[tip]))
    body_b = Bone('body', [0, 0, 0], bones=[head] + tents)
    root = Bone('root', [0, 6, 0], bones=[body_b])
    m = Model(name, root, tex=128)

    def leg_axis(x, z):
        n = math.hypot(x, z) or 1
        return (-z / n, 0, x / n)

    idle = {'body': {'position': bob(2.0, 0.6)}, 'h_head': {'rotation': wave(2.0, 3, axis=(0, 0, 1))}}
    walk = {'body': {'position': bob(0.8, 1.2)}, 'h_head': {'rotation': wave(0.8, 4, axis=(1, 0, 0))}}
    for i, (x, z) in enumerate(spots):
        ax = leg_axis(x, z)
        idle[f'leg{i}'] = {'rotation': wave(2.0, 8, phase=i * 1.1, axis=ax, offset=[a * 6 for a in ax])}
        idle[f'tip{i}'] = {'rotation': wave(2.0, 12, phase=i * 1.1 + 0.6, axis=ax)}
        walk[f'leg{i}'] = {'rotation': wave(0.8, 24, phase=(i % 2) * math.pi, axis=ax, offset=[a * 8 for a in ax])}
        walk[f'tip{i}'] = {'rotation': wave(0.8, 20, phase=(i % 2) * math.pi + 0.8, axis=ax)}
    m.anim('idle', 2.0, idle)
    m.anim('walk', 0.8, walk)
    octo_extra(m, spots)
    return m



def legs4(paint, xs=(-1.25, 1.25), zf=(-0.5, 1.0), zb=(3.5, 5.0), top=3, w=1.5):
    """네 다리 뼈: fl, fr, bl, br (피벗 = 다리 위)"""
    out = []
    for name, x, (z0, z1) in [('fl', xs[0], zf), ('fr', xs[1], zf), ('bl', xs[0], zb), ('br', xs[1], zb)]:
        out.append(Bone(name, [x, top, (z0 + z1) / 2], cubes=[Cube([x - w / 2, 0, z0], [x + w / 2, top, z1], paint, name)]))
    return out


def quad_anims(m, body_bob=0.4, tail_bones=(), head='h_head'):
    idle = {'body': {'position': bob(2.4, 0.3)}, head: {'rotation': wave(2.4, 4, axis=(0, 0, 1))}}
    walk = {'body': {'position': bob(0.6, 0.6, n=8)}, head: {'rotation': wave(0.6, 3, axis=(1, 0, 0))}}
    for i, tb in enumerate(tail_bones):
        idle[tb] = {'rotation': wave(2.4, 14 + i * 6, phase=i * 0.7, axis=(0, 1, 0))}
        walk[tb] = {'rotation': wave(0.6, 10 + i * 4, phase=i * 0.7, axis=(0, 1, 0))}
    for leg, ph in [('fl', 0), ('br', 0), ('fr', math.pi), ('bl', math.pi)]:
        walk[leg] = {'rotation': wave(0.6, 32, phase=ph, axis=(1, 0, 0))}
    m.anim('idle', 2.4, idle)
    m.anim('walk', 0.6, walk)


# ======================================================================
# 아기 여우
# ======================================================================
def fox(name='pet_fox'):
    O, W, K, N = hexc('#ee8a3c'), hexc('#fbf3e8'), hexc('#3b2a24'), hexc('#1b1420')

    def body_p(f, w, h):
        im = noise_fill(w, h, O, 0.025, w + h + len(f), grad=0.1)
        if f == 'down':
            return noise_fill(w, h, W, 0.02, 3)
        if f == 'north':
            rect(im, 2, 2, w - 4, h - 2, W)  # 가슴 흰 털
        return im

    def head_p(f, w, h):
        if f == 'down':
            return noise_fill(w, h, W, 0.02, 4)
        im = noise_fill(w, h, O, 0.025, 7 + len(f), grad=0.08)
        if f == 'north':
            rect(im, 0, 8, 4, 4, W); rect(im, 12, 8, 4, 4, W)   # 볼 흰 털
            rect(im, 2, 9, 2, 3, W); rect(im, 12, 9, 2, 3, W)
            eye(im, 3, 4, 3, 4)
            eye(im, 10, 4, 3, 4)
        elif f in ('east', 'west'):
            rect(im, 0, 8, w, 4, W)
        return im

    def snout_p(f, w, h):
        im = noise_fill(w, h, W, 0.02, 9)
        if f == 'north':
            rect(im, w // 2 - 1, 0, 2, 2, N)
        if f == 'up':
            im = noise_fill(w, h, O, 0.02, 9)
            rect(im, w // 2 - 1, 0, 2, 1, N)
        return im

    def ear_p(f, w, h):
        im = noise_fill(w, h, O, 0.02, 5 + len(f))
        if f in ('north',):
            rect(im, 1, 2, w - 2, h - 2, hexc('#ffd9c2'))
        rect(im, 0, 0, w, 2, K)
        if f == 'up':
            im = noise_fill(w, h, K, 0.02, 1)
        return im

    def leg_p(f, w, h):
        im = noise_fill(w, h, O, 0.02, w * h, grad=0.1)
        rect(im, 0, h - 3, w, 3, K)
        if f == 'down':
            im = noise_fill(w, h, K, 0.02, 2)
        return im

    def tail_p(f, w, h):
        return noise_fill(w, h, O, 0.025, 30 + len(f), grad=0.1)

    def tip_p(f, w, h):
        return noise_fill(w, h, W, 0.02, 31 + len(f))

    head = Bone('h_head', [0, 7, -1], cubes=[
        Cube([-4, 6, -6], [4, 12, 0], head_p, 'head'),
        Cube([-1.5, 6, -8], [1.5, 8.5, -6], snout_p, 'snout'),
        Cube([-3.5, 12, -3.5], [-1, 15, -2], ear_p, 'ear_l'),
        Cube([1, 12, -3.5], [3.5, 15, -2], ear_p, 'ear_r'),
    ])
    tail2 = Bone('tail2', [0, 6, 9], cubes=[Cube([-1.5, 4.5, 9], [1.5, 7.5, 11], tip_p, 'tail_tip')])
    tail = Bone('tail', [0, 6, 5], rotation=[-20, 0, 0], cubes=[Cube([-1.5, 4.5, 5], [1.5, 7.5, 9], tail_p, 'tail')], bones=[tail2])
    body = Bone('body', [0, 3, 2], cubes=[Cube([-2, 3, -1], [2, 7, 5], body_p, 'torso')], bones=[head, tail])
    root = Bone('root', [0, 4, 2], bones=[body] + legs4(leg_p))
    m = Model(name, root, tex=128)
    quad_anims(m, tail_bones=('tail', 'tail2'))
    quad_extra(m, 'roll')
    return m


# ======================================================================
# 아기 고양이 (회색 줄무늬)
# ======================================================================
def cat(name='pet_cat'):
    G, D, W, P = hexc('#a9b1c2'), hexc('#7a8398'), hexc('#f7f4f0'), hexc('#ff9fb4')

    def stripes(im, vertical=False, n=3):
        w, h = im.size
        if vertical:
            for i in range(n):
                x = 2 + i * max(3, (w - 4) // n)
                rect(im, x, 0, 2, min(h, 4), D)
        else:
            for i in range(n):
                y = 1 + i * max(3, (h - 2) // n)
                rect(im, 0, y, min(w, 4), 2, D)

    def body_p(f, w, h):
        if f == 'down':
            return noise_fill(w, h, W, 0.02, 3)
        im = noise_fill(w, h, G, 0.025, w + h + len(f), grad=0.1)
        if f == 'up':
            for y in range(2, h - 1, 4):
                rect(im, 0, y, w, 2, D)
        elif f in ('east', 'west'):
            stripes(im, vertical=True, n=3)
        elif f == 'north':
            rect(im, 2, 2, w - 4, h - 2, W)
        return im

    def head_p(f, w, h):
        if f == 'down':
            return noise_fill(w, h, W, 0.02, 4)
        im = noise_fill(w, h, G, 0.025, 7 + len(f), grad=0.06)
        if f == 'north':
            rect(im, 7, 0, 2, 3, D); rect(im, 4, 0, 2, 2, D); rect(im, 10, 0, 2, 2, D)  # 이마 줄무늬
            rect(im, 4, 8, 8, 4, W)  # 입가 흰 털
            eye(im, 3, 4, 3, 4)
            eye(im, 10, 4, 3, 4)
            rect(im, 7, 8, 2, 1, P)  # 코
            blush(im, 1, 9, 2, 2)
            blush(im, 13, 9, 2, 2)
        elif f == 'up':
            for x in range(3, w - 2, 4):
                rect(im, x, 0, 2, h // 2, D)
        else:
            rect(im, 0, 3, 3, 2, D); rect(im, 0, 7, 3, 2, D)
        return im

    def ear_p(f, w, h):
        im = noise_fill(w, h, G, 0.02, 5 + len(f))
        if f == 'north':
            rect(im, 1, 1, max(1, w - 2), h - 1, P)
        return im

    def leg_p(f, w, h):
        im = noise_fill(w, h, G, 0.02, w * h, grad=0.08)
        rect(im, 0, h - 2, w, 2, W)
        if f == 'down':
            im = noise_fill(w, h, P, 0.02, 2)
        return im

    def tail_p(f, w, h):
        im = noise_fill(w, h, G, 0.025, 40 + len(f))
        for y in range(1, h, 4):
            rect(im, 0, y, w, 2, D)
        return im

    head = Bone('h_head', [0, 7, -1], cubes=[
        Cube([-4, 6, -6], [4, 12, 0], head_p, 'head'),
        Cube([-3.5, 12, -3.5], [-1.5, 14, -2], ear_p, 'ear_l'),
        Cube([1.5, 12, -3.5], [3.5, 14, -2], ear_p, 'ear_r'),
        Cube([-3, 14, -3.25], [-2, 15, -2.25], ear_p, 'ear_l2'),
        Cube([2, 14, -3.25], [3, 15, -2.25], ear_p, 'ear_r2'),
    ])
    tail2 = Bone('tail2', [0, 7.25, 8], cubes=[Cube([-0.75, 6.5, 7.25], [0.75, 12, 8.75], tail_p, 'tail_up')])
    tail = Bone('tail', [0, 6, 5], cubes=[Cube([-0.75, 5.5, 5], [0.75, 7, 8.75], tail_p, 'tail')], bones=[tail2])
    body = Bone('body', [0, 3, 2], cubes=[Cube([-2, 3, -1], [2, 7, 5], body_p, 'torso')], bones=[head, tail])
    root = Bone('root', [0, 4, 2], bones=[body] + legs4(leg_p))
    m = Model(name, root, tex=128)
    quad_anims(m, tail_bones=('tail', 'tail2'))
    quad_extra(m, 'loaf')
    return m


# ======================================================================
# 교감 동작 (OctoPet 이 재생: pet · hop · play · sit · pose · trick)
# ======================================================================
def keys(*pts):
    """keys((t, [x,y,z]), ...)"""
    return [(t, list(v)) for t, v in pts]


def spin(length, axis=1, n=12, turns=1.0, start=0.0, end=None):
    end = length if end is None else end
    out = []
    for i in range(n + 1):
        t = start + (end - start) * i / n
        v = [0, 0, 0]
        v[axis] = 360 * turns * i / n
        out.append((t, v))
    if start > 0:
        out.insert(0, (0, [0, 0, 0]))
    if end < length:
        out.append((length, [0, 0, 0] if turns % 1 else [0, 0, 0]))
    return out


def common_anims(m, head, extra_wag=()):
    # 쓰다듬기: 고개 갸웃갸웃 + 몸 살짝 눌림
    pet = {head: {'rotation': keys((0, [0, 0, 0]), (0.2, [0, 0, 12]), (0.4, [0, 0, -12]), (0.6, [0, 0, 10]), (0.8, [0, 0, 0]))},
           'body': {'position': keys((0, [0, 0, 0]), (0.2, [0, -0.6, 0]), (0.5, [0, 0.3, 0]), (0.8, [0, 0, 0]))}}
    for tb in extra_wag:
        pet[tb] = {'rotation': wave(0.8, 25, axis=(0, 1, 0), n=8)}
    m.anim('pet', 0.8, pet, loop='once')
    # 폴짝
    m.anim('hop', 0.4, {'root': {'position': keys((0, [0, 0, 0]), (0.2, [0, 2.2, 0]), (0.4, [0, 0, 0]))}}, loop='once')
    # 놀기: 높이 뛰며 한 바퀴
    m.anim('play', 1.2, {'root': {'position': keys((0, [0, 0, 0]), (0.15, [0, -0.8, 0]), (0.6, [0, 4, 0]), (1.05, [0, 0, 0]), (1.2, [0, 0, 0])),
                                  'rotation': spin(1.2, axis=1, n=12, start=0.15, end=1.05)}}, loop='once')


def octo_extra(m, spots):
    common_anims(m, 'h_head')
    sit = {'body': {'position': keys((0, [0, -1.5, 0]), (1, [0, -1.5, 0]))}}
    pose = {'h_head': {'rotation': keys((0, [0, 0, 10]), (1, [0, 0, 10]))}}
    trick = {'h_head': {'rotation': keys((0, [0, 0, 0]), (0.4, [-15, 0, 0]), (0.7, [12, 0, 0]), (1.6, [0, 0, 0]))},
             'body': {'position': keys((0, [0, 0, 0]), (0.4, [0, -1.2, 0]), (0.7, [0, 1.5, 0]), (1.6, [0, 0, 0]))}}
    for i, (x, z) in enumerate(spots):
        n = math.hypot(x, z) or 1
        ax = (-z / n, 0, x / n)
        sit[f'leg{i}'] = {'rotation': keys((0, [a * 35 for a in ax]), (1, [a * 35 for a in ax]))}
        flare = [a * 45 for a in ax]
        trick[f'leg{i}'] = {'rotation': keys((0, [0, 0, 0]), (0.4, [a * -10 for a in ax]), (0.7, flare), (1.6, [0, 0, 0]))}
    # 포즈: 앞 오른다리(1번) 번쩍
    pose['leg1'] = {'rotation': keys((0, [-70, 0, -20]), (1, [-70, 0, -20]))}
    pose['tip1'] = {'rotation': keys((0, [-30, 0, 0]), (1, [-30, 0, 0]))}
    m.anim('sit', 1.0, sit, loop='loop')
    m.anim('pose', 1.0, pose, loop='loop')
    m.anim('trick', 1.6, trick, loop='once')


def quad_extra(m, trick):
    common_anims(m, 'h_head', extra_wag=('tail',))
    # 앉기: 엉덩이 내리고 몸 세우기 + 뒷다리 접기
    sit = {'body': {'rotation': keys((0, [28, 0, 0]), (1, [28, 0, 0])), 'position': keys((0, [0, -0.8, 0]), (1, [0, -0.8, 0]))},
           'h_head': {'rotation': keys((0, [-24, 0, 0]), (1, [-24, 0, 0]))},
           'bl': {'rotation': keys((0, [-80, 0, 0]), (1, [-80, 0, 0])), 'position': keys((0, [0, -0.6, -1]), (1, [0, -0.6, -1]))},
           'br': {'rotation': keys((0, [-80, 0, 0]), (1, [-80, 0, 0])), 'position': keys((0, [0, -0.6, -1]), (1, [0, -0.6, -1]))}}
    m.anim('sit', 1.0, sit, loop='loop')
    # 포즈: 고개 갸웃 + 앞발 들기
    pose = {'h_head': {'rotation': keys((0, [0, 0, 14]), (1, [0, 0, 14]))},
            'fr': {'rotation': keys((0, [-75, 0, 0]), (1, [-75, 0, 0])), 'position': keys((0, [0, 1, -0.5]), (1, [0, 1, -0.5]))},
            'tail': {'rotation': keys((0, [20, 0, 0]), (1, [20, 0, 0]))}}
    m.anim('pose', 1.0, pose, loop='loop')
    if trick == 'roll':      # 여우: 데굴 구르기
        m.anim('trick', 1.6, {
            'root': {'position': keys((0, [0, 0, 0]), (0.3, [0, 1, 0]), (0.55, [0, 4, 0]), (0.8, [0, 7, 0]), (1.05, [0, 4, 0]), (1.3, [0, 1, 0]), (1.6, [0, 0, 0])),
                     'rotation': spin(1.6, axis=2, n=12, start=0.3, end=1.3)},
            'tail': {'rotation': wave(1.6, 30, axis=(0, 1, 0), n=8)}}, loop='once')
    else:                    # 고양이: 식빵 굽기
        loaf = {'body': {'position': keys((0, [0, 0, 0]), (0.4, [0, -2.6, 0]), (2.6, [0, -2.6, 0]), (3.0, [0, 0, 0]))},
                'h_head': {'rotation': keys((0, [0, 0, 0]), (0.6, [0, 0, 8]), (1.6, [0, 0, -8]), (2.6, [0, 0, 0]))},
                'tail': {'rotation': keys((0, [0, 0, 0]), (0.4, [0, 70, 0]), (2.6, [0, 70, 0]), (3.0, [0, 0, 0]))}}
        for leg in ('fl', 'fr', 'bl', 'br'):
            loaf[leg] = {'position': keys((0, [0, 0, 0]), (0.4, [0, 2.4, 0]), (2.6, [0, 2.4, 0]), (3.0, [0, 0, 0]))}
        m.anim('trick', 3.0, loaf, loop='once')


PETS = {
    'octopus': octopus,
    'fox': fox,
    'cat': cat,
}
