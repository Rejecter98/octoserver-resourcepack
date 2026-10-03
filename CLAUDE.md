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

## 리소스팩 구조
- `pack.mcmeta`: min_format/max_format 88 (26.2 리소스팩 포맷)
- 텍스처: `pack/assets/cosmetics/textures/item/<스킨id>.png` (16x16 픽셀아트)
- 모델: `pack/assets/cosmetics/models/item/<스킨id>.json`
  → `{"parent": "minecraft:item/handheld", "textures": {"layer0": "cosmetics:item/<스킨id>"}}`
- 아이템 정의: `pack/assets/minecraft/items/<재질>_<도구>.json`
  → `minecraft:range_dispatch` / property `minecraft:custom_model_data` / index 0,
    fallback 은 바닐라 모델, entries 에 threshold 별 모델 (`cosmetics:item/<스킨id>`)
- 기존 스킨 12종: flame/frost/sakura × blade/pickaxe/axe/shovel = custom-model-data 100001~100012
- `pack/assets/servermenu/` (메뉴 GUI 배경·폰트) 는 다른 플러그인용 → **절대 수정 금지**
- 참고: 현재 팩/skins.yml 에는 구리(copper) 도구가 없음 (나무·돌·철·금·다이아·네더라이트만)

## 규칙
- 새 custom-model-data 는 skins.yml 에서 가장 큰 값 +1 부터, 절대 중복 금지
- `assets/minecraft/items/*.json` 은 덮어쓰지 말고 entries 에 추가, threshold 오름차순 유지
- 스킨 하나는 같은 종류 도구 전 재질(나무·돌·구리(있으면)·철·금·다이아·네더라이트)에 적용,
  skins.yml allowed-materials 도 동일
- skins.yml category 는 sword, pickaxe, axe, shovel, helmet, chestplate, leggings, boots 중 하나
- 갑옷 스킨은 손에 든 모습/아이콘만 바뀌고 입은 모습은 안 바뀜 → 제안할 때 미리 알려줄 것
- 컨셉: 친구들끼리 하는 "힐링" 서버 → 귀엽고 부드러운 파스텔 톤 선호
- 사용자가 **"승인"이라고 하기 전에는 절대 push 하지 말 것**

## 작업 순서 (스킨 요청마다)
1. 요청을 받으면 스킨 id·이름(한국어, &색코드)·카테고리·번호 계획을 먼저 짧게 보여줌
2. 텍스처·모델·아이템 정의·skins.yml 수정
3. 검증: 모든 JSON 파싱, PNG 16x16, 번호 중복 없음, 기존 entries 유지,
   servermenu 폴더 변경 없음
4. 미리보기 이미지 (새 스킨들을 크게 확대해 한 장에) 를 사용자에게 보여주고 승인 요청
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
