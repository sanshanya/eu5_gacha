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

*   **Phase 1 (Done)**：**抽卡系统 + 8角色 V3 工作流稳定**。
    *   跑通“交互 -> 抽卡池 -> 创角 -> 2D立绘显示 -> 命座升级/剧情链”全流程。
    *   8 位角色均可用（详见 [spec_character_roster.md](spec_character_roster.md)）。
*   **Phase 2 (Current)**：**七国系统原型 + 交互门控**。
    *   以璃月（`GL1`）为原型：角色交互解锁内阁行动，创建/修复附庸国。
    *   角色身份“收口”（dynasty/estate）以支持未来的王权/联姻/附庸玩法。
*   **Phase 3**：**七国扩展**。
    *   扩展到其他国家（蒙德/稻妻/须弥/枫丹/纳塔/至冬）与对应的角色入口。
*   **Phase 4**：**深度系统**。
    *   好感度系统落地（UI/触发/解锁），婚姻/誓约与更多长期事件。

## 4. 文件结构 (File Structure)

### 通用 Gacha 层

| 路径 | 说明 | 状态 |
|------|------|------|
| `in_game/common/character_interactions/gacha_wish_interaction.txt` | 祈愿交互入口（含防连点锁） | ✅ 正确 |
| `in_game/common/script_values/gacha_eu_values.txt` | 抽卡概率计算 | ✅ 正确 |
| `in_game/common/scripted_effects/gacha_common_effects.txt` | 通用角色注册内核 | ✅ 正确 |
| `in_game/common/scripted_effects/gacha_logic_effects.txt` | 核心抽卡结果逻辑 | ✅ 正确 |
| `in_game/common/scripted_effects/gacha_constellation_effects.txt` | 命座效果通用逻辑 | ✅ 正确 |
| `in_game/events/gacha_events.txt` | 抽卡主界面与通用结果事件 | ✅ 正确 |

### 角色层 (8 位角色)

| 路径 | 说明 | 状态 |
|------|------|------|
| `in_game/events/gacha_{char}_events.txt` | 角色事件链（初见/命座/C3剧情） | ✅ 正确 |
| `in_game/common/scripted_effects/gacha_{char}_effects.txt` | 角色 Wrapper（新建/重复抽取/命座路由） | ✅ 正确 |
| `main_menu/common/static_modifiers/gacha_{char}_modifiers.txt` | 角色数值（角色/国家修正） | ✅ 正确 |

### 七国层 (原型：璃月)

| 路径 | 说明 | 状态 |
|------|------|------|
| `in_game/setup/countries/gacha_seven_nations.txt` | 静态 TAG 定义（颜色/基础文化宗教） | ✅ 正确 |
| `in_game/common/subject_types/gacha_archon_vassal.txt` | 七国附庸类型 | ✅ 正确 |
| `in_game/common/character_interactions/gacha_keqing_liyue_plan_interaction.txt` | 刻晴专属「璃月计划」交互入口 | ✅ 正确 |
| `in_game/events/gacha_nation_events.txt` | 璃月计划（两幕）与建国通知事件 | ✅ 正确 |
| `in_game/common/cabinet_actions/gacha_nation_actions.txt` | 内阁行动：创建/修复璃月并设刻晴为统治者 | ✅ 正确 |
| `main_menu/common/static_modifiers/gacha_liyue_modifiers.txt` | 璃月国家修正（10年强力 + 常驻） | ✅ 正确 |
| `main_menu/common/flag_definitions/gacha_flag_definitions.txt` | 旗帜定义 | ✅ 正确 |
| `main_menu/common/coat_of_arms/coat_of_arms/gacha_coat_of_arms.txt` | CoA 定义 | ✅ 正确 |
| `main_menu/localization/*/gacha_country_names_l_*.yml` | 国家名/形容词本地化集中管理 | ✅ 正确 |

---

## 5. 快速导航 (Quick Navigation)

- **我要添加新角色** → [Workflow: Add Character](spec_workflow_add_character.md)
- **我要修改抽卡概率** → [Spec: Gacha System](spec_gacha_system.md)
- **我要写复杂脚本** → [Standard: Scope Management](spec_scope_management.md)
- **我要添加七国国家** → [Spec: Genshin Nations](spec_genshin_nations.md)
