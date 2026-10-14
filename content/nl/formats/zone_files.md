---
title: "Zonebestanden"
description: "De binaire terreinlaagbestanden: naamgeving, structuurlay-outs, vlagbitsen, de opslaggroei en wat in de DB staat in plaats daarvan."
weight: 50
---

# Zonebestanden

Het terrein van een zone wordt opgeslagen als een set **binaire laagbestanden**, één per laag, naast de zonegegevens. De naam is `{layer}.{zoneid:0000}.bin`
(`Zone.CreateTerrainDataFilename`) — bijv. `plants.0042.bin` voor zone 42. Lagen zijn
platte arrays van een struct met vaste grootte, **rij-voor-rij, breedte × hoogte** (standaard 2048×2048 =
4.194.304 tegels).

## De lagen

| Bestand | Struct | Bytes/tegel | Inhoud |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (byte) + `height` (byte) — obstakels, planten, decor, eilanden |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (of 1) | controlebits per tegel (zie bijzonderheid hieronder) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | de planttoestand per tegel (hieronder) |
| `altitude.NNNN.bin` | `ushort` | 2 | hoogte; vergeleken als `value / 4` in plantcontroles (client-coördinaatschaal) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | alleen terraformeerbare zones: blendmasker per tegel (hieronder) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | alleen terraformeerbare zones: pre-terraform hoogte op schijf — **niet gelezen door de server** (hieronder) |

Gedeelde lagen (berekend bij laden, **geen** bestanden): `SlopeLayer` (uit altitude) en
`Passable` (uit blocks + slope + DB-bereikbare posities, alleen niet-terraformeerbare zones).
Bij terraformeerbare zones wordt de altitude ingepakt in een `TerraformableAltitude`, die
bij laden een **barrière**-bereik per tegel berekent: `blend/65535` mengt de constanten
1850 → oorspronkelijke hoogte (min) en 30000 → oorspronkelijke hoogte (max), en klempt het
bereik zodat het de huidige waarde altijd bevat. Terraformeerde altitude-updates worden
geklempt binnen die barrière — dus `blend = 0` laat een tegel vrij terraformeerbaar tussen 1850 en
30000, terwijl `blend = 65535` deze vastzet op de oorspronkelijke hoogte. (De
`altitude_original.NNNN.bin` bestanden op schijf bevatten pre-terraform hoogtes voor externe
tools; de server neemt zijn oorspronkelijke-hoogtesnapshot in het geheugen van het geladen
`altitude.NNNN.bin` en leest die bestandsnaam nooit.)

### `BlockingInfo` (2 bytes)

`flags` is `BlockingFlags` (byte):

| Bit | Naam |
|---|---|
| 1 | Obstacle |
| 2 | Plant |
| 4 | Decor |
| 8 | Island |

`NonNaturally` = Decor \| Island \| Obstacle. `height` is de loopblokkeerhoogte van de tegel
(de plantblokkeerhoogte wordt hier door de plantgroeicode geschreven).

### `TerrainControlFlags` (controlelaag)

`ushort` vlagset:

| Bit | Naam |
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

(512/1024 nummering volgt `1 << n`; bit 32 is ongebruikt.) Een tegel is planttoegestaan wanneer
`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`.

**Opslagbijzonderheid**: de loader accepteert zowel **1 byte/tegel** als **2 bytes/tegel** controle-
bestanden — als de bestandslengte gelijk is aan het aantal tegels, wordt elke byte verbreed tot een
`TerrainControlFlags`; anders wordt de ruwe `ushort`-array gelezen
(`LayerFileIO.LoadLayerData`). De actieve zones gebruiken allemaal de **2-bytevorm**
(`control.0000.bin` = 8.388.608 B = 4.194.304 × 2); de 1-bytevorm (4 MB) is een
legacy-fallback die de loader nog steeds ondersteunt.

### `PlantInfo` (7 bytes) — de planttegeltoestand

