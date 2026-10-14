---
title: "Formáty"
description: "Referenční dokumentace pro vývojáře: jak je každé statistické pole ukládáno, parsováno a používáno serverem."
weight: 60
---

# Formáty

Referenční dokumentace polí pro vývojáře. Každá stránka sleduje statistické pole od jeho úložiště (sloupec DB, klíč souboru pravidel nebo bajt binární vrstvy) přes kód, který ho zpracovává, včetně vypracovaných číselných příkladů. Souhrny zaměřené na hráče („co to znamená ve hře") najdete v sekcích [funkce](/cs/features/) a [obsah](/content/) — zde jsou přesné typy, výchozí hodnoty, vzorce a kódové cesty.

| Stránka | Obsah |
|---|---|
| [Pole rostlin](/cs/formats/plant-fields/) | Formát souboru pravidel rostlin (GenXY), každé pole pravidel s typem/výchozí hodnotou/zpracovatelem, stavový automat růstu, validační kontroly |
| [Pole rud](/cs/formats/ore-fields/) | Sloupce `minerals` + `mineralconfigs`, vzorce generování uzlů, životní cyklus a perzistence uzlů, mechanika extrakce |
| [Pole nasaditelných objektů](/cs/formats/deployable-fields/) | Jak jsou nasaditelné objekty identifikovány, spárování kapsle↔objekt a agregační pole, která řídí umístěné objekty |
| [Soubory zón](/cs/formats/zone-files/) | Binární soubory terénních vrstev: rozložení struktur, bitové příznaky, cyklus ukládání a co je místo toho v DB |

Konvence:

- **GenXY** je serializace nastavení používaná pro soubory pravidel a `entitydefaults.options` (znakové tokeny dle `GenxyToken.cs`; viz [Pole rostlin → formát souboru](/cs/formats/plant-fields/)).
- Kódové cesty jsou relativní vůči `src/`.
- Kde je hodnota **konstantou** (ne datem), je uvedeno soubor a název konstanty.