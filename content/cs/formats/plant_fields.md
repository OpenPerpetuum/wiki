---
title: "Pole rostlin"
description: "Formát souboru pravidel rostlin (GenXY), každé pole pravidla s typem, výchozí hodnotou a spotřebitelem, plus stroj stavů růstu."
weight: 380
---

# Pole rostlin

Chování rostlin je definováno pro každý druh **souborem pravidel**
(obyčejný text) pod `$GameRoot/plantrules/`.

## Formát souboru

Jeden `key=value` na řádek; komentáře ve stylu `//` se odstraní. Hodnoty
používají **znaky tokenů GenXY** (`GenxyReader.cs`):

| Token | Analyzováno jako | Příklad |
|---|---|---|
| `#`</parameter>
</invoke>
