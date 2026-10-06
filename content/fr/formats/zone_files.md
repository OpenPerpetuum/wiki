---
title: "Fichiers de zone"
description: "Format des fichiers de zone (GZT), structure des données de zone, et le pipeline de génération des cartes de zone."
weight: 22
---

# Fichiers de zone

Les **fichiers de zone** (GZT) sont les données binaires qui définissent le terrain,
les objets, et les entités d'une zone.

## Format GZT

Les fichiers GZT sont des fichiers binaires compressés qui contiennent :

- **Le terrain** (hauteur, texture)
- **Les objets** (minerais, plantes, structures)
- **Les entités** (PNJ, robots, conteneurs)
- **Les téléporteurs** (positions, canaux)
- **Les limites** (zones protégées, PvP)

## Pipeline de génération

Le pipeline de génération des cartes de zone :

1. **C# `ZoneMapSvg.cs`** — génère le SVG de base (nœuds, lignes de téléportation)
2. **Python `gen_zone_teleport_maps.py`** — post-traite le SVG (labels, couleurs)
3. **Les fichiers générés** sont commités dans le dépôt

## Cartes de zone

Les **cartes de zone** sont les SVG interactifs affichés sur les pages de zone :

- **Vue normale** — les nœuds et les téléporteurs
- **Vue couleur** — les familles de zones (TM, ICS, ASI, Gamma)
- **Vue hauteur** — le relief du terrain

## Notes pratiques

- **Les fichiers GZT sont binaires** — ils ne sont pas lisibles directement.
- **Les cartes SVG sont générées** — ne les éditez pas à la main.
- **Le pipeline est automatisé** — `make zonemaps` génère toutes les cartes.
- **Les zones sans TP inter-zones** sont exclues de la carte du monde.
