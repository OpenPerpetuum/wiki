---
title: "File di zona"
description: "I file binari dei layer del terreno: convenzioni di denominazione, layout delle struct, bit dei flag, ciclo di salvataggio e cosa risiede invece nel database."
weight: 50
---

# File di zona

Il terreno di una zona è memorizzato come un insieme di **file binari di layer**, uno per livello, posizionati accanto ai dati della zona. Il nome segue il formato `{layer}.{zoneid:0000}.bin` (`Zone.CreateTerrainDataFilename`) — ad esempio `plants.0042.bin` per la zona 42. I layer sono array lineari (flat) di una struct a dimensione fissa, in ordine **row-major (per riga), larghezza × altezza** (di default 2048×2048 = 4.194.304 tile).

## I layer

| File | Struct | Byte/tile | Contenuto |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (byte) + `height` (byte) — ostacoli, piante, elementi decorativi, isole |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (o 1) | bit di controllo per tile (vedere la particolarità descritta sotto) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | stato della vegetazione per tile (dettagli sotto) |
| `altitude.NNNN.bin` | `ushort` | 2 | elevazione; confrontata come `value / 4` nei controlli della vegetazione (scala di coordinate del client) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | solo zone terraformabili: maschera di fusione (blend) per tile (sotto) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | solo zone terraformabili: elevazione pre-terraformazione su disco — **non letta dal server** (sotto) |

