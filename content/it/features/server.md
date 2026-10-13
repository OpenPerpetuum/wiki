---
title: "Server e dati di riferimento"
description: "Informazioni sul server, record, download dei dati di riferimento e negozio di gioco."
weight: 170
---

# Server e dati di riferimento

Questa pagina illustra i "meta" sistemi: informazioni su server e sistema, record, dati di
riferimento scaricati dal client e negozio in-game.

> Le posizioni nell'interfaccia seguono la [panoramica della UI del client](/it/features/ui/). Le meccaniche
> riportate di seguito sono state verificate rispetto al server.

## Informazioni su server e sistema

- **Informazioni server** — stato e informazioni generali del server.
- **Informazioni sistema** — dettagli a livello di sistema.
- **Stato arresto server** — indica se è programmato un riavvio o uno spegnimento (in sola lettura per
  i giocatori; l'arresto effettivo è un'azione amministrativa).

## Record

- **Record del server** — i migliori punteggi e risultati dell'intero server.
- **I miei record** — i tuoi record personali.

Vedi anche [combattimento](/it/features/combat/) per i dettagli su come le uccisioni alimentano queste statistiche.

## Dati di riferimento

Il client scarica dati di riferimento statici dal server per eseguire il rendering corretto dei contenuti.
Si tratta di **consultazioni in sola lettura**, non di azioni del giocatore:

- **Effetti** — definizioni degli effetti.
- **Enum** — valori delle enumerazioni.
- **Predefiniti entità** — definizioni di base per le entità.
- **Campi aggregati** — dati dei campi aggregati.
- **Unità configurazione definizioni** — configurazioni per singola definizione.
- **Distanze** — costanti di distanza utilizzate dal client.
- **Comandi** — elenco dei comandi noti (un riferimento lato client).
- **Rift** — definizioni dei varchi/rift (vedi anche l'elenco dei rift di zona).

Questi dati non vengono "utilizzati" direttamente dall'utente; il client li recupera su richiesta. Sono
elencati qui in quanto compaiono nell'inventario dei comandi.

## Il negozio

Il negozio in-game (un'integrazione di pagamento):

- **Elenco prodotti** — visualizza gli articoli in vendita.
- **Avvia transazione** — inizia un acquisto.
- **Completa transazione** — finalizza un acquisto.

Gli acquisti nel negozio sono transazioni con denaro reale (o equivalente); i prodotti esatti e
i prezzi dipendono dai contenuti del negozio.

## Note pratiche

- **I dati di riferimento vengono recuperati automaticamente** — non è mai necessario richiederli manualmente;
  mantengono il client sincronizzato con i contenuti del server.
- **I record servono per vantarsi** — controlla i tuoi primati personali e quelli del server.
- **Le transazioni del negozio sono a due fasi** — inizio e completamento; non considerare un acquisto
  concluso finché non è stato finalizzato.
- **Lo stato di arresto è informativo** — segnala l'arrivo imminente di una finestra di manutenzione.

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