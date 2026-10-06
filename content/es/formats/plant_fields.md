---
title: "Campos de las plantas"
description: "Formato del archivo de reglas de las plantas (GenXY), cada campo de regla con tipo, valor por defecto y consumidor, más la máquina de estados de crecimiento."
weight: 380
---

# Campos de las plantas

El comportamiento de las plantas está definido por especie por un **archivo de reglas**
(texto plano) bajo `$GameRoot/plantrules/`.

## Formato del archivo

Una `key=value` por línea; los comentarios de estilo `//` se eliminan. Los valores
usan los **caracteres de token GenXY** (`GenxyReader.cs`):

| Token | Analizado como | Ejemplo |
|---|---|---|
| `#` | Número entero decimal | `#100` = 100 |
| `.` | Número flotante | `.5` = 0.5 |
| `s` | Cadena de caracteres | `sHello` |
| `b` | Booleano | `b1` = true |
| `c` | Carácter | `cA` = 'A' |

## Campos de reglas

| Campo | Tipo | Defecto | Descripción |
|---|---|---|---|
| `fertility` | # | 1 | Frecuencia de aparición de la planta |
| `growRate` | # | 1 | Número de ciclos por etapa de crecimiento |
| `spreading` | # | 1 | Tendencia a crecer en grupos |
| `killDistance` | # | 0 | Espaciamento mínimo entre plantas |
| `slope` | # | 0 | Pendiente máxima del suelo |
| `minSlope` | # | 0 | Pendiente mínima del suelo |
| `allowedAltitudeLow` | # | 0 | Altitud mínima |
| `allowedAltitudeHigh` | # | 100 | Altitud máxima |
| `allowedWaterLevelLow` | # | 0 | Distancia mínima de la orilla |
| `allowedWaterLevelHigh` | # | 100 | Distancia máxima de la orilla |
| `fruitingState` | # | 3 | Etapa de crecimiento para la fructificación |
| `fruitDefinition` | s | – | Definición del fruto producido |
| `fruitAmount` | # | 1 | Cantidad de fruto producida |
| `maxAmount` | # | 100 | Número máximo en una zona de procesamiento |
| `health` | # | 10 | Puntos de vida por etapa |
| `damageScale` | # | 1 | Resistencia al daño |
| `playerSeeded` | b | false | Solo existe si plantada por un jugador |
| `onlyOnUnprotectedZone` | b | false | Solo crece en zonas no protegidas |

## Máquina de estados de crecimiento

Las plantas progresan a través de una secuencia de etapas:

1. **Semilla** — etapa inicial
2. **Brote** — la planta comienza a crecer
3. **Joven** — la planta está en crecimiento
4. **Maduro** — la planta está lista para fructificar
5. **Fructificación** — la planta produce fruto (cosechable)

Cada etapa toma `growRate` ciclos de crecimiento antes de avanzar aleatoriamente.
