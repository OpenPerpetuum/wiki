---
title: "Zónové soubory"
description: "Binární soubory terénních vrstev: pojmenování, rozložení struktur, bitové příznaky, cyklus ukládání a co se místo toho nachází v databázi."
weight: 50
---

# Zónové soubory

Terén zóny je uložen jako sada **binárních souborů vrstev**, jeden pro každou vrstvu, vedle
dat zóny. Název má tvar `{layer}.{zoneid:0000}.bin`
(`Zone.CreateTerrainDataFilename`) — např. `plants.0042.bin` pro zónu 42. Vrstvy jsou
ploché pole struktur pevné velikosti, **řádkově, šířka × výška** (výchozí 2048×2048 =
4 194 304 dlaždic).

## Vrstvy

| Soubor | Struktura | Bajtů/dlaždice | Obsah |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (bajt) + `height` (bajt) — překážky, rostliny, dekorace, ostrovy |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (nebo 1) | ovládací bity pro každou dlaždice (viz zvláštnost níže) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | stav rostliny pro každou dlaždice (viz níže) |
| `altitude.NNNN.bin` | `ushort` | 2 | nadmořská výška; při kontrolách rostlin porovnáváno jako `value / 4` (škálování souřadnic klienta) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | pouze terafórovatelné zóny: maska přechodu pro každou dlaždice (viz níže) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | pouze terafórovatelné zóny: nadmořská výška před terafórováním na disku — **server tento soubor nečte** (viz níže) |

Odvozené vrstvy (vypočtené při načtení, **nejsou** soubory): `SlopeLayer` (z nadmořské výšky) a
`Passable` (z blocks + sklonu + pozic průchodnosti v DB, pouze pro neterafórovatelné zóny).
U terafórovatelných zón je nadmořská výška obalená do `TerraformableAltitude`, která
při načtení vypočítá rozsah **bariéry** pro každou dlaždice: `blend/65535` míchá konstanty
1850 → původní nadmořská výška (min) a 30000 → původní nadmořská výška (max), poté omezí
rozsah tak, aby vždy obsahoval aktuální hodnotu. Aktualizace terafórované nadmořské výšky jsou
omezeny do této bariéry — takže `blend = 0` ponechává dlaždice volně terafórovatelnou mezi 1850 a
30000, zatímco `blend = 65535` ji připne k původní nadmořské výšce. (Soubory
`altitude_original.NNNN.bin` na disku obsahují nadmořské výšky před terafórováním pro externí
nástroje; server si svůj snímek původní nadmořské výšky bere v paměti z načteného
`altitude.NNNN.bin` a tento název souboru nikdy nečte.)

### `BlockingInfo` (2 bajty)

`flags` je `BlockingFlags` (bajt):

| Bit | Název |
|---|---|
| 1 | Obstacle |
| 2 | Plant |
| 4 | Decor |
| 8 | Island |

`NonNaturally` = Decor \| Island \| Obstacle. `height` je výška blokování chůze dlaždice
(výška blokování rostlin je sem zapisována kódem růstu rostlin).

### `TerrainControlFlags` (ovládací vrstva)

Množina příznaků `ushort`:

| Bit | Název |
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

(Číslování 512/1024 odpovídá `1 << n`; bit 32 není použit.) Dlaždice umožňuje rostliny, když
`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`.

**Zvláštnost ukládání**: načtení přijímá ovládací soubory jak ve formátu **1 bajt/dlaždice**,
tak **2 bajty/dlaždice** — pokud délka souboru odpovídá počtu dlaždic, každý bajt se rozšíří na
`TerrainControlFlags`; jinak se načte pole `ushort` tak, jak je
(`LayerFileIO.LoadLayerData`). Všechny aktivní zóny používají **2bajtovou formu**
(`control.0000.bin` = 8 388 608 B = 4 194 304 × 2); 1bajtová forma (4 MB) je
zastaralá záložní varianta, kterou načtení stále podporuje.

### `PlantInfo` (7 bajtů) — stav dlaždice s rostlinou

