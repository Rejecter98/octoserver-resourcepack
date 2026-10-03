# octoserver-resourcepack — 작업 지침

Paper 26.2 마인크래프트 서버의 스킨 리소스팩(CosmeticPack) 레포.
사용자가 GitHub에 직접 들어가지 않아도 **스킨 제작 → 사용자 승인 → 업로드 → 릴리스 → sha1 안내**까지 끝내는 것이 목표.
사용자와의 대화는 한국어로.

## 레포 구조
- `pack/` — 리소스팩 원본. `pack/pack.mcmeta` 가 zip 최상위가 됨
- `skins.yml` — CosmeticSkins 플러그인 설정 원본 (서버의 `plugins/CosmeticSkins/skins.yml`)
- `.github/workflows/release.yml` — main 에 `pack/**` 또는 `skins.yml` 변경이 push 되면
  `CosmeticPack.zip` 빌드 → sha1 계산 → 기존 `vN` 중 최대 N+1 태그로 릴리스 생성
  (첨부: `CosmeticPack.zip`, `skins.yml` / 본문 첫 줄 `sha1: <값>`, 그 아래 변경된 스킨 목록)

## 서버 플러그인 (CosmeticSkins) 연동
- 서버 폴더: `plugins/CosmeticSkins` (버전 없는 이름) — skins.yml 은 `plugins/CosmeticSkins/skins.yml`
- **스킨 토큰 아이콘**: 토큰은 종이(PAPER) 아이템이지만, 서버가 `item_model` 을 그 스킨의 대표 재질로 바꾸고
  같은 custom_model_data 를 붙여서 스킨 모양으로 보여줌
  - 대표 재질 = allowed-materials 중 다이아 > 네더라이트 > 철 > 첫 번째 순
    (예: 검 → DIAMOND_SWORD, 말 갑옷 → DIAMOND_HORSE_ARMOR, 활 → BOW)
  - 그래서 allowed-materials 에 넣은 **모든 재질**의 `assets/minecraft/items/<재질>.json` 에
    그 스킨의 entry 가 반드시 있어야 함 (빠지면 토큰·아이템이 기본 모양으로 보임)
  - 토큰용 `paper.json` 같은 별도 파일은 만들지 말 것
- **display-name** 은 토큰 이름과 스킨 도감 이름으로 그대로 쓰임
  → 한국어 + `&` 색코드로 예쁘게 (테마 색 하나로 통일, 예: 솜사탕 `&d`, 서리 `&b`, 불꽃 `&c`, 벚꽃 `&d`)
  - 이미 쓰이는 이름과 겹치지 않게, 너무 길지 않게 (도감 한 줄에 들어가도록)

## 리소스팩 구조
- `pack.mcmeta`: min_format/max_format 88 (26.2 리소스팩 포맷)
- 텍스처: `pack/assets/cosmetics/textures/item/<스킨id>.png` (16x16 픽셀아트)
- 모델: `pack/assets/cosmetics/models/item/<스킨id>.json`
  → `{"parent": "minecraft:item/handheld", "textures": {"layer0": "cosmetics:item/<스킨id>"}}`
  (갑옷 스킨은 바닐라 갑옷처럼 `minecraft:item/generated`)
- 바닐라 갑옷 아이템 정의는 장식(trim)·가죽 염색용 `minecraft:select` 구조라서, 갑옷 아이템 정의를
  새로 만들 때는 fallback 에 바닐라 정의의 `model` 을 그대로 넣을 것
  (바닐라 원본: `git ls-remote https://github.com/InventivetalentDev/minecraft-assets` 의 버전 브랜치, 예: `26.2`)
- 아이템 정의: `pack/assets/minecraft/items/<아이템>.json` (재질 있는 건 `<재질>_<도구>.json`)
  → `minecraft:range_dispatch` / property `minecraft:custom_model_data` / index 0,
    fallback 은 바닐라 모델, entries 에 threshold 별 모델 (`cosmetics:item/<스킨id>`)
- 스킨 모델 parent 는 해당 바닐라 아이템 모델과 같은 계열로 (도구·무기 `item/handheld`,
  낚싯대·당근 낚싯대 `item/handheld_rod`, 가위·부싯돌·갑옷·말/늑대 갑옷·겉날개 `item/generated` 등 — 바닐라 모델을 확인)
