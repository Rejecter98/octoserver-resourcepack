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
  - `models/**`, `server/BetterModel/**`, `tools/**` 변경도 릴리스를 만듦
- `models/` — 레이드 보스 BetterModel 원본 `.bbmodel` (팩 밖, 서버 `plugins/BetterModel/models/` 에도 같은 파일)
- `server/` — 서버에 넣는 설정 원본 (MythicMobs Mobs/Skills, BetterModel config.yml)
- `tools/gen_bettermodel.py` — 릴리스 때 BetterModel 팩을 실제 BetterModel 로 생성해 합침 (아래 "레이드 보스")

## 서버 플러그인 (CosmeticSkins) 연동
- 서버 폴더: `plugins/CosmeticSkins` (버전 없는 이름) — skins.yml 은 `plugins/CosmeticSkins/skins.yml`
- **스킨 토큰 아이콘**: 토큰은 종이(PAPER) 아이템이지만, 서버가 `item_model` 을 그 스킨의 대표 재질로 바꾸고
  같은 custom_model_data 를 붙여서 스킨 모양으로 보여줌
  - 대표 재질 = allowed-materials 중 다이아 > 네더라이트 > 철 > 첫 번째 순
    (예: 검 → DIAMOND_SWORD, 말 갑옷 → DIAMOND_HORSE_ARMOR, 활 → BOW)
  - 그래서 allowed-materials 에 넣은 **모든 재질**의 `assets/minecraft/items/<재질>.json` 에
    그 스킨의 entry 가 반드시 있어야 함 (빠지면 토큰·아이템이 기본 모양으로 보임)
  - 토큰용 `paper.json` 같은 별도 파일은 만들지 말 것
- **rarity (등급)**: skins.yml 의 모든 스킨에 `rarity:` 필수 (값은 `B` / `A` / `S`). 기준:
  - **B** : 기존(바닐라) 모양에 색칠·픽셀만 바꾼 스킨 (실루엣이 원본과 같음)
  - **A** : 외형(모양·실루엣) 자체가 원본에서 바뀐 스킨 (예: 심해 닻 — 곡괭이가 닻 모양)
  - **S** : 크기 변화(모델 display 크기 조정) 또는 `effects`(파티클) 포함
  - **S 한정** : S + 전용 커스텀 사운드 포함. 한정 여부는 가챠 배너 설정에서 지정하므로 skins.yml 의 rarity 는 그대로 `S`
  - 위치: `display-name` 바로 아래 (skins.yml 맨 위 주석에 같은 기준이 적혀 있으니 지우지 말 것)
  - 새 스킨은 위 기준으로 등급을 정하고, **계획 단계 표에 등급도 같이** 보여줄 것
  - 바닐라 그림을 다시 칠하는 방식(지금까지의 대부분)은 B, 직접 새 실루엣을 그리면 A
  - S·한정 S 는 가챠 상위 등급이므로 실루엣도 새로 그리는 것(A 수준 외형)을 기본으로 하고 거기에 효과를 얹을 것
- 현재 등급 (87종):
  - A: deep_sea_anchor_pickaxe(100033), starlight_wand_sword(100060), watering_can_hoe(100061), fish_bread_shovel(100062),
    cat_ear_helmet ~ kaleidoscope_spyglass (100076~100085)
  - S 상시: sakura_fairy_sword(100063), firefly_pickaxe(100064), constellation_sword(100086), sun_phoenix_crossbow(100087)
  - S 한정(시즌 1 심해): deep_sea_whale_bow(100065) — 전용 사운드 `cosmetics:skin.whale.shoot` (거품 보글보글 0.43초)
  - 나머지는 전부 B
