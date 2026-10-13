---
title: "Client- & PC-Einrichtung"
description: "Den Client unter Windows und Linux ausführen, Multiboxing im Rahmen der Regeln, UI-Skalierung und Starten ohne Administratorrechte."
weight: 24
---

# Client- & PC-Einrichtung

Praktische Hinweise zum Ausführen des Perpetuum-Clients.

## Die Regeln zuerst

Multiboxing (mehrere Clients, die mehrere Charaktere steuern) ist **in gewissen Grenzen**
erlaubt. Fair-Play-Regeln, die man vorab kennen muss:

- **Keine Automatisierung oder Multi-Client-Steuerungssoftware** — niemals.
- **Nicht mehr als 5 gleichzeitig aktive Accounts.**
- Keine Accounts, die mit gefälschten, ungültigen oder unerreichbaren E-Mail-Adressen registriert wurden —
  die Adresse muss dir gehören.

Verstöße können einen sofortigen, permanenten Bann zur Folge haben.

## Windows: Mehrere Clients

1. Installiere den Perpetuum-Steam-Client.
2. Prüfe, ob der Spielordner eine `steam_appid.txt` enthält, deren Inhalt
   `223410` lautet.
3. Kopiere den gesamten Ordner `Perpetuum` einmal für jeden zusätzlichen Client.
4. Führe die `Perpetuum.exe` in jeder Kopie aus (optional können die Kopien als
   Steam-fremde Spiele zu Steam hinzugefügt werden).

**Speicherplatz:** `Layers.gbf` und `Perpetuum.gbf` sind groß und in jeder
Kopie identisch — erstelle symbolische Links (`mklink`) oder Verknüpfungen, damit sie
nur einmal gespeichert werden.

## Linux: Mehrere Clients

Jede Client-Kopie benötigt eine **andere Proton-Version**, andernfalls verweigert sie den Start:

1. Installiere Steam und Perpetuum wie gewohnt; überprüfe `steam_appid.txt` (`223410`).
2. Kopiere den Ordner `Perpetuum` pro Client.
3. Während du bei Steam angemeldet bist, installiere mehrere aktuelle Proton-Versionen (über Steam,
   manuell oder GloriousEggroll-Builds).
4. Füge jede Kopie als Steam-fremdes Spiel zu Steam hinzu und verweise auf die jeweilige `Perpetuum.exe`.
5. Erzwinge in den Startoptionen jeder Kopie eine **andere Proton-Version**.
6. Starte zuerst die eigentliche Steam-Anwendung und starte danach die Kopien.

Fehlerbehebung:

- Das Auswählen einer Proton-Version installiert sie **nicht** — du musst das
  Spiel einmal mit dieser Auswahl starten.
- Falls die eigentliche Steam-App nicht startet, starte sie zuerst im abgesicherten Modus (Safe Mode).
- Seit Proton 5.0 läuft die DirectX 9/12-Emulation über **Vulkan**. Keine
  Vulkan-fähige GPU vorhanden? Füge `PROTON_USE_WINED3D=1 %command%` zu den Startoptionen
  jeder Kopie hinzu.
- Leeres Textfeld mit roter Warnung: Installiere `libfreetype6:i386`
  (Debian-/Ubuntu-basierte Distributionen).

## UI-Skalierung

Der Client verwendet eine Pixel-feste Benutzeroberfläche ohne dynamische Skalierung. Ausweichmöglichkeiten:

- **Vollbild mit niedrigerer Auflösung** — wechsle in den Vollbildmodus mit einer geringeren Auflösung als dein
  Bildschirm und lasse die Benutzeroberfläche strecken (Fenster- und rahmenlose Modi
  verwenden immer die native Auflösung). Das Herabsetzen der Bildschirmauflösung im Betriebssystem
  bewirkt dasselbe.
- **UI-Scaler-Programme** — z. B. Lossless Scaling (Steam, Windows): Führe den Client im
  Fenstermodus in der Basisgröße aus, lege einen benutzerdefinierten Skalierungsfaktor im Scaler fest,
  aktiviere die Skalierung und fokussiere das Client-Fenster. Beachte den üblichen Kompromiss
  zwischen Bildglättung und Textschärfe.
- **Bildschirmlupe des Betriebssystems** — die Windows-Bildschirmlupe (oder ein Äquivalent) für das gelegentliche
  genaue Ablesen.

## Starten ohne Administratorrechte

1. Kopiere die Client-Dateien aus dem Steam-Ordner an einen beschreibbaren Speicherort.
2. Erstelle dort eine `Perpetuum.bat` mit dem Inhalt:
   `cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"`.
3. Starte das Spiel über die Batch-Datei.

<!--
Developer notes: rewritten 2026 in original prose. An earlier version was adapted from the
Open Perpetuum community wiki (perpetuum.miraheze.org: Multi-Boxing, Linux
Setup, Client UI Scaling, Launching without Admin Rights); that text was
fully replaced, not reused. These are client-side procedures for the retail Steam client build;
nothing here is verifiable from this server's backend, and no server feature is
claimed. The Reshader (graphics mod) was intentionally left out: it targets the
retail client build and is not an OPP-server feature.
-->
