---
title: "Serwer i dane referencyjne"
description: "Informacje o serwerze, najlepsze wyniki, pobieranie danych referencyjnych oraz sklep w grze."
weight: 170
---

# Serwer i dane referencyjne

Ta strona obejmuje systemy „meta": informacje o serwerze i systemie, najlepsze wyniki, dane referencyjne pobierane przez klienta oraz sklep w grze.

> Lokalizacje w interfejsie użytkownika są opisane w [przeglądzie interfejsu klienta](/pl/features/ui/). Mechaniki poniżej zostały potwierdzone na serwerze.

## Informacje o serwerze i systemie

- **Informacje o serwerze** — ogólny stan i informacje o serwerze.
- **Informacje o systemie** — szczegóły na poziomie systemowym.
- **Stan wyłączenia serwera** — czy zaplanowane wyłączenie jest aktywne (tylko do odczytu dla graczy; samo wyłączenie jest działaniem administratora).

## Najlepsze wyniki

- **Najlepsze wyniki serwera** — najlepsze rezultaty na serwerze.
- **Moje najlepsze wyniki** — Twoje osobiste rekordy.

Zobacz również [walka](/pl/features/combat/), aby dowiedzieć się, jak eliminacje wpływają na te wyniki.

## Dane referencyjne

Klient pobiera statyczne dane referencyjne z serwera, aby poprawnie renderować treści. Są to **zapytania tylko do odczytu**, a nie akcje gracza:

- **Efekty** — definicje efektów.
- **Wyliczenia** — wartości wyliczeń (enum).
- **Wartości domyślne encji** — podstawowe definicje encji.
- **Pola agregowane** — zagregowane dane pól.
- **Jednostki konfiguracji definicji** — konfiguracja dla każdej definicji.
- **Odległości** — stałe odległości używane przez klienta.
- **Polecenia** — lista znanych poleceń (dane referencyjne po stronie klienta).
- **Rozłamy** — definicje rozłamów (zobacz również listę rozłamów stref).

Nie „używasz" ich bezpośrednio; klient pobiera je na żądanie. Są tu wymienione, ponieważ pojawiają się w inwentarzu poleceń.

## Sklep

Sklep w grze (integracja płatności):

- **Lista produktów** — zobacz, co jest w sprzedaży.
- **Rozpoczęcie transakcji** — rozpoczęcie zakupu.
- **Zakończenie transakcji** — ukończenie zakupu.

Zakupy w sklepie to transakcje za prawdziwe pieniądze (lub ich odpowiednik); dokładne produkty i ceny to treść sklepu.

## Uwagi praktyczne

- **Dane referencyjne są pobierane automatycznie** — nigdy nie inicjujesz tego ręcznie; utrzymują one klienta w synchronizacji z treścią serwera.
- **Najlepsze wyniki to Twoje powody do chwalenia się** — sprawdź swoje osobiste rekordy i wyniki serwera.
- **Transakcje w sklepie są dwuetapowe** — najpierw rozpocznij, potem zakończ; nie zakładaj, że zakup jest ukończony, dopóki nie zostanie zakończony.
- **Stan wyłączenia ma charakter informacyjny** — informuje, czy nadchodzi okno konserwacji.

<!-- TODO: pozostaje tylko lista danych referencyjnych (po stronie klienta).
     Potwierdzone: sklep za prawdziwe pieniądze NIE jest aktywny w tym wdrożeniu — polecenia transakcji Steam (steamGetProducts / steamStartTransaction /
     steamFinishTransaction) są zadeklarowane w Commands.cs, ale nie zarejestrowano żadnego handlera
     w bootstrapie, a tabele treści sklepu (storeitems, storecategories)
     są puste.
     Notatki developerskie: ServerInfoGet.cs / SystemInfo.cs / ServerShutDownState.cs;
     GetHighScores.cs / GetMyHighScores.cs; GetEffects.cs / GetEnums.cs /
     GetEntityDefaults.cs / GetAggregateFields.cs / GetDefinitionConfigUnits.cs /
     GetDistances.cs / GetCommands.cs / GetRifts.cs; SteamGetProducts.cs /
     SteamStartTransaction.cs / SteamFinishTransaction.cs. -->