- 기존 스킨 12종: flame/frost/sakura × blade/pickaxe/axe/shovel = custom-model-data 100001~100012
- 솜사탕 신규 16종: cotton_candy_<category> (elytra ~ shield) = 100017~100032
- 솜사탕 방어구 4종: cotton_candy_helmet/chestplate/leggings/boots = 100013~100016
  (가죽·사슬·구리·철·금·다이아·네더라이트, equipment-asset `cosmetics:cotton_candy`)
- 갑옷 입은 모습 (세트마다, `<세트이름>` 예: cotton_candy):
  - `pack/assets/cosmetics/equipment/<세트이름>.json`
    → `{"layers":{"humanoid":[{"texture":"cosmetics:<세트이름>"}],"humanoid_leggings":[{"texture":"cosmetics:<세트이름>"}]}}`
  - `pack/assets/cosmetics/textures/entity/equipment/humanoid/<세트이름>.png` (64x32, 투구·흉갑·부츠)
  - `pack/assets/cosmetics/textures/entity/equipment/humanoid_leggings/<세트이름>.png` (64x32, 레깅스)
  - UV 배치는 바닐라 `textures/entity/equipment/humanoid(_leggings)/iron.png` 와 같게
    (바닐라 원본을 모양·명암 기준으로 쓰고 색만 바꾸는 방식이 안전)
- `pack/assets/servermenu/` (메뉴 GUI 배경·폰트) 는 다른 플러그인용 → **절대 수정 금지**
- 참고: 26.2 에는 구리 도구·갑옷이 있지만, 기존 도구 스킨 12종에는 아직 구리가 없음 (나무·돌·철·금·다이아·네더라이트만)

## 규칙
- 새 custom-model-data 는 skins.yml 에서 가장 큰 값 +1 부터, 절대 중복 금지
- `assets/minecraft/items/*.json` 은 덮어쓰지 말고 entries 에 추가, threshold 오름차순 유지
- 스킨 하나는 같은 종류 아이템 전 재질에 적용, skins.yml allowed-materials 도 동일
  - 도구·무기 (검·곡괭이·도끼·삽·괭이·창): 나무·돌·구리·철·금·다이아·네더라이트 (7종)
  - 갑옷: 가죽·사슬·구리·철·금·다이아·네더라이트 (7종)
  - 말 갑옷: 가죽·구리·철·금·다이아·네더라이트 (6종, `<재질>_HORSE_ARMOR`)
  - 그 외(철퇴·삼지창·활·석궁·방패·가위·낚싯대·부싯돌·브러시·망원경·당근 낚싯대·겉날개·늑대 갑옷)는 아이템 1종
- 창(spear)은 26.2 신규 아이템 → 재질 7종 전부(`WOODEN_SPEAR` ~ `NETHERITE_SPEAR`) allowed-materials 에 넣을 것
- skins.yml category 는 아래 24종 중 하나 (서버 CosmeticSkins 의 부위 목록과 동일)
  - 방어구: helmet, chestplate, leggings, boots, elytra, horse_armor, wolf_armor
  - 도구: pickaxe, axe, shovel, hoe, shears, fishing_rod, flint_and_steel, brush, spyglass, carrot_on_a_stick
  - 무기: sword, spear, mace, trident, bow, crossbow, shield
- 사용 상태가 있는 아이템 (활·석궁·방패·삼지창·낚싯대·브러시·망원경, 그리고 창·겉날개·늑대 갑옷처럼
  바닐라 정의가 select/condition 구조인 것 전부):
  - `assets/minecraft/items/<아이템>.json` 의 fallback 에 **바닐라 정의(상태별 구조, transformation 포함)를 그대로** 유지
    → 스킨 없는 아이템의 당기기·막기·던지기·던짐·솔질·망원경 애니메이션이 절대 깨지면 안 됨
  - 스킨 entry 의 model 도 바닐라와 같은 상태 구조로 만들고, 상태마다 스킨 모델을 따로 만들 것
    - 활: 기본 + `_pulling_0/1/2` (using_item → use_duration)
    - 석궁: 기본 + `_pulling_0/1/2` + `_arrow` + `_firework` (charge_type / crossbow/pull)
    - 낚싯대: 기본 + `_cast` (fishing_rod/cast)
    - 브러시: 기본 + `_brushing_0/1/2` (use_cycle)
    - 망원경·창·삼지창: 인벤토리용 + 손에 든 모델 (display_context 로 구분)
    - 겉날개: 기본 + `_broken` (broken)
    - 늑대 갑옷: 바닐라의 염색 분기(has_component)는 fallback 에만 유지
  - 방패·삼지창의 바닐라 손 모델은 `minecraft:special`(엔티티 렌더러)이라 텍스처를 바꿀 수 없음
    → 스킨은 일반 모델(직접 만든 3D/2D 모델)로 만들고, 막기(using_item)·던지기 상태 모델도 따로 만들 것
