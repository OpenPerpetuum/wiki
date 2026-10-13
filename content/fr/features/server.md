---
title: "Serveur & référence"
description: "Informations sur le serveur, meilleurs scores, téléchargement de données de référence et boutique en jeu."
weight: 170
---

# Serveur & référence

Cette page couvre les « méta-systèmes » : informations sur le serveur et le système, meilleurs scores, données de référence
téléchargées par le client et boutique en jeu.

> Les emplacements dans l'interface suivent la [vue d'ensemble de l'interface](/fr/features/ui/). Les mécaniques ci-dessous
> sont confirmées par le serveur.

## Informations sur le serveur et le système

- **Infos serveur** — état général et informations sur le serveur.
- **Infos système** — détails au niveau du système hôte.
- **État d'arrêt du serveur** — indique si un arrêt programmé est en cours (en lecture seule pour les joueurs ;
  l'arrêt lui-même est une action d'administration).

## Meilleurs scores (High scores)

- **Meilleurs scores du serveur** — les meilleurs résultats sur l'ensemble du serveur.
- **Mes meilleurs scores** — vos records personnels.

Voir également [combat](/fr/features/combat/) pour la manière dont les éliminations alimentent ces classements.

## Données de référence

Le client télécharge des données de référence statiques depuis le serveur afin d'afficher correctement le contenu.
Il s'agit de **consultations en lecture seule**, et non d'actions de joueur :

- **Effets** — définitions des effets.
- **Énumérations (Enums)** — valeurs d'énumération.
- **Valeurs par défaut des entités (Entity defaults)** — définitions de base des entités.
- **Champs agrégés (Aggregate fields)** — données des champs agrégés.
- **Unités de configuration des définitions (Definition config units)** — configuration par définition.
- **Distances** — constantes de distance utilisées par le client.
- **Commandes** — liste des commandes connues (référence côté client).
- **Failles (Rifts)** — définitions des failles (voir aussi la liste des failles de zone).

Vous n'« utilisez » pas ces données ; le client les récupère à la demande. Elles sont listées ici car elles figurent
dans l'inventaire des commandes.

## La boutique

La boutique en jeu (intégration de paiement) :

- **Lister les produits** — voir ce qui est en vente.
- **Initier une transaction** — commencer un achat.
- **Finaliser une transaction** — conclure un achat.

Les achats en boutique sont des transactions en argent réel (ou équivalent) ; les produits précis et leurs tarifs
dépendent du contenu de la boutique.

## Notes pratiques

- **Les données de référence sont récupérées automatiquement** — vous ne les déclenchez jamais manuellement ;
  elles maintiennent le client synchronisé avec le contenu du serveur.
- **Les meilleurs scores sont vos faits d'armes** — consultez vos records personnels et ceux du serveur.
- **Les transactions en boutique se font en deux étapes** — initiation, puis finalisation ; ne considérez pas un achat achevé
  tant qu'il n'est pas finalisé.
- **L'état d'arrêt est informatif** — il vous avertit si une fenêtre de maintenance approche.

<!-- TODO: only the reference-data payload list (client-side) remains.
     Confirmed: the real-money store is NOT active on this deployment — the Steam
     transaction commands (steamGetProducts / steamStartTransaction /
     steamFinishTransaction) are declared in Commands.cs but no handler is registered
     in the bootstrapper, and the store content tables (storeitems, storecategories)
     are empty.
     Developer notes: ServerInfoGet.cs / SystemInfo.cs / ServerShutDownState.cs;
     GetHighScores.cs / GetMyHighScores.cs; GetEffects.cs / GetEnums.cs /
     GetEntityDefaults.cs / GetAggregateFields.cs / GetDefinitionConfigUnits.cs /
     GetDistances.cs / GetCommands.cs / GetRifts.cs; SteamGetProducts.cs /
     SteamStartTransaction.cs / SteamFinishTransaction.cs. -->
