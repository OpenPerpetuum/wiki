---
title: "社交"
description: "通訊與聲望：郵件、聊天頻道、好友、聲望值、黃頁、新聞與投票。"
weight: 140
---

# 社交

本頁涵蓋通訊與聲望：**郵件**、**聊天頻道**、**好友**、**聲望值**，以及公開的**黃頁 / 新聞 / 投票**。

> 介面位置請參閱[客戶端介面總覽](/zh-TW/features/ui/)（左上角的**郵件**按鈕；聊天與社交各有獨立視窗）。以下機制已與伺服器端確認。

## 郵件

**個人郵件：**
- **列出**郵件、**開啟**訊息、**發送**郵件、**刪除**訊息。
- **未讀數量** — 你目前有多少未讀訊息。
- **資料夾** — 檢視**已使用的資料夾**、將訊息**移動**至資料夾、**刪除**資料夾。

**群發郵件（企業）：** 發送給整個企業：
- **發送**、**列出**、**開啟**、**刪除**、**未讀數量**。

## 聊天頻道

**頻道**是具名稱的聊天室：

- **建立**頻道、**加入**頻道、**離開**頻道、在頻道中**發言**。
- **列出**頻道（全部，或僅顯示自己的）。
- **管理**（作為頻道擁有者/幹部）：**踢出**、**封禁** / **解除封禁**、**設定成員角色**、**全域靜音**、檢視**已靜音** / **已封禁**的成員。
- **設定**：**設定密碼**、**設定主題**、**通知**偏好。

**私訊** — 角色之間的私人訊息。

## 好友

- **發送好友請求**、**回覆**請求、**確認**待處理的請求。
- **刪除**好友、**封鎖**角色。
- **列出**你的好友。

封鎖某角色後，該角色將無法與你交易或發送訊息（每個角色的交易封鎖請參閱[入門指南](/zh-TW/features/getting-started/)）。

## 聲望值（聲望）

**聲望值**是實體之間（角色、企業、聯盟）的數值聲望：

- **列出**你的聲望值、檢視**聲望歷史**。
- **設定聲望值** — 在允許的情況下，設定聲望值。限制條件：
  - **目標**必須是角色、（私人）企業或（私人）聯盟，
  - **來源**同樣必須是有效的實體，
  - 無法對自身設定聲望值。
- **預設聲望值** — 預設聯盟/企業的基準聲望值。

聲望值的範圍為 **-10 至 +10**（0 = 中立，為預設值；設定為 0 會清除該條目）。某實體的**聲望**是所有實體對其聲望值的總和。正向聲望值在特定場景中具有重要意義 — 例如在[入侵](/zh-TW/features/intrusion/)期間，與你互相關係聲望值 ≥ 10 的企業會被視為**盟友**，其 SAP 勝利不會損害你的站點。

聲望值會影響派系和其他玩家對你及你的企業的態度（請參閱[群組](/zh-TW/features/groups/)）。

## 黃頁

公開目錄（由企業經營的列表）：
- **取得**列表、**提交**列表、**刪除**列表、**搜尋**目錄。

## 新聞與投票

- **新聞** — 檢視**分類**與**新聞列表**；未讀項目的**未讀數量**。
- **投票** — **檢視**投票並**回答**。

## 實務要點

- **郵件與聊天的區別** — 郵件是持久且私密的；頻道是即時群組聊天室。
- **群發郵件是企業工具** — 幹部使用它向成員廣播。
- **聲望值是有方向的** — A 對 B 的聲望值與 B 對 A 的聲望值各自獨立，且隨你的企業而變。
- **封鎖是你的防線** — 封鎖垃圾訊息發送者或敵對交易者。
- **頻道可以鎖定** — 密碼和角色控制誰可以加入/發言。

<!-- TODO: only the mail/channel/social UI remains.
     Confirmed: standing range [-10,10], clamp in StandingHandler.SetStanding, 0 =
     neutral/clears the row (standings table empty on this deployment); reputation =
     aggregate toward a target (GetReputationFor); mission standing changes clamp to
     [0,10] (missionstandingchange/missionrequiredstanding); ally check = mutual
     standing >= 10 (intrusion).
     Developer notes: Mails/* (list/open/send/delete/folders, mass-mail variants);
     Channels/* (create/join/leave/talk, moderation, password/topic); Socials/* (friend
     request/reply/confirm/delete/block/list); Chat.cs; Standings/SetStanding.cs
     (entity-category + private-corp/alliance constraints, self-excluded),
     StandingHistory.cs, GetStandingForDefault*.cs; Corporations/YellowPages/*;
     GetNews.cs / NewsCategory.cs / FreshNewsCount.cs; PollGet.cs / PollAnswer.cs. -->