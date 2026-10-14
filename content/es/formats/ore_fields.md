---
title: "Campos de mineral"
description: "Las tablas minerals y mineralconfigs, fórmulas de generación de nodos, ciclo de vida de los nodos y mecánicas de extracción."
weight: 30
---

# Campos de mineral

Los datos de los minerales tienen dos niveles: **por tipo** (`minerals` — qué es el material y cuánto
produce una extracción) y **por zona y por tipo** (`mineralconfigs` — cuántos nodos hay,
qué tamaño tienen y cómo de llenos están). El estado del nodo en tiempo de ejecución reside en la tabla `mineralnodes`.

## `minerals`

| Columna | Tipo | Utilizado por | Significado |
|---|---|---|---|
| `idx` | int | `(MaterialType) idx` | El ordinal del enum `MaterialType` (1=Titan … 19=DHDT, 0=Undefined). Todas las combinaciones utilizan `mineralconfigs.materialtype = minerals.idx`. |
| `name` | varchar | `ToMaterialType()` | Nombre del tipo ("titan", "crude", …). |
| `definition` | int | `MaterialHelper` → objeto | La definición del objeto producido por la extracción (p. ej., titan → def 168). |
| `amount` | int | `DrillerModule` | **Unidades base por extracción** (titan 1500, crude 1500, stermonit 975, liquizit 450, epriton 450, …). |
| `extractionType` | int | `TerrainsModule` | 0 = Sólido (`OreLayer`), 1 = Líquido (`LiquidLayer`). |
| `enablereffectrequired` | bit | restricción de módulo | Si se requiere un efecto habilitador para extraer. |
| `geoscandocument` | int | objetos de escaneo | Objeto de documento de geoescaneo para este material. |

## `mineralconfigs`

Una fila por (zona, material). Consumido por `MineralConfigurationReader` → una
`MineralLayer` por fila:

| Columna | Tipo | Utilizado por | Significado |
|---|---|---|---|
| `zoneId` | int | construcción de capa | Zona propietaria. |
| `materialtype` | int | → `minerals.idx` | El material. |
| `maxnodes` | int | `MineralLayer.LoadMineralNodes` | Nodos que la zona mantiene de este tipo. |
| `maxtilespernode` | int | generador | Máximo de casillas por mancha (blob) de nodo; también determina el radio de espaciado (abajo). |
| `totalamountpernode` | int | generador | Material total en un nodo nuevo, distribuido entre las casillas de la mancha. |
| `minthreshold` | double | generador | Llenado mínimo normalizado por casilla (0–1); las casillas por debajo se descartan. |

### Fórmulas de generación de nodos (`MineralNodeGeneratorBase.cs`)

Para un nuevo nodo de un tipo con la configuración anterior:

```
radius  = floor( sqrt(maxtilespernode / π) ) × 2
spacing = start position must be ≥ 2 × radius from the nearest existing node
blob    = random-walk flood fill (4-tile brush) up to maxtilespernode valid tiles
tile[i] = ( noise[i] / max(noise) ) normalized into [minthreshold, 1]
         × (tile[i] / Σtile) × totalamountpernode
         × uniform(0.9, 1.1)          // jitter, then truncated to uint
```

Zonas de exclusión alrededor de bases de acoplamiento y teletransportadores (`KeepOutDist`): epriton = 100 casillas
(`MINERAL_DISTANCE_FROM_BASE_MIN`), flux ore = 200; todos los demás tipos = 0.

### Ejemplo práctico — Daoden (zone_ASI) crudo (id 2)

`maxnodes=8, maxtilespernode=1257, totalamountpernode=125,000,000, minthreshold=0.5`:

```
radius  = floor(√(1257/π)) × 2 = floor(20.0) × 2 = 40   → spacing ≥ 80 tiles
blob    = up to 1257 tiles
tile    = share ∈ [0.5, 1.0] × (125,000,000 / Σnormalized) × jitter
```

Un nodo de crudo lleno contiene 125 M de unidades; con la extracción base de 1500 unidades por ciclo de
perforación, eso equivale a aproximadamente 83 000 ciclos de material por nodo, y ~666 000 en los 8
nodos de la zona.

## Estado del nodo — `mineralnodes`

| Columna | Significado |
|---|---|
| `zoneid`, `materialtype` | Zona propietaria + tipo |
| `x, y, width, height` | Cuadro delimitador del nodo (área de la mancha) |
| `data` | `uint` comprimido por casilla (orden de filas dentro del cuadro) |

Ciclo de vida (`MineralNode.cs`, `MineralLayer.cs`):

- **Carga**: al iniciar la zona, se cargan todos los nodos almacenados; un nodo cuyo total sea ≤ **1%** de
  `totalamountpernode` se elimina.
- **Reposición**: si sobrevivieron menos de `maxnodes`, se generan nuevos nodos (fórmula anterior).
- **Expiración**: un nodo **intacto** expira después de **7 días** (`TimeTracker`); la minería
  reinicia el reloj. Un nodo cuyo valor máximo de casilla llega a 0 también expira.
- **Persistencia**: los nodos modificados se guardan en la base de datos mediante un temporizador de guardado de **30 minutos**.
- **Vinculación con Flux Ore**: la reducción/expiración de un nodo de `FluxOre` publica
  `OreNpcSpawnMessage` → el generador de NPCs escucha (`OreNPCSpawner`).

## Mecánicas de extracción (`MineralExtractor.cs`, `DrillerModule.cs`)

La cantidad de extracción es `minerals.amount` escalada por la propiedad
`mining_amount_modifier` del robot (agregada a partir de `mining_amount_modifier`,
`effect_mining_amount_modifier`, `drone_amplification_mining_amount_modifier`,
`effect_excavator_mining_amount_modifier`).

- **Sólido** (`OreLayer`): toma `min(tile value, amount)` de la **única casilla** sobre la que se
  encuentra el robot.
- **Líquido** (`LiquidLayer`): drena **todo el nodo**, empezando por las casillas más cercanas
  (cola de prioridad por distancia al cuadrado), hasta que se cubra la cantidad requerida.
- **Grava** (solo en zonas de entrenamiento, `GravelLayer`): lee el valor de la casilla pero no
  lo decrementa; los nodos de grava son inagotables.

El rendimiento por tipo (productos refinados) se encuentra en [Minerales](/es/content/ores/); el recuento de nodos por zona
está en el [Índice de zonas](/zones/zone-index/).

<!-- Developer notes: Zones/Terrains/Materials/Minerals/MineralConfiguration.cs
     (reader + config), MineralLayer.cs (LoadMineralNodes 1% delete + top-up,
     GenerateNewNode radius/tile/amount wiring, FluxOre events),
     Generators/MineralNodeGeneratorBase.cs (FindStartPosition, NormalizeNoise,
     CreateMineralNode, KeepOutDist), Generators/RandomWalkMineralNodeGenerator.cs
     (flood fill, 50k step cap), MineralNode.cs (uint[] values, 7-day expiry,
     30-min save), MineralNodeRepository.cs (mineralnodes table, compressed
     values), Minerals/MineralExtractor.cs (solid/liquid/gravel extraction),
     Modules/DrillerModule.cs (amount property + modifiers), Materials/MaterialHelper.cs
     (minerals.definition -> item), Zones/DistanceConstants.cs
     (MINERAL_DISTANCE_FROM_BASE_MIN = 100). -->
