---
title: "Campi delle piante"
description: "Formato del file di regole delle piante (GenXY), ogni campo di regola con tipo, valore predefinito e consumatore, più la macchina a stati di crescita."
weight: 380
---

# Campi delle piante

Il comportamento delle piante è definito per specie da un **file di regole**
(testo puro) sotto `$GameRoot/plantrules/`.

## Formato del file

Un `key=value` per riga; i commenti di stile `//` vengono rimossi. I valori
usano i **caratteri di token GenXY** (`GenxyReader.cs`):

| Token | Analizzato come | Esempio |
|---|---|---|
| `#` | Numero intero decimale | `#100` = 100 |
| `.` | Numero a virgola mobile | `.5` = 0.5 |
| `s` | Stringa | `sHello` |
| `b` | Booleano | `b1` = true |
| `c` | Carattere | `cA` = 'A' |

## Campi di regole

| Campo | Tipo | Predefinito | Descrizione |
|---|---|---|---|
| `fertility` | # | 1 | Frequenza di comparsa della pianta |
| `growRate` | # | 1 | Numero di cicli per stadio di crescita |
| `spreading` | # | 1 | Tendenza a crescere in gruppi |
| `killDistance` | # | 0 | Spaziamento minimo tra piante |
| `slope` | # | 0 | Pendenza massima del terreno |
| `minSlope` | # | 0 | Pendenza minima del terreno |
| `allowedAltitudeLow` | # | 0 | Altitudine minima |
| `allowedAltitudeHigh` | # | 100 | Altitudine massima |
| `allowedWaterLevelLow` | # | 0 | Distanza minima dalla riva |
| `allowedWaterLevelHigh` | # | 100 | Distanza massima dalla riva |
| `fruitingState` | # | 3 | Stadio di crescita per la fruttificazione |
| `fruitDefinition` | s | – | Definizione del frutto prodotto |
| `fruitAmount` | # | 1 | Quantità di frutto prodotta |
| `maxAmount` | # | 100 | Numero massimo in una zona di elaborazione |
| `health` | # | 10 | Punti vita per stadio |
| `damageScale` | # | 1 | Resistenza al danno |
| `playerSeeded` | b | false | Esiste solo se piantata da un giocatore |
| `onlyOnUnprotectedZone` | b | false | Cresce solo in zone non protette |

## Macchina a stati di crescita

Le piante passano attraverso una sequenza di stadi:

1. **Seme</parameter>
</invoke>
