---
title: "植物フィールド"
description: "植物ルールファイルのフォーマット（GenXY）、各ルールフィールドの型、デフォルト値、利用箇所、および成長ステートマシン。"
weight: 20
---

# 植物フィールド

植物の挙動は、種ごとに`$GameRoot/plantrules/`下の**ルールファイル**（プレーンテキスト）で
定義されます。どのファイルがどのゾーンに属するかは、DBマッピング
`plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset`で定義され、読み込みと
マージは`PlantRuleLoader.cs`が、フィールドからオブジェクトへのマッピングは`PlantRule.cs`が
担当します。

## ファイル形式

1行に1つの`key=value`で記述され、`//`形式のコメントは除去されます。値には**GenXYトークン
文字**（`GenxyReader.cs` — 先頭文字が型と進数を指定）が使用されます：

| トークン | 解釈される型 | 例 |
|---|---|---|
| `n` | int, 10進数 | `n125`, `n-1` |
| `N` | int[], 10進数, カンマ区切り | `N5,5,5,5` |
| `f` | double, 10進数 | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **16進数** | `iFF` |
| `L` | long, **16進数** | `L100` |
| `4` | int[], **16進数** | `41,2,3` → [1, 2, 3] |

### ⚠ 「素の配列（bare array）」の罠

ファイルには**明示的なトークンなし**で`blockingHeight=40,3,3,4`のように記述された値も存在します。
パーサーはこれらを特別扱いしません：先頭の`4`が`IntegerArray`（16進数）トークンとして消費され、
残りが16進数としてパースされます。したがって：

```
blockingHeight=40,3,3,4   →  トークン '4' + 16進数配列 "0,3,3,4"  →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  トークン 'N' + 10進数配列            →  [0, 8, 11, 14]
```

どちらの表記も最終的には`int[]`となり、先頭の`0`は`4`によって「飲み込まれた」値です。配布されている
ファイル内のすべての素の配列が`4`で始まっているのはこのためです — 最初の要素を意図した値に保つための
慣例となっています。**新しいルールファイルを作成する際は、明示的に`N`プレフィックスを使用してください。**
素の配列内の10以上の値は16進数として解釈され、意図しない意味に変わってしまいます。

### 継承

`source=$other_rule.txt`というキーを指定すると、まず`other_rule.txt`が読み込まれ、現在の
ファイルのキーが上書きとして適用されます（`PlantRuleLoader.LoadRuleByName`）。例：
`irontree_t2.txt`の内容は以下の通りです：

```
source=$irontree_lo.txt
fruitAmount=n125
```

## フィールドリファレンス

すべてのフィールドはマージされた設定ディクショナリ（`PlantRule.cs`）から読み出されます。
キーが存在しない場合は、記載されているデフォルト値が使用されます。

| キー | 型 / デフォルト | 利用箇所 | 効果 |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | この種の`PlantType` enum値（1=GrassA … 19=Devrinol）。また、タイルごとに保存される`PlantInfo.type`バイト値でもあります。 |
| `name` | string | クライアント情報ペイロード | 表示名。 |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | 周囲に植物の隣接が**ない**タイルで種を選択する重み付け抽選の重み。0 = 自然生成されない。 |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | タイルに隣接植物が**ある**場合の重み乗数：候補の重み = `neighbourCount × spreading`。0 = 繁殖抽選で選ばれない。 |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | 同種の既存植物からの最小距離。0または負の値 = 無制限。 |
| `growRate` | int (0) | `GrowPlantOnTile` | ステートマシンが進行するまでに`PlantInfo.time`バイトが蓄積する必要があるキューブティック数。値が大きいほど成長が遅い。 |
| `slope` / `minSlope` | int (0) | `ValidateTile` | 派生スロープレイヤーにおける許容傾斜範囲。範囲外の植物は除去されます。 |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | 許容高度範囲。`Altitude / 4`と比較されます（`/4`はクライアント座標系に対応）。ゾーンの`plantaltitudescale`によってスケールされます。 |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | `altitude/4 − waterLevel/4`の許容範囲 — 海岸植生を作成します。こちらも高度スケールが適用されます。 |
| `allowedTerrainTypes` | int[] (空) | `ValidateTile` | 許容される`groundType`バイト値（[ゾーンファイル](/ja/formats/zone-files/)参照）。空の場合はどこにも生えません。`allowedOnNonNatural`が設定されている場合は完全にスキップされます。 |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | 果実を結び始める最初の状態。−1 ⇒ `NotFruiting`（収穫不可）。 |
| `fruitDefinition` | int (−1) | harvesting | 果実のアイテム定義ID。 |
| `fruitMaterialName` | string | display | 果実名（例：`$prismocitae`）。 |
| `fruitAmount` | byte (0), 0–255の範囲 | `GrowPlantOnTile` | 植物あたりの最大果実量。結実状態に初めて入った際にその5–15%が満たされ、その後の成長ティックごとに15–25%が加算され、最大100%まで蓄積されます。 |
| `health` | 状態ごとのbyte[] | `GrowPlantOnTile`, combat | 成長状態ごとの耐久力（HP）。状態遷移時、現在の耐久力**割合（ratio）**が新しい状態に引き継がれます。 |
| `blockingHeight` | 状態ごとのint[] | `GrowPlantOnTile`, spawn counting | 状態ごとの進入ブロック高。`>0`の場合、ブロックレイヤーの`Plant`ビットが設定され（walkable=false）、ゾーンの肥沃度目標の計算対象になります。 |
| `maxAmount` | int (−1) | `SpawnPlants` | ゾーンあたりのこの種の最大個体数制限。−1 = 無制限。 |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, fertility draw | **すべての**自然生成から除外されます。プレイヤーが植えた場所にのみ存在します。 |
| `damageScale` | double (1.0) | plant combat | 受けるダメージの乗数。 |
| `onlyOnUnprotectedZone` | bool (0) | spawn validation | 非保護ゾーンでのみ成長します。 |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | コントロールビット、地形タイプ、傾斜のチェックをスキップします（「人工」タイル上でも成長）。 |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (死亡時) | 死亡時、タイル下のConcreteA/Bコントロールビットをクリアします。 |
| `state_N` | int[] | `GetNextState` | 状態`N`における次の状態の候補 — 各要素は**一様ランダム**に選ばれます。 |
| `action_N` | int[] | `GetNextState` | 状態`N`における次の`PlantType`候補（一様ランダム）。アクション値`0`（NotDefined）は**死亡**を意味します。 |

