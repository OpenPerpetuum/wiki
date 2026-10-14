---
title: "Ervaakvelden"
description: "De minerals- en mineralconfigs-tabellen, node-generatieformules, nodelevenscyclus en extractiemechanieken."
weight: 30
---

# Ervaakvelden

Erdata heeft twee niveaus: **per type** (`minerals` — wat het materiaal is en hoeveel
één extractie oplevert) en **per zone per type** (`mineralconfigs` — hoeveel nodes,
hoe groot, hoe vol). De runtime-node-status staat in de `mineralnodes`-tabel.

## `minerals`

| Kolom | Type | Gebruikt door | Betekenis |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | De `MaterialType`-enum-ordinaal (1=Titan … 19=DHDT, 0=Undefined). Alle joins gebruiken `mineralconfigs.materialtype = minerals.idx`. |
| `name` | varchar | `ToMaterialType()` | Typenaam ("titan", "crude", …). |
| `definition` | int | `MaterialHelper` → item | De itemdefinitie die door extractie wordt geproduceerd (bv. titan → def 168). |
| `amount` | int | `DrillerModule` | **Basis-eenheden per extractie** (titan 1500, crude 1500, stermonit 975, liquizit 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = Vast (`OreLayer`), 1 = Vloeibaar (`LiquidLayer`). |
| `enablereffectrequired` | bit | module gating | Of een enabler-effect vereist is voor extractie. |
| `geoscandocument` | int | scan items | Geoscandocument-item voor dit materiaal. |

## `mineralconfigs`

Eén rij per (zone, materiaal). Verbruikt door `MineralConfigurationReader` → één
`MineralLayer` per rij:

| Kolom | Type | Gebruikt door | Betekenis |
|---|---|---|---|
| `zoneId` | int | laagconstructie | Bezittende zone. |
| `materialtype` | int | → `minerals.idx` | Het materiaal. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | Aantal nodes van dit type dat de zone onderhoudt. |
| `maxtilespernode` | int | generator | Max. tegels per node-blob; bepaalt ook de afstandsstraal (hieronder). |
| `totalamountpernode` | int | generator | Totaal materiaal in een nieuwe node, verdeeld over de tegels van de blob. |
| `minthreshold` | double | generator | Minimum genormaliseerde vulling per tegel (0–1); tegels daaronder worden verwijderd. |

### Node-generatieformules (`MineralNodeGeneratorBase.cs`)

Voor een nieuwe node van een type met de bovenstaande configuratie:

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = startpositie moet ≥ 2 × radius zijn van de dichtstbijzijnde bestaande node
blob    = random-walk flood fill (4-tegel kwast) tot maxtilespernode geldige tegels
tile[i] = ( noise[i] / max(noise) ) genormaliseerd naar [minthreshold, 1]
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // jitter, daarna afgekapt naar uint
```

Uitsluitzones rond dockingsbases en teleports (`KeepOutDist`): epriton = 100 tegels
(`MINERAL_DISTANCE_FROM_BASE_MIN`), flux ore = 200; alle andere types = 0.

### Werkvoorbeeld — Daoden (zone_ASI) crude (id 2)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125.000.000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → afstand ≥ 80 tegels
blob    = tot 1257 tegels
tile    = aandeel ∈ [0.5, 1.0] × (125.000.000 / Σgenormaliseerd) × jitter
```

Een volledige crude-node bevat 125 M eenheden; bij de basisextractie van 1.500 eenheden
per boorcyclus is dat ~83.000 cycli materiaal per node, ~666.000 over de 8 nodes van
de zone.

## Node-status — `mineralnodes`

| Kolom | Betekenis |
|---|---|
| `zoneid`, `materialtype` | Bezittende zone + type |
| `x, y, width, height` | Bounding box van de node (het gebied van de blob) |
| `data` | Gecomprimeerde `uint` per tegel (rij-maag binnen de box) |

Levenscyclus (`MineralNode.cs`, `MineralLayer.cs`):

- **Laden**: bij zone-start worden alle opgeslagen nodes geladen; een node waarvan het
  totaal ≤ **1%** van `totalamountpernode` is, wordt in plaats daarvan verwijderd.
- **Aanvullen**: als minder dan `maxnodes` over zijn gebleven, worden nieuwe nodes
  gegenereerd (formule hierboven).
- **Verval**: een **onaangetaste** node verloopt na **7 dagen** (`TimeTracker`);
  mijnen zet de klok terug. Een node waarvan de maximale tegelwaarde 0 bereikt,
  verloopt eveneens.
- **Persistentie**: gewijzigde nodes worden op een **30-minuten**-sleeptimer naar de
  DB geschreven.
- **Flux ore-koppeling**: afname/verval van een `FluxOre`-node publiceert
  `OreNpcSpawnMessage` → de NPC-spawner luistert (`OreNPCSpawner`).

## Extractiemechanieken (`MineralExtractor.cs`, `DrillerModule.cs`)

De extractiehoeveelheid is `minerals.amount` geschaald met de
`mining_amount_modifier`-eigenschap van de robot (geaggregeerd uit
`mining_amount_modifier`, `effect_mining_amount_modifier`,
`drone_amplification_mining_amount_modifier`,
`effect_excavator_mining_amount_modifier`).

- **Vast** (`OreLayer`): neemt `min(tegelwaarde, amount)` van de **enkele tegel**
  waarop de robot staat.
- **Vloeibaar** (`LiquidLayer`): onttrekt aan de **hele node**, eerst de dichtstbijzijnde
  tegels (prioriteitswachtrij op gekwadrateerde afstand), totdat de hoeveelheid is
  voldaan.
- **Gravel** (alleen trainingszones, `GravelLayer`): leest de tegelwaarde maar
  verlaagt deze niet — gravel-nodes zijn onuitputtelijk.

Opbrengst per type (geraffineerde producten) staat in [Erven](/content/ores/);
aantallen nodes per zone staan in [Zone-index](/zones/zone-index/).

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