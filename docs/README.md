# EU5 Gacha Mod - 文档总导航

> 当前版本：**0.4.0**（见 [CHANGELOG.md](CHANGELOG.md)）

---

## 快速入口

- 版本变更：`docs/CHANGELOG.md`
- 规范（Current Truth）：`docs/spec/README.md`
- 设计（Why / Future）：`docs/design/README.md`
- 历史归档：`docs/archive/README.md`
- 引擎误区速查：`docs/幻觉表.md`

---

## 0.4 里程碑（摘要）

- **七国系统原型（璃月）**：静态 TAG `GL1` + 附庸类型 `gacha_archon_vassal` + 内阁行动「再造璃月」
- **璃月筹建局势**：局势 `gacha_liyue_reconstruction` + 必做「东莞独立市场」+ 投资加速 + 进度 100 自动建国
- **刻晴交互「璃月计划」**：两幕事件 + 一次性解锁（按钮置灰、防连点锁）
- **角色身份标准化**：统一兜底 dynasty/estate，避免“抽出来变贵族/宗族缺失/统治者被拖回本国”

> 文档提示：Phase 1-4 的进展要与 [spec/00_project_overview.md](spec/00_project_overview.md) 里的状态同步，`Version` / `Last Verified` 字段切勿遗漏。

---

## 目录说明

### `docs/spec/` - 规范与标准

这里写的是“**当前必须遵守的事实**”。实现代码应与 Spec 一致；若发现 Spec 与代码不一致，以 **base game + 本项目已跑通实现** 为准，并同步修正文档。

### `docs/design/` - 设计与分析

这里写的是“**为什么这么做 / 将来怎么做**”。当设计最终落地，应把结论整理进 `docs/spec/`。

### `docs/archive/` - 归档与历史

过时草案、旧 Bug 记录、弃用方案等，只用于考古，不作为开发依据。

## 文档治理

- **分类与流程**：`docs/spec/` 记录“Current Truth”，`docs/design/` 讨论构想，`docs/archive/` 留存历史。详细的文档编写/审核流程请参阅 [`docs/documentation_playbook.md`](documentation_playbook.md)。
- **同步与元数据**：任何代码变更都应配套更新文档，并在新文档开头写明 `Version`/`Last Verified`（参考 `docs/design/design_project_guidelines.md`）。
- **可追查性**：正文提及具体文件路径或 Spec ID（如 `in_game/events/gacha_events.txt`），方便其他开发者迅速准确地验对代码。

---

## 常见任务入口

- 添加新角色：`docs/spec/spec_workflow_add_character.md`
- 七国系统扩展（添加新国家）：`docs/spec/spec_genshin_nations.md`
- Scope 规范与踩坑：`docs/spec/spec_scope_management.md`
- 调试与日志定位：`docs/spec/spec_debugging.md`

---

## 文档维护公约（强制）

1. **Code + Docs in Sync**：任何核心机制的变更都要在同一次提交中更新 Spec，必要时同步拿掉原理设想，留下“已实现”片段。
2. **权威性**：Design 与 Spec 冲突 → 以 Spec 为准；Spec 与代码冲突 → 先修代码/验证，再修 Spec，并在 `docs/design/` 相应位置加上“已同步”注记。
3. **可验证**：每条结论写清涉及文件路径/变量/关键 effect，再附上对应 Spec ID 方便复查。
4. **审阅清单**：提交前自查 [`docs/documentation_playbook.md`](documentation_playbook.md) 中的核对项（Scope 清理、随机/Localization 限制等），避免文档残缺或误导。

---

## ⚠️ 原版覆盖（必须知悉）

本版本包含 **对原版 GUI 的覆盖补丁**（用于消除引擎日志刷屏，属于“Vanilla Patch”）：

- `in_game/gui/zz_gacha_messages_patch.gui`：覆盖原版 `template message_template`（源自 `in_game/gui/messages.gui`），为描述区补齐 `BlockList` 上下文以避免 `BlockList.GetBlocks` 报错。

> 兼容性提示：这会与其他“改 messages 弹窗”的 UI 模组产生冲突；如需要排查 UI 兼容性，可临时移除该文件验证。
