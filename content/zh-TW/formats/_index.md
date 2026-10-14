---
title: "格式"
description: "開發者參考：每個屬性欄位的儲存、解析與伺服器使用方式。"
weight: 60
---

# 格式

面向開發者的欄位參考。每個頁面追蹤一個屬性欄位，從其儲存位置（資料庫欄位、規則檔案金鑰或二進位層位元組）到消費該欄位的程式碼，並附上數值範例。面向玩家的「遊戲中代表什麼意義」摘要位於 [功能](/zh-TW/features/) 與 [內容](/content/) 章節——此處則記錄精確的型別、預設值、公式與程式碼路徑。

| 頁面 | 內容 |
|---|---|
| [植物欄位](/zh-TW/formats/plant-fields/) | 植物規則檔案格式（GenXY）、每個規則欄位的型別/預設值/消費者、成長狀態機、驗證檢查 |
| [礦物欄位](/zh-TW/formats/ore-fields/) | `minerals` + `mineralconfigs` 欄位、節點生成公式、節點生命週期與持久化、採集機制 |
| [可部署欄位](/zh-TW/formats/deployable-fields/) | 可部署物件的識別方式、膠囊↔物件配對、以及驅動已放置物件的聚合欄位 |
| [區域檔案](/zh-TW/formats/zone-files/) | 二進位地形層檔案：結構體佈局、旗標位元、儲存週期，以及改存於資料庫的內容 |

慣例：

- **GenXY** 是用於規則檔案與 `entitydefaults.options` 的設定序列化格式（token 字元定義見 `GenxyToken.cs`；詳見 [植物欄位 → 檔案格式](/zh-TW/formats/plant-fields/)）。
- 程式碼路徑相對於 `src/`。
- 當某個值為**常數**（而非資料）時，會標註其所在檔案與常數名稱。