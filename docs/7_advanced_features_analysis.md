# Snow Project Advanced Features Analysis

## 1. Custom Subject Type: `ls_snow_common_vassal`

### Overview
The reference mod creates a custom subject type that requires the overlord to have the `ls_snow_overlord_reform` government reform (granted when the ruler has the MASTER trait).

### Key Features

#### A. Visibility & Availability
```jomini
visible_through_diplomacy = {
    has_reform = government_reform:ls_snow_overlord_reform
}
```
Only players with the special government reform can create this subject type.

#### B. Subject Benefits (修正)
```jomini
subject_modifier = {
    loyalty_to_overlord = 100  # 永远忠诚
    discipline = 0.05
    global_defensive = 0.20
    global_manpower_modifier = 0.25
    tax_income_efficiency = 0.25
}
```
**Key Insight**: The `loyalty_to_overlord = 100` modifier ensures subjects NEVER rebel.

#### C. Overlord Benefits
```jomini
overlord_modifier = {
    dip = 1
    max_diplomats = 1
    global_manpower_modifier = 0.05
}
```

#### D. On Enable/Disable Effects
```jomini
on_enable = {
    save_scope_as = ls_snow_subject_scope
    add_reform = government_reform:ls_snow_wife_reform  # 附属国自动变为"妻子"政体
    scope:future_overlord = {
        trigger_event_non_silently = ls_snow_events.2
    }
}
```
When a country becomes this subject type, it automatically gets the "Wife Reform" government and triggers a special event.

#### E. Monthly Check
```jomini
on_monthly = {
    root.overlord = { ls_snow_check_subject_effect = yes }
}
```
Every month, the system checks if the subject's ruler still has the WAIFU trait. If not, the subject type reverts to a normal vassal.

### Applicability to Our Gacha Mod
**Not Directly Applicable**: Our mod focuses on character collection, not nation subjugation. However, we could create a "Gacha Nation" feature where C6 characters can be assigned as rulers of custom vassal states.

---

## 2. Custom Estate: `ls_snow_Heimdall_estate`

### Overview
A custom estate for storing "Waifu" characters with unique properties.

### Key Features
```jomini
ls_snow_Heimdall_estate = {
    pop_type = pop_type:ls_snow_Heimdall_estate
    character_estate = yes
    can_randomly_spawn_characters = no  # 防止随机角色生成
    can_generate_character_dynasties = no  # 防止生成新家族
}
```

**Key Insights**:
- `can_randomly_spawn_characters = no`: Prevents the engine from auto-spawning random characters into this estate
- `can_generate_character_dynasties = no`: Prevents the engine from creating new dynasties

### Applicability to Our Gacha Mod
**Highly Applicable**: We should create a custom `gacha_guild_estate` with these same properties to ensure:
1. Only Gacha characters are assigned to this estate
2. No random characters pollute our Gacha roster

---

##3. Government Reforms

### A. Overlord Reform (`ls_snow_overlord_reform`)
```jomini
ls_snow_overlord_reform = {
    potential = {
        ruler = { has_trait = ls_snow_MASTER_trait }
    }
    modifier = {
        female_spouses = 50  # 配偶槽位 +50
        allow_female_cabinet = yes
        allow_female_leaders = yes
        allow_female_generals = yes
        vassalization_speed = 0.5
        subject_annexation_speed = 1.0
    }
}
```

**Key Insight**: This is how the mod increases spouse limits—through a government reform tied to a ruler trait.

### B. Wife Reform (`ls_snow_wife_reform`)
```jomini
ls_snow_wife_reform = {
    potential = {
        ruler = { has_trait = ls_snow_WAIFU_trait }
    }
    modifier = {
        tolerance_of_different_culture = 1
        tolerance_of_different_religion = 1
        subject_integration_speed = 0.25
        allow_male_cabinet = no  # 禁止男性内阁
    }
}
```

This reform is automatically granted to subjects of the custom vassal type.

### Applicability to Our Gacha Mod
**Potentially Applicable**: Instead of increasing spouse limits via traits, we could create a government reform that players get when they perform their first Gacha pull. This reform would:
- Grant bonus spouse slots
- Unlock the Marriage interaction
- Provide other "Summoner" bonuses

---

## 4. Customizable Localization

The mod uses `customizable_localization` to change estate names based on culture:

```jomini
ls_snow_Heimdall_estate = {
    text = {
        localization_key = ls_snow_Heimdall_estate_noumin
        trigger = { culture.language = language:japanese_language }
    }
    text = {
        localization_key = ls_snow_Heimdall_estate_krestyanstvo
        trigger = { culture.language = language:russian_language }
    }
    # Default
    text = {
        localization_key = ls_snow_Heimdall_estate
    }
}
```

### Applicability to Our Gacha Mod
**Low Priority**: While cool for immersion, this is not critical for our Gacha system.

---

## 5. Summary & Recommendations

| Feature | Priority | Recommendation |
| :--- | :--- | :--- |
| **Custom Estate** | **High** | Create `gacha_guild_estate` with `can_randomly_spawn_characters = no` |
| **Government Reform** | **Medium** | Consider using a reform instead of a trait for spouse limit increases |
| **Subject Type** | **Low** | Not needed unless we add "Gacha Nations" feature |
| **Customizable Localization** | **Low** | Nice-to-have for polish |

---

## 6. Custom Culture & Religion Design (提瓦特世界观)

### Overview
To create an immersive "Golden Apple Archipelago" nation with Gacha characters, we need to establish custom cultures and religions based on the Genshin Impact (Teyvat) universe.

