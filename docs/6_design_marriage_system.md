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

### 3.1. Ruler Modifier (`common/static_modifiers/gacha_modifiers.txt`)
We create a **scaled modifier** that grants +1 `female_spouses` per marriage count:
```jomini
gacha_marriage_slot_modifier = {
    female_spouses = 1
}
```

### 3.2. Character Interaction (`common/character_interactions/gacha_interactions.txt`)
```jomini
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
        # 1. Increment marriage counter
        scope:actor.ruler = {
            if = {
                limit = { has_variable = gacha_marriage_count }
                change_variable = { name = gacha_marriage_count add = 1 }
            }
            else = {
                set_variable = { name = gacha_marriage_count value = 1 }
            }
            
            # 2. Add +1 spouse slot modifier
            add_character_modifier = {
                modifier = gacha_marriage_slot_modifier
                years = -1
                mode = add_and_stack
            }
        }
        
        # 3. Remove marriage block & marry
        scope:recipient = {
            remove_character_modifier = block_marriage
            marry_character = scope:actor.ruler
        }
        
        # 4. Flavor Event
        scope:actor = {
            trigger_event_non_silently = gacha_events.100
        }
    }
    
    ai_will_do = {
        base = 0  # AI never uses this
    }
}
```

### 3.3. Marriage Event (`events/gacha_events.txt`)
```jomini
gacha_events.100 = {
    type = country_event
    title = gacha_marriage_event_title
    desc = gacha_marriage_event_desc
    
    option = {
        name = gacha_marriage_event_accept
        # Optional: Add prestige/legitimacy bonus
        add_prestige = 100
    }
}
```

## 4. Workflow
1.  **Define Modifier**: Add `gacha_marriage_slot_modifier` to `main_menu/common/static_modifiers/gacha_modifiers.txt`.
2.  **Define Interaction**: Create `gacha_marry_interaction` in `in_game/common/character_interactions/gacha_interactions.txt`.
3.  **Create Event**: Add `gacha_events.100` to `events/gacha_events.txt`.
4.  **Localization**: Add text for the interaction and event in `localization/simp_chinese/`.

## 5. Edge Cases
*   **Ruler Death**: The `gacha_marriage_count` is stored on the ruler, so it will reset when a new ruler inherits. This is intentional (each ruler gets their own 3 marriages).
*   **Divorce**: If a marriage ends (rare in EU5), the slot is **not** recovered. This prevents exploit loops.
