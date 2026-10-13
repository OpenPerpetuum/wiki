---
title: "Pole rostlin"
description: "Formát souboru pravidel rostlin (GenXY), každé pole pravidel s typem, výchozí hodnotou a zpracovatelem, plus stavový automat růstu."
weight: 20
---

# Pole rostlin

Chování rostlin je definováno pro každý druh **souborem pravidel** (prostý text) v adresáři
`$GameRoot/plantrules/`. Které soubory patří které zóně, je určeno mapováním v databázi
`plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset`; načítání a slučování probíhá v
`PlantRuleLoader.cs` a mapování polí na objekty se nachází v `PlantRule.cs`.

## Formát souboru

Jeden záznam `key=value` na řádek; komentáře ve stylu `//` jsou odstraněny. Hodnoty používají **znakové
tokeny GenXY** (`GenxyReader.cs` — první znak určuje datový typ a číselnou soustavu):

| Token | Zpracováno jako | Příklad |
|---|---|---|
| `n` | int, desítkově | `n125`, `n-1` |
| `N` | int[], desítkově, odděleno čárkami | `N5,5,5,5` |
| `f` | double, desítkově | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **šestnáctkově (hex)** | `iFF` |
| `L` | long, **šestnáctkově (hex)** | `L100` |
| `4` | int[], **šestnáctkově (hex)** | `41,2,3` → [1, 2, 3] |

### ⚠ Past s neoznačenými poli („bare array“)

Soubory obsahují také hodnoty jako `blockingHeight=40,3,3,4` **bez explicitního tokenu**.
Parser s nimi nezachází jako se speciálním případem: úvodní znak `4` je zkonzumován jako token
`IntegerArray` (hex) a zbytek je parsován hexadecimálně. Tedy:

```
blockingHeight=40,3,3,4   →  token '4' + hex pole "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  token 'N' + desítkové pole      →  [0, 8, 11, 14]
```

Oba zápisy skončí jako `int[]` a úvodní `0` je to, co token `4` „pohltí“. Proto každé neoznačené
pole v distribuovaných souborech začíná číslem `4` — je to konvence, která udržuje první prvek
na zamýšlené hodnotě. **Při psaní nových souborů pravidel používejte explicitně předponu `N`**;
hodnoty ≥ 10 v neoznačeném poli by byly parsovány šestnáctkově a tiše by změnily význam.

### Dědičnost

Klíč `source=$other_rule.txt` nejprve načte `other_rule.txt` a poté aplikuje klíče aktuálního souboru
jako přepsání (`PlantRuleLoader.LoadRuleByName`). Příklad:
`irontree_t2.txt` je pouze:

```
source=$irontree_lo.txt
fruitAmount=n125
```

## Přehled polí

Všechna pole jsou čtena ze sloučeného slovníku nastavení (`PlantRule.cs`). Chybějící klíče se vrátí
k uvedené výchozí hodnotě.

