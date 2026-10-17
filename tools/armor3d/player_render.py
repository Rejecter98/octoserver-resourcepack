"""플레이어 + 갑옷(입은 모습 텍스처, box UV) + 머리 아이템 입체 모델 미리보기 렌더러 (정사영, z-버퍼).
좌표: 픽셀 단위, 발 = y0, 앞 = -Z (카메라 쪽), 플레이어 오른쪽 = -X (화면 왼쪽)."""
import json, math
import numpy as np
from PIL import Image

PPU = 12  # 화면 픽셀 / 월드 픽셀


class Canvas:
    def __init__(self, w, h, ox, oy):
        self.img = np.zeros((h, w, 4), np.float32)
        self.z = np.full((h, w), 1e9, np.float32)
        self.w, self.h, self.ox, self.oy = w, h, ox, oy

    def proj(self, p, R):
        q = R @ np.asarray(p, float)
        return np.array([self.ox + q[0] * PPU, self.oy - q[1] * PPU, q[2]])

    def quad(self, P0, P1, P2, tex, uvr, shade, R, flip=False):
        """P0=왼쪽 위, P1=오른쪽 위, P2=왼쪽 아래 (텍스처 기준). uvr=(u0,v0,u1,v1) 텍스처 픽셀."""
        a, b, c = self.proj(P0, R), self.proj(P1, R), self.proj(P2, R)
        e1, e2 = b - a, c - a
        det = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(det) < 1e-6:
            return
        d = a + e1 + e2
        xs = [a[0], b[0], c[0], d[0]]; ys = [a[1], b[1], c[1], d[1]]
        x0, x1 = max(0, int(min(xs))), min(self.w, int(max(xs)) + 1)
        y0, y1 = max(0, int(min(ys))), min(self.h, int(max(ys)) + 1)
        if x0 >= x1 or y0 >= y1:
            return
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        dx, dy = X - a[0], Y - a[1]
        s = (dx * e2[1] - dy * e2[0]) / det
        t = (e1[0] * dy - e1[1] * dx) / det
        inside = (s >= 0) & (s < 1) & (t >= 0) & (t < 1)
        if flip:
            s = 1 - s
        u0, v0, u1, v1 = uvr
        th, tw = tex.shape[:2]
        U = np.clip((u0 + s * (u1 - u0)).astype(int), 0, tw - 1)
        V = np.clip((v0 + t * (v1 - v0)).astype(int), 0, th - 1)
        col = tex[V, U]
        depth = a[2] + s * e1[2] + t * e2[2] if not flip else a[2] + (1 - s) * e1[2] + t * e2[2]
        m = inside & (col[..., 3] > 0.5) & (depth < self.z[y0:y1, x0:x1])
        reg = self.img[y0:y1, x0:x1]
        reg[m, :3] = col[m, :3] * shade
        reg[m, 3] = 1
        self.z[y0:y1, x0:x1][m] = depth[m]

    def image(self, bg):
        out = np.zeros_like(self.img); out[..., :3] = np.array(bg) / 255; out[..., 3] = 1
        a = self.img[..., 3:4]
        out[..., :3] = self.img[..., :3] * a + out[..., :3] * (1 - a)
        return Image.fromarray((out * 255).astype(np.uint8), "RGBA")


SH = {"front": 0.92, "back": 0.78, "right": 0.72, "left": 0.84, "top": 1.0, "bottom": 0.6}


def box(cv, R, frm, to, tex, uv, size, k, inflate=0.0, mirror=False):
    """마인크래프트 box UV 큐브. uv=(u,v), size=(w,h,d) 텍스처 픽셀, k = 텍스처 배율(고해상도면 2)."""
    (x0, y0, z0), (x1, y1, z1) = [np.array(frm) - inflate, np.array(to) + inflate]
    u, v = uv; w, h, d = size
    r = lambda a, b, c, e: (a * k, b * k, c * k, e * k)
    front = r(u + d, v + d, u + d + w, v + d + h)
    back = r(u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h)
    rside = r(u, v + d, u + d, v + d + h)            # 플레이어 오른쪽(-X)
    lside = r(u + d + w, v + d, u + 2 * d + w, v + d + h)
    top = r(u + d, v, u + d + w, v + d)
    bot = r(u + d + w, v, u + 2 * d + w, v + d)
    if mirror:
        rside, lside = lside, rside
    f = mirror
    # 앞(-Z): 왼쪽 위 = (-X 쪽, 위)
    cv.quad((x0, y1, z0), (x1, y1, z0), (x0, y0, z0), tex, front, SH["front"], R, f)
    cv.quad((x1, y1, z1), (x0, y1, z1), (x1, y0, z1), tex, back, SH["back"], R, f)
    cv.quad((x0, y1, z1), (x0, y1, z0), (x0, y0, z1), tex, rside, SH["right"], R, f)
    cv.quad((x1, y1, z0), (x1, y1, z1), (x1, y0, z0), tex, lside, SH["left"], R, f)
    cv.quad((x0, y1, z1), (x1, y1, z1), (x0, y1, z0), tex, top, SH["top"], R, f)
    cv.quad((x0, y0, z0), (x1, y0, z0), (x0, y0, z1), tex, bot, SH["bottom"], R, f)


