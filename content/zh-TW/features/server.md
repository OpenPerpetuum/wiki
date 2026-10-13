---
title: "伺服器與參考資料"
description: "伺服器資訊、最高分數、參考資料下載，以及遊戲內商店。"
weight: 170
---

# 伺服器與參考資料

本頁涵蓋「元」系統：伺服器／系統資訊、最高分數、客戶端下載的參考資料，以及遊戲內商店。

> 介面位置請參閱[客戶端介面總覽](/zh-TW/features/ui/)。以下機制已與伺服器端確認。

## 伺服器與系統資訊

- **伺服器資訊** — 伺服器的一般狀態／資訊。
- **系統資訊** — 系統層級的詳細資訊。
- **伺服器關閉狀態** — 是否有排定的維護關閉生效中（對玩家而言為唯讀；關閉操作本身屬於管理員動作）。

## 最高分數

- **伺服器最高分數** — 整個伺服器上的最佳成績。
- **我的最高分數** — 你個人的最佳紀錄。

另請參閱[戰鬥](/zh-TW/features/combat/)，了解擊殺如何計入這些分數。

## 參考資料

客戶端會從伺服器下載靜態參考資料，以正確渲染內容。這些是**唯讀查詢**，而非玩家操作：

- **效果** — 效果定義。
- **列舉值** — 列舉型別的值。
- **實體預設值** — 實體的基礎定義。
- **彙總欄位** — 彙總後的欄位資料。
- **定義設定單位** — 每個定義的設定。
- **距離** — 客戶端使用的距離常數。
- **指令** — 已知指令清單（客戶端端的參考資料）。
- **裂隙** — 裂隙定義（另請參閱區域裂隙清單）。

你不需要「使用」這些資料；客戶端會按需自動擷取。它們在此列出是因為它們出現在指令清單中。

## 商店

遊戲內商店（付款整合）：

- **列出商品** — 查看有哪些商品在售。
- **開始交易** — 開始購買流程。
- **完成交易** — 完成購買。

商店購買屬於真實貨幣（或等值）交易；具體商品與定價屬於商店內容。

## 實務說明

- **參考資料為自動擷取** — 你無需手動觸發；它會保持客戶端與伺服器內容同步。
- **最高分數是你的榮耀** — 查看你的個人最佳紀錄和伺服器排行榜。
- **商店交易為兩步驟** — 先開始，再完成；在交易完成前，不要假設購買已結束。
- **關閉狀態僅供參考** — 它告訴你是否有維護窗口即將到來。

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