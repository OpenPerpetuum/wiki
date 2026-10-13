---
title: "Formatos"
description: "Referencia para desarrolladores: cómo el servidor almacena, procesa y utiliza cada campo de estadísticas."
weight: 60
---

# Formatos

Referencia de campos orientada a desarrolladores. Cada página rastrea un campo de estadísticas desde su almacenamiento
(columna de BD, clave de archivo de reglas o byte de capa binaria) a través del código que lo consume,
con ejemplos numéricos resueltos. Los resúmenes orientados a los jugadores sobre «qué significa esto en el juego» se encuentran
en las secciones de [características](/es/features/) y [contenido](/content/); aquí es donde se detallan
los tipos exactos, valores por defecto, fórmulas y rutas de código.

| Página | Contenido |
|---|---|
| [Campos de plantas](/es/formats/plant-fields/) | Formato de archivo de reglas de plantas (GenXY), cada campo de regla con tipo/valor por defecto/consumidor, la máquina de estados de crecimiento, comprobaciones de validación |
| [Campos de minerales](/es/formats/ore-fields/) | Columnas `minerals` + `mineralconfigs`, fórmulas de generación de nodos, ciclo de vida y persistencia de nodos, mecánicas de extracción |
| [Campos de desplegables](/es/formats/deployable-fields/) | Cómo se identifican los desplegables, emparejamiento cápsula↔objeto y los campos agregados que controlan los objetos colocados |
| [Archivos de zona](/es/formats/zone-files/) | Los archivos de capas de terreno binarias: estructuras, bits de flags, ciclo de guardado y qué reside en la BD en su lugar |

Convenciones:

- **GenXY** es la serialización de configuraciones utilizada para archivos de reglas y `entitydefaults.options`
  (caracteres de tokens según `GenxyToken.cs`; consulte [Campos de plantas → formato de archivo](/es/formats/plant-fields/)).
- Las rutas de código son relativas a `src/`.
- Cuando un valor es una **constante** (no un dato), se indica el archivo y el nombre de la constante.