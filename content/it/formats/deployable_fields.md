---
title: "Campi dei deployable"
description: "Identificazione dei deployable, accoppiamento capsula-oggetto e campi aggregati che gestiscono gli oggetti piazzati nelle zone."
weight: 40
---

# Campi dei deployable

Un **deployable** (dispositivo piazzabile) è un oggetto che può essere posizionato in una zona come unità (teletrasporti mobili, mine terrestri, emettitori di effetti di campo, strutture PBS, …). Viene identificato tramite flag, accoppiato a una definizione capsula↔oggetto e gestito a runtime da campi aggregati.

## Identificazione

- **Category flag** `cf_deployable_structure` = `0x998` (bitmask) su
  `entitydefaults.categoryflags` — il set scansionato dal registro delle entità per registrare
  le classi di elementi deployer (`EntitiesModule.cs`, ad es. `PlantSeedDeployer` è registrato
  per questa categoria).
- **Attribute flag** `deployable` = bit **23** su `entitydefaults.attributeflags`
  (maschera `1 << 23`).
- Il catalogo completo (con statistiche) è generato in [Deployables](/content/deployables/).

## Accoppiamento capsula ↔ oggetto

I deployable si presentano in coppia: una **capsula** (l'oggetto trasportato nell'inventario) e l'**oggetto** (l'unità che appare nella zona). La coppia è definita dalla colonna del database `entitydefaults.targetdefinition`, che è **bidirezionale**:

- capsula.`targetdefinition` → definizione dell'oggetto
- oggetto.`targetdefinition` → definizione della capsula

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` risolvono entrambe le direzioni. Esempio di coppia: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Flusso di piazzamento (deployment)

`ItemDeployer.cs` (base per deployable non-PBS):

1. `Deploy(zone, player)` calcola la posizione di spawn al centro del giocatore.
2. `CreateDeployableItem` crea l'unità **oggetto** (non la capsula) e la salva.
3. Viene visualizzato un "raggio di piazzamento" della durata di 5 secondi.
4. Al commit della transazione, l'oggetto viene aggiunto alla zona (`ZoneEnterType.Deploy`).

Le strutture PBS utilizzano il percorso separato `PBSDeployer` / `PBSObjectHelper`; quando un oggetto PBS viene decostruito, viene rimosso dalla zona e la sua **capsula** viene aggiunta al bottino (`PBSObjectHelper.cs`).

## Campi aggregati a runtime

Questi campi (da `aggregatevalues`, per definizione) guidano un oggetto piazzato una volta che si trova nella zona. È indicato anche il relativo consumer.

| Campo | Significato | Consumer |
|---|---|---|
| `despawn_time` | Durata di vita dell'oggetto piazzato, in **millisecondi**. Alla scadenza l'unità viene rimossa dalla zona (o distrutta, se controllata da remoto). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → applica `effect_despawn_timer`. |
| `armor_max` | Armatura massima dell'unità piazzata. | combattimento unità |
| `resist_chemical/explosive/kinetic/thermal` | Resistenze ai danni. | combattimento unità |
| `signature_radius` | Dimensione della segnatura radar/scansione. | scanner / occultamento |
| `stealth_strength` | Efficacia dell'occultamento (stealth strength). | scanner / occultamento |
| `effect_*` (ad es. `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Modificatori degli effetti di campo emessi dall'oggetto. | `FieldEffectGenerators/*` (ad es. `FieldEccmEffectGeneratorDeployer` legge `despawn_time` e i campi degli effetti tramite `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Tempo di ricarica (ms) tra gli utilizzi di un teletrasporto mobile. | unità teletrasporto mobile |
| `trigger_mass` | Soglia di massa che innesca l'attivazione di una mina terrestre. | unità mina terrestre |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Danno inflitto da una mina terrestre per ciascun attributo. | unità mina terrestre |

`despawn_time` è il campo fondamentale: ogni oggetto piazzato riceve un `UnitDespawnHelper` il cui `IntervalTimer` (tick di 650 ms) ricontrolla l'effetto `effect_despawn_timer` e, una volta esaurito, esegue la strategia di despawn.

### Esempio pratico — `def_mobile_field_eccm`

Da [Deployables](/content/deployables/):

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (object) / 50 (armored capsule)
despawn_time=900000          → 900 s = 15 min lifetime
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Piazzare la capsula genera l'oggetto nella posizione del robot; questo rimane attivo per 15 minuti, possiede 15.000 di armatura con il 150% di resistenza e, finché è attivo, emette un campo che aumenta la potenza dei sensori del 100% e riduce le radiazioni del reattore del 25%.

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