---
title: "Archivos de zona"
description: "Los archivos binarios de capas de terreno: nomenclatura, diseño de estructuras, bits de control, el ciclo de guardado y qué reside en la base de datos."
weight: 50
---

# Archivos de zona

El terreno de una zona se almacena como un conjunto de **archivos de capas binarias**, uno por capa, junto a
los datos de la zona. El nombre es `{layer}.{zoneid:0000}.bin`
(`Zone.CreateTerrainDataFilename`) — p. ej., `plants.0042.bin` para la zona 42. Las capas son
arrays planos de una estructura de tamaño fijo, **ordenados por filas, ancho × alto** (por defecto 2048×2048 =
4 194 304 casillas).

## Las capas

| Archivo | Estructura | Bytes/casilla | Contenido |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (byte) + `height` (byte) — obstáculos, plantas, decoración, islas |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (o 1) | bits de control por casilla (ver peculiaridad más abajo) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | el estado de las plantas por casilla (abajo) |
| `altitude.NNNN.bin` | `ushort` | 2 | elevación; comparada como `value / 4` en comprobaciones de plantas (escalado de coordenadas del cliente) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | solo zonas terraformables: máscara de mezcla por casilla (abajo) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | solo zonas terraformables: elevación previa a la terraformación en disco — **no leída por el servidor** (abajo) |

Capas derivadas (calculadas en la carga, **no** son archivos): `SlopeLayer` (a partir de la altitud) y
`Passable` (a partir de bloques + pendiente + posiciones transitables de la BD, solo en zonas no terraformables).
En zonas terraformables, la altitud se envuelve en un `TerraformableAltitude`, que
calcula un rango de **barrera** por casilla en la carga: `blend/65535` mezcla las constantes
1850 → altitud original (mín) y 30000 → altitud original (máx), y luego restringe el
rango para que siempre contenga el valor actual. Las actualizaciones de altitud terraformada se restringen
a esa barrera — de modo que `blend = 0` deja una casilla libremente terraformable entre 1850 y
30000, mientras que `blend = 65535` la fija a su elevación original. (Los
archivos `altitude_original.NNNN.bin` en disco contienen las elevaciones previas a la terraformación para
herramientas externas; el servidor toma su instantánea de altitud original en memoria a partir del archivo
`altitude.NNNN.bin` cargado y nunca lee ese nombre de archivo).

### `BlockingInfo` (2 bytes)

`flags` es `BlockingFlags` (byte):

| Bit | Nombre |
|---|---|
| 1 | Obstacle |
| 2 | Plant |
| 4 | Decor |
| 8 | Island |

`NonNaturally` = Decor \| Island \| Obstacle. `height` es la altura de bloqueo de paso de la casilla
(la altura de bloqueo de la planta la escribe aquí el código de crecimiento de la planta).

### `TerrainControlFlags` (capa de control)

Conjunto de flags `ushort`:

| Bit | Nombre |
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

(La numeración 512/1024 sigue `1 << n`; el bit 32 no se utiliza). Una casilla permite plantas cuando
`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`.

**Peculiaridad de almacenamiento**: el cargador acepta tanto archivos de control de **1 byte/casilla** como de
**2 bytes/casilla** — si la longitud del archivo coincide con el número de casillas, cada byte se expande a
un `TerrainControlFlags`; de lo contrario, se lee el array raw de `ushort`
(`LayerFileIO.LoadLayerData`). Todas las zonas activas utilizan el **formato de 2 bytes**
(`control.0000.bin` = 8 388 608 B = 4 194 304 × 2); el formato de 1 byte (4 MB) es una
alternativa heredada que el cargador aún admite.

### `PlantInfo` (7 bytes) — el estado de la casilla de planta

