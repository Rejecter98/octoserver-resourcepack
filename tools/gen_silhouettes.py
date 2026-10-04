#!/usr/bin/env python3
"""도감 미등록 실루엣 생성기.

서버 도감 플러그인이 요청하는 모델을 만든다.
  - 아이템 실루엣:  assets/dogam/items/silhouette/<아이템id>.json        (26.2 의 모든 아이템)
  - 스킨 실루엣:    assets/dogam/items/silhouette/skin/<스킨id>.json    (skins.yml 의 모든 스킨)
  - 입체 모델용:    assets/dogam/models/silhouette/[skin/]<id>.json
실루엣 = 원래 모양 그대로, 색만 검정 (minecraft:constant 틴트).

바닐라 데이터는 Mojang 버전 매니페스트에서 클라이언트 jar 를 받아 items/*.json · models/** 만 읽는다
(jar·텍스처는 레포에 넣지 않음). 네트워크가 막힌 곳에서는 --assets-dir 로 압축 푼 assets 폴더를 지정.

사용:
  python3 tools/gen_silhouettes.py                       # Mojang 에서 26.2 받아서 pack/assets/dogam 생성
  python3 tools/gen_silhouettes.py --version 26.3        # 마크 버전 업데이트 때
  python3 tools/gen_silhouettes.py --assets-dir <dir>    # <dir>/assets/minecraft/... 를 직접 사용
"""
import argparse, copy, io, json, os, shutil, sys, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
DEFAULT_VERSION = "26.2"
GRAY = "minecraft:item/gray_stained_glass_pane"      # 틴트가 안 되는 아이템(special 등)의 대체 모델


# ------------------------------------------------------------------ 바닐라 데이터 읽기
class Vanilla:
    """items/*.json 과 models/** 만 메모리에 들고 있음"""

    def __init__(self):
        self.items, self.models = {}, {}

    def add(self, rel, data):
        rel = rel.replace("\\", "/")
        if not rel.endswith(".json"):
            return
        if rel.startswith("assets/minecraft/items/"):
            name = rel[len("assets/minecraft/items/"):-5]
            if "/" not in name and not name.startswith("_"):
                self.items[name] = json.loads(data)
        elif rel.startswith("assets/minecraft/models/"):
            name = rel[len("assets/minecraft/models/"):-5]
            if not name.split("/")[-1].startswith("_"):
                self.models["minecraft:" + name] = json.loads(data)


def load_from_mojang(version):
    def get(url):
        with urllib.request.urlopen(url, timeout=120) as r:
            return r.read()
    man = json.loads(get(MANIFEST))
    ent = next((v for v in man["versions"] if v["id"] == version), None)
    if not ent:
        sys.exit(f"버전 {version} 을 매니페스트에서 찾지 못함")
    jar_url = json.loads(get(ent["url"]))["downloads"]["client"]["url"]
    print(f"[다운로드] {version} client jar")
    v = Vanilla()
    with zipfile.ZipFile(io.BytesIO(get(jar_url))) as z:
        for n in z.namelist():
            if n.startswith(("assets/minecraft/items/", "assets/minecraft/models/")) and n.endswith(".json"):
                v.add(n, z.read(n))
    return v


def load_from_dir(d):
    v = Vanilla()
    for sub in ("items", "models"):
        base = os.path.join(d, "assets", "minecraft", sub)
        for root, _, files in os.walk(base):
            for f in files:
                p = os.path.join(root, f)
                with open(p, "rb") as fh:
                    v.add(os.path.relpath(p, d), fh.read())
    return v


# ------------------------------------------------------------------ 모델 해석
def norm(mid):
    if mid.startswith("builtin/"):
        return mid
    return mid if ":" in mid else "minecraft:" + mid


class Models:
    def __init__(self, vanilla, pack_assets):
        self.v, self.pack = vanilla, pack_assets

    def get(self, mid):
        mid = norm(mid)
        if mid.startswith("builtin/"):
            return None
        ns, path = mid.split(":", 1)
        p = os.path.join(self.pack, ns, "models", path + ".json")
        if os.path.exists(p):                      # 리소스팩 쪽(cosmetics 등)이 우선
            with open(p) as f:
                return json.load(f)
        return self.v.models.get(mid)

    def chain(self, mid):
        out, seen = [], set()
        while mid and not norm(mid).startswith("builtin/") and mid not in seen:
            seen.add(mid)
            m = self.get(mid)
            if m is None:
                raise KeyError(mid)
            out.append((norm(mid), m))
            mid = m.get("parent")
        return out, (norm(mid) if mid else None)

    def classify(self, mid):
        """→ ('flat', 레이어 수) / ('block', elements) / ('none', None)"""
        chain, root = self.chain(mid)
        for _, m in chain:
            if "elements" in m:
                return "block", m["elements"]
        if root == "builtin/generated":
            layers = set()
            for _, m in chain:
                for k in m.get("textures", {}):
                    if k.startswith("layer") and k[5:].isdigit():
                        layers.add(int(k[5:]))
            if layers:
                return "flat", max(layers) + 1
        return "none", None


