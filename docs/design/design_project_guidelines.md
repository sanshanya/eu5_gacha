# Project Guidelines (Modding Bible)

- **Version**: 1.0
- **Last Verified**: 2025-11-25
- **Purpose**: 本项目的最高设计指引，汇总了所有官方约束、项目规范与最佳实践。

---

## 1. 总则 (General Principles)

### 1.1 引擎真相 (Engine Truth)
- 我们严格遵守 [Spec: Engine Basics](../spec/spec_engine_basics.md) 中定义的引擎行为。
- 遇到未知行为时，必须先验证并更新 Engine Basics，禁止基于猜测编写核心逻辑。

### 1.2 维护公约 (Maintenance Pact)
- **Code ↔ Spec**: 任何对核心机制（抽卡、工作流、Scope）的修改，必须在同一个 PR 中同步更新对应的 `spec_*.md`。
- **Source Tags**: 在文档中引用规则时，使用 `[ENGINE]`、`[SAFEGUARD]`、`[STYLE]` 标签明确来源。

---

## 2. 常用模式 (Common Patterns)

### 2.1 RNG (随机数生成)
- **禁止**: 依赖 `random_list` 权重逻辑进行核心判定
- **标准模式**: Silent内核计算 → 存变量 → 根据变量触发后续
- **参考**: [Spec: Gacha System](../spec/spec_gacha_system.md)

### 2.2 Scope Management
- **黄金法则**: 谁创建 `save_scope_as`，谁清理 `clear_saved_scope`
- **清理时机**: 同一Effect块结束前 或 触发UI事件前
- **参考**: [Spec: Scope Management](../spec/spec_scope_management.md)

### 2.3 Modifiers
- **命名**: 项目专属须以 `gacha_` 开头
- **类型**: `static_modifiers` (永久Buff) vs `character_modifier` (临时标记)

---

## 3. 禁止事项 / 红线 (Red Lines)

> [!CAUTION]
> 违反以下规则可能导致严重 Bug 或存档损坏。

1.  **禁止** 在 `random_list` 中使用 `value:script_value` 语法。
2.  **禁止** 在 `if/else` 分支中遗漏 Scope 清理（导致 Dynasty Bug）。
3.  **禁止** 尝试在 Country Event 的 `desc` 中动态显示角色名字。
4.  **禁止** 在 `scripted_effect` 模板参数中传递复杂对象（只能传 ID）。

*详见 [Design: Engine Pitfalls](design_engine_pitfalls.md) 获取完整反例集。*

---

## 4. 参考索引 (Reference Index)

| 类别 | 文档 | 说明 |
| :--- | :--- | :--- |
| **真理层** | [Spec: Engine Basics](../spec/spec_engine_basics.md) | 官方 Wiki 与实测结论 |
| **规范层** | [Spec: Gacha System](../spec/spec_gacha_system.md) | 抽卡系统核心规范 |
| **规范层** | [Spec: Scope Management](../spec/spec_scope_management.md) | 作用域管理规范 |
| **反例层** | [Design: Engine Pitfalls](design_engine_pitfalls.md) | 历史错误与避坑指南 |
| **工作流** | [Workflow: Add Character](../spec/spec_workflow_add_character.md) | 添加新角色操作手册 |
