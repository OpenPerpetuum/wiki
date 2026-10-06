---
title: "Champs des minerais"
description: "Format du fichier de règles des minerais (GenXY), chaque champ avec type, valeur par défaut et consommateur."
weight: 21
---

# Champs des minerais

Les minerais sont définis par espèce dans la base de données. Les données de
minerais sont chargées depuis la table `minerals` et les `entitydefaults`.

## Champs de données

| Champ | Type | Description |
|---|---|---|
| `definition` | int | ID de la définition |
| `definitionname` | string | Nom de la définition (ex: `def_titanium`) |
| `type` | string | Type de minerai (solide, liquide) |
| `charge` | # | Charge du minerai (densité) |
| `mass` | # | Masse du minerai |
| `value` | # | Valeur du minerai |

## Types de minerais

| Type | Description |
|---|---|
| **Solide** | S'épuise tuile par tuile |
| **Liquide** | Puisé en continu depuis le champ |

## Minerais disponibles

Les minerais sont listés dans [Contenu → Minerais](/content/ores/). Chaque minerai a :

- Un **nom** (ex: Titanium, Epriton, Fluxore)
- Un **type** (solide ou liquide)
- Une **charge** (densité)
- Une **masse**
- Une **valeur**
- Des **composants** (pour la production)

## Notes pratiques

- **Les minerais solides** s'épuisent tuile par tuile.
- **Les minerais liquides** sont plus faciles à miner (continus).
- **La charge** détermine la densité du minerai.
- **La valeur** détermine le prix du minerai.
