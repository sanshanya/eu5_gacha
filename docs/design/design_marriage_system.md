# Gacha Marriage System Design

## 1. Objective
Allow players to marry **up to 3 Gacha characters** who have reached **Max Constellation (C6)**. This acts as the ultimate "Affinity" reward.

## 2. Core Mechanics

### A. Incremental Spouse Slot System
Unlike the reference mod's fixed bonus, we use a **dynamic counter** approach:
*   **Variable**: `gacha_marriage_count` (stored on the ruler)
*   **Mechanic**: Each time you marry a Gacha character, `gacha_marriage_count` increases by 1, which grants +1 `female_spouses`.
*   **Limit**: Maximum 3 Gacha marriages (`gacha_marriage_count < 3`).

### B. Marriage Unlock Condition
*   **Condition**: Character must be **C6** (`gacha_constellation_lvl >= 6`).
*   **Current State**: Gacha characters have `block_marriage` modifier by default.
*   **Action**: When the interaction is used, remove `block_marriage`, marry the ruler, and increment the counter.

## 3. Implementation Details

> [!WARNING]
> **Common Pitfall**: The `mode = add_and_stack` parameter does **NOT** exist in EU5. Valid modes are: `add`, `extend`, `replace`, and `add_and_extend` only.

### 3.1. Ruler Modifiers (`main_menu/common/static_modifiers/gacha_modifiers.txt`)

We create **three separate modifiers** instead of a single stackable one:

```paradox
# 结婚槽位修正
gacha_marriage_slot_1_modifier = {
    game_data = { category = character }
    female_spouses = 1
}

gacha_marriage_slot_2_modifier = {
    game_data = { category = character }
    female_spouses = 2
}

gacha_marriage_slot_3_modifier = {
    game_data = { category = character }
    female_spouses = 3
}
```

> [!IMPORTANT]
> **Why Three Separate Modifiers?**
> 
> Since there is no "stackable modifier" system in EU5, we use three independent modifiers that provide different amounts of spouse slots. The interaction logic will **remove all old modifiers** and **apply the correct one** based on the marriage count.

### 3.2. Character Interaction (`in_game/common/character_interactions/gacha_interactions.txt`)

```paradox
gacha_marry_interaction = {
    category = CATEGORY_DYNASTIC_ACTIONS
    
    potential = {
        scope:actor = {
            is_player = yes  # Only for players
        }
    }
    
    allow = {
        scope:actor.ruler = {
            # Check marriage count limit
            trigger_if = {
                limit = { has_variable = gacha_marriage_count }
                var:gacha_marriage_count < 3
            }
            trigger_else = {
                always = yes  # First marriage
            }
        }
        
        scope:recipient = {
            # Must be a Gacha Character with C6
            has_variable = gacha_constellation_lvl
            var:gacha_constellation_lvl >= 6
            
            # Must not be married
            is_married = no
            is_alive = yes
        }
    }
    
    effect = {
        # 1. 在统治者身上更新结婚计数
        scope:actor.ruler = {
            if = {
                limit = { has_variable = gacha_marriage_count }
                change_variable = { name = gacha_marriage_count add = 1 }
            }
            else = {
                set_variable = { name = gacha_marriage_count value = 1 }
            }
            
            # 2. 移除所有旧的结婚槽位修正，防止错误叠加
            remove_character_modifier = gacha_marriage_slot_1_modifier
            remove_character_modifier = gacha_marriage_slot_2_modifier
            remove_character_modifier = gacha_marriage_slot_3_modifier

            # 3. 根据当前的结婚次数，添加正确的修正
            if = {
                limit = { var:gacha_marriage_count = 1 }
                add_character_modifier = { 
                    modifier = gacha_marriage_slot_1_modifier 
                    years = -1 
                }
            }
            else_if = {
                limit = { var:gacha_marriage_count = 2 }
                add_character_modifier = { 
                    modifier = gacha_marriage_slot_2_modifier 
                    years = -1 
                }
            }
            else_if = {
                limit = { var:gacha_marriage_count >= 3 }
                add_character_modifier = { 
                    modifier = gacha_marriage_slot_3_modifier 
                    years = -1 
                }
            }
        }
        
        # 4. 解除角色的婚姻锁定并结婚
        scope:recipient = {
            remove_character_modifier = block_marriage
            marry_character = scope:actor.ruler
        }
        
        # 5. (可选) 触发一个庆祝事件
        scope:actor = {
            trigger_event_non_silently = { id = gacha_events.100 }
        }
    }
    
    ai_will_do = {
        base = 0  # AI never uses this
    }
}
```

### 3.3. Marriage Event (`in_game/events/gacha_events.txt`)

```paradox
# ==========================================
# 100. Gacha 角色结婚庆祝事件
# ==========================================
gacha_events.100 = {
    type = country_event
    title = gacha_marriage_event_title
    desc = gacha_marriage_event_desc
    
    is_triggered_only = yes
    
    option = {
        name = gacha_marriage_event_accept
        # Optional: Add prestige/legitimacy bonus
        add_prestige = 100
        add_legitimacy = 10
    }
}
```

## 4. Workflow

1.  **Define Modifiers**: Add the three `gacha_marriage_slot_X_modifier` definitions to `main_menu/common/static_modifiers/gacha_modifiers.txt`.
2.  **Define Interaction**: Create `gacha_marry_interaction` in `in_game/common/character_interactions/gacha_interactions.txt`.
3.  **Create Event**: Add `gacha_events.100` to `in_game/events/gacha_events.txt`.
4.  **Localization**: Add text for the interaction and event in `main_menu/localization/simp_chinese/eu_gacha_l_simp_chinese.yml`.

## 5. Edge Cases

*   **Ruler Death**: The `gacha_marriage_count` is stored on the ruler, so it will reset when a new ruler inherits. This is intentional (each ruler gets their own 3 marriages).
*   **Divorce**: If a marriage ends (rare in EU5), the slot is **not** recovered. This prevents exploit loops.
*   **Save Game Compatibility**: If you modify the system after marriages have been performed, you may need to manually clean up old modifiers using a migration event.

## 6. Technical Notes

### Why Not Use a Single Stackable Modifier?

The initial design attempted to use `mode = add_and_stack`, which **does not exist** in EU5's scripting system. This is a common cross-game knowledge contamination from other Paradox titles like Stellaris.

**Valid modes in EU5**:
- `add` - Adds the modifier (default)
- `extend` - Extends the duration if already present
- `replace` - Replaces existing instance
- `add_and_extend` - Adds a new instance and extends duration

**Our solution**: Use the "remove-all, then-apply-correct-one" pattern with three separate modifiers. While less elegant, it's 100% reliable and explicitly clear about the game state.
