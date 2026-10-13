---
title: "Fichiers de zone"
description: "Les fichiers binaires de couches de terrain : nommage, structures, bits de contrôle, cycle de sauvegarde et ce qui réside en base de données."
weight: 50
---

# Fichiers de zone

Le terrain d'une zone est stocké sous forme d'un ensemble de **fichiers binaires de couches**, un par couche,
aux côtés des données de la zone. Le nommage suit le format `{couche}.{zoneid:0000}.bin`
(`Zone.CreateTerrainDataFilename`) — par exemple `plants.0042.bin` pour la zone 42. Les couches sont des
tableaux plats d'une structure de taille fixe, **en ordre ligne par ligne (row-major), largeur × hauteur**
(par défaut 2048×2048 = 4 194 304 tuiles).

## Les couches

| Fichier | Structure | Octets/tuile | Contenu |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (octet) + `height` (octet) — obstacles, plantes, décors, îles |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (ou 1) | bits de contrôle par tuile (voir particularité ci-dessous) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | état des plantes par tuile (ci-dessous) |
| `altitude.NNNN.bin` | `ushort` | 2 | élévation ; comparée comme `valeur / 4` dans les tests de plantes (mise à l'échelle des coordonnées client) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | zones terraformables uniquement : masque de fondu par tuile (ci-dessous) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | zones terraformables uniquement : élévation pré-terraformage sur disque — **non lue par le serveur** (ci-dessous) |

Couches dérivées (calculées au chargement, **non** stockées sous forme de fichiers) : `SlopeLayer` (d'après l'altitude)
et `Passable` (d'après blocks + pente + positions praticables en base de données, zones non-terraformables uniquement).
Sur les zones terraformables, l'altitude est enveloppée dans un `TerraformableAltitude`, qui calcule une plage de
**barrière** par tuile au chargement : `blend/65535` mélange les constantes 1850 → altitude d'origine (min) et
30000 → altitude d'origine (max), puis restreint la plage afin qu'elle contienne toujours la valeur actuelle.
Les mises à jour d'altitude terraformée sont bornées par cette barrière — ainsi `blend = 0` laisse une tuile
librement terraformable entre 1850 et 30000, tandis que `blend = 65535` la fige à son élévation d'origine.
(Les fichiers `altitude_original.NNNN.bin` sur le disque contiennent les élévations pré-terraformage pour les outils
externes ; le serveur effectue son instantané d'altitude originale en mémoire à partir du `altitude.NNNN.bin` chargé
et ne lit jamais ce fichier sur disque.)

### `BlockingInfo` (2 octets)

`flags` correspond à `BlockingFlags` (octet) :

| Bit | Nom |
|---|---|
| 1 | Obstacle |
| 2 | Plant (Plante) |
| 4 | Decor (Décor) |
| 8 | Island (Île) |

`NonNaturally` = Decor \| Island \| Obstacle. `height` est la hauteur de blocage du déplacement de la tuile
(la hauteur de blocage des plantes y est inscrite par le code de croissance des plantes).

### `TerrainControlFlags` (couche de contrôle)

Ensemble de drapeaux `ushort` :

| Bit | Nom |
|---|---|
| 1 | AntiPlant |
| 2 | TerraformProtected |
| 4 | SyndicateArea |
| 8 | ConcreteA |
| 16 | ConcreteB |
| 64 | Roaming |
| 128 | Highway |
| 256 | PBSHighway |
| 512 | PBSTerraformProtected |
| 1024 | NpcRestricted |

(La numérotation 512/1024 suit `1 << n` ; le bit 32 est inutilisé.) Une tuile est autorisée pour les plantes lorsque
`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`.

**Particularité de stockage** : le chargeur accepte les fichiers de contrôle à **1 octet/tuile** et à
**2 octets/tuile** — si la taille du fichier est égale au nombre de tuiles, chaque octet est élargi en un
`TerrainControlFlags` ; sinon, le tableau brut de `ushort` est lu (`LayerFileIO.LoadLayerData`). Les zones en
production utilisent toutes le **format 2 octets** (`control.0000.bin` = 8 388 608 octets = 4 194 304 × 2) ;
la variante à 1 octet (4 Mo) est un format hérité que le chargeur supporte toujours.

### `PlantInfo` (7 octets) — l'état de la tuile de plante

| Octet | Champ | Signification |
|---|---|---|
| 0 | `type` | `PlantType` (0 = vide ; 1..19 selon [Champs de plantes](/fr/formats/plant-fields/)) |
| 1 | `state` | Indice d'état de croissance (dans la table `state_N` de la règle) |
| 2 | `time` | Accumulateur de ticks de croissance (comparé au `growRate` de la règle) |
| 3 | `spawn` | **Probabilité d'apparition par tuile, intégrée dans le fichier de zone ; le serveur ne l'écrit jamais** (aucune affectation n'existe dans le code — `PlantInfo.Clear()` la préserve délibérément). 0 = tuile stérile : toute plante déjà présente est immédiatement retirée lors de la validation, et aucune ne germe. Sinon, sert de filtre par tentative : lors de la passe de régénération des plantes, une tuile vide aléatoire n'est acceptée que si `FastRandom.NextByte() < spawn`, soit une chance de validation par tuile ≈ `spawn/256`. |
| 4 | `health` | PV actuels (ratio des points de vie par état de la règle) |
| 5 | `material` | Quantité actuelle de fruit (0–255) |
| 6 | `groundType` | Octet `GroundType` (0=Darkrocks … 17=Sand-ish, 20=undefined) — classe de terrain testée par le `allowedTerrainTypes` de la règle végétale |

### Exemple concret — tailles de fichiers pour une zone de 2048×2048 (vérifié d'après les fichiers réels)

```
blocks    4 194 304 tuiles × 2 B = 8 388 608 B (8 Mo)
plants    4 194 304 tuiles × 7 B = 29 360 128 B (28 Mo)
altitude  4 194 304 tuiles × 2 B = 8 388 608 B (8 Mo)
control   4 194 304 tuiles × 2 B = 8 388 608 B (8 Mo, format 2 octets ; un ancien fichier 1 octet ferait 4 Mo)
```

**Vérification sur données réelles** (`plants.0106.bin`, la zone gamma terraformable) : l'ensemble des 4 194 304
tuiles porte `spawn = 0x83` (131/256 ≈ 51 % de chance par tentative) et `type = 0` à l'exception de 10 tuiles
contenant des plantes vivantes — la carte d'apparition est un champ de probabilités précalculé sur toute la zone,
indépendamment de l'emplacement actuel des plantes.

Toutes les zones ne possèdent pas l'ensemble des fichiers : 66 des 84 zones fournissent un `plants.NNNN.bin`.
Les 18 zones manquantes sont les variantes gamma héritées remplacées (`zone_tm_g_*`, `zone_ics_g_*`, `zone_asi_g_*`,
identifiants 20–43), qui ne sont pas chargées. Le répertoire des couches est `$GameRoot/layers/`.

## Le cycle de sauvegarde (`IntervalLayerSaver.cs`)

- Chaque couche modifiable (blocks, control, plants, altitude) est surveillée par un `IntervalLayerSaver<T>` ;
  toute écriture sur une tuile ou une zone active un drapeau de modification (dirty).
- Le mécanisme de sauvegarde est enregistré comme un processus sur un intervalle de **2 heures** (`TerrainsModule`) ;
  une couche modifiée est enregistrée lorsque le tick se déclenche.
- Les écritures s'effectuent dans un fichier `.tmp<ticks>.bin`, sont **vérifiées par empreinte MD5** par rapport
  à une relecture, et remplacent seulement ensuite le fichier réel.
- À l'arrêt du serveur, les couches modifiées sont sauvegardées une dernière fois.
- Les filons de minerai ne sont **pas** stockés dans ces fichiers — ils sont persistés dans la table de base
  de données `mineralnodes` (sauvegarde toutes les 30 minutes, voir [Champs de minerais](/fr/formats/ore-fields/)).

## Ce qui est et n'est pas un fichier

| Données | Emplacement |
|---|---|
| Couches de terrain (blocks/control/plants/altitude) | Fichiers `.bin` |
| État des filons de minerai | Base de données `mineralnodes` |
| Espèces végétales par zone | Base de données `plantrules` + **fichiers** de règles (`$GameRoot/plantrules/*.txt`) |
| Configuration de zone (fertilité, taille, type, ensemble de règles) | Base de données `zones` |
| Configuration de minerai | Base de données `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1-vs-2 byte control handling, safe zero-fill on size mismatch);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty flag, MD5 + tmp rename, stop-save);
     Bootstrapper/Modules/TerrainsModule.cs (layer load order: blocks, control, plants,
     altitude, blend; slope + passable derivation; 2h saver + 2h material process). -->
