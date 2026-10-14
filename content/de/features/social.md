---
title: "Soziales"
description: "Kommunikation und Ansehen: Mail, Chat-Kanäle, Freunde, Ansehen (Standings), die Gelben Seiten, Neuigkeiten und Umfragen."
weight: 140
---

# Soziales

Diese Seite behandelt Kommunikation und Reputation: **Mail**, **Chat-Kanäle**, **Freunde**,
**Ansehen (Standings)** sowie die öffentlichen **Gelben Seiten / Neuigkeiten / Umfragen**.

> UI-Positionen richten sich nach der [Client-UI-Übersicht](/de/features/ui/) (die Schaltfläche **Mail** oben links;
> Chat und Soziales besitzen eigene Fenster). Die folgenden Mechaniken sind anhand des Servers bestätigt.

## Mail

**Persönliche Mail:**
- Mails **auflisten**, eine Nachricht **öffnen**, Mail **senden**, eine Nachricht **löschen**.
- **Ungelesen-Zähler** — wie viele ungelesene Nachrichten du hast.
- **Ordner** — **genutzte Ordner** anzeigen, eine Nachricht in einen Ordner **verschieben**, einen Ordner **löschen**.

**Massen-Mail (Konzern):** An deinen gesamten Konzern gesendet:
- **Senden**, **auflisten**, **öffnen**, **löschen**, **Ungelesen-Zähler**.

## Chat-Kanäle

**Kanäle** sind benannte Chaträume:

- Einen Kanal **erstellen**, einem Kanal **beitreten**, ihn **verlassen**, darin **schreiben**.
- Kanäle **auflisten** (alle oder nur deine eigenen).
- **Moderation** (als Kanalbesitzer/-offizier): **Rauswerfen (Kick)**, **Bannen** / **Entbannen**,
  die **Rolle eines Mitglieds festlegen**, **global stummschalten**, **stummgeschaltete** / **gebannte** Mitglieder anzeigen.
- **Einstellungen**: Ein **Passwort festlegen**, ein **Thema festlegen**, **Benachrichtigungseinstellungen**.

**Direktnachrichten (Flüstern)** — eine private Unterhaltung zwischen zwei Charakteren.

## Freunde

- Eine **Freundschaftsanfrage senden**, auf eine **antworten**, eine ausstehende Anfrage **bestätigen**.
- Einen Freund **löschen**, einen Charakter **blockieren**.
- Deine Freunde **auflisten**.

Das Blockieren eines Charakters verhindert, dass er mit dir handelt oder dir Nachrichten sendet (siehe
[Erste Schritte](/de/features/getting-started/) für die Handelsblockade pro Charakter).

## Ansehen (Standings & Reputation)

**Ansehen (Standing)** ist ein numerischer Reputationswert zwischen Einheiten (Charakteren, Konzernen, Allianzen):

- Deine Standings **auflisten**, den **Standings-Verlauf** einsehen.
- **Standing festlegen** — wo zulässig, einen Ansehens-Wert definieren. Einschränkungen:
  - das **Ziel** muss ein Charakter, ein (privater) Konzern oder eine (private) Allianz sein,
  - die **Quelle** muss ebenfalls eine gültige Entität sein,
  - du kannst kein Standing dir selbst gegenüber festlegen.
- **Standard-Standings** — die Basis-Standings für Standard-Allianzen/Konzerne.

Standing ist ein Wert von **-10 bis +10** (0 = neutral, der Standardwert; das Setzen auf 0 löscht den Eintrag).
**Reputation** einer Entität ist das Aggregat der Standings aller anderen ihr gegenüber.
Positives Ansehen spielt an konkreten Stellen eine Rolle — z. B. zählt bei [Intrusion](/de/features/intrusion/)
ein Konzern mit beidseitigem Standing ≥ 10 als **Verbündeter**, dessen SAP-Sieg deinen Stützpunkt nicht beschädigt.

Standing beeinflusst, wie Fraktionen und andere Spieler dich und deinen Konzern behandeln
(siehe [Gruppen](/de/features/groups/)).

## Gelbe Seiten

Ein öffentliches Branchenverzeichnis (von Konzernen betriebene Einträge):
- Einen Eintrag **abrufen**, einen **eintragen**, einen **löschen**, das Verzeichnis **durchsuchen**.

## Neuigkeiten & Umfragen

- **Neuigkeiten** — **Kategorien** und die **News-Liste** ansehen; **Ungelesen-Zähler** für neue Meldungen.
- **Umfragen** — eine Umfrage **ansehen** und **beantworten**.

## Praktische Hinweise

- **Mail vs. Chat** — Mail ist persistent und privat; Kanäle sind synchrone Gruppenräume.
- **Massen-Mail ist ein Offizierswerkzeug** — Führungskräfte nutzen es für Rundschreiben an Mitglieder.
- **Standings sind gerichtet** — As Ansehen gegenüber B ist unabhängig von Bs Ansehen gegenüber A,
  und es folgt deinem Konzern.
- **Blockieren ist dein Schutzschild** — blockiere Spammer oder aufdringliche Händler.
- **Kanäle können geschützt werden** — Passwörter und Rollen steuern, wer beitreten und schreiben darf.

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