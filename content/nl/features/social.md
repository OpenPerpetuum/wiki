---
title: "Sociaal"
description: "Communicatie en reputatie: e-mail, chatkanalen, vrienden, standings, de gouden gids, nieuws en peilingen."
weight: 140
---

# Sociaal

Deze pagina behandelt communicatie en reputatie: **e-mail**, **chatkanalen**, **vrienden**,
**standings** en de openbare **gouden gids / nieuws / peilingen**.

> De UI-locaties volgen het [client UI-overzicht](/nl/features/ui/) (de **Mail**-knop linksboven; chat en
> social hebben hun eigen vensters). De onderstaande mechanismen zijn bevestigd tegen de server.

## E-mail

**Persoonlijke e-mail:**
- E-mail **lijsten**, een bericht **openen**, e-mail **versturen**, een bericht **verwijderen**.
- **Nieuw aantal** — het aantal ongelezen berichten dat je hebt.
- **Mappen** — **gebruikte mappen** bekijken, een bericht **verplaatsen** naar een map, een map **verwijderen**.

**Massamail (corporatie):** verzonden naar je hele corporatie:
- **Versturen**, **lijsten**, **openen**, **verwijderen**, **nieuw aantal**.

## Chatkanalen

**Kanalen** zijn benoemde chatkamers:

- **Maak** een kanaal, **sluit** je erbij aan, **verlaat** het, **praat** erin.
- Kanalen **lijsten** (allemaal, of alleen de jouwe).
- **Moderatie** (als kanaaleigenaar/officier): **uitschakelen**, **bannen** / **opheffen**, **de
  rol van een lid instellen**, **globaal dempen**, **gedempte** / **verbannen** leden bekijken.
- **Instellingen**: **een wachtwoord instellen**, **een onderwerp instellen**, **meldingsvoorkeuren**.

**Directe chat** — een privébericht tussen personages.

## Vrienden

- **Een vriendverzoek versturen**, **erop reageren**, **een openstaand verzoek bevestigen**.
- **Een vriend verwijderen**, **een personage blokkeren**.
- Je vrienden **lijsten**.

Als je een personage blokkeert, kan het niet meer met je handelen of berichten (zie
[getting started](/nl/features/getting-started/) voor de per-personage handelsblokkade).

## Standings (reputatie)

**Standing** is een numerieke reputatie tussen entiteiten (personages, corporaties,
allianties):

- Je standings **lijsten**, **standinggeschiedenis** bekijken.
- **Standing instellen** — waar toegestaan, een standingwaarde instellen. Beperkingen:
  - het **doel** moet een personage, een (privé) corporatie of een (privé) alliantie zijn,
  - de **bron** moet eveneens een geldige entiteit zijn,
  - je kunt geen standing op jezelf instellen.
- **Standaard standings** — de basis standings voor standaard allianties/corporaties.

Standing is een waarde van **-10 tot +10** (0 = neutraal, de standaard; 0 instellen wist de
vermelding). **Reputatie** voor een entiteit is het aggregaat van de standing van iedereen richting die entiteit.
Positieve standing is op concrete plekken van belang — bijvoorbeeld tijdens [intrusie](/nl/features/intrusion/)
telt een corporatie met wederzijdse standing ≥ 10 als **bondgenoot** wiens SAP-overwinning je site niet
beschadigt.

Standing beïnvloedt hoe facties en andere spelers je en je corporatie behandelen
(zie [groepen](/nl/features/groups/)).

## Gouden gids

Een openbare gids (door corporaties beheerde advertenties):
- **Ophalen** van een advertentie, **indienen** van een advertentie, **verwijderen** van een advertentie, **doorzoeken** van de gids.

## Nieuws & peilingen

- **Nieuws** — **categorieën** en de **nieuwslijst** bekijken; **nieuw aantal** voor ongelezen items.
- **Peilingen** — een peiling **bekijken** en **beantwoorden**.

## Praktische notities

- **E-mail vs. chat** — e-mail is permanent en privé; kanalen zijn live groepsruimtes.
- **Massamail is een corporatietool** — officiers gebruiken het om berichten naar leden te uitzenden.
- **Standings zijn richtingsgebonden** — de standing van A t.o.v. B is apart van die van B t.o.v. A, en
  het volgt je corporatie.
- **Blokkeren is je schild** — blokkeer spamders of vijandige handelaren.
- **Kanalen kunnen worden vergrendeld** — wachtwoorden en rollen bepalen wie kan toetreden/praten.

<!-- TODO: alleen de mail/kanaal/social UI blijft over.
     Bevestigd: standingbereik [-10,10], clamp in StandingHandler.SetStanding, 0 =
     neutraal/wist de rij (standings-tabel leeg in deze uitrol); reputatie =
     aggregaat richting een doel (GetReputationFor); missiestandingveranderingen worden geclamped naar
     [0,10] (missionstandingchange/missionrequiredstanding); bondgenootscheck = wederzijdse
     standing >= 10 (intrusion).
     Ontwikkelaarsnotities: Mails/* (lijst/openen/versturen/verwijderen/mappen, massamailvarianten);
     Channels/* (maken/toetreden/verlaten/praten, moderatie, wachtwoord/onderwerp); Socials/* (vriendverzoek/beantwoorden/bevestigen/verwijderen/blokkeren/lijst); Chat.cs; Standings/SetStanding.cs
     (entiteitscategorie + private-corp/alliance-beperkingen, zichzelf uitgesloten),
     StandingHistory.cs, GetStandingForDefault*.cs; Corporations/YellowPages/*;
     GetNews.cs / NewsCategory.cs / FreshNewsCount.cs; PollGet.cs / PollAnswer.cs. -->