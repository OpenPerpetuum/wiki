---
title: "Social"
description: "Communication et réputation : messagerie, canaux de discussion, amis, réputations (standings), pages jaunes, actualités et sondages."
weight: 140
---

# Social

Cette page traite de la communication et de la réputation : **messagerie**, **canaux de discussion**, **amis**,
**réputations (standings)** ainsi que des rubriques publiques **pages jaunes / actualités / sondages**.

> Les emplacements dans l'interface suivent la [vue d'ensemble de l'interface](/fr/features/ui/) (le bouton **Courrier** en haut à gauche ;
> la discussion et le volet social disposent de leurs propres fenêtres). Les mécaniques ci-dessous sont confirmées par le serveur.

## Messagerie

**Courrier personnel :**
- **Lister** le courrier, **ouvrir** un message, **envoyer** un courrier, **supprimer** un message.
- **Compteur de non-lus** — nombre de messages non lus.
- **Dossiers** — consulter les **dossiers utilisés**, **déplacer** un message vers un dossier, **supprimer** un dossier.

**Courrier collectif (corporation) :** diffusé à l'ensemble de votre corporation :
- **Envoyer**, **lister**, **ouvrir**, **supprimer**, **compteur de non-lus**.

## Canaux de discussion

Les **canaux** sont des salons de discussion nommés :

- **Créer** un canal, en **rejoindre** un, le **quitter**, y **parler**.
- **Lister** les canaux (l'ensemble ou seulement les vôtres).
- **Modération** (en tant que propriétaire ou officier du canal) : **expulser (kick)**, **bannir** / **débannir**,
  **définir le rôle d'un membre**, **rendre muet globalement**, consulter les membres **muets** / **bannis**.
- **Paramètres** : **définir un mot de passe**, **définir un sujet**, préférences de **notification**.

**Discussion directe** — message privé entre deux personnages.

## Amis

- **Envoyer une demande d'ami**, y **répondre**, **confirmer** une demande en attente.
- **Supprimer** un ami, **bloquer** un personnage.
- **Lister** vos amis.

Bloquer un personnage l'empêche de commercer ou de communiquer avec vous (voir [premiers pas](/fr/features/getting-started/)
pour le blocage de commerce par personnage).

## Réputations (Standings)

Le **standing** est une valeur de réputation numérique entre entités (personnages, corporations, alliances) :

- **Lister** vos réputations, consulter l'**historique des réputations**.
- **Définir une réputation** — là où c'est autorisé, fixer une valeur de réputation. Contraintes :
  - la **cible** doit être un personnage, une corporation (privée) ou une alliance (privée),
  - la **source** doit également être une entité valide,
  - vous ne pouvez pas vous attribuer une réputation à vous-même.
- **Réputations par défaut** — réputations de base pour les alliances/corporations par défaut.

Le standing est une valeur comprise entre **-10 et +10** (0 = neutre, valeur par défaut ; attribuer 0 efface l'entrée).
La **notoriété (reputation)** d'une entité est l'agrégat des réputations de chacun à son égard.
Un standing positif intervient dans des situations concrètes — par exemple durant une [intrusion](/fr/features/intrusion/),
une corporation bénéficiant d'un standing mutuel ≥ 10 est considérée comme un **allié** dont la victoire à un SAP n'endommage pas votre site.

Le standing influe sur la façon dont les factions et les autres joueurs vous traitent, vous et votre corporation
(voir [groupes](/fr/features/groups/)).

## Pages jaunes

Un annuaire public (annonces tenues par les corporations) :
- **Consulter** une annonce, en **publier** une, en **supprimer** une, **rechercher** dans l'annuaire.

## Actualités & sondages

- **Actualités** — consulter les **catégories** et la **liste des actualités** ; **compteur de nouveautés** pour les articles non lus.
- **Sondages** — **consulter** un sondage et y **répondre**.

## Notes pratiques

- **Courrier vs discussion** — le courrier est persistant et privé ; les canaux sont des salons de groupe en direct.
- **Le courrier collectif est un outil de corporation** — les officiers l'utilisent pour s'adresser à l'ensemble des membres.
- **Les standings sont directionnels** — la réputation de A envers B est distincte de celle de B envers A, et s'aligne sur votre corporation.
- **Le blocage est votre protection** — bloquez les pollueurs ou les commerçants malveillants.
- **Les canaux peuvent être verrouillés** — mots de passe et rôles filtrent qui peut entrer et s'exprimer.

<!-- TODO: only the mail/channel/social UI remains.
     Confirmed: standing range [-10,10], clamp in StandingHandler.SetStanding, 0 =
     neutral/clears the row (standings table empty on this deployment); reputation =
     aggregate toward a target (GetReputationFor); mission standing changes clamp to
     [0,10] (missionstandingchange/missionrequiredstanding); ally check = mutual
     standing >= 10 (intrusion).
     Developer notes: Mails/* (list/open/send/delete/folders, mass-mail variants);
     Channels/* (create/join/leave/talk, moderation, password/topic); Socials/* (friend
     request/reply/confirm/delete/block/list); Chat.cs; Standings/SetStanding.cs
     (entity-category + private-corp/alliance constraints, self-excluded),
     StandingHistory.cs, GetStandingForDefault*.cs; Corporations/YellowPages/*;
     GetNews.cs / NewsCategory.cs / FreshNewsCount.cs; PollGet.cs / PollAnswer.cs. -->
