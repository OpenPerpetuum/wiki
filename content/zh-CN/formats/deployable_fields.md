---
title: "可部署字段"
description: "可部署物的识别方式、胶囊与对象的配对关系，以及驱动已放置区域对象的聚合字段。"
weight: 40
---

# 可部署字段

**可部署物**（deployable）是指可以作为整体放置到区域中的物品（移动传送器、地雷、场效应发射器、PBS 结构等）。它通过标志位进行识别，与胶囊↔对象定义进行配对，并在运行时由聚合字段驱动。

## 识别方式

- **类别标志** `cf_deployable_structure` = `0x998`（位掩码），位于
  `entitydefaults.categoryflags` 上——这是实体注册表扫描以注册
  部署器物品类别的标志集合（`EntitiesModule.cs`，例如 `PlantSeedDeployer`
  即为该类别注册）。
- **属性标志** `deployable` = `entitydefaults.attributeflags` 上的第 **23** 位
  （掩码 `1 << 23`）。
- 完整目录（含属性数据）生成于 [Deployables](/content/deployables/)。

## 胶囊 ↔ 对象配对

可部署物以成对形式存在：**胶囊**（capsule，即玩家背包中携带的物品）和
**对象**（object，即出现在区域中的实体单元）。配对关系由数据库列
`entitydefaults.targetdefinition` 表示，且为**双向**：

- capsule.`targetdefinition` → 对象的定义
- object.`targetdefinition` → 胶囊的定义

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` 可解析
任意方向。示例配对：`def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`。

## 部署流程

`ItemDeployer.cs`（非 PBS 可部署物的基类）：

1. `Deploy(zone, player)` 计算玩家中心处的生成位置。
2. `CreateDeployableItem` 构建**对象**单元（而非胶囊）并保存。
3. 渲染一个 5 秒的"部署光束"。
4. 事务提交时，对象被添加到区域中（`ZoneEnterType.Deploy`）。

PBS 结构使用独立的 `PBSDeployer` / `PBSObjectHelper` 路径；当 PBS
对象被拆解时，它从区域中移除，其**胶囊**被添加到战利品中
（`PBSObjectHelper.cs`）。

## 运行时聚合字段

以下字段（来自 `aggregatevalues`，按定义区分）在对象放置到区域后驱动其行为。
消费方已标注。

| 字段 | 含义 | 消费方 |
|---|---|---|
| `despawn_time` | 已放置对象的生命周期，单位为**毫秒**。到期后该单元从区域中移除（若为远程操控则被销毁）。 | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → 应用 `effect_despawn_timer`。 |
| `armor_max` | 已放置单元的最大护甲值。 | 单元战斗 |
| `resist_chemical/explosive/kinetic/thermal` | 伤害抗性。 | 单元战斗 |
| `signature_radius` | 扫描信号半径。 | 扫描仪 / 隐蔽 |
| `stealth_strength` | 隐蔽强度。 | 扫描仪 / 隐蔽 |
| `effect_*`（如 `effect_field_sensor_strength_modifier`、`effect_stealth_strength_modifier`、`effect_field_reactor_radiation_modifier`） | 对象发出的场效应修正值。 | `FieldEffectGenerators/*`（如 `FieldEccmEffectGeneratorDeployer` 通过 `GetPropertyModifier` 读取 `despawn_time` 和 effect 字段）。 |
| `mobile_teleport_cooldown` | 移动传送器两次使用之间的冷却时间（毫秒）。 | 移动传送器单元 |
| `trigger_mass` | 触发地雷起爆的质量阈值。 | 地雷单元 |
| `damage_kinetic/thermal/explosive/chemical/toxic` | 地雷按属性造成的伤害值。 | 地雷单元 |

`despawn_time` 是核心字段：每个已放置对象都会获得一个
`UnitDespawnHelper`，其 `IntervalTimer`（650 毫秒 tick）会重新检查
`effect_despawn_timer` 效果，当该效果消失时执行移除策略。

### 实例 — `def_mobile_field_eccm`

来自 [Deployables](/content/deployables/)：

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (object) / 50 (armored capsule)
despawn_time=900000          → 900 秒 = 15 分钟生命周期
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

部署胶囊后，对象在机器人位置生成；其生命周期为 15 分钟，拥有 15,000 护甲
和 150% 抗性，存活期间会发出一个场效应，将传感器强度提升 100%，
并将反应堆辐射降低 25%。

<!-- Developer notes: EntitiesModule.cs:449 (ByCategoryFlags<PlantSeedDeployer>
     cf_deployable_structure); ExportedTypes/CategoryFlags.cs (cf_deployable_structure
     = 0x998), ExportedTypes/AttributeFlags.cs (deployable = 23);
     EntityFramework/DefinitionConfig.cs (targetdefinition column, TargetEntityDefault);
     Deployers/ItemDeployer.cs (Deploy flow, 5s beam, ZoneEnterType.Deploy);
     Zones/PBS/PBSHelper.cs (capsule<->object), Zones/PBS/PBSObjectHelper.cs
     (deconstruct -> capsule loot); Units/UnitDespawnHelper.cs (despawn_time ->
     effect_despawn_timer, 650ms tick, CancellableDespawnHelper for strongholds);
     Zones/FieldEffectGenerators/FieldEccmEffectGeneratorDeployer.cs
     (GetPropertyModifier(AggregateField.despawn_time) + effect_* fields). -->