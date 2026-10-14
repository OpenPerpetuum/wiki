---
title: "Pflanzenfelder"
description: "Pflanzen-Regeldateiformat (GenXY), jedes Regelfeld mit Typ, Standardwert und Verbraucher, plus die Wachstums-Zustandsmaschine."
weight: 20
---

# Pflanzenfelder

Das Pflanzenverhalten wird pro Art durch eine **Regeldatei** (Klartext) unter
`$GameRoot/plantrules/` definiert. Welche Dateien zu einer Zone gehören, ist die
DB-Abbildung `plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset`; Laden und
Mergen macht `PlantRuleLoader.cs`, die Feld-zu-Objekt-Abbildung ist `PlantRule.cs`.

## Dateiformat

Ein `key=value` pro Zeile; `//`-Kommentare werden entfernt. Werte verwenden
**GenXY-Tokenzeichen** (`GenxyReader.cs` — das erste Zeichen wählt Typ und
Zahlengrundlage):

| Token | Geparst als | Beispiel |
|---|---|---|
| `n` | int, deizimal | `n125`, `n-1` |
| `N` | int[], deizimal, kommagetrennt | `N5,5,5,5` |
| `f` | double, deizimal | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **hex** | `iFF` |
| `L` | long, **hex** | `L100` |
| `4` | int[], **hex** | `41,2,3` → [1, 2, 3] |

### ⚠ Die „nackte Array"-Falle

Die Dateien enthalten auch Werte wie `blockingHeight=40,3,3,4` **ohne explizites
Token**. Der Parser behandelt diese nicht als Sonderfall: die führende `4` wird als
`IntegerArray`-Token (hex) verbraucht, und der Rest wird als hex geparst. Also:

```
blockingHeight=40,3,3,4   →  Token '4' + hex-Array "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  Token 'N' + dezimales Array         →  [0, 8, 11, 14]
```

Beide Schreibweisen enden als `int[]`, und die führende `0` ist das, was die `4`
„verschluckt". Deshalb beginnt jedes nackte Array in den ausgelieferten Dateien mit
`4` — es ist eine Konvention, die das erste Element auf dem beabsichtigten Wert
hält. **Bei neuen Regeldateien das `N`-Präfix explizit verwenden**; Werte ≥ 10 in
einem nackten Array würden als hex geparst und die Bedeutung stillschweigend ändern.

### Vererbung

Ein `source=$other_rule.txt`-Schlüssel lädt zuerst `other_rule.txt` und wendet die
Schlüssel der aktuellen Datei als Override an (`PlantRuleLoader.LoadRuleByName`).
Beispiel: `irontree_t2.txt` ist nur:

```
source=$irontree_lo.txt
fruitAmount=n125
```

## Feldreferenz

Alle Felder werden aus dem gemergten Einstellungen-Wörterbuch gelesen
(`PlantRule.cs`). Fehlende Schlüssel fallen auf den gezeigten Standardwert zurück.

