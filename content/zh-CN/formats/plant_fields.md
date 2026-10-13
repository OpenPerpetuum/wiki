---
title: "植物字段"
description: "植物规则文件格式（GenXY），每个规则字段的类型、默认值和消费者，以及生长状态机。"
weight: 20
---

# 植物字段

植物行为通过每个物种的**规则文件**（纯文本）在 `$GameRoot/plantrules/` 下定义。哪些文件属于某个区域由数据库映射 `plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset` 决定；加载与合并由 `PlantRuleLoader.cs` 处理，字段到对象的映射由 `PlantRule.cs` 负责。

## 文件格式

每行一个 `key=value`；`//` 风格的注释会被移除。值使用 **GenXY 标记字符**（`GenxyReader.cs` —— 第一个字符决定类型和进制）：

| 标记 | 解析为 | 示例 |
|---|---|---|
| `n` | int，十进制 | `n125`, `n-1` |
| `N` | int[]，十进制，逗号分隔 | `N5,5,5,5` |
| `f` | double，十进制 | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int，**十六进制** | `iFF` |
| `L` | long，**十六进制** | `L100` |
| `4` | int[]，**十六进制** | `41,2,3` → [1, 2, 3] |

### ⚠ “裸数组”陷阱

文件中还包含形如 `blockingHeight=40,3,3,4` 且**没有显式标记**的值。解析器对此并没有特殊处理：开头的 `4` 会被当作 `IntegerArray`（十六进制）标记消费，其余部分按十六进制解析。因此：

```
blockingHeight=40,3,3,4   →  标记 '4' + 十六进制数组 "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  标记 'N' + 十进制数组                →  [0, 8, 11, 14]
```

两种写法最终都解析为 `int[]`，开头的 `0` 正是被 `4`“吞掉”的部分。这就是为什么官方自带文件中的每个裸数组都以 `4` 开头——这是一种确保首个元素保持预期值的惯例。**在编写新的规则文件时，请显式使用 `N` 前缀**；裸数组中 ≥ 10 的值会被当作十六进制解析，从而悄无声息地改变含义。

### 继承

`source=$other_rule.txt` 键会先加载 `other_rule.txt`，然后将当前文件的键作为覆盖项应用（`PlantRuleLoader.LoadRuleByName`）。例如：`irontree_t2.txt` 的内容仅为：

```
source=$irontree_lo.txt
fruitAmount=n125
```

## 字段参考

所有字段均从合并后的配置字典中读取（`PlantRule.cs`）。缺失的键会回退到所示的默认值。

| 键 | 类型 / 默认值 | 使用者 | 效果 |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | 该物种的 `PlantType` 枚举值（1=GrassA … 19=Devrinol）。也是每图块存储的 `PlantInfo.type` 字节。 |
| `name` | string | 客户端信息载荷 | 显示名称。 |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | 在为**无**相邻植物图块选择物种的加权抽取中的权重。0 = 永不自然生成。 |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | 当图块**有**相邻植物时的权重乘数：候选权重 = `neighbourCount × spreading`。0 = 永远不会在扩散抽取中胜出。 |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | 与同类型现有植物的最小距离；0/负数 = 无限制。 |
| `growRate` | int (0) | `GrowPlantOnTile` | 在状态机轮转之前，`PlantInfo.time` 字节必须累积的立方体 tick 数量。数值越大 = 生长越慢。 |
| `slope` / `minSlope` | int (0) | `ValidateTile` | 派生坡度层允许的坡度范围。超出此范围的植物会被清除。 |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | 海拔范围，与 `Altitude / 4` 比较（`/4` 对应客户端坐标）。由区域的 `plantaltitudescale` 缩放。 |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | `altitude/4 − waterLevel/4` 的范围——用于生成海岸植被。同样按海拔缩放。 |
| `allowedTerrainTypes` | int[] (空) | `ValidateTile` | 允许的 `groundType` 字节（参见[区域文件](/zh-CN/formats/zone-files/)）。空 = 无法在任何地方生长。设置 `allowedOnNonNatural` 时完全跳过。 |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | 第一个产出果实的状态。−1 ⇒ `NotFruiting`（永不可采摘）。 |
| `fruitDefinition` | int (−1) | 采摘 | 果实的物品定义。 |
| `fruitMaterialName` | string | 显示 | 果实名称（例如 `$prismocitae`）。 |
| `fruitAmount` | byte (0)，钳制在 0–255 | `GrowPlantOnTile` | 每株植物的最大果实数量。首次进入结果状态时填充其 5–15%；此后每次生长 tick 增加 15–25%，上限为 100%。 |
| `health` | 每个状态 byte[] | `GrowPlantOnTile`，战斗 | 每个生长状态的生命值。在状态转变时，当前的生命值**比率**会继承到新状态中。 |
| `blockingHeight` | 每个状态 int[] | `GrowPlantOnTile`，生成计数 | 每个状态的阻挡高度；`>0` 会在阻挡层设置 `Plant` 位（walkable=false），并使植物计入区域肥力目标。 |
| `maxAmount` | int (−1) | `SpawnPlants` | 该物种在每个区域的上限；−1 = 无限制。 |
| `playerSeeded` | bool (0) | `GetNewPlantRule`，肥力抽取 | 从**所有**自然生成中排除；仅存在于玩家种植的地方。 |
| `damageScale` | double (1.0) | 植物战斗 | 承受伤害倍率。 |
| `onlyOnUnprotectedZone` | bool (0) | 生成验证 | 仅在非保护区域生长。 |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | 跳过控制位、地形类型和坡度检查（可在“人造”图块上生长）。 |
| `placesConcrete` | bool (0) | `GrowPlantOnTile`（死亡） | 死亡时清除图块下方的 ConcreteA/B 控制位。 |
| `state_N` | int[] | `GetNextState` | 状态 `N` 的下一状态选项——每个元素被**等概率随机抽取**。 |
| `action_N` | int[] | `GetNextState` | 状态 `N` 的下一 `PlantType` 选项（等概率）。动作值为 `0`（NotDefined）意味着**死亡**。 |