- **스킨 이펙트 (CosmeticSkins 1.4.1-octo~)**: skins.yml 스킨마다 선택으로 `effects:` (S 등급의 조건)
  ```yaml
  effects:
    swing:  { particle: CHERRY_LEAVES, count: 15, spread: 0.3, speed: 0.02 }              # 허공에 휘두를 때 (손, 0.25초 쿨타임)
    hit:    { particle: CHERRY_LEAVES, count: 20, spread: 0.3, speed: 0.02, at: target }  # 무기로 때릴 때
    break:  { particle: WAX_ON, count: 20, spread: 0.4, speed: 0.03, at: target }         # 도구로 블록 캘 때
    shoot:  { particle: BUBBLE_POP, count: 20, spread: 0.3, speed: 0.03, sound: "cosmetics:skin.whale.shoot", volume: 0.8, pitch: 1.0 }
    hold:   { particle: FIREFLY, count: 3, spread: 0.3, speed: 0.01, interval: 10 }      # 손에 든 동안 주기적으로 (틱, 20=1초)
  ```
  - 트리거 5종: `swing`(허공 휘두르기, 손에서, 0.25초 쿨타임) · `hit`(무기로 때릴 때) · `break`(도구로 블록 캘 때) ·
    `shoot`(활/석궁 쏠 때) · `hold`(손에 든 동안 주기적으로, `interval` 틱)
  - **위치 `at`**: 기본은 `hand`(손 위치). 맞은 대상/블록 위치가 필요하면 `at: target`, 둘 다면 `at: both`
    (`target`/`both` 는 위치가 있는 hit·break 에서만 의미 있음 — swing·shoot·hold 는 `at` 생략 = 손)
  - **swing 과 hit 겹침 주의**: 때리거나 캘 때도 휘두르기가 같이 일어남 → swing + hit 를 둘 다 넣으면
    손(swing)과 대상(hit)에 동시에 나옴. 둘 다 쓸 땐 hit 를 `at: target` 으로 두어 같은 자리에 겹치지 않게 하고,
    hit 를 `at: hand`/`both` 로 쓸 거면 swing 은 빼기. 곡괭이처럼 계속 캐는 도구는 swing 을 빼는 게 깔끔함
  - **값 형식 (서버 확인 완료)**: `particle` 은 Bukkit 대문자 이름(`CHERRY_LEAVES`) — `minecraft:` 형식은 서버가 인식 못 함.
    `sound` 는 바닐라 `minecraft:block.amethyst_block.chime`, 커스텀 `cosmetics:skin.whale.shoot` 형식
  - 각 항목 키: `particle`, `count`, `spread`, `speed`, `color`("#RRGGBB", DUST 계열만), `size`,
    `sound`, `volume`, `pitch`, `interval`(hold 전용), `at`(hand/target/both)
  - **블록/아이템 데이터가 필요한 파티클은 금지** (서버가 무시): BLOCK, BLOCK_MARKER, BLOCK_CRUMBLE, FALLING_DUST,
    DUST_PILLAR, ITEM, 그리고 색 2개가 필요한 DUST_COLOR_TRANSITION, 색이 필수인 ENTITY_EFFECT 도 쓰지 않음
  - 무난한 파티클: DUST(색 지정), CHERRY_LEAVES, END_ROD, HEART, NOTE, HAPPY_VILLAGER, WAX_ON, GLOW, SNOWFLAKE,
    BUBBLE_POP, NAUTILUS, FIREFLY, CLOUD (26.2 바닐라 particles 목록에 있는 것만)
  - **양 기준 (인게임 테스트 결과 — 적으면 거의 안 보임)**: 서버 config 의 전체 배율 `effects-scale` 이 있으므로,
    스킨별 값은 **배율 1.0 기준으로 잘 보이는 양**으로 맞출 것
    - hit / break / swing / shoot: count 15~30, spread 0.2~0.4
    - hold: count 3~5, interval 5~10 (손에 들고 있으면 확실히 보이게)
    - speed: 0.01~0.05 (크면 순식간에 흩어져서 안 보임)
  - 바닐라 소리는 `minecraft:block.amethyst_block.chime` 처럼 사운드 이벤트 이름으로 (26.2 sounds.json 에 있는 것만)
  - 크기 변화(S): 스킨 모델의 `display` 에서 손에 든 모습 scale 을 키움 (1.1~1.3 정도, 인벤토리 gui 는 그대로)
