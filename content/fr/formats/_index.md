---
title: "Formats"
description: "Référence développeur : comment chaque champ de statistique est stocké, parsé et utilisé par le serveur."
weight: 60
---

# Formats

Référence de champs pour développeurs. Chaque page suit un champ de statistique
depuis son stockage (colonne DB, clé de fichier de règles, ou octet de couche
binaire) jusqu'au code qui le consomme, avec des exemples chiffrés. Les
résumés « que cela signifie-t-il dans le jeu » destinés aux joueurs se trouvent
dans les sections [features](/fr/features/) et [content](/content/) — ici sont les
types exacts, les valeurs par défaut, les formules et les chemins de code.

| Page | Contenus |
|---|---|
| [Champs de plantes](/fr/formats/plant-fields/) | le format des fichiers de règles de plantes (GenXY), chaque champ de règle avec son type/sa valeur par défaut/ses consommateurs, la machine à états de croissance, les vérifications de validation |
| [Champs de minerais](/fr/formats/ore-fields/) | les colonnes `minerals` + `mineralconfigs`, les formules de génération de nœuds, le cycle de vie et la persistance des nœuds, la mécanique d'extraction |
| [Champs de déployables](/fr/formats/deployable-fields/) | comment identifier un déployable, l'appariement capsule↔objet et les champs agrégés qui pilotent les objets placés |
| [Fichiers de zone](/fr/formats/zone-files/) | les fichiers binaires de couches de terrain : layout des structures, bits de drapeaux, cycles de stockage et ce qui vit plutôt dans la base de données |

Conventions :

- **GenXY** est la sérialisation de configuration pour les fichiers de règles et
  `entitydefaults.options` (jetons selon `GenxyToken.cs` ; voir
  [Champs de plantes → Format de fichier](/fr/formats/plant-fields/)).
- Les chemins de code sont relatifs à `src/`.
- Quand une valeur est une **constante** (pas de données), le fichier et le nom
  de la constante sont donnés.
