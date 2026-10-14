---
title: "Server & referentie"
description: "Serverinformatie, high scores, referentiedata-downloaden en de in-game winkel."
weight: 170
---

# Server & referentie

Deze pagina behandelt de "meta"-systemen: server/systeeminfo, high scores, de referentiedata die de client downloadt en de in-game winkel.

> De UI-locaties volgen het [client UI-overzicht](/nl/features/ui/). De mechanismen hieronder zijn bevestigd tegen de server.

## Server- en systeeminfo

- **Serverinfo** — algemene serverstatus/informatie.
- **Systeeminfo** — systeemgerelateerde details.
- **Serveruitschakelstatus** — of een geplande uitschakeling van kracht is (alleen-lezen voor spelers; de uitschakeling zelf is een beheeractie).

## High scores

- **Server high scores** — de beste resultaten over de hele server.
- **Mijn high scores** — je persoonlijke records.

Zie ook [gevecht](/nl/features/combat/) voor hoe kills bijdragen aan deze scores.

## Referentiedata

De client downloadt statische referentiedata van de server om content correct weer te geven. Dit zijn **alleen-lezen opslagen**, geen speleracties:

- **Effecten** — de effectdefinities.
- **Enums** — enumeratiewaarden.
- **Entiteitsstandaardwaarden** — basisdefinities voor entiteiten.
- **Geaggregeerde velden** — geaggregeerde veldgegevens.
- **Definitie-configuratie-eenheden** — configuratie per definitie.
- **Afstanden** — afstandsconstanten die door de client worden gebruikt.
- **Commando's** — de lijst met bekende commando's (een client-referentie).
- **Rifts** — riftdefinities (zie ook de zone-riftlijst).

Je "gebruikt" deze niet; de client haalt ze op bij aanvraag. Ze staan hier omdat ze in het commando-overzicht verschijnen.

## De winkel

De in-game winkel (een betalingsintegratie):

- **Producten weergeven** — bekijk wat er te koop is.
- **Transactie starten** — begin met een aankoop.
- **Transactie afronden** — voltooi een aankoop.

Winkel-aankopen zijn echte-geldtransacties (of equivalent); de exacte producten en prijzen zijn winkelcontent.

## Praktische opmerkingen

- **Referentiedata wordt automatisch opgehaald** — je triggert dit nooit handmatig; het houdt de client in sync met de servercontent.
- **High scores zijn je praalrechten** — check je persoonlijke records en die van de server.
- **Winkeltransacties zijn tweestaps** — starten, dan afronden; neem niet aan dat een aankoop is voltooid totdat deze is afgerond.
- **Uitschakelstatus is informatief** — het laat zien of er een onderhoudsvenster aankomt.

<!-- TODO: alleen de referentiedata-payloadlijst (client-side) resteert.
     Bevestigd: de echte-geldwinkel is NIET actief op deze deployment — de Steam
     transactiecommando's (steamGetProducts / steamStartTransaction /
     steamFinishTransaction) zijn gedeclareerd in Commands.cs maar er is geen handler
     geregistreerd in de bootstrapper, en de winkelcontent-tabellen (storeitems,
     storecategories) zijn leeg.
     Ontwikkelaarsnotities: ServerInfoGet.cs / SystemInfo.cs / ServerShutDownState.cs;
     GetHighScores.cs / GetMyHighScores.cs; GetEffects.cs / GetEnums.cs /
     GetEntityDefaults.cs / GetAggregateFields.cs / GetDefinitionConfigUnits.cs /
     GetDistances.cs / GetCommands.cs / GetRifts.cs; SteamGetProducts.cs /
     SteamStartTransaction.cs / SteamFinishTransaction.cs. -->