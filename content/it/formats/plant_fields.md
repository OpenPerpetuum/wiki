---
title: "Campi delle piante"
description: "Formato del file di regole delle piante (GenXY), ogni campo di regola con tipo, valore predefinito e consumatore, più la macchina a stati di crescita."
weight: 20
---

# Campi delle piante

Il comportamento delle piante è definito per specie da un **file di regole** (testo normale) sotto
`$GameRoot/plantrules/`. L'associazione tra i file e una zona è definita nel mapping del DB
`plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset`; il caricamento e l'unione sono gestiti da
`PlantRuleLoader.cs`, mentre la mappatura da campi a oggetti risiede in `PlantRule.cs`.

## Formato del file

Un `key=value` per riga; i commenti in stile `//` vengono rimossi. I valori utilizzano i **caratteri token
GenXY** (`GenxyReader.cs` — il primo carattere seleziona il tipo e la base numerica):

| Token | Interpretato come | Esempio |
|---|---|---|
| `n` | int, decimale | `n125`, `n-1` |
| `N` | int[], decimale, separato da virgole | `N5,5,5,5` |
| `f` | double, decimale | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **esadecimale** | `iFF` |
| `L` | long, **esadecimale** | `L100` |
| `4` | int[], **esadecimale** | `41,2,3` → [1, 2, 3] |

### ⚠ L'insidia degli array "nudi" (senza prefisso)

I file contengono anche valori come `blockingHeight=40,3,3,4` **senza un token esplicito**.
Il parser non gestisce questi casi in modo speciale: il `4` iniziale viene consumato come token
`IntegerArray` (esadecimale), e il resto viene interpretato come esadecimale. Quindi:

```
blockingHeight=40,3,3,4   →  token '4' + array esadecimale "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  token 'N' + array decimale              →  [0, 8, 11, 14]
```

Entrambe le sintassi producono un `int[]`, e lo `0` iniziale è ciò che il `4` "inghiotte". È per questo
che ogni array nudo nei file distribuiti inizia con `4` — si tratta di una convenzione che mantiene
il primo elemento al valore desiderato. **Quando scrivi nuovi file di regole, usa esplicitamente il prefisso `N`**;
i valori ≥ 10 in un array nudo verrebbero interpretati come esadecimali, alterandone silenziosamente il significato.

### Ereditarietà

Una chiave `source=$other_rule.txt` carica prima `other_rule.txt` e applica le chiavi del file corrente
come sovrascritture (`PlantRuleLoader.LoadRuleByName`). Esempio:
`irontree_t2.txt` è semplicemente:

```
source=$irontree_lo.txt
fruitAmount=n125
```

## Riferimento dei campi

Tutti i campi vengono letti dal dizionario delle impostazioni unite (`PlantRule.cs`). Le chiavi mancanti
utilizzano il valore predefinito mostrato.

| Chiave | Tipo / predefinito | Consumato da | Effetto |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | Il valore dell'enum `PlantType` per questa specie (1=GrassA … 19=Devrinol). Corrisponde anche al byte `PlantInfo.type` memorizzato per tile. |
| `name` | string | payload info client | Nome visualizzato. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | Peso nell'estrazione ponderata che sceglie una specie per un tile **senza** piante vicine. 0 = non genera mai spawn. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | Moltiplicatore di peso quando un tile **ha** piante vicine: peso candidato = `neighbourCount × spreading`. 0 = non vince mai l'estrazione per diffusione. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | Distanza minima da qualsiasi pianta esistente dello stesso tipo; 0/negativo = nessun limite. |
| `growRate` | int (0) | `GrowPlantOnTile` | Numero di tick del cubo che il byte `PlantInfo.time` deve accumulare prima che la macchina a stati effettui un avanzamento. Più alto = più lento. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | Fascia di pendenza consentita del livello di pendenza derivato. Al di fuori della fascia la pianta viene rimossa. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | Fascia di altitudine, confrontata con `Altitude / 4` (il `/4` corrisponde alle coordinate client). Scalato da `plantaltitudescale` della zona. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | Fascia per `altitude/4 − waterLevel/4` — crea la vegetazione costiera. Anch'essa scalata per l'altitudine. |
| `allowedTerrainTypes` | int[] (vuoto) | `ValidateTile` | Byte `groundType` consentiti (vedi [File di zona](/it/formats/zone-files/)). Vuoto = da nessuna parte. Saltato del tutto quando `allowedOnNonNatural` è impostato. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | Primo stato che produce frutti. −1 ⇒ `NotFruiting` (mai raccoglibile). |
| `fruitDefinition` | int (−1) | raccolta | Definizione dell'oggetto (item) del frutto. |
| `fruitMaterialName` | string | display | Nome del frutto (es. `$prismocitae`). |
| `fruitAmount` | byte (0), limitato a 0–255 | `GrowPlantOnTile` | Quantità massima di frutti per pianta. Il primo ingresso nello stato di fruttificazione ne genera il 5–15%; ogni successivo tick di crescita aggiunge il 15–25%, fino al 100%. |
| `health` | byte[] per stato | `GrowPlantOnTile`, combattimento | Punti ferita per stato di crescita. Al cambio di stato, il **rapporto** di salute attuale viene trasferito nel nuovo stato. |
| `blockingHeight` | int[] per stato | `GrowPlantOnTile`, conteggio spawn | Altezza di blocco per stato; `>0` imposta il bit `Plant` nel layer di blocco (walkable=false) e fa contare la pianta verso l'obiettivo di fertilità della zona. |
| `maxAmount` | int (−1) | `SpawnPlants` | Limite per zona sul numero di esemplari di questa specie; −1 = illimitato. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, estrazione fertilità | Esclusa da **tutti** gli spawn naturali; esiste solo dove è stata piantata da un giocatore. |
| `damageScale` | double (1.0) | combattimento piante | Moltiplicatore del danno in ingresso. |
| `onlyOnUnprotectedZone` | bool (0) | validazione spawn | Cresce solo dove la zona non è protetta. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | Salta i controlli sui bit di controllo, sul tipo di terreno e sulla pendenza (cresce su tile "artificiali"). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (morte) | Alla morte, rimuove i bit di controllo ConcreteA/B sotto il tile. |
| `state_N` | int[] | `GetNextState` | Scelte per lo stato successivo per lo stato `N` — ciascun elemento viene scelto con **distribuzione uniforme casuale**. |
| `action_N` | int[] | `GetNextState` | Scelte del prossimo `PlantType` per lo stato `N` (uniforme). Un valore di azione pari a `0` (NotDefined) indica la **morte**. |

