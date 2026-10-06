---
title: "Archivos de zona"
description: "Formato de los archivos de zona (GZT), estructura de los datos de zona, y el pipeline de generación de los mapas de zona."
weight: 400
---

# Archivos de zona

Los **archivos de zona** (GZT) son las datos binarias que definen el terreno,
los objetos, y las entidades de una zona.

## Formato GZT

Los archivos GZT son archivos binarios comprimidos que contienen:

- **El terreno** (altura, textura)
- **Los objetos** (minerales, plantas, estructuras)
- **Las entidades** (PNJ, robots, contenedores)
- **Los teletransportadores** (posiciones, canales)
- **Las límites** (zonas protegidas, PvP)

## Pipeline de generación

El pipeline de generación de los mapas de zona:

1. **C# `ZoneMapSvg.cs`** — genera el SVG de base (nodos, líneas de teletransporte)
2. **Python `gen_zone_teleport_maps.py`** — post-procesa el SVG (labels, colores)
3. **Los archivos generados** son commitados en el repositorio

## Mapas de zona

Los **mapas de zona** son los SVG interactivos mostrados en las páginas de zona:

- **Vista normal** — los nodos y los teletransportadores
- **Vista color** — las familias de zonas (TM, ICS, ASI, Gamma)
- **Vista altura** — el relieve del terreno

## Notas prácticas

- **Los archivos GZT son binarios** — no son legibles directamente.
- **Los mapas SVG son generados** — no los edites a mano.
- **El pipeline es automatizado** — `make zonemaps` genera todos los mapas.
- **Las zonas sin TP inter-zonas** están excluidas del mapa del mundo.
