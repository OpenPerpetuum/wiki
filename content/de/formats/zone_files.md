---
title: "Zonendateien"
description: "Die binären Gelände-Ebenendateien: Benennung, Struct-Layouts, Flag-Bits, der Speicherzyklus und was stattdessen in der Datenbank liegt."
weight: 50
---

# Zonendateien

Das Gelände einer Zone wird als ein Satz **binärer Ebenendateien** (Layer-Dateien) gespeichert, eine pro Ebene, neben
den Zonendaten. Der Name lautet `{layer}.{zoneid:0000}.bin`
(`Zone.CreateTerrainDataFilename`) — z. B. `plants.0042.bin` für Zone 42. Ebenen sind
flache Arrays eines Structs mit fester Größe, **Row-Major, Breite × Höhe** (Standard 2048×2048 =
4.194.304 Tiles).

## Die Ebenen

| Datei | Struct | Bytes/Tile | Inhalt |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (Byte) + `height` (Byte) — Hindernisse, Pflanzen, Deko, Inseln |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (oder 1) | Steuerungs-Bits pro Tile (siehe Besonderheit unten) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | der Pflanzenzustand pro Tile (unten) |
| `altitude.NNNN.bin` | `ushort` | 2 | Höhe; verglichen als `value / 4` bei Pflanzenprüfungen (Client-Koordinatenskalierung) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | Nur terraformbare Zonen: Blend-Maske pro Tile (unten) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | Nur terraformbare Zonen: Höhe vor dem Terraformen auf der Festplatte — **wird vom Server nicht gelesen** (unten) |

Abgeleitete Ebenen (beim Laden berechnet, **keine** Dateien): `SlopeLayer` (aus Höhe) und
`Passable` (aus Blöcken + Steigung + passierbaren DB-Positionen, nur nicht-terraformbare Zonen).
Auf terraformbaren Zonen ist die Höhe in ein `TerraformableAltitude` gehüllt, welches
beim Laden einen **Barriere**-Bereich pro Tile berechnet: `blend/65535` mischt die Konstanten
1850 → ursprüngliche Höhe (Min) und 30000 → ursprüngliche Höhe (Max) und begrenzt den
Bereich so, dass er immer den aktuellen Wert enthält. Terraforme Höhenänderungen werden
in diese Barriere eingeklemmt — `blend = 0` lässt ein Tile also frei zwischen 1850 und
30000 terraformbar, während `blend = 65535` es auf seiner ursprünglichen Höhe fixiert. (Die
`altitude_original.NNNN.bin`-Dateien auf der Festplatte enthalten Höhen vor dem Terraformen für externe
Tools; der Server erstellt seinen Snapshot der ursprünglichen Höhe im Arbeitsspeicher aus der geladenen
`altitude.NNNN.bin` und liest diesen Dateinamen nie.)

### `BlockingInfo` (2 Bytes)

`flags` ist `BlockingFlags` (Byte):

| Bit | Name |
|---|---|
| 1 | Obstacle |
| 2 | Plant |
| 4 | Decor |
| 8 | Island |

`NonNaturally` = Decor \| Island \| Obstacle. `height` ist die Lauf-Blockierhöhe des Tiles
(die Blockierhöhe von Pflanzen wird hier durch den Pflanzenwachstumscode eingetragen).

### `TerrainControlFlags` (Control-Ebene)

`ushort`-Flag-Satz:

| Bit | Name |
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

(Die 512/1024-Nummerierung folgt `1 << n`; Bit 32 ist ungenutzt.) Ein Tile ist für Pflanzen zulässig, wenn
`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`.

**Speicher-Besonderheit**: Der Lader akzeptiert sowohl Steuerungsdateien mit **1 Byte/Tile** als auch
**2 Bytes/Tile** — entspricht die Dateilänge der Tile-Anzahl, wird jedes Byte zu einem
`TerrainControlFlags` erweitert; andernfalls wird das rohe `ushort`-Array eingelesen
(`LayerFileIO.LoadLayerData`). Die Live-Zonen nutzen alle das **2-Byte-Format**
(`control.0000.bin` = 8.388.608 B = 4.194.304 × 2); die 1-Byte-Form (4 MB) ist ein
Legacy-Fallback, den der Lader weiterhin unterstützt.

### `PlantInfo` (7 Bytes) — der Pflanzen-Tile-Zustand

