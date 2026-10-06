---
title: "Production"
description: "Transformer des composants en objets : lignes de production, raffinage, réparation, reprocesseur, prototypes, et assurance."
weight: 70
---

# Production

La production est le processus de transformation des composants en objets. Vous pouvez
produire des modules, des munitions, des matériaux, et des prototypes.

> Les emplacements dans l'interface suivent l'[aperçu de l'interface client](/fr/features/ui/).
> Les mécaniques ci-dessous sont confirmées par rapport au serveur.

## Lignes de production

Un robot peut avoir des **lignes de production** — des emplacements dédiés où vous
placez des composants pour les assembler en objets. Les règles :

- Vous devez être **amarré** pour produire.
- Chaque ligne a un **temps de production** (variable selon l'objet).
- Les composants sont **consommés** à la fin de la production.
- Vous pouvez **annuler** une production en cours (les composants sont rendus).

## Types de production

| Type | Description |
|---|---|
| **Assemblage** | Combiner des composants en un objet |
| **Raffinage** | Transformer des minerais bruts en matériaux |
| **Réparation** | Réparer des modules endommagés |
| **Reprocesseur** | Extraire des composants d'un objet |
| **Prototype** | Créer un prototype d'objet |

## Prototypes

Les **prototypes** sont des objets spéciaux qui permettent de produire des objets
normaux sans composants. Ils sont obtenus via :

- La recherche (arbre technologique)
- Les missions
- Le marché

## Assurance

L'**assurance** protège un robot contre la perte en cas de destruction. Vous pouvez
assurer un robot à l'installation d'assurance d'une base (amarré) :

- Coût : défini par le type de robot (table `insuranceprices`)
- Durée : 15 jours + bonus d'extension
- Payout : payé en crédits si le robot est détruit
- Limite : 1 + (bonus d'extension) robots assurés

## Notes pratiques

- **Produisez ce dont vous avez besoin** — ne stockez pas de composants inutilisés.
- **Vérifiez les temps de production** — certains objets prennent des heures.
- **Assurez vos robots chers** — la perte d'un robot T4 est coûteuse.
- **Les prototypes sont des investissements** — ils produisent des objets gratuits
  mais coûtent cher à obtenir.