| Klíč | Typ / výchozí | Zpracováno v | Efekt |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | Hodnota enumu `PlantType` pro tento druh (1=GrassA … 19=Devrinol). Také bajt `PlantInfo.type` uložený na dlaždici. |
| `name` | string | klientská informační data | Zobrazovaný název. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | Váha ve váženém losování, které vybírá druh pro dlaždici **bez** sousedních rostlin. 0 = nikdy se nespawne. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | Násobitel váhy, pokud dlaždice **má** sousedy: váha kandidáta = `neighbourCount × spreading`. 0 = nikdy nevyhraje losování šíření. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | Minimální vzdálenost od jakékoli existující rostliny stejného druhu; 0/záporné = bez omezení. |
| `growRate` | int (0) | `GrowPlantOnTile` | Počet ticků krychle, které musí bajt `PlantInfo.time` nasbírat, než stavový automat provede krok. Vyšší = pomalejší. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | Povolený rozsah sklonu odvozené vrstvy sklonu. Mimo tento rozsah je rostlina odstraněna. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | Rozsah nadmořské výšky porovnávaný s `Altitude / 4` (`/4` odpovídá souřadnicím klienta). Škálováno hodnotou `plantaltitudescale` zóny. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | Rozsah pro `altitude/4 − waterLevel/4` — vytváří pobřežní vegetaci. Také škálováno nadmořskou výškou. |
| `allowedTerrainTypes` | int[] (prázdné) | `ValidateTile` | Povolené bajty `groundType` (viz [Soubory zón](/cs/formats/zone-files/)). Prázdné = nikde. Zcela přeskočeno, pokud je nastaveno `allowedOnNonNatural`. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | První stav, který produkuje plody. −1 ⇒ `NotFruiting` (nikdy nelze sklízet). |
| `fruitDefinition` | int (−1) | sklizeň | Definice předmětu plodu. |
| `fruitMaterialName` | string | zobrazení | Název plodu (např. `$prismocitae`). |
| `fruitAmount` | byte (0), omezeno 0–255 | `GrowPlantOnTile` | Maximální počet plodů na rostlinu. První vstup do stavu plodení naplní 5–15 %; každý další růstový tick přidá 15–25 %, maximálně do 100 %. |
| `health` | byte[] pro každý stav | `GrowPlantOnTile`, boj | Životy (HP) pro každý stav růstu. Při změně stavu se aktuální **poměr** zdraví přenáší do nového stavu. |
| `blockingHeight` | int[] pro každý stav | `GrowPlantOnTile`, počítání spawnů | Výška blokování pro každý stav; `>0` nastaví bit `Plant` v blokovací vrstvě (walkable=false) a započítává rostlinu do cíle fertility zóny. |
| `maxAmount` | int (−1) | `SpawnPlants` | Limit počtu jedinců tohoto druhu na zónu; −1 = neomezeno. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, losování fertility | Vyloučeno ze **všech** přirozených spawnů; existuje pouze tam, kde ji zasadil hráč. |
| `damageScale` | double (1.0) | boj rostlin | Násobitel příchozího poškození. |
| `onlyOnUnprotectedZone` | bool (0) | validace spawnu | Roste pouze v nechráněných zónách. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | Přeskakuje kontroly ovládacích bitů, typu terénu a sklonu (roste na „umělých" dlaždicích). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (smrt) | Při zániku vyčistí ovládací bity ConcreteA/B pod dlaždicí. |
| `state_N` | int[] | `GetNextState` | Možnosti dalšího stavu pro stav `N` — každý prvek je vybrán **rovnoměrně náhodně**. |
| `action_N` | int[] | `GetNextState` | Možnosti dalšího `PlantType` pro stav `N` (rovnoměrně). Hodnota akce `0` (NotDefined) znamená **zánik/smrt**. |

Konzistence je vynucována při načtení (`CheckConsistency`): `len(health) == len(blockingHeight) == počet stavů`.

## Stavový automat růstu

Každý tick krychle 32×32 pro každou dlaždici rostliny (`GrowPlantOnTile`):

1. Pokud `time < growRate`: `time++`, hotovo.
2. Jinak: `time = 0`, vylosuj `state_N` a `action_N` pro aktuální stav:
   - `action == 0` → rostlina zahyne (signál zničení `type:0, state:1` pro klienta);
     pokud `placesConcrete`, vyčisti beton pod dlaždicí.
   - jinak → `type = action`, `state = next`, `health = healthRatio × Health[newState]` (poměr poškození zůstává zachován).
   - Plody: pokud `newState == fruitingState`, `material = fruitAmount × uniform(0.05, 0.15)`; pokud `newState > fruitingState`, `material += fruitAmount × uniform(0.15, 0.25)` (omezeno do `fruitAmount`); jinak `material = 0`.
   - Výška blokování = `blockingHeight[newState]`; bit `Plant` v blokovací vrstvě se řídí podmínkou `height > 0`.

### Příklad z praxe — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → váha 1/… v losování bez sousedů
spreading=n2        → váha shluku = 2 × sousedé
growRate=n1         → losuje stav každý tick krychle (rychlé)
maxAmount=n190      → nanejvýš 190 na krychli
health=N5,5,5,5     → 5 HP v každém stavu
blockingHeight=40,0,0,0 → parsováno jako [0,0,0,0]: tráva NIKDY neblokuje
fruitingState=n-1   → NotFruiting: tráva nikdy neplodí
state_0=40,0,1      → [0,0,1]: 2/3 zůstávají ve stavu 0, 1/3 postupuje
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → v konečném stavu: 3/4 zůstávají, 1/4 zahyne
```

Dlaždice trávy tedy: postoupí v průměru zhruba o jeden stav každé 3 ticky a v posledním
stavu má 25% šanci na tick, že zahyne a znovu se vysemení — neustále se obnovující
druh půdního pokryvu bez plodů.

### Příklad z praxe — `wall.txt` (12 stavů, předpona `N`)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (může klesnout o stav), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: hráčem zasazené opevnění, které existuje
pouze v nechráněných zónách s limitem 15 na krychli, které roste (a občas klesá)
přes 12 stavů až do výšky 14 a 255 HP.

## Kde je uložen stav jednotlivých dlaždic

Stav dlaždice za běhu je 7bajtová struktura `PlantInfo` v souboru vrstvy rostlin dané zóny
(`type, state, time, spawn, health, material, groundType`) — viz
[Soubory zón](/cs/formats/zone-files/). Bajt `spawn` je pravděpodobnost spawnu dlaždice
vepsaná do souboru zóny — `0` označuje sterilní dlaždici (rostliny na ní jsou při validaci
odstraněny a nikdy na ní nic nevyraší); jakákoli jiná hodnota znamená, že pokus o regeneraci
rostliny na dané dlaždici projde náhodným výběrem s pravděpodobností ≈ `spawn/256`. Server
tento bajt nikdy nepřepisuje. Živá data: každá dlaždice v `plants.0106.bin` nese hodnotu `0x83` (≈ 51 %).

## Klientská data

`PlantRuleExtensions.GetPlantInfoForClient` odesílá pro každý druh: `index`, `mineral`
(= fruitDefinition), `name`, `blocks` (blockingHeight), `health`.

<!-- Developer notes: Materials/Plants/PlantRule.cs (field getters, GetNextState,
     CheckConsistency); PlantRuleLoader.cs (file load, source: override,
     plantAltitudeScale applied to allowedAltitudeLow/High + allowedWaterLevelLow);
     PlantRuleExtensions.cs (fertility + spreading weighted draws);
     NatureCube.cs (ValidateTile checks order: block flags -> spawn byte -> rule
     existence -> control bits -> altitude/4 -> water level -> terrain type ->
     slope; GrowPlantOnTile state machine + fruit math); Common/SettingsLoader.cs
     (line join with '#' then GenxyConverter.Deserialize); GenXY/GenxyReader.cs +
     GenxyToken.cs (token characters; '4' = hex int array, 'N' = decimal int array,
     'n' = int decimal). Rule files live at $GameRoot/plantrules (plantrules table
     maps rulesetid -> file names). -->
