---
title: "Campos de plantas"
description: "Formato de archivo de reglas de plantas (GenXY), cada campo de regla con tipo, valor por defecto y consumidor, además de la máquina de estados de crecimiento."
weight: 20
---

# Campos de plantas

El comportamiento de las plantas se define por especie mediante un **archivo de reglas** (texto plano) bajo
`$GameRoot/plantrules/`. Qué archivos pertenecen a una zona es el mapeo de base de datos
`plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset`; la carga y combinación la realiza
`PlantRuleLoader.cs`, y el mapeo de campos a objetos es `PlantRule.cs`.

## Formato de archivo

Una línea `clave=valor` por línea; los comentarios de estilo `//` se eliminan. Los valores utilizan **caracteres de token
GenXY** (`GenxyReader.cs` — el primer carácter selecciona el tipo y la base numérica):

| Token | Interpretado como | Ejemplo |
|---|---|---|
| `n` | int, decimal | `n125`, `n-1` |
| `N` | int[], decimal, separado por comas | `N5,5,5,5` |
| `f` | double, decimal | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **hexadecimal** | `iFF` |
| `L` | long, **hexadecimal** | `L100` |
| `4` | int[], **hexadecimal** | `41,2,3` → [1, 2, 3] |

### ⚠ La trampa del "array simple"

Los archivos también contienen valores como `blockingHeight=40,3,3,4` sin **ningún token explícito**.
El analizador no los trata como casos especiales: el `4` inicial se consume como el token
`IntegerArray` (hexadecimal), y el resto se analiza como hexadecimal. Por lo tanto:

```
blockingHeight=40,3,3,4   →  token '4' + hex array "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  token 'N' + decimal array         →  [0, 8, 11, 14]
```

Ambas sintaxis resultan en `int[]`, y el `0` inicial es lo que el `4` "se traga". Por esta
razón, todos los arrays simples en los archivos distribuidos comienzan con `4` — es una convención
que mantiene el primer elemento en el valor deseado. **Al escribir nuevos archivos de reglas,
utiliza el prefijo `N` de forma explícita**; los valores ≥ 10 en un array simple se analizarían como hexadecimales
y cambiarían silenciosamente de significado.

### Herencia

Una clave `source=$other_rule.txt` carga primero `other_rule.txt` y aplica las claves del
archivo actual como anulaciones (`PlantRuleLoader.LoadRuleByName`). Ejemplo:
`irontree_t2.txt` es simplemente:

```
source=$irontree_lo.txt
fruitAmount=n125
```

## Referencia de campos

Todos los campos se leen del diccionario combinado de opciones (`PlantRule.cs`). Las claves que faltan
recurren al valor por defecto mostrado.

| Clave | Tipo / por defecto | Consumido por | Efecto |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | El valor enum `PlantType` para esta especie (1=GrassA … 19=Devrinol). También el byte `PlantInfo.type` almacenado por casilla. |
| `name` | string | carga útil de info del cliente | Nombre mostrado. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | Peso en el sorteo ponderado que elige una especie para una casilla **sin** plantas vecinas. 0 = nunca aparece. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | Multiplicador de peso cuando una casilla **tiene** vecinas: peso del candidato = `neighbourCount × spreading`. 0 = nunca gana el sorteo de propagación. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | Distancia mínima desde cualquier planta existente del mismo tipo; 0/negativo = sin límite. |
| `growRate` | int (0) | `GrowPlantOnTile` | Número de intervalos (ticks) del cubo que el byte `PlantInfo.time` debe acumular antes de que la máquina de estados tire los dados. Mayor = más lento. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | Rango de pendiente permitido en la capa de pendiente derivada. Fuera del rango, la planta se elimina. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | Rango de altitud, comparado con `Altitude / 4` (el `/4` coincide con las coordenadas del cliente). Escalado por el `plantaltitudescale` de la zona. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | Rango para `altitude/4 − waterLevel/4` — crea vegetación costera. También escalado por altitud. |
| `allowedTerrainTypes` | int[] (vacío) | `ValidateTile` | Bytes de `groundType` permitidos (ver [Archivos de zona](/es/formats/zone-files/)). Vacío = en ningún sitio. Se omite completamente si se activa `allowedOnNonNatural`. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | Primer estado que produce frutos. −1 ⇒ `NotFruiting` (nunca recolectable). |
| `fruitDefinition` | int (−1) | recolección | Definición de objeto del fruto. |
| `fruitMaterialName` | string | visualización | Nombre del fruto (p. ej., `$prismocitae`). |
| `fruitAmount` | byte (0), limitado 0–255 | `GrowPlantOnTile` | Máximo de frutos por planta. La primera entrada en el estado de fructificación llena el 5–15%; cada tick de crecimiento posterior añade 15–25%, con límite en 100%. |
| `health` | byte[] por estado | `GrowPlantOnTile`, combate | Puntos de vida por estado de crecimiento. Al cambiar de estado, la **proporción** de vida actual se traslada al nuevo estado. |
| `blockingHeight` | int[] por estado | `GrowPlantOnTile`, conteo de apariciones | Altura de bloqueo por estado; `>0` activa el bit `Plant` en la capa de bloqueo (walkable=false) y hace que la planta cuente para el objetivo de fertilidad de la zona. |
| `maxAmount` | int (−1) | `SpawnPlants` | Límite por zona en el número de ejemplares de esta especie; −1 = ilimitado. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, sorteo de fertilidad | Excluido de **todas** las apariciones naturales; solo existe donde un jugador lo haya plantado. |
| `damageScale` | double (1.0) | combate de plantas | Multiplicador de daño recibido. |
| `onlyOnUnprotectedZone` | bool (0) | validación de aparición | Solo crece donde la zona está desprotegida. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | Omite las comprobaciones de bits de control, tipo de terreno y pendiente (crece en casillas "artificiales"). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (muerte) | Al morir, limpia los bits de control ConcreteA/B bajo la casilla. |
| `state_N` | int[] | `GetNextState` | Opciones de siguiente estado para el estado `N` — cada elemento se elige **de manera uniforme y aleatoria**. |
| `action_N` | int[] | `GetNextState` | Siguientes opciones de `PlantType` para el estado `N` (uniforme). Un valor de acción de `0` (NotDefined) significa **muerte**. |

