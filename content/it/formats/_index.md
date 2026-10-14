---
title: "Formati"
description: "Riferimento per gli sviluppatori: come ogni campo delle statistiche viene memorizzato, analizzato e utilizzato dal server."
weight: 60
---

# Formati

Riferimento dei campi rivolto agli sviluppatori. Ogni pagina traccia un campo delle statistiche dalla sua memorizzazione
(colonna DB, chiave del file delle regole o byte del layer binario) attraverso il codice che lo consuma,
con esempi numerici svolti. I riassunti rivolti ai giocatori su "cosa significa nel gioco" si trovano
nelle sezioni [features](/it/features/) e [content](/content/) — qui si trovano invece i
tipi esatti, i valori predefiniti, le formule e i percorsi del codice.

| Pagina | Contenuti |
|---|---|
| [Plant fields](/it/formats/plant-fields/) | Formato del file delle regole delle piante (GenXY), ogni campo delle regole con tipo/default/consumer, la macchina a stati di crescita, i controlli di validazione |
| [Ore fields](/it/formats/ore-fields/) | Colonne di `minerals` + `mineralconfigs`, le formule di generazione dei nodi, ciclo di vita e persistenza dei nodi, meccaniche di estrazione |
| [Deployable fields](/it/formats/deployable-fields/) | Come vengono identificati i deployable, associazione capsula↔oggetto e i campi aggregati che gestiscono gli oggetti posizionati |
| [Zone files](/it/formats/zone-files/) | I file dei layer binari del terreno: layout delle struct, flag bit, ciclo di salvataggio e cosa risiede invece nel DB |

Convenzioni:

- **GenXY** è la serializzazione delle impostazioni utilizzata per i file delle regole e per `entitydefaults.options`
  (caratteri token secondo `GenxyToken.cs`; vedere [Plant fields → file format](/it/formats/plant-fields/)).
- I percorsi del codice sono relativi a `src/`.
- Quando un valore è una **costante** (non un dato), vengono indicati il file e il nome della costante.