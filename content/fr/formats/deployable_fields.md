---
title: "Champs des déployables"
description: "Identification des déployables, appariement capsule-objet et champs agrégés pilotant les objets placés en zone."
weight: 40
---

# Champs des déployables

Un **déployable** (deployable) est un objet pouvant être placé dans une zone en tant qu'unité (téléporteurs mobiles,
mines terrestres, émetteurs d'effets de zone, structures PBS, …). Il est identifié par des drapeaux (flags),
associé à une définition capsule ↔ objet, et piloté au moment de l'exécution par des champs agrégés.

## Identification

- **Drapeau de catégorie** `cf_deployable_structure` = `0x998` (masque binaire) sur
  `entitydefaults.categoryflags` — l'ensemble analysé par le registre d'entités pour enregistrer
  les classes d'objets déployeurs (`EntitiesModule.cs`, par ex. `PlantSeedDeployer` est enregistré
  pour cette catégorie).
- **Drapeau d'attribut** `deployable` = bit **23** sur `entitydefaults.attributeflags`
  (masque `1 << 23`).
- Le catalogue complet (avec statistiques) est généré sous [Déployables](/fr/content/deployables/).

## Appariement capsule ↔ objet

Les déployables fonctionnent par paires : une **capsule** (l'objet transporté dans l'inventaire) et
l'**objet** (l'unité qui apparaît dans la zone). La paire est définie dans la colonne de base de données
`entitydefaults.targetdefinition`, qui est **bidirectionnelle** :

- capsule.`targetdefinition` → la définition de l'objet
- objet.`targetdefinition` → la définition de la capsule

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper` résolvent dans les deux sens.
Exemple de paire : `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## Déroulement du déploiement

`ItemDeployer.cs` (base pour les déployables non-PBS) :

1. `Deploy(zone, player)` calcule la position d'apparition au centre du joueur.
2. `CreateDeployableItem` construit l'unité **objet** (et non la capsule) et la sauvegarde.
3. Un « rayon de déploiement » de 5 secondes est affiché.
4. Lors de la validation de la transaction, l'objet est ajouté à la zone (`ZoneEnterType.Deploy`).

Les structures PBS utilisent le chemin distinct `PBSDeployer` / `PBSObjectHelper` ; lorsqu'un objet PBS
est déconstruit, il est retiré de la zone et sa **capsule** est ajoutée au butin (`PBSObjectHelper.cs`).

## Champs agrégés d'exécution

Ces champs (issus de `aggregatevalues`, par définition) pilotent un objet placé une fois qu'il est
présent dans la zone. Le consommateur de chaque champ est indiqué.

| Champ | Signification | Consommateur |
|---|---|---|
| `despawn_time` | Durée de vie de l'objet placé, en **millisecondes**. À expiration, l'unité est retirée de la zone (ou détruite si contrôlée à distance). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → applique `effect_despawn_timer`. |
| `armor_max` | Blindage maximal de l'unité placée. | combat d'unité |
| `resist_chemical/explosive/kinetic/thermal` | Résistances aux dégâts. | combat d'unité |
| `signature_radius` | Rayon de signature de détection. | scanner / furtivité |
| `stealth_strength` | Puissance de furtivité. | scanner / furtivité |
| `effect_*` (par ex. `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | Modificateurs d'effet de zone émis par l'objet. | `FieldEffectGenerators/*` (par ex. `FieldEccmEffectGeneratorDeployer` lit `despawn_time` et les champs d'effet via `GetPropertyModifier`). |
| `mobile_teleport_cooldown` | Temps de recharge (ms) entre utilisations d'un téléporteur mobile. | unité téléporteur mobile |
| `trigger_mass` | Seuil de masse qui déclenche une mine terrestre. | unité mine terrestre |
| `damage_kinetic/thermal/explosive/chemical/toxic` | Dégâts infligés par une mine selon l'attribut. | unité mine terrestre |

`despawn_time` est le champ clé : chaque objet placé dispose d'un `UnitDespawnHelper` dont le `IntervalTimer` (tick de 650 ms) revérifie l'effet `effect_despawn_timer` et, lorsque celui-ci a disparu, exécute la stratégie de disparition (despawn).

### Exemple concret — `def_mobile_field_eccm`

Issu de [Déployables](/fr/content/deployables/) :

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (objet) / 50 (capsule blindée)
despawn_time=900000          → 900 s = 15 min de durée de vie
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

Le déploiement de la capsule fait apparaître l'objet à la position du robot ; il reste actif 15 minutes, possède 15 000 de blindage avec 150 % de résistance, et émet un champ qui augmente la puissance des capteurs de 100 % et réduit le rayonnement du réacteur de 25 %.

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
