"""BetterModel 용 .bbmodel 생성 공용 라이브러리.

모델 스크립트는 BONES / CUBES / MATS / 애니메이션을 정의하고 build() 를 호출한다.
- 좌표: Blockbench free 포맷 픽셀 단위, 발밑 중심 = (0,0,0), 앞 = 북쪽(-Z), 오른쪽(+X)
- 큐브 회전은 쓰지 않음 (뼈 회전만) → BetterModel/바닐라 모델 제약 회피
- 애니메이션 값은 Blockbench 값 그대로: 회전 x- = 팔을 앞으로 듦 / x+ = 앞으로 숙임, z+ = 오른팔(+X) 바깥
- 뼈 이름 태그: h_ = 머리(시선 따라감), glow_ = 발광
"""
import base64, io, json, random, uuid
from PIL import Image

FACES = ("north", "east", "south", "west", "up", "down")


def C(r, g, b, a=255):
    return (r, g, b, a)


def face_size(f, t, face):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy),
            "up": (dx, dz), "down": (dx, dz)}[face]


def paint_default(mat, spec, face, w, h, rnd):
    """spec = (base, dark, light, style)."""
    b, d, l, style = spec
    px = [[b] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r = rnd.random()
            if style == "flat":
                px[y][x] = b
            elif style == "glow":
                px[y][x] = l if r < 0.25 else b
            elif style == "grain" and face not in ("up", "down"):
                px[y][x] = d if (x * 7 + (y // 3) * 3) % 5 == 0 else (l if r < 0.12 else b)
            elif style == "metal":
                px[y][x] = l if y == 0 else (d if y == h - 1 or (x in (0, w - 1) and r < 0.5) else (l if r < 0.06 else b))
                if face not in ("up", "down") and h >= 4 and w >= 4 and y in (1, h - 2) and x in (1, w - 2):
                    px[y][x] = l  # 리벳
            elif style == "fur":
                px[y][x] = l if r < 0.3 else (d if r > 0.9 else b)
            elif style == "stripe":  # 가로 줄무늬 (2칸 간격)
                px[y][x] = d if (y // 2) % 2 else b
                if r < 0.08:
                    px[y][x] = l
            else:  # noise
                px[y][x] = l if r < 0.15 else (d if r > 0.9 else b)
    return px


def build(out, name, bones, cubes, mats, anims, deco=None, seed=7, tex_sizes=((64, 64), (128, 64), (128, 128))):
    """bones: [(bone, pivot, parent)], cubes: [(cube, bone, from, to, mat)],
    mats: {mat: (base, dark, light, style)}, anims: {name: (length, loop, {bone: {channel: [(t,(x,y,z))]}})},
    deco(cube, face, px, w, h, mat) -> px (선택)."""
    reqs = []
    for cname, bone, f, t, mat in cubes:
        for face in FACES:
            w, h = face_size(f, t, face)
            if min(w, h) < 0.5 and mats[mat][3] == "glow" and face != "north":
                continue
            reqs.append((cname, face, max(1, round(w)), max(1, round(h)), mat))
    reqs.sort(key=lambda r: (-r[3], -r[2]))
    for TW, TH in tex_sizes:
        x = y = rowh = 0
        uvs, ok = {}, True
        for cname, face, w, h, mat in reqs:
            if x + w > TW:
                x, y, rowh = 0, y + rowh, 0
            if y + h > TH:
                ok = False
                break
            uvs[(cname, face)] = (x, y, w, h, mat)
            x += w
            rowh = max(rowh, h)
        if ok:
            break
    else:
        raise SystemExit("텍스처 공간 부족")
    rnd = random.Random(seed)
    img = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    for (cname, face), (x, y, w, h, mat) in sorted(uvs.items(), key=lambda kv: (kv[1][1], kv[1][0])):
        px = paint_default(mat, mats[mat], face, w, h, rnd)
        if deco:
            px = deco(cname, face, px, w, h, mat) or px
        for yy, row in enumerate(px):
            for xx, c in enumerate(row):
                img.putpixel((x + xx, y + yy), c)

    ns = uuid.UUID("6f6f6f6f-0000-4000-8000-00000000b0b0")
    uid = lambda s: str(uuid.uuid5(ns, f"{name}:{s}"))
    pivot = {b: p for b, p, _ in bones}
    elements = []
    for cname, bone, f, t, mat in cubes:
        faces = {}
        for face in FACES:
            if (cname, face) in uvs:
                x, y, w, h, _ = uvs[(cname, face)]
                faces[face] = {"uv": [x, y, x + w, y + h], "texture": 0}
            else:
                faces[face] = {"uv": [0, 0, 0, 0], "texture": None}
        elements.append({"name": cname, "box_uv": False, "rescale": False, "locked": False, "light_emission": 0,
                         "render_order": "default", "allow_mirror_modeling": True, "from": f, "to": t, "autouv": 0,
                         "color": 0, "origin": pivot[bone], "faces": faces, "type": "cube", "uuid": uid("e:" + cname)})

    def group(b):
        kids = [uid("e:" + n) for n, bb, *_ in cubes if bb == b]
        kids += [group(c) for c, _, p in bones if p == b]
        return {"name": b, "origin": pivot[b], "color": 0, "uuid": uid("g:" + b), "export": True, "mirror_uv": False,
                "isOpen": True, "locked": False, "visibility": True, "autouv": 0, "selected": False, "children": kids}

    fmt = lambda v: str(round(v, 4))
    animations = []
    for an, (length, loop, tracks) in anims.items():
        animators = {}
        for bone, chans in tracks.items():
            assert bone in pivot, (an, bone)
            kfs = []
            for ch, pts in chans.items():
                for tm, v in pts:
                    kfs.append({"channel": ch, "data_points": [{"x": fmt(v[0]), "y": fmt(v[1]), "z": fmt(v[2])}],
                                "uuid": uid(f"k:{an}:{bone}:{ch}:{tm}"), "time": tm, "color": -1,
                                "interpolation": "linear"})
            animators[uid("g:" + bone)] = {"name": bone, "type": "bone", "keyframes": kfs}
        animations.append({"uuid": uid("a:" + an), "name": an, "loop": loop, "override": False, "length": length,
                           "snapping": 20, "selected": False, "anim_time_update": "", "blend_weight": "",
                           "start_delay": "", "loop_delay": "", "animators": animators})
    buf = io.BytesIO()
    img.save(buf, "PNG")
    roots = [b for b, _, p in bones if p is None]
    model = {
        "meta": {"format_version": "4.10", "model_format": "free", "box_uv": False},
        "name": name, "model_identifier": "", "visible_box": [2, 3, 0],
        "variable_placeholders": "", "variable_placeholder_buttons": [], "timeline_setups": [],
        "unhandled_root_fields": {}, "resolution": {"width": TW, "height": TH},
        "elements": elements, "outliner": [group(r) for r in roots],
        "textures": [{"path": "", "name": f"{name}.png", "folder": "", "namespace": "", "id": "0",
                      "group": "", "width": TW, "height": TH, "uv_width": TW, "uv_height": TH,
                      "particle": False, "use_as_default": False, "layers_enabled": False, "sync_to_project": "",
                      "render_mode": "default", "render_sides": "auto", "pbr_channel": "color", "frame_time": 1,
                      "frame_order_type": "loop", "frame_order": "", "frame_interpolate": False, "visible": True,
                      "internal": True, "saved": False, "uuid": uid("tex"),
                      "source": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}],
        "animations": animations,
    }
    json.dump(model, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"{name}: 큐브 {len(cubes)} · 텍스처 {TW}x{TH} · 애니메이션 {list(anims)} → {out}")
    return model
