---
title: "Arquitectura del desarrollador"
description: "Arquitectura de alto nivel del juego y servidor Open Perpetuum, para desarrolladores y devops."
---

# Arquitectura del desarrollador

Esta página da una vista general de la arquitectura de Open Perpetuum para
desarrolladores y devops.

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| **Servidor de juego** | C# / .NET |
| **Cliente** | C# / .NET (Windows), Proton (Linux) |
| **Base de datos** | SQL Server |
| **Wiki** | Zola (Rust) + HTML/CSS/JS |
| **CI/CD** | GitHub Actions |

## Arquitectura del servidor

El servidor de juego es una aplicación C# que gestiona:

- **Las conexiones** de los clientes
- **El mundo** (zonas, robots, objetos)
- **Las transacciones** (producción, mercado, investigación)
- **Las misiones**
- **Las PBS**

## Base de datos

La base de datos SQL Server contiene:

- **entitydefaults** — todas las definiciones de objetos
- **components** — las recetas de producción
- **techtree** — el árbol tecnológico
- **extensions** — el árbol de extensiones
- **zones** — las datos de zonas
- **items** — los objetos de los jugadores
- **characters** — los personajes

## Wiki

El wiki es un sitio estático generado por **Zola**:

- **Contenido escrito a mano**: `content/features/`, `content/menu/`, `content/formats/`
- **Contenido generado**: `content/content/` (objetos, minerales, recetas, etc.)
- **Generador C#**: `generator/Perpetuum.WikiGenerate/`
- **Assets**: `static/` (CSS, JS, imágenes, SVG)

## CI/CD

El pipeline CI/CD:

1. **Build** — compila el generador C#
2. **Generate** — genera el contenido desde la base de datos
3. **Zonemaps** — genera los mapas de zonas
4. **Build wiki** — build del sitio Zola
5. **Test** — ejecuta las pruebas Playwright
6. **Deploy** — despliega en GitHub Pages

## Notas prácticas

- **El generador C# es la fuente de verdad** — el contenido es generado, no escrito a mano.
- **La base de datos es solo lectura** — el generador nunca modifica las datos.
- **El wiki es estático** — sin backend, todo es pre-generado.
- **Las pruebas Playwright** verifican los enlaces, la navegación, y el i18n.
