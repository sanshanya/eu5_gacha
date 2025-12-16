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

### 2.4 Interaction / Event Option 安全模式

> **目标**：避免“鼠标悬浮就闪退（CTD）”这类由 Tooltip 预评估脚本引发的崩溃。

- **DO**: `character_interaction` 的 `effect` 里，凡是会触发事件/创建对象/改变量的逻辑，一律放进 `hidden_effect`。
- **DO**: 对“可重复点击”的交互添加锁变量（如 `gacha_event_lock`），并在事件 `after` 或 `on_game_start` 中兜底解锁。
- **DON'T**: 在交互/事件选项中直接写大量 effect（尤其包含 `create_character`、复杂随机、递归自调用）。

### 2.5 角色追踪（不要用 Character 全局列表）

- **DON'T**: 把 `Character` 作为 `global_variable_list` 的 target 长期存储（死亡后可能残留坏引用，触发 CTD）。
- **DO**: 用 `has_character_modifier` 做全局搜索（`random_country` → `random_character`），把角色识别“编码在 modifier 上”。
- **DO**: 需要“已召唤”状态时，用 `gacha_*_is_summoned` 这类全局变量；角色死亡时在 `on_character_death` 里同步清理。

### 2.6 禁止递归 effect（尤其是兜底递归）

- **DON'T**: `gacha_create_xxx_effect` 内部用“清旗标 + 自己调用自己”的递归兜底；在 Tooltip/预评估模式下很容易变成无限递归 → CTD。
- **DO**: 用两个 if 分支表达：
  - A：`has_global_variable` 时走“升级/复用”
  - B：`NOT has_global_variable` 时走“新建角色”
  - 当 A 找不到存活角色时，只需要 `remove_global_variable` 让 B 在同一条 effect 链继续执行。

### 2.7 尽量不覆盖原版（Vanilla Patch 规范）

> **目标**：降低与其他模组的冲突面，避免“改了原版导致全局副作用”。

- **DON'T**: 为了省事直接复制/覆盖整份原版文件（尤其是 `gui/`、`common/` 下的核心文件）。
- **DO**: 优先用“新增 key / 新文件 / 新 action / 新 subject_type”等方式实现需求。
- **DO**: 如果不得不覆盖原版（例如修复原版 UI 的日志刷屏），必须满足：
  - 在 `docs/` 明确标注：文件路径、覆盖目标、原因、兼容性风险、如何回滚
  - 覆盖内容尽量 **最小化**（只改必要字段/区块）

---

## 3. 禁止事项 / 红线 (Red Lines)

> [!CAUTION]
> 违反以下规则可能导致严重 Bug 或存档损坏。

1.  **禁止** 在 `random_list` 中使用 `value:script_value` 语法。
2.  **禁止** 在 `if/else` 分支中遗漏 Scope 清理（导致 Dynasty Bug）。
3.  **禁止** 尝试在 Country Event 的 `desc` 中动态显示角色名字。
4.  **禁止** 在 `scripted_effect` 模板参数中传递复杂对象（只能传 ID）。
5.  **禁止** 把 `Character` 存入 `global_variable_list` 作为长期数据结构。
6.  **禁止** 在 `scripted_effect` 中做递归自调用兜底。
7.  **禁止** 在交互/事件选项的非 `hidden_effect` 中执行“创建/随机/大量改变量”等复杂逻辑。

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
