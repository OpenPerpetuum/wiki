---
title: "Поля развёртываемых объектов"
description: "Идентификация развёртываемых объектов, связывание капсулы с объектом и агрегатные поля, управляющие размещёнными объектами в зоне."
weight: 40
---

# Поля развёртываемых объектов

**Развёртываемый объект (deployable)** — это предмет, который может быть размещён в зоне как отдельный юнит (мобильные телепорты, мины, излучатели эффектов поля, PBS-структуры и т. д.). Он идентифицируется с помощью флагов, связывается через пару определений «капсула ↔ объект» и управляется во время выполнения агрегатными полями.

## Идентификация

- **Флаг категории** `cf_deployable_structure` = `0x998` (битовая маска) в `entitydefaults.categoryflags` — набор, сканируемый реестром сущностей для регистрации классов развёртываемых предметов (`EntitiesModule.cs`, например, `PlantSeedDeployer` зарегистрирован для этой категории).
- **Флаг атрибута** `deployable` = бит **23** в `entitydefaults.attributeflags` (маска `1 << 23`).
- Полный каталог (с характеристиками) сформирован на странице [Deployables](/content/deployables/).

## Связка капсулы и объекта (Capsule ↔ object pairing)

Развёртываемые объекты существуют парами: **капсула** (предмет, переносимый в инвентаре) и **объект** (юнит, появляющийся в зоне). Связь задаётся колонкой базы данных `entitydefaults.targetdefinition`, которая является **двунаправленной**:

- капсула.`targetdefinition` → определение объекта
- объект.`targetdefinition` → определение капсулы

Методы `PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` разрешают связь в обоих направлениях. Пример пары: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Процесс развёртывания (Deployment flow)

`ItemDeployer.cs` (базовый класс для развёртываемых объектов, не относящихся к PBS):

1. `Deploy(zone, player)` вычисляет позицию появления в центре координат игрока.
2. `CreateDeployableItem` создаёт юнит **объекта** (не капсулу) и сохраняет его.
3. Отрисовывается 5-секундный «луч развёртывания» (deploy beam).
4. При фиксации транзакции объект добавляется в зону (`ZoneEnterType.Deploy`).

PBS-структуры используют отдельную ветку логики `PBSDeployer` / `PBSObjectHelper`; когда PBS-объект демонтируется, он удаляется из зоны, а его **капсула** добавляется в лут (`PBSObjectHelper.cs`).

## Агрегатные поля во время выполнения (Runtime aggregate fields)

Эти поля (из таблицы `aggregatevalues`, для каждого определения) управляют размещённым объектом после его появления в зоне. Также указан компонент-потребитель данных.

| Поле | Назначение | Потребитель |
|---|---|---|
| `despawn_time` | Время жизни размещённого объекта, **миллисекунды**. По истечении юнит удаляется из зоны (или уничтожается, если управляется удалённо). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → накладывает `effect_despawn_timer`. |
| `armor_max` | Максимальная броня размещённого юнита. | unit combat |
| `resist_chemical/explosive/kinetic/thermal` | Сопротивления урону. | unit combat |
| `signature_radius` | Радиус сигнатуры сканирования. | scanner / stealth |
| `stealth_strength` | Сила маскировки (стелса). | scanner / stealth |
| `effect_*` (например, `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Модификаторы эффектов поля, излучаемые объектом. | `FieldEffectGenerators/*` (например, `FieldEccmEffectGeneratorDeployer` считывает `despawn_time` и поля эффектов через `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Время перезарядки (мс) между использованиями мобильного телепорта. | mobile teleport unit |
| `trigger_mass` | Порог массы, приводящий взрыватель мины в боевое положение. | landmine unit |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Урон мины по каждому типу атрибута. | landmine unit |

`despawn_time` является определяющим полем: каждый размещённый объект получает `UnitDespawnHelper`, чей `IntervalTimer` (с тактом 650 мс) проверяет эффект `effect_despawn_timer` и, когда он исчезает, запускает стратегию исчезновения (деспавна).

### Практический пример — `def_mobile_field_eccm`

Из раздела [Deployables](/content/deployables/):

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (object) / 50 (armored capsule)
despawn_time=900000          → 900 s = 15 min lifetime
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Развёртывание капсулы создаёт объект на позиции робота; он живёт 15 минут, имеет 15 000 брони со 150% сопротивлений, и пока активен, излучает поле, увеличивающее силу сенсоров на 100% и снижающее радиацию реактора на 25%.

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