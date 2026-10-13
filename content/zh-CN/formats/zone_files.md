---
title: "区域文件"
description: "二进制地形层文件：命名规则、结构体布局、标志位、保存周期，以及存储在数据库中的内容。"
weight: 50
---

# 区域文件

区域的地形以一组**二进制层文件**存储，每层一个文件，与区域数据并列存放。文件名为 `{layer}.{zoneid:0000}.bin`（`Zone.CreateTerrainDataFilename`）——例如区域 42 对应 `plants.0042.bin`。各层是固定大小结构体的扁平数组，**行优先，宽 × 高**（默认 2048×2048 = 4,194,304 个图块）。

## 各层说明

| 文件 | 结构体 | 每图块字节数 | 内容 |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags`（字节）+ `height`（字节）——障碍物、植物、装饰、岛屿 |
| `control.NNNN.bin` | `TerrainControlFlags` | 2（或 1） | 每图块的控制位（见下方特殊说明） |
| `plants.NNNN.bin` | `PlantInfo` | 7 | 每图块的植物状态（见下文） |
| `altitude.NNNN.bin` | `ushort` | 2 | 高程；在植物检查中以 `value / 4` 比较（客户端坐标缩放） |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | 仅限可改造区域：每图块的混合掩码（见下文） |
| `altitude_original.NNNN.bin` | `ushort` | 2 | 仅限可改造区域：磁盘上的改造前高程——**服务器不读取此文件**（见下文） |

派生层（加载时计算，**非**文件）：`SlopeLayer`（由高程计算）和 `Passable`（由 blocks + 坡度 + 数据库中的可通行位置计算，仅限不可改造区域）。在可改造区域中，高程被包装为 `TerraformableAltitude`，加载时为每个图块计算一个**屏障**范围：`blend/65535` 将常量 1850 → 原始高程（最小值）和 30000 → 原始高程（最大值）进行混合，然后将范围钳制为始终包含当前值。改造后的高程更新会被钳制在该屏障内——因此 `blend = 0` 时图块可在 1850 到 30000 之间自由改造，而 `blend = 65535` 则将其锁定在原始高程。（磁盘上的 `altitude_original.NNNN.bin` 文件保存改造前的高程，供外部工具使用；服务器在内存中从已加载的 `altitude.NNNN.bin` 获取原始高程快照，从不读取该文件名。）

### `BlockingInfo`（2 字节）

`flags` 为 `BlockingFlags`（字节）：

| 位 | 名称 |
|---|---|
| 1 | Obstacle（障碍物） |
| 2 | Plant（植物） |
| 4 | Decor（装饰） |
| 8 | Island（岛屿） |

`NonNaturally` = Decor \| Island \| Obstacle。`height` 是图块的行走阻挡高度（植物阻挡高度由植物生长代码写入此处）。

### `TerrainControlFlags`（控制层）

`ushort` 标志集：

| 位 | 名称 |
|---|---|
| 1 | AntiPlant（禁止种植） |
| 2 | TerraformProtected（改造保护） |
| 4 | SyndicateArea（辛迪加区域） |
| 8 | ConcreteA（混凝土 A） |
| 16 | ConcreteB（混凝土 B） |
| 64 | Roaming（游荡区） |
| 128 | Highway（公路） |
| 256 | PBSHighway（PBS 公路） |
| 512 | PBSTerraformProtected（PBS 改造保护） |
| 1024 | NpcRestricted（NPC 限制） |

（512/1024 的编号遵循 `1 << n`；位 32 未使用。）当 `!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)` 时，图块允许种植。

**存储特殊说明**：加载器同时接受**每图块 1 字节**和**每图块 2 字节**的控制文件——如果文件长度等于图块数量，则每个字节被扩展为 `TerrainControlFlags`；否则直接读取原始 `ushort` 数组（`LayerFileIO.LoadLayerData`）。所有在线区域均使用**2 字节格式**（`control.0000.bin` = 8,388,608 B = 4,194,304 × 2）；1 字节格式（4 MB）是加载器仍支持的遗留回退方案。

### `PlantInfo`（7 字节）——植物图块状态

| 字节 | 字段 | 含义 |
|---|---|---|
| 0 | `type` | `PlantType`（0 = 空；1..19 见 [Plant fields](/zh-CN/formats/plant-fields/)） |
| 1 | `state` | 生长状态索引（对应规则的 `state_N` 表） |
| 2 | `time` | 生长计时累加器（与规则的 `growRate` 比较） |
| 3 | `spawn` | **每图块的生成概率，烘焙在区域文件中；服务器从不写入此字段**（代码中不存在任何赋值——`PlantInfo.Clear()` 刻意保留该值）。0 = 不育图块：其上已有的任何植物会在验证时立即清除，且永远不会萌发。否则它充当每次尝试的门槛：在植物再生遍历中，随机选中的空图块仅当 `FastRandom.NextByte() < spawn` 时才被接受，即每图块通过概率 ≈ `spawn/256`。 |
| 4 | `health` | 当前生命值（规则中对应状态生命值的比例） |
| 5 | `material` | 当前果实数量（0–255） |
| 6 | `groundType` | `GroundType` 字节（0=Darkrocks … 17=Sand-ish, 20=undefined）——植物规则的 `allowedTerrainTypes` 所检查的地形类别 |

### 实例——2048×2048 区域的文件大小（已对照在线文件验证）

```
blocks    4,194,304 tiles × 2 B = 8,388,608 B (8 MB)
plants    4,194,304 tiles × 7 B = 29,360,128 B (28 MB)
altitude  4,194,304 tiles × 2 B = 8,388,608 B (8 MB)
control   4,194,304 tiles × 2 B = 8,388,608 B (8 MB, 2-byte form; a 1-byte legacy file would be 4 MB)
```

**在线数据验证**（`plants.0106.bin`，可改造的 gamma 区域）：全部 4,194,304 个图块的 `spawn = 0x83`（131/256 ≈ 51% 每次尝试概率），`type = 0`，仅有 10 个图块持有存活植物——生成图是一个覆盖全区域的预烘焙概率场，与植物当前位置无关。

并非每个区域都拥有所有文件：84 个区域中有 66 个附带 `plants.NNNN.bin`。缺少该文件的 18 个区域是被取代的遗留 gamma 变体（`zone_tm_g_*`、`zone_ics_g_*`、`zone_asi_g_*`，ID 20–43），不会被加载。层目录为 `$GameRoot/layers/`。

## 保存周期（`IntervalLayerSaver.cs`）

- 每个可变层（blocks、control、plants、altitude）由一个 `IntervalLayerSaver<T>` 监视；任何图块/区域写入都会设置脏标志。
- 保存器注册为进程，绑定在 **2 小时**定时器上（`TerrainsModule`）；当计时触发时，脏层会被写入。
- 写入先输出到 `.tmp<ticks>.bin` 文件，经过**MD5 校验**（重新读取比对）后，才替换正式文件。
- 服务器停止时，脏层会再保存一次。
- 矿节点**不**在这些文件中——它们持久化到 `mineralnodes` 数据库表（30 分钟刷新，见 [Ore fields](/zh-CN/formats/ore-fields/)）。

## 哪些是文件，哪些不是

| 数据 | 存储位置 |
|---|---|
| 地形层（blocks/control/plants/altitude） | `.bin` 文件 |
| 矿节点状态 | 数据库 `mineralnodes` |
| 每区域的植物物种 | 数据库 `plantrules` + 规则**文件**（`$GameRoot/plantrules/*.txt`） |
| 区域配置（肥力、大小、类型、规则集） | 数据库 `zones` |
| 矿石配置 | 数据库 `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1-vs-2 byte control handling, safe zero-fill on size mismatch);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty flag, MD5 + tmp rename, stop-save);
     Bootstrapper/Modules/TerrainsModule.cs (layer load order: blocks, control, plants,
     altitude, blend; slope + passable derivation; 2h saver + 2h material process). -->