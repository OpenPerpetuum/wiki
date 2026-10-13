---
title: "Ervfelder"
description: "Die minerals- und mineralconfigs-Tabellen, die Node-Generierungsformeln, der Node-Lebenszyklus und die Extraktionsmechanik."
weight: 30
---

# Ervfelder

Erdedaten gibt es auf zwei Ebenen: **pro Typ** (`minerals` — was das Material ist und
wie viel eine Extraktion ergibt) und **pro Zone und Typ** (`mineralconfigs` — wie viele
Nodes, wie groß, wie voll). Der Laufzeit-Nodezustand liegt in der Tabelle
`mineralnodes`.

## `minerals`

| Spalte | Typ | Verwendet von | Bedeutung |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | Die `MaterialType`-Enum-Ordnal (1=Titan … 19=DHDT, 0=Undefined). Alle Joins verwenden `mineralconfigs.materialtype = minerals.idx`. |
| `name` | varchar | `ToMaterialType()` | Typname ("titan", "crude", …). |
| `definition` | int | `MaterialHelper` → Item | Die Itemdefinition, die durch Extraktion entsteht (z. B. titan → def 168). |
| `amount` | int | `DrillerModule` | **Basis-Einheiten pro Extraktion** (titan 1500, crude 1500, stermonit 975, liquizit 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = Fest (`OreLayer`), 1 = Flüssig (`LiquidLayer`). |
| `enablereffectrequired` | bit | Modul-Zugriff | Ob ein Enabler-Effekt zur Extraktion erforderlich ist. |
| `geoscandocument` | int | Scan-Items | Geo-Scan-Dokument-Item für dieses Material. |

## `mineralconfigs`

Eine Zeile pro (Zone, Material). Verbraucht von `MineralConfigurationReader` → ein
`MineralLayer` pro Zeile:

| Spalte | Typ | Verwendet von | Bedeutung |
|---|---|---|---|
| `zoneId` | int | Layer-Aufbau | Die Zone, der es gehört. |
| `materialtype` | int | → `minerals.idx` | Das Material. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | Nodes dieses Typs, die die Zone vorhält. |
| `maxtilespernode` | int | Generator | Max. Kacheln pro Node-Blob; bestimmt auch den Abstandsradius (unten). |
| `totalamountpernode` | int | Generator | Gesamtmaterial eines frischen Nodes, verteilt über die Kacheln des Blobs. |
| `minthreshold` | double | Generator | Minimale normierte Füllung pro Kachel (0–1); Kacheln darunter werden verworfen. |

### Node-Generierungsformeln (`MineralNodeGeneratorBase.cs`)

Für einen neuen Node eines Typs mit der obigen Konfiguration:

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = Startposition muss ≥ 2 × radius vom nächsten bestehenden Node sein
blob    = Random-Walk-Floodfill (4-Kachel-Pinsel) bis maxtilespernode gültige Kacheln
tile[i] = ( noise[i] / max(noise) ) normiert nach [minthreshold, 1]
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // Jitter, danach auf uint gekürzt
```

Sperrzonen um Docking-Basen und Teleporter (`KeepOutDist`): epriton = 100 Kacheln
(`MINERAL_DISTANCE_FROM_BASE_MIN`), Fluxore = 200; alle anderen Typen = 0.

### Beispiel — Daoden (zone_ASI) crude (id 2)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125.000.000, minthreshold=0,5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20,0) × 2 = 40   → Abstand ≥ 80 Kacheln
blob    = bis zu 1257 Kacheln
tile    = Anteil ∈ [0,5; 1,0] × (125.000.000 / Σnormiert) × Jitter
```

Ein voller crude-Node enthält 125 M Einheiten; bei der Basisextraktion von 1.500
Einheiten pro Bohrzyklus sind das ~83.000 Zyklus Material pro Node, ~666.000 über die
8 Nodes der Zone.

## Node-Zustand — `mineralnodes`

| Spalte | Bedeutung |
|---|---|
| `zoneid`, `materialtype` | Zone + Typ |
| `x, y, width, height` | Bounding Box des Nodes (Fläche des Blobs) |
| `data` | Komprimierte `uint` pro Kachel (zeilenweise innerhalb der Box) |

Lebenszyklus (`MineralNode.cs`, `MineralLayer.cs`):

- **Laden**: beim Zonenstart werden alle gespeicherten Nodes geladen; ein Node, dessen
  Gesamtmenge ≤ **1 %** von `totalamountpernode` beträgt, wird stattdessen gelöscht.
- **Nachfüllen**: wenn weniger als `maxnodes` überlebt haben, werden neue Nodes
  generiert (Formel oben).
- **Ablauf**: ein **unberührter** Node läuft nach **7 Tagen** ab (`TimeTracker`);
  Abbau setzt die Uhr zurück. Ein Node, dessen maximale Kachelnzahl 0 erreicht, läuft
  ebenfalls ab.
- **Persistenz**: veränderte Nodes werden per **30-Minuten**-Speichertimer in die DB
  geschrieben.
- **Fluxore-Kopplung**: Abnahme/Ablauf eines `FluxOre`-Nodes veröffentlicht
  `OreNpcSpawnMessage` → der NPC-Spawner hört zu (`OreNPCSpawner`).

## Extraktionsmechanik (`MineralExtractor.cs`, `DrillerModule.cs`)

Die Extraktionsmenge ist `minerals.amount`, skaliert mit der Eigenschaft
`mining_amount_modifier` des Roboters (aggregiert aus
`mining_amount_modifier`, `effect_mining_amount_modifier`,
`drone_amplification_mining_amount_modifier`,
`effect_excavator_mining_amount_modifier`).

- **Fest** (`OreLayer`): nimmt `min(Kachelwert, amount)` von der **einzigen Kachel**,
  auf der der Roboter steht.
- **Flüssig** (`LiquidLayer`): leert den **gesamten Node**, beginnend bei den
  nächsten Kacheln (Prioritätswarteschlange nach quadriertem Abstand), bis die Menge
  erreicht ist.
- **Kies** (nur Trainingszonen, `GravelLayer`): liest den Kachelwert, reduziert ihn
  aber nicht — Kies-Node sind unerschöpflich.

Erträge pro Typ (raffinierte Produkte) stehen in [Erze](/content/ores/); Node-Zahlen
pro Zone im [Zonenindex](/zones/zone-index/).

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
