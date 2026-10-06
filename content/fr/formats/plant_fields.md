---
title: "Champs des plantes"
description: "Format du fichier de règles des plantes (GenXY), chaque champ de règle avec type, valeur par défaut et consommateur, plus la machine à états de croissance."
weight: 20
---

# Champs des plantes

Le comportement des plantes est défini par espèce par un **fichier de règles** (texte
plain) sous `$GameRoot/plantrules/`. Les fichiers qui appartiennent à une zone sont la
cartographie DB `plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset` ; le
chargement et la fusion sont `PlantRuleLoader.cs`, et la mapping champ-objet est
`PlantRule.cs`.

## Format du fichier

Une `key=value` par ligne ; les commentaires de style `//` sont retirés. Les valeurs
utilisent les **caractères de jetons GenXY** (`GenxyReader.cs` — le premier caractère
sélectionne le type et la base du nombre) :

| Jeton | Analysé comme | Exemple |
|---|---|---|
| `#` | Nombre entier décimal | `#100` = 100 |
| `.` | Nombre flottant | `.5` = 0.5 |
| `s` | Chaîne de caractères | `sHello` |
| `b` | Booléen | `b1` = true |
| `c` | Caractère | `cA` = 'A' |

## Champs de règles

| Champ | Type | Défaut | Description |
|---|---|---|---|
| `fertility` | # | 1 | Fréquence d'apparition de la plante |
| `growRate` | # | 1 | Nombre de cycles par stade de croissance |
| `spreading` | # | 1 | Tendance à pousser en grappes |
| `killDistance` | # | 0 | Espacement minimum entre plantes |
| `slope` | # | 0 | Pente maximale du sol |
| `minSlope` | # | 0 | Pente minimale du sol |
| `allowedAltitudeLow` | # | 0 | Altitude minimale |
| `allowedAltitudeHigh` | # | 100 | Altitude maximale |
| `allowedWaterLevelLow` | # | 0 | Distance minimale de la rive |
| `allowedWaterLevelHigh` | # | 100 | Distance maximale de la rive |
| `fruitingState` | # | 3 | Stade de croissance pour la fructification |
| `fruitDefinition` | s | – | Définition du fruit produit |
| `fruitAmount` | # | 1 | Quantité de fruit produite |
| `maxAmount` | # | 100 | Nombre maximum dans une zone de traitement |
| `health` | # | 10 | Points de vie par stade |
| `damageScale` | # | 1 | Résistance aux dégâts |
| `playerSeeded` | b | false | N'existe que si plantée par un joueur |
| `onlyOnUnprotectedZone` | b | false | Ne pousse que sur les zones non protégées |

## Machine à états de croissance

Les plantes progressent à travers une séquence de stades :

1. **Graine** — stade initial
2. **Pousse** — la plante commence à pousser
3. **Jeune** — la plante est en croissance
4. **Mature** — la plante est prête à fructifier
5. **Fructification** — la plante produit du fruit (récoltable)

Chaque stade prend `growRate` cycles de croissance avant d'avancer aléatoirement.
