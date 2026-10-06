---
title: "Campos das plantas"
description: "Formato do arquivo de regras das plantas (GenXY), cada campo de regra com tipo, valor padrão e consumidor, mais a máquina de estados de crescimento."
weight: 380
---

# Campos das plantas

O comportamento das plantas é definido por espécie por um **arquivo de regras**
(texto puro) sob `$GameRoot/plantrules/`.

## Formato do arquivo

Um `key=value` por linha; comentários de estilo `//` são removidos. Os valores
usam os **caracteres de token GenXY** (`GenxyReader.cs`):

| Token | Analisado como | Exemplo |
|---|---|---|
| `#` | Número inteiro decimal | `#100` = 100 |
| `.` | Número flutuante | `.5` = 0.5 |
| `s` | Cadeia de caracteres | `sHello` |
| `b` | Booleano | `b1` = true |
| `c` | Caractere | `cA` = 'A' |

## Campos de regras

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `fertility` | # | 1 | Frequência de aparição da planta |
| `growRate` | # | 1 | Número de ciclos por estágio de crescimento |
| `spreading` | # | 1 | Tendência a crescer em grupos |
| `killDistance` | # | 0 | Espaçamento mínimo entre plantas |
| `slope` | # | 0 | Inclinação máxima do solo |
| `minSlope` | # | 0 | Inclinação mínima do solo |
| `allowedAltitudeLow` | # | 0 | Altitude mínima |
| `allowedAltitudeHigh` | # | 100 | Altitude máxima |
| `allowedWaterLevelLow` | # | 0 | Distância mínima da margem |
| `allowedWaterLevelHigh` | # | 100 | Distância máxima da margem |
| `fruitingState` | # | 3 | Estágio de crescimento para frutificação |
| `fruitDefinition` | s | – | Definição do fruto produzido |
| `fruitAmount` | # | 1 | Quantidade de fruto produzida |
| `maxAmount` | # | 100 | Número máximo em uma zona de processamento |
| `health` | # | 10 | Pontos de vida por estágio |
| `damageScale` | # | 1 | Resistência a dano |
| `playerSeeded` | b | false | Só existe se plantada por um jogador |
| `onlyOnUnprotectedZone` | b | false | Só cresce em zonas não protegidas |

## Máquina de estados de crescimento

As plantas progridem através de uma sequência de estágios:

1. **Semente** — estágio inicial
2. **Broto</parameter>
</invoke>
