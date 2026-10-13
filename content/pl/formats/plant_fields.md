---
title: "Pola roślin"
description: "Format pliku reguł roślin (GenXY), każde pole reguły z typem, wartością domyślną i konsumentem, plus automat stanów wzrostu."
weight: 20
---

# Pola roślin

Zachowanie roślin jest definiowane dla każdego gatunku przez **plik reguł** (zwykły tekst)
w katalogu `$GameRoot/plantrules/`. Informacja o tym, które pliki należą do danej strefy,
znajduje się w mapowaniu bazy danych `plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset`;
ładowaniem i łączeniem zajmuje się `PlantRuleLoader.cs`, a mapowaniem pól na obiekty `PlantRule.cs`.

## Format pliku

Jedna para `key=value` na linię; komentarze w stylu `//` są odrzucane. Wartości używają
**znaków tokenów GenXY** (`GenxyReader.cs` — pierwszy znak wybiera typ i podstawę liczbową):

| Token | Analizowane jako | Przykład |
|---|---|---|
| `n` | int, dziesiętny | `n125`, `n-1` |
| `N` | int[], dziesiętny, rozdzielany przecinkami | `N5,5,5,5` |
| `f` | double, dziesiętny | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **szesnastkowy** | `iFF` |
| `L` | long, **szesnastkowy** | `L100` |
| `4` | int[], **szesnastkowy** | `41,2,3` → [1, 2, 3] |

### ⚠ Pułapka „nagiej tablicy”

Pliki zawierają także wartości w rodzaju `blockingHeight=40,3,3,4` **bez jawnego tokenu**.
Parser nie traktuje ich w żaden specjalny sposób: początkowa cyfra `4` jest traktowana jako token
`IntegerArray` (szesnastkowy), a reszta jest parsowana szesnastkowo. Zatem:

```
blockingHeight=40,3,3,4   →  token '4' + tablica hex "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  token 'N' + tablica dziesiętna     →  [0, 8, 11, 14]
```

Oba zapisy dają `int[]`, a początkowe `0` to wartość, którą „połyka” cyfra `4`. Z tego powodu
każda naga tablica w dostarczanych plikach zaczyna się od `4` — jest to konwencja zachowująca
zamierzoną wartość pierwszego elementu. **Przy pisaniu nowych plików reguł należy jawnie używać
prefiksu `N`**; wartości ≥ 10 w nagiej tablicy byłyby parsowane szesnastkowo, co po cichu
zmieniłoby ich znaczenie.

### Dziedziczenie

Klucz `source=$other_rule.txt` najpierw ładuje plik `other_rule.txt`, a następnie stosuje klucze
bieżącego pliku jako nadpisania (`PlantRuleLoader.LoadRuleByName`). Przykład:
`irontree_t2.txt` to po prostu:

```
source=$irontree_lo.txt
fruitAmount=n125
```

## Referencja pól

Wszystkie pola są odczytywane ze scalonego słownika ustawień (`PlantRule.cs`). Brakujące klucze
przyjmują pokazane wartości domyślne.

