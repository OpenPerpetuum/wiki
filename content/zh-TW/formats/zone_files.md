---
title: "區域檔案"
description: "二進位地形層檔案：命名規則、結構體佈局、旗標位元、儲存週期，以及哪些資料存在資料庫中。"
weight: 50
---

# 區域檔案

區域的地形以一組**二進位層檔案**儲存，每層一個檔案，與區域資料並排放置。命名格式為 `{layer}.{zoneid:0000}.bin`
（`Zone.CreateTerrainDataFilename`）——例如第 42 號區域的植物層為 `plants.0042.bin`。各層為固定大小結構體的
平坦陣列，採用**列優先、寬 × 高**排列（預設 2048×2048 =
4,194,304 格）。

## 各層說明

| 檔案 | 結構體 | 每格位元組數 | 內容 |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags`（byte）+ `height`（byte）——障礙物、植物、裝飾、島嶼 |
| `control.NNNN.bin` | `TerrainControlFlags` | 2（或 1） | 每格的控制位元（見下方特殊說明） |
| `plants.NNNN.bin` | `PlantInfo` | 7 | 每格的植物狀態（見下方） |
| `altitude.NNNN.bin` | `ushort` | 2 | 海拔高度；植物判定時以 `value / 4` 比較（客戶端座標縮放） |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | 僅限可地形改造區域：每格的混合遮罩（見下方） |
| `altitude_original.NNNN.bin` | `ushort` | 2 | 僅限可地形改造區域：改造前的磁碟海拔——**伺服器不會讀取此檔案**（見下方） |

衍生層（載入時計算，**非**檔案）：`SlopeLayer`（由海拔計算）和
`Passable`（由 blocks + 坡度 + 資料庫可通行位置計算，僅限不可地形改造區域）。
可地形改造區域的海拔會被包裝在 `TerraformableAltitude` 中，
載入時計算每格的**屏障**範圍：`blend/65535` 混合常數
1850 → 原始海拔（最小值）和 30000 → 原始海拔（最大值），然後將
範圍限制為必定包含當前值。地形改造後的海拔更新會被限制在該屏障內——因此 `blend = 0` 時該格可在 1850 到
30000 之間自由改造，而 `blend = 65535` 則將其固定在原始海拔。（磁碟上的
`altitude_original.NNNN.bin` 檔案儲存改造前的海拔，供外部工具使用；伺服器從已載入的
`altitude.NNNN.bin` 在記憶體中取得原始海拔快照，從不讀取該檔名。）

### `BlockingInfo`（2 位元組）

`flags` 為 `BlockingFlags`（byte）：

| 位元 | 名稱 |
|---|---|
| 1 | Obstacle（障礙物） |
| 2 | Plant（植物） |
| 4 | Decor（裝飾） |
| 8 | Island（島嶼） |

`NonNaturally` = Decor \| Island \| Obstacle。`height` 為該格的行走阻擋高度
（植物生長程式碼會將植物阻擋高度寫入此欄位）。

### `TerrainControlFlags`（控制層）

`ushort` 旗標集合：

| 位元 | 名稱 |
|---|---|
| 1 | AntiPlant |
| 2 | TerraformProtected |
| 4 | SyndicateArea |
| 8 | ConcreteA |
| 16 | ConcreteB |
| 64 | Roaming |
| 128 | Highway |
| 256 | PBSHighway |
| 512 | PBSTerraformProtected |
| 1024 | NpcRestricted |

（512/1024 的編號遵循 `1 << n`；位元 32 未使用。）當
`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)` 時，該格允許植物生長。

**儲存特殊說明**：載入器同時接受**每格 1 位元組**和**每格 2 位元組**的控制
檔案——若檔案長度等於格數，則每個位元組會被擴展為
`TerrainControlFlags`；否則直接讀取原始 `ushort` 陣列
（`LayerFileIO.LoadLayerData`）。現行區域全部使用**2 位元組格式**
（`control.0000.bin` = 8,388,608 B = 4,194,304 × 2）；1 位元組格式（4 MB）是
載入器仍支援的舊版備援。

### `PlantInfo`（7 位元組）——植物格狀態

| 位元組 | 欄位 | 意義 |
|---|---|---|
| 0 | `type` | `PlantType`（0 = 空；1..19 見[植物欄位](/zh-TW/formats/plant-fields/)） |
| 1 | `state` | 生長狀態索引（對應規則的 `state_N` 表格） |
| 2 | `time` | 生長計數器（與規則的 `growRate` 比較） |
| 3 | `spawn` | **每格生成機率，已烘焙至區域檔案中；伺服器從不寫入此值**（程式碼中不存在任何賦值——`PlantInfo.Clear()` 刻意保留此欄位）。0 = 不育格：其上已有的植物會在驗證時立即清除，且永遠不會萌發。否則它作為每次嘗試的閘門：植物再生遍歷中，隨機選取的空白格僅在 `FastRandom.NextByte() < spawn` 時才被接受，即每格通過機率 ≈ `spawn/256`。 |
| 4 | `health` | 當前生命值（規則中該狀態生命值的比例） |
| 5 | `material` | 當前果實數量（0–255） |
| 6 | `groundType` | `GroundType` 位元組（0=Darkrocks … 17=Sand-ish, 20=undefined）——植物規則的 `allowedTerrainTypes` 所比對的地形類別 |

### 實例——2048×2048 區域的檔案大小（已對照現行檔案驗證）

```
blocks    4,194,304 格 × 2 B = 8,388,608 B (8 MB)
plants    4,194,304 格 × 7 B = 29,360,128 B (28 MB)
altitude  4,194,304 格 × 2 B = 8,388,608 B (8 MB)
control   4,194,304 格 × 2 B = 8,388,608 B (8 MB, 2 位元組格式；1 位元組舊版檔案則為 4 MB)
```

**現行資料驗證**（`plants.0106.bin`，可地形改造的 gamma 區域）：全部 4,194,304
格的 `spawn = 0x83`（131/256 ≈ 51% 每次嘗試機率），且 `type = 0`，
僅有 10 格持有存活植物——生成圖為覆蓋整個區域的烘焙機率場，
與植物當前所在位置無關。

並非每個區域都擁有所有檔案：84 個區域中有 66 個附有 `plants.NNNN.bin`。
缺少此檔案的 18 個為已被取代的舊版 gamma 變體（`zone_tm_g_*`、`zone_ics_g_*`、
`zone_asi_g_*`，id 20–43），不會被載入。層目錄為
`$GameRoot/layers/`。

## 儲存週期（`IntervalLayerSaver.cs`）

- 每個可變層（blocks、control、plants、altitude）都由一個
  `IntervalLayerSaver<T>` 監控；任何格/區域寫入都會設定髒標記。
- 儲存器以**2 小時**計時器註冊為一個行程
  （`TerrainsModule`）；計時器觸發時，髒層會被寫入。
- 寫入會先寫入 `.tmp<ticks>.bin` 暫存檔案，經**MD5 驗證**（重新讀取比對）後，
  才替換正式檔案。
- 伺服器停止時，髒層會再儲存一次。
- 礦物節點**不在**這些檔案中——它們持久化到 `mineralnodes` 資料庫
  表格（30 分鐘刷新，見[礦物欄位](/zh-TW/formats/ore-fields/)）。

## 哪些是檔案、哪些不是

| 資料 | 存放位置 |
|---|---|
| 地形層（blocks/control/plants/altitude） | `.bin` 檔案 |
| 礦物節點狀態 | 資料庫 `mineralnodes` |
| 各區域的植物物種 | 資料庫 `plantrules` + 規則**檔案**（`$GameRoot/plantrules/*.txt`） |
| 區域設定（肥沃度、大小、類型、規則集） | 資料庫 `zones` |
| 礦物設定 | 資料庫 `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1-vs-2 byte control handling, safe zero-fill on size mismatch);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty flag, MD5 + tmp rename, stop-save);
     Bootstrapper/Modules/TerrainsModule.cs (layer load order: blocks, control, plants,
     altitude, blend; slope + passable derivation; 2h saver + 2h material process). -->