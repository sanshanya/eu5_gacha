# EU5 Gacha Mod - 文档总导航

> **欢迎!** 这是 EU5 Gacha Mod 项目的文档中枢。

---

## 🚀 快速开始

### 我是新人,想了解这个项目

👉 请阅读 [**项目总览**](spec/00_project_overview.md)

### 我要开发新功能

👉 先看 [**规范目录 (Spec)**](spec/README.md),确保理解当前系统标准

### 我要讨论设计方案

👉 参考 [**设计目录 (Design)**](design/README.md),查看现有设计思路

### 我要查找历史资料

👉 浏览 [**归档目录 (Archive)**](archive/README.md)

---

## 📚 目录结构

### [spec/](spec/) - 规范与标准

> **Current Truth (当前真相)**

这里的文档代表项目**当前必须遵守**的事实和标准。所有实现代码都应与这些文档保持一致。

**核心文档**:

- [引擎底层事实](spec/spec_engine_basics.md) - Modifiers, Scopes, Effects等引擎机制
- [Gacha系统规范](spec/spec_gacha_system.md) - 抽卡概率、保底、奖池
- [Scope管理规范](spec/spec_scope_management.md) - 作用域编码标准
- [添加角色工作流](spec/spec_workflow_add_character.md) - 标准操作流程

---

### [design/](design/) - 设计与分析

> **Concepts & Logic (构想与逻辑)**

包含功能构想、系统设计、可行性分析及未来计划。这里解释"为什么这么做"和"将来打算怎么做"。

**分类**:

- **系统设计**: 剧情、婚姻、好感度等系统的架构设计
- **可行性分析**: 高级功能的技术可行性评估
- **工程规范**: 项目开发圣经与引擎陷阱指南

---

### [archive/](archive/) - 归档与历史

> **Historical Materials (历史材料)**

过时的设计草案、Bug修复日志、废弃的技术方案等。**仅供参考或考古,禁止作为开发依据**。

**重要日志**:

- RNG修复日志 (2025-11-23)
- Scope对齐报告 (2025-11-25)
- Dynasty Bug 教训

---

## ⚡ 常见任务快速链接

| 任务         | 文档                                                           |
| :----------- | :------------------------------------------------------------- |
| 添加新角色   | [Workflow: Add Character](spec/spec_workflow_add_character.md)    |
| 修改抽卡概率 | [Spec: Gacha System](spec/spec_gacha_system.md)                   |
| 编写脚本     | [Spec: Scope Management](spec/spec_scope_management.md)           |
| 理解引擎限制 | [Spec: Engine Basics](spec/spec_engine_basics.md)                 |
| 查看项目规范 | [Design: Project Guidelines](design/design_project_guidelines.md) |
| 避免常见错误 | [Design: Engine Pitfalls](design/design_engine_pitfalls.md)       |

---

## 📖 文档维护公约

> **Code + Docs in Sync**
>
> 任何对核心系统的修改,必须在同一个PR中同步更新对应的Spec文档。

1. **同步更新**: 代码逻辑变更 → 同步更新 Spec
2. **权威性**: Design 与 Spec 冲突时,以 Spec 为准
3. **新功能落地**: 从 Design 迁移最终方案至 Spec

---

## 🏗️ 项目当前阶段

**Phase 1 (Current)**: 架构搭建与心海 MVP
详见 [项目总览 - 开发阶段](spec/00_project_overview.md#3-开发阶段-phasing)

---

## 📞 其他资源

- **Bug追踪**: 见各 `archive/archive_*_log.md`
- **技术债务**: 见 `spec/spec_engine_basics.md` §Unverified
- **设计讨论**: 见 `design/` 各系统设计文档

文档需要更新的地方

查证幻觉！！！

查证幻觉！！！

查证幻觉！！！

角色唯一标识变为了has_character_modifier = gacha_XXXX_modifier
添加了通用trait gacha_core_trait 来给 2D头像识别

gold 不存在，gold用来判断钱

* **报错信息**: **Error: "Unexpected token: base, near line: 38" in file: "common/character_interactions/gacha_wish_interaction.txt"**
* **原因**: 在 **ai_will_do** **中使用了** **base = 0**。在 EU5 (Project Caesar) 的 Jomini 引擎中，权重的写法通常是直接赋值或使用 **value**。
* **修复**:
  打开 **in_game/common/character_interactions/gacha_wish_interaction.txt**，将：

  **code**Paradox

```
  ai_will_do = { base = 0 }
```

  **修改为：**

  **code**Paradox

```
  ai_will_do = { value = 0 }
```



* **报错信息** **:** **Error: add_trait effect [ target: field not set ] ... events/gacha_furina_events.txt:38**
* **原因**: 代码中写的是 **add_trait = gacha_furina_awakened_trait**。引擎试图把 **gacha_furina_awakened_trait** **解析为一个 Scope（作用域），但它找不到这个作用域，所以报错。**
* **修复**:
  必须显式告诉引擎这是一个 **Trait 类型**。
  在所有 Event 和 Effect 文件中（如 **gacha_furina_events.txt**, **gacha_constellation_effects.txt** **等），将：**

  **code**Paradox

```
  add_trait = gacha_furina_awakened_trait
```

  **修改为（加上** **trait:** **前缀）：**

  **code**Paradox

```
  add_trait = trait:gacha_furina_awakened_trait
```

  **(对所有角色的所有** **add_trait** **都需要这样做)**


character_event 不存在不存在不存在
