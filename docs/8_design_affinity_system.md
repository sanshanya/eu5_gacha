# Gacha Affinity System Design (好感度系统设计)

## 1. Overview
好感度系统让玩家通过与Gacha角色互动来提升关系，解锁专属事件和奖励。在C6时，最高好感度将解锁婚姻系统。

## 2. Core Mechanics

### A. Affinity Value (好感度数值)
每个Gacha角色拥有一个 `gacha_affinity_level` 变量（范围 0-100）。

```jomini
# 在角色注册时初始化
scope:new_gacha_char = {
    set_variable = { name = gacha_affinity_level value = 0 }
}
```

### B. Affinity Tiers (好感度等级)
| 等级 | 好感度范围 | 名称 | 解锁内容 |
| :--- | :--- | :--- | :--- |
| 0 | 0-19 | 陌生 (Stranger) | 基础对话 |
| 1 | 20-39 | 熟识 (Acquaintance) | 好感度事件 1 |
| 2 | 40-59 | 友善 (Friend) | 好感度事件 2 + 小礼物 |
| 3 | 60-79 | 信赖 (Trust) | 好感度事件 3 + 特殊修正 |
| 4 | 80-99 | 挚友 (Close Friend) | 好感度事件 4 + 强力修正 |
| 5 | 100 | 永恒之约 (Eternal Bond) | **婚姻解锁** (需C6) |

## 3. Gaining Affinity (好感度获取)

### A. Character Interactions (角色互动)
创建 `gacha_character_interaction`:

```jomini
gacha_talk_interaction = {
    category = CATEGORY_FRIENDLY_ACTIONS
    
    potential = {
        scope:recipient = { has_variable = gacha_affinity_level }
    }
    
    allow = {
        scope:recipient = {
            employer = scope:actor
            is_alive = yes
        }
    }
    
    cooldown = { months = 1 }  # 每月一次
    
    effect = {
        scope:recipient = {
            # +5 好感度
            change_variable = { name = gacha_affinity_level add = 5 }
            gacha_check_affinity_milestone_effect = yes
        }
        
        # 触发随机对话事件
        scope:actor = {
            trigger_event_non_silently = gacha_affinity_events.1
        }
    }
}
```

### B. Gift System (赠礼系统)
```jomini
gacha_gift_interaction = {
    category = CATEGORY_FRIENDLY_ACTIONS
    
    price = {
        gold = 100
        prestige = 10
    }
    
    effect = {
        scope:recipient = {
            # +10 好感度
            change_variable = { name = gacha_affinity_level add = 10 }
            gacha_check_affinity_milestone_effect = yes
        }
        
        # 触发感谢事件
        scope:actor = {
            trigger_event_non_silently = gacha_affinity_events.10
        }
    }
}
```

### C. Mission System (委托任务)
```jomini
gacha_mission_interaction = {
    category = CATEGORY_FRIENDLY_ACTIONS
    
    allow = {
        scope:recipient = {
            is_employed_as = advisor
            var:gacha_affinity_level >= 20
        }
    }
    
    cooldown = { months = 3 }
    
    effect = {
        # 临时离队执行任务
        scope:recipient = {
            add_character_modifier = {
                modifier = gacha_on_mission_modifier
                months = 3
            }
        }
        
        # 3个月后触发完成事件
        scope:actor = {
            trigger_event = {
                id = gacha_affinity_events.20
                months = 3
            }
        }
    }
}
```

### D. Event-Based Gains (事件获取)
某些事件选项可以增加好感度：
```jomini
option = {
    name = "与心海讨论治国之道"
    
    trigger = {
        any_in_list = {
            variable = gacha_obtained_characters
            has_trait = gacha_xinhai_origin_trait
            var:gacha_affinity_level >= 40
        }
    }
    
    # +15 好感度
    random_in_list = {
        variable = gacha_obtained_characters
        limit = { has_trait = gacha_xinhai_origin_trait }
        change_variable = { name = gacha_affinity_level add = 15 }
    }
}
```

## 4. Affinity Events (好感度事件)

### A. Milestone Check Effect
```jomini
gacha_check_affinity_milestone_effect = {
    # 达到 20 好感度
    if = {
        limit = {
            var:gacha_affinity_level >= 20
            NOT = { has_variable = gacha_affinity_tier_1_unlocked }
        }
        set_variable = { name = gacha_affinity_tier_1_unlocked value = 1 }
        
        # 触发角色专属事件
        if = {
            limit = { has_trait = gacha_xinhai_origin_trait }
            employer = { trigger_event_non_silently = gacha_xinhai_events.11 }
        }
    }
    
    # 达到 40 好感度
    if = {
        limit = {
            var:gacha_affinity_level >= 40
            NOT = { has_variable = gacha_affinity_tier_2_unlocked }
        }
        set_variable = { name = gacha_affinity_tier_2_unlocked value = 1 }
        
        if = {
            limit = { has_trait = gacha_xinhai_origin_trait }
            employer = { trigger_event_non_silently = gacha_xinhai_events.12 }
        }
    }
    
    # ... 以此类推到 100 好感度
}
```

### B. Event Structure