加载时强制进行一致性检查（`CheckConsistency`）：`len(health) == len(blockingHeight) == 状态数量`。

## 生长状态机

每个 32×32 立方体 tick，针对每个植物图块（`GrowPlantOnTile`）：

1. 如果 `time < growRate`：`time++`，结束。
2. 否则：`time = 0`，针对当前状态掷骰选取 `state_N` 和 `action_N`：
   - `action == 0` → 植物死亡（向客户端发送清除信号 `type:0, state:1`）；如果 `placesConcrete`，清除图块下方的混凝土。
   - 否则 → `type = action`，`state = next`，`health = healthRatio × Health[newState]`（保留受损比例）。
   - 果实：若 `newState == fruitingState`，`material = fruitAmount × uniform(0.05, 0.15)`；若 `newState > fruitingState`，`material += fruitAmount × uniform(0.15, 0.25)`（上限为 `fruitAmount`）；否则 `material = 0`。
   - 阻挡高度 = `blockingHeight[newState]`；阻挡层的 `Plant` 位跟随 `height > 0`。

### 实例计算 — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → 无相邻图块抽取中 1/… 的权重
spreading=n2        → 聚集权重 = 2 × 邻居数量
growRate=n1         → 每个立方体 tick 都轮转一次状态（极快）
maxAmount=n190      → 每个立方体最多 190 个
health=N5,5,5,5     → 每个状态下 5 点生命值
blockingHeight=40,0,0,0 → 解析为 [0,0,0,0]：草丛从不阻挡
fruitingState=n-1   → NotFruiting：草丛永不可采摘
state_0=40,0,1      → [0,0,1]：2/3 留在状态 0，1/3 前进
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → 在最终状态中：3/4 存留，1/4 死亡
```

因此，一个草丛图块：平均每 3 个 tick 推进一个状态，在最终状态下每个 tick 有 25% 的概率死亡并重新播种——这是一种没有果实、持续更替的地表覆盖物种。

### 实例计算 — `wall.txt`（12 个状态，带 `N` 前缀）

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`，`health=N20,60,80,…,255`，
`state_7=N7,7,8,8,6`（可以状态后退），`playerSeeded=n1`，
`onlyOnUnprotectedZone=n1`，`maxAmount=n15`：一种玩家种植的防御工事，仅存在于非保护区域，每个立方体上限为 15 个，经过 12 个状态生长（偶尔会缩减），最高可达高度 14 和 255 点生命值。

## 每图块状态的存储位置

运行时每图块状态是区域植物层文件中的 7 字节 `PlantInfo` 结构体（`type, state, time, spawn, health, material, groundType`）——参见[区域文件](/zh-CN/formats/zone-files/)。`spawn` 字节是烘焙在区域文件中的每图块生成概率——`0` 表示不育图块（其上的植物在验证期间会被清除，且永远不会发芽）；任何其他值表示在该图块上的植物再生尝试以 ≈ `spawn/256` 的概率通过随机门。服务器从不写入该字节。在线数据验证：`plants.0106.bin` 的每个图块均携带 `0x83`（≈ 51%）。

## 客户端数据载荷

`PlantRuleExtensions.GetPlantInfoForClient` 为每个物种发送：`index`、`mineral`（= fruitDefinition）、`name`、`blocks`（blockingHeight）、`health`。

<!-- 开发者说明：Materials/Plants/PlantRule.cs（字段获取器、GetNextState、CheckConsistency）；
     PlantRuleLoader.cs（文件加载、source: 覆盖、应用于 allowedAltitudeLow/High + allowedWaterLevelLow 的 plantAltitudeScale）；
     PlantRuleExtensions.cs（fertility + spreading 加权抽取）；
     NatureCube.cs（ValidateTile 检查顺序：阻挡标志 -> 生成字节 -> 规则存在性 -> 控制位 -> altitude/4 -> 水位 -> 地形类型 -> 坡度；
     GrowPlantOnTile 状态机 + 果实计算）；Common/SettingsLoader.cs（使用 '#' 连接行随后由 GenxyConverter.Deserialize 解析）；
     GenXY/GenxyReader.cs + GenxyToken.cs（标记字符；'4' = 十六进制 int 数组，'N' = 十进制 int 数组，'n' = 十进制 int）。
     规则文件位于 $GameRoot/plantrules（plantrules 表映射 rulesetid -> 文件名）。 -->
