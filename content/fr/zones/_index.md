---
title: "Zones"
description: "Comment les ressources de zone sont générées : gisements de minerai, flore et exemples de zones réelles."
weight: 50
---

# Zones

Une **zone** est une carte 2D de cases (généralement 2048×2048) où les robots récoltent des ressources. Chaque zone dispose de deux systèmes de ressources gérés automatiquement par le serveur :

- **Gisements de minerai** — nœuds dispersés dans le sol avec une quantité finie de matière par case. Épuisé sous un seuil, le nœud disparaît et un nouveau réapparaît ailleurs.
- **Plantes** — une population vivante qui croît, fructifie et se propage de case en case, maintenue proche de l'**objectif de fertilité** de la zone.

Cette section détaille ces mécanismes et présente des zones réelles en exemples concrets.

| Page | Contenu |
|---|---|
| [Carte](/zones/map/) | Toutes les zones tracées sur la grille x/y du serveur, colorées par galaxie, avec les liaisons de portails connues |
| [Niveaux de protection](/fr/zones/protection/) | Niveaux alpha, bêta et gamma, règles PvP, diodes d'état et terraformation |
| [Génération](/zones/generation/) | Les règles : création, croissance et remplacement des nœuds de minerai et de la végétation |
| [Index des zones](/zones/zone-index/) | Chaque zone : type, protection, fertilité, nombre d'espèces végétales, minerais |
| [New Virginia](/zones/zone-tm/) | Exemple concret — zone de départ PvE protégée (3 types de minerai, flore basique) |
| [Daoden](/zones/zone-asi/) | Exemple concret — zone PvP alpha ouverte (8 types de minerai dont flux rare, flore abondante) |
| [zone_gamma_z106](/zones/zone-gamma-z106/) | Exemple concret — zone PvP de haut niveau (gisements réduits, faible fertilité, flore T2) |

Les mécaniques de récolte côté joueur sont détaillées dans [Collecte de ressources](/fr/features/gathering/) ; les tables de statistiques se trouvent dans [Contenu](/fr/content/).

