# Workflow: Add New Character (添加新角色工作流)

- **Version**: 2.0
- **Last Verified**: 2025-12-10
- **Relevant Files**:
  - `in_game/common/traits/`
  - `main_menu/common/static_modifiers/`
  - `main_menu/localization/simp_chinese/`
  - `in_game/common/scripted_effects/gacha_logic_effects.txt` (核心奖池逻辑)
  - `in_game/common/script_values/gacha_eu_values.txt` (奖池大小定义)

> **See Also**: 关于特质与修正的设计理念，请参阅 [Design: Traits & Modifiers](../design/design_traits_and_modifiers.md)。

本文档详细说明如何向卡池中添加一位新角色（以"雷电将军" `raiden` 为例）。

## 1. 文件清单 (Checklist)

你需要创建或修改以下文件：

| 类别 | 路径 | 说明 |
| :--- | :--- | :--- |
| **特质** | `in_game/common/traits/gacha_raiden_traits.txt` | 定义角色的核心特质与属性加成 |
| **修正** | `main_menu/common/static_modifiers/gacha_raiden_modifiers.txt` | 定义角色的永久修正 (可选) |
| **修正类型** | `main_menu/common/modifier_type_definitions/gacha_modifier_types.txt` | **[NEW]** 定义新的神之眼/命座修正类型 |
| **图标** | `main_menu/common/modifier_icons/gacha_modifier_icons.txt` | **[NEW]** 绑定修正类型的图标 |
| **特质图标** | `main_menu/gfx/interface/icons/traits/gacha_raiden_origin_trait.dds` | **[NEW]** 特质图标 (必须与特质同名) |
| **立绘** | `in_game/gfx/portraits/portrait_modifiers/gacha_raiden_portrait.txt` | 定义角色的 2D/3D 立绘绑定 |
| **配件** | `in_game/gfx/portraits/accessories/gacha_raiden_props.txt` | **[NEW]** 定义角色使用的配件 (Props) |
| **基因** | `in_game/common/genes/gacha_raiden_genes_special_accessories_misc.txt` | **[NEW]** 定义配件的基因绑定 |
| **资产** | `in_game/gfx/models/props/gacha_raiden/gacha_raiden_01.asset` | **[NEW]** 定义 3D 模型/贴图资产 |
| **触发器** | `in_game/common/scripted_triggers/gacha_trigger.txt` | **[NEW]** 更新立绘显示触发器 |
| **本地化** | `main_menu/localization/simp_chinese/eu_gacha_l_simp_chinese.yml` | **[UPDATE]** 添加名字、描述、事件文本 (不要新建文件) |
| **事件** | `in_game/events/gacha_raiden_events.txt` | 初次见面、命座提升、满命事件 |
| **逻辑** | `in_game/common/scripted_effects/gacha_raiden_effects.txt` | **新架构**：角色专属 Wrapper 文件 |
| **奖池** | `in_game/common/scripted_effects/gacha_logic_effects.txt` | **[UPDATE]** 将角色加入常驻池轮询逻辑 |
| **池大小** | `in_game/common/script_values/gacha_eu_values.txt` | **[UPDATE]** 更新常驻池总数 |

---

## 2. 详细步骤 (Step-by-Step)

### 步骤 1：定义特质 (Traits)

创建 `in_game/common/traits/gacha_raiden_traits.txt`。
这是角色最核心的属性来源。

```paradox
gacha_raiden_origin_trait = {
    category = ruler
    allow = { always = no } # 只通过脚本添加

    modifier = {
        # 在这里写角色的强力 Buff
        global_tax_modifier = 0.20      # 税收 +20%
        land_morale_modifier = 0.10     # 士气 +10%
    }
}

# C2 觉醒特质
gacha_raiden_awakened_trait = {
    category = ruler
    allow = { always = no }
    modifier = {
        discipline = 0.05
    }
}

# C4 超越特质
gacha_raiden_transcended_trait = {
    category = ruler
    allow = { always = no }
    modifier = {
        army_morale_modifier = 0.15
    }
}
```

### 步骤 2：配置立绘与资产 (Portraits & Assets)

这是一个多步骤过程，涉及 4 个文件。

#### 2.1 创建资产定义 (.asset)
创建 `in_game/gfx/models/props/gacha_raiden/gacha_raiden_01.asset`。
定义模型的 Mesh 和贴图路径。

