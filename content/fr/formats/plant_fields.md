---
title: "Champs de plantes"
description: "Format du fichier de règles des plantes (GenXY), chaque champ de règle avec type, valeur par défaut et consommateur, plus la machine à états de croissance."
weight: 20
---

# Champs de plantes

Le comportement des plantes est défini par espèce au moyen d'un **fichier de règles** (texte brut) situé dans
`$GameRoot/plantrules/`. L'association des fichiers à une zone est définie dans la table de base de données
`plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset` ; le chargement et la fusion sont assurés par
`PlantRuleLoader.cs`, et la mise en correspondance champ-objet par `PlantRule.cs`.

## Format de fichier

Une ligne `clé=valeur` par ligne ; les commentaires de type `//` sont ignorés. Les valeurs utilisent des
**caractères de jetons GenXY** (`GenxyReader.cs` — le premier caractère sélectionne le type et la base numérique) :

| Jeton | Analysé comme | Exemple |
|---|---|---|
| `n` | int, décimal | `n125`, `n-1` |
| `N` | int[], décimal, séparé par des virgules | `N5,5,5,5` |
| `f` | double, décimal | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **hexadécimal** | `iFF` |
| `L` | long, **hexadécimal** | `L100` |
| `4` | int[], **hexadécimal** | `41,2,3` → [1, 2, 3] |

### ⚠ Le piège du « tableau nu »

Les fichiers contiennent également des valeurs comme `blockingHeight=40,3,3,4` sans **aucun jeton explicite**.
L'analyseur ne traite pas ces cas de manière spécifique : le `4` initial est consommé en tant que jeton
`IntegerArray` (hexadécimal), et le reste est analysé en hexadécimal. Ainsi :

```
blockingHeight=40,3,3,4   →  jeton '4' + tableau hex "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  jeton 'N' + tableau décimal         →  [0, 8, 11, 14]
```

Les deux syntaxes aboutissent à un `int[]`, et le `0` initial est ce que le `4` « absorbe ». C'est pourquoi
chaque tableau nu dans les fichiers fournis commence par `4` — c'est une convention qui conserve le premier
élément à la valeur voulue. **Lors de la rédaction de nouveaux fichiers de règles, utilisez explicitement
le préfixe `N`** ; les valeurs ≥ 10 dans un tableau nu seraient analysées en hexadécimal et changeraient
silencieusement de sens.

### Héritage

Une clé `source=$autre_regle.txt` charge d'abord `autre_regle.txt` et applique les clés du fichier courant
comme remplacements (`PlantRuleLoader.LoadRuleByName`). Exemple :
`irontree_t2.txt` est simplement :

```
source=$irontree_lo.txt
fruitAmount=n125
```

## Référence des champs

Tous les champs sont lus depuis le dictionnaire de paramètres fusionné (`PlantRule.cs`). Les clés manquantes
prennent la valeur par défaut indiquée.

| Clé | Type / défaut | Consommé par | Effet |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | Valeur de l'énumération `PlantType` pour cette espèce (1=GrassA … 19=Devrinol). Également l'octet `PlantInfo.type` stocké par tuile. |
| `name` | string | charge utile d'informations client | Nom d'affichage. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | Poids dans le tirage pondéré qui choisit une espèce pour une tuile **sans** voisin végétal. 0 = n'apparaît jamais. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | Multiplicateur de poids lorsqu'une tuile **a** des voisins : poids du candidat = `nbVoisins × spreading`. 0 = ne gagne jamais le tirage de propagation. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | Distance minimale par rapport à toute plante existante du même type ; 0/négatif = aucune limite. |
| `growRate` | int (0) | `GrowPlantOnTile` | Nombre de ticks de cube que l'octet `PlantInfo.time` doit accumuler avant que la machine à états ne change d'état. Plus il est élevé, plus c'est lent. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | Plage de pente autorisée de la couche de pente dérivée. En dehors de cette plage, la plante est nettoyée. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | Plage d'altitude, comparée à `Altitude / 4` (le `/4` correspond aux coordonnées client). Modulée par le `plantaltitudescale` de la zone. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | Plage pour `altitude/4 − waterLevel/4` — crée la végétation côtière. Également modulée par l'altitude. |
| `allowedTerrainTypes` | int[] (vide) | `ValidateTile` | Octets `groundType` autorisés (voir [Fichiers de zone](/fr/formats/zone-files/)). Vide = nulle part. Entièrement ignoré lorsque `allowedOnNonNatural` est activé. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | Premier état produisant des fruits. −1 ⇒ `NotFruiting` (jamais récoltable). |
| `fruitDefinition` | int (−1) | récolte | Définition d'objet du fruit. |
| `fruitMaterialName` | string | affichage | Nom du fruit (par ex. `$prismocitae`). |
| `fruitAmount` | byte (0), borné 0–255 | `GrowPlantOnTile` | Fruit maximal par plante. Le premier passage à l'état de fructification remplit 5–15 % du total ; chaque tick de croissance suivant ajoute 15–25 %, plafonné à 100 %. |
| `health` | byte[] par état | `GrowPlantOnTile`, combat | Points de vie par état de croissance. Lors d'un changement d'état, le **ratio** de santé actuel est conservé dans le nouvel état. |
| `blockingHeight` | int[] par état | `GrowPlantOnTile`, comptage d'apparition | Hauteur de blocage par état ; `>0` active le bit `Plant` dans la couche de blocage (walkable=false) et fait compter la plante dans l'objectif de fertilité de la zone. |
| `maxAmount` | int (−1) | `SpawnPlants` | Limite par zone sur le nombre d'individus de cette espèce ; −1 = illimité. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, tirage de fertilité | Exclu de **toutes** les apparitions naturelles ; n'existe que là où un joueur l'a planté. |
| `damageScale` | double (1.0) | combat végétal | Multiplicateur de dégâts subis. |
| `onlyOnUnprotectedZone` | bool (0) | validation d'apparition | Ne pousse que dans les zones non protégées. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | Ignore les vérifications de bits de contrôle, de type de terrain et de pente (pousse sur les tuiles « artificielles »). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (mort) | À la mort, efface les bits de contrôle ConcreteA/B sous la tuile. |
| `state_N` | int[] | `GetNextState` | Choix d'état suivant pour l'état `N` — chaque élément est sélectionné **uniformément au hasard**. |
| `action_N` | int[] | `GetNextState` | Choix de `PlantType` suivant pour l'état `N` (uniforme). Une valeur d'action de `0` (NotDefined) signifie la **mort**. |

