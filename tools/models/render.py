""".bbmodel 소프트웨어 렌더러 (Blockbench 규칙: 그룹 Euler ZYX, 애니메이션 회전 x·y 부호 반전, 위치 x 반전)."""
import base64, io, json, math
import numpy as np
from PIL import Image


def rot(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    X = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Y = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Z = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Z @ Y @ X


def M4(R=np.eye(3), t=(0, 0, 0)):
    m = np.eye(4); m[:3, :3] = R; m[:3, 3] = t; return m


class Model:
    def __init__(self, path):
        d = json.load(open(path))
        self.d = d
        src = d["textures"][0]["source"].split(",", 1)[1]
        self.tex = np.array(Image.open(io.BytesIO(base64.b64decode(src))).convert("RGBA"))
        self.el = {e["uuid"]: e for e in d["elements"]}
        self.groups = []  # (name, origin, parent, [element uuids])

        def walk(g, parent):
            self.groups.append((g["name"], g["origin"], parent, [c for c in g["children"] if isinstance(c, str)]))
            for c in g["children"]:
                if isinstance(c, dict):
                    walk(c, g["name"])
        for g in d["outliner"]:
            walk(g, None)
        self.anims = {a["name"]: a for a in d["animations"]}

    def sample(self, anim, t):
        out = {}
        if not anim:
            return out
        a = self.anims[anim]
        for an in a["animators"].values():
            for ch in ("rotation", "position", "scale"):
                ks = sorted([k for k in an["keyframes"] if k["channel"] == ch], key=lambda k: k["time"])
                if not ks:
                    continue
                v = lambda k: np.array([float(k["data_points"][0][c]) for c in "xyz"])
                if t <= ks[0]["time"]:
                    val = v(ks[0])
                elif t >= ks[-1]["time"]:
                    val = v(ks[-1])
                else:
                    for k0, k1 in zip(ks, ks[1:]):
                        if k0["time"] <= t <= k1["time"]:
                            f = (t - k0["time"]) / (k1["time"] - k0["time"] or 1)
                            val = v(k0) * (1 - f) + v(k1) * f
                            break
                out[(an["name"], ch)] = val
        return out

    def faces(self, anim=None, t=0.0):
        s = self.sample(anim, t)
        world = {}
        res = []
        for name, o, parent, els in self.groups:
            o = np.array(o, float)
            r = s.get((name, "rotation"), np.zeros(3))
            p = s.get((name, "position"), np.zeros(3))
            sc = s.get((name, "scale"), np.ones(3))
            R = rot(-r[0], -r[1], r[2]) @ np.diag(sc)
            m = M4(t=o + np.array([-p[0], p[1], p[2]])) @ M4(R) @ M4(t=-o)
            world[name] = (world[parent] if parent else np.eye(4)) @ m
            W = world[name]
            for u in els:
                e = self.el[u]
                x0, y0, z0 = e["from"]; x1, y1, z1 = e["to"]
                corners = {
                    "north": ((x1, y1, z0), (x0, y1, z0), (x1, y0, z0), (0, 0, -1)),
                    "south": ((x0, y1, z1), (x1, y1, z1), (x0, y0, z1), (0, 0, 1)),
                    "east": ((x1, y1, z1), (x1, y1, z0), (x1, y0, z1), (1, 0, 0)),
                    "west": ((x0, y1, z0), (x0, y1, z1), (x0, y0, z0), (-1, 0, 0)),
                    "up": ((x0, y1, z0), (x1, y1, z0), (x0, y1, z1), (0, 1, 0)),
                    "down": ((x0, y0, z1), (x1, y0, z1), (x0, y0, z0), (0, -1, 0)),
                }
                for fn, f in e["faces"].items():
                    if f.get("texture") is None:
                        continue
                    TL, TR, BL, n = corners[fn]
                    P = [(W @ np.array([*c, 1]))[:3] for c in (TL, TR, BL)]
                    N = W[:3, :3] @ np.array(n, float)
                    res.append((P, N / (np.linalg.norm(N) or 1), f["uv"], name == "glow_eyes"))
        return res


def render(model, anim=None, t=0.0, yaw=0, pitch=12, S=8, size=(360, 420), ground=None, extra=(), scale=1.0, bg=(0, 0, 0, 0), base=None):
    W, H = size
    img = np.zeros((H, W, 4), np.uint8); img[:] = bg
    if base is not None:
        img[:] = np.array(base.convert('RGBA'))
    zb = np.full((H, W), -1e9)
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    # 카메라는 -Z(앞)에서 바라봄: 화면 오른쪽 = 모델 -X
    def proj(p):
        x, y, z = p[0] * scale, p[1] * scale, p[2] * scale
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp + z * sp, -y * sp + z * cp
        gy = ground if ground is not None else H - 30
        return np.array([W / 2 - x * S, gy - y * S, -z])
    L = np.array([0.4, 0.8, -0.45]); L /= np.linalg.norm(L)
    tex = model.tex
    allf = list(model.faces(anim, t)) + list(extra)
    # 바닥 그림자
    gy = ground if ground is not None else H - 30
    yy, xx = np.mgrid[0:H, 0:W]
    sh = (((xx - W / 2) / (11 * S * scale)) ** 2 + ((yy - gy) / (3.2 * S * scale)) ** 2) < 1
    img[sh] = (img[sh] * 0.6 + np.array([40, 60, 40, 255]) * 0.4).astype(np.uint8)
    img[sh, 3] = 255
    trans = []

    def draw(P, N, uv, glow, mode):
        A, B, Cc = [proj(p) for p in P]
        u = B - A; v = Cc - A
        det = u[0] * v[1] - u[1] * v[0]
        if abs(det) < 1e-6:
            return
        D = B + v
        xs = [A[0], B[0], Cc[0], D[0]]; ys = [A[1], B[1], Cc[1], D[1]]
        x0, x1 = max(0, int(min(xs))), min(W - 1, int(max(xs)) + 1)
        y0, y1 = max(0, int(min(ys))), min(H - 1, int(max(ys)) + 1)
        if x0 >= x1 or y0 >= y1:
            return
        gx, gyy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        dx, dy = gx - A[0], gyy - A[1]
        s_ = (dx * v[1] - dy * v[0]) / det
        t_ = (u[0] * dy - u[1] * dx) / det
        m = (s_ >= 0) & (s_ < 1) & (t_ >= 0) & (t_ < 1)
        if not m.any():
            return
        z = A[2] + s_ * u[2] + t_ * v[2]
        tu = np.clip((uv[0] + s_ * (uv[2] - uv[0])).astype(int), 0, tex.shape[1] - 1)
        tv = np.clip((uv[1] + t_ * (uv[3] - uv[1])).astype(int), 0, tex.shape[0] - 1)
        col = tex[tv, tu]
        a = col[..., 3]
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        shade = 1.0 if glow else 0.6 + 0.4 * max(0.0, float(N @ L)) + 0.08 * max(0.0, float(-N[2]))
        c = np.clip(col[..., :3] * shade, 0, 255)
        reg = img[y0:y1 + 1, x0:x1 + 1]
        if mode == "opaque":
            m &= (a == 255) & (z > sub)
            if not m.any():
                return
            reg[m, :3] = c[m].astype(np.uint8); reg[m, 3] = 255
            sub[m] = z[m]
        else:
            m &= (a > 8) & (a < 255) & (z > sub)
            if not m.any():
                return
            al = (a[..., None] / 255.0)
            reg[m, :3] = (reg[m, :3] * (1 - al[m]) + c[m] * al[m]).astype(np.uint8)
            reg[m, 3] = 255

    for P, N, uv, glow in allf:
        draw(P, N, uv, glow, "opaque")
        trans.append((P, N, uv, glow))
    # 반투명 면은 먼 것부터
    trans.sort(key=lambda f: min(proj(p)[2] for p in f[0]))
    for P, N, uv, glow in trans:
        draw(P, N, uv, glow, "trans")
    return Image.fromarray(img)