| Klucz | Typ / domyślna | Używane przez | Działanie |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | Wartość wyliczenia `PlantType` dla danego gatunku (1=GrassA … 19=Devrinol). Także bajt `PlantInfo.type` przechowywany na kafel. |
| `name` | string | ładunek info dla klienta | Wyświetlana nazwa. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | Waga w losowaniu ważonym wybierającym gatunek dla kafla **bez** sąsiadujących roślin. 0 = nigdy się nie spawnuje. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | Mnożnik wagi, gdy kafel **ma** sąsiadów: waga kandydata = `neighbourCount × spreading`. 0 = nigdy nie wygrywa losowania rozprzestrzeniania. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | Minimalna odległość od istniejącej rośliny tego samego typu; 0/ujemna = brak limitu. |
| `growRate` | int (0) | `GrowPlantOnTile` | Liczba ticków sześcianu (cube), jaką bajt `PlantInfo.time` musi zgromadzić przed przejściem automatu stanów. Wyższa wartość = wolniejszy wzrost. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | Dozwolony przedział nachylenia wyliczonej warstwy nachylenia. Poza tym przedziałem roślina jest usuwana. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | Przedział wysokości, porównywany z `Altitude / 4` (dzielnik `/4` odpowiada współrzędnym klienta). Skalowany przez strefowe `plantaltitudescale`. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | Przedział dla `altitude/4 − waterLevel/4` — tworzy roślinność przybrzeżną. Również skalowany przez wysokość. |
| `allowedTerrainTypes` | int[] (pusty) | `ValidateTile` | Dozwolone bajty `groundType` (patrz [Pliki stref](/pl/formats/zone-files/)). Pusty = nigdzie. Pomijany w całości, gdy ustawione jest `allowedOnNonNatural`. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | Pierwszy stan dający owoce. −1 ⇒ `NotFruiting` (nigdy nie nadaje się do zbioru). |
| `fruitDefinition` | int (−1) | zbiory | Definicja przedmiotu owocu. |
| `fruitMaterialName` | string | wyświetlanie | Nazwa owocu (np. `$prismocitae`). |
| `fruitAmount` | byte (0), obcięte 0–255 | `GrowPlantOnTile` | Maksymalna ilość owocu na roślinę. Pierwsze wejście w stan owocowania wypełnia 5–15%; każdy kolejny tick wzrostu dodaje 15–25%, z limitem 100%. |
| `health` | byte[] per stan | `GrowPlantOnTile`, walka | Punkty życia (HP) na każdy stan wzrostu. Przy zmianie stanu bieżący **stosunek** zdrowia jest przenoszony do nowego stanu. |
| `blockingHeight` | int[] per stan | `GrowPlantOnTile`, zliczanie spawnu | Wysokość blokowania na stan; `>0` ustawia bit `Plant` w warstwie blokowania (walkable=false) i sprawia, że roślina wlicza się do celu żyzności strefy. |
| `maxAmount` | int (−1) | `SpawnPlants` | Limit tej rośliny na strefę; −1 = bez limitu. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, losowanie żyzności | Wykluczona ze **wszystkich** naturalnych spawnów; istnieje tylko tam, gdzie posadził ją gracz. |
| `damageScale` | double (1.0) | walka roślin | Mnożnik otrzymywanych obrażeń. |
| `onlyOnUnprotectedZone` | bool (0) | walidacja spawnu | Rośnie wyłącznie w strefach niechronionych. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | Pomija sprawdzanie bitów kontrolnych, typu terenu i nachylenia (rośnie na kaflach „sztucznych”). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (śmierć) | Przy śmierci czyści bity kontrolne ConcreteA/B pod kaflem. |
| `state_N` | int[] | `GetNextState` | Wybory kolejnego stanu dla stanu `N` — każdy element wybierany jest **równomiernie losowo**. |
| `action_N` | int[] | `GetNextState` | Wybory kolejnego `PlantType` dla stanu `N` (losowanie równomierne). Wartość akcji `0` (NotDefined) oznacza **śmierć**. |

Spójność jest weryfikowana przy ładowaniu (`CheckConsistency`): `len(health) == len(blockingHeight) == liczba stanów`.

## Automat stanów wzrostu

W każdym ticku sześcianu 32×32, dla każdego kafla z rośliną (`GrowPlantOnTile`):

1. Jeśli `time < growRate`: `time++`, koniec.
2. W przeciwnym razie: `time = 0`, losuj `state_N` oraz `action_N` dla bieżącego stanu:
   - `action == 0` → roślina umiera (sygnał likwidacji `type:0, state:1` dla klienta);
     jeśli `placesConcrete`, usuń beton pod kaflem.
   - w przeciwnym razie → `type = action`, `state = next`, `health = healthRatio × Health[newState]` (zachowany stosunek uszkodzeń).
   - Owoce: jeśli `newState == fruitingState`, `material = fruitAmount × uniform(0.05, 0.15)`;
     jeśli `newState > fruitingState`, `material += fruitAmount × uniform(0.15, 0.25)` (z limitem `fruitAmount`);
     w przeciwnym razie `material = 0`.
   - Wysokość blokowania = `blockingHeight[newState]`; bit `Plant` w warstwie blokowania przyjmuje stan `height > 0`.

