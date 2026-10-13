---
title: "Plantenvelden"
description: "Plantregelbestandsformaat (GenXY), elk regelveld met type, standaardwaarde en consument, plus de groeistatemachine."
weight: 20
---

# Plantenvelden

Het plantgedrag wordt per soort gedefinieerd door een **regelbestand** (plain text) onder
`$GameRoot/plantrules/`. Welke bestanden bij een zone horen, wordt bepaald door de DB-mapping
`plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset`; laden en combineren gebeurt in
`PlantRuleLoader.cs`, en de veld-naar-object-mapping staat in `PlantRule.cs`.

## Bestandsformaat

Eén `key=value` per regel; `//`-stijl commentaar wordt verwijderd. Waarden gebruiken **GenXY-tokenkarakters**
(`GenxyReader.cs` — het eerste karakter bepaalt het type en het getalstelsel):

| Token | Geparst als | Voorbeeld |
|---|---|---|
| `n` | int, decimaal | `n125`, `n-1` |
| `N` | int[], decimaal, komma-gescheiden | `N5,5,5,5` |
| `f` | double, decimaal | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **hex** | `iFF` |
| `L` | long, **hex** | `L100` |
| `4` | int[], **hex** | `41,2,3` → [1, 2, 3] |

### ⚠ De "naakte array"-val

Bestanden bevatten ook waarden zoals `blockingHeight=40,3,3,4` **zonder expliciet token**.
De parser behandelt deze niet als speciaal geval: het leidende `4` wordt geconsumeerd als
`IntegerArray` (hex)-token, en de rest wordt als hex geparst. Dus:

```
blockingHeight=40,3,3,4   →  token '4' + hex array "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  token 'N' + decimale array         →  [0, 8, 11, 14]
```

Beide schrijfwijzen eindigen als `int[]`, en het leidende `0` is wat het `4` "verslindt". Dit
is de reden waarom elke naakte array in de geleverde bestanden begint met `4` — het is een
conventie die het eerste element op de beoogde waarde houdt. **Gebruik bij het schrijven van
nieuwe regelbestanden expliciet het `N`-prefix**; waarden ≥ 10 in een naakte array zouden als
hex geparst worden en de betekenis stilzwijgend veranderen.

### Erfelijkheid

Een `source=$other_rule.txt`-sleutel laadt eerst `other_rule.txt` en past de sleutels van het
huidige bestand als overschrijvingen toe (`PlantRuleLoader.LoadRuleByName`). Voorbeeld:
`irontree_t2.txt` is slechts:

```
source=$irontree_lo.txt
fruitAmount=n125
```

## Veldreferentie

Alle velden worden gelezen uit het gecombineerde instellingenwoordenboek (`PlantRule.cs`).
Ontbrekende sleutels vallen terug op de getoonde standaardwaarde.

| Sleutel | Type / standaard | Gebruikt door | Effect |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | De `PlantType`-enumwaarde voor dit soort (1=GrassA … 19=Devrinol). Ook het `PlantInfo.type`-byte dat per tegel wordt opgeslagen. |
| `name` | string | client-info-payload | Weergavenaam. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | Gewicht in de gewichtste loting die een soort kiest voor een tegel **zonder** plantburen. 0 = komt nooit voor. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | Gewichtsmenigvuldiger wanneer een tegel **wel** buren heeft: kandidaatgewicht = `aantalBuren × spreading`. 0 = wint nooit de verspreidingsloting. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | Minimale afstand tot een bestaande plant van hetzelfde type; 0/negatief = geen limiet. |
| `growRate` | int (0) | `GrowPlantOnTile` | Aantal kubusticks dat het `PlantInfo.time`-byte moet ophopen voordat de statemachine een trekking doet. Hoger = trager. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | Toegestane hellingsband van de afgeleide hellingslaag. Buiten de band wordt de plant verwijderd. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | Hoogteband, vergeleken met `Altitude / 4` (de `/4` komt overeen met clientcoördinaten). Geschaald met de `plantaltitudescale` van de zone. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | Band voor `altitude/4 − waterLevel/4` — creëert kustvegetatie. Ook hoogteschaal. |
| `allowedTerrainTypes` | int[] (leeg) | `ValidateTile` | Toegestane `groundType`-bytes (zie [Zone files](/nl/formats/zone-files/)). Leeg = nergens. Volledig overgeslagen wanneer `allowedOnNonNatural` is ingesteld. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | Eerste staat die vrucht produceert. −1 ⇒ `NotFruiting` (nooit oogstbaar). |
| `fruitDefinition` | int (−1) | oogsten | Itemdefinitie van de vrucht. |
| `fruitMaterialName` | string | weergave | Vruchtnaam (bijv. `$prismocitae`). |
| `fruitAmount` | byte (0), begrensd 0–255 | `GrowPlantOnTile` | Maximale vruchten per plant. Bij de eerste overgang naar de vruchtzame staat wordt 5–15% gevuld; elke latere groeitik voegt 15–25% toe, begrensd tot 100%. |
| `health` | byte[] per staat | `GrowPlantOnTile`, gevecht | Levenspunten per groeistaat. Bij staatswissel wordt de huidige gezondheidsverhouding overgenomen in de nieuwe staat. |
| `blockingHeight` | int[] per staat | `GrowPlantOnTile`, spawn-telling | Blokkerende hoogte per staat; `>0` zet het `Plant`-bit in de blokkerlaag (walkable=false) en laat de plant meetellen voor het vruchtbaarheidstoestel van de zone. |
| `maxAmount` | int (−1) | `SpawnPlants` | Zone-limiet op het aantal van dit soort; −1 = onbeperkt. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, vruchtbaarheidsloting | Uitgesloten van **alle** natuurlijke spawns; bestaat alleen waar een speler het heeft geplant. |
| `damageScale` | double (1.0) | plantengevecht | Menigvuldiger voor inkomende schade. |
| `onlyOnUnprotectedZone` | bool (0) | spawn-validatie | Groeit alleen waar de zone onbeschermde is. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | Slaapt de controlebit-, terreintype- en hellingscontroles over (groeit op "kunstmatige" tegels). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (dood) | Bij dood wist de ConcreteA/B-controlebits onder de tegel. |
| `state_N` | int[] | `GetNextState` | Volgende-staatkeuzes voor staat `N` — elk element wordt **uniform willekeurig** getrokken. |
| `action_N` | int[] | `GetNextState` | Volgende `PlantType`-keuzes voor staat `N` (uniform). Een actiewaarde van `0` (NotDefined) betekent **dood**. |

