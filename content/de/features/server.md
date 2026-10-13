---
title: "Server & Referenz"
description: "Server-Informationen, Highscores, Referenzdaten-Downloads und der Ingame-Shop."
weight: 170
---

# Server & Referenz

Diese Seite behandelt die „Meta“-Systeme: Server- und Systeminformationen, Highscores, die vom Client heruntergeladenen Referenzdaten und den Ingame-Shop.

> UI-Positionen orientieren sich an der [Client-UI-Übersicht](/de/features/ui/). Die nachfolgenden Mechaniken wurden anhand des Servers verifiziert.

## Server- & Systeminformationen

- **Server-Info (Server info)** — allgemeiner Serverzustand und Basisdaten.
- **System-Info (System info)** — Details auf Systemebene.
- **Server-Abschaltstatus (Server shutdown state)** — ob ein geplanter Server-Neustart bzw. eine Abschaltung aktiv ist (für Spieler schreibgeschützt; das Herunterfahren ist eine Administrator-Aktion).

## Highscores

- **Server-Highscores (Server high scores)** — die besten Ergebnisse auf dem gesamten Server.
- **Meine Highscores (My high scores)** — persönliche Bestleistungen.

Siehe auch den Abschnitt [Kampf](/de/features/combat/) darüber, wie Abschüsse in diese Statistiken einfließen.

## Referenzdaten

Der Client lädt statische Referenzdaten vom Server herunter, um Spielinhalte korrekt darzustellen. Dies sind **reine Leseabfragen** und keine Spieleraktionen:

- **Effekte (Effects)** — Definitionen von Statuseffekten.
- **Enums** — Aufzählungswerte.
- **Entitäts-Standardwerte (Entity defaults)** — Basisdefinitionen für Spielelemente.
- **Aggregatfelder (Aggregate fields)** — zusammengefasste Felddaten.
- **Definitions-Konfigurationseinheiten (Definition config units)** — Konfiguration pro Definition.
- **Distanzen (Distances)** — Entfernungs-Konstanten des Clients.
- **Befehle (Commands)** — Liste bekannter Befehle (clientseitige Referenz).
- **Risse (Rifts)** — Riss-Definitionen (siehe auch Zonen-Rissliste).

Diese Daten werden nicht aktiv „benutzt“; der Client ruft sie bei Bedarf automatisch ab. Sie sind hier aufgeführt, da sie im Befehlsinventar des Servers vorkommen.

## Der Shop

Der Ingame-Shop (eine Zahlungsintegration):

- **Produkte auflisten (List products)** — einsehen, welche Artikel zum Kauf stehen.
- **Transaktion starten (Start a transaction)** — einen Kaufvorgang einleiten.
- **Transaktion abschließen (Finish a transaction)** — den Kaufvorgang abschließen.

Shop-Käufe sind Echtgeld-Transaktionen (oder vergleichbare Transaktionen); Produkte und Preise werden serverseitig festgelegt.

## Praktische Hinweise

- **Referenzdaten werden automatisch geladen** — ein manuelles Eingreifen ist nicht nötig; dies hält den Client mit den Daten des Servers synchron.
- **Highscores zeigen deine Erfolge** — vergleiche deine persönlichen Bestleistungen mit den Rekorden des Servers.
- **Shop-Transaktionen erfolgen in zwei Schritten** — zuerst starten, dann abschließen; ein Kauf ist erst nach dem Abschluss gültig.
- **Abschaltstatus dient zur Information** — zeigt an, ob Wartungsarbeiten oder Server-Neustarts anstehen.