| Bajt | Pole | Význam |
|---|---|---|
| 0 | `type` | `PlantType` (0 = prázdné; 1..19 dle [Pole rostlin](/cs/formats/plant-fields/)) |
| 1 | `state` | Index růstového stavu (do tabulky `state_N` pravidla) |
| 2 | `time` | Akumulátor růstových tiků (porovnáváno s `growRate` pravidla) |
| 3 | `spawn` | **Pravděpodobnost výskytu pro každou dlaždice, předpočítaná do zónového souboru; server ji nikdy nezapisuje** (v kódu neexistuje žádná přiřazení — `PlantInfo.Clear()` ji záměrně zachovává). 0 = sterilní dlaždice: jakákoliv rostlina na ní je okamžitě odstraněna při validaci a nikdy se na ní nevyroste. Jinak slouží jako brána pro každý pokus: během procházky regenerace rostlin je náhodně vybraná prázdná dlaždice přijata pouze pokud `FastRandom.NextByte() < spawn`, tj. pravděpodobnost úspěchu pro dlaždice ≈ `spawn/256`. |
| 4 | `health` | Aktuální HP (poměr z HP pravidla pro daný stav) |
| 5 | `material` | Aktuální množství ovoce (0–255) |
| 6 | `groundType` | Bajt `GroundType` (0=Darkrocks … 17=Sand-ish, 20=nedefinováno) — třída terénu, proti které kontroluje `allowedTerrainTypes` pravidla rostliny |

### Ukázka — velikosti souborů pro zónu 2048×2048 (ověřeno proti aktivním souborům)

```
blocks    4 194 304 dlaždic × 2 B = 8 388 608 B (8 MB)
plants    4 194 304 dlaždic × 7 B = 29 360 128 B (28 MB)
altitude  4 194 304 dlaždic × 2 B = 8 388 608 B (8 MB)
control   4 194 304 dlaždic × 2 B = 8 388 608 B (8 MB, 2bajtová forma; 1bajtový zastaralý soubor by byl 4 MB)
```

**Kontrola živých dat** (`plants.0106.bin`, terafórovatelná gamma zóna): všech 4 194 304
dlaždic nese `spawn = 0x83` (131/256 ≈ 51 % pravděpodobnost na pokus) a `type = 0`, kromě
10 dlaždic s živými rostlinami — mapa výskytu je předpočítané pravděpodobnostní pole pro celou
zónu, nezávislé na tom, kde se rostliny aktuálně nacházejí.

Ne každá zóna má všechny soubory: 66 ze 84 zón obsahuje `plants.NNNN.bin`. 18 zón bez něj
jsou nahrazené zastaralé gamma varianty (`zone_tm_g_*`, `zone_ics_g_*`,
`zone_asi_g_*`, id 20–43), které se nenakládají. Adresář vrstev je
`$GameRoot/layers/`.

## Cyklus ukládání (`IntervalLayerSaver.cs`)

- Každá měnitelná vrstva (blocks, control, plants, altitude) je sledována
  instancí `IntervalLayerSaver<T>`; jakýkoliv zápis dlaždice/oblasti nastaví příznak změny.
- Ukládač je registrován jako proces na **2hodinovém** časovači
  (`TerrainsModule`); vrstva se změnou se zapíše, když tik nastane.
- Zápisy jdou do souboru `.tmp<ticks>.bin`, jsou **ověřeny MD5** proti přečtení a
  až poté nahradí skutečný soubor.
- Při zastavení serveru se vrstvy se změnami uloží ještě jednou.
- Minerální uzly **nejsou** v těchto souborech — perzistují do tabulky `mineralnodes`
  v databázi (odkládání po 30 minutách, viz [Pole rudy](/cs/formats/ore-fields/)).

## Co je a co není soubor

| Data | Kde |
|---|---|
| Terénní vrstvy (blocks/control/plants/altitude) | `.bin` soubory |
| Stav minerálních uzlů | DB `mineralnodes` |
| Druhy rostlin pro zónu | DB `plantrules` + soubory **pravidel** (`$GameRoot/plantrules/*.txt`) |
| Konfigurace zóny (úrodnost, velikost, typ, sada pravidel) | DB `zones` |
| Konfigurace rudy | DB `mineralconfigs` |

<!-- Poznámky pro vývojáře: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     zpracování 1 vs 2 bajtů pro control, bezpečné doplnění nulou při neshodě velikosti);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (příznak změny, MD5 + přejmenování tmp, ukládání při zastavení);
     Bootstrapper/Modules/TerrainsModule.cs (pořadí načítání vrstev: blocks, control, plants,
     altitude, blend; odvození sklonu a průchodnosti; 2h ukládač + 2h proces materiálů). -->