---
title: "Formaty"
description: "Referencja dla programistów: jak każde pole statystyk jest przechowywane, analizowane i wykorzystywane przez serwer."
weight: 60
---

# Formaty

Referencja pól skierowana do programistów. Każda strona śledzi pole statystyk od jego przechowywania (kolumna bazy danych, klucz pliku reguł lub bajt warstwy binarnej) przez kod, który je wykorzystuje, wraz z przykładowymi obliczeniami numerycznymi. Podsumowania skierowane do graczy („co to oznacza w grze") znajdują się w sekcjach [funkcje](/pl/features/) i [kontent](/content/) — tutaj znajdują się dokładne typy, wartości domyślne, wzory i ścieżki kodu.

| Strona | Zawartość |
|---|---|
| [Pola roślin](/pl/formats/plant-fields/) | Format pliku reguł roślin (GenXY), każde pole reguły z typem/wartością domyślną/konsumentem, automat stanów wzrostu, sprawdziany walidacyjne |
| [Pola rud](/pl/formats/ore-fields/) | Kolumny `minerals` + `mineralconfigs`, wzory generowania węzłów, cykl życia i trwałość węzłów, mechanika wydobywania |
| [Pola obiektów rozmieszczanych](/pl/formats/deployable-fields/) | Jak identyfikowane są obiekty rozmieszczane, parowanie kapsuła↔obiekt oraz pola agregowane sterujące umieszczonymi obiektami |
| [Pliki stref](/pl/formats/zone-files/) | Pliki binarnych warstw terenu: układy struktur, bity flag, cykl zapisu i co zamiast tego znajduje się w bazie danych |

Konwencje:

- **GenXY** to serializacja ustawień używana dla plików reguł i `entitydefaults.options` (znaki tokenów zgodnie z `GenxyToken.cs`; patrz [Pola roślin → format pliku](/pl/formats/plant-fields/)).
- Ścieżki kodu są względem `src/`.
- Gdy wartość jest **stałą** (nie danymi), podawane są nazwa pliku i nazwa stałej.