- **커스텀 사운드 (한정 S 전용)**:
  - `pack/assets/cosmetics/sounds.json` 에 이벤트 추가 — 이미 있으면 **덮어쓰지 말고 항목만 추가**
    → `{"skin.anchor.hit": {"sounds": [{"name": "cosmetics:skin/anchor_hit"}]}}`
  - 파일: `pack/assets/cosmetics/sounds/skin/<이름>.ogg` — **Ogg Vorbis, 모노** (스테레오면 위치에 따라 안 들림)
  - skins.yml 에서는 `sound: "cosmetics:skin.anchor.hit"` (이벤트 이름)
  - 소리는 직접 합성해서 만듦 (ffmpeg libvorbis 사용 가능), 짧고(1초 안팎) 부드럽게, 볼륨 과하지 않게
- **display-name** 은 토큰 이름과 스킨 도감 이름으로 그대로 쓰임
  → 한국어 + `&` 색코드로 예쁘게 (테마 색 하나로 통일, 예: 솜사탕 `&d`, 서리 `&b`, 불꽃 `&c`, 벚꽃 `&d`)
  - 이미 쓰이는 이름과 겹치지 않게, 너무 길지 않게 (도감 한 줄에 들어가도록)

## 도감 미등록 실루엣 (assets/dogam — 자동 생성, 레포에 커밋하지 않음)
- 서버 도감 플러그인이 요청하는 모델:
  - 아이템: `assets/dogam/items/silhouette/<아이템id>.json` → 26.2 의 **모든 아이템**(1,537개) 빠짐없이
    (없으면 보라·검정 체크무늬)
  - 스킨: `assets/dogam/items/silhouette/skin/<스킨id>.json` → skins.yml 의 **모든 스킨**
  - 입체 모델용: `assets/dogam/models/silhouette/[skin/]<id>.json`
- 실루엣 = 원래 모양 그대로 + 색만 검정 (`minecraft:constant` 틴트, 기본 `0x000000`;
  너무 새까매서 안 보이면 `--color 0x202020`)