# ------------------------------------------------------------------ 대표 모델 고르기
def pick(node):
    """아이템 정의 트리에서 실루엣으로 쓸 minecraft:model 노드 하나. 틴트 불가면 None."""
    t = node.get("type", "").replace("minecraft:", "")
    if t == "model":
        return node
    if t == "condition":
        return pick(node["on_false"])
    if t == "select":
        if node.get("property") == "minecraft:display_context":   # 도감은 GUI 에 보이므로 gui 케이스 우선
            for c in node.get("cases", []):
                w = c["when"] if isinstance(c["when"], list) else [c["when"]]
                if "gui" in w:
                    return pick(c["model"])
        if "fallback" in node:
            return pick(node["fallback"])
        return pick(node["cases"][0]["model"]) if node.get("cases") else None
    if t == "range_dispatch":
        if "fallback" in node:
            return pick(node["fallback"])
        return pick(node["entries"][0]["model"]) if node.get("entries") else None
    if t == "composite":
        if any(_has_special(m) for m in node.get("models", [])):
            return None
        for m in node.get("models", []):
            r = pick(m)
            if r:
                return r
        return None
    return None                                     # special, empty, bundle/selected_item 등


def _has_special(n):
    if isinstance(n, dict):
        if n.get("type") in ("minecraft:special",):
            return True
        return any(_has_special(v) for v in n.values())
    if isinstance(n, list):
        return any(_has_special(v) for v in n)
    return False


# ------------------------------------------------------------------ 실루엣 만들기
def tint(color, n):
    return [{"type": "minecraft:constant", "value": color} for _ in range(max(1, n))]


def silhouette(models, src_node, model_out_id, model_out_path, color):
    """→ (아이템 정의 dict, 종류) — 종류: flat / block / gray"""
    node = pick(src_node) if src_node else None
    if node is None:
        return {"model": {"type": "minecraft:model", "model": GRAY}}, "gray"
    mid = norm(node["model"])
    kind, data = models.classify(mid)
    if kind == "flat":
        return {"model": {"type": "minecraft:model", "model": mid, "tints": tint(color, data)}}, "flat"
    if kind == "block":
        els = copy.deepcopy(data)
        for e in els:
            for f in e.get("faces", {}).values():
                f["tintindex"] = 0
        os.makedirs(os.path.dirname(model_out_path), exist_ok=True)
        with open(model_out_path, "w") as f:
            json.dump({"parent": mid, "elements": els}, f, separators=(",", ":"))
        return {"model": {"type": "minecraft:model", "model": model_out_id, "tints": tint(color, 1)}}, "block"
    return {"model": {"type": "minecraft:model", "model": GRAY}}, "gray"


def load_skins(path):
    import yaml
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["skins"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default=DEFAULT_VERSION)
    ap.add_argument("--assets-dir", help="Mojang 대신 이 폴더의 assets/minecraft 사용")
    ap.add_argument("--pack", default=os.path.join(ROOT, "pack"))
    ap.add_argument("--skins", default=os.path.join(ROOT, "skins.yml"))
    ap.add_argument("--color", default="0x000000", help="실루엣 색 (너무 새까매서 안 보이면 0x202020)")
    a = ap.parse_args()
    color = int(a.color, 16)

    van = load_from_dir(a.assets_dir) if a.assets_dir else load_from_mojang(a.version)
    print(f"[바닐라] 아이템 {len(van.items)}개 · 모델 {len(van.models)}개")
    if len(van.items) < 1000:
        sys.exit("아이템 정의가 너무 적음 — 다운로드/경로 확인")

    assets = os.path.join(a.pack, "assets")
    out = os.path.join(assets, "dogam")
    if os.path.exists(out):
        shutil.rmtree(out)                          # 항상 새로 생성 (지워진 아이템이 남지 않게)
    models = Models(van, assets)
    report = {"flat": [], "block": [], "gray": []}

    def emit(rel, defn):
        p = os.path.join(out, "items", "silhouette", rel + ".json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(defn, f, separators=(",", ":"))

    for item, d in sorted(van.items.items()):
        defn, kind = silhouette(models, d["model"], f"dogam:silhouette/{item}",
                                os.path.join(out, "models", "silhouette", item + ".json"), color)
        emit(item, defn)
        report[kind].append(item)

    skins = load_skins(a.skins)
    skin_gray = []
    for sid, s in skins.items():
        mat = s["allowed-materials"][0].lower()
        p = os.path.join(assets, "minecraft", "items", mat + ".json")
        node = None
        if os.path.exists(p):
            with open(p) as f:
                ent = [e for e in json.load(f)["model"].get("entries", []) if e["threshold"] == s["custom-model-data"]]
            node = ent[0]["model"] if ent else None
        defn, kind = silhouette(models, node, f"dogam:silhouette/skin/{sid}",
                                os.path.join(out, "models", "silhouette", "skin", sid + ".json"), color)
        emit(f"skin/{sid}", defn)
        if kind == "gray":
            skin_gray.append(sid)

    n_items = len(os.listdir(os.path.join(out, "items", "silhouette"))) - 1   # skin 폴더 제외
    print(f"[실루엣] 아이템 {n_items}/{len(van.items)} (평면 {len(report['flat'])} · 입체 {len(report['block'])} · "
          f"회색 대체 {len(report['gray'])}) · 스킨 {len(skins)} (회색 대체 {len(skin_gray)})")
    print("[회색 대체] " + ", ".join(report["gray"]))
    if skin_gray:
        print("[스킨 회색 대체] " + ", ".join(skin_gray))
    if n_items != len(van.items):
        sys.exit("아이템 수 불일치")
    with open(os.path.join(out, "report.json"), "w") as f:     # 확인용 (게임은 무시)
        json.dump({"version": a.version, "items": len(van.items), "flat": len(report["flat"]),
                   "block": len(report["block"]), "gray": report["gray"], "skins": len(skins),
                   "skin_gray": skin_gray}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
