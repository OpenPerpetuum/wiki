---
title: "Champs de minerais"
description: "Les tables minerals et mineralconfigs, les formules de génération des gisements, le cycle de vie des nœuds et les mécaniques d'extraction."
weight: 30
---

# Champs de minerais

Les données de minerai comportent deux niveaux : **par type** (`minerals` — nature du matériau et rendement d'une extraction) et **par zone et par type** (`mineralconfigs` — nombre de filons, taille, remplissage). L'état d'exécution des filons réside dans la table `mineralnodes`.

## `minerals`

| Colonne | Type | Utilisé par | Signification |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | Valeur ordinale de l'énumération `MaterialType` (1=Titan … 19=DHDT, 0=Undefined). Toutes les jointures utilisent `mineralconfigs.materialtype = minerals.idx`. |
| `name` | varchar | `ToMaterialType()` | Nom du type (« titan », « crude », …). |
| `definition` | int | `MaterialHelper` → objet | Définition de l'objet produit par l'extraction (par ex. titan → def 168). |
| `amount` | int | `DrillerModule` | **Unités de base par extraction** (titan 1500, brut 1500, stermonite 975, liquizite 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = Solide (`OreLayer`), 1 = Liquide (`LiquidLayer`). |
| `enablereffectrequired` | bit | restriction de module | Indique si un effet d'activation est requis pour l'extraction. |
| `geoscandocument` | int | objets de scan | Document de géo-scan pour ce matériau. |

## `mineralconfigs`

Une ligne par (zone, matériau). Consommée par `MineralConfigurationReader` → un `MineralLayer` par ligne :

| Colonne | Type | Utilisé par | Signification |
|---|---|---|---|
| `zoneId` | int | construction de couche | Zone propriétaire. |
| `materialtype` | int | → `minerals.idx` | Le matériau. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | Nombre de filons de ce type maintenus par la zone. |
| `maxtilespernode` | int | générateur | Nombre maximal de tuiles par bloc de filon ; détermine également le rayon d'espacement (ci-dessous). |
| `totalamountpernode` | int | générateur | Quantité totale de matériau dans un filon neuf, répartie sur les tuiles du bloc. |
| `minthreshold` | double | générateur | Remplissage normalisé minimal par tuile (0–1) ; les tuiles inférieures sont ignorées. |

### Formules de génération de filons (`MineralNodeGeneratorBase.cs`)

Pour un nouveau filon d'un type selon la configuration ci-dessus :

```
rayon       = floor( sqrt(maxtilespernode / π) ) × 2
espacement  = la position de départ doit être ≥ 2 × rayon du filon existant le plus proche
bloc        = remplissage par diffusion aléatoire (pinceau de 4 tuiles) jusqu'à maxtilespernode tuiles valides
tuile[i]    = ( bruit[i] / max(bruit) ) normalisé dans [minthreshold, 1]
             × (tuile[i] / Σtuile) × totalamountpernode
             × uniforme(0.9, 1.1)          // fluctuation, puis tronqué en uint
```

Zones d'exclusion autour des bases d'amarrage et des téléporteurs (`KeepOutDist`) : epriton = 100 tuiles (`MINERAL_DISTANCE_FROM_BASE_MIN`), minerai de flux = 200 ; tous les autres types = 0.

### Exemple concret — Brut (id 2) sur Daoden (zone_ASI)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5` :

```
rayon  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → espacement ≥ 80 tuiles
bloc   = jusqu'à 1257 tuiles
tuile  = part ∈ [0.5, 1.0] × (125 000 000 / Σnormalisé) × fluctuation
```

Un filon de brut complet contient 125 M d'unités ; avec l'extraction de base de 1 500 unités par cycle de foreuse, cela représente environ 83 000 cycles d'extraction par filon, et ~666 000 sur l'ensemble des 8 filons de la zone.

## État des filons — `mineralnodes`

| Colonne | Signification |
|---|---|
| `zoneid`, `materialtype` | Zone propriétaire + type |
| `x, y, width, height` | Boîte englobante du filon (zone du bloc) |
| `data` | `uint` compressé par tuile (ordre ligne par ligne dans la boîte) |

Cycle de vie (`MineralNode.cs`, `MineralLayer.cs`) :

- **Chargement** : au démarrage de la zone, tous les filons enregistrés sont chargés ; un filon dont le total est ≤ **1 %** de `totalamountpernode` est supprimé.
- **Réapprovisionnement** : s'il reste moins de `maxnodes` filons, de nouveaux filons sont générés (formule ci-dessus).
- **Expiration** : un filon **intact** expire après **7 jours** (`TimeTracker`) ; le minage réinitialise ce décompte. Un filon dont la valeur maximale de tuile atteint 0 expire également.
- **Persistance** : les filons modifiés sont enregistrés en base de données selon un intervalle de sauvegarde de **30 minutes**.
- **Couplage minerai de flux** : la diminution ou l'expiration d'un filon de `FluxOre` publie `OreNpcSpawnMessage` → le générateur de PNJ l'intercepte (`OreNPCSpawner`).

## Mécaniques d'extraction (`MineralExtractor.cs`, `DrillerModule.cs`)

La quantité extraite correspond à `minerals.amount` modulée par la propriété `mining_amount_modifier` du robot (agrégée depuis `mining_amount_modifier`, `effect_mining_amount_modifier`, `drone_amplification_mining_amount_modifier`, `effect_excavator_mining_amount_modifier`).

- **Solide** (`OreLayer`) : extrait `min(valeur de la tuile, amount)` depuis l'**unique tuile** sur laquelle se trouve le robot.
- **Liquide** (`LiquidLayer`) : draine l'**ensemble du filon**, en commençant par les tuiles les plus proches (file de priorité par distance au carré), jusqu'à satisfaire la quantité.
- **Gravier** (zones d'entraînement uniquement, `GravelLayer`) : lit la valeur de la tuile mais ne la décrémente pas — les filons de gravier sont inépuisables.

Le rendement par type (produits raffinés) est détaillé dans [Minerais](/fr/content/ores/) ; les nombres de filons par zone se trouvent dans [Index des zones](/zones/zone-index/).

<!-- Developer notes: Zones/Terrains/Materials/Minerals/MineralConfiguration.cs
     (reader + config), MineralLayer.cs (LoadMineralNodes 1% delete + top-up,
     GenerateNewNode radius/tile/amount wiring, FluxOre events),
     Generators/MineralNodeGeneratorBase.cs (FindStartPosition, NormalizeNoise,
     CreateMineralNode, KeepOutDist), Generators/RandomWalkMineralNodeGenerator.cs
     (flood fill, 50k step cap), MineralNode.cs (uint[] values, 7-day expiry,
     30-min save), MineralNodeRepository.cs (mineralnodes table, compressed
     values), Minerals/MineralExtractor.cs (solid/liquid/gravel extraction),
     Modules/DrillerModule.cs (amount property + modifiers), Materials/MaterialHelper.cs
     (minerals.definition -> item), Zones/DistanceConstants.cs
     (MINERAL_DISTANCE_FROM_BASE_MIN = 100). -->
