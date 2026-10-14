---
title: "Server a reference"
description: "Informace o serveru, nejlepší skóre, stažení referenčních dat a herní obchod."
weight: 170
---

# Server a reference

Tato stránka pokrývá „meta" systémy: informace o serveru/systému, nejlepší skóre, referenční data,
která klient stahuje, a herní obchod.

> Umístění v UI odpovídá [přehledu uživatelského rozhraní klienta](/cs/features/ui/). Mechanismy níže
> jsou potvrzeny na serveru.

## Informace o serveru a systému

- **Informace o serveru** — obecný stav/informace o serveru.
- **Informace o systému** — systémové podrobnosti.
- **Stav vypnutí serveru** — zda je v platnosti naplánované vypnutí (pro hráče pouze ke čtení;
  samotné vypnutí je administrátorská akce).

## Nejlepší skóre

- **Nejlepší skóre na serveru** — nejlepší výsledky na celém serveru.
- **Moje nejlepší skóre** — vaše osobní rekordy.

Viz také [boj](/cs/features/combat/) pro to, jak se zabití promítají do těchto žebříčků.

## Referenční data

Klient stahuje ze serveru statická referenční data, aby správně vykresloval obsah.
Jedná se o **vyhledávání pouze ke čtení**, nikoli o hráčské akce:

- **Efekty** — definice efektů.
- **Enumy** — hodnoty výčtových typů.
- **Výchozí hodnoty entit** — základní definice entit.
- **Agregovaná pole** — agregovaná data polí.
- **Konfigurační jednotky definic** — konfigurace pro jednotlivé definice.
- **Vzdálenosti** — konstanty vzdáleností používané klientem.
- **Příkazy** — seznam známých příkazů (klientská reference).
- **Roztržení** — definice roztržení (viz také seznam roztržení zón).

Tyto data se ne„používají" aktivně; klient je načítá na vyžádání. Jsou zde uvedena, protože
se objevují v inventáři příkazů.

## Obchod

Herní obchod (integrace plateb):

- **Vypsat produkty** — zobrazit, co je k prodeji.
- **Spustit transakci** — zahájit nákup.
- **Dokončit transakci** — dokončit nákup.

Nákupy v obchodě jsou transakce za skutečné peníze (nebo ekvivalent); konkrétní produkty a
ceny jsou obsahem obchodu.

## Praktické poznámky

- **Referenční data se načítají automaticky** — nikdy je neprovádíte ručně; udržují klienta
  v souladu s obsahem serveru.
- **Nejlepší skóre jsou vaše pochlubování** — zkontrolujte své osobní rekordy i ty na serveru.
- **Obchodní transakce jsou dvoustupňové** — nejprve spustit, pak dokončit; nepředpokládejte,
  že je nákup hotový, dokud není dokončen.
- **Stav vypnutí je informační** — říká vám, zda se blíží údržbové okno.

<!-- TODO: only the reference-data payload list (client-side) remains.
     Confirmed: the real-money store is NOT active on this deployment — the Steam
     transaction commands (steamGetProducts / steamStartTransaction /
     steamFinishTransaction) are declared in Commands.cs but no handler is registered
     in the bootstrapper, and the store content tables (storeitems, storecategories)
     are empty.
     Developer notes: ServerInfoGet.cs / SystemInfo.cs / ServerShutDownState.cs;
     GetHighScores.cs / GetMyHighScores.cs; GetEffects.cs / GetEnums.cs /
     GetEntityDefaults.cs / GetAggregateFields.cs / GetDefinitionConfigUnits.cs /
     GetDistances.cs / GetCommands.cs / GetRifts.cs; SteamGetProducts.cs /
     SteamStartTransaction.cs / SteamFinishTransaction.cs. -->