La cohérence est vérifiée au chargement (`CheckConsistency`) : `len(health) == len(blockingHeight) == nombre d'états`.

## La machine à états de croissance

À chaque tick de cube de 32×32, pour chaque tuile de plante (`GrowPlantOnTile`) :

1. Si `time < growRate` : `time++`, terminé.
2. Sinon : `time = 0`, tirage de `state_N` et `action_N` pour l'état actuel :
   - `action == 0` → la plante meurt (signal d'élimination `type:0, state:1` pour le client) ;
     si `placesConcrete`, efface le béton sous la tuile.
   - sinon → `type = action`, `state = next`, `health = healthRatio × Health[newState]` (ratio de dégâts préservé).
   - Fruit : si `newState == fruitingState`, `material = fruitAmount × uniform(0.05, 0.15)` ; si `newState > fruitingState`, `material += fruitAmount × uniform(0.15, 0.25)` (plafonné à `fruitAmount`) ; sinon `material = 0`.
   - Hauteur de blocage = `blockingHeight[newState]` ; le bit `Plant` de la couche de blocage suit `height > 0`.

### Exemple concret — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → 1/… poids dans le tirage sans voisin
spreading=n2        → poids de grappe = 2 × voisins
growRate=n1         → tire un état à chaque tick de cube (rapide)
maxAmount=n190      → au maximum 190 par cube
health=N5,5,5,5     → 5 PV dans chaque état
blockingHeight=40,0,0,0 → analysé comme [0,0,0,0] : l'herbe ne bloque JAMAIS
fruitingState=n-1   → NotFruiting : l'herbe n'est jamais récoltable
state_0=40,0,1      → [0,0,1] : 2/3 restent à l'état 0, 1/3 avance
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → dans le dernier état : 3/4 restent, 1/4 meurt
```

Ainsi, une tuile d'herbe : avance d'environ un état tous les 3 ticks en moyenne, et dans le dernier état a 25 % de chances par tick de mourir et de se réensemencer — une espèce de couverture en perpétuel renouvellement sans fruits.

### Exemple concret — `wall.txt` (12 états, préfixé par `N`)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (peut régresser d'un état), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15` : une fortification plantée par le joueur qui n'existe
que dans les zones non protégées, plafonnée à 15 par cube, qui grandit (et rétrécit occasionnellement)
à travers 12 états jusqu'à une hauteur de 14 et 255 PV.

## Emplacement de l'état par tuile

L'état d'exécution par tuile est la structure `PlantInfo` de 7 octets dans le fichier de couche végétale
de la zone (`type, state, time, spawn, health, material, groundType`) — voir
[Fichiers de zone](/fr/formats/zone-files/). L'octet `spawn` est une probabilité d'apparition par tuile
intégrée dans le fichier de zone — `0` marque une tuile stérile (les plantes présentes sont nettoyées
lors de la validation, elle ne germe jamais) ; toute autre valeur signifie qu'une tentative de régénération
de plante sur cette tuile passe un filtre aléatoire avec une probabilité ≈ `spawn/256`. Le serveur n'écrit
jamais cet octet. Données réelles : chaque tuile de `plants.0106.bin` porte `0x83` (≈ 51 %).

## Données transmises au client

`PlantRuleExtensions.GetPlantInfoForClient` envoie, par espèce : `index`, `mineral`
(= fruitDefinition), `name`, `blocks` (blockingHeight), `health`.

<!-- Developer notes: Materials/Plants/PlantRule.cs (field getters, GetNextState,
     CheckConsistency); PlantRuleLoader.cs (file load, source: override,
     plantAltitudeScale applied to allowedAltitudeLow/High + allowedWaterLevelLow);
     PlantRuleExtensions.cs (fertility + spreading weighted draws);
     NatureCube.cs (ValidateTile checks order: block flags -> spawn byte -> rule
     existence -> control bits -> altitude/4 -> water level -> terrain type ->
     slope; GrowPlantOnTile state machine + fruit math); Common/SettingsLoader.cs
     (line join with '#' then GenxyConverter.Deserialize); GenXY/GenxyReader.cs +
     GenxyToken.cs (token characters; '4' = hex int array, 'N' = decimal int array,
     'n' = int decimal). Rule files live at $GameRoot/plantrules (plantrules table
     maps rulesetid -> file names). -->