| Byte | Feld | Bedeutung |
|---|---|---|
| 0 | `type` | `PlantType` (0 = leer; 1..19 gemäß [Pflanzenfelder](/de/formats/plant-fields/)) |
| 1 | `state` | Wachstumszustands-Index (in die `state_N`-Tabelle der Regel) |
| 2 | `time` | Wachstums-Tick-Akkumulator (verglichen mit `growRate` der Regel) |
| 3 | `spawn` | **Spawn-Wahrscheinlichkeit pro Tile, in der Zonendatei fest vorgegeben; der Server schreibt sie nie** (im gesamten Code existiert keine Zuweisung — `PlantInfo.Clear()` behält sie bewusst bei). 0 = steriles Tile: jede Pflanze, die sich bereits darauf befindet, wird bei der Validierung sofort entfernt, und es sprießt nie eine. Andernfalls dient es als Tor pro Versuch: während des Pflanzen-Regenerationsdurchlaufs wird ein zufälliges leeres Tile nur akzeptiert, wenn `FastRandom.NextByte() < spawn`, d. h. Erfolgschance pro Tile ≈ `spawn/256`. |
| 4 | `health` | Aktuelle HP (Verhältnis der Gesundheit pro Zustand der Regel) |
| 5 | `material` | Aktuelle Fruchtmenge (0–255) |
| 6 | `groundType` | `GroundType`-Byte (0=Darkrocks … 17=Sand-ish, 20=undefined) — die Geländeklasse, gegen die `allowedTerrainTypes` der Pflanzenregel prüft |

### Rechenbeispiel — Dateigrößen für eine 2048×2048-Zone (verifiziert anhand von Live-Dateien)

```
blocks    4.194.304 Tiles × 2 B = 8.388.608 B (8 MB)
plants    4.194.304 Tiles × 7 B = 29.360.128 B (28 MB)
altitude  4.194.304 Tiles × 2 B = 8.388.608 B (8 MB)
control   4.194.304 Tiles × 2 B = 8.388.608 B (8 MB, 2-Byte-Form; eine 1-Byte-Legacy-Datei wäre 4 MB)
```

**Live-Daten-Prüfung** (`plants.0106.bin`, die terraformbare Gamma-Zone): Alle 4.194.304
Tiles tragen `spawn = 0x83` (131/256 ≈ 51 % Chance pro Versuch) und `type = 0`, abgesehen von
10 Tiles mit lebenden Pflanzen — die Spawn-Karte ist ein zonenweites, vorgebackenes Wahrscheinlichkeitsfeld,
unabhängig davon, wo sich aktuell Pflanzen befinden.

Nicht jede Zone hat jede Datei: 66 der 84 Zonen enthalten eine `plants.NNNN.bin`. Die 18
ohne Datei sind die abgelösten Legacy-Gamma-Varianten (`zone_tm_g_*`, `zone_ics_g_*`,
`zone_asi_g_*`, IDs 20–43), die nicht geladen werden. Das Ebenen-Verzeichnis ist
`$GameRoot/layers/`.

## Der Speicherzyklus (`IntervalLayerSaver.cs`)

- Jede veränderbare Ebene (blocks, control, plants, altitude) wird von einem
  `IntervalLayerSaver<T>` überwacht; jeder Tile-/Bereichsschreibvorgang setzt ein Dirty-Flag.
- Der Saver ist als Prozess auf einem **2-Stunden**-Timer registriert
  (`TerrainsModule`); eine veränderte Ebene wird geschrieben, wenn der Tick auslöst.
- Schreibvorgänge erfolgen in eine `.tmp<ticks>.bin`-Datei, werden durch erneutes Lesen
  per **MD5 verifiziert** und ersetzen erst dann die eigentliche Datei.
- Beim Herunterfahren des Servers werden veränderte Ebenen noch einmal gespeichert.
- Mineralknoten befinden sich **nicht** in diesen Dateien — sie werden in der DB-Tabelle
  `mineralnodes` persistent gespeichert (30-Minuten-Flush, siehe [Erzfelder](/de/formats/ore-fields/)).

## Was eine Datei ist und was nicht

| Daten | Speicherort |
|---|---|
| Geländeebenen (blocks/control/plants/altitude) | `.bin`-Dateien |
| Erz-Knotenzustand | DB `mineralnodes` |
| Pflanzenarten pro Zone | DB `plantrules` + Regel-**Dateien** (`$GameRoot/plantrules/*.txt`) |
| Zonenkonfiguration (Fruchtbarkeit, Größe, Typ, Regelwerk) | DB `zones` |
| Erz-Konfiguration | DB `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1-vs-2 byte control handling, safe zero-fill on size mismatch);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty flag, MD5 + tmp rename, stop-save);
     Bootstrapper/Modules/TerrainsModule.cs (layer load order: blocks, control, plants,
     altitude, blend; slope + passable derivation; 2h saver + 2h material process). -->