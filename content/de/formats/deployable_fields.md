---
title: "Deployable-Felder"
description: "Identifikation platzierbarer Objekte, Kapsel-Objekt-Paarung und die Aggregatfelder für platzierte Einheiten."
weight: 40
---

# Deployable-Felder

Ein **Deployable** ist ein Gegenstand, der als Einheit in einer Zone platziert werden kann (mobile Teleporter, Landminen, Feldeffekt-Emitter, PBS-Strukturen usw.). Es wird über Flags identifiziert, ist über eine Kapsel-Objekt-Definition gepaart und wird zur Laufzeit von Aggregatfeldern gesteuert.

## Identifikation

- **Kategorie-Flag (Category flag)** `cf_deployable_structure` = `0x998` (Bitmaske) in `entitydefaults.categoryflags` — diese Menge durchsucht die Entitäten-Registrierung, um Deployer-Gegenstandsklassen zu registrieren (`EntitiesModule.cs`, z. B. ist `PlantSeedDeployer` für diese Kategorie registriert).
- **Attribut-Flag (Attribute flag)** `deployable` = Bit **23** in `entitydefaults.attributeflags` (Maske `1 << 23`).
- Der vollständige Katalog (mit Werten) wird unter [Deployables](/content/deployables/) generiert.

## Paarung von Kapsel ↔ Objekt

Platzierbare Objekte treten paarweise auf: eine **Kapsel** (der Gegenstand im Inventar) und das **Objekt** (die tatsächlich in der Zone platzierte Einheit). Das Paar wird in der DB-Spalte `entitydefaults.targetdefinition` definiert, die **bidirektional** ist:

- Kapsel.`targetdefinition` → Definition des Objekts
- Objekt.`targetdefinition` → Definition der Kapsel

`PBSHelper.GetPBSObjectDefinitionFromCapsule` und `ItemDeployerHelper` lösen beide Richtungen auf. Beispielpaar: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Ablauf der Platzierung (Deployment flow)

`ItemDeployer.cs` (Basis für Nicht-PBS-Deployables):

1. `Deploy(zone, player)` berechnet die Spawn-Position im Zentrum des Spielers.
2. `CreateDeployableItem` erstellt die **Objekt**-Einheit (nicht die Kapsel) und speichert sie.
3. Ein 5-sekündiger „Platzierungsstrahl“ wird dargestellt.
4. Beim Datenbank-Commit wird das Objekt der Zone hinzugefügt (`ZoneEnterType.Deploy`).

PBS-Strukturen nutzen den separaten Pfad `PBSDeployer` / `PBSObjectHelper`; wird ein PBS-Objekt abgebaut, wird es aus der Zone entfernt und seine **Kapsel** als Beute hinterlassen (`PBSObjectHelper.cs`).

## Aggregatfelder zur Laufzeit

Diese Felder (aus `aggregatevalues`, pro Definition) steuern ein platziertes Objekt in der Zone. Der jeweilige Verwender ist angegeben.

| Feld | Bedeutung | Verwender |
|---|---|---|
| `despawn_time` | Lebensdauer des platzierten Objekts in **Millisekunden**. Nach Ablauf wird die Einheit aus der Zone entfernt (oder zerstört, falls ferngesteuert). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → wendet `effect_despawn_timer` an. |
| `armor_max` | Maximale Panzerung der Einheit. | Einheitenkampf |
| `resist_chemical/explosive/kinetic/thermal` | Schadensresistenzen. | Einheitenkampf |
| `signature_radius` | Größe der Sensorsignatur. | Scanner / Tarnung |
| `stealth_strength` | Tarnstärke. | Scanner / Tarnung |
| `effect_*` (z. B. `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Vom Objekt abgestrahlte Feldeffekt-Modifikatoren. | `FieldEffectGenerators/*` (z. B. liest `FieldEccmEffectGeneratorDeployer` die Felder `despawn_time` und die Effektfelder über `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Abklingzeit (ms) zwischen Nutzungen eines mobilen Teleporters. | Mobiler Teleporter |
| `trigger_mass` | Masseschwelle, die eine Landmine auslöst. | Landmine |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Schaden, den eine Landmine pro Attribut verursacht. | Landmine |

`despawn_time` ist das zentrale Feld: Jedes platzierte Objekt erhält einen `UnitDespawnHelper`, dessen `IntervalTimer` (650-ms-Takt) den Effekt `effect_despawn_timer` prüft und bei dessen Ablauf die Despawn-Strategie ausführt.

### Rechenbeispiel — `def_mobile_field_eccm`

Aus [Deployables](/content/deployables/):

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (Objekt) / 50 (gepanzerte Kapsel)
despawn_time=900000          → 900 s = 15 Minuten Lebensdauer
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Das Platzieren der Kapsel spawnt das Objekt an der Position des Roboters; es existiert 15 Minuten, verfügt über 15.000 Panzerung mit 150 % Resistenz und erzeugt ein Feld, das die Sensorstärke um 100 % erhöht und die Reaktorstrahlung um 25 % verringert.
