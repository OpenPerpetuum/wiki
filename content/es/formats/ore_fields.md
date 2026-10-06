---
title: "Campos de los minerales"
description: "Formato de las reglas de los minerales (GenXY), cada campo con tipo, valor por defecto y consumidor."
weight: 390
---

# Campos de los minerales

Los minerales están definidos por especie en la base de datos. Los datos de
minerales se cargan desde la tabla `minerals` y las `entitydefaults`.

## Campos de datos

| Campo | Tipo | Descripción |
|---|---|---|
| `definition` | int | ID de la definición |
| `definitionname` | string | Nombre de la definición (ej: `def_titanium`) |
| `type` | string | Tipo de mineral (sólido, líquido) |
| `charge` | # | Carga del mineral (densidad) |
| `mass` | # | Masa del mineral |
| `value` | # | Valor del mineral |

## Tipos de minerales

| Tipo | Descripción |
|---|---|
| **Sólido** | Se agota por tile |
| **Líquido** | Extraído continuamente desde el campo |

## Minerales disponibles

Los minerales están listados en [Contenido → Minerales](/content/ores/). Cada mineral
tiene:

- Un **nombre** (ej: Titanium, Epriton, Fluxore)
- Un **tipo** (sólido o líquido)
- Una **carga** (densidad)
- Una **masa**
- Un **valor**
- **Componentes** (para la producción)

## Notas prácticas

- **Los minerales sólidos** se agotan por tile.
- **Los minerales líquidos** son más fáciles de minar (continuos).
- **La carga** determina la densidad del mineral.
- **El valor** determina el precio del mineral.
