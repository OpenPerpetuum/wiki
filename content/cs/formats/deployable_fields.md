---
title: "Pole nasaditelných položek"
description: "Jak jsou nasaditelné položky identifikovány, párování kapsle a objektu a agregační pole, která řídí umístěné zónové objekty."
weight: 40
---

# Pole nasaditelných položek

**Nasaditelná položka** je předmět, který lze do zóny umístit jako jednotku (mobilní teleporty,
minové pasti, emitory poleových efektů, PBS struktury, …). Je identifikována příznaky,
spárována s definicí kapsle↔objektu a v době běhu řízena agregačními poli.

## Identifikace

- **Příznak kategorie** `cf_deployable_structure` = `0x998` (bitová maska) na
  `entitydefaults.categoryflags` — množina, kterou rejstřík entit skenuje pro registraci
  tříd položek nasazovačů (`EntitiesModule.cs`, např. `PlantSeedDeployer` je registrován
  pro tuto kategorii).
- **Příznak atributu** `deployable` = bit **23** na `entitydefaults.attributeflags`
  (maska `1 << 23`).
- Úplný katalog (se statistikami) je generován na stránce [Deployables](/content/deployables/).

## Párování kapsle ↔ objektu

Nasaditelné položky přicházejí v párech: **kapsle** (položka, kterou nosíte v inventáři) a
**objekt** (jednotka, která se objeví v zóně). Párem je sloupec DB
`entitydefaults.targetdefinition`, který je **obousměrný**:

- kapsle.`targetdefinition` → definice objektu
- objekt.`targetdefinition` → definice kapsle

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` vyřeší
kterýkoli směr. Příklad páru: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Průběh nasazení

`ItemDeployer.cs` (základ pro nasaditelné položky, které nejsou PBS):

1. `Deploy(zone, player)` vypočítá pozici zrodu ve středu hráče.
2. `CreateDeployableItem` vytvoří jednotku **objektu** (ne kapsle) a uloží ji.
3. Je vykreslen 5sekundový nasazovací paprsek.
4. Při ukončení transakce je objekt přidán do zóny (`ZoneEnterType.Deploy`).

PBS struktury používají samostatnou cestu `PBSDeployer` / `PBSObjectHelper`; když je PBS
objekt demontován, je odstraněn ze zóny a jeho **kapsle** je přidána do kořisti
(`PBSObjectHelper.cs`).

## Agregační pole v době běhu

Tato pole (z `aggregatevalues`, podle definice) řídí umístěný objekt, jakmile je
v zóně. Spotřebitel je uveden.

| Pole | Význam | Spotřebitel |
|---|---|---|
| `despawn_time` | Doba života umístěného objektu, **milisekundy**. Po vypršení je jednotka odstraněna ze zóny (nebo zničena, pokud je ovládána na dálku). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → aplikuje `effect_despawn_timer`. |
| `armor_max` | Maximální brnění umístěné jednotky. | boj jednotky |
| `resist_chemical/explosive/kinetic/thermal` | Odolnosti vůči poškození. | boj jednotky |
| `signature_radius` | Velikost signatury skenování. | skener / skrytost |
| `stealth_strength` | Síla skrytosti. | skener / skrytost |
| `effect_*` (např. `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Modifikátory poleových efektů emitované objektem. | `FieldEffectGenerators/*` (např. `FieldEccmEffectGeneratorDeployer` čte `despawn_time` a pole efektů přes `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Doběh (ms) mezi použitími mobilního teleportu. | jednotka mobilního teleportu |
| `trigger_mass` | Hmotnostní práh, který aktivuje spouštěč minové pasti. | jednotka minové pasti |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Poškození, které minová past způsobí podle atributu. | jednotka minové pasti |

`despawn_time` je určujícím polem: každý umístěný objekt dostane
`UnitDespawnHelper`, jehož `IntervalTimer` (cyklus 650 ms) znovu kontroluje
efekt `effect_despawn_timer` a když zmizí, spustí strategii odstranění.

### Příklad z praxe — `def_mobile_field_eccm`

Z [Deployables](/content/deployables/):

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (objekt) / 50 (brněná kapsle)
despawn_time=900000          → 900 s = 15 min doba života
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Nasazení kapsle zrodí objekt na pozici robota; žije 15 minut,
má 15 000 brnění s 150 % odolností a po celou dobu svého života emituje pole, které zvyšuje
sílu senzorů o 100 % a snižuje radiaci reaktoru o 25 %.

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