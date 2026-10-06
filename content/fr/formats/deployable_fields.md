---
title: "Champs des déplaçables"
description: "Format des données des déplaçables, types de structures, et les règles de démontage."
weight: 23
---

# Champs des déplaçables

Les **déplaçables** sont des objets placés dans les zones. Ils incluent les
structures PBS, les téléporteurs, les kiosques, et d'autres objets.

## Types de déplaçables

| Type | Description |
|---|---|
| **PBS** | Stations de base de pouvoir |
| **Téléporteur** | Structures de téléportation |
| **Kiosque** | Structures de mission |
| **Terminal** | Terminaux de terrain |
| **Porte** | Portes de zone |
| **Turret** | Tourelles de défense |

## Champs de données

| Champ | Type | Description |
|---|---|---|
| `definition` | int | ID de la définition |
| `definitionname` | string | Nom de la définition |
| `type` | string | Type de déplaçable |
| `position` | (x, y) | Position dans la zone |
| `owner` | int | ID du propriétaire (corporation) |
| `health` | # | Points de vie |
| `energy` | # | Énergie |

## Démontage

Certains déplaçables peuvent être **démontés** pour des matériaux :

- Le démontage **détruit** l'objet.
- Les matériaux sont ajoutés à la **cargaison** du robot.
- Les rendements sont définis par type dans la base de données.

## Notes pratiques

- **Les déplaçables sont des objets** — ils ont des stats et des composants.
- **Le démontage est destructif** — l'objet est détruit.
- **Les rendements varient** selon le type de déplaçable.
- **Les PBS sont des déplaçables** — voir [PBS](/fr/features/pbs/).
