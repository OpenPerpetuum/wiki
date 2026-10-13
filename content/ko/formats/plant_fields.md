---
title: "식물 필드"
description: "식물 규칙 파일 형식 (GenXY), 각 규칙 필드의 타입, 기본값, 소비 모듈 및 성장 상태 기계(state machine)."
weight: 20
---

# 식물 필드

식물의 동작은 종별로 `$GameRoot/plantrules/` 아래의 **규칙 파일** (일반 텍스트)에 정의됩니다.
어떤 파일이 어느 지역에 속하는지는 DB 매핑 `plantrules(idx, plantrule, rulesetid)` →
`zones.plantruleset`으로 정의되며, 로드 및 병합은 `PlantRuleLoader.cs`가, 필드와 객체 간
매핑은 `PlantRule.cs`가 담당합니다.

## 파일 형식

한 줄에 `key=value` 하나씩 작성되며, `//` 스타일의 주석은 제거됩니다. 값은 **GenXY 토큰
문자**(`GenxyReader.cs` — 첫 문자가 타입과 진법을 결정함)를 사용합니다:

| 토큰 | 파싱 결과 | 예시 |
|---|---|---|
| `n` | int, 10진수 | `n125`, `n-1` |
| `N` | int[], 10진수, 쉼표 구분 | `N5,5,5,5` |
| `f` | double, 10진수 | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **16진수** | `iFF` |
| `L` | long, **16진수** | `L100` |
| `4` | int[], **16진수** | `41,2,3` → [1, 2, 3] |

### ⚠ "원시 배열(bare array)" 함정

파일에는 **명시적 토큰 없이** `blockingHeight=40,3,3,4`와 같은 값도 존재합니다.
파서는 이를 특별하게 처리하지 않습니다: 첫 글자 `4`가 `IntegerArray`(16진수) 토큰으로 소비되고,
나머지는 16진수로 파싱됩니다. 따라서:

```
blockingHeight=40,3,3,4   →  토큰 '4' + 16진수 배열 "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  토큰 'N' + 10진수 배열            →  [0, 8, 11, 14]
```

두 표기법 모두 결과적으로 `int[]`가 되며, 선행된 `0`은 `4`가 "삼켜버린" 값입니다. 배포된
파일의 모든 원시 배열이 `4`로 시작하는 이유가 바로 이 때문입니다 — 첫 요소를 의도한 값으로
유지하기 위한 일종의 관례입니다. **새 규칙 파일을 작성할 때는 반드시 `N` 접두사를 명시적으로
사용하십시오.** 원시 배열에서 10 이상의 값은 16진수로 해석되어 의미가 예기치 않게 변경됩니다.

### 상속

`source=$other_rule.txt` 키는 먼저 `other_rule.txt`를 로드한 뒤 현재 파일의 키를 오버라이드로
적용합니다(`PlantRuleLoader.LoadRuleByName`). 예:
`irontree_t2.txt`의 내용은 다음과 같습니다:

```
source=$irontree_lo.txt
fruitAmount=n125
```

## 필드 참조

모든 필드는 병합된 설정 딕셔너리(`PlantRule.cs`)에서 읽어옵니다. 누락된 키는 표시된 기본값을
사용합니다.

