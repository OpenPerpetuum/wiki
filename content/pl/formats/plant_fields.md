---
title: "Pola roślin"
description: "Format pliku reguł roślin (GenXY), każde pole reguły z typem, wartością domyślną i konsumentem, plus maszyna stanów wzrostu."
weight: 380
---

# Pola roślin

Zachowanie roślin jest definiowane dla każdego gatunku **plikiem reguł**
(zwykły tekst) pod `$GameRoot/plantrules/`.

## Format pliku

Jedna `key=value` na linię; komentarze w stylu `//` są usuwane. Wartości
używają **znaków tokenów GenXY** (`GenxyReader.cs`):

| Token | Analizowane jako | Przykład |
|---|---|---|
| `#` | Liczba całkowita dziesiętna | `#100` = 100 |
| `.` | Liczba zmiennoprzecinkowa | `.5` = 0.5 |
| `s</parameter>
</invoke>
