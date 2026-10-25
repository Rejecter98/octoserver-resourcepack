"""블록형 펫 모델 생성기: 파이썬으로 뼈대·큐브·텍스처를 정의 → .bbmodel (BetterModel) + CSS 3D 미리보기 HTML.

좌표: Blockbench 단위 (16 = 1블록), 발밑 중앙이 원점, 앞(얼굴)은 north(-Z).
텍스처: 1단위 = PX 픽셀. 면 그림은 바깥에서 본 모습 (옆면은 위쪽 = +Y).
  north: 왼쪽 = +X / south: 왼쪽 = -X / east: 왼쪽 = +Z / west: 왼쪽 = -Z / up: 위쪽 = -Z, 왼쪽 = -X / down: 위쪽 = +Z, 왼쪽 = -X
"""
import base64, io, json, math, uuid
from PIL import Image, ImageDraw

PX = 2  # 단위당 픽셀


def uid():
    return str(uuid.uuid4())


def hexc(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (c[3] if len(c) > 3 else 255,)


class Cube:
    def __init__(self, frm, to, paint, name='cube', inflate=0.0):
        self.frm, self.to, self.paint, self.name, self.inflate = list(frm), list(to), paint, name, inflate
        self.uuid = uid()

    def dims(self):
        return [self.to[i] - self.frm[i] for i in range(3)]

    def face_size(self, f):
        w, h, d = self.dims()
        return {'north': (w, h), 'south': (w, h), 'east': (d, h), 'west': (d, h), 'up': (w, d), 'down': (w, d)}[f]


class Bone:
    def __init__(self, name, origin, rotation=(0, 0, 0), cubes=(), bones=()):
        self.name, self.origin, self.rotation = name, list(origin), list(rotation)
        self.cubes, self.bones = list(cubes), list(bones)
        self.uuid = uid()

    def walk(self):
        yield self
        for b in self.bones:
            yield from b.walk()


FACES = ['north', 'south', 'east', 'west', 'up', 'down']


class Model:
    def __init__(self, name, root, tex=128):
        self.name, self.root, self.tex = name, root, tex
        self.anims = []  # (name, length, loop, {bone_name: {'rotation': [(t,[x,y,z])], 'position': [...]}})

    def anim(self, name, length, tracks, loop=True):
        self.anims.append((name, length, loop, tracks))

    # ---------- 텍스처 굽기 ----------
    def bake(self):
        img = Image.new('RGBA', (self.tex, self.tex), (0, 0, 0, 0))
        x = y = row_h = 0
        self.uv = {}
        items = []
        for b in self.root.walk():
            for c in b.cubes:
                for f in FACES:
                    fw, fh = c.face_size(f)
                    if fw <= 0 or fh <= 0:
                        continue
                    items.append((c, f, int(round(fw * PX)), int(round(fh * PX))))
        items.sort(key=lambda t: -t[3])
        for c, f, pw, ph in items:
            if x + pw > self.tex:
                x, y, row_h = 0, y + row_h, 0
            if y + ph > self.tex:
                raise RuntimeError('텍스처 공간 부족: tex 를 키우세요')
            face_img = c.paint(f, pw, ph)
            img.paste(face_img, (x, y))
            self.uv[(c.uuid, f)] = [x, y, x + pw, y + ph]   # 텍스처 픽셀 좌표 (resolution = 텍스처 크기)
            x += pw
            row_h = max(row_h, ph)
        self.image = img
        return img

    # ---------- .bbmodel ----------
    def bbmodel(self):
        if not hasattr(self, 'image'):
            self.bake()
        res = self.tex
        elements = []

        def outl(b):
            for c in b.cubes:
                faces = {f: {'uv': self.uv[(c.uuid, f)], 'texture': 0} for f in FACES if (c.uuid, f) in self.uv}
                elements.append({'name': c.name, 'box_uv': False, 'rescale': False, 'locked': False,
                                 'render_order': 'default', 'allow_mirror_modeling': True,
                                 'from': c.frm, 'to': c.to, 'autouv': 0, 'color': 0, 'inflate': c.inflate,
                                 'origin': b.origin, 'faces': faces, 'type': 'cube', 'uuid': c.uuid})
            return {'name': b.name, 'origin': b.origin, 'rotation': b.rotation, 'color': 0, 'uuid': b.uuid,
                    'export': True, 'mirror_uv': False, 'isOpen': True, 'locked': False, 'visibility': True,
                    'autouv': 0, 'children': [c.uuid for c in b.cubes] + [outl(x) for x in b.bones]}

        outliner = [outl(self.root)]
        buf = io.BytesIO()
        self.image.save(buf, 'PNG')
        src = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
        bones = {b.name: b for b in self.root.walk()}
        anims = []
        for name, length, loop, tracks in self.anims:
            animators = {}
            for bn, ch in tracks.items():
                b = bones[bn]
                kfs = []
                for channel, pts in ch.items():
                    for t, v in pts:
                        # Blockbench 규칙: 애니메이션 회전 x·y 부호 반전, 위치 x 반전 → 의도한 방향이 되도록 미리 뒤집어 저장
                        v = [-v[0], -v[1], v[2]] if channel == 'rotation' else [-v[0], v[1], v[2]]
                        kfs.append({'channel': channel, 'data_points': [{'x': str(round(v[0], 3)), 'y': str(round(v[1], 3)), 'z': str(round(v[2], 3))}],
                                    'uuid': uid(), 'time': round(t, 4), 'color': -1, 'interpolation': 'catmullrom'})
                animators[b.uuid] = {'name': bn, 'type': 'bone', 'keyframes': kfs}
            anims.append({'uuid': uid(), 'name': name, 'loop': 'loop' if loop else 'once', 'override': False,
                          'length': length, 'snapping': 20, 'selected': False, 'anim_time_update': '',
                          'blend_weight': '', 'start_delay': '', 'loop_delay': '', 'animators': animators})
        return {
            'meta': {'format_version': '4.10', 'model_format': 'free', 'box_uv': False},
            'name': self.name, 'model_identifier': '', 'visible_box': [1, 1, 0],
            'variable_placeholders': '', 'variable_placeholder_buttons': [], 'timeline_setups': [],
            'unhandled_root_fields': {},
            'resolution': {'width': res, 'height': res},
            'elements': elements, 'outliner': outliner,
            'textures': [{'path': '', 'name': self.name + '.png', 'folder': '', 'namespace': '', 'id': '0',
                          'width': self.tex, 'height': self.tex, 'uv_width': res, 'uv_height': res,
                          'particle': False, 'use_as_default': False, 'layers_enabled': False,
                          'sync_to_project': '', 'render_mode': 'default', 'render_sides': 'auto',
                          'frame_time': 1, 'frame_order_type': 'loop', 'frame_order': '', 'frame_interpolate': False,
                          'visible': True, 'internal': True, 'saved': False, 'uuid': uid(),
                          'relative_path': '', 'source': src}],
            'animations': anims,
        }

    # ---------- 포즈 계산 (미리보기용) ----------
    def sample(self, anim_name, t):
        """해당 시간의 뼈별 (rotation, position) — catmull-rom 대신 cosine 보간 근사"""
        out = {}
        for name, length, loop, tracks in self.anims:
            if name != anim_name:
                continue
            tt = t % length
            for bn, ch in tracks.items():
                r = [0, 0, 0]; p = [0, 0, 0]
                for channel, pts in ch.items():
                    pts = sorted(pts, key=lambda q: q[0])
                    v = pts[-1][1]
                    for i in range(len(pts) - 1):
                        t0, v0 = pts[i]; t1, v1 = pts[i + 1]
                        if t0 <= tt <= t1:
                            k = 0 if t1 == t0 else (tt - t0) / (t1 - t0)
                            k = (1 - math.cos(k * math.pi)) / 2
                            v = [v0[j] + (v1[j] - v0[j]) * k for j in range(3)]
                            break
                    if channel == 'rotation':
                        r = v
                    else:
                        p = v
                out[bn] = (r, p)
        return out

    # ---------- CSS 3D 미리보기 ----------
    def preview_html(self, views, pose=None, scale=14, size=(560, 560), transparent=False):
        """views: [(yaw, pitch)] 도 단위. pose: {bone: (rot, pos)}"""
        if not hasattr(self, 'image'):
            self.bake()
        pose = pose or {}
        faces_html = []

        def mat_mul(a, b):
            return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

        def tr(x, y, z):
            return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]

        def rot(rx, ry, rz):
            rx, ry, rz = [math.radians(v) for v in (rx, ry, rz)]
            X = [[1, 0, 0, 0], [0, math.cos(rx), -math.sin(rx), 0], [0, math.sin(rx), math.cos(rx), 0], [0, 0, 0, 1]]
            Y = [[math.cos(ry), 0, math.sin(ry), 0], [0, 1, 0, 0], [-math.sin(ry), 0, math.cos(ry), 0], [0, 0, 0, 1]]
            Z = [[math.cos(rz), -math.sin(rz), 0, 0], [math.sin(rz), math.cos(rz), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
            return mat_mul(Z, mat_mul(Y, X))

        def apply(m, v):
            return [m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2] + m[i][3] for i in range(3)]

        crops = {}

        def face_png(c, f):
            u = self.uv[(c.uuid, f)]
            im = self.image.crop((int(u[0]), int(u[1]), int(u[2]), int(u[3])))
            buf = io.BytesIO(); im.save(buf, 'PNG')
            return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

        def visit(b, parent):
            r, p = pose.get(b.name, ([0, 0, 0], [0, 0, 0]))
            o = b.origin
            rr = [b.rotation[i] + r[i] for i in range(3)]
            m = mat_mul(parent, mat_mul(tr(o[0] + p[0], o[1] + p[1], o[2] + p[2]), mat_mul(rot(*rr), tr(-o[0], -o[1], -o[2]))))
            for c in b.cubes:
                i = c.inflate
                x0, y0, z0 = [c.frm[k] - i for k in range(3)]
                x1, y1, z1 = [c.to[k] + i for k in range(3)]
                # (TL, TR, BL) 바깥에서 본 모습
                corners = {
                    'north': ([x1, y1, z0], [x0, y1, z0], [x1, y0, z0]),
                    'south': ([x0, y1, z1], [x1, y1, z1], [x0, y0, z1]),
                    'east': ([x1, y1, z1], [x1, y1, z0], [x1, y0, z1]),
                    'west': ([x0, y1, z0], [x0, y1, z1], [x0, y0, z0]),
                    'up': ([x0, y1, z0], [x1, y1, z0], [x0, y1, z1]),
                    'down': ([x0, y0, z1], [x1, y0, z1], [x0, y0, z0]),
                }
                for f, (TL, TR, BL) in corners.items():
                    if (c.uuid, f) not in self.uv:
                        continue
                    TL, TR, BL = [apply(m, q) for q in (TL, TR, BL)]
                    # 월드(오른손) → CSS(왼손): (x, -y, z)
                    cv = lambda q: [q[0] * scale, -q[1] * scale, q[2] * scale]
                    TL, TR, BL = cv(TL), cv(TR), cv(BL)
                    ax = [(TR[k] - TL[k]) / 100 for k in range(3)]
                    ay = [(BL[k] - TL[k]) / 100 for k in range(3)]
                    az = [ax[1] * ay[2] - ax[2] * ay[1], ax[2] * ay[0] - ax[0] * ay[2], ax[0] * ay[1] - ax[1] * ay[0]]
                    n = math.sqrt(sum(v * v for v in az)) or 1
                    az = [v / n for v in az]
                    mm = ax + [0] + ay + [0] + az + [0] + TL + [1]
                    shade_f = {'up': 1.0, 'down': 0.5, 'north': 0.82, 'south': 0.82, 'east': 0.65, 'west': 0.65}[f]
                    faces_html.append(f'<div class="f" style="filter:brightness({shade_f});background-image:url({face_png(c, f)});transform:matrix3d({",".join(f"{v:.5f}" for v in mm)})"></div>')
            for x in b.bones:
                visit(x, m)

        visit(self.root, [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        scene = ''.join(faces_html)
        W, H = size
        cells = ''.join(f'<div class="cell" style="width:{W}px;height:{H}px"><div class="cam" style="transform:translate({W/2}px,{H*0.72}px) rotateX({-pitch}deg) rotateY({yaw + 180}deg)">{scene}</div>'
                        + ('' if transparent else '<div class="sh"></div>') + '</div>' for yaw, pitch in views)
        return f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:{'transparent' if transparent else '#1d1a24'};display:flex;gap:0}}
.cell{{position:relative;perspective:1400px;overflow:hidden;background:{'transparent' if transparent else 'radial-gradient(circle at 50% 70%,#3b3450,#1d1a24 70%)'}}}
.cam{{position:absolute;left:0;top:0;transform-style:preserve-3d}}
.f{{position:absolute;left:0;top:0;width:100px;height:100px;transform-origin:0 0;background-size:100% 100%;image-rendering:pixelated;backface-visibility:hidden}}
.sh{{position:absolute;left:50%;top:73%;width:150px;height:30px;margin-left:-75px;border-radius:50%;background:rgba(0,0,0,.35);filter:blur(6px);z-index:-1}}
</style></head><body>{cells}</body></html>'''