La coerenza viene verificata al caricamento (`CheckConsistency`): `len(health) == len(blockingHeight) == numero di stati`.

## La macchina a stati di crescita

A ogni tick del cubo 32×32, per ogni tile di pianta (`GrowPlantOnTile`):

1. Se `time < growRate`: `time++`, operazione completata.
2. Altrimenti: `time = 0`, estrai `state_N` e `action_N` per lo stato corrente:
   - `action == 0` → la pianta muore (segnale di eliminazione `type:0, state:1` per il client);
     se `placesConcrete`, rimuovi il cemento sotto il tile.
   - altrimenti → `type = action`, `state = next`, `health = healthRatio × Health[newState]` (il rapporto del danno viene preservato).
   - Frutto: se `newState == fruitingState`, `material = fruitAmount × uniform(0.05, 0.15)`; se `newState > fruitingState`, `material += fruitAmount × uniform(0.15, 0.25)` (con limite a `fruitAmount`); altrimenti `material = 0`.
   - Altezza di blocco = `blockingHeight[newState]`; il bit `Plant` del layer di blocco segue `height > 0`.

### Esempio pratico svolto — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → peso 1/… nell'estrazione senza vicini
spreading=n2        → peso cluster = 2 × vicini
growRate=n1         → estrae uno stato a ogni tick del cubo (veloce)
maxAmount=n190      → massimo 190 per cubo
health=N5,5,5,5     → 5 HP in ogni stato
blockingHeight=40,0,0,0 → interpretato come [0,0,0,0]: l'erba NON blocca MAI
fruitingState=n-1   → NotFruiting: l'erba non è mai raccoglibile
state_0=40,0,1      → [0,0,1]: 2/3 rimane nello stato 0, 1/3 avanza
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → nello stato finale: 3/4 rimane, 1/4 muore
```

Quindi un tile d'erba: avanza all'incirca di uno stato ogni 3 tick in media, e nell'ultimo
stato ha una probabilità del 25% per tick di morire e riseminarsi — una specie di copertura
in continuo ricambio senza frutti.

### Esempio pratico svolto — `wall.txt` (12 stati, prefisso `N`)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (può regredire di uno stato), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: una fortificazione piantata dai giocatori che
esiste solo in zone non protette, con un limite di 15 per cubo, che cresce (e occasionalmente
si riduce) attraverso 12 stati fino a un'altezza di 14 e 255 HP.

## Dove risiede lo stato per tile

Lo stato di runtime per tile è la struct di 7 byte `PlantInfo` nel file del layer delle piante della zona
(`type, state, time, spawn, health, material, groundType`) — vedi
[File di zona](/it/formats/zone-files/). Il byte `spawn` è una probabilità di spawn per tile incorporata
nel file di zona — `0` contrassegna un tile sterile (le piante su di esso vengono rimosse durante la
validazione e non germogliano mai); qualsiasi altro valore fa sì che un tentativo di rigenerazione
della pianta su quel tile superi una soglia casuale con probabilità ≈ `spawn/256`. Il server non scrive mai
questo byte. Dati reali: ogni tile di `plants.0106.bin` contiene `0x83` (≈ 51%).

## Payload del client

`PlantRuleExtensions.GetPlantInfoForClient` invia al client, per specie: `index`, `mineral`
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