Layer derivati (calcolati durante il caricamento, **non** file su disco): `SlopeLayer` (dall'altitudine) e `Passable` (da blocks + slope + posizioni percorribili nel DB, solo per zone non terraformabili).
Nelle zone terraformabili l'altitudine è incapsulata in un `TerraformableAltitude`, che al momento del caricamento calcola un intervallo di **barriera** per tile: `blend/65535` interpola le costanti 1850 → altitudine originale (min) e 30000 → altitudine originale (max), bloccando poi l'intervallo (clamp) in modo che contenga sempre il valore corrente. Gli aggiornamenti dell'altitudine terraformata vengono limitati all'interno di tale barriera — pertanto `blend = 0` rende un tile liberamente terraformabile tra 1850 e 30000, mentre `blend = 65535` lo vincola alla sua elevazione originale. (I file `altitude_original.NNNN.bin` su disco conservano le quote pre-terraformazione per tool esterni; il server crea il proprio snapshot in memoria dell'altitudine originale dal file `altitude.NNNN.bin` caricato e non legge mai quel file con tale nome).

### `BlockingInfo` (2 byte)

`flags` è di tipo `BlockingFlags` (byte):

| Bit | Nome |
|---|---|
| 1 | Obstacle |
| 2 | Plant |
| 4 | Decor |
| 8 | Island |

`NonNaturally` = Decor \| Island \| Obstacle. `height` rappresenta l'altezza di blocco al calpestio del tile (l'altezza di blocco dovuta alla vegetazione viene scritta qui dal codice di crescita delle piante).

### `TerrainControlFlags` (layer di controllo)

Insieme di flag `ushort`:

| Bit | Nome |
|---|---|
| 1 | AntiPlant |
| 2 | TerraformProtected |
| 4 | SyndicateArea |
| 8 | ConcreteA |
| 16 | ConcreteB |
| 64 | Roaming |
| 128 | Highway |
| 256 | PBSHighway |
| 512 | PBSTerraformProtected |
| 1024 | NpcRestricted |

(La numerazione 512/1024 segue lo schema `1 << n`; il bit 32 non è utilizzato). Un tile consente la crescita delle piante quando `!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`.

**Particolarità di archiviazione**: il loader supporta file di controllo sia a **1 byte/tile** che a **2 byte/tile** — se la dimensione del file corrisponde al numero totale di tile, ciascun byte viene esteso a un `TerrainControlFlags`; in caso contrario, viene letto direttamente l'array grezzo di `ushort` (`LayerFileIO.LoadLayerData`). Tutte le zone attive utilizzano il **formato a 2 byte** (`control.0000.bin` = 8.388.608 B = 4.194.304 × 2); il formato a 1 byte (4 MB) è un fallback legacy ancora supportato dal loader.

### `PlantInfo` (7 byte) — lo stato del tile di vegetazione

| Byte | Campo | Significato |
|---|---|---|
| 0 | `type` | `PlantType` (0 = vuoto; 1..19 secondo [Plant fields](/it/formats/plant-fields/)) |
| 1 | `state` | Indice dello stato di crescita (nella tabella `state_N` della regola) |
| 2 | `time` | Accumulatore dei tick di crescita (confrontato con il `growRate` della regola) |
| 3 | `spawn` | **Probabilità di spawn per tile, incorporata nel file di zona; il server non la scrive mai** (non esiste alcuna assegnazione nel codice — `PlantInfo.Clear()` la preserva deliberatamente). 0 = tile sterile: qualsiasi pianta presente su di esso viene rimossa immediatamente durante la validazione e non germoglierà mai. Altrimenti funge da filtro per tentativo: durante il ciclo di rigenerazione della vegetazione, un tile vuoto casuale viene accettato solo se `FastRandom.NextByte() < spawn`, ovvero probabilità di successo per tile ≈ `spawn/256`. |
| 4 | `health` | HP correnti (frazione della salute per stato definita dalla regola) |
| 5 | `material` | Quantità corrente di frutti (0–255) |
| 6 | `groundType` | Byte `GroundType` (0=Darkrocks … 17=Sand-ish, 20=non definito) — la classe di terreno verificata rispetto a `allowedTerrainTypes` nella regola della pianta |

### Esempio pratico — dimensioni dei file per una zona 2048×2048 (verificate sui file effettivi)

```
blocks    4,194,304 tiles × 2 B = 8,388,608 B (8 MB)
plants    4,194,304 tiles × 7 B = 29,360,128 B (28 MB)
altitude  4,194,304 tiles × 2 B = 8,388,608 B (8 MB)
control   4,194,304 tiles × 2 B = 8,388,608 B (8 MB, formato a 2 byte; un file legacy a 1 byte occuperebbe 4 MB)
```

**Verifica sui dati reali** (`plants.0106.bin`, la zona gamma terraformabile): tutti i 4.194.304 tile presentano `spawn = 0x83` (131/256 ≈ 51% di probabilità per tentativo) e `type = 0`, ad eccezione di 10 tile che contengono piante attive — la mappa di spawn è un campo di probabilità precalcolato per l'intera zona, del tutto indipendente dalla presenza attuale delle piante.

Non tutte le zone contengono ciascun file: 66 delle 84 zone includono un file `plants.NNNN.bin`. Le 18 prive di tale file corrispondono a varianti gamma legacy ormai sostituite (`zone_tm_g_*`, `zone_ics_g_*`, `zone_asi_g_*`, ID 20–43), che non vengono caricate. La directory dei layer è `$GameRoot/layers/`.

## Il ciclo di salvataggio (`IntervalLayerSaver.cs`)

- Ciascun layer modificabile (blocks, control, plants, altitude) è monitorato da un `IntervalLayerSaver<T>`; qualsiasi operazione di scrittura su tile o area imposta un flag dirty.
- Il saver è registrato come processo su un timer da **2 ore** (`TerrainsModule`); un layer dirty viene scritto quando scatta il tick.
- Le scritture avvengono su un file temporaneo `.tmp<ticks>.bin`, vengono **verificate tramite checksum MD5** a seguito di una rilettura, e solo allora sostituiscono il file reale.
- All'arresto del server, i layer con flag dirty vengono salvati un'ultima volta.
- I nodi minerari **non** sono inclusi in questi file — persistono nella tabella di database `mineralnodes` (flush ogni 30 minuti, consultare [Ore fields](/it/formats/ore-fields/)).

## Cosa è e cosa non è un file

| Dato | Posizione |
|---|---|
| Layer del terreno (blocks/control/plants/altitude) | File `.bin` |
| Stato dei nodi minerari | DB `mineralnodes` |
| Specie vegetali per zona | DB `plantrules` + **file** di regole (`$GameRoot/plantrules/*.txt`) |
| Configurazione della zona (fertilità, dimensioni, tipo, ruleset) | DB `zones` |
| Configurazione dei minerali | DB `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1-vs-2 byte control handling, safe zero-fill on size mismatch);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty flag, MD5 + tmp rename, stop-save);
     Bootstrapper/Modules/TerrainsModule.cs (layer load order: blocks, control, plants,
     altitude, blend; slope + passable derivation; 2h saver + 2h material process). -->