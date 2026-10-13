---
title: "Configurazione client e PC"
description: "Esecuzione del client su Windows e Linux, multi-boxing nel rispetto delle regole, ridimensionamento della UI e avvio senza privilegi di amministratore."
weight: 24
---

# Configurazione client e PC

Note pratiche per l'esecuzione del client di Perpetuum.

## Prima di tutto, le regole

Il multi-boxing (più client che controllano diversi personaggi) è consentito
**entro certi limiti**. Regole di fair-play da conoscere prima di farlo:

- **Nessuna automazione o software di controllo multi-client** — mai.
- **Non più di 5 account attivi contemporaneamente.**
- Nessun account registrato con indirizzi email falsi, non validi o irraggiungibili —
  l'indirizzo deve essere di tua proprietà.

Le violazioni possono comportare un ban immediato e permanente.

## Windows: client multipli

1. Installa il client Steam di Perpetuum.
2. Verifica che la cartella di gioco contenga un file `steam_appid.txt` con contenuto
   `223410`.
3. Copia l'intera cartella `Perpetuum` per ciascun client aggiuntivo.
4. Esegui `Perpetuum.exe` in ogni copia (facoltativamente aggiungi le copie a Steam come
   giochi non di Steam).

**Spazio su disco:** `Layers.gbf` e `Perpetuum.gbf` sono di grandi dimensioni e identici in
ogni copia — crea collegamenti simbolici (`mklink`) o scorciatoie in modo che siano
archiviati una sola volta.

## Linux: client multipli

Ogni copia del client necessita di una **versione di Proton diversa**, altrimenti si rifiuterà di avviarsi:

1. Installa Steam e Perpetuum come di consueto; verifica `steam_appid.txt` (`223410`).
2. Copia la cartella `Perpetuum` per ciascun client.
3. Con l'accesso effettuato su Steam, installa diverse versioni recenti di Proton (tramite Steam,
   manualmente o tramite build GloriousEggroll).
4. Aggiungi ogni copia a Steam come gioco non di Steam che punta al rispettivo `Perpetuum.exe`.
5. Forza una **versione di Proton diversa** per ciascuna copia nelle relative opzioni di avvio.
6. Avvia prima l'app principale di Steam, quindi esegui le copie.

Risoluzione dei problemi:

- Selezionare una versione di Proton **non** la installa automaticamente — è necessario avviare il
  gioco almeno una volta con tale versione selezionata.
- Se l'app principale di Steam non si avvia, prova ad avviarla prima in modalità provvisoria (Safe mode).
- A partire da Proton 5.0, l'emulazione di DirectX 9/12 si basa su **Vulkan**. Non possiedi una GPU compatibile con Vulkan? Aggiungi `PROTON_USE_WINED3D=1 %command%` alle opzioni di avvio di ciascuna copia.
- Casella di testo vuota con un avviso rosso: installa `libfreetype6:i386`
  (distribuzioni basate su Debian/Ubuntu).

## Ridimensionamento della UI

Il client utilizza un'interfaccia utente a pixel fissi senza ridimensionamento dinamico. Soluzioni alternative:

- **Schermo intero a bassa risoluzione** — passa a schermo intero impostando una risoluzione inferiore a quella del tuo display e lascia che la UI si adatti estendendosi per riempirlo (le modalità finestra e senza bordi utilizzano sempre la risoluzione nativa). Anche abbassare la risoluzione del display stesso produce lo stesso effetto.
- **Applicazioni di ridimensionamento UI** — ad esempio Lossless Scaler (Steam, Windows): esegui il client in modalità finestra alla risoluzione di base, imposta un rapporto di scala personalizzato nel programma, attiva il ridimensionamento e porta in primo piano la finestra del client. Aspettati il consueto compromesso tra fluidità e nitidezza del testo.
- **Lente di ingrandimento del sistema operativo** — la Lente di ingrandimento di Windows (o equivalente) per una lettura occasionale da vicino.

## Avvio senza privilegi di amministratore

1. Copia i file del client al di fuori della cartella di Steam in una posizione accessibile in scrittura.
2. Crea lì un file `Perpetuum.bat` contenente
   `cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"`.
3. Avvia tramite il file batch.

<!--
Developer notes: rewritten 2026 in original prose. An earlier version was adapted from the
Open Perpetuum community wiki (perpetuum.miraheze.org: Multi-Boxing, Linux
Setup, Client UI Scaling, Launching without Admin Rights); that text was
fully replaced, not reused. These are client-side procedures for the retail Steam client build;
nothing here is verifiable from this server's backend, and no server feature is
claimed. The Reshader (graphics mod) was intentionally left out: it targets the
retail client build and is not an OPP-server feature.
-->