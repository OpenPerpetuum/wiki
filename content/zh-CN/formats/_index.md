---
title: "格式"
description: "开发者参考：每个属性字段的存储、解析及服务器使用方式。"
weight: 60
---

# 格式

面向开发者的字段参考。每个页面追踪一个属性字段从其存储位置（数据库列、规则文件键或二进制层字节）到消费该字段的代码，并附有数值示例。面向玩家的"游戏中意味着什么"概述位于[功能](/zh-CN/features/)和[内容](/content/)部分——这里记录的是精确的类型、默认值、公式和代码路径。

| 页面 | 内容 |
|---|---|
| [植物字段](/zh-CN/formats/plant-fields/) | 植物规则文件格式（GenXY），每个规则字段的类型/默认值/消费者，生长状态机，验证检查 |
| [矿石字段](/zh-CN/formats/ore-fields/) | `minerals` + `mineralconfigs` 列，节点生成公式，节点生命周期与持久化，开采机制 |
| [可部署物字段](/zh-CN/formats/deployable-fields/) | 可部署物的识别方式，胶囊↔对象配对，以及驱动已放置对象的聚合字段 |
| [区域文件](/zh-CN/formats/zone-files/) | 二进制地形层文件：结构体布局、标志位、保存周期，以及存储在数据库中的内容 |

约定：

- **GenXY** 是用于规则文件和 `entitydefaults.options` 的配置序列化格式（标记字符参见 `GenxyToken.cs`；见[植物字段 → 文件格式](/zh-CN/formats/plant-fields/)）。
- 代码路径相对于 `src/`。
- 当某个值为**常量**（而非数据）时，会给出所在文件和常量名称。