| 키 | 타입 / 기본값 | 소비 위치 | 효과 |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | 해당 종의 `PlantType` 열거형 값 (1=GrassA … 19=Devrinol). 또한 타일별로 저장되는 `PlantInfo.type` 바이트 값입니다. |
| `name` | string | 클라이언트 정보 페이로드 | 표시 이름. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | 주변에 식물 이웃이 **없는** 타일에서 종을 추첨할 때의 가중치. 0 = 자연 스폰되지 않음. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | 타일에 이웃 식물이 **있을** 때의 가중치 승수: 후보 가중치 = `neighbourCount × spreading`. 0 = 번식 추첨에서 당첨되지 않음. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | 같은 종류의 기존 식물 간 최소 거리; 0 또는 음수 = 제한 없음. |
| `growRate` | int (0) | `GrowPlantOnTile` | 상태 기계가 진행되기 전에 `PlantInfo.time` 바이트가 누적해야 하는 큐브 틱 수. 높을수록 느림. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | 파생된 경사 레이어의 허용 경사 범위. 범위를 벗어나면 식물이 제거됩니다. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | 허용 고도 범위, `Altitude / 4`와 비교됨(`/4`는 클라이언트 좌표계에 대응). 지역의 `plantaltitudescale`에 따라 조정됩니다. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | `altitude/4 − waterLevel/4`의 허용 범위 — 해안 식생을 만듭니다. 고도 스케일링도 적용됩니다. |
| `allowedTerrainTypes` | int[] (비어있음) | `ValidateTile` | 허용되는 `groundType` 바이트 목록([지역 파일](/ko/formats/zone-files/) 참고). 비어있으면 아무 곳에도 자라지 않음. `allowedOnNonNatural`이 설정되면 완전히 건너뜁니다. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | 열매를 맺기 시작하는 첫 번째 상태. −1 ⇒ `NotFruiting` (결코 수확할 수 없음). |
| `fruitDefinition` | int (−1) | harvesting | 열매의 아이템 정의 ID. |
| `fruitMaterialName` | string | display | 열매 이름 (예: `$prismocitae`). |
| `fruitAmount` | byte (0), 0–255 제한 | `GrowPlantOnTile` | 식물당 최대 열매량. 결실 상태에 처음 진입하면 5–15%가 채워지며, 이후 성장 틱마다 15–25%가 추가되어 최대 100%까지 채워집니다. |
| `health` | byte[] (상태별) | `GrowPlantOnTile`, combat | 성장 상태별 체력(HP). 상태가 변경될 때 현재 체력 **비율(ratio)**이 새 상태로 유지됩니다. |
| `blockingHeight` | int[] (상태별) | `GrowPlantOnTile`, spawn counting | 상태별 차단 높이; `>0`이면 블록 레이어의 `Plant` 비트가 설정되어(walkable=false) 지역 번식도 목표에 식물이 반영됩니다. |
| `maxAmount` | int (−1) | `SpawnPlants` | 지역당 해당 종의 최대 개체수 제한; −1 = 무제한. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, fertility draw | **모든** 자연 스폰에서 제외됨; 플레이어가 직접 심은 경우에만 존재합니다. |
| `damageScale` | double (1.0) | plant combat | 받는 피해 승수. |
| `onlyOnUnprotectedZone` | bool (0) | spawn validation | 비보호(unprotected) 지역에서만 성장함. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | 컨트롤 비트, 지형 타입 및 경사 검사를 건너뜀("인공" 타일에서도 성장). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (사망 시) | 식물이 죽을 때 해당 타일 아래의 ConcreteA/B 제어 비트를 제거합니다. |
| `state_N` | int[] | `GetNextState` | 상태 `N`에서의 다음 상태 후보들 — 각 요소는 **균등한 확률(uniformly at random)**로 선택됩니다. |
| `action_N` | int[] | `GetNextState` | 상태 `N`에서의 다음 `PlantType` 후보들 (균등 확률). 액션 값이 `0`(NotDefined)이면 **죽음**을 의미합니다. |

일관성은 로드 시점에 검증됩니다(`CheckConsistency`): `len(health) == len(blockingHeight) == 상태 수`.

## 성장 상태 기계

매 32×32 큐브 틱마다 모든 식물 타일에 대해 다음이 수행됩니다(`GrowPlantOnTile`):

1. 만약 `time < growRate`이면: `time++` 후 종료.
2. 그렇지 않으면: `time = 0`, 현재 상태에 대해 `state_N` 및 `action_N`을 추첨:
   - `action == 0` → 식물 사망 (클라이언트에 `type:0, state:1` 제거 신호 전송);
     `placesConcrete`가 설정된 경우 타일 아래 콘크리트 제거.
   - 기타 → `type = action`, `state = next`, `health = healthRatio × Health[newState]`
     (피해 비율 보존).
   - 열매: `newState == fruitingState`이면 `material = fruitAmount × uniform(0.05, 0.15)`;
     `newState > fruitingState`이면 `material += fruitAmount × uniform(0.15, 0.25)`
     (최대 `fruitAmount`로 제한); 그 외의 경우 `material = 0`.
   - 차단 높이 = `blockingHeight[newState]`; 블록 레이어의 `Plant` 비트는 `height > 0`을 따름.

