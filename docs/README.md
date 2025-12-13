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
- **刻晴交互「璃月计划」**：两幕事件 + 一次性解锁（按钮置灰、防连点锁）
- **角色身份标准化**：统一兜底 dynasty/estate，避免“抽出来变贵族/宗族缺失/统治者被拖回本国”

---

## 目录说明

### `docs/spec/` - 规范与标准

这里写的是“**当前必须遵守的事实**”。实现代码应与 Spec 一致；若发现 Spec 与代码不一致，以 **base game + 本项目已跑通实现** 为准，并同步修正文档。

### `docs/design/` - 设计与分析

这里写的是“**为什么这么做 / 将来怎么做**”。当设计最终落地，应把结论整理进 `docs/spec/`。

### `docs/archive/` - 归档与历史

过时草案、旧 Bug 记录、弃用方案等，只用于考古，不作为开发依据。

---

## 常见任务入口

- 添加新角色：`docs/spec/spec_workflow_add_character.md`
- 七国系统扩展（添加新国家）：`docs/spec/spec_genshin_nations.md`
- Scope 规范与踩坑：`docs/spec/spec_scope_management.md`
- 调试与日志定位：`docs/spec/spec_debugging.md`

---

## 文档维护公约（强制）

1. **Code + Docs in Sync**：任何核心机制变更必须在同一次提交中更新对应 Spec。
2. **权威性**：Design 与 Spec 冲突 → 以 Spec 为准；Spec 与代码冲突 → 先修代码/验证，再修 Spec。
3. **可验证**：每条关键结论尽量写清对应文件路径/关键变量/关键 effect，方便回查与复用。
