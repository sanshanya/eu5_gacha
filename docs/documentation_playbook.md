# Documentation Playbook

> **Purpose**: 让所有文档变更遵循统一的节奏/质量标准，在亮点与更新点之间形成清晰的“前后链路”。

## 1. Scope & Intent

- **Spec** (`docs/spec/`): “Current Truth”，讲实装结果。代码变更必须以这里为准，用户、QA、reviewer 都从这里查状态。
- **Design** (`docs/design/`): 记录“为什么这么做”“哪些方向还没定”，留下 rationale、trade-offs 和下一步候选项。
- **Archive** (`docs/archive/`)：保存旧版草案、踩过的坑、被 replace 的方案。仅用于历史查证。

任何新文档都应该先判断它属于哪类，再按该类的语义组织内容（参考 [docs/spec/README.md](spec/README.md) 与 [docs/design/README.md](design/README.md)）。

## 2. Writing & Update Workflow

1. **先想清 scope**：如果涉及代码行为先询问“是否已有 spec 条目？”；若没有，请在 spec 里开一个 stub 。
2. **维护 metadata**：每篇文档开始附上 `Version`、`Last Verified`、`Status`（Draft / Active / Obsolete），参照 `docs/design/design_project_guidelines.md` 提到的格式。
3. **记录代码痕迹**：正文至少提一次关键文件路径（e.g. `in_game/common/scripted_effects/gacha_logic_effects.txt`），并在结尾补上“影响范围”段落。
4. **关联 Spec / Design**：若属于设计思考，说明“该内容最迟应该落地到哪个 spec”；若是 spec 内容，列出与设计决策的来源（可引用 `docs/design/design_gacha_design_decisions.md`、`docs/design/design_project_guidelines.md`）。
5. **归档/撤下**：当文档被重写或废弃，请在 `docs/archive/` 留下原件，并在原文首部加上“Replaced by xxx”说明。

## 3. Metadata & Status Guidance

- `Version`：用语义版本或日期（如 `Version: 1.2`）。
- `Last Verified`：写最新一次人工确认日期。文档审核/重新签到后更新此字段。
- `Status`：可选 Draft / Active / Passive / Obsolete，帮助 reader 了解是否可以直接引用。
- `Source Tags`：引用 `docs/design/design_project_guidelines.md` 中提到的 `[ENGINE]`、`[SAFEGUARD]`、`[STYLE]` 标签，说明结论来源。

## 4. Review Checklist

1. 核心机制文档是否在同一次提交中改了 Spec + 代码（如 `spec_gacha_system.md`）？
2. 是否明确列出相关 files/variables/effects，方便 QA 定位?
3. `Version` / `Last Verified` / `Status` 是否存在且合理？
4. 文中的逻辑是否引用了 `docs/design/design_engine_pitfalls.md`、`docs/design/analysis_tech_wrappers.md` 等钉子文（如果涉及 Scope、random、modifier 等敏感区域）？
5. 是否说明了下一步行动（例如“落地到 spec X” 或 “需在 phase Y 中完成”）？
6. 交互/事件/Scope 相关文档是否提到 `clear_saved_scope` / 交互锁 / 触发条件等防坑要点？
7. 是否附上 Localization/graphics/asset 说明（如有），并标注本地化路径。
8. 是否附上附加参考（spec/design/engine pitfall），便于 reviewer 进一步追查。

## 5. Ongoing Maintenance

- 每个 release 前回顾 `Version` / `Last Verified` 是否过期；过旧的文档请在 metadata 中改为 `Status: Obsolete` 并移动到 `docs/archive/` 。
- 代码重构后，重新走一次 checklist（point 4）确认文档反映了新结构。
- 文档也应该跟进 `docs/design/design_project_guidelines.md` 定义的 “Scope Management” 与 “RNG” 规范，以免误导新开发者。

## 6. References

- `docs/spec/README.md`： Current Truth 入口。
- `docs/design/README.md`：设计与分析的入口。
- `docs/design/design_project_guidelines.md`：编码 + 文档维护整体规范。
- `docs/design/design_engine_pitfalls.md`：常见坑位与禁区索引。