### 실제 사례 — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → 이웃 없는 추첨에서 1/… 가중치
spreading=n2        → 군집 가중치 = 2 × 이웃 수
growRate=n1         → 매 큐브 틱마다 상태 롤링 (매우 빠름)
maxAmount=n190      → 큐브당 최대 190개
health=N5,5,5,5     → 모든 상태에서 체력 5 HP
blockingHeight=40,0,0,0 → [0,0,0,0]으로 파싱됨: 잔디는 결코 이동을 차단하지 않음
fruitingState=n-1   → NotFruiting: 잔디는 결코 수확 불가
state_0=40,0,1      → [0,0,1]: 2/3 확률로 상태 0 유지, 1/3 확률로 다음 상태 진행
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → 최종 상태에서: 3/4 확률로 유지, 1/4 확률로 사망
```

따라서 잔디 타일은: 평균 약 3틱마다 한 단계 진행되며, 마지막 상태에서는 틱당 25%의 확률로
죽고 다시 씨앗을 퍼뜨립니다 — 열매가 없으며 끊임없이 순환하는 지표 식물입니다.

### 실제 사례 — `wall.txt` (12개 상태, `N` 접두사 사용)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (이전 상태로 퇴행 가능), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: 플레이어가 직접 심는 방어 시설로,
비보호 지역에만 존재하고 큐브당 15개로 제한되며, 12개 상태를 거쳐 성장(때로는 퇴행)하여
최대 높이 14와 체력 255 HP에 도달합니다.

## 타일별 상태 저장 위치

타일별 런타임 상태는 지역의 식물 레이어 파일에 있는 7바이트 크기의 `PlantInfo` 구조체
(`type, state, time, spawn, health, material, groundType`)입니다 — [지역 파일](/ko/formats/zone-files/)을
참조하십시오. `spawn` 바이트는 지역 파일에 미리 계산되어 내장된 타일별 스폰 확률입니다 —
`0`은 불모지 타일을 나타내며(검증 시 해당 타일의 식물은 제거되고 절대 싹트지 않음), 그 외의 값은
해당 타일의 식물 재생 시도가 약 `spawn/256`의 확률로 무작위 게이트를 통과함을 의미합니다.
서버는 이 바이트를 결코 수정하지 않습니다. 실제 데이터: `plants.0106.bin`의 모든 타일은
`0x83`(약 51%)을 보유하고 있습니다.

## 클라이언트 페이로드

`PlantRuleExtensions.GetPlantInfoForClient`는 종별로 다음 데이터를 전송합니다: `index`, `mineral`
(= fruitDefinition), `name`, `blocks` (blockingHeight), `health`.

<!-- Developer notes: Materials/Plants/PlantRule.cs (field getters, GetNextState,
     CheckConsistency); PlantRuleLoader.cs (file load, source: override,
     plantAltitudeScale applied to allowedAltitudeLow/High + allowedWaterLevelLow);
     PlantRuleExtensions.cs (fertility + spreading weighted draws);
     NatureCube.cs (ValidateTile checks order: block flags -> spawn byte -> rule
     existence -> control bits -> altitude/4 -> water level -> terrain type ->
     slope; GrowPlantOnTile state machine + fruit math); Common/SettingsLoader.cs
     (line join with '#' then GenxyConverter.Deserialize); GenXY/GenxyReader.cs +
     GenxyToken.cs (token characters; '4' = hex int array, 'N' = decimal int array,
     'n' = int decimal). Rule files live at $GameRoot/plantrules (plantrules table
     maps rulesetid -> file names). -->
