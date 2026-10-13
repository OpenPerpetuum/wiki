---
title: "Sociale"
description: "Comunicazione e reputazione: posta, canali di chat, amici, relazioni (standing), pagine gialle, notizie e sondaggi."
weight: 140
---

# Sociale

Questa pagina illustra la comunicazione e la reputazione: **posta**, **canali di chat**, **amici**,
**relazioni (standing)** e le funzionalità pubbliche di **pagine gialle / notizie / sondaggi**.

> Le posizioni nell'interfaccia seguono la [panoramica dell'interfaccia utente del client](/it/features/ui/) (il pulsante **Posta** in alto a sinistra; chat e
> social hanno finestre dedicate). Le meccaniche descritte di seguito sono verificate lato server.

## Posta

**Posta personale:**
- **Elencare** i messaggi, **aprire** un messaggio, **inviare** posta, **eliminare** un messaggio.
- **Conteggio nuovi messaggi** — quanti messaggi non letti sono presenti.
- **Cartelle** — visualizzare le **cartelle in uso**, **spostare** un messaggio in una cartella, **eliminare** una cartella.

**Posta di massa (corporation):** inviata all'intera corporazione:
- **Inviare**, **elencare**, **aprire**, **eliminare**, **conteggio nuovi messaggi**.

## Canali di chat

I **canali** sono stanze di chat con un nome:

- **Creare** un canale, **entrare** in un canale, **uscire** da un canale, **scrivere** al suo interno.
- **Elencare** i canali (tutti, o solo i propri).
- **Moderazione** (in qualità di proprietario/ufficiale del canale): **espellere (kick)**, **bannare** / **sbannare**, **impostare il ruolo di un membro**, **silenziare globalmente (mute)**, visualizzare i membri **silenziati** / **bannati**.
- **Impostazioni**: **impostare una password**, **impostare un argomento (topic)**, preferenze di **notifica**.

**Chat diretta** — un messaggio privato tra personaggi.

## Amici

- **Inviare una richiesta di amicizia**, **rispondere** a una richiesta, **confermare** una richiesta in sospeso.
- **Rimuovere** un amico, **bloccare** un personaggio.
- **Elencare** i propri amici.

Bloccare un personaggio gli impedisce di commerciare o scambiarsi messaggi con te (consulta
[guida introduttiva](/it/features/getting-started/) per il blocco degli scambi per singolo personaggio).

## Relazioni (standing / reputazione)

Lo **standing** è un valore numerico di reputazione tra entità (personaggi, corporation,
alleanze):

- **Elencare** i propri standing, visualizzare la **cronologia dello standing**.
- **Impostare lo standing** — dove consentito, impostare un valore di standing. Vincoli:
  - il **bersaglio** deve essere un personaggio, una corporazione (privata) o un'alleanza (privata),
  - la **sorgente** deve analogamente essere un'entità valida,
  - non è possibile impostare uno standing verso se stessi.
- **Standing predefiniti** — i valori base di standing per le alleanze/corporation predefinite.

Lo standing è un valore compreso tra **-10 e +10** (0 = neutrale, il valore predefinito; impostare 0 cancella
la voce). La **reputazione** di un'entità è l'aggregato dello standing di tutti verso di essa.
Uno standing positivo ha un impatto pratico in contesti specifici — ad esempio, durante un'[intrusione](/it/features/intrusion/)
una corporazione con standing reciproco ≥ 10 è considerata un **alleato**, la cui vittoria SAP non
danneggia la tua struttura.

Lo standing influenza il modo in cui le fazioni e gli altri giocatori trattano te e la tua corporazione
(vedi [gruppi](/it/features/groups/)).

## Pagine gialle

Un elenco pubblico (annunci gestiti dalle corporazioni):
- **Consultare** un annuncio, **pubblicarne** uno, **eliminarne** uno, **cercare** nell'elenco.

## Notizie e sondaggi

- **Notizie** — visualizzare le **categorie** e l'**elenco delle notizie**; **conteggio nuovi elementi** per gli elementi non letti.
- **Sondaggi** — **visualizzare** un sondaggio e **rispondere**.

## Note pratiche

- **Posta vs. chat** — la posta è persistente e privata; i canali sono stanze di gruppo in tempo reale.
- **La posta di massa è uno strumento aziendale** — gli ufficiali la usano per inviare comunicazioni a tutti i membri.
- **Gli standing sono direzionali** — lo standing di A verso B è separato da quello di B verso A, e
  segue la tua corporazione.
- **Il blocco è la tua difesa** — blocca spammer o commercianti ostili.
- **I canali possono essere protetti** — password e ruoli regolano chi può accedere o parlare.

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