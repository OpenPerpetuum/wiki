---
title: "Pole rud"
description: "Tabulky minerals a mineralconfigs, vzorce pro generování nodů, životní cyklus nodů a mechaniky těžby."
weight: 30
---

# Pole rud

Data rud mají dvě úrovně: **podle typu** (`minerals` — o jaký materiál jde a kolik
jedna těžba vynese) a **podle zóny a typu** (`mineralconfigs` — kolik nodů,
jak velkých, jak plných). Stav nodů za běhu je uložen v tabulce `mineralnodes`.

## `minerals`

| Sloupec | Typ | Použito v | Význam |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | Pořadové číslo enumu `MaterialType` (1=Titan … 19=DHDT, 0=Undefined). Všechna propojení používají `mineralconfigs.materialtype = minerals.idx`. |
| `name` | varchar | `ToMaterialType()` | Název typu ("titan", "crude", …). |
| `definition` | int | `MaterialHelper` → item | Definice předmětu vytvořeného těžbou (např. titan → def 168). |
| `amount` | int | `DrillerModule` | **Základní jednotky na těžební cyklus** (titan 1500, crude 1500, stermonit 975, liquizit 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = Pevná (`OreLayer`), 1 = Kapalná (`LiquidLayer`). |
| `enablereffectrequired` | bit | přístup k modulu | Zda je pro těžbu vyžadován enabler efekt. |
| `geoscandocument` | int | předměty skenu | Předmět dokumentu geo-skenu pro tento materiál. |

## `mineralconfigs`

Jeden řádek pro dvojici (zóna, materiál). Načítáno přes `MineralConfigurationReader` → jedna
vrstva `MineralLayer` na řádek:

| Sloupec | Typ | Použito v | Význam |
|---|---|---|---|
| `zoneId` | int | konstrukce vrstvy | Vlastnící zóna. |
| `materialtype` | int | → `minerals.idx` | Daný materiál. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | Počet nodů tohoto typu, které zóna udržuje. |
| `maxtilespernode` | int | generátor | Maximální počet dlaždic na blob nodu; určuje také rozestupový poloměr (níže). |
| `totalamountpernode` | int | generátor | Celkové množství materiálu v novém nodu, rozdělené mezi dlaždice blobu. |
| `minthreshold` | double | generátor | Minimální normalizované naplnění dlaždice (0–1); dlaždice pod touto hodnotou jsou vynechány. |

### Vzorce generování nodů (`MineralNodeGeneratorBase.cs`)

Pro nový nod typu s výše uvedenou konfigurací:

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = počáteční pozice musí být ≥ 2 × radius od nejbližšího existujícího nodu
blob    = random-walk flood fill (štětec o velikosti 4 dlaždic) až do maxtilespernode platných dlaždic
tile[i] = ( noise[i] / max(noise) ) normalizováno do [minthreshold, 1]
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // šum (jitter), poté oříznuto na uint
```

Ochranné zóny kolem dokovacích základen a teleportů (`KeepOutDist`): epriton = 100 dlaždic
(`MINERAL_DISTANCE_FROM_BASE_MIN`), flux ore = 200; všechny ostatní typy = 0.

### Příklad z praxe — Daoden (zone_ASI) surová ropa / crude (id 2)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → rozestup ≥ 80 dlaždic
blob    = až 1257 dlaždic
tile    = podíl ∈ [0.5, 1.0] × (125,000,000 / Σnormalized) × jitter
```

Plný ropný nod obsahuje 125 milionů jednotek; při základní těžbě 1 500 jednotek na vrtací cyklus
to představuje ~83 000 cyklů materiálu na nod, tedy ~666 000 napříč 8 nody v zóně.

## Stav nodu — `mineralnodes`

| Sloupec | Význam |
|---|---|
| `zoneid`, `materialtype` | Vlastnící zóna + typ |
| `x, y, width, height` | Ohraničující rámeček nodu (plocha blobu) |
| `data` | Komprimovaný `uint` na dlaždici (po řádcích uvnitř rámečku) |

Životní cyklus (`MineralNode.cs`, `MineralLayer.cs`):

- **Načtení (Load)**: při spuštění zóny se načtou všechny uložené nody; nod, jehož celkový obsah
  je ≤ **1 %** z `totalamountpernode`, je namísto toho smazán.
- **Doplnění (Top-up)**: pokud přežilo méně než `maxnodes`, vygenerují se nové nody (vzorec výše).
- **Expirace (Expiry)**: **nedotčený** nod expiruje po **7 dnech** (`TimeTracker`); těžba
  resetuje odpočet. Nod, jehož maximální hodnota dlaždice klesne na 0, rovněž expiruje.
- **Uložení (Persistence)**: změněné nody se zapisují do DB v **30minutovém** intervalu ukládání.
- **Propojení s flux ore**: pokles nebo expirace nodu `FluxOre` odešle
  `OreNpcSpawnMessage` → NPC spawner na zprávu reaguje (`OreNPCSpawner`).

## Mechaniky těžby (`MineralExtractor.cs`, `DrillerModule.cs`)

Vytěžené množství odpovídá hodnotě `minerals.amount` vynásobené vlastností robota
`mining_amount_modifier` (agregováno z `mining_amount_modifier`,
`effect_mining_amount_modifier`, `drone_amplification_mining_amount_modifier`,
`effect_excavator_mining_amount_modifier`).

- **Pevná ruda** (`OreLayer`): odebírá `min(hodnota dlaždice, amount)` z **jediné dlaždice**,
  na které robot stojí.
- **Kapalná ruda** (`LiquidLayer`): čerpá z **celého nodu**, od nejbližších dlaždic
  (prioritní fronta podle čtverce vzdálenosti), dokud není množství uspokojeno.
- **Štěrk (Gravel)** (pouze tréninkové zóny, `GravelLayer`): čte hodnotu dlaždice, ale
  nesnižuje ji — štěrkové nody jsou nevyčerpatelné.

Výtěžnost podle typu (rafinované produkty) najdete v sekci [Rudy](/content/ores/); počty nodů
podle zón v sekci [Rejstřík zón](/zones/zone-index/).

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
