# Design & Analysis (设计与分析)

> [!NOTE]
> **Concepts & Logic (构想与逻辑)**
> 
> 本目录包含功能构想、系统设计逻辑、可行性分析以及未来计划。这里是“为什么这么做”与“将来怎么做”的讨论场所，最终的可执行规范必须写在 `docs/spec/` 中。

## Purpose & usage

1. **非实施标准**：实现功能时，仅依照 `docs/spec/` 的“Current Truth”；Design 文档用来解释背后原理、权衡和演进路线（参见 `docs/spec/README.md` 的维护公约）。
2. **沉淀迁移**：当某个设计被采纳并完全落地后，请将核心实现细节同步写入对应的 Spec，Design 本身只保留 rationale、诱发条件与未解决的问题。
3. **版本与验证**：每篇设计文档都应保留 `Version`/`Last Verified` 元数据（例如 `design_project_guidelines.md`），便于追踪哪些内容还在筹划中、哪些已被淘汰。

## 文档索引

### 系统设计 (System Designs)
- [**design_gacha_design_decisions.md**](design_gacha_design_decisions.md): 抽卡系统设计决策与权衡 (Silent Core、概率设计、架构选择等)。
- [**design_story_system.md**](design_story_system.md): 剧情系统架构与触发逻辑设计。
- [**design_traits_and_modifiers.md**](design_traits_and_modifiers.md): 特质与修正系统的设计理念与推导过程。
- [**design_marriage_system.md**](design_marriage_system.md): 婚姻与亲密度系统设计草案。
- [**design_affinity_system.md**](design_affinity_system.md): 好感度系统深度设计。

### 可行性分析 (Feasibility Analysis)
- [**analysis_advanced_features.md**](analysis_advanced_features.md): 高级功能(如自定义附庸、Estate)的可行性分析。
- [**analysis_reference_snow.md**](analysis_reference_snow.md): Snow Project 参考 mod 深度分析。
- [**analysis_tech_wrappers.md**](analysis_tech_wrappers.md): 技术封装层分析与最佳实践。

### 工程规范与反思 (Engineering Guidelines & Lessons)
- [**design_project_guidelines.md**](design_project_guidelines.md): 项目开发圣经(编码规范、Git流程、文档规范)。
- [**design_engine_pitfalls.md**](design_engine_pitfalls.md): 引擎陷阱案例与规避方法(Random List、Scope 泄漏、模板参数等)。

## Keeping docs in sync

1. **从设计到规范闭环**：任何 Design 里的决策只在 Spec 中 final；实现后在 Spec 中补充对应段落，并在 Design 里加上 `Status` 注记（请参考 `docs/design/design_project_guidelines.md:15-18` 的同步公约）。
2. **保持元数据**：若某篇设计文档缺少 `Version`/`Last Verified`，优先补上，这样 reviewer 无需再去比对提交记录。
3. **串联依赖**：在 Design 里引用关键 Spec（如 `spec_gacha_system.md`、`spec_scope_management.md`），让人知道哪份文档支撑当前决策，避免重复讨论。
