# Character Story System Design (角色剧情系统设计)

## 1. 目标 (Objective)
建立一套**动态响应式**的剧情触发机制，让角色对玩家的国家行为（战争、扩张、灾难）做出反应。

## 2. 核心机制：On-Action 监听

利用 EU5 的 `on_actions` 系统监听游戏行为，而非随机 MTTH。

### 架构
*   **Listener**: `common/on_actions/gacha_story_actions.txt` (监听全局事件)
*   **Dispatcher**: `common/scripted_effects/gacha_story_dispatchers.txt` (分发给持有角色)
*   **Content**: `events/gacha_story_events.txt` (具体剧情)

## 3. 场景设计 (Scenarios)

### A. 故土重游 (Conquest)
*   **Trigger**: `on_province_owner_change`
*   **Condition**: 获得“稻妻”区域省份 + 拥有心海/雷神。
*   **Content**: 角色感叹故土变化，提供法理或行政 Buff。

### B. 瘟疫与治愈 (Plague)
*   **Trigger**: `on_monthly_pulse`
*   **Condition**: 首都遭受瘟疫 + 拥有心海。
*   **Content**: 心海举行仪式净化瘟疫，消耗精力换取稳定度。

### C. 战争与兵法 (War)
*   **Trigger**: `on_war_declared`
*   **Condition**: 拥有心海。
*   **Content**: 提供“锦囊妙计” (士气 Buff vs 后勤 Buff)。

## 4. 添加机制 (Workflow)

1.  **Define Effect**: 在角色文件中定义 `xinhai_on_war_effect`。
2.  **Register**: 在 `gacha_story_dispatchers.txt` 中添加该 effect。

```paradox
gacha_on_war_declared_dispatcher = {
    xinhai_on_war_declared_effect = yes
    raiden_on_war_declared_effect = yes
}
```