def skin_tex():
    """간단한 기본 스킨 (64x64)."""
    t = np.zeros((64, 64, 4), np.float32)
    def fill(x0, y0, x1, y1, c):
        t[y0:y1, x0:x1, :3] = np.array(c) / 255; t[y0:y1, x0:x1, 3] = 1
    SK, HA, SH_, PA, SO = (236, 200, 170), (120, 84, 60), (120, 196, 200), (90, 110, 170), (80, 70, 70)
    fill(0, 0, 32, 16, SK); fill(8, 0, 16, 8, HA); fill(0, 8, 32, 10, HA); fill(24, 8, 32, 16, HA)  # 머리
    fill(8, 8, 16, 10, HA); fill(9, 12, 11, 13, (40, 40, 60)); fill(13, 12, 15, 13, (40, 40, 60)); fill(10, 14, 14, 15, (200, 130, 120))
    fill(16, 16, 40, 32, SH_); fill(40, 16, 56, 32, SH_); fill(44, 28, 48, 32, SK); fill(40, 28, 56, 32, SK)
    fill(0, 16, 16, 32, PA); fill(0, 29, 16, 32, SO)
    fill(32, 48, 48, 64, SH_); fill(32, 60, 48, 64, SK); fill(16, 48, 32, 64, PA); fill(16, 61, 32, 64, SO)
    return t


def load(path):
    return np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255


def item_model(cv, R, path, texdir):
    """머리 아이템 입체 모델: 모델 0~16 → 머리 중심 (0,28,0), 1 단위 = 10/16 px."""
    m = json.load(open(path))
    tname = m["textures"]["0"].split("/")[-1]
    tex = load(f"{texdir}/{tname}.png")
    k = tex.shape[1] / 16
    sc = 10 / 16
    T = lambda p: ((p[0] - 8) * sc, 28 + (p[1] - 8) * sc, (p[2] - 8) * sc)
    for e in m["elements"]:
        (x0, y0, z0), (x1, y1, z1) = e["from"], e["to"]
        F = e["faces"]
        def q(face, A, B, C, s):
            if face in F:
                u0, v0, u1, v1 = F[face]["uv"]
                cv.quad(T(A), T(B), T(C), tex, (u0 * k, v0 * k, u1 * k, v1 * k), s, R)
        q("north", (x0, y1, z0), (x1, y1, z0), (x0, y0, z0), SH["front"])
        q("south", (x1, y1, z1), (x0, y1, z1), (x1, y0, z1), SH["back"])
        q("west", (x0, y1, z1), (x0, y1, z0), (x0, y0, z1), SH["right"])
        q("east", (x1, y1, z0), (x1, y1, z1), (x1, y0, z0), SH["left"])
        q("up", (x0, y1, z1), (x1, y1, z1), (x0, y1, z0), SH["top"])
        q("down", (x0, y0, z0), (x1, y0, z0), (x0, y0, z1), SH["bottom"])


def render(armor, head_model=None, texdir=None, yaw=0, pitch=-8, size=(420, 560), bg=(58, 54, 70)):
    """armor = {"humanoid": path or None, "humanoid_leggings": path, "parts": set("helmet","chest","legs","boots")}"""
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    R = Rx @ Ry
    cv = Canvas(size[0], size[1], size[0] / 2, size[1] - 30)
    sk = skin_tex()
    box(cv, R, (-4, 24, -4), (4, 32, 4), sk, (0, 0), (8, 8, 8), 1)
    box(cv, R, (-4, 12, -2), (4, 24, 2), sk, (16, 16), (8, 12, 4), 1)
    box(cv, R, (-8, 12, -2), (-4, 24, 2), sk, (40, 16), (4, 12, 4), 1)
    box(cv, R, (4, 12, -2), (8, 24, 2), sk, (32, 48), (4, 12, 4), 1)
    box(cv, R, (-4, 0, -2), (0, 12, 2), sk, (0, 16), (4, 12, 4), 1)
    box(cv, R, (0, 0, -2), (4, 12, 2), sk, (16, 48), (4, 12, 4), 1)
    parts = armor.get("parts", set())
    if armor.get("humanoid"):
        t = load(armor["humanoid"]); k = t.shape[1] / 64
        if "helmet" in parts:
            box(cv, R, (-4, 24, -4), (4, 32, 4), t, (0, 0), (8, 8, 8), k, 1.0)
        if "chest" in parts:
            box(cv, R, (-4, 12, -2), (4, 24, 2), t, (16, 16), (8, 12, 4), k, 1.01)
            box(cv, R, (-8, 12, -2), (-4, 24, 2), t, (40, 16), (4, 12, 4), k, 1.0)
            box(cv, R, (4, 12, -2), (8, 24, 2), t, (40, 16), (4, 12, 4), k, 1.0, mirror=True)
        if "boots" in parts:
            box(cv, R, (-4, 0, -2), (0, 12, 2), t, (0, 16), (4, 12, 4), k, 1.0)
            box(cv, R, (0, 0, -2), (4, 12, 2), t, (0, 16), (4, 12, 4), k, 1.0, mirror=True)
    if armor.get("humanoid_leggings") and "legs" in parts:
        t = load(armor["humanoid_leggings"]); k = t.shape[1] / 64
        box(cv, R, (-4, 12, -2), (4, 24, 2), t, (16, 16), (8, 12, 4), k, 0.5)
        box(cv, R, (-4, 0, -2), (0, 12, 2), t, (0, 16), (4, 12, 4), k, 0.5)
        box(cv, R, (0, 0, -2), (4, 12, 2), t, (0, 16), (4, 12, 4), k, 0.5, mirror=True)
    if head_model:
        item_model(cv, R, head_model, texdir)
    return cv.image(bg)
