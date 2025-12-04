# 天外之人阶层规范 (Gacha Estate Specification)

**Version**: 1.0  
**Last Updated**: 2025-12-04  
**Status**: 🟢 Production  

---

## 1. 概述

"天外之人"是为抽卡角色设计的自定义阶层，使其能够：
- 担任内阁职位
- 领导军队
- 在阶层面板中可见并拥有权力值

---

## 2. 核心文件结构

```
in_game/common/
├── estates/gacha_estate.txt              # 阶层定义
├── estate_privileges/gacha_estate.txt    # 2个特权
├── auto_modifiers/gacha_estate.txt       # 自动修正(权限基线)
├── pop_types/gacha_pop_type.txt          # Pop类型绑定
└── character_interactions/gacha_estate_privileges_interaction.txt

main_menu/common/
├── static_modifiers/gacha_modifiers.txt  # 国家级修正
├── modifier_type_definitions/gacha_modifier_types.txt
├── customizable_localization/gacha_estates.txt
└── modifier_icons/gacha_modifier_icons.txt
```

---

## 3. 阶层定义

**文件**: `in_game/common/estates/gacha_estate.txt`

```paradox
gacha_estate = {
    color = { 147 112 219 }  # Medium Purple
    power_per_pop = 0.05
    tax_per_pop = 0          # 不征税
    rival = 0
    alliance = 0
    bank = no
    characters_have_dynasty = sometimes
}
```

| 属性 | 值 | 说明 |
|:---|:---|:---|
| `color` | 紫色 RGB(147,112,219) | UI显示颜色 |
| `power_per_pop` | 0.05 | 每Pop贡献的权力 |
| `tax_per_pop` | 0 | 不参与常规税收 |
| `bank` | no | 不参与银行系统 |

---

## 4. 特权系统

**文件**: `in_game/common/estate_privileges/gacha_estate.txt`

### 4.1 内阁权限 (gacha_in_administration)

```paradox
gacha_in_administration = {
    estate = gacha_estate
    country_modifier = {
        gacha_estate_allowed_in_cabinet = yes
        gacha_estate_blocked_from_cabinet = no
        gacha_estate_target_satisfaction = medium_privilege_target_satisfaction
        global_gacha_estate_power = 0.1
    }
}
```

### 4.2 军职权限 (gacha_command_positions)

```paradox
gacha_command_positions = {
    estate = gacha_estate
    country_modifier = {
        gacha_estate_allowed_leading_military = yes
        gacha_estate_target_satisfaction = medium_privilege_target_satisfaction
        global_gacha_estate_power = 0.1
    }
}
```

---

## 5. 自动修正

**文件**: `in_game/common/auto_modifiers/gacha_estate.txt`

```paradox
gacha_estate_access = {
    gacha_estate_allowed_in_cabinet = yes
    gacha_estate_allowed_leading_military = yes
    gacha_estate_blocked_from_cabinet = no
    gacha_estate_target_satisfaction = medium_permanent_target_satisfaction
    global_gacha_estate_power = 5.0  # 基础权力保证面板可见
}
```

---

## 6. 国家级整合修正

**文件**: `main_menu/common/static_modifiers/gacha_modifiers.txt`

```paradox
gacha_estate_integration_modifier = {
    game_data = { category = country decaying = no }
    gacha_estate_allowed_in_cabinet = yes
    gacha_estate_allowed_leading_military = yes
    gacha_estate_target_satisfaction = medium_permanent_target_satisfaction
    gacha_estate_blocked_from_cabinet = no
    global_gacha_estate_power = 5.0
}
```

---

## 7. 角色分配流程

### 7.1 自动分配

角色创建后通过 `gacha_register_new_character` 自动分配：

```paradox
# gacha_common_effects.txt
gacha_register_new_character = {
    ...
    gacha_assign_to_gacha_estate = yes
}

gacha_assign_to_gacha_estate = {
    if = { limit = { is_character = yes } }
    change_character_estate = estate_type:gacha_estate
}
```

### 7.2 游戏启动初始化

**文件**: `in_game/common/on_actions/gacha_on_actions.txt`

```paradox
on_game_start = {
    effect = {
        every_country = {
            if = { limit = { is_player = yes } }
            add_country_modifier = { 
                modifier = gacha_estate_integration_modifier 
                years = -1 
                mode = add_and_extend 
            }
            add_estate_privilege = { 
                estate = estate_type:gacha_estate 
                privilege = estate_privilege:gacha_in_administration 
            }
            add_estate_privilege = { 
                estate = estate_type:gacha_estate 
                privilege = estate_privilege:gacha_command_positions 
            }
        }
    }
}
```

---

## 8. 玩家交互

**文件**: `in_game/common/character_interactions/gacha_estate_privileges_interaction.txt`

玩家可通过"授予天外之人特权"交互按钮手动激活：
1. 添加 `gacha_estate_integration_modifier` 国家修正
2. 添加两个阶层特权
3. 确保阶层在面板中可见

---

## 9. 自定义修正类型

| 修正类型 | 用途 |
|:---|:---|
| `gacha_estate_allowed_in_cabinet` | 允许担任内阁 |
| `gacha_estate_allowed_leading_military` | 允许领兵 |
| `gacha_estate_blocked_from_cabinet` | 禁止担任内阁 |
| `gacha_estate_target_satisfaction` | 目标满意度 |
| `global_gacha_estate_power` | 阶层权力加成 |

---

## 10. 设计要点

1. **权力来源**: 需要实际Pop + 权力修正才能在面板显示
2. **双层放行**: 角色层(`force_allow_as_leader`) + 国家层(integration修正)
3. **UTF-8 BOM**: 所有自定义文件必须使用UTF-8 BOM编码
4. **图标占位**: 自定义修正类型需配套图标定义

---

## 11. 已知问题

- `goods_demand` 提示: Pop需求分类未完全识别
- `mipmap` 警告: 阶层图标缺少mipmaps

详见 [ESTATE_IMPLEMENTATION_REPORT.md](../ESTATE_IMPLEMENTATION_REPORT.md)
