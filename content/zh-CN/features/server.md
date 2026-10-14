---
title: "服务器与参考数据"
description: "服务器信息、排行榜、参考数据下载以及游戏内商店。"
weight: 170
---

# 服务器与参考数据

本页涵盖"元"系统：服务器/系统信息、排行榜、客户端下载的参考数据，以及游戏内商店。

> UI 位置参见[客户端 UI 概览](/zh-CN/features/ui/)。以下机制已对照服务器确认。

## 服务器与系统信息

- **服务器信息** — 服务器总体状态/信息。
- **系统信息** — 系统级别的详细信息。
- **服务器关闭状态** — 是否有计划中的关闭生效（对玩家为只读；关闭操作本身是管理员操作）。

## 排行榜

- **服务器排行榜** — 服务器上的最高成绩。
- **我的排行榜** — 你的个人最佳成绩。

另请参阅[战斗](/zh-CN/features/combat/)了解击杀如何计入排行榜。

## 参考数据

客户端从服务器下载静态参考数据以正确渲染内容。这些是**只读查询**，而非玩家操作：

- **效果** — 效果定义。
- **枚举** — 枚举值。
- **实体默认值** — 实体的基础定义。
- **聚合字段** — 聚合字段数据。
- **定义配置单元** — 按定义的配置。
- **距离** — 客户端使用的距离常量。
- **命令** — 已知命令列表（客户端侧参考）。
- **裂隙** — 裂隙定义（另请参阅区域裂隙列表）。

你不需要"使用"这些数据；客户端会按需获取。它们列在此处是因为它们出现在命令清单中。

## 商店

游戏内商店（支付集成）：

- **列出商品** — 查看在售商品。
- **开始交易** — 开始购买。
- **完成交易** — 完成购买。

商店购买是真实货币（或等价物）交易；具体商品和定价属于商店内容。

## 实用说明

- **参考数据自动获取** — 你无需手动触发；它保持客户端与服务器内容同步。
- **排行榜是你的荣誉** — 查看你的个人最佳成绩和服务器排行榜。
- **商店交易分两步** — 先开始，再完成；在完成之前不要假设购买已完成。
- **关闭状态仅供参考** — 它告诉你是否即将进入维护窗口。

<!-- TODO: 仅剩参考数据载荷列表（客户端侧）。
     已确认：此部署中真实货币商店未启用 — Steam
     交易命令（steamGetProducts / steamStartTransaction /
     steamFinishTransaction）在 Commands.cs 中已声明，但启动器中
     未注册任何处理器，且商店内容表（storeitems、storecategories）
     为空。
     开发者备注：ServerInfoGet.cs / SystemInfo.cs / ServerShutDownState.cs；
     GetHighScores.cs / GetMyHighScores.cs；GetEffects.cs / GetEnums.cs /
     GetEntityDefaults.cs / GetAggregateFields.cs / GetDefinitionConfigUnits.cs /
     GetDistances.cs / GetCommands.cs / GetRifts.cs；SteamGetProducts.cs /
     SteamStartTransaction.cs / SteamFinishTransaction.cs。 -->