```paradox
pdxmesh = {
	name = "gacha_raiden_01_mesh"
	file = "gacha_hm_prophet.mesh" # 使用通用平面 Mesh
	scale = 1
	meshsettings = {
		name = "prophet_shieldShape"
		index = 0
		texture_diffuse = "gacha_raiden_1024_0.dds" # 你的贴图文件名
		texture_specular = "gacha_raiden_1024_0.dds"
		shader = "portrait_attachment_alpha_to_coverage"
		shader_file = "gfx/hmportrait.shader"
	}
}
entity = {
	name = "gacha_raiden_01_entity"
	pdxmesh = "gacha_raiden_01_mesh"
}
```

#### 2.2 定义配件 (Props)
创建 `in_game/gfx/portraits/accessories/gacha_raiden_props.txt`。

```paradox
gacha_raiden_01 = {
  entity = {
    required_tags     = ""
    shared_pose_entity = head
    entity            = "gacha_raiden_01_entity" # 对应上面的 entity name
  }
}
```

#### 2.3 定义基因 (Genes)
创建 `in_game/common/genes/gacha_raiden_genes_special_accessories_misc.txt`。

```paradox
accessory_genes = {
  gacha_raiden_props_1 = {
    gene_raiden_blank_1 = { index = 0 }

    gacha_raiden_01 = {
      index = 1
      male   = { 1 = gacha_raiden_01 } # 对应 Props 里的名字
      female = male
      boy    = male
      girl   = male
      adolescent_boy  = male
      adolescent_girl = male
      infant = male
    }
  }
}
```

#### 2.4 绑定立绘 (Portrait Modifiers)
创建 `in_game/gfx/portraits/portrait_modifiers/gacha_raiden_portrait.txt`。

```paradox
gacha_raiden_portrait = {
  usage    = game
  priority = 100

  gacha_raiden_01 = {
    dna_modifiers = {
      accessory = {
        mode     = replace
        gene     = gacha_raiden_props_1      # 对应 Gene 里的名字
        template = gacha_raiden_01          # 对应 Props 里的名字
        value    = 0.5
      }
    }
    weight = {
      base = 0
      modifier = {
        add = 255
        has_trait = gacha_raiden_origin_trait
      }
    }
  }
}
```

#### 2.5 更新触发器 (Triggers)
修改 `in_game/common/scripted_triggers/gacha_trigger.txt`，将新角色的特质加入 `ls_gacha_portrait_trigger`。

```paradox
ls_gacha_portrait_trigger = {
  OR = {
    has_trait = gacha_xinhai_origin_trait
    # ... 其他角色 ...
    has_trait = gacha_raiden_origin_trait # 新增
  }
}
```

### 步骤 3：配置修正与图标 (Modifiers & Icons)

#### 3.1 定义修正类型
修改 `main_menu/common/modifier_type_definitions/gacha_modifier_types.txt`。
如果角色有新的神之眼类型（如雷元素），需要在此定义。

```paradox
gacha_electro_godeye={
  color=good
  boolean=yes
  game_data={
    category=character
  }
}
```

#### 3.2 绑定图标
修改 `main_menu/common/modifier_icons/gacha_modifier_icons.txt`。

```paradox
gacha_electro_godeye = {
  positive = "gfx/interface/icons/modifier_types/gacha_electro_godeye.dds"
}
```

#### 3.3 定义静态修正
创建 `main_menu/common/static_modifiers/gacha_raiden_modifiers.txt`。

```paradox
gacha_raiden_modifier = {
  game_data = { category = character decaying = no }
  gacha_core = yes
  gacha_electro_godeye = yes # 使用上面定义的类型
  icon = "gfx/interface/icons/modifier_types/intertwined_fate.dds" # 可选：指定图标
}
# ... 命座修正 ...
```

#### 3.4 制作特质图标 (Trait Icons)
**重要**：你需要为每个特质制作对应的图标，并放入 `main_menu/gfx/interface/icons/traits/` 目录。
文件名必须与特质名完全一致（例如 `gacha_raiden_origin_trait.dds`）。

### 步骤 4：本地化 (Localization)

**重要**：请直接修改 `main_menu/localization/simp_chinese/eu_gacha_l_simp_chinese.yml`，**不要**创建新的 `.yml` 文件。

```yaml
l_simp_chinese:
 # 名字
 gacha_first_name_raiden: "影"
 gacha_last_name_raiden: "雷电"
 
 # 特质
 gacha_raiden_origin_trait: "御建鸣神主尊"
 desc_gacha_raiden_origin_trait: "..."

 # 修正类型描述
 MODIFIER_TYPE_NAME_gacha_electro_godeye: "雷元素神之眼"
 MODIFIER_TYPE_DESC_gacha_electro_godeye: "「...」"
 
 # 静态修正描述
 STATIC_MODIFIER_NAME_gacha_raiden_modifier: "鸣神的加护"
 STATIC_MODIFIER_DESC_gacha_raiden_modifier: "..."

 # 事件标题
 gacha_raiden_events.1.title: "雷霆的威光"
```