整合性は読み込み時に検証されます（`CheckConsistency`）：`len(health) == len(blockingHeight) == 状態数`。

## 成長ステートマシン

32×32キューブのティックごとに、すべての植物タイルに対して以下が実行されます（`GrowPlantOnTile`）：

1. `time < growRate`の場合：`time++`を行い終了。
2. それ以外の場合：`time = 0`とし、現在の状態に対応する`state_N`と`action_N`を抽選：
   - `action == 0` → 植物が死亡（クライアントへ`type:0, state:1`の消去信号を送信）。
     `placesConcrete`が有効な場合、タイル下のコンクリートをクリア。
   - それ以外 → `type = action`, `state = next`, `health = healthRatio × Health[newState]`
     （被ダメージ割合を維持）。
   - 果実：`newState == fruitingState`の場合、`material = fruitAmount × uniform(0.05, 0.15)`。
     `newState > fruitingState`の場合、`material += fruitAmount × uniform(0.15, 0.25)`
     （最大`fruitAmount`まで）。それ以外は`material = 0`。
   - ブロック高 = `blockingHeight[newState]`。ブロックレイヤーの`Plant`ビットは`height > 0`に従います。

### 具体例 — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → 隣接なしの抽選における重み 1/…
spreading=n2        → クラスタ重み = 2 × 隣接数
growRate=n1         → キューブティックごとに状態をロール（高速）
maxAmount=n190      → キューブあたり最大190
health=N5,5,5,5     → すべての状態で5 HP
blockingHeight=40,0,0,0 → [0,0,0,0]とパース：草は通行を一切ブロックしない
fruitingState=n-1   → NotFruiting：草は収穫不可
state_0=40,0,1      → [0,0,1]：2/3の確率で状態0を維持、1/3で進行
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → 最終状態で：3/4が維持、1/4が死亡
```

したがって、草タイルは平均約3ティックごとに1段階進行し、最終状態では毎ティック25%の確率で
枯れて再び種を撒きます — 果実をつけず、絶えず入れ替わる地表被覆種です。

### 具体例 — `wall.txt`（12状態、`N`プレフィックス使用）

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6`（1段階退行可能）, `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: プレイヤーが植える防壁であり、
非保護ゾーンにのみ存在し、キューブあたり15個に制限され、12段階の状態を通じて成長
（時に縮小）し、最大高さ14、255 HPに達します。

## タイルごとの状態の保存場所

タイルごとの実行時状態は、ゾーンの植物レイヤーファイル内の7バイト構造体`PlantInfo`
（`type, state, time, spawn, health, material, groundType`）です — [ゾーンファイル](/ja/formats/zone-files/)
を参照してください。`spawn`バイトはゾーンファイルに焼き込まれたタイルごとの出現確率です —
`0`は不毛のタイルを示し（検証時に植物が消去され、芽吹くことはありません）、それ以外の値は
そのタイルでの植物再生試行が約`spawn/256`の確率のランダムゲートを通過することを意味します。
サーバーはこのバイトを書き換えることはありません。実際のデータ：`plants.0106.bin`のすべてのタイルは
`0x83`（約51%）を保持しています。

## クライアントペイロード

`PlantRuleExtensions.GetPlantInfoForClient`は、種ごとに次の情報を送信します：`index`、`mineral`
（= fruitDefinition）、`name`、`blocks`（blockingHeight）、`health`。

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