### Praktyczny przykład — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → waga 1/… w losowaniu bez sąsiadów
spreading=n2        → waga klastra = 2 × sąsiedzi
growRate=n1         → losuje stan w każdym ticku sześcianu (szybko)
maxAmount=n190      → maksymalnie 190 na sześcian
health=N5,5,5,5     → 5 HP w każdym stanie
blockingHeight=40,0,0,0 → parsowane jako [0,0,0,0]: trawa NIGDY nie blokuje
fruitingState=n-1   → NotFruiting: trawa nigdy nie daje plonów
state_0=40,0,1      → [0,0,1]: 2/3 pozostaje w stanie 0, 1/3 przechodzi dalej
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → w stanie końcowym: 3/4 zostaje, 1/4 ginie
```

Zatem kafel trawy: przechodzi średnio o jeden stan co 3 ticki, a w ostatnim stanie ma
25% szansy na tick na śmierć i ponowne zasianie — nieustannie odnawiający się gatunek
okrywowy bez owoców.

### Praktyczny przykład — `wall.txt` (12 stanów, prefiks `N`)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (może cofnąć stan), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: fortyfikacja sadzona przez gracza,
która istnieje wyłącznie w strefach niechronionych, ograniczona do 15 na sześcian,
rosnąca (i okazjonalnie cofająca się) przez 12 stanów aż do wysokości 14 i 255 HP.

## Gdzie znajduje się stan per-kafel

Stan w czasie działania serwera per-kafel to 7-bajtowa struktura `PlantInfo` w pliku warstwy
roślin strefy (`type, state, time, spawn, health, material, groundType`) — patrz
[Pliki stref](/pl/formats/zone-files/). Bajt `spawn` to prawdopodobieństwo spawnu na kafel
wbudowane w plik strefy — `0` oznacza kafel jałowy (rośliny na nim są usuwane podczas walidacji,
nigdy nie kiełkują); każda inna wartość oznacza, że próba regeneracji rośliny na tym kaflu
przechodzi przez losową bramkę z prawdopodobieństwem ≈ `spawn/256`. Serwer nigdy nie modyfikuje
tego bajtu. Dane produkcyjne: każdy kafel pliku `plants.0106.bin` zawiera `0x83` (≈ 51%).

## Ładunek dla klienta

Metoda `PlantRuleExtensions.GetPlantInfoForClient` wysyła dla każdego gatunku: `index`,
`mineral` (= fruitDefinition), `name`, `blocks` (blockingHeight), `health`.

<!-- Notatki deweloperskie: Materials/Plants/PlantRule.cs (gettery pól, GetNextState,
     CheckConsistency); PlantRuleLoader.cs (ładowanie plików, nadpisywanie source:,
     plantAltitudeScale stosowane do allowedAltitudeLow/High + allowedWaterLevelLow);
     PlantRuleExtensions.cs (losowania ważone fertility + spreading);
     NatureCube.cs (kolejność sprawdzania ValidateTile: flagi blokowania -> bajt spawnu ->
     istnienie reguły -> bity kontrolne -> altitude/4 -> poziom wody -> typ terenu ->
     nachylenie; automat stanów GrowPlantOnTile + obliczenia owoców); Common/SettingsLoader.cs
     (łączenie linii za pomocą '#' a następnie GenxyConverter.Deserialize); GenXY/GenxyReader.cs +
     GenxyToken.cs (znaki tokenów; '4' = tablica int hex, 'N' = tablica int dziesiętna,
     'n' = int dziesiętny). Pliki reguł znajdują się w $GameRoot/plantrules (tabela plantrules
     mapuje rulesetid -> nazwy plików). -->