| Schlüssel | Typ / Standard | Verbraucht von | Wirkung |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | Der `PlantType`-Enum-Wert für diese Art (1=GrassA … 19=Devrinol). Auch das `PlantInfo.type`-Byte, das pro Kachel gespeichert wird. |
| `name` | string | Client-Info-Payload | Anzeigename. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | Gewicht im gewichteten Zufallszug, der für eine Kachel **ohne** PflanzenNachbarn eine Art auswählt. 0 = spawnt nie. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | Gewichtsfaktor, wenn eine Kachel **Nachbarn hat**: Kandidatengewicht = `neighbourCount × spreading`. 0 = gewinnt nie den Ausbreitungs-Zufallszug. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | Mindestabstand von jeder bestehenden Pflanze desselben Typs; 0/negativ = keine Grenze. |
| `growRate` | int (0) | `GrowPlantOnTile` | Anzahl der Cube-Ticks, die das `PlantInfo.time`-Byte anhäufen muss, bevor die Zustandsmaschine würfelt. Höher = langsamer. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | Erlaubtes Steilungsband der abgeleiteten Steigungsschicht. Außerhalb des Bands wird die Pflanze entfernt. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | Höhenband, verglichen mit `Altitude / 4` (das `/4` passt zu den Client-Koordinaten). Skaliert mit `plantaltitudescale` der Zone. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | Band für `altitude/4 − waterLevel/4` — erzeugt Küstenvegetation. Ebenfalls höhen-skaliert. |
| `allowedTerrainTypes` | int[] (leer) | `ValidateTile` | Erlaubte `groundType`-Bytes (siehe [Zonendateien](/de/formats/zone-files/)). Leer = nirgends. Wird vollständig übersprungen, wenn `allowedOnNonNatural` gesetzt ist. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | Erster Zustand, der Frucht produziert. −1 ⇒ `NotFruiting` (nie erntbar). |
| `fruitDefinition` | int (−1) | Ernte | Itemdefinition der Frucht. |
| `fruitMaterialName` | string | Anzeige | Fruchtname (z. B. `$prismocitae`). |
| `fruitAmount` | byte (0), begrenzt 0–255 | `GrowPlantOnTile` | Maximale Frucht pro Pflanze. Der erste Eintritt in den fruchtenden Zustand füllt 5–15 % davon; jeder spätere Wachstumstick fügt 15–25 % hinzu, begrenzt auf 100 %. |
| `health` | byte[] pro Zustand | `GrowPlantOnTile`, Kampf | Trefferpunkte pro Wachstumszustand. Bei Zustandswechsel wird das aktuelle **Verhältnis** der Gesundheit in den neuen Zustand übernommen. |
| `blockingHeight` | int[] pro Zustand | `GrowPlantOnTile`, Spawn-Zählung | Blockierungshöhe pro Zustand; `>0` setzt den `Plant`-Bit in der Blockierschicht (begehbar=false) und zählt die Pflanze auf das Fruchtbarkeitsziel der Zone an. |
| `maxAmount` | int (−1) | `SpawnPlants` | Zonenobergrenze für die Anzahl dieser Art; −1 = unbegrenzt. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, Fruchtbarkeits-Zufallszug | Aus **allen** natürlichen Spawns ausgeschlossen; existiert nur, wo ein Spieler sie gepflanzt hat. |
| `damageScale` | double (1,0) | Pflanzenkampf | Eingehender Schadensfaktor. |
| `onlyOnUnprotectedZone` | bool (0) | Spawn-Validierung | Wächst nur, wo die Zone ungeschützt ist. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | Überspringt die Kontrollbit-, Geländetyp- und Steilungsprüfungen (wächst auf „künstlichen" Kacheln). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (Tod) | Beim Tod räumt die ConcreteA/B-Kontrollbits unter der Kachel. |
| `state_N` | int[] | `GetNextState` | Nächste-Zustands-Optionen für Zustand `N` — jedes Element wird **gleichmäßig zufällig** gewählt. |
| `action_N` | int[] | `GetNextState` | Nächste `PlantType`-Optionen für Zustand `N` (gleichmäßig). Ein Aktionswert von `0` (NotDefined) bedeutet **Tod**. |

Konsistenz wird beim Laden durchgesetzt (`CheckConsistency`): `len(health) ==
len(blockingHeight) == Anzahl der Zustände`.

## Die Wachstums-Zustandsmaschine

Jeden 32×32-Cube-Tick, für jede Pflanzenkachel (`GrowPlantOnTile`):

1. Wenn `time < growRate`: `time++`, fertig.
2. Sonst: `time = 0`, würfle `state_N` und `action_N` für den aktuellen Zustand:
   - `action == 0` → die Pflanze stirbt (Kill-Signal `type:0, state:1` für den
     Client); bei `placesConcrete` Beton unter der Kachel räumen.
   - sonst → `type = action`, `state = next`, `health = healthRatio ×
     Health[newState]` (Schadensverhältnis bleibt erhalten).
   - Frucht: wenn `newState == fruitingState`, `material = fruitAmount ×
     uniform(0.05, 0.15)`; wenn `newState > fruitingState`, `material += fruitAmount ×
     uniform(0.15, 0.25)` (begrenzt auf `fruitAmount`); sonst `material = 0`.
   - Blockierungshöhe = `blockingHeight[newState]`; das `Plant`-Bit der
     Blockierschicht folgt `height > 0`.

### Beispiel — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → 1/… Gewicht im Nachbarn-losen Zufallszug
spreading=n2        → Cluster-Gewicht = 2 × Nachbarn
growRate=n1         → würfelt jeden Cube-Tick einen Zustand (schnell)
maxAmount=n190      → höchstens 190 pro Cube
health=N5,5,5,5     → 5 TP in jedem Zustand
blockingHeight=40,0,0,0 → geparst als [0,0,0,0]: Gras blockiert NIEMALS
fruitingState=n-1   → NotFruiting: Gras ist nie erntbar
state_0=40,0,1      → [0,0,1]: 2/3 bleiben in Zustand 0, 1/3 gehen weiter
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → im Endzustand: 3/4 bleiben, 1/4 sterben
```

Eine Gras-Kachel also: geht im Durchschnitt etwa alle 3 Ticks einen Zustand
weiter, und im letzten Zustand gibt es 25 % Chance pro Tick zu sterben und neu zu
keimen — eine Art Deckungspflanze mit ständigem Umsatz, aber ohne Frucht.

### Beispiel — `wall.txt` (12 Zustände, `N`-präfixiert)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (kann einen Zustand zurückgehen), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: eine von Spielern gepflanzte Befestigung,
die nur in ungeschützten Zonen existiert, auf 15 pro Cube begrenzt, die durch 12
Zustände (und gelegentlich schrumpfend) bis Höhe 14 und 255 TP wächst.

## Wo der Kachel-Zustand lebt

Der Laufzeit-Zustand pro Kachel ist der 7-Byte-`PlantInfo`-Struct in der
Pflanzenschichtdatei der Zone (`type, state, time, spawn, health, material,
groundType`) — siehe [Zonendateien](/de/formats/zone-files/). Das `spawn`-Byte ist eine
pro Kachel in die Zonendatei eingebackene Spawn-Wahrscheinlichkeit — `0` markiert eine
sterile Kachel (Pflanzen darauf werden bei der Validierung entfernt, sie keimt nie);
jeder andere Wert bedeutet, dass ein Pflanzen-Regen-Versuch auf dieser Kachel ein
zufälliges Gate mit Chance ≈ `spawn/256` passiert. Der Server schreibt das Byte nie.
Live-Daten: jede Kachel von `plants.0106.bin` trägt `0x83` (≈ 51 %).

## Client-Payload

`PlantRuleExtensions.GetPlantInfoForClient` sendet pro Art: `index`, `mineral`
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