### A. Culture System

#### Culture Group: `teyvat_cultures`
```jomini
teyvat_cultures = {
    graphical_culture = european_gfx  # 或 asian_gfx
    
    # 蒙德文化 (Mondstadt - 风之国)
    mondstadt_culture = {
        primary_language = language:german_language
        color = { 115 194 155 }  # 青绿色 (风元素)
    }
    
    # 璃月文化 (Liyue - 岩之国)
    liyue_culture = {
        primary_language = language:chinese_language
        color = { 255 200 100 }  # 金色 (岩元素)
    }
    
    # 稻妻文化 (Inazuma - 雷之国)
    inazuma_culture = {
        primary_language = language:japanese_language
        color = { 153 102 204 }  # 紫色 (雷元素)
    }
    
    # 金苹果群岛 (Golden Apple Archipelago)
    golden_apple_culture = {
        primary_language = language:german_language
        color = { 255 215 0 }  # 金黄色
        heritage_from = mondstadt_culture  # 继承蒙德文化
    }
}
```

#### Character Assignment
```jomini
# In character creation:
create_character = {
    culture = culture:inazuma_culture  # 心海来自稻妻
    religion = religion:electro_archon_faith
}
```

### B. Religion System

#### Religion Group: `teyvat_faith`
```jomini
teyvat_faith = {
    graphical_culture = abrahamic_group_gfx
    
    # 风神信仰 (巴巴托斯)
    anemo_archon_faith = {
        color = { 115 194 155 }
        icon = 1
        country_modifiers = {
            tolerance_of_different_culture = 1
            state_movement_cost = -0.10
        }
    }
    
    # 岩神信仰 (摩拉克斯)
    geo_archon_faith = {
        color = { 255 200 100 }
        icon = 2
        country_modifiers = {
            global_gold_reserve_limit = 0.15
            global_tax_income_modifier = 0.10
        }
    }
    
    # 雷神信仰 (巴尔泽布)
    electro_archon_faith = {
        color = { 153 102 204 }
        icon = 3
        country_modifiers = {
            discipline = 0.05
            army_morale_modifier = 0.10
        }
    }
    
    # 水神信仰 (芙卡洛斯) - 金苹果群岛的主流信仰
    hydro_archon_faith = {
        color = { 100 149 237 }
        icon = 4
        country_modifiers = {
            naval_morale_modifier = 0.10
            ship_movement_cost = -0.15
        }
    }
}
```

### C. National Setup: Golden Apple Archipelago

#### Country Definition (`common/country_definitions/`)
```jomini
GAA = {  # Golden Apple Archipelago
    color = { 255 215 0 }
    
    country_type = recognized
    tier = kingdom
    
    cultures = { golden_apple_culture }
    religion = hydro_archon_faith
    
    capital = c:GAA_capital  # 首都省份
}
```

#### Historical Setup (`history/countries/`)
```jomini
c:GAA = {
    effect_starting_technology_tier = tech_tier_1
    
    add_culture_obsession = golden_apple_culture
    set_state_religion = religion:hydro_archon_faith
    
    # 初始政体
    add_reform = government_reform:gacha_summoner_reform
    
    # 初始统治者
    create_character = {
        first_name = "Alice"
        age = 35
        female = yes
        culture = culture:mondstadt_culture
        religion = religion:anemo_archon_faith
        adm = 85
        dip = 90
        mil = 75
        
        set_as_ruler = yes
    }
}
```

### D. Integration with Gacha System

#### Estate Assignment
All Gacha characters should be assigned to the custom `gacha_guild_estate`:
```jomini
scope:new_gacha_char = {
    move_country = c:GAA
    change_character_estate = estate_type:gacha_guild_estate
}
```

#### Cultural Compatibility
Characters retain their original culture but gain acceptance in GAA:
```jomini
gacha_summoner_reform = {
    modifier = {
        tolerance_of_different_culture = 3  # 高度文化包容
        tolerance_of_different_religion = 3  # 高度宗教包容
    }
}
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (High Priority)
1. **Custom Estate**: Create `gacha_guild_estate` with character spawn protection
2. **Government Reform**: Create `gacha_summoner_reform` for spouse limits and cultural tolerance

### Phase 2: World Building (Medium Priority)
3. **Culture Group**: Define `teyvat_cultures` with Mondstadt, Liyue, Inazuma, Golden Apple
4. **Religion Group**: Define `teyvat_faith` with Seven Archons religions
5. **Nation Setup**: Create Golden Apple Archipelago country with initial setup

### Phase 3: Integration (Low Priority)
6. **Character Updates**: Assign correct culture/religion to all Gacha characters
7. **Localization**: Add culture/religion names and flavor text
8. **Custom Subject Type**: Consider "Gacha Nation" vassal type (optional)

---

## 8. File Structure

```
in_game/
├── common/
│   ├── cultures/
│   │   └── gacha_cultures.txt          # 提瓦特文化组
│   ├── religions/
│   │   └── gacha_religions.txt         # 七神信仰
│   ├── estates/
│   │   └── gacha_estates.txt           # 抽卡公会阶层
│   ├── government_reforms/
│   │   └── gacha_reforms.txt           # 召唤师政体
│   └── country_definitions/
│       └── gacha_countries.txt         # GAA国家定义
├── history/
│   └── countries/
│       └── GAA.txt                     # GAA历史设置
main_menu/
└── localization/
    └── simp_chinese/
        ├── gacha_cultures_l_simp_chinese.yml
        └── gacha_religions_l_simp_chinese.yml
```
