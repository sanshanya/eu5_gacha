# Character Story System Design (角色剧情系统设计)

## 1. 目标 (Objective)
建立一套**动态响应式**的剧情触发机制，让角色对玩家的国家行为（战争、扩张、灾难）做出反应。

## 2. 核心机制：On-Action 监听

利用 EU5 的 `on_actions` 系统监听游戏行为，而非随机 MTTH。

### 架构

| 文件 | 作用 |
|------|------|
| `in_game/common/on_action/gacha_on_actions.txt` | **监听器 (Listener)**：注册游戏内的原生 on_action（如 `on_war_declared`），并调用我们的分发器。 |
| `in_game/common/scripted_effects/gacha_story_effects.txt` | **分发器 (Dispatcher)** 与 **内容 (Content)**：包含一个核心分发效果，以及各个角色对不同事件的响应逻辑。 |
| `in_game/events/gacha_story_events.txt` | **事件文件 (Events)**：存放由响应逻辑触发的具体剧情事件弹窗。 |

## 3. 场景设计 (Scenarios)

### A. 故土重游 (Conquest)
*   **Trigger**: `on_province_owner_change`
*   **Condition**: 获得"稻妻"区域省份 + 拥有心海/雷神。
*   **Content**: 角色感叹故土变化，提供法理或行政 Buff。

### B. 瘟疫与治愈 (Plague)
*   **Trigger**: `on_monthly_pulse`
*   **Condition**: 首都遭受瘟疫 + 拥有心海。
*   **Content**: 心海举行仪式净化瘟疫，消耗精力换取稳定度。

### C. 战争与兵法 (War)
*   **Trigger**: `on_war_declared`
*   **Condition**: 拥有心海。
*   **Content**: 提供"锦囊妙计" (士气 Buff vs 后勤 Buff)。

## 4. 实现工作流 (Implementation Workflow)

以 **"战争与兵法 (War)"** 场景为例，说明如何从零开始实现一个完整的剧情互动。

### 步骤 1: 创建监听器 (Listener)

在 `in_game/common/on_action/gacha_on_actions.txt` 中写入：

```paradox
# 当玩家宣战时触发
# root = 宣战的国家, scope:recipient = 被宣战的国家
on_war_declared = {
    on_actions = {
        gacha_on_war_declared_dispatcher_effect
    }
}
```

### 步骤 2: 创建分发器与角色响应逻辑 (Dispatcher & Logic)

在 `in_game/common/scripted_effects/gacha_story_effects.txt` 中写入：

```paradox
# ======================================================
# 宣战事件分发器
# ======================================================
gacha_on_war_declared_dispatcher_effect = {
    # 遍历全局角色列表中的每一个角色
    every_in_global_list = {
        variable = gacha_obtained_characters
        
        # 将当前遍历到的角色保存为 'story_character'
        save_scope_as = story_character

        # 在该角色身上执行她的专属响应逻辑
        # 引擎会自动根据角色的特质，执行匹配的那个 if 分支
        scope:story_character = {
            # --- 心海的响应 ---
            if = {
                limit = { has_trait = gacha_xinhai_origin_trait }
                
                # 调用心海的专属战争事件
                # 使用 root.root 来确保作用域回到最开始的国家
                root.root = { 
                    trigger_event_non_silently = { id = gacha_story_events.1 }
                }
            }
            # --- 雷电将军的响应 (未来添加) ---
            # else_if = {
            #     limit = { has_trait = gacha_raiden_origin_trait }
            #     root.root = { 
            #         trigger_event_non_silently = { id = gacha_story_events.2 }
            #     }
            # }
        }
    }
}
```

> [!IMPORTANT]
> **关键点**：这个分发器通过 `every_in_global_list` 遍历所有角色，并用 `if` 和 `else_if` 来精确调用每个角色自己的剧情，这才是可行的实现方式。

### 步骤 3: 创建剧情事件内容 (Event Content)

在 `in_game/events/gacha_story_events.txt` 中写入：

```paradox
namespace = gacha_story_events

# 心海的战争建议事件
gacha_story_events.1 = {
    type = country_event
    title = "军师的锦囊"
    desc = "战争的号角已经吹响。珊瑚宫心海步入殿前，向您呈上两份早已拟好的作战方略。\n\n"兵者，诡道也。根据敌我之势，妾身有二策可选，请定夺。""
    

    # 选项A: 奇袭
    option = {
        name = "采纳奇袭之策，鼓舞士气。"
        add_country_modifier = {
            modifier = gacha_xinhai_war_morale_buff # 临时士气Buff
            months = 12
        }
    }
    
    # 选项B: 稳进
    option = {
        name = "采纳稳进之策，保障后勤。"
        add_country_modifier = {
            modifier = gacha_xinhai_war_logistics_buff # 临时后勤Buff
            months = 12
        }
    }
}
```