#### 好感度事件 1 (Lv. 20)
```jomini
gacha_xinhai_events.11 = {
    type = country_event
    title = gacha_xinhai_affinity_1_title
    desc = gacha_xinhai_affinity_1_desc
    
    option = {
        name = "倾听她的故事"
        # 可选：额外奖励
        add_adm_power = 50
    }
}
```

#### 好感度事件 2 (Lv. 40)
```jomini
gacha_xinhai_events.12 = {
    type = country_event
    title = gacha_xinhai_affinity_2_title
    desc = gacha_xinhai_affinity_2_desc
    
    option = {
        name = "陪她巡视海岛"
        
        # 解锁小礼物：特殊修正
        random_in_list = {
            variable = gacha_obtained_characters
            limit = { has_trait = gacha_xinhai_origin_trait }
            add_character_modifier = {
                modifier = gacha_xinhai_gift_tier_2
                years = -1
            }
        }
    }
}
```

#### 好感度事件 3 (Lv. 60)
深入角色背景故事，提供重要的叙事体验。

#### 好感度事件 4 (Lv. 80)
角色成长/转变事件，玩家的选择可能影响角色的发展方向。

#### 好感度事件 5 (Lv. 100 + C6)
解锁婚姻交互和最终奖励。

## 5. Affinity Rewards (好感度奖励)

### A. Character Modifiers
```jomini
# Tier 2 礼物（Lv. 40）
gacha_xinhai_gift_tier_2 = {
    # 在顾问位时
    if_advisor = {
        administrative_efficiency = 0.05
    }
}

# Tier 3 礼物（Lv. 60）
gacha_xinhai_gift_tier_3 = {
    if_advisor = {
        administrative_efficiency = 0.10
        prosperity_change_speed = 0.15
    }
}

# Tier 4 礼物（Lv. 80）
gacha_xinhai_gift_tier_4 = {
    if_advisor = {
        administrative_efficiency = 0.15
        prosperity_change_speed = 0.25
        state_maintenance_cost = -0.10
    }
}
```

### B. Country Modifiers
某些好感度等级可能解锁国家修正或特殊能力：
```jomini
# 当心海达到 Lv. 80 时
add_country_modifier = {
    modifier = blessing_of_watatsumi
    years = -1
}
```

## 6. Integration with Marriage System

### A. Marriage Interaction Update
```jomini
gacha_marry_interaction = {
    allow = {
        scope:recipient = {
            var:gacha_constellation_lvl >= 6
            var:gacha_affinity_level >= 100  # 新增好感度要求
            is_married = no
        }
    }
}
```

### B. Affinity Decay (可选)
如果角色长时间未互动，好感度可能缓慢下降：
```jomini
on_action = {
    on_yearly_pulse = {
        events = { gacha_affinity_decay_event }
    }
}

gacha_affinity_decay_event = {
    hidden = yes
    
    trigger = {
        any_in_list = {
            variable = gacha_obtained_characters
            var:gacha_affinity_level > 0
            NOT = { has_variable = gacha_affinity_interaction_this_year }
        }
    }
    
    immediate = {
        every_in_list = {
            variable = gacha_obtained_characters
            limit = {
                var:gacha_affinity_level > 0
                NOT = { has_variable = gacha_affinity_interaction_this_year }
            }
            # -5 好感度/年
            change_variable = { name = gacha_affinity_level add = -5 }
        }
        
        # 清除交互标记
        every_in_list = {
            variable = gacha_obtained_characters
            remove_variable = gacha_affinity_interaction_this_year
        }
    }
}
```

## 7. UI Integration

### A. Affinity Display
在角色面板显示好感度：
```
[好感度]: ❤❤❤❤❤ (80/100) - 挚友
```

### B. Interaction Buttons
- **对话** (Talk): +5 好感度, 1个月冷却
- **赠礼** (Gift): +10 好感度, 花费金币100
- **委托** (Mission): +20 好感度（完成后），3个月冷却
- **结婚** (Marry): 仅在 C6 + Lv.100 时可用

## 8. Localization Keys

```yaml
# main_menu/localization/simp_chinese/gacha_affinity_l_simp_chinese.yml
gacha_affinity_level_0: "陌生"
gacha_affinity_level_1: "熟识"
gacha_affinity_level_2: "友善"
gacha_affinity_level_3: "信赖"
gacha_affinity_level_4: "挚友"
gacha_affinity_level_5: "永恒之约"

gacha_talk_interaction: "与角色交谈"
gacha_gift_interaction: "赠送礼物"
gacha_mission_interaction: "委托任务"

gacha_xinhai_affinity_1_title: "海岛的巫女"
gacha_xinhai_affinity_1_desc: "心海向你讲述了海祇岛的故事..."
```

## 9. Implementation Checklist

- [ ] 定义好感度变量和等级阈值
- [ ] 创建角色互动 (对话、赠礼、委托)
- [ ] 编写好感度里程碑检测 effect
- [ ] 为每个角色创建 5 个好感度事件（Lv.20/40/60/80/100）
- [ ] 定义好感度奖励修正
- [ ] 更新婚姻系统以要求 Lv.100 好感度
- [ ] 添加 UI 显示和本地化
- [ ] (可选) 实现好感度衰减机制
