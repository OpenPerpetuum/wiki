---
title: "Client & config PC"
description: "Lancer le client sous Windows et Linux, multi-boxing dans les règles, échelle de l'interface, et lancement sans droits admin."
weight: 24
---

# Client & config PC

Notes pratiques pour lancer le client Perpetuum.

## Les règles d'abord

Le multi-boxing (plusieurs clients contrôlant plusieurs personnages) est autorisé
**dans certaines limites**. Règles de fair-play à connaître avant de le faire :

- **Pas d'automatisation ni de logiciel de contrôle multi-client** — jamais.
- **Pas plus de 5 comptes simultanément actifs.**
- Pas de comptes enregistrés avec des adresses e-mail factices, invalides ou
  injoignables — l'adresse doit être la vôtre.

Les violations peuvent entraîner un bannissement immédiat et permanent.

## Windows : plusieurs clients

1. Installez le client Steam Perpetuum.
2. Vérifiez que le dossier du jeu contient un `steam_appid.txt` dont le contenu est
   `223410`.
3. Copiez le dossier `Perpetuum` entier une fois par client supplémentaire.
4. Lancez `Perpetuum.exe` dans chaque copie (facultatif : ajoutez les copies à Steam
   en tant que jeux non-Steam).

**Espace disque :** `Layers.gbf` et `Perpetuum.gbf` sont volumineux et identiques dans
chaque copie — faites-en des liens symboliques (`mklink`) ou des raccourcis pour
qu'ils soient stockés une seule fois.

## Linux : plusieurs clients

Chaque copie de client a besoin d'une **version Proton différente**, sinon elle refuse
de se lancer :

1. Installez Steam et Perpetuum normalement ; vérifiez `steam_appid.txt` (`223410`).
2. Copiez le dossier `Perpetuum` par client.
3. Connecté à Steam, installez plusieurs versions Proton récentes (via Steam,
   manuellement, ou builds GloriousEggroll).
4. Ajoutez chaque copie à Steam en tant que jeu non-Steam pointant vers son `Perpetuum.exe`.
5. Forcez une **version Proton différente** par copie dans ses options de lancement.
6. Lancez d'abord la vraie application Steam, puis lancez les copies.

Dépannage :

- Sélectionner une version Proton ne l'**installe** pas — vous devez lancer le
  jeu une fois avec cette version pour la télécharger.
- Si un client refuse de se lancer, vérifiez que les options de lancement
  pointent bien vers une version Proton différente des autres.

## Échelle de l'interface

Le client supporte le redimensionnement de l'interface :

- **Paramètres > Affichage > Échelle de l'interface** — ajustez le facteur
  d'échelle pour adapter l'UI à votre écran.
- Sur les grands écrans (4K+), une échelle de 150-200 % est souvent confortable.
- Le redimensionnement est instantané et ne nécessite pas de redémarrage.

## Lancement sans droits admin

Le client ne nécessite pas de droits administrateur. Sur Windows, il s'exécute
en tant qu'application utilisateur normale. Sur Linux/Proton, les permissions
standard suffisent.
