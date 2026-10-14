---
title: "植物欄位"
description: "植物規則檔案格式（GenXY），每個規則欄位的型別、預設值和消費者，以及生長狀態機。"
weight: 20
---

# 植物欄位

植物行為透過每個物種的**規則檔案**（純文字）在 `$GameRoot/plantrules/` 下定義。哪些檔案屬於某個區域由資料庫映射 `plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset` 決定；載入與合併由 `PlantRuleLoader.cs` 處理，欄位到物件的映射由 `PlantRule.cs` 負責。

## 檔案格式

每行一個 `key=value`；`//` 風格的註解會被移除。值使用 **GenXY 標記字元**（`GenxyReader.cs` —— 第一個字元決定型別和進位制）：

| 標記 | 解析為 | 範例 |
|---|---|---|
| `n` | int，十進位 | `n125`, `n-1` |
| `N` | int[]，十進位，逗號分隔 | `N5,5,5,5` |
| `f` | double，十進位 | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int，**十六進位** | `iFF` |
| `L` | long，**十六進位** | `L100` |
| `4` | int[]，**十六進位** | `41,2,3` → [1, 2, 3] |

### ⚠ 「裸陣列」陷阱

檔案中還包含形如 `blockingHeight=40,3,3,4` 且**沒有明確標記**的值。解析器對此並沒有特殊處理：開頭的 `4` 會被當作 `IntegerArray`（十六進位）標記處理，其餘部分按十六進位解析。因此：

```
blockingHeight=40,3,3,4   →  標記 '4' + 十六進位陣列 "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  標記 'N' + 十進位陣列                →  [0, 8, 11, 14]
```

兩種寫法最終都解析為 `int[]`，開頭的 `0` 正是被 `4`「吞掉」的部分。這就是為什麼官方內建檔案中的每個裸陣列都以 `4` 開頭——這是一種確保首個元素保持預期值的慣例。**在編寫新的規則檔案時，請明確使用 `N` 前綴**；裸陣列中 ≥ 10 的值會被當作十六進位解析，從而悄然改變含義。

### 繼承

`source=$other_rule.txt` 鍵會先載入 `other_rule.txt`，然後將當前檔案的鍵作為覆蓋項套用（`PlantRuleLoader.LoadRuleByName`）。範例：`irontree_t2.txt` 的內容僅為：

```
source=$irontree_lo.txt
fruitAmount=n125
```

## 欄位參考

所有欄位均從合併後的設定字典中讀取（`PlantRule.cs`）。缺失的鍵會回退到所示的預設值。

| 鍵 | 型別 / 預設值 | 使用者 | 效果 |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | 該物種的 `PlantType` 列舉值（1=GrassA … 19=Devrinol）。也是每圖塊儲存的 `PlantInfo.type` 位元組。 |
| `name` | string | 用戶端資訊負載 | 顯示名稱。 |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | 在為**無**相鄰植物圖塊選擇物種的加權抽取中的權重。0 = 永不自然生成。 |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | 當圖塊**有**相鄰植物時的權重乘數：候選權重 = `neighbourCount × spreading`。0 = 永遠不會在擴散抽取中勝出。 |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | 與同類型現有植物的最小距離；0/負數 = 無限制。 |
| `growRate` | int (0) | `GrowPlantOnTile` | 在狀態機輪轉之前，`PlantInfo.time` 位元組必須累積的立方體 tick 數量。數值越大 = 生長越慢。 |
| `slope` / `minSlope` | int (0) | `ValidateTile` | 衍生坡度層允許的坡度範圍。超出此範圍的植物會被清除。 |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | 海拔範圍，與 `Altitude / 4` 比較（`/4` 對應用戶端座標）。由區域的 `plantaltitudescale` 縮放。 |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | `altitude/4 − waterLevel/4` 的範圍——用於生成海岸植被。同樣按海拔縮放。 |
| `allowedTerrainTypes` | int[] (空) | `ValidateTile` | 允許的 `groundType` 位元組（參見[區域檔案](/zh-TW/formats/zone-files/)）。空 = 無法在任何地方生長。設定 `allowedOnNonNatural` 時完全跳過。 |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | 第一個產出果實的狀態。−1 ⇒ `NotFruiting`（永不可採摘）。 |
| `fruitDefinition` | int (−1) | 採摘 | 果實的物品定義。 |
| `fruitMaterialName` | string | 顯示 | 果實名稱（例如 `$prismocitae`）。 |
| `fruitAmount` | byte (0)，鉗制在 0–255 | `GrowPlantOnTile` | 每株植物的最大果實數量。首次進入結果狀態時填充其 5–15%；此後每次生長 tick 增加 15–25%，上限為 100%。 |
| `health` | 每個狀態 byte[] | `GrowPlantOnTile`，戰鬥 | 每個生長狀態的生命值。在狀態轉變時，當前的生命值**比率**會繼承到新狀態中。 |
| `blockingHeight` | 每個狀態 int[] | `GrowPlantOnTile`，生成計數 | 每個狀態的阻擋高度；`>0` 會在阻擋層設定 `Plant` 位元（walkable=false），並使植物計入區域肥力目標。 |
| `maxAmount` | int (−1) | `SpawnPlants` | 該物種在每個區域的上限；−1 = 無限制。 |
| `playerSeeded` | bool (0) | `GetNewPlantRule`，肥力抽取 | 從**所有**自然生成中排除；僅存在於玩家種植的地方。 |
| `damageScale` | double (1.0) | 植物戰鬥 | 承受傷害倍率。 |
| `onlyOnUnprotectedZone` | bool (0) | 生成驗證 | 僅在非保護區域生長。 |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | 跳過控制位元、地形類型和坡度檢查（可在「人造」圖塊上生長）。 |
| `placesConcrete` | bool (0) | `GrowPlantOnTile`（死亡） | 死亡時清除圖塊下方的 ConcreteA/B 控制位元。 |
| `state_N` | int[] | `GetNextState` | 狀態 `N` 的下一狀態選項——每個元素被**等機率隨機抽取**。 |
| `action_N` | int[] | `GetNextState` | 狀態 `N` 的下一 `PlantType` 選項（等機率）。動作值為 `0`（NotDefined）意味著**死亡**。 |

