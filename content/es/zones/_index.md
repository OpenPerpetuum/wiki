---
title: "Zonas"
description: "Cómo se generan los recursos de las zonas: yacimientos de mineral, poblaciones de plantas y ejemplos de zonas reales."
weight: 50
---

# Zonas

Una **zona** es un mapa 2D de cuadrículas (habitualmente 2048×2048) donde los robots recolectan recursos. Cada zona cuenta con dos sistemas de recursos gestionados automáticamente por el servidor:

- **Yacimientos de mineral** — nodos dispersos en el suelo con una cantidad finita de material por casilla. Al agotarse por debajo del umbral, el nodo se elimina y se genera uno nuevo en otro lugar.
- **Plantas** — una población viva que crece, da frutos y se propaga casilla a casilla, manteniéndose cerca del **objetivo de fertilidad** de la zona.

Esta sección explica las mecánicas y muestra zonas reales como ejemplos prácticos.

| Página | Contenido |
|---|---|
| [Mapa](/zones/map/) | Todas las zonas trazadas en la cuadrícula x/y del servidor, coloreadas por galaxia, con las conexiones de portales conocidas |
| [Niveles de protección](/es/zones/protection/) | Niveles alfa, beta y gamma, reglas de PvP, indicadores de diodos y terraformación |
| [Generación](/zones/generation/) | Las reglas: cómo se crean, crecen y sustituyen los nodos de mineral y las poblaciones vegetales |
| [Índice de zonas](/zones/zone-index/) | Cada zona: tipo, protección, fertilidad, especies de plantas, configuración de minerales |
| [New Virginia](/zones/zone-tm/) | Ejemplo práctico — zona inicial PvE protegida (3 tipos de mineral, plantas básicas) |
| [Daoden](/zones/zone-asi/) | Ejemplo práctico — zona PvP alfa abierta (8 tipos de mineral incl. flux raro, flora rica) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Ejemplo práctico — zona PvP de alto nivel (menos nodos de mineral, baja fertilidad, plantas tier 2) |

Las mecánicas de recolección para jugadores se encuentran en [Recolección de recursos](/es/features/gathering/); las tablas de rendimiento de minerales y plantas están en [Contenido](/es/content/).

