---
title: "Pliki stref"
description: "Pliki binarnych warstw terenu: nazywanie, układy struktur, bity flag, cykl zapisu oraz to, co znajduje się w bazie danych."
weight: 50
---

# Pliki stref

Teren strefy jest przechowywany jako zestaw **binarnych plików warstw**, po jednym na warstwę, obok danych strefy. Nazwa to `{layer}.{zoneid:0000}.bin`
(`Zone.CreateTerrainDataFilename`) — np. `plants.0042.bin` dla strefy 42. Warstwy to
płaskie tablice struktur o stałym rozmiarze, **wierszowo, szerokość × wysokość** (domyślnie 2048×2048 =
4 194 304 kafle).

## Warstwy

| Plik | Struktura | Bajtów/kafel | Zawartość |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (bajt) + `height` (bajt) — przeszkody, rośliny, dekoracje, wyspy |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (lub 1) | bity sterowania na kafel (patrz niżej) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | stan rośliny na kafel (poniżej) |
| `altitude.NNNN.bin` | `ushort` | 2 | wysokość; porównywana jako `value / 4` w sprawdzianach roślin (skalowanie współrzędnych klienta) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | tylko strefy terraformowalne: maska blendu na kafel (poniżej) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | tylko strefy terraformowalne: wysokość przed terraformowaniem na dysku — **nie odczytywana przez serwer** (poniżej) |

Wyprowadzone warstwy (obliczane przy ładowaniu, **nie** pliki): `SlopeLayer` (z wysokości) i
`Passable` (z bloków + nachylenia + przechodnich pozycji z bazy danych, tylko strefy nieterraformowalne).
W strefach terraformowalnych wysokość jest zawijana w `TerraformableAltitude`, który
przy ładowaniu oblicza zakres **bariery** na kafel: `blend/65535` miesza stałe
1850 → oryginalna wysokość (min) i 30000 → oryginalna wysokość (max), a następnie ogranicza
zakres tak, aby zawsze zawierał bieżącą wartość. Aktualizacje wysokości po terraformowaniu są ograniczane
do tej bariery — więc `blend = 0` pozostawia kafel swobodnie terraformowalny między 1850 a
30000, a `blend = 65535` przypina go do oryginalnej wysokości. (Pliki
`altitude_original.NNNN.bin` na dysku zawierają wysokości przed terraformowaniem dla zewnętrznych
narzędzi; serwer pobiera swój snapshot oryginalnej wysokości w pamięci z załadowanego
`altitude.NNNN.bin` i nigdy nie odczytuje tej nazwy pliku.)

### `BlockingInfo` (2 bajty)

`flags` to `BlockingFlags` (bajt):

| Bit | Nazwa |
|---|---|
| 1 | Przeszkoda |
| 2 | Roślina |
| 4 | Dekoracja |
| 8 | Wyspa |

`NonNaturally` = Dekoracja \| Wyspa \| Przeszkoda. `height` to wysokość blokowania ruchu kafela
(wysokość blokowania roślin jest zapisywana tutaj przez kod wzrostu roślin).

### `TerrainControlFlags` (warstwa sterowania)

Zbiór flag `ushort`:

| Bit | Nazwa |
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

(Numeracja 512/1024 odpowiada `1 << n`; bit 32 jest nieużywany.) Kafel pozwala na rośliny, gdy
`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`.

**Ciekawostka dotycząca przechowywania**: loader akceptuje zarówno pliki sterowania **1 bajt/kafel**, jak i **2 bajty/kafel** —
jeśli długość pliku jest równa liczbie kafli, każdy bajt jest rozszerzany do
`TerrainControlFlags`; w przeciwnym razie odczytywana jest surowa tablica `ushort`
(`LayerFileIO.LoadLayerData`). Wszystkie aktywne strefy używają **formatu 2-bajtowego**
(`control.0000.bin` = 8 388 608 B = 4 194 304 × 2); format 1-bajtowy (4 MB) to
legacy'owy fallback, który loader nadal obsługuje.

### `PlantInfo` (7 bajtów) — stan kafela rośliny

