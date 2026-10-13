---
title: "Formaten"
description: "Ontwikkelaarreferentie: hoe elk statistieveld wordt opgeslagen, geparseerd en gebruikt door de server."
weight: 60
---

# Formaten

Veldreferentie voor ontwikkelaars. Elke pagina volgt een statistieveld van de opslag
(DB-kolom, regelbestandsleutel of binair laagbyte) door de code die het verwerkt,
met uitgewerkte numerieke voorbeelden. Spelersgerichte samenvattingen over
"wat betekent het in het spel" staan in de [features](/nl/features/) en
[content](/content/) secties — hier staan de exacte types, standaardwaarden,
formules en codepaden.

| Pagina | Inhoud |
|---|---|
| [Plantenvelden](/nl/formats/plant-fields/) | Plantenregelbestandsformaat (GenXY), elk regelveld met type/standaardwaarde/verwerker, de groeistatemachine, validatiecontroles |
| [Ertsvelden](/nl/formats/ore-fields/) | `minerals` + `mineralconfigs` kolommen, de node-generatieformules, node-levenscyclus en persistentie, extractiemechanieken |
| [Plaatsbare velden](/nl/formats/deployable-fields/) | Hoe plaatsbare objecten worden geïdentificeerd, capsule↔object-koppeling, en de aggregatievelden die geplaatste objecten sturen |
| [Zonebestanden](/nl/formats/zone-files/) | De binaire terreinlaagbestanden: structuurindelingen, vlagbits, opslagcyclus en wat in plaats daarvan in de DB staat |

Conventies:

- **GenXY** is de instellingen-serialisatie die wordt gebruikt voor regelbestanden en `entitydefaults.options`
  (tekenkarakters per `GenxyToken.cs`; zie [Plantenvelden → bestandsformaat](/nl/formats/plant-fields/)).
- Codepaden zijn relatief ten opzichte van `src/`.
- Wanneer een waarde een **constant** is (geen data), worden het bestand en de constantenaam vermeld.