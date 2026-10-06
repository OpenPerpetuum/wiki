---
title: "Architecture développeur"
description: "Architecture de haut niveau du jeu et du serveur Open Perpetuum, pour les développeurs et les devops."
---

# Architecture développeur

Cette page donne une vue d'ensemble de l'architecture d'Open Perpetuum pour les
développeurs et les devops.

## Stack technique

| Composant | Technologie |
|---|---|
| **Serveur de jeu** | C# / .NET |
| **Client** | C# / .NET (Windows), Proton (Linux) |
| **Base de données** | SQL Server |
| **Wiki** | Zola (Rust) + HTML/CSS/JS |
| **CI/CD** | GitHub Actions |

## Architecture du serveur

Le serveur de jeu est une application C# qui gère :

- **Les connexions** des clients
- **Le monde** (zones, robots, objets)
- **Les transactions** (production, marché, recherche)
- **Les missions**
- **Les PBS**

## Base de données

La base de données SQL Server contient :

- **entitydefaults** — toutes les définitions d'objets
- **components** — les recettes de production
- **techtree** — l'arbre technologique
- **extensions** — l'arbre d'extensions
- **zones** — les données de zones
- **items** — les objets des joueurs
- **characters** — les personnages

## Wiki

Le wiki est un site statique généré par **Zola** :

- **Contenu manuscrit** : `content/features/`, `content/menu/`, `content/formats/`
- **Contenu généré** : `content/content/` (items, ores, recipes, etc.)
- **Générateur C#** : `generator/Perpetuum.WikiGenerate/`
- **Assets** : `static/` (CSS, JS, images, SVG)

## CI/CD

Le pipeline CI/CD :

1. **Build** — compile le générateur C#
2. **Generate** — génère le contenu depuis la base de données
3. **Zonemaps** — génère les cartes de zones
4. **Build wiki** — build le site Zola
5. **Test** — exécute les tests Playwright
6. **Deploy** — déploie sur GitHub Pages

## Notes pratiques

- **Le générateur C# est la source de vérité** — le contenu est généré, pas écrit à la main.
- **La base de données est en lecture seule** — le générateur ne modifie jamais les données.
- **Le wiki est statique** — pas de backend, tout est pré-généré.
- **Les tests Playwright** vérifient les liens, la navigation, et l'i18n.