| Bajt | Pole | Znaczenie |
|---|---|---|
| 0 | `type` | `PlantType` (0 = pusty; 1..19 wg [Pola roślin](/pl/formats/plant-fields/)) |
| 1 | `state` | Indeks stanu wzrostu (do tabeli `state_N` reguły) |
| 2 | `time` | Akumulator ticków wzrostu (porównywany z `growRate` reguły) |
| 3 | `spawn` | **Prawdopodobieństwo spawnu na kafel, wbudowane w plik strefy; serwer nigdy go nie zapisuje** (nie ma żadnego przypisania w całym kodzie — `PlantInfo.Clear()` celowo go zachowuje). 0 = jałowy kafel: każda roślina na nim jest natychmiast usuwana podczas walidacji, a nigdy nie kiełkuje. W przeciwnym razie jest to bramka na próbę: podczas przejścia regeneracji roślin losowy pusty kafel jest akceptowany tylko wtedy, gdy `FastRandom.NextByte() < spawn`, czyli szansa na kafel ≈ `spawn/256`. |
| 4 | `health` | Bieżące HP (proporcja zdrowia reguły dla danego stanu) |
| 5 | `material` | Bieżąca ilość owocu (0–255) |
| 6 | `groundType` | Bajt `GroundType` (0=Darkrocks … 17=piaskowy, 20=niezdefiniowany) — klasa terenu, z którą porównuje `allowedTerrainTypes` reguły rośliny |

### Przykład — rozmiary plików dla strefy 2048×2048 (zweryfikowane z plikami produkcyjnymi)

```
blocks    4 194 304 kafle × 2 B = 8 388 608 B (8 MB)
plants    4 194 304 kafle × 7 B = 29 360 128 B (28 MB)
altitude  4 194 304 kafle × 2 B = 8 388 608 B (8 MB)
control   4 194 304 kafle × 2 B = 8 388 608 B (8 MB, format 2-bajtowy; plik legacy 1-bajtowy miałby 4 MB)
```

**Weryfikacja na danych produkcyjnych** (`plants.0106.bin`, terraformowalna strefa gamma): wszystkie 4 194 304
kafle mają `spawn = 0x83` (131/256 ≈ 51% szansa na próbę) i `type = 0`, z wyjątkiem
10 kafli z żywymi roślinami — mapa spawnu to wbudowane pole prawdopodobieństwa
dla całej strefy, niezależne od bieżącej lokalizacji roślin.

Nie każda strefa ma każdy plik: 66 z 84 stref zawiera `plants.NNNN.bin`. 18
stref bez tego pliku to zastąpione legacy'owe warianty gamma (`zone_tm_g_*`, `zone_ics_g_*`,
`zone_asi_g_*`, id 20–43), które nie są ładowane. Katalog warstw to
`$GameRoot/layers/`.

## Cykl zapisu (`IntervalLayerSaver.cs`)

- Każda modyfikowalna warstwa (blocks, control, plants, altitude) jest obserwowana przez
  `IntervalLayerSaver<T>`; każda zmiana kafela/obszaru ustawia flagę modyfikacji.
- Saver jest zarejestrowany jako proces na timerze **2-godzinnym**
  (`TerrainsModule`); zmodyfikowana warstwa jest zapisywana, gdy tick się wykona.
- Zapisy trafiają do pliku `.tmp<ticks>.bin`, są **weryfikowane MD5** po ponownym odczycie i
  dopiero wtedy zastępują właściwy plik.
- Przy zatrzymaniu serwera zmodyfikowane warstwy są zapisywane jeszcze raz.
- Węzły mineralne **nie** znajdują się w tych plikach — są przechowywane w tabeli `mineralnodes` bazy
  danych (spłukanie co 30 minut, patrz [Pola rudy](/pl/formats/ore-fields/)).

## Co jest, a co nie jest plikiem

| Dane | Gdzie |
|---|---|
| Warstwy terenu (blocks/control/plants/altitude) | pliki `.bin` |
| Stan węzłów rud | baza danych `mineralnodes` |
| Gatunki roślin na strefę | baza danych `plantrules` + **pliki** reguł (`$GameRoot/plantrules/*.txt`) |
| Konfiguracja strefy (użyźnienie, rozmiar, typ, zestaw reguł) | baza danych `zones` |
| Konfiguracja rud | baza danych `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     obsługa 1-vs-2 bajtów w sterowaniu, bezpieczne wypełnianie zerami przy niezgodności rozmiaru);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (flaga modyfikacji, MD5 + zmiana nazwy tmp, zapis przy zatrzymaniu);
     Bootstrapper/Modules/TerrainsModule.cs (kolejność ładowania warstw: blocks, control, plants,
     altitude, blend; wyprowadzanie nachylenia + przechodniości; saver 2h + proces materiałów 2h). -->