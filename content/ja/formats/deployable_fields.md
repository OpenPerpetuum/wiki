---
title: "配置可能オブジェクトのフィールド"
description: "配置可能オブジェクトの識別方法、カプセルとオブジェクトのペアリング、配置済みゾーンオブジェクトを駆動する集約フィールドについて。"
weight: 40
---

# 配置可能オブジェクトのフィールド

**配置可能オブジェクト**とは、ゾーンにユニットとして配置できるアイテムです（モバイルテレポート、
地雷、フィールドエフェクトエミッター、PBS 構造体など）。フラグで識別され、
カプセル↔オブジェクトの定義とペアリングされ、実行時には集約フィールドによって駆動されます。

## 識別

- **カテゴリフラグ** `cf_deployable_structure` = `0x998`（ビットマスク）が
  `entitydefaults.categoryflags` に設定されています。エンティティレジストリがこの集合をスキャンして、
  デプロイヤーアイテムクラスを登録するためのセットです（`EntitiesModule.cs`、例：`PlantSeedDeployer` はこのカテゴリに登録されています）。
- **属性フラグ** `deployable` = `entitydefaults.attributeflags` のビット **23**
  （マスク `1 << 23`）。
- 完全なカタログ（ステータス付き）は [配置可能オブジェクト](/content/deployables/) で生成されています。

## カプセル ↔ オブジェクトのペアリング

配置可能オブジェクトはペアで存在します：**カプセル**（インベントリに所持するアイテム）と
**オブジェクト**（ゾーンに出現するユニット）です。このペアは DB カラム
`entitydefaults.targetdefinition` で表され、**双方向**です：

- capsule.`targetdefinition` → オブジェクトの定義
- object.`targetdefinition` → カプセルの定義

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` がどちらの方向も解決します。
ペアの例：`def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`。

## 配置フロー

`ItemDeployer.cs`（PBS 以外の配置可能オブジェクトのベース）：

1. `Deploy(zone, player)` がプレイヤーの中心を基準にスポーン位置を計算します。
2. `CreateDeployableItem` が**オブジェクト**ユニット（カプセルではなく）を構築して保存します。
3. 5 秒間の「配置ビーム」が描画されます。
4. トランザクションのコミット時に、オブジェクトがゾーンに追加されます（`ZoneEnterType.Deploy`）。

PBS 構造体は別の `PBSDeployer` / `PBSObjectHelper` パスを使用します。PBS
オブジェクトが解体されると、ゾーンから削除され、その**カプセル**が戦利品に追加されます
（`PBSObjectHelper.cs`）。

## 実行時集約フィールド

これらのフィールド（定義ごとの `aggregatevalues` から）は、オブジェクトがゾーンに配置された後にその動作を駆動します。使用箇所を示します。

| フィールド | 意味 | 使用箇所 |
|---|---|---|
| `despawn_time` | 配置済みオブジェクトの生存時間（**ミリ秒**）。期限が来ると、ユニットはゾーンから削除されます（リモート制御の場合は破壊されます）。 | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → `effect_despawn_timer` を適用。 |
| `armor_max` | 配置済みユニットの最大アーマー。 | ユニット戦闘 |
| `resist_chemical/explosive/kinetic/thermal` | ダメージ耐性。 | ユニット戦闘 |
| `signature_radius` | スキャンシグネチャサイズ。 | スキャナー / ステルス |
| `stealth_strength` | ステルス強度。 | スキャナー / ステルス |
| `effect_*`（例：`effect_field_sensor_strength_modifier`、`effect_stealth_strength_modifier`、`effect_field_reactor_radiation_modifier`） | オブジェクトが発するフィールドエフェクト修正値。 | `FieldEffectGenerators/*`（例：`FieldEccmEffectGeneratorDeployer` は `GetPropertyModifier` を通じて `despawn_time` とエフェクトフィールドを読み取ります）。 |
| `mobile_teleport_cooldown` | モバイルテレポートの使用間隔（ミリ秒）。 | モバイルテレポートユニット |
| `trigger_mass` | 地雷のトリガーをアームする質量のしきい値。 | 地雷ユニット |
| `damage_kinetic/thermal/explosive/chemical/toxic` | 地雷が属性ごとに与えるダメージ。 | 地雷ユニット |

`despawn_time` が決定的なフィールドです：配置されたすべてのオブジェクトには
`UnitDespawnHelper` が付与され、その `IntervalTimer`（650 ms 間隔）が
`effect_despawn_timer` エフェクトを再チェックし、エフェクトが消えたらデスポーン処理を実行します。

### 具体例 — `def_mobile_field_eccm`

[配置可能オブジェクト](/content/deployables/) より：

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (オブジェクト) / 50 (装甲カプセル)
despawn_time=900000          → 900 秒 = 15 分間
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

カプセルを配置すると、ロボットの位置にオブジェクトがスポーンします。15 分間生存し、
アーマー 15,000 と 150% の耐性を備え、生存中はセンサー強度を 100% 向上させ、
リアクター放射線を 25% 低減するフィールドを発します。

<!-- 開発者向け注記: EntitiesModule.cs:449 (ByCategoryFlags<PlantSeedDeployer>
     cf_deployable_structure); ExportedTypes/CategoryFlags.cs (cf_deployable_structure
     = 0x998), ExportedTypes/AttributeFlags.cs (deployable = 23);
     EntityFramework/DefinitionConfig.cs (targetdefinition カラム, TargetEntityDefault);
     Deployers/ItemDeployer.cs (Deploy フロー, 5 秒ビーム, ZoneEnterType.Deploy);
     Zones/PBS/PBSHelper.cs (カプセル<->オブジェクト), Zones/PBS/PBSObjectHelper.cs
     (解体 -> カプセル戦利品); Units/UnitDespawnHelper.cs (despawn_time ->
     effect_despawn_timer, 650ms 間隔, CancellableDespawnHelper（要塞用）);
     Zones/FieldEffectGenerators/FieldEccmEffectGeneratorDeployer.cs
     (GetPropertyModifier(AggregateField.despawn_time) + effect_* フィールド). -->