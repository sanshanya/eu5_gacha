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

*   **通用 Gacha 层**
    *   `common/scripted_effects/gacha_common_effects.txt`: 通用效果
    *   `common/scripted_effects/gacha_logic_effects.txt`: 核心概率逻辑
    *   `events/gacha_events.txt`: 抽卡界面与结果事件
*   **角色层 (以心海为例)**
    *   `events/gacha_xinhai_events.txt`: 角色专属事件
    *   `common/scripted_effects/xinhai_effects.txt`: 角色专属逻辑
    *   `localization/simp_chinese/gacha_xinhai_l_simp_chinese.yml`: 角色本地化
