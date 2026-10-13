---
title: "クライアントとPCのセットアップ"
description: "WindowsおよびLinuxでのクライアント実行、ルール内での複垢（マルチボックス）起動、UIスケーリング、管理者権限なしでの起動方法。"
weight: 24
---

# クライアントとPCのセットアップ

Perpetuum クライアントを実行するための実践的な注意事項です。

## まずルールについて

マルチボクシング（複数のクライアントで複数のキャラクターを操作すること）は**制限の範囲内**で許可されています。行う前に把握しておくべきフェアプレイのルールは以下の通りです：

- **自動化ソフトウェアや複数クライアント一括操作ツールの使用は禁止** — いかなる場合も不可。
- **同時にアクティブにできるアカウントは最大5つまで。**
- 偽造、無効、または連絡不能なメールアドレスで登録されたアカウントは不可 — 自身が所有するメールアドレスである必要があります。

違反した場合は、警告なしで即座に永久BANとなる可能性があります。

## Windows: 複数クライアントの起動

1. Perpetuum の Steam クライアントをインストールします。
2. ゲームフォルダー内に内容が `223410` である `steam_appid.txt` が存在することを確認します。
3. 追加するクライアントの数だけ、`Perpetuum` フォルダー全体をコピーします。
4. 各コピー内の `Perpetuum.exe` を実行します（任意で、非Steamゲームとして各コピーをSteamに追加することも可能です）。

**ディスク容量の節約:** `Layers.gbf` と `Perpetuum.gbf` はファイルサイズが大きく、すべてのコピーで同一の内容です。これらをシンボリックリンク（`mklink`）またはショートカットにすることで、ストレージの消費を1つ分に抑えられます。

## Linux: 複数クライアントの起動

各クライアントのコピーには**異なるバージョンのProton**が必要になります。そうしないと起動しません：

1. 通常どおりSteamとPerpetuumをインストールし、`steam_appid.txt`（`223410`）を確認します。
2. クライアントごとに `Perpetuum` フォルダーをコピーします。
3. Steamにログインした状態で、最近のProtonバージョンをいくつかインストールします（Steam経由、手動、またはGloriousEggrollビルド）。
4. 各コピーの `Perpetuum.exe` を指す非SteamゲームとしてSteamに追加します。
5. 各コピーの起動オプションで、それぞれ**異なるProtonバージョン**を強制適用します。
6. まず本来のSteamアプリを起動し、その後各コピーを起動します。

トラブルシューティング:

- Protonバージョンを選択しただけではインストールされ**ません** — 選択した状態でゲームを一度起動する必要があります。
- 本来のSteamアプリが起動しない場合は、まずセーフモードで起動してみてください。
- Proton 5.0以降、DirectX 9/12のエミュレーションは**Vulkan**上で動作します。Vulkan対応のGPUをお持ちでない場合は、各コピーの起動オプションに `PROTON_USE_WINED3D=1 %command%` を追加してください。
- 赤い警告が表示された空のテキストボックスが出る場合: `libfreetype6:i386` をインストールしてください（Debian/Ubuntu系ディストリビューション）。

## UIスケーリング

クライアントは固定ピクセルUIを使用しており、動的なスケーリング機能はありません。回避策は以下の通りです：

- **低解像度でのフルスクリーン** — ディスプレイよりも低い解像度でフルスクリーン表示にし、画面全体にUIを引き伸ばします（ウィンドウモードおよびボーダーレスモードは常にネイティブ解像度を使用します）。ディスプレイ自体の解像度を下げることでも同様の効果が得られます。
- **UIスケーラーアプリ** — 例：Lossless Scaling（Steam、Windows）。クライアントを基本サイズでウィンドウモード起動し、スケーラー側で好みのスケーリング比率を設定した上でスケーリングを有効化し、クライアントウィンドウにフォーカスします。拡大による滑らかさと文字の鮮明さのトレードオフが発生します。
- **OSの拡大鏡** — たまに文字を細かく読みたい場合は、Windowsの「拡大鏡」（または同等のOS機能）を使用します。

## 管理者権限なしでの起動

1. Steamフォルダーからクライアントファイルを書き込み可能な場所にコピーします。
2. その場所に、`cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"` と記述した `Perpetuum.bat` を作成します。
3. そのバッチファイルから起動します。

<!--
Developer notes: rewritten 2026 in original prose. An earlier version was adapted from the
Open Perpetuum community wiki (perpetuum.miraheze.org: Multi-Boxing, Linux
Setup, Client UI Scaling, Launching without Admin Rights); that text was
fully replaced, not reused. These are client-side procedures for the retail Steam client build;
nothing here is verifiable from this server's backend, and no server feature is
claimed. The Reshader (graphics mod) was intentionally left out: it targets the
retail client build and is not an OPP-server feature.
-->