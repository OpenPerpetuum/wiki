---
title: "Sociální"
description: "Komunikace a renomé: pošta, chatovací kanály, přátelé, postavení, žluté stránky, zprávy a ankety."
weight: 140
---

# Sociální

Tato stránka pokrývá komunikaci a renomé: **poštu**, **chatovací kanály**, **přátele**,
**postavení** a veřejné **žluté stránky / zprávy / ankety**.

> Umístění v uživatelském rozhraní následuje podle [přehledu uživatelského rozhraní klienta](/cs/features/ui/) (tlačítko **Pošta** v levém horním rohu; chat a
> sociální funkce mají vlastní okna). Mechaniky níže jsou potvrzeny na serveru.

## Pošta

**Osobní pošta:**
- **Seznam** pošty, **otevření** zprávy, **odeslání** pošty, **smazání** zprávy.
- **Počet nových** — kolik n přečtených zpráv máte.
- **Složky** — zobrazení **použitých složek**, **přesun** zprávy do složky, **smazání** složky.

**Hromadná pošta (korporace):** odeslána celé vaší korporaci:
- **Odeslat**, **seznam**, **otevřít**, **smazat**, **počet nových**.

## Chatovací kanály

**Kanály** jsou pojmenované chatovací místnosti:

- **Vytvoření** kanálu, **připojení** k němu, **opuštění**, **komunikace** v něm.
- **Seznam** kanálů (všechny, nebo jen vaše).
- **Moderace** (jako vlastník/důstojník kanálu): **vykopnutí**, **zakázání** / **odzakázání**, **nastavení
  role člena**, **globální ztlumení**, zobrazení **ztlumených** / **zakázaných** členů.
- **Nastavení**: **nastavení hesla**, **nastavení tématu**, **notifikační** preference.

**Přímý chat** — soukromá zpráva mezi postavami.

## Přátelé

- **Odeslání žádosti o přátelství**, **odpověď** na ni, **potvrzení** čekající žádosti.
- **Smazání** přítele, **zablokování** postavy.
- **Seznam** vašich přátel.

Zablokování postavy jí znemožní obchodovat s vámi nebo vám posílat zprávy (viz
[základní návod](/cs/features/getting-started/) pro zablokování obchodu pro konkrétní postavu).

## Postavení (renomé)

**Postavení** je číselná hodnota renomé mezi entitami (postavy, korporace,
aliance):

- **Seznam** vašich postavení, zobrazení **historie postavení**.
- **Nastavení postavení** — tam, kde je povoleno, nastavte hodnotu postavení. Omezení:
  - **cílem** musí být postava, (soukromá) korporace nebo (soukromá) aliance,
  - **zdrojem** musí být rovněž platná entita,
  - nemůžete nastavit postavení sobě samému.
- **Výchozí postavení** — základní postavení pro výchozí aliance/korporace.

Postavení je hodnota od **-10 do +10** (0 = neutrální, výchozí; nastavení 0 smaže
záznam). **Renomé** entity je součtem postavení všech vůči ní.
Kladné postavení má konkrétní význam — např. během [intruze](/cs/features/intrusion/)
korporace s vzájemným postavením ≥ 10 se počítá jako **ally**, jejíž výhra SAP
nezpůsobí poškození vašeho webu.

Postavení ovlivňuje, jak frakce a ostatní hráči zacházejí s vámi a vaší korporací
(viz [skupiny](/cs/features/groups/)).

## Žluté stránky

Veřejný adresář (seznamy provozované korporacemi):
- **Získání** inzerátu, **odeslání** inzerátu, **smazání** inzerátu, **vyhledávání** v adresáři.

## Zprávy a ankety

- **Zprávy** — zobrazení **kategorií** a **seznamu zpráv**; **počet nových** pro nepřečtené položky.
- **Ankety** — **zobrazení** ankety a **odpověď** na ni.

## Praktické poznámky

- **Pošta vs. chat** — pošta je trvalá a soukromá; kanály jsou živé skupinové místnosti.
- **Hromadná pošta je nástroj korporace** — důstojníci ji používají k vysílání zpráv členům.
- **Postavení jsou směrová** — postavení A vůči B je oddělené od postavení B vůči A, a
  následuje vaši korporaci.
- **Blokování je vaše ochrana** — blokujte spammaře nebo nepřátelské obchodníky.
- **Kanály lze uzamknout** — hesla a role určují, kdo se může připojit/komunikovat.

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