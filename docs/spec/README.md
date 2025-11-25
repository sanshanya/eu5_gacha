# Specifications & Standards (规范与标准)

> [!IMPORTANT]
> **Current Truth (当前真相)**
> 
> 本目录下的文档代表项目**当前必须遵守的事实和标准**。
> 这里的每一个机制描述都应与游戏内的实际代码行为保持一致。

## 维护规则
1. **同步更新**：当代码逻辑发生变更时，**必须**同步更新对应的 Spec 文档。
2. **权威性**：如果 Design 文档与 Spec 文档冲突，以 Spec 为准。
3. **新功能**：新功能落地后，其最终方案应从 Design 目录迁移或整理至此。

## ⚠️ 维护公约 (Maintenance Pact)

# Specifications & Standards (规范与标准)

> [!IMPORTANT]
> **Current Truth (当前真相)**
> 
> 本目录下的文档代表项目**当前必须遵守的事实和标准**。
> 这里的每一个机制描述都应与游戏内的实际代码行为保持一致。

## 维护规则
1. **同步更新**：当代码逻辑发生变更时，**必须**同步更新对应的 Spec 文档。
2. **权威性**：如果 Design 文档与 Spec 文档冲突，以 Spec 为准。
3. **新功能**：新功能落地后，其最终方案应从 Design 目录迁移或整理至此。

## ⚠️ 维护公约 (Maintenance Pact)

> **Any change to core systems (Gacha, character workflow, scope conventions) must be reflected in the corresponding `spec_*.md` file in the same PR.**
> 
> (任何对核心机制的修改，必须在同一个 PR 中同步更新对应的 Spec 文档。)

## 文档索引
- [**00_project_overview.md**](00_project_overview.md): 项目总览与索引。
- [**spec_engine_basics.md**](spec_engine_basics.md): 引擎底层事实与验证行为(Modifiers, Script Values, Scopes, Effects)。
- [**spec_gacha_system.md**](spec_gacha_system.md): 抽卡系统核心机制(概率、保底、奖池)。
- [**spec_scope_management.md**](spec_scope_management.md): 脚本作用域管理与编码规范。
- [**spec_workflow_add_character.md**](spec_workflow_add_character.md): 添加新角色的标准工作流。
- [**spec_debugging.md**](spec_debugging.md): 调试工具、Console命令与常见问题解决。


记得时刻查看"C:\Users\sansm\OneDrive\文档\Paradox Interactive\Europa Universalis V\logs\game.log" 来获取最新错误信息

已知  不存在 [21:17:24][pdx_persistent_reader.cpp:289]: Error: "Unexpected token: is_triggered_only, near line: 18" in file: "events/gacha_xinhai_events.txt" near line: 18

已知需要用utf8-bom [21:17:22][lexer.cpp:286]: File 'common/static_modifiers/gacha_klee_modifiers.txt' should be in utf8-bom encoding (will try to use it anyways)