La coherencia se impone al cargar (`CheckConsistency`): `len(health) == len(blockingHeight) == number of states`.

## La máquina de estados de crecimiento

En cada intervalo (tick) del cubo de 32×32, para cada casilla de planta (`GrowPlantOnTile`):

1. Si `time < growRate`: `time++`, fin.
2. En caso contrario: `time = 0`, tirar los dados para `state_N` y `action_N` para el estado actual:
   - `action == 0` → la planta muere (señal de eliminación `type:0, state:1` para el cliente);
     si `placesConcrete`, limpiar el hormigón bajo la casilla.
   - en caso contrario → `type = action`, `state = next`, `health = healthRatio × Health[newState]` (se mantiene la proporción de daño).
   - Fruto: si `newState == fruitingState`, `material = fruitAmount × uniform(0.05, 0.15)`; si `newState > fruitingState`, `material += fruitAmount × uniform(0.15, 0.25)` (con un límite de `fruitAmount`); de lo contrario, `material = 0`.
   - Altura de bloqueo = `blockingHeight[newState]`; el bit `Plant` de la capa de bloqueo sigue a `height > 0`.

### Ejemplo práctico — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → 1/… weight in the no-neighbour draw
spreading=n2        → cluster weight = 2 × neighbours
growRate=n1         → rolls a state every cube tick (fast)
maxAmount=n190      → at most 190 per cube
health=N5,5,5,5     → 5 HP in every state
blockingHeight=40,0,0,0 → parsed as [0,0,0,0]: grass NEVER blocks
fruitingState=n-1   → NotFruiting: grass is never harvestable
state_0=40,0,1      → [0,0,1]: 2/3 stay in state 0, 1/3 advance
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → in the final state: 3/4 stay, 1/4 die
```

Por lo tanto, una casilla de hierba: avanza aproximadamente un estado cada 3 ticks de media, y en el último
estado tiene un 25% de probabilidad por tick de morir y volver a sembrarse — una especie de cobertura
de renovación constante sin frutos.

### Ejemplo práctico — `wall.txt` (12 estados, con prefijo `N`)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (puede retroceder de estado), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: una fortificación plantada por el jugador que solo
existe en zonas desprotegidas, con un límite de 15 por cubo, que crece (y ocasionalmente
decrece) a lo largo de 12 estados hasta alcanzar una altura de 14 y 255 HP.

## Dónde reside el estado por casilla

El estado en tiempo de ejecución por casilla es la estructura `PlantInfo` de 7 bytes en el archivo de capa de plantas
de la zona (`type, state, time, spawn, health, material, groundType`) — ver
[Archivos de zona](/es/formats/zone-files/). El byte `spawn` es una probabilidad de aparición por casilla
incorporada en el archivo de zona — `0` marca una casilla estéril (las plantas en ella se limpian durante
la validación, nunca brota nada); cualquier otro valor significa que un intento de regeneración de plantas en esa
casilla pasa una puerta aleatoria con una probabilidad ≈ `spawn/256`. El servidor nunca escribe este
byte. Datos reales: cada casilla de `plants.0106.bin` contiene `0x83` (≈ 51%).

## Carga útil del cliente

`PlantRuleExtensions.GetPlantInfoForClient` envía, por especie: `index`, `mineral`
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
