# Project Overview: EU5 Gacha Mod

## 1. 核心理念 (Core Concept)

**主题**：抽卡 + 陪伴
**定位**：轻量级陪伴型扩展，不全面接管游戏机制。
**体验**：
1.  **即时反馈**：消耗金币 -> 祈愿 -> 出货的快感。
2.  **长线陪伴**：角色作为廷臣/将领提供 Buff，并通过周期性剧情事件与玩家互动。

## 2. 核心循环 (Core Loop)

1.  **积累资源**：正常游玩 EU5，攒钱。
2.  **祈愿 (Gacha)**：通过决议/按钮进入祈愿池。
3.  **角色登场**：获得角色，触发登场剧情，获得强力 Trait/Modifier。
4.  **日常互动**：触发“锦囊妙计”或“日常闲聊”事件。
5.  **重复获取**：再次抽到相同角色 -> 转化为“命之座”或资源。

## 3. 开发阶段 (Phasing)

*   **Phase 1 (Current)**：**架构搭建与心海 MVP**。
    *   跑通“交互 -> 抽卡池 -> 创角 -> 纸片人显示”全流程。
    *   实装心海的基础 Trait 和 Modifier。
*   **Phase 2**：**剧情与互动系统**。
    *   实装月度脉冲 (Pulse)，触发心海的建议事件。
    *   完善好感度/命之座的变量埋点。
*   **Phase 3**：**多角色扩展**。
    *   引入第二个角色（如雷神/神里），验证 Gacha 池的多角色兼容性。
*   **Phase 4**：**深度系统**。
    *   好感度系统 UI、结婚/誓约系统、更多随机事件。

## 4. 文件结构 (File Structure)

### 通用 Gacha 层

| 路径 | 说明 | 状态 |
|------|------|------|
| `in_game/common/character_interactions/gacha_wish_interaction.txt` | 祈愿交互入口 | ✅ 正确 |
| `in_game/common/script_values/gacha_values.txt` | 抽卡概率计算 | ✅ 正确 |
| `in_game/common/scripted_effects/gacha_common_effects.txt` | 通用角色注册内核 | ✅ 正确 |
| `in_game/common/scripted_effects/gacha_logic_effects.txt` | 核心抽卡结果逻辑 | ✅ 正确 |
| `in_game/common/scripted_effects/gacha_constellation_effects.txt` | 命座效果通用逻辑 | ✅ 正确 |
| `in_game/events/gacha_events.txt` | 抽卡主界面与通用结果事件 | ✅ 正确 |

### 角色层 (心海)

| 路径 | 说明 | 状态 |
|------|------|------|
| `in_game/events/gacha_xinhai_events.txt` | 角色专属事件（初见/命座/满命） | ✅ 正确 |
| `in_game/common/scripted_effects/gacha_xinhai_effects.txt` | 角色专属效果 Wrapper | ✅ 正确 |
| `main_menu/localization/simp_chinese/eu_gacha_l_simp_chinese.yml` | 项目主本地化文件 | ✅ 正确 |

---

## 5. 快速导航 (Quick Navigation)

- **我要添加新角色** → [Workflow: Add Character](spec_workflow_add_character.md)
- **我要修改抽卡概率** → [Spec: Gacha System](spec_gacha_system.md)
- **我要写复杂脚本** → [Standard: Scope Management](spec_scope_management.md)
