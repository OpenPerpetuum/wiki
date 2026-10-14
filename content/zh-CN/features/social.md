---
title: "社交"
description: "通信与声望：邮件、聊天频道、好友、声望、黄页、新闻和投票。"
weight: 140
---

# 社交

本页涵盖通信与声望：**邮件**、**聊天频道**、**好友**、**声望**，以及公开的**黄页 / 新闻 / 投票**。

> 界面位置参见[客户端界面概览](/zh-CN/features/ui/)（左上角的**邮件**按钮；聊天和社交有各自的窗口）。以下机制已对照服务器确认。

## 邮件

**个人邮件：**
- **列出**邮件、**打开**一条消息、**发送**邮件、**删除**一条消息。
- **新消息数** — 你有多少条未读消息。
- **文件夹** — 查看**已用文件夹**、将消息**移动**到文件夹、**删除**文件夹。

**群发邮件（公司）：** 发送给你整个公司：
- **发送**、**列出**、**打开**、**删除**、**新消息数**。

## 聊天频道

**频道**是命名的聊天室：

- **创建**频道、**加入**频道、**离开**频道、在频道中**发言**。
- **列出**频道（全部，或仅你自己的）。
- **管理**（作为频道所有者/官员）：**踢出**、**封禁** / **解封**、**设置成员角色**、**全局静音**、查看**已静音** / **已封禁**成员。
- **设置**：**设置密码**、**设置主题**、**通知**偏好。

**私聊** — 角色之间的私人消息。

## 好友

- **发送好友请求**、**回复**请求、**确认**待处理请求。
- **删除**好友、**屏蔽**角色。
- **列出**你的好友。

屏蔽某角色后，该角色将无法与你交易/发送消息（关于针对单个角色的交易屏蔽，参见[入门指南](/zh-CN/features/getting-started/)）。

## 声望

**声望**是实体（角色、公司、联盟）之间的数值化声誉：

- **列出**你的声望，查看**声望历史**。
- **设置声望** — 在允许的情况下，设置声望值。约束条件：
  - **目标**必须是角色、（私有）公司或（私有）联盟，
  - **来源**同样必须是有效实体，
  - 你不能为自己设置声望。
- **默认声望** — 默认联盟/公司的基准声望。

声望的取值范围为 **-10 到 +10**（0 = 中立，即默认值；设置为 0 会清除该条目）。某实体的**声誉**是所有实体对其声望的汇总。正面声望在特定场景中有实际意义 — 例如在[入侵](/zh-CN/features/intrusion/)期间，相互声望 ≥ 10 的公司被视为**盟友**，其 SAP 胜利不会损害你的站点。

声望会影响派系和其他玩家对你及你公司的态度（参见[群组](/zh-CN/features/groups/)）。

## 黄页

公开目录（公司发布的列表）：
- **获取**列表、**提交**列表、**删除**列表、**搜索**目录。

## 新闻与投票

- **新闻** — 查看**分类**和**新闻列表**；未读条目的**新消息数**。
- **投票** — **查看**投票并**作答**。

## 实用说明

- **邮件与聊天** — 邮件是持久且私密的；频道是实时群组房间。
- **群发邮件是公司工具** — 官员用它向成员广播。
- **声望是有方向的** — A 对 B 的声望与 B 对 A 的声望是独立的，且跟随你的公司。
- **屏蔽是你的盾牌** — 屏蔽垃圾信息发送者或敌对交易者。
- **频道可以锁定** — 密码和角色控制谁可以加入/发言。

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