### 步骤 5：创建事件 (Events)

创建 `in_game/events/gacha_raiden_events.txt`。
**注意**：V3 架构下必须使用 `country_event` 类型。

你需要至少 5 个事件：
1.  `.1`: 初次获得 (First Meeting)
2.  `.2`: 命座提升 (Constellation Up)
3.  `.4`: 满命 (Max Constellation)
4.  `.11`: 命座觉醒 (C2)
5.  `.12`: 命座超越 (C4)

```paradox
namespace = gacha_raiden_events

gacha_raiden_events.11 = {
    type = country_event  # 必须是 country_event
    title = gacha_raiden_events.11.title
    desc = gacha_raiden_events.11.desc
    
    immediate = {
        # 立绘绑定
        event_illustration_estate_effect = { 
            foreground = estate_type:nobles_estate 
            background = estate_type:nobles_estate 
        }
    }

    option = {
        name = gacha_raiden_events.11.a
        # 使用 saved scope 操作角色
        scope:gacha_last_pulled_char = {
            add_trait = trait:gacha_raiden_awakened_trait
        }
    }
}
```

### 步骤 6：编写逻辑 Wrapper (Scripted Effects)

创建 `in_game/common/scripted_effects/gacha_raiden_effects.txt`。
参考 `gacha_xinhai_effects.txt`，复制并修改为 `gacha_create_raiden_effect`。

**需要修改的关键点**：
1.  **全局变量锁**: `gacha_xinhai_is_summoned` -> `gacha_raiden_is_summoned`
2.  **特质检查**: `gacha_xinhai_origin_trait` -> `gacha_raiden_origin_trait`
3.  **事件 ID**: `gacha_xinhai_events.1/2/4/11/12` -> `gacha_raiden_events.1/2/4/11/12`
4.  **名字 Key**: `gacha_first_name_xinhai` -> `gacha_first_name_raiden`
5.  **注册调用**: `gacha_register_new_character = { who = raiden }`
6.  **数值**: 修改 `adm/dip/mil` 属性、文化、宗教

**注意事项**:
- 使用 `save_scope_as = existing_char` 和 `exists = scope:existing_char` 检查
- 确保调用 `save_scope_as = gacha_last_pulled_char` 以便 UI 正确显示

### 步骤 7：加入奖池 (Pools)

此步骤涉及两个文件的修改。

#### 7.1 更新奖池大小
打开 `in_game/common/script_values/gacha_eu_values.txt`，更新常驻池大小：

```paradox
# --- 常驻 5 星池大小 ---
gacha_pool_size_standard_5_sv = { value = 9 } # 原为 8，改为 9
```

#### 7.2 添加到轮询逻辑
打开 `in_game/common/scripted_effects/gacha_logic_effects.txt`，找到 `gacha_resolve_5star_and_save_scope`，在 `else` (歪常驻) 的分支中添加新角色：

```paradox
if = { limit = { local_var:gacha_standard_5_idx = 0 } gacha_create_keqing_effect = yes }
else_if = { limit = { local_var:gacha_standard_5_idx = 1 } gacha_create_raiden_effect = yes }
# ... 
else_if = { limit = { local_var:gacha_standard_5_idx = 7 } gacha_create_fischl_effect = yes }
else = { gacha_create_new_char_effect = yes } # Index 8 (你的新角色)
```

**重要**：不要使用 `random_list`！`gacha_eu_values.txt` 中的 `gacha_calc_standard_5_idx_sv` 会自动根据池子大小处理随机分布。

---

## 3. 常见问题 (FAQ)

*   **Q: 角色名字显示乱码？**
    *   A: 检查 `.yml` 文件是否以 UTF-8 BOM 格式保存。
*   **Q: 抽到了但是没弹窗？**
    *   A: 检查 namespace 是否定义，以及是否错误使用了 `character_event` (应为 `country_event`)。
*   **Q: 交互 scope:actor 报错？**
    *   A: 记住 Interaction 的 `scope:actor` 是 Country，不是 Character。
*   **Q: 角色属性没加上？**
    *   A: 检查 Effect 是否在 Character Scope 内执行 (`scope:char = { add_adm = 5 }`)。