| Byte | Veld | Betekenis |
|---|---|---|
| 0 | `type` | `PlantType` (0 = leeg; 1..19 per [Plant fields](/nl/formats/plant-fields/)) |
| 1 | `state` | Groeistoeks-index (in de `state_N`-tabel van de regel) |
| 2 | `time` | Groeitik-accumulator (vergeleken met de `growRate` van de regel) |
| 3 | `spawn` | **Spawnkans per tegel, gebakken in het zonebestand; de server schrijft dit nooit** (er bestaat geen toewijzing ergens in de code — `PlantInfo.Clear()` bewaart dit opzettelijk). 0 = steriele tegel: elke plant die er al op staat wordt direct gewist tijdens validatie, en er groeit er nooit iets. Anders is het een poort per poging: tijdens de plantregeneratiepass wordt een willekeurige lege tegel alleen geaccepteerd als `FastRandom.NextByte() < spawn`, d.w.z. de kans per tegel ≈ `spawn/256`. |
| 4 | `health` | Huidige HP (ratio van de per-toestand gezondheid van de regel) |
| 5 | `material` | Huidige vrucht hoeveelheid (0–255) |
| 6 | `groundType` | `GroundType` byte (0=Darkrocks … 17=Sand-ish, 20=undefined) — de terreinklasse waar de `allowedTerrainTypes` van de plantregel tegen controleert |

### Werkvoorbeeld — bestandsgroottes voor een 2048×2048 zone (geverifieerd tegen actieve bestanden)

```
blocks    4.194.304 tegels × 2 B = 8.388.608 B (8 MB)
plants    4.194.304 tegels × 7 B = 29.360.128 B (28 MB)
altitude  4.194.304 tegels × 2 B = 8.388.608 B (8 MB)
control   4.194.304 tegels × 2 B = 8.388.608 B (8 MB, 2-bytevorm; een 1-byte legacy-bestand zou 4 MB zijn)
```

**Actieve-gegevenscontrole** (`plants.0106.bin`, de terraformeerbare gamma-zone): alle 4.194.304
tegels hebben `spawn = 0x83` (131/256 ≈ 51% kans per poging) en `type = 0`, behalve
10 tegels met levende planten — het spawnmap is een zonebreed gebakken kansveld
onafhankelijk van waar planten momenteel staan.

Niet elke zone heeft elk bestand: 66 van de 84 zones leveren een `plants.NNNN.bin` mee. De 18
zonder een zijn de verouderde legacy gamma-varianten (`zone_tm_g_*`, `zone_ics_g_*`,
`zone_asi_g_*`, ids 20–43), die niet worden geladen. De laagmap is
`$GameRoot/layers/`.

## De opslaggroei (`IntervalLayerSaver.cs`)

- Elke mutabele laag (blocks, control, plants, altitude) wordt bewaakt door een
  `IntervalLayerSaver<T>`; elke tegel-/gebiedsschrijving zet een dirty-vlag.
- De saver is geregistreerd als een proces op een **2-uur**-timer
  (`TerrainsModule`); een dirty-laag wordt geschreven wanneer de tick afvuurt.
- Schrijvingen gaan naar een `.tmp<ticks>.bin`-bestand, worden **MD5-geverifieerd** tegen een herlezing, en
  vervangen dan pas het echte bestand.
- Bij serverstop worden dirty-lagen nog één keer opgeslagen.
- Mineralknopen zitten **niet** in deze bestanden — ze worden opgeslagen in de `mineralnodes` DB-
  tabel (30-minuten flush, zie [Ore fields](/nl/formats/ore-fields/)).

## Wat wel en niet een bestand is

| Gegevens | Waar |
|---|---|
| Terreinlagen (blocks/control/plants/altitude) | `.bin` bestanden |
| Mineralknoopstatus | DB `mineralnodes` |
| Plantensoorten per zone | DB `plantrules` + regel**bestanden** (`$GameRoot/plantrules/*.txt`) |
| Zoneconfiguratie (vruchtbaarheid, grootte, type, regelsysteem) | DB `zones` |
| Oerconfiguratie | DB `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1-vs-2 byte controleafhandeling, veilige nulvulling bij grootteschil);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty-vlag, MD5 + tmp-hernoeming, stop-opslag);
     Bootstrapper/Modules/TerrainsModule.cs (laaglaadvolgorde: blocks, control, plants,
     altitude, blend; slope + passable afleiding; 2u saver + 2u materiaalproces). -->