- 아이템 정의 파일을 새로 만들 때는 바닐라 정의를 받아서 fallback 에 넣을 것 (손으로 다시 쓰지 말 것)
- 갑옷이 아닌 장착 아이템도 입은 모습까지 바꿈 (skins.yml 에 equipment-asset 지정, equipment json 의 레이어):
  - 겉날개: `"wings"` 레이어 → `textures/entity/equipment/wings/<세트이름>.png` (64x32)
    (바닐라 elytra 의 `use_player_texture: true` 는 넣지 말 것 — 넣으면 망토 있는 플레이어는 스킨 대신 망토 그림이 보임)
  - 말 갑옷: `"horse_body"` 레이어 → `textures/entity/equipment/horse_body/<세트이름>.png` (64x64)
  - 늑대 갑옷: `"wolf_body"` 레이어 → `textures/entity/equipment/wolf_body/<세트이름>.png` (64x32)
  - UV 배치는 각각 바닐라 `wings/elytra.png`, `horse_body/iron.png`, `wolf_body/armadillo_scute.png` 기준
- 갑옷 스킨은 아이콘(custom-model-data, 기존 방식) + 입은 모습(equipment) 둘 다 바뀜
  - skins.yml 갑옷 스킨에 `equipment-asset: "cosmetics:<세트이름>"` 추가
  - 갑옷 세트 4부위(투구·흉갑·레깅스·부츠)는 같은 equipment-asset 사용
  - 리소스팩에 위 "갑옷 입은 모습" 파일 3개 추가
- 컨셉: 친구들끼리 하는 "힐링" 서버 → 귀엽고 부드러운 파스텔 톤 선호
- 사용자가 **"승인"이라고 하기 전에는 절대 push 하지 말 것**

## 작업 순서 (스킨 요청마다)
1. 요청을 받으면 스킨 id·이름(한국어, &색코드 — 토큰·도감에 그대로 보임)·카테고리·번호 계획을 먼저 짧게 보여줌
2. 텍스처·모델·아이템 정의·skins.yml 수정
3. 검증: 모든 JSON 파싱, 아이콘 PNG 16x16 / 입은 모습 PNG 크기(humanoid·wings·wolf_body 64x32, horse_body 64x64),
   번호 중복 없음, 기존 entries 유지, equipment-asset ↔ equipment json ↔ 텍스처 연결,
   상태 있는 아이템은 fallback 이 바닐라 정의와 동일 + 스킨 모델이 상태별로 다 있는지, servermenu 폴더 변경 없음,
   **새 스킨마다 allowed-materials 전부에 `assets/minecraft/items/<재질>.json` entry(같은 threshold)가 있는지**
   (토큰 대표 재질 포함 — 하나라도 빠지면 토큰이 기본 모양으로 보임), `paper.json` 이 생기지 않았는지
4. 미리보기 이미지 (새 스킨들을 크게 확대해 한 장에) 를 사용자에게 보여주고 승인 요청
   - 갑옷·겉날개·말/늑대 갑옷이면 입은 모습(텍스처 펼친 그림)도 같이 보여줄 것
   - 상태 있는 아이템이면 상태별 모습(활 당기기 단계 등)도 같이 보여줄 것
5. 수정 요청이 오면 반영 후 다시 미리보기
6. "승인" 하면 커밋·push → Actions 완료까지 기다림 → 새 릴리스 확인
   (Actions 결과를 못 읽으면 릴리스 zip 을 받아 직접 sha1 계산)
7. 마지막에 사용자에게 전달:
   - 새 sha1 값 (server.properties 의 `resource-pack-sha1=` 에 넣을 값)
   - 최신 skins.yml 파일 (파일로 전송)
   - 서버에서 할 일: skins.yml → `plugins/CosmeticSkins/` 에 덮어쓰기,
     `resource-pack-sha1` 교체, 서버 재시작
   - 릴리스 태그 이름

## 참고 (세션 환경)
- 이 환경의 `gh` 는 GraphQL 이 막혀 있음 → `gh api repos/Rejecter98/octoserver-resourcepack/...` (REST) 사용
  - 릴리스 목록: `gh api repos/Rejecter98/octoserver-resourcepack/releases --jq '.[].tag_name'`
  - Actions 실행: `gh api repos/Rejecter98/octoserver-resourcepack/actions/runs --jq '.workflow_runs[0]'`
