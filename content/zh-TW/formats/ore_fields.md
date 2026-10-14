---
title: "礦石欄位"
description: "minerals 與 mineralconfigs 資料表、節點生成公式、節點生命週期以及採集機制。"
weight: 30
---

# 礦石欄位

礦石資料分為兩個層級：**按類型**（`minerals` —— 材料是什麼以及單次採集產出多少）和**按區域按類型**（`mineralconfigs` —— 有多少節點、多大、填充量如何）。執行時節點狀態保存在 `mineralnodes` 資料表中。

## `minerals`

| 欄位 | 型別 | 使用者 | 意義 |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | `MaterialType` 列舉序號（1=Titan … 19=DHDT，0=Undefined）。所有關聯查詢均使用 `mineralconfigs.materialtype = minerals.idx`。 |
| `name` | varchar | `ToMaterialType()` | 類型名稱（"titan"、"crude" 等）。 |
| `definition` | int | `MaterialHelper` → item | 採集產出的物品定義（例如 titan → def 168）。 |
| `amount` | int | `DrillerModule` | **每次採集的基本單位數**（titan 1500、crude 1500、stermonit 975、liquizit 450、epriton 450 等）。 |
| `extractionType` | int | `TerrainsModule` | 0 = 固體（`OreLayer`），1 = 液體（`LiquidLayer`）。 |
| `enablereffectrequired` | bit | 模組限制 | 採集是否需要啟用效果（enabler）。 |
| `geoscandocument` | int | 掃描物品 | 該材料的地質掃描文件物品。 |

## `mineralconfigs`

每個（區域，材料）一筆記錄。由 `MineralConfigurationReader` 讀取 → 每行對應一個 `MineralLayer`：

| 欄位 | 型別 | 使用者 | 意義 |
|---|---|---|---|
| `zoneId` | int | 圖層建構 | 所屬區域。 |
| `materialtype` | int | → `minerals.idx` | 材料類型。 |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | 該區域維持的該類型節點數量。 |
| `maxtilespernode` | int | 生成器 | 每個節點斑塊的最大圖塊數；同時也決定間距半徑（見下文）。 |
| `totalamountpernode` | int | 生成器 | 新生節點中的材料總量，分佈在該斑塊的各圖塊上。 |
| `minthreshold` | double | 生成器 | 最小正規化單圖塊填充量（0–1）；低於該值的圖塊會被捨棄。 |

### 節點生成公式（`MineralNodeGeneratorBase.cs`）

對於具有上述配置的新節點：

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = 起始位置必須與最近的現有節點相距 ≥ 2 × radius
blob    = 隨機漫步洪水填充（4 圖塊筆刷），最多填充 maxtilespernode 個有效圖塊
tile[i] = ( noise[i] / max(noise) ) 正規化到 [minthreshold, 1]
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // 抖動擾動，隨後截斷為 uint
```

停靠基地與傳送點周圍的禁區距離（`KeepOutDist`）：epriton = 100 圖塊（`MINERAL_DISTANCE_FROM_BASE_MIN`），flux ore = 200；所有其他類型 = 0。

### 實例計算 — Daoden (zone_ASI) 原油 crude（id 2）

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → 間距 ≥ 80 圖塊
blob    = 最多 1257 個圖塊
tile    = 份額 ∈ [0.5, 1.0] × (125,000,000 / Σnormalized) × 抖動擾動
```

一個完整的原油節點包含 1.25 億單位材料；按每個採礦週期 1,500 單位的基礎採集量計算，每個節點約可進行 83,000 次採集，全區 8 個節點總計約 666,000 次。

## 節點狀態 — `mineralnodes`

| 欄位 | 意義 |
|---|---|
| `zoneid`, `materialtype` | 所屬區域 + 類型 |
| `x, y, width, height` | 節點邊界包圍盒（斑塊區域） |
| `data` | 每個圖塊壓縮的 `uint` 資料（包圍盒內按行優先排列） |

生命週期（`MineralNode.cs`、`MineralLayer.cs`）：

- **載入**：區域啟動時載入所有儲存的節點；總量 ≤ `totalamountpernode` 的 **1%** 的節點將被直接刪除。
- **補充**：如果存活的節點數少於 `maxnodes`，則生成新節點（見上方公式）。
- **過期**：**未被觸碰**的節點在 **7 天**後過期（`TimeTracker`）；採礦會重設該計時器。最大圖塊值歸 0 的節點也會過期。
- **持久化**：髒節點在 **30 分鐘**儲存定時器觸發時寫入資料庫。
- **通量礦聯動**：`FluxOre` 節點的減少/過期會發布 `OreNpcSpawnMessage` → NPC 生成器監聽該訊息（`OreNPCSpawner`）。

## 採集機制（`MineralExtractor.cs`、`DrillerModule.cs`）

實際採集量為 `minerals.amount` 乘以機器人的 `mining_amount_modifier` 屬性（由 `mining_amount_modifier`、`effect_mining_amount_modifier`、`drone_amplification_mining_amount_modifier`、`effect_excavator_mining_amount_modifier` 聚合而成）。

- **固體**（`OreLayer`）：從機器人所站立的**單一圖塊**中提取 `min(圖塊值, 採集量)`。
- **液體**（`LiquidLayer`）：抽取**整個節點**，優先抽取距離最近的圖塊（按距離平方優先佇列），直到滿足採集量。
- **砂石 Gravel**（僅限新手訓練區域，`GravelLayer`）：讀取圖塊值但不扣減——砂石節點是取之不盡的。

各類型的產出（精煉產物）參見[礦石](/content/ores/)；各區域的節點數量參見[區域索引](/zones/zone-index/)。

<!-- 開發者說明：Zones/Terrains/Materials/Minerals/MineralConfiguration.cs
     （讀取器 + 配置）、MineralLayer.cs（LoadMineralNodes 1% 刪除 + 補齊、
     GenerateNewNode 半徑/圖塊/儲量連接、FluxOre 事件）、
     Generators/MineralNodeGeneratorBase.cs（FindStartPosition、NormalizeNoise、
     CreateMineralNode、KeepOutDist）、Generators/RandomWalkMineralNodeGenerator.cs
     （洪水填充，5 萬步上限）、MineralNode.cs（uint[] 數值，7 天過期，
     30 分鐘儲存）、MineralNodeRepository.cs（mineralnodes 表，壓縮數值）、
     Minerals/MineralExtractor.cs（固體/液體/砂石採集）、
     Modules/DrillerModule.cs（amount 屬性 + 修正）、Materials/MaterialHelper.cs
     （minerals.definition -> item）、Zones/DistanceConstants.cs
     （MINERAL_DISTANCE_FROM_BASE_MIN = 100）。 -->
