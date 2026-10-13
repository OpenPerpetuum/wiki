---
title: "Społeczność"
description: "Komunikacja i reputacja: poczta, kanały czatu, znajomi, renomy, żółte strony, wiadomości i sondaże."
weight: 140
---

# Społeczność

Ta strona obejmuje komunikację i reputację: **pocztę**, **kanały czatu**, **znajomych**,
**renomy** oraz publiczne **żółte strony / wiadomości / sondaże**.

> Lokalizacje w interfejsie są zgodne z [przeglądem interfejsu klienta](/pl/features/ui/) (przycisk **Poczta** w lewym górnym rogu; czat i
> społeczność mają własne okna). Mechaniki poniżej zostały potwierdzone na serwerze.

## Poczta

**Poczta osobista:**
- **Lista** poczty, **otwarcie** wiadomości, **wysłanie** wiadomości, **usunięcie** wiadomości.
- **Liczba nowych** — ile masz nieprzeczytanych wiadomości.
- **Foldery** — przeglądanie **używanych folderów**, **przeniesienie** wiadomości do folderu, **usunięcie** folderu.

**Poczta masowa (korporacja):** wysyłana do całej Twojej korporacji:
- **Wyślij**, **lista**, **otwórz**, **usuń**, **liczba nowych**.

## Kanały czatu

**Kanały** to nazwane pokoje czatu:

- **Utworzenie** kanału, **dołączenie** do niego, **opuścienie** go, **rozmowa** w nim.
- **Lista** kanałów (wszystkie lub tylko Twoje).
- **Moderacja** (jako właściciel/oficer kanału): **wykop**, **ban** / **odban**, **ustawienie
  roli członka**, **globalne wyciszenie**, przegląd **wyciszonych** / **zbanowanych** członków.
- **Ustawienia**: **ustawienie hasła**, **ustawienie tematu**, preferencje **powiadomień**.

**Czat bezpośredni** — prywatna wiadomość między postaciami.

## Znajomi

- **Wysłanie zaproszenia do znajomych**, **odpowiedź** na zaproszenie, **potwierdzenie** oczekującego zaproszenia.
- **Usunięcie** znajomego, **zablokowanie** postaci.
- **Lista** Twoich znajomych.

Zablokowanie postaci uniemożliwia jej handel i wysyłanie wiadomości do Ciebie (zobacz
[szybki start](/pl/features/getting-started/) w sprawie blokady handlowej dla konkretnej postaci).

## Renomy (reputacja)

**Renoma** to numeryczna reputacja między bytami (postaciami, korporacjami,
aliansami):

- **Lista** Twoich renom, przegląd **historii renomy**.
- **Ustawienie renomy** — tam, gdzie jest to dozwolone, ustaw wartość renomy. Ograniczenia:
  - **cel** musi być postacią, (prywatną) korporacją lub (prywatnym) aliansem,
  - **źródło** musi również być ważnym bytem,
  - nie możesz ustawić renomy wobec siebie samego.
- **Domyślne renomy** — bazowe renomy dla domyślnych aliansów/korporacji.

Renoma to wartość od **-10 do +10** (0 = neutralna, domyślna; ustawienie 0 czyści
wpis). **Reputacja** bytu to suma wszystkich renom wobec niego.
Pozytywna renoma ma znaczenie w konkretnych miejscach — np. podczas [inwazji](/pl/features/intrusion/)
korporacja z wzajemną renomą ≥ 10 jest traktowana jako **sojusznik**, którego zwycięstwo SAP nie
uszkadza Twojej bazy.

Renomy wpływają na to, jak frakcje i inni gracze traktują Ciebie i Twoją korporację
(zobacz [grupy](/pl/features/groups/)).

## Żółte strony

Publiczny katalog (wpisy prowadzone przez korporacje):
- **Pobranie** wpisu, **dodanie** wpisu, **usunięcie** wpisu, **wyszukiwanie** w katalogu.

## Wiadomości i sondaże

- **Wiadomości** — przeglądanie **kategorii** i **listy wiadomości**; **liczba nowych** dla nieprzeczytanych.
- **Sondaże** — **przeglądanie** sondażu i **odpowiedź** na niego.

## Praktyczne uwagi

- **Poczta vs. czat** — poczta jest trwała i prywatna; kanały to żywe pokoje grupowe.
- **Poczta masowa to narzędzie korporacyjne** — oficerowie używają jej do rozgłaszania informacji do członków.
- **Renomy są kierunkowe** — renoma A wobec B jest odrębna od renomy B wobec A, i
  podąża za Twoją korporacją.
- **Blokowanie to Twoja tarcza** — blokuj spammerów i wrogich handlowców.
- **Kanały mogą być zablokowane** — hasła i role decydują, kto może dołączyć/rozmawiać.

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