- 생성기: `tools/gen_silhouettes.py`
  - Mojang 버전 매니페스트에서 클라이언트 jar 를 받아 items/*.json · models/** 만 읽음 (jar·텍스처는 레포에 넣지 않음)
  - 대표 모델: condition → on_false, select → (display_context 면 gui 케이스) fallback/첫 케이스,
    range_dispatch → fallback/첫 entry, composite → 첫 모델(special 이 섞이면 회색)
  - 평면(builtin/generated 계열): 원래 모델 그대로 참조 + 레이어 수만큼 검정 tints
  - 입체(elements): parent 체인의 elements 를 복사한 모델(parent = 원래 모델, 모든 face `tintindex: 0`) + 검정 tint
  - `minecraft:special`(상자·현수막·머리·셜커 상자·방패·구리 골렘 석상 등) · 빈 모델(air) → `minecraft:item/gray_stained_glass_pane`
    (현재 63개, 그래도 파일은 반드시 생성)
  - 스킨: skins.yml 각 스킨의 첫 allowed-material 아이템 정의에서 그 스킨 entry 를 같은 규칙으로 따라감
  - 출력 폴더는 매번 지우고 새로 만듦 / 확인용 `assets/dogam/report.json` (zip 에서는 제외)
- **release.yml 이 zip 만들기 전에 자동 실행** → 새 스킨을 skins.yml 에 넣으면 실루엣도 자동으로 생김
  (생성 실패·아이템 수 불일치면 릴리스가 멈춤)
  - 마크 버전 업데이트: Actions 의 workflow_dispatch 에서 `mc_version` 입력 (또는 스크립트 `DEFAULT_VERSION` 수정)
- 이 세션 환경은 Mojang 서버 접속이 막혀 있음 → 로컬 확인은 미러 에셋으로:
  `python3 tools/gen_silhouettes.py --assets-dir <InventivetalentDev/minecraft-assets 26.2 체크아웃>`
- `pack/assets/dogam/` 은 `.gitignore` 에 있음 (생성물이라 커밋하지 않음)

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
1. 요청을 받으면 스킨 id·이름(한국어, &색코드 — 토큰·도감에 그대로 보임)·카테고리·번호·**등급(rarity)** 계획을 먼저 짧게 보여줌
2. 텍스처·모델·아이템 정의·skins.yml 수정
3. 검증: 모든 JSON 파싱, 아이콘 PNG 16x16 / 입은 모습 PNG 크기(humanoid·wings·wolf_body 64x32, horse_body 64x64),
   번호 중복 없음, 기존 entries 유지, equipment-asset ↔ equipment json ↔ 텍스처 연결,
   상태 있는 아이템은 fallback 이 바닐라 정의와 동일 + 스킨 모델이 상태별로 다 있는지, servermenu 폴더 변경 없음,
   **새 스킨마다 allowed-materials 전부에 `assets/minecraft/items/<재질>.json` entry(같은 threshold)가 있는지**
   (토큰 대표 재질 포함 — 하나라도 빠지면 토큰이 기본 모양으로 보임), `paper.json` 이 생기지 않았는지,
   모든 스킨에 `rarity` 가 있고 값이 B/A/S 중 하나인지,
   effects 가 있으면: 트리거·키가 위 목록 안에 있는지, 금지 파티클이 아닌지, color 는 DUST 계열에만, interval 은 hold 에만,
   `at` 은 hand/target/both 이고 target/both 는 hit·break 에만, 양이 기준 안인지(hit/break/swing/shoot count 15~30 ·
   spread 0.2~0.4, hold count 3~5 · interval 5~10, speed 0.01~0.05), swing 과 hit 가 같은 자리(hand)에 겹치지 않는지,
   `effects` 나 크기 변화가 있으면 rarity S 인지,
   `cosmetics:` 사운드는 sounds.json 에 이벤트가 있고 ogg 파일이 있으며 Vorbis·모노(채널 1)인지(ffprobe),
   바닐라 사운드는 26.2 sounds.json 에 있는 이벤트인지,
   `tools/gen_silhouettes.py --assets-dir ...` 를 돌려서 새 스킨 실루엣(`silhouette/skin/<id>.json`)이 생기고
   아이템 수가 26.2 와 같은지 (스킨이 회색 대체로 빠지면 원인 확인)
4. 미리보기 이미지 (새 스킨들을 크게 확대해 한 장에) 를 사용자에게 보여주고 승인 요청
   - 갑옷·겉날개·말/늑대 갑옷이면 입은 모습(텍스처 펼친 그림)도 같이 보여줄 것
   - 상태 있는 아이템이면 상태별 모습(활 당기기 단계 등)도 같이 보여줄 것
   - S 면 이펙트(어떤 파티클·색·언제)를 그림/표로, 커스텀 사운드는 ogg 파일도 같이 보내서 들어볼 수 있게
5. 수정 요청이 오면 반영 후 다시 미리보기
6. "승인" 하면 커밋·push → Actions 완료까지 기다림 → 새 릴리스 확인
   (Actions 결과를 못 읽으면 릴리스 zip 을 받아 직접 sha1 계산)
7. 마지막에 사용자에게 전달:
   - 새 sha1 값 (server.properties 의 `resource-pack-sha1=` 에 넣을 값)
   - 최신 skins.yml 파일 (파일로 전송)
   - 서버에서 할 일: skins.yml → `plugins/CosmeticSkins/` 에 덮어쓰기,
     `resource-pack-sha1` 교체, 서버 재시작
   - 릴리스 태그 이름

## 레이드 보스 (OctoRaid + MythicMobs 5.13 무료 + BetterModel)
- 보스 하나당 결과물: 컨셉 · 밸런스 계산 · `server/MythicMobs/Mobs|Skills/<이름>.yml` · `models/<이름>.bbmodel`
  · raids.yml boss 부분 · (필요 시) spigot.yml 값 · 릴리스 sha1 · 적용 체크리스트 · 플러그인 쪽 요청사항(따로)
- 진행: 테마/설계안 → 미리보기(모델 렌더 + 모션 GIF) → 사용자 "승인" → 제작·릴리스 → 전달
- OctoRaid 가 하는 일(보스에서 하지 말 것): 파티·아레나·제한 시간·사망/부활·보상·인원 체력 배율(1+0.6×(n-1))·
  크기(SCALE 속성)·60블록 리쉬·종료 시 몹 정리. 보스는 `PreventOtherDrops: true`, `Despawn: false`, 보상 없음
- 이름: 영문 소문자 + `octo_` (스킬 `octo_<약어>_<패턴>`), 대사 한국어 + `&` 색코드
- 큰 공격은 반드시 예고(채팅·사운드·파티클·멈춤) → 모션의 예고 자세 시간과 스킬 `delay` 를 맞출 것
- 체력 2048 초과(인원 배율 2.8배 포함)면 spigot.yml `settings.attribute.maxHealth.max` 값을 안내
- 몹이 든 무기 공격력이 Damage 에 더해짐 (나무 도끼 +6, 철 도끼 +8 …) → 실제 피해 = Damage + 무기
- MythicMobs 줄에 `: `(콜론+공백)이 들어가면 YAML 이 깨짐 → 그 줄 전체를 작은따옴표로 감쌀 것
- MythicMobs 문법은 wiki.mythiccraft.io 에서 확인 (추측 금지). 프리미엄 기능 금지
- 모델이 없어도 레이드가 돌아가야 함: 바닐라 외형(몹 종류·장비·크기·가벼운 오라) + `bm:` 줄은 실패해도 무시됨

### BetterModel 연동 (버전 고정: BetterModel 3.5.0, Paper 26.2 build 129 — `tools/gen_bettermodel.py` 상단)
- MythicMobs 문법 (BetterModel 3.5.0 소스 `compatibility/mythicmobs` 에서 확인):
  - 모델 입히기: `bm:model{mid=<모델>;da=true} @self ~onSpawn` (scale 생략 = 몹 SCALE 속성을 그대로 따라감)
  - 패턴 모션: `bm:state{mid=<모델>;s=<애니메이션>} @self` (li/lo = 블렌드 틱, sp = 속도, r=true = 정지)
  - 애니메이션 이름 `idle`·`walk`·`spawn`·`damage`·`death` 는 BetterModel 이 자동 재생 → 나머지만 bm:state
- .bbmodel 규칙: Blockbench free 포맷, 앞 = 북쪽(-Z), 큐브 회전 없이 뼈(그룹) 회전만 사용, 큐브 30~40개,
  텍스처는 파일 안에 base64 로 포함, 뼈 이름 태그 `h_`(머리=시선 따라감) `glow_`(발광)
  - 생성기: `tools/models/<모델>.py` (큐브·텍스처·애니메이션을 코드로 작성 → `models/<모델>.bbmodel`)
  - 미리보기: `tools/models/render.py` (소프트웨어 렌더러. Blockbench 규칙: 그룹 Euler ZYX, 애니메이션 회전 x·y 부호 반전)
- **팩 합치기 (사용자 서버 작업 없이)**: 릴리스 워크플로가 `tools/gen_bettermodel.py` 실행 →
  Paper + BetterModel 을 잠깐 켜서 `models/*.bbmodel` 로 팩 생성(`pack-type: folder`) →
  `assets/bettermodel/**` 만 `pack/assets/bettermodel/` 로 **통째 교체** (그 밖의 경로가 생기면 실패로 멈춤 = 겹침 보고)
  - `pack/assets/bettermodel/` 은 생성물이라 `.gitignore` (커밋하지 않음), pack.mcmeta(88)는 우리 것 유지
  - 서버 BetterModel 설정 = `server/BetterModel/config.yml` (`pack-type: none`, `pack.use-obfuscation: false`,
    `module.player-animation: false`) — CI 는 같은 파일에서 pack-type 만 folder 로 바꿔 씀 → 이름·내용 일치
  - 서버와 CI 의 BetterModel 버전·config·.bbmodel 이 같아야 함. BetterModel 버전을 올릴 땐 스크립트 상수와
    사용자 서버 jar 를 같이 바꾸도록 안내
- 모델이 바뀔 때 사용자 서버 작업: `.bbmodel` 를 `plugins/BetterModel/models/` 에 넣기 → `/bettermodel reload`
  → `resource-pack-sha1` 교체 (BetterModel 첫 실행 전에 models 폴더를 만들어 두면 예제 모델이 안 생김)

## 참고 (세션 환경)
- 이 환경의 `gh` 는 GraphQL 이 막혀 있음 → `gh api repos/Rejecter98/octoserver-resourcepack/...` (REST) 사용
  - 릴리스 목록: `gh api repos/Rejecter98/octoserver-resourcepack/releases --jq '.[].tag_name'`
  - Actions 실행: `gh api repos/Rejecter98/octoserver-resourcepack/actions/runs --jq '.workflow_runs[0]'`
