---
title: "Formate"
description: "Entwicklerreferenz: Wie jedes Statistikfeld gespeichert, geparst und vom Server verwendet wird."
weight: 60
---

# Formate

Feldreferenz für Entwickler. Jede Seite verfolgt ein Statistikfeld von seiner
Speicherung (DB-Spalte, Regeldatei-Schlüssel oder Binary-Layer-Byte) durch den Code,
der es verbraucht, mit ausgerechneten Zahlenbeispielen. Spielerorientierte
„Was bedeutet das im Spiel"-Zusammenfassungen stehen in den Sektionen
[features](/de/features/) und [content](/content/) — hier stehen die exakten Typen,
Standardwerte, Formeln und Code-Pfade.

| Seite | Inhalt |
|---|---|
| [Pflanzenfelder](/de/formats/plant-fields/) | Pflanzen-Regeldateiformat (GenXY), jedes Regelfeld mit Typ/Standard/Verbraucher, die Wachstums-Zustandsmaschine, Validierungsprüfungen |
| [Ervfelder](/de/formats/ore-fields/) | Spalten von `minerals` + `mineralconfigs`, die Node-Generierungsformeln, Node-Lebenszyklus und -persistenz, Extraktionsmechanik |
| [Deployable-Felder](/de/formats/deployable-fields/) | Wie Deployables identifiziert werden, Kapsel↔Objekt-Paarung und die Aggregatfelder, die platzierte Objekte steuern |
| [Zonendateien](/de/formats/zone-files/) | Die binären Geländelayer-Dateien: Struct-Layouts, Flag-Bits, Speichzyklus und was stattdessen in der DB liegt |

Konventionen:

- **GenXY** ist die Einstellungen-Serialisierung für Regeldateien und
  `entitydefaults.options` (Tokenzeichen nach `GenxyToken.cs`; siehe [Pflanzenfelder →
  Dateiformat](/de/formats/plant-fields/)).
- Code-Pfade sind relativ zu `src/`.
- Wo ein Wert eine **Konstante** (keine Daten) ist, werden Datei und
  Konstantenname genannt.
