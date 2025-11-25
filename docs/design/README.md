# Design & Analysis (设计与分析)

> [!NOTE]
> **Concepts & Logic (构想与逻辑)**
> 
> 本目录包含功能构想、系统设计逻辑、可行性分析以及未来计划。
> 这里的文档主要用于阐述"为什么这么做"以及"将来打算怎么做"。
# Design & Analysis (设计与分析)

> [!NOTE]
> **Concepts & Logic (构想与逻辑)**
> 
> 本目录包含功能构想、系统设计逻辑、可行性分析以及未来计划。
> 这里的文档主要用于阐述"为什么这么做"以及"将来打算怎么做"。

## 使用指南
1. **非实施标准**：实现功能时，**必须**制定或遵循 `spec/` 目录下的规范，而不是直接照搬 Design 文档（后者可能包含未定案的脑洞）。
2. **设计沉淀**：当一个设计被采纳并完全实现后，应将其中的"实现细节"整理到 Spec 中，本目录保留"设计理念"部分。

## 文档索引

### 系统设计 (System Designs)
- [**design_gacha_design_decisions.md**](design_gacha_design_decisions.md): 抽卡系统设计决策与权衡 (Silent Core、概率设计、架构选择等)。
- [**design_story_system.md**](design_story_system.md): 剧情系统架构与触发逻辑设计。
- [**design_traits_and_modifiers.md**](design_traits_and_modifiers.md): 特质与修正系统的设计理念与推导过程。
- [**design_marriage_system.md**](design_marriage_system.md): 婚姻与亲密度系统设计草案。
- [**design_affinity_system.md**](design_affinity_system.md): 好感度系统深度设计。

### 可行性分析 (Feasibility Analysis)
- [**analysis_advanced_features.md**](analysis_advanced_features.md): 高级功能(如自定义附庸、Estate)的可行性分析。
- [**analysis_reference_snow.md**](analysis_reference_snow.md): Snow Project参考mod深度分析。
- [**analysis_tech_wrappers.md**](analysis_tech_wrappers.md): 技术封装层分析与最佳实践。

### 工程规范与反思 (Engineering Guidelines & Lessons)
- [**design_project_guidelines.md**](design_project_guidelines.md): 项目开发圣经(编码规范、Git流程、文档规范)。
- [**design_engine_pitfalls.md**](design_engine_pitfalls.md): 引擎陷阱案例与规避方法(Random List、Scope泄漏、模板参数等)。
