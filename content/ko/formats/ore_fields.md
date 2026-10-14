---
title: "광석 필드"
description: "minerals 및 mineralconfigs 테이블, 노드 생성 공식, 노드 수명 주기 및 채굴 메커니즘."
weight: 30
---

# 광석 필드

광석 데이터는 두 가지 레벨로 구성됩니다: **종류별** (`minerals` — 어떤 물질이며 1회 채굴 시
산출량이 얼마인지) 및 **지역별·종류별** (`mineralconfigs` — 노드 수, 크기, 매장량).
런타임 노드 상태는 `mineralnodes` 테이블에 저장됩니다.

## `minerals`

| 컬럼 | 타입 | 사용 위치 | 의미 |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | `MaterialType` 열거형 서수 (1=Titan … 19=DHDT, 0=Undefined). 모든 조인은 `mineralconfigs.materialtype = minerals.idx`를 사용합니다. |
| `name` | varchar | `ToMaterialType()` | 종류 이름 ("titan", "crude", …). |
| `definition` | int | `MaterialHelper` → item | 채굴로 생성되는 아이템 정의 (예: titan → def 168). |
| `amount` | int | `DrillerModule` | **1회 채굴당 기본 단위** (titan 1500, crude 1500, stermonit 975, liquizit 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = 고체 (`OreLayer`), 1 = 액체 (`LiquidLayer`). |
| `enablereffectrequired` | bit | module gating | 채굴에 활성화 효과(enabler effect)가 필요한지 여부. |
| `geoscandocument` | int | scan items | 해당 물질에 대한 지질 스캔 문서 아이템. |

## `mineralconfigs`

(지역, 광물) 쌍당 한 행. `MineralConfigurationReader`에 의해 처리되어 행당 하나의
`MineralLayer`가 생성됩니다:

| 컬럼 | 타입 | 사용 위치 | 의미 |
|---|---|---|---|
| `zoneId` | int | layer construction | 소속 지역 ID. |
| `materialtype` | int | → `minerals.idx` | 광물 종류. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | 해당 지역에서 유지되는 이 종류의 노드 수. |
| `maxtilespernode` | int | generator | 노드 덩어리(blob)당 최대 타일 수; 간격 반경(아래 참고)도 결정합니다. |
| `totalamountpernode` | int | generator | 신규 생성 노드의 총 매장량(덩어리 내 타일들에 분배됨). |
| `minthreshold` | double | generator | 타일당 최소 정규화 매장 비율 (0–1); 미만인 타일은 제거됩니다. |

### 노드 생성 공식 (`MineralNodeGeneratorBase.cs`)

위 구성을 가진 종류의 새 노드 생성 공식:

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = 시작 위치는 가장 가까운 기존 노드로부터 ≥ 2 × radius 이상 떨어져야 함
blob    = 최대 maxtilespernode 개의 유효 타일까지 랜덤 워크 플러드 필(4-타일 브러시)
tile[i] = ( noise[i] / max(noise) )를 [minthreshold, 1] 범위로 정규화
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // 지터 적용 후 uint로 절사
```

도킹 기지 및 텔레포트 주변의 진입 금지 구역(`KeepOutDist`): 에프리톤(epriton) = 100 타일
(`MINERAL_DISTANCE_FROM_BASE_MIN`), 플럭스 광석(flux ore) = 200; 기타 모든 종류 = 0.

### 실제 사례 — 다오덴(Daoden, zone_ASI) 원유(crude, id 2)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → 간격 ≥ 80 타일
blob    = 최대 1257 타일
tile    = 지분 ∈ [0.5, 1.0] × (125,000,000 / Σnormalized) × jitter
```

가득 찬 원유 노드는 1억 2,500만 유닛을 보유합니다. 드릴 주기당 기본 1,500 유닛 채굴 시
노드당 약 83,000회의 채굴 주기 분량이며, 해당 지역의 8개 노드 전체로는 약 666,000회에 달합니다.

## 노드 상태 — `mineralnodes`

| 컬럼 | 의미 |
|---|---|
| `zoneid`, `materialtype` | 소속 지역 + 광물 종류 |
| `x, y, width, height` | 노드 바운딩 박스 (덩어리 영역) |
| `data` | 타일당 압축된 `uint` (박스 내 행 우선(row-major) 순서) |

수명 주기 (`MineralNode.cs`, `MineralLayer.cs`):

- **로드**: 지역 시작 시 저장된 모든 노드를 로드합니다. 총합이 `totalamountpernode`의
  **1%** 이하인 노드는 로드하지 않고 삭제됩니다.
- **보충**: 살아남은 노드 수가 `maxnodes`보다 적으면 새 노드가 생성됩니다(위 공식 참고).
- **만료**: **채굴되지 않은(untouched)** 노드는 **7일** 후 만료됩니다(`TimeTracker`). 채굴 시
  타이머가 재설정됩니다. 최대 타일 값이 0이 된 노드도 만료됩니다.
- **영속화**: 변경된(dirty) 노드는 **30분** 저장 타이머 주기로 DB에 기록됩니다.
- **플럭스 광석 연동**: `FluxOre` 노드가 감소하거나 만료되면 `OreNpcSpawnMessage`를
  발행하여 NPC 스포너(`OreNPCSpawner`)가 이를 수신합니다.

## 채굴 메커니즘 (`MineralExtractor.cs`, `DrillerModule.cs`)

채굴량은 `minerals.amount`에 로봇의 `mining_amount_modifier` 속성(`mining_amount_modifier`,
`effect_mining_amount_modifier`, `drone_amplification_mining_amount_modifier`,
`effect_excavator_mining_amount_modifier` 합산)이 적용되어 계산됩니다.

- **고체** (`OreLayer`): 로봇이 위치한 **단일 타일**에서 `min(tile value, amount)`만큼 채굴합니다.
- **액체** (`LiquidLayer`): 채굴 요구량이 충족될 때까지 가장 가까운 타일부터(거리 제곱 기준 우선순위 큐)
  **노드 전체**에서 추출합니다.
- **자갈** (훈련 구역 전용, `GravelLayer`): 타일 값을 읽지만 값을 감소시키지 않습니다 — 자갈 노드는
  무한합니다.

종류별 산출량(정제된 생산품)은 [광석](/content/ores/)에서 확인할 수 있으며, 지역별 노드 수는
[지역 색인](/zones/zone-index/)에 정리되어 있습니다.

<!-- Developer notes: Zones/Terrains/Materials/Minerals/MineralConfiguration.cs
     (reader + config), MineralLayer.cs (LoadMineralNodes 1% delete + top-up,
     GenerateNewNode radius/tile/amount wiring, FluxOre events),
     Generators/MineralNodeGeneratorBase.cs (FindStartPosition, NormalizeNoise,
     CreateMineralNode, KeepOutDist), Generators/RandomWalkMineralNodeGenerator.cs
     (flood fill, 50k step cap), MineralNode.cs (uint[] values, 7-day expiry,
     30-min save), MineralNodeRepository.cs (mineralnodes table, compressed
     values), Minerals/MineralExtractor.cs (solid/liquid/gravel extraction),
     Modules/DrillerModule.cs (amount property + modifiers), Materials/MaterialHelper.cs
     (minerals.definition -> item), Zones/DistanceConstants.cs
     (MINERAL_DISTANCE_FROM_BASE_MIN = 100). -->
