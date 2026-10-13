---
title: "可部署物欄位"
description: "可部署物的識別方式、膠囊與物件的配對關係，以及驅動已放置區域物件的聚合欄位。"
weight: 40
---

# 可部署物欄位

**可部署物**（deployable）是指可以作為一個單位放置到區域中的項目（行動傳送器、地雷、場效應發射器、PBS 結構等）。它透過旗標進行識別，與膠囊↔物件定義進行配對，並在執行時由聚合欄位驅動。

## 識別方式

- **類別旗標** `cf_deployable_structure` = `0x998`（位元遮罩），位於
  `entitydefaults.categoryflags` — 這是實體註冊表掃描以註冊
  部署器項目類別的集合（`EntitiesModule.cs`，例如 `PlantSeedDeployer` 即為
  此類別註冊的項目）。
- **屬性旗標** `deployable` = `entitydefaults.attributeflags` 上的第 **23** 位
  （遮罩值 `1 << 23`）。
- 完整的目錄（含屬性數據）可在 [Deployables](/content/deployables/) 中查看。

## 膠囊 ↔ 物件配對

可部署物以成對形式存在：**膠囊**（capsule，即攜帶在物品欄中的項目）和
**物件**（object，即出現在區域中的單位）。配對關係由資料庫欄位
`entitydefaults.targetdefinition` 定義，且為**雙向**的：

- capsule.`targetdefinition` → 物件的定義
- object.`targetdefinition` → 膠囊的定義

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` 可解析
任一方向的配對。範例配對：`def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`。

## 部署流程

`ItemDeployer.cs`（非 PBS 可部署物的基礎類別）：

1. `Deploy(zone, player)` 計算玩家中心位置的生成座標。
2. `CreateDeployableItem` 建立**物件**單位（而非膠囊）並儲存。
3. 渲染一段 5 秒的「部署光束」。
4. 交易提交後，物件被加入區域（`ZoneEnterType.Deploy`）。

PBS 結構使用獨立的 `PBSDeployer` / `PBSObjectHelper` 路徑；當 PBS
物件被拆解時，它會從區域中移除，而其**膠囊**會被加入掉落物
（`PBSObjectHelper.cs`）。

## 執行時聚合欄位

以下欄位（來自 `aggregatevalues`，依定義而異）在物件被放置到區域中後驅動該物件。
消費者已標註於表中。

| 欄位 | 意義 | 消費者 |
|---|---|---|
| `despawn_time` | 已放置物件的存活時間，單位為**毫秒**。到期後單位從區域中移除（若為遠端控制則直接摧毀）。 | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → 套用 `effect_despawn_timer`。 |
| `armor_max` | 已放置單位的最大護甲值。 | 單位戰鬥 |
| `resist_chemical/explosive/kinetic/thermal` | 傷害抗性。 | 單位戰鬥 |
| `signature_radius` | 掃描訊號特徵半徑。 | 掃描器 / 隱形 |
| `stealth_strength` | 隱形強度。 | 掃描器 / 隱形 |
| `effect_*`（例如 `effect_field_sensor_strength_modifier`、`effect_stealth_strength_modifier`、`effect_field_reactor_radiation_modifier`） | 由物件發出的場效應修正值。 | `FieldEffectGenerators/*`（例如 `FieldEccmEffectGeneratorDeployer` 透過 `GetPropertyModifier` 讀取 `despawn_time` 及 effect 欄位）。 |
| `mobile_teleport_cooldown` | 行動傳送器兩次使用之間的冷卻時間（毫秒）。 | 行動傳送器單位 |
| `trigger_mass` | 觸發地雷的質量閾值。 | 地雷單位 |
| `damage_kinetic/thermal/explosive/chemical/toxic` | 地雷對各屬性造成的傷害。 | 地雷單位 |

`despawn_time` 是核心欄位：每個已放置物件都會獲得一個
`UnitDespawnHelper`，其 `IntervalTimer`（650 毫秒跳動）會重新檢查
`effect_despawn_timer` 效果，當該效果消失時即執行消失策略。

### 實例 — `def_mobile_field_eccm`

取自 [Deployables](/content/deployables/)：

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (object) / 50 (armored capsule)
despawn_time=900000          → 900 秒 = 15 分鐘存活時間
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

部署膠囊後，物件會在機器人所在位置生成；它存活 15 分鐘，
擁有 15,000 護甲及 150% 抗性，存活期間會發出場效應，使感測器
強度提升 100%，並降低反應爐輻射 25%。

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