"""등급 낚싯대(OctoFishing)에도 낚싯대 스킨이 보이게 하는 아이템 정의 생성기.

등급 낚싯대는 item_model="octofish:rod_<등급>" 이라서 바닐라 fishing_rod.json 을 안 탄다.
그래서 assets/minecraft/items/fishing_rod.json 을 그대로 복사하고, 스킨이 없을 때(fallback)만
등급 모양(octofish:item/rod_<등급>, 던지면 _cast)으로 바꿔서
assets/octofish/items/rod_<등급>.json 으로 저장한다.
→ 낚싯대 스킨을 새로 추가해도 릴리스 때 이 스크립트가 다시 돌아 자동으로 맞춰짐.
"""
import copy, json, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "pack", "assets")
SRC = os.path.join(ROOT, "minecraft", "items", "fishing_rod.json")
TIERS = ["iron", "gold", "diamond", "netherite"]


def tier_model(tier):
    return {
        "type": "minecraft:condition",
        "property": "minecraft:fishing_rod/cast",
        "on_true": {"type": "minecraft:model", "model": f"octofish:item/rod_{tier}_cast"},
        "on_false": {"type": "minecraft:model", "model": f"octofish:item/rod_{tier}"},
    }


def main():
    base = json.load(open(SRC, encoding="utf-8"))
    model = base.get("model", {})
    if model.get("type") != "minecraft:range_dispatch" or "fallback" not in model:
        print("fishing_rod.json 이 예상한 모양(range_dispatch + fallback)이 아님", file=sys.stderr)
        sys.exit(1)
    out_dir = os.path.join(ROOT, "octofish", "items")
    os.makedirs(out_dir, exist_ok=True)
    for t in TIERS:
        d = copy.deepcopy(base)
        d["model"]["fallback"] = tier_model(t)
        with open(os.path.join(out_dir, f"rod_{t}.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(f"octofish rod 정의 {len(TIERS)}개 생성 (스킨 {len(model.get('entries', []))}개 포함)")


if __name__ == "__main__":
    main()