| Byte | Campo | Significado |
|---|---|---|
| 0 | `type` | `PlantType` (0 = vacía; 1..19 según [Campos de plantas](/es/formats/plant-fields/)) |
| 1 | `state` | Índice de estado de crecimiento (en la tabla `state_N` de la regla) |
| 2 | `time` | Acumulador de ticks de crecimiento (comparado contra el `growRate` de la regla) |
| 3 | `spawn` | **Probabilidad de aparición por casilla, integrada en el archivo de zona; el servidor nunca la escribe** (no existe ninguna asignación en ninguna parte del código — `PlantInfo.Clear()` la preserva deliberadamente). 0 = casilla estéril: cualquier planta que ya esté en ella se limpia de inmediato durante la validación y nunca brota nada. De lo contrario, actúa como un filtro por intento: durante la pasada de regeneración de plantas, una casilla vacía aleatoria solo se acepta si `FastRandom.NextByte() < spawn`, es decir, probabilidad de éxito por casilla ≈ `spawn/256`. |
| 4 | `health` | Vida actual (proporción de la vida por estado de la regla) |
| 5 | `material` | Cantidad actual de fruto (0–255) |
| 6 | `groundType` | Byte de `GroundType` (0=Darkrocks … 17=Sand-ish, 20=undefined) — la clase de terreno que comprueba `allowedTerrainTypes` en la regla de la planta |

### Ejemplo práctico — tamaños de archivo para una zona de 2048×2048 (verificado contra archivos reales)

```
blocks    4,194,304 tiles × 2 B = 8,388,608 B (8 MB)
plants    4,194,304 tiles × 7 B = 29,360,128 B (28 MB)
altitude  4,194,304 tiles × 2 B = 8,388,608 B (8 MB)
control   4,194,304 tiles × 2 B = 8,388,608 B (8 MB, 2-byte form; a 1-byte legacy file would be 4 MB)
```

**Comprobación con datos reales** (`plants.0106.bin`, la zona gamma terraformable): las 4 194 304
casillas tienen `spawn = 0x83` (131/256 ≈ 51% de probabilidad por intento) y `type = 0` excepto
10 casillas que contienen plantas vivas — el mapa de generación es un campo de probabilidad completo precalculado para toda la zona,
independiente de dónde se encuentren las plantas actualmente.

No todas las zonas tienen todos los archivos: 66 de las 84 zonas distribuyen un `plants.NNNN.bin`. Las 18
que no lo tienen son las variantes gamma heredadas y reemplazadas (`zone_tm_g_*`, `zone_ics_g_*`,
`zone_asi_g_*`, IDs 20–43), que no se cargan. El directorio de capas es
`$GameRoot/layers/`.

## El ciclo de guardado (`IntervalLayerSaver.cs`)

- Cada capa mutable (bloques, control, plantas, altitud) está supervisada por un
  `IntervalLayerSaver<T>`; cualquier escritura en una casilla/área activa un indicador de modificación (dirty flag).
- El guardador está registrado como un proceso en un temporizador de **2 horas**
  (`TerrainsModule`); una capa modificada se escribe cuando se activa el temporizador.
- Las escrituras se dirigen a un archivo `.tmp<ticks>.bin`, se **verifican mediante MD5** contra una relectura y
  solo entonces reemplazan el archivo real.
- Al detener el servidor, las capas modificadas se guardan una vez más.
- Los nodos de minerales **no** están en estos archivos — persisten en la tabla de base de datos
  `mineralnodes` (volcado cada 30 minutos, ver [Campos de mineral](/es/formats/ore-fields/)).

## Qué es y qué no es un archivo

| Datos | Dónde |
|---|---|
| Capas de terreno (bloques/control/plantas/altitud) | Archivos `.bin` |
| Estado de los nodos de mineral | Base de datos `mineralnodes` |
| Especies de plantas por zona | Base de datos `plantrules` + **archivos** de reglas (`$GameRoot/plantrules/*.txt`) |
| Configuración de la zona (fertilidad, tamaño, tipo, conjunto de reglas) | Base de datos `zones` |
| Configuración de minerales | Base de datos `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1-vs-2 byte control handling, safe zero-fill on size mismatch);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty flag, MD5 + tmp rename, stop-save);
     Bootstrapper/Modules/TerrainsModule.cs (layer load order: blocks, control, plants,
     altitude, blend; slope + passable derivation; 2h saver + 2h material process). -->
