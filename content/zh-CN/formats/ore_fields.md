---
title: "矿石字段"
description: "minerals 和 mineralconfigs 表、节点生成公式、节点生命周期以及开采机制。"
weight: 30
---

# 矿石字段

矿石数据分为两个层级：**按类型**（`minerals` —— 材料是什么以及单次开采产出多少）和**按区域按类型**（`mineralconfigs` —— 有多少节点、多大、填充量如何）。运行时节点状态保存在 `mineralnodes` 表中。

## `minerals`

| 列 | 类型 | 使用者 | 含义 |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | `MaterialType` 枚举序号（1=Titan … 19=DHDT，0=Undefined）。所有关联查询均使用 `mineralconfigs.materialtype = minerals.idx`。 |
| `name` | varchar | `ToMaterialType()` | 类型名称（"titan"、"crude" 等）。 |
| `definition` | int | `MaterialHelper` → item | 开采产出的物品定义（例如 titan → def 168）。 |
| `amount` | int | `DrillerModule` | **每次开采的基础单位数**（titan 1500、crude 1500、stermonit 975、liquizit 450、epriton 450 等）。 |
| `extractionType` | int | `TerrainsModule` | 0 = 固体（`OreLayer`），1 = 液体（`LiquidLayer`）。 |
| `enablereffectrequired` | bit | 模块限制 | 开采是否需要启用效果（enabler）。 |
| `geoscandocument` | int | 扫描物品 | 该材料的地质扫描文档物品。 |

## `mineralconfigs`

每个（区域，材料）一条记录。由 `MineralConfigurationReader` 读取 → 每行对应一个 `MineralLayer`：

| 列 | 类型 | 使用者 | 含义 |
|---|---|---|---|
| `zoneId` | int | 层构建 | 所属区域。 |
| `materialtype` | int | → `minerals.idx` | 材料类型。 |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | 该区域维持的该类型节点数量。 |
| `maxtilespernode` | int | 生成器 | 每个节点斑块的最大图块数；同时也决定间距半径（见下文）。 |
| `totalamountpernode` | int | 生成器 | 新生节点中的材料总量，分布在该斑块的各图块上。 |
| `minthreshold` | double | 生成器 | 最小归一化单图块填充量（0–1）；低于该值的图块会被丢弃。 |

### 节点生成公式（`MineralNodeGeneratorBase.cs`）

对于具有上述配置的新节点：

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = 起始位置必须与最近的现有节点相距 ≥ 2 × radius
blob    = 随机游走漫水填充（4 图块笔刷），最多填充 maxtilespernode 个有效图块
tile[i] = ( noise[i] / max(noise) ) 归一化到 [minthreshold, 1]
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // 抖动扰动，随后截断为 uint
```

停靠基地与传送点周围的禁区距离（`KeepOutDist`）：epriton = 100 图块（`MINERAL_DISTANCE_FROM_BASE_MIN`），flux ore = 200；所有其他类型 = 0。

### 实例计算 — Daoden (zone_ASI) 原油 crude（id 2）

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → 间距 ≥ 80 图块
blob    = 最多 1257 个图块
tile    = 份额 ∈ [0.5, 1.0] × (125,000,000 / Σnormalized) × 抖动扰动
```

一个完整的原油节点包含 1.25 亿单位材料；按每个钻探周期 1,500 单位的基础开采量计算，每个节点约可进行 83,000 次开采，全区 8 个节点总计约 666,000 次。

## 节点状态 — `mineralnodes`

| 列 | 含义 |
|---|---|
| `zoneid`, `materialtype` | 所属区域 + 类型 |
| `x, y, width, height` | 节点边界包围盒（斑块区域） |
| `data` | 每个图块压缩的 `uint` 数据（包围盒内按行优先排列） |

生命周期（`MineralNode.cs`、`MineralLayer.cs`）：

- **加载**：区域启动时加载所有存储的节点；总量 ≤ `totalamountpernode` 的 **1%** 的节点将被直接删除。
- **补充**：如果存活的节点数少于 `maxnodes`，则生成新节点（见上方公式）。
- **过期**：**未被触碰**的节点在 **7 天**后过期（`TimeTracker`）；采矿会重置该计时器。最大图块值归 0 的节点也会过期。
- **持久化**：脏节点在 **30 分钟**保存定时器触发时刷新写入数据库。
- **通量矿联动**：`FluxOre` 节点的减少/过期会发布 `OreNpcSpawnMessage` → NPC 生成器监听该消息（`OreNPCSpawner`）。

## 开采机制（`MineralExtractor.cs`、`DrillerModule.cs`）

实际开采量为 `minerals.amount` 乘以机器人的 `mining_amount_modifier` 属性（由 `mining_amount_modifier`、`effect_mining_amount_modifier`、`drone_amplification_mining_amount_modifier`、`effect_excavator_mining_amount_modifier` 聚合而成）。

- **固体**（`OreLayer`）：从机器人所站立的**单个图块**中提取 `min(图块值, 开采量)`。
- **液体**（`LiquidLayer`）：抽取**整个节点**，优先抽取距离最近的图块（按距离平方优先队列），直到满足开采量。
- **砂石 Gravel**（仅限新手训练区域，`GravelLayer`）：读取图块值但不扣减——砂石节点是取之不尽的。

各类型的产出（精炼产物）参见[矿石](/content/ores/)；各区域的节点数量参见[区域索引](/zones/zone-index/)。

<!-- 开发者说明：Zones/Terrains/Materials/Minerals/MineralConfiguration.cs
     （读取器 + 配置）、MineralLayer.cs（LoadMineralNodes 1% 删除 + 补齐、
     GenerateNewNode 半径/图块/储量连接、FluxOre 事件）、
     Generators/MineralNodeGeneratorBase.cs（FindStartPosition、NormalizeNoise、
     CreateMineralNode、KeepOutDist）、Generators/RandomWalkMineralNodeGenerator.cs
     （漫水填充，5 万步上限）、MineralNode.cs（uint[] 数值，7 天过期，
     30 分钟保存）、MineralNodeRepository.cs（mineralnodes 表，压缩数值）、
     Minerals/MineralExtractor.cs（固体/液体/砂石开采）、
     Modules/DrillerModule.cs（amount 属性 + 修正）、Materials/MaterialHelper.cs
     （minerals.definition -> item）、Zones/DistanceConstants.cs
     （MINERAL_DISTANCE_FROM_BASE_MIN = 100）。 -->