Consistentie wordt afgedwongen bij laden (`CheckConsistency`): `len(health) ==
len(blockingHeight) == aantal staten`.

## De groeistatemachine

Elke 32×32-kubustick, voor elke planttegel (`GrowPlantOnTile`):

1. Als `time < growRate`: `time++`, klaar.
2. Anders: `time = 0`, trek `state_N` en `action_N` voor de huidige staat:
   - `action == 0` → de plant sterft (doodsignaal `type:0, state:1` voor de client);
     indien `placesConcrete`, wist beton onder de tegel.
   - anders → `type = action`, `state = next`, `health = healthRatio ×
     Health[newState]` (schadeverhouding behouden).
   - Vrucht: als `newState == fruitingState`, `material = fruitAmount ×
     uniform(0.05, 0.15)`; als `newState > fruitingState`, `material += fruitAmount ×
     uniform(0.15, 0.25)` (begrensd tot `fruitAmount`); anders `material = 0`.
   - Blokhoogte = `blockingHeight[newState]`; het `Plant`-bit van de blokkerlaag volgt
     `height > 0`.

### Uitgewerkt voorbeeld — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → 1/… gewicht in de loting zonder buren
spreading=n2        → clustergewicht = 2 × buren
growRate=n1         → trekt elke kubustick een staat (snel)
maxAmount=n190      → maximaal 190 per kubus
health=N5,5,5,5     → 5 LP in elke staat
blockingHeight=40,0,0,0 → geparst als [0,0,0,0]: gras blokkeert NOOIT
fruitingState=n-1   → NotFruiting: gras is nooit oogstbaar
state_0=40,0,1      → [0,0,1]: 2/3 blijven in staat 0, 1/3 gaan door
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → in de laatste staat: 3/4 blijven, 1/4 sterft
```

Een grastegel gaat dus gemiddeld ongeveer één staat per 3 ticks door, en heeft in de laatste
staat per tick een 25% kans om te sterven en opnieuw te kiemen — een soort met constante
omzet zonder vrucht.

### Uitgewerkt voorbeeld — `wall.txt` (12 staten, met `N`-prefix)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (kan een staat terug), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: een door speler geplante versterking die alleen
in onbeschermde zones bestaat, begrensd tot 15 per kubus, die (en af en toe krimpt) door
12 staten groeit tot hoogte 14 en 255 LP.

## Waar de per-tegel staat zich bevindt

De runtime-status per tegel is de 7-byte `PlantInfo`-struct in het plantlagenbestand van de
zone (`type, state, time, spawn, health, material, groundType`) — zie
[Zone files](/nl/formats/zone-files/). Het `spawn`-byte is een per-tegel spawnkans die in het
zonebestand is ingebakken — `0` markeert een steriele tegel (planten erop worden verwijderd
tijdens validatie, het kiemt nooit); elke andere waarde betekent dat een plantregeneratiepoging
op die tegel een willekeurige poort door gaat met kans ≈ `spawn/256`. De server schrijft het
byte nooit. Live data: elke tegel van `plants.0106.bin` draagt `0x83` (≈ 51%).

## Client-payload

`PlantRuleExtensions.GetPlantInfoForClient` stuurt, per soort: `index`, `mineral`
(= fruitDefinition), `name`, `blocks` (blockingHeight), `health`.

<!-- Ontwikkelaarsnotities: Materials/Plants/PlantRule.cs (veldgetters, GetNextState,
     CheckConsistency); PlantRuleLoader.cs (bestandsladen, source:-overschrijving,
     plantAltitudeScale toegepast op allowedAltitudeLow/High + allowedWaterLevelLow);
     PlantRuleExtensions.cs (vruchtbaarheid + verspreiding gewichtste lotingen);
     NatureCube.cs (ValidateTile-controlevolgorde: blokkeerbits -> spawn-byte -> regel
     bestaan -> controlebits -> altitude/4 -> waterpeil -> terreintype ->
     helling; GrowPlantOnTile statemachine + vruchtformule); Common/SettingsLoader.cs
     (regelsamenvoegen met '#' dan GenxyConverter.Deserialize); GenXY/GenxyReader.cs +
     GenxyToken.cs (tokenkarakters; '4' = hex int array, 'N' = decimale int array,
     'n' = int decimaal). Regelbestanden staan in $GameRoot/plantrules (plantrules-tabel
     mapt rulesetid -> bestandsnamen). -->