---
title: "Pola rud"
description: "Tabele minerals i mineralconfigs, wzory generowania węzłów, cykl życia węzłów oraz mechanika wydobycia."
weight: 30
---

# Pola rud

Dane o rudach istnieją na dwóch poziomach: **per-typ** (`minerals` — czym jest materiał
i ile daje jedno wydobycie) oraz **per-strefa-per-typ** (`mineralconfigs` — ile węzłów,
jak duże, jak zapełnione). Stan węzłów w czasie działania serwera znajduje się w tabeli `mineralnodes`.

## `minerals`

| Kolumna | Typ | Używane przez | Znaczenie |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | Liczba porządkowa wyliczenia `MaterialType` (1=Titan … 19=DHDT, 0=Undefined). Wszystkie złączenia używają `mineralconfigs.materialtype = minerals.idx`. |
| `name` | varchar | `ToMaterialType()` | Nazwa typu ("titan", "crude", …). |
| `definition` | int | `MaterialHelper` → item | Definicja przedmiotu generowana przez wydobycie (np. titan → def 168). |
| `amount` | int | `DrillerModule` | **Bazowe jednostki na cykl wydobycia** (titan 1500, crude 1500, stermonit 975, liquizit 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = Stała (`OreLayer`), 1 = Płynna (`LiquidLayer`). |
| `enablereffectrequired` | bit | bramkowanie modułów | Czy do wydobycia wymagany jest efekt aktywujący (enabler). |
| `geoscandocument` | int | przedmioty skanowania | Przedmiot dokumentu geoskanu dla tego materiału. |

## `mineralconfigs`

Jeden wiersz na parę (strefa, materiał). Odczytywany przez `MineralConfigurationReader` → jedna
warstwa `MineralLayer` na wiersz:

| Kolumna | Typ | Używane przez | Znaczenie |
|---|---|---|---|
| `zoneId` | int | budowa warstwy | Strefa właściciela. |
| `materialtype` | int | → `minerals.idx` | Materiał. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | Liczba węzłów tego typu utrzymywana przez strefę. |
| `maxtilespernode` | int | generator | Maksymalna liczba kafli na plamę węzła; określa też promień odstępu (poniżej). |
| `totalamountpernode` | int | generator | Całkowity materiał w nowym węźle, rozdzielony pomiędzy kafle plamy. |
| `minthreshold` | double | generator | Minimalne znormalizowane wypełnienie na kafel (0–1); kafle poniżej progu są odrzucane. |

### Wzory generowania węzłów (`MineralNodeGeneratorBase.cs`)

Dla nowego węzła danego typu o powyższej konfiguracji:

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = pozycja startowa musi być ≥ 2 × radius od najbliższego istniejącego węzła
blob    = zalewanie błądzeniem losowym (pędzel 4-kaflowy) do maxtilespernode prawidłowych kafli
tile[i] = ( noise[i] / max(noise) ) znormalizowane do [minthreshold, 1]
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // szum/jitter, następnie obcięte do uint
```

Strefy wyłączone (keep-out) wokół baz dokowania i teleportów (`KeepOutDist`): epriton = 100 kafli
(`MINERAL_DISTANCE_FROM_BASE_MIN`), ruda flux = 200; wszystkie pozostałe typy = 0.

### Praktyczny przykład — ropa Daoden (zone_ASI) crude (id 2)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → odstęp ≥ 80 kafli
blob    = do 1257 kafli
tile    = udział ∈ [0.5, 1.0] × (125,000,000 / Σnormalized) × jitter
```

Pełny węzeł ropy zawiera 125 mln jednostek; przy bazowym wydobyciu 1 500 jednostek na cykl
wiertła daje to ~83 000 cykli materiału na węzeł, ~666 000 w 8 węzłach strefy.

## Stan węzła — `mineralnodes`

| Kolumna | Znaczenie |
|---|---|
| `zoneid`, `materialtype` | Strefa właściciela + typ |
| `x, y, width, height` | Ramka ograniczająca węzła (obszar plamy) |
| `data` | Skompresowane wartości `uint` na kafel (wierszowo w ramce) |

Cykl życia (`MineralNode.cs`, `MineralLayer.cs`):

- **Ładowanie**: przy starcie strefy ładowane są wszystkie zapisane węzły; węzeł, którego suma wynosi ≤ **1%**
  `totalamountpernode`, jest zamiast tego usuwany.
- **Uzupełnianie**: jeśli przetrwało mniej niż `maxnodes`, generowane są nowe węzły (wzór powyżej).
- **Wygaśnięcie**: **nietknięty** węzeł wygasa po **7 dniach** (`TimeTracker`); wydobycie
  resetuje licznik. Węzeł, którego maksymalna wartość kafla osiągnie 0, również wygasa.
- **Trwałość**: zmodyfikowane węzły są spłukiwane do bazy danych co **30 minut** przez timer zapisu.
- **Powiązanie z rudą flux**: zmniejszenie/wygaśnięcie węzła `FluxOre` publikuje
  `OreNpcSpawnMessage` → na co nasłuchuje spawner NPC (`OreNPCSpawner`).

## Mechanika wydobycia (`MineralExtractor.cs`, `DrillerModule.cs`)

Ilość wydobycia to `minerals.amount` przeskalowane przez właściwość robota
`mining_amount_modifier` (agregowaną z `mining_amount_modifier`,
`effect_mining_amount_modifier`, `drone_amplification_mining_amount_modifier`,
`effect_excavator_mining_amount_modifier`).

- **Stała** (`OreLayer`): pobiera `min(wartość kafla, amount)` z **pojedynczego kafla**,
  na którym stoi robot.
- **Płynna** (`LiquidLayer`): drenuje **cały węzeł**, najpierw najbliższe kafle
  (kolejka priorytetowa wg kwadratu odległości), aż do zaspokojenia wymaganej ilości.
- **Żwir** (tylko strefy szkoleniowe, `GravelLayer`): odczytuje wartość kafla, ale jej
  nie zmniejsza — węzły żwiru są niewyczerpywalne.

Wydajność według typu (produkty rafinacji) znajduje się w [Rudy](/content/ores/); liczba węzłów
na strefę znajduje się w [Indeks stref](/zones/zone-index/).

<!-- Notatki deweloperskie: Zones/Terrains/Materials/Minerals/MineralConfiguration.cs
     (reader + config), MineralLayer.cs (LoadMineralNodes 1% delete + top-up,
     GenerateNewNode radius/tile/amount wiring, FluxOre events),
     Generators/MineralNodeGeneratorBase.cs (FindStartPosition, NormalizeNoise,
     CreateMineralNode, KeepOutDist), Generators/RandomWalkMineralNodeGenerator.cs
     (flood fill, limit 50k kroków), MineralNode.cs (wartości uint[], 7-dniowe wygaśnięcie,
     30-min zapis), MineralNodeRepository.cs (tabela mineralnodes, skompresowane
     wartości), Minerals/MineralExtractor.cs (wydobycie stałe/płynne/żwir),
     Modules/DrillerModule.cs (właściwość amount + modyfikatory), Materials/MaterialHelper.cs
     (minerals.definition -> item), Zones/DistanceConstants.cs
     (MINERAL_DISTANCE_FROM_BASE_MIN = 100). -->
