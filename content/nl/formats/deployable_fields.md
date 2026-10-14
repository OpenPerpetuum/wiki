---
title: "Velden van inzetbare objecten"
description: "Hoe inzetbare objecten worden geïdentificeerd, capsule-object koppeling, en de aggregaatvelden die geplaatste zone-objecten sturen."
weight: 40
---

# Velden van inzetbare objecten

Een **inzetbaar object** is een item dat als eenheid in een zone kan worden geplaatst (mobiele teleporters,
landmijnen, veld-effectemitters, PBS-structuren, …). Het wordt geïdentificeerd door vlaggen,
gekoppeld aan een capsule↔object-definitie, en op runtime aangestuurd door aggregaatvelden.

## Identificatie

- **Categorievlag** `cf_deployable_structure` = `0x998` (bitmasker) op
  `entitydefaults.categoryflags` — de set die het entiteitsregister scant om
  inzetbare itemklassen te registreren (`EntitiesModule.cs`, bijv. `PlantSeedDeployer`
  is geregistreerd voor deze categorie).
- **Attribuutvlag** `deployable` = bit **23** op `entitydefaults.attributeflags`
  (masker `1 << 23`).
- De volledige catalogus (met statistieken) wordt gegenereerd op [Deployables](/content/deployables/).

## Capsule ↔ object koppeling

Inzetbare objecten komen in paren voor: een **capsule** (het item dat je in je inventaris draagt) en het
**object** (de eenheid die in de zone verschijnt). Het paar is de DB-kolom
`entitydefaults.targetdefinition`, die **bidirectioneel** is:

- capsule.`targetdefinition` → de definitie van het object
- object.`targetdefinition` → de definitie van de capsule

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` lossen beide
richtingen op. Voorbeeldpaar: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Inzetflow

`ItemDeployer.cs` (basis voor niet-PBS inzetbare objecten):

1. `Deploy(zone, player)` berekent de spawnpositie op het midden van de speler.
2. `CreateDeployableItem` bouwt de **object**-eenheid (niet de capsule) en slaat deze op.
3. Een 5-seconden "inzetstraal" wordt gerenderd.
4. Bij transactiecommit wordt het object aan de zone toegevoegd (`ZoneEnterType.Deploy`).

PBS-structuren gebruiken het aparte `PBSDeployer` / `PBSObjectHelper`-pad; wanneer een PBS
object wordt gedemonteerd, wordt het uit de zone verwijderd en wordt de **capsule** aan
de loot toegevoegd (`PBSObjectHelper.cs`).

## Runtime aggregaatvelden

Deze velden (uit `aggregatevalues`, per definitie) sturen een geplaatst object zodra het
in de zone is. De consument wordt vermeld.

| Veld | Betekenis | Consument |
|---|---|---|
| `despawn_time` | Levensduur van het geplaatste object, in **milliseconden**. Bij verlopen wordt de eenheid uit de zone verwijderd (of gedood, indien op afstand bestuurd). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → past `effect_despawn_timer` toe. |
| `armor_max` | Maximale pantserwaarde van de geplaatste eenheid. | eenheidsgevecht |
| `resist_chemical/explosive/kinetic/thermal` | Schade-resistenties. | eenheidsgevecht |
| `signature_radius` | Grootte van de scanningsignatuur. | scanner / stealth |
| `stealth_strength` | Stealth-sterkte. | scanner / stealth |
| `effect_*` (bijv. `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Veld-effectmodificatoren die door het object worden uitgezonden. | `FieldEffectGenerators/*` (bijv. `FieldEccmEffectGeneratorDeployer` leest `despawn_time` en de effectvelden via `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Cooldown (ms) tussen gebruik van een mobiele teleporter. | mobiele teleporter-eenheid |
| `trigger_mass` | Massadrempel die een landmijntrigger activeert. | landmijn-eenheid |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Schade die een landmijn toebrengt per attribuut. | landmijn-eenheid |

`despawn_time` is het bepalende veld: elk geplaatst object krijgt een
`UnitDespawnHelper` waarvan de `IntervalTimer` (650 ms-tick) de
`effect_despawn_timer`-effect controleert en, wanneer deze is verdwenen, de despawn-strategie uitvoert.

### Werkvoorbeeld — `def_mobile_field_eccm`

Van [Deployables](/content/deployables/):

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (object) / 50 (gepantserde capsule)
despawn_time=900000          → 900 s = 15 min levensduur
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Bij het inzetten van de capsule wordt het object op de positie van de robot gespawned; het leeft 15 minuten,
heeft 15.000 pantser met 150% resistentie, en zendt tijdens zijn levensduur een veld uit dat de sensorsterkte
met 100% verhoogt en de reactorstraling met 25% verlaagt.

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