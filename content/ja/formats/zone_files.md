---
title: "ゾーンファイル"
description: "バイナリ地形レイヤーファイル：命名規則、構造体レイアウト、フラグビット、保存サイクル、および代わりにDBに格納されるデータ。"
weight: 50
---

# ゾーンファイル

ゾーンの地形は、ゾーンデータと同じ場所に、レイヤーごとに1つの**バイナリレイヤーファイル**のセットとして保存されます。ファイル名は `{layer}.{zoneid:0000}.bin`（`Zone.CreateTerrainDataFilename`）です。例：ゾーン42では `plants.0042.bin`。レイヤーは固定サイズ構造体のフラットな配列で、**行優先、幅 × 高さ**（既定は 2048×2048 = 4,194,304 タイル）です。

## レイヤー

| ファイル | 構造体 | バイト/タイル | 内容 |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags`（byte）+ `height`（byte）— 障害物、植物、装飾、島 |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (or 1) | タイルごとの制御ビット（以下のクセを参照） |
| `plants.NNNN.bin` | `PlantInfo` | 7 | タイルごとの植物状態（下記） |
| `altitude.NNNN.bin` | `ushort` | 2 | 標高。植物チェックでは `value / 4` として比較されます（クライアント座標のスケーリング） |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | 地形変形可能ゾーンのみ：タイルごとのブレンドマスク（下記） |
| `altitude_original.NNNN.bin` | `ushort` | 2 | 地形変形可能ゾーンのみ：ディスク上の地形変形前の標高 — **サーバーは読み込みません**（下記） |

派生レイヤー（読み込み時に計算され、**ファイルではありません**）：`SlopeLayer`（altitude から）と `Passable`（blocks + slope + DB の通過可能位置から、地形変形不可ゾーンのみ）。
地形変形可能ゾーンでは、altitude は `TerraformableAltitude` にラップされ、読み込み時にタイルごとの**バリア**範囲を計算します：`blend/65535` が定数 1850 → 元の標高（最小）と 30000 → 元の標高（最大）を混合し、その後範囲を現在の値を常に含むようにクランプします。地形変形後の標高更新は、そのバリア内にクランプされます。したがって `blend = 0` の場合、タイルは 1850 と 30000 の間で自由に地形変形可能になり、`blend = 65535` の場合は元の標高に固定されます。（ディスク上の `altitude_original.NNNN.bin` ファイルは、外部ツール用の地形変形前の標高を保持します。サーバーは、読み込んだ `altitude.NNNN.bin` からメモリ内で元の標高のスナップショットを取得し、そのファイル名を読み込むことはありません。）

### `BlockingInfo`（2バイト）

`flags` は `BlockingFlags`（byte）です：

| ビット | 名前 |
|---|---|
| 1 | 障害物（Obstacle） |
| 2 | 植物（Plant） |
| 4 | 装飾（Decor） |
| 8 | 島（Island） |

`NonNaturally` = Decor \| Island \| Obstacle。`height` はタイルの歩行ブロック高さです（植物のブロック高さは植物成長コードによってここに書き込まれます）。

### `TerrainControlFlags`（control レイヤー）

`ushort` フラグセット：

| ビット | 名前 |
|---|---|
| 1 | 植物禁止（AntiPlant） |
| 2 | 地形変形保護（TerraformProtected） |
| 4 | シンジケート領域（SyndicateArea） |
| 8 | コンクリートA（ConcreteA） |
| 16 | コンクリートB（ConcreteB） |
| 64 | 徘徊（Roaming） |
| 128 | ハイウェイ（Highway） |
| 256 | PBSハイウェイ（PBSHighway） |
| 512 | PBS地形変形保護（PBSTerraformProtected） |
| 1024 | NPC制限（NpcRestricted） |

（512/1024 の番号付けは `1 << n` に従います。ビット32は未使用です。）タイルが植物を許可するのは、`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)` のときです。

**保存上のクセ**：ローダーは **1バイト/タイル** と **2バイト/タイル** の両方の control ファイルを受け入れます — ファイル長がタイル数と等しい場合、各バイトが `TerrainControlFlags` に拡張されます。それ以外の場合は生の `ushort` 配列が読み込まれます（`LayerFileIO.LoadLayerData`）。稼働ゾーンはすべて **2バイト形式** を使用しています（`control.0000.bin` = 8,388,608 B = 4,194,304 × 2）。1バイト形式（4 MB）は、ローダーが今もサポートしているレガシーフォールバックです。

### `PlantInfo`（7バイト）— 植物タイルの状態

| バイト | フィールド | 意味 |
|---|---|---|
| 0 | `type` | `PlantType`（0 = 空。1..19 は [植物フィールド](/ja/formats/plant-fields/) を参照） |
| 1 | `state` | 成長状態インデックス（ルールの `state_N` テーブル内） |
| 2 | `time` | 成長ティックの累積値（ルールの `growRate` と比較） |
| 3 | `spawn` | **タイルごとの出現確率。ゾーンファイルに焼き込まれており、サーバーは書き込みません**（コードのどこにも代入が存在しません — `PlantInfo.Clear()` は意図的にこれを保持します）。0 = 不毛タイル：既に存在する植物は検証中に即座にクリアされ、発芽することはありません。それ以外の場合は試行ごとのゲートです：植物再生パスでは、ランダムに選ばれた空タイルは `FastRandom.NextByte() < spawn` の場合のみ採用され、つまりタイルごとの通過確率は ≈ `spawn/256` です。 |
| 4 | `health` | 現在のHP（ルールの状態ごとのHPに対する比率） |
| 5 | `material` | 現在の果実量（0–255） |
| 6 | `groundType` | `GroundType` byte（0=Darkrocks … 17=Sand-ish、20=未定義）— 植物ルールの `allowedTerrainTypes` が照合する地形クラス |

### 具体例 — 2048×2048 ゾーンのファイルサイズ（稼働ファイルと照合済み）

```
blocks    4,194,304 タイル × 2 B = 8,388,608 B (8 MB)
plants    4,194,304 タイル × 7 B = 29,360,128 B (28 MB)
altitude  4,194,304 タイル × 2 B = 8,388,608 B (8 MB)
control   4,194,304 タイル × 2 B = 8,388,608 B (8 MB, 2バイト形式; 1バイトのレガシーファイルなら 4 MB)
```

**ライブデータ確認**（`plants.0106.bin`、地形変形可能な gamma ゾーン）：全 4,194,304 タイルが `spawn = 0x83`（131/256 ≈ 試行あたり 51%）を持ち、`type = 0` となっていますが、現存する植物を持つ 10 タイルを除きます — spawn マップは、現在植物がある位置に依存しない、ゾーン全体の焼き込み確率フィールドです。

すべてのゾーンにすべてのファイルがあるわけではありません：84 ゾーン中 66 ゾーンが `plants.NNNN.bin` を同梱しています。ない 18 ゾーンは、置き換えられたレガシー gamma 変種（`zone_tm_g_*`、`zone_ics_g_*`、`zone_asi_g_*`、id 20–43）で、読み込まれません。レイヤーディレクトリは `$GameRoot/layers/` です。

## 保存サイクル（`IntervalLayerSaver.cs`）

- 変更可能な各レイヤー（blocks、control、plants、altitude）は `IntervalLayerSaver<T>` によって監視されます。タイル/領域への書き込みがあると dirty フラグが設定されます。
- このセーバーは **2時間** タイマーのプロセスとして登録されます（`TerrainsModule`）。ティックが発火すると、dirty なレイヤーが書き込まれます。
- 書き込みは `.tmp<ticks>.bin` ファイルに行われ、再読み込みに対して **MD5 検証** された後、初めて実際のファイルを置き換えます。
- サーバー停止時、dirty なレイヤーはもう一度保存されます。
- 鉱石ノードはこれらのファイルには**含まれません** — `mineralnodes` DB テーブルに永続化されます（30分ごとのフラッシュ、[鉱石フィールド](/ja/formats/ore-fields/) を参照）。

## ファイルであるデータとそうでないデータ

| データ | 保存場所 |
|---|---|
| 地形レイヤー（blocks/control/plants/altitude） | `.bin` ファイル |
| 鉱石ノード状態 | DB `mineralnodes` |
| ゾーンごとの植物種 | DB `plantrules` + ルール**ファイル**（`$GameRoot/plantrules/*.txt`） |
| ゾーン設定（肥沃度、サイズ、タイプ、ルールセット） | DB `zones` |
| 鉱石設定 | DB `mineralconfigs` |

<!-- 開発者向け注記: Zones/ZoneExtensions.cs（LayerFileIO、CreateTerrainDataFilename、
     1バイト/2バイトの control 処理、サイズ不一致時の安全なゼロ埋め）;
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs（RawData、SizeInBytes = Marshal.SizeOf<T>）;
     Zones/Terrains/IntervalLayerSaver.cs（dirty フラグ、MD5 + tmp リネーム、停止時保存）;
     Bootstrapper/Modules/TerrainsModule.cs（レイヤー読み込み順序: blocks、control、plants、
     altitude、blend; slope + passable の導出; 2時間セーバー + 2時間マテリアルプロセス）。 -->