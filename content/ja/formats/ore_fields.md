---
title: "鉱石フィールド"
description: "mineralsおよびmineralconfigsテーブル、ノード生成式、ノードのライフサイクル、採掘メカニクス。"
weight: 30
---

# 鉱石フィールド

鉱石データには2つの階層があります：**種類別**（`minerals` — どのような物質であり、
1回の採掘でどれだけ得られるか）および**ゾーン・種類別**（`mineralconfigs` — ノード数、
サイズ、埋蔵量）。実行時のノード状態は`mineralnodes`テーブルに保持されます。

## `minerals`

| カラム | 型 | 使用箇所 | 意味 |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | `MaterialType` enumの序数（1=Titan … 19=DHDT、0=Undefined）。すべての結合は`mineralconfigs.materialtype = minerals.idx`を使用します。 |
| `name` | varchar | `ToMaterialType()` | 種類名（"titan"、"crude"など）。 |
| `definition` | int | `MaterialHelper` → item | 採掘によって生成されるアイテム定義（例：titan → def 168）。 |
| `amount` | int | `DrillerModule` | **1回の採掘あたりの基本単位**（titan 1500、crude 1500、stermonit 975、liquizit 450、epriton 450など）。 |
| `extractionType` | int | `TerrainsModule` | 0 = 固体（`OreLayer`）、1 = 液体（`LiquidLayer`）。 |
| `enablereffectrequired` | bit | module gating | 採掘にイネーブラー効果（enabler effect）が必要かどうか。 |
| `geoscandocument` | int | scan items | この鉱物用の地質スキャンドキュメントアイテム。 |

## `mineralconfigs`

（ゾーン、鉱物）のペアごとに1行。`MineralConfigurationReader`によって読み取られ、
1行につき1つの`MineralLayer`が生成されます：

| カラム | 型 | 使用箇所 | 意味 |
|---|---|---|---|
| `zoneId` | int | layer construction | 所属ゾーン。 |
| `materialtype` | int | → `minerals.idx` | 鉱物の種類。 |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | ゾーン内で維持されるこの種類のノード数。 |
| `maxtilespernode` | int | generator | ノードの塊（ブロブ）あたりの最大タイル数。配置間隔の半径（下記参照）も決定します。 |
| `totalamountpernode` | int | generator | 新規ノードの総埋蔵量（ブロブの各タイルに分散）。 |
| `minthreshold` | double | generator | タイルごとの最小正規化充填率（0–1）。この値を下回るタイルは破棄されます。 |

### ノード生成式（`MineralNodeGeneratorBase.cs`）

上記の設定を持つ種類の新規ノード生成手順：

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = 開始位置は最も近い既存ノードから ≥ 2 × radius 離れている必要がある
blob    = 最大 maxtilespernode 個の有効タイルまでのランダムウォーク・フラッドフィル（4タイルブラシ）
tile[i] = ( noise[i] / max(noise) ) を [minthreshold, 1] の範囲に正規化
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // ジッター適用後、uintに切り捨て
```

ドッキング基地およびテレポート周辺の進入禁止ゾーン（`KeepOutDist`）：epriton = 100タイル
（`MINERAL_DISTANCE_FROM_BASE_MIN`）、flux ore = 200、その他すべての種類 = 0。

### 具体例 — Daoden（zone_ASI）の原油（crude、id 2）

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → 間隔 ≥ 80タイル
blob    = 最大1257タイル
tile    = 割合 ∈ [0.5, 1.0] × (125,000,000 / Σnormalized) × ジッター
```

満杯の原油ノードには1億2,500万ユニットが保持されます。ドリル1サイクルあたり基本1,500ユニットの
採掘レートでは、1ノードあたり約83,000サイクルの採掘量となり、ゾーン内の8ノード全体では
約666,000サイクル分に相当します。

## ノードの状態 — `mineralnodes`

| カラム | 意味 |
|---|---|
| `zoneid`, `materialtype` | 所属ゾーン ＋ 鉱物の種類 |
| `x, y, width, height` | ノードのバウンディングボックス（ブロブの領域） |
| `data` | タイルごとの圧縮された`uint`（ボックス内の行優先順） |

ライフサイクル（`MineralNode.cs`、`MineralLayer.cs`）：

- **ロード**：ゾーン起動時、保存されているすべてのノードがロードされます。合計が
  `totalamountpernode`の**1%**以下のノードはロードされず削除されます。
- **補充**：残ったノード数が`maxnodes`未満の場合、新しいノードが生成されます（上記の計算式）。
- **期限切れ**：**未採掘（untouched）**のノードは**7日**で期限切れとなります（`TimeTracker`）。採掘すると
  タイマーがリセットされます。最大タイル値が0になったノードも期限切れとなります。
- **永続化**：変更されたノードは**30分**の保存タイマー周期でDBに書き込まれます。
- **Flux oreとの連携**：`FluxOre`ノードの減少または期限切れにより`OreNpcSpawnMessage`が
  発行され、NPCスポナー（`OreNPCSpawner`）がこれを受信します。

## 採掘メカニクス（`MineralExtractor.cs`、`DrillerModule.cs`）

採掘量は、ロボットの`mining_amount_modifier`プロパティ（`mining_amount_modifier`、
`effect_mining_amount_modifier`、`drone_amplification_mining_amount_modifier`、
`effect_excavator_mining_amount_modifier`の合算値）によってスケールされた`minerals.amount`となります。

- **固体**（`OreLayer`）：ロボットが立っている**単一のタイル**から`min(tile value, amount)`を採掘します。
- **液体**（`LiquidLayer`）：採掘要求量が満たされるまで、最も近いタイルから順に（距離の2乗に基づく優先度キュー）
  **ノード全体**から抽出します。
- **砂利**（訓練ゾーンのみ、`GravelLayer`）：タイルの値を読み取りますが減算はしません — 砂利ノードは無尽蔵です。

種類ごとの産出量（精製された生産物）は[鉱石](/content/ores/)に、ゾーンごとのノード数は
[ゾーン一覧](/zones/zone-index/)に記載されています。

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
