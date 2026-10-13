---
title: "Campi dei minerali"
description: "Le tabelle minerals e mineralconfigs, formule di generazione dei nodi, ciclo vitale dei nodi e meccaniche di estrazione."
weight: 30
---

# Campi dei minerali

I dati sui minerali operano su due livelli: **per tipo** (`minerals` — che tipo di materiale è
e quanto rende una singola estrazione) e **per zona per tipo** (`mineralconfigs` — quanti
nodi, quanto grandi, quanto ricchi). Lo stato dei nodi a runtime risiede nella tabella `mineralnodes`.

## `minerals`

| Colonna | Tipo | Utilizzato da | Significato |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | Il valore ordinale dell'enum `MaterialType` (1=Titan … 19=DHDT, 0=Undefined). Tutti i join usano `mineralconfigs.materialtype = minerals.idx`. |
| `name` | varchar | `ToMaterialType()` | Nome del tipo ("titan", "crude", …). |
| `definition` | int | `MaterialHelper` → item | La definizione dell'oggetto prodotta dall'estrazione (ad es. titan → def 168). |
| `amount` | int | `DrillerModule` | **Unità base per estrazione** (titan 1500, crude 1500, stermonit 975, liquizit 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = Solido (`OreLayer`), 1 = Liquido (`LiquidLayer`). |
| `enablereffectrequired` | bit | module gating | Indica se è richiesto un effetto abilitatore per l'estrazione. |
| `geoscandocument` | int | scan items | Oggetto documento di geo-scansione per questo materiale. |

## `mineralconfigs`

Una riga per ogni coppia (zona, materiale). Elaborata da `MineralConfigurationReader` → un
`MineralLayer` per riga:

| Colonna | Tipo | Utilizzato da | Significato |
|---|---|---|---|
| `zoneId` | int | layer construction | Zona di appartenenza. |
| `materialtype` | int | → `minerals.idx` | Il materiale. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | Nodi di questo tipo mantenuti dalla zona. |
| `maxtilespernode` | int | generator | Numero massimo di tessere per nodo/agglomerato; definisce anche il raggio di spaziatura (sotto). |
| `totalamountpernode` | int | generator | Materiale totale in un nodo intatto, distribuito sulle tessere dell'agglomerato. |
| `minthreshold` | double | generator | Riempimento normalizzato minimo per tessera (0–1); le tessere al di sotto di questa soglia vengono scartate. |

### Formule di generazione dei nodi (`MineralNodeGeneratorBase.cs`)

Per un nuovo nodo di una tipologia con la configurazione sopra descritta:

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = start position must be ≥ 2 × radius from the nearest existing node
blob    = random-walk flood fill (4-tile brush) up to maxtilespernode valid tiles
tile[i] = ( noise[i] / max(noise) ) normalized into [minthreshold, 1]
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // jitter, then truncated to uint
```

Zone di rispetto attorno alle basi di attracco e ai teletrasporti (`KeepOutDist`): epriton = 100 tessere
(`MINERAL_DISTANCE_FROM_BASE_MIN`), flux ore = 200; tutti gli altri tipi = 0.

### Esempio pratico — Greggio di Daoden (zone_ASI) (id 2)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → spacing ≥ 80 tiles
blob    = up to 1257 tiles
tile    = share ∈ [0.5, 1.0] × (125,000,000 / Σnormalized) × jitter
```

Un nodo pieno di greggio contiene 125 M unità; con l'estrazione base di 1.500 unità per ciclo
di trivellazione, ciò corrisponde a circa 83.000 cicli di materiale per nodo, ~666.000
tra gli 8 nodi della zona.

## Stato dei nodi — `mineralnodes`

| Colonna | Significato |
|---|---|
| `zoneid`, `materialtype` | Zona di appartenenza + tipo |
| `x, y, width, height` | Bounding box del nodo (l'area dell'agglomerato) |
| `data` | Valore `uint` compresso per tessera (in ordine row-major all'interno della bounding box) |

Ciclo vitale (`MineralNode.cs`, `MineralLayer.cs`):

- **Caricamento**: all'avvio della zona, vengono caricati tutti i nodi salvati; un nodo il cui totale
  è ≤ **1%** di `totalamountpernode` viene invece eliminato.
- **Rifornimento**: se sono sopravvissuti meno di `maxnodes`, vengono generati nuovi nodi (formula sopra).
- **Scadenza**: un nodo **incontaminato** scade dopo **7 giorni** (`TimeTracker`); l'estrazione
  reimposta il timer. Anche un nodo il cui valore massimo per tessera scende a 0 scade.
- **Persistenza**: i nodi modificati vengono salvati nel DB su un timer di salvataggio di **30 minuti**.
- **Accoppiamento flux ore**: la diminuzione/scadenza di un nodo di `FluxOre` pubblica
  `OreNpcSpawnMessage` → lo spawner NPC riceve l'evento (`OreNPCSpawner`).

## Meccaniche di estrazione (`MineralExtractor.cs`, `DrillerModule.cs`)

La quantità estratta è `minerals.amount` scalata dalla proprietà del robot
`mining_amount_modifier` (aggregata da `mining_amount_modifier`,
`effect_mining_amount_modifier`, `drone_amplification_mining_amount_modifier`,
`effect_excavator_mining_amount_modifier`).

- **Solido** (`OreLayer`): preleva `min(tile value, amount)` dalla **singola tessera** su cui
  si trova il robot.
- **Liquido** (`LiquidLayer`): drena l'**intero nodo**, a partire dalle tessere più vicine
  (coda con priorità in base alla distanza al quadrato), fino a soddisfare la quantità richiesta.
- **Ghiaia** (solo zone di addestramento, `GravelLayer`): legge il valore della tessera ma non
  lo decrementa — i nodi di ghiaia sono inesauribili.

La resa per tipo (prodotti raffinati) è disponibile in [Minerali](/content/ores/); il numero di nodi
per zona è presente nell'[Indice delle zone](/zones/zone-index/).

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