載入時強制進行一致性檢查（`CheckConsistency`）：`len(health) == len(blockingHeight) == 狀態數量`。

## 生長狀態機

每個 32×32 立方體 tick，針對每個植物圖塊（`GrowPlantOnTile`）：

1. 如果 `time < growRate`：`time++`，結束。
2. 否則：`time = 0`，針對當前狀態擲骰選取 `state_N` 和 `action_N`：
   - `action == 0` → 植物死亡（向用戶端發送清除訊號 `type:0, state:1`）；如果 `placesConcrete`，清除圖塊下方的混凝土。
   - 否則 → `type = action`，`state = next`，`health = healthRatio × Health[newState]`（保留受損比例）。
   - 果實：若 `newState == fruitingState`，`material = fruitAmount × uniform(0.05, 0.15)`；若 `newState > fruitingState`，`material += fruitAmount × uniform(0.15, 0.25)`（上限為 `fruitAmount`）；否則 `material = 0`。
   - 阻擋高度 = `blockingHeight[newState]`；阻擋層的 `Plant` 位元跟隨 `height > 0`。

### 實例計算 — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → 無相鄰圖塊抽取中 1/… 的權重
spreading=n2        → 聚集權重 = 2 × 鄰居數量
growRate=n1         → 每個立方體 tick 都輪轉一次狀態（極快）
maxAmount=n190      → 每個立方體最多 190 個
health=N5,5,5,5     → 每個狀態下 5 點生命值
blockingHeight=40,0,0,0 → 解析為 [0,0,0,0]：草叢從不阻擋
fruitingState=n-1   → NotFruiting：草叢永不可採摘
state_0=40,0,1      → [0,0,1]：2/3 留在狀態 0，1/3 前進
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → 在最終狀態中：3/4 存留，1/4 死亡
```

因此，一個草叢圖塊：平均每 3 個 tick 推進一個狀態，在最終狀態下每個 tick 有 25% 的機率死亡並重新播種——這是一種沒有果實、持續更替的地表覆蓋物種。

### 實例計算 — `wall.txt`（12 個狀態，帶 `N` 前綴）

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`，`health=N20,60,80,…,255`，
`state_7=N7,7,8,8,6`（可以狀態後退），`playerSeeded=n1`，
`onlyOnUnprotectedZone=n1`，`maxAmount=n15`：一種玩家種植的防禦工事，僅存在於非保護區域，每個立方體上限為 15 個，經過 12 個狀態生長（偶爾會縮減），最高可達高度 14 和 255 點生命值。

## 每圖塊狀態的儲存位置

執行時每圖塊狀態是區域植物層檔案中的 7 位元組 `PlantInfo` 結構體（`type, state, time, spawn, health, material, groundType`）——參見[區域檔案](/zh-TW/formats/zone-files/)。`spawn` 位元組是烘焙在區域檔案中的每圖塊生成機率——`0` 表示不育圖塊（其上的植物在驗證期間會被清除，且永遠不會發芽）；任何其他值表示在該圖塊上的植物再生嘗試以 ≈ `spawn/256` 的機率通過隨機門。伺服器從不寫入該位元組。線上資料驗證：`plants.0106.bin` 的每個圖塊均攜帶 `0x83`（≈ 51%）。

## 用戶端資料負載

`PlantRuleExtensions.GetPlantInfoForClient` 為每個物種發送：`index`、`mineral`（= fruitDefinition）、`name`、`blocks`（blockingHeight）、`health`。

<!-- 開發者說明：Materials/Plants/PlantRule.cs（欄位獲取器、GetNextState、CheckConsistency）；
     PlantRuleLoader.cs（檔案載入、source: 覆蓋、套用於 allowedAltitudeLow/High + allowedWaterLevelLow 的 plantAltitudeScale）；
     PlantRuleExtensions.cs（fertility + spreading 加權抽取）；
     NatureCube.cs（ValidateTile 檢查順序：阻擋旗標 -> 生成位元組 -> 規則存在性 -> 控制位元 -> altitude/4 -> 水位 -> 地形類型 -> 坡度；
     GrowPlantOnTile 狀態機 + 果實計算）；Common/SettingsLoader.cs（使用 '#' 連接行隨後由 GenxyConverter.Deserialize 解析）；
     GenXY/GenxyReader.cs + GenxyToken.cs（標記字元；'4' = 十六進位 int 陣列，'N' = 十進位 int 陣列，'n' = 十進位 int）。
     規則檔案位於 $GameRoot/plantrules（plantrules 表映射 rulesetid -> 檔案名稱）。 -->
