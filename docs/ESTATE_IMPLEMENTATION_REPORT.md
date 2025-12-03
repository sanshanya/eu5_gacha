# EU5 自定义阶层（天外之人）实现纪要

## 1. 目标与现状
- **目标**：为抽卡角色提供独立阶层“天外之人”，可入内阁/领兵，并在阶层面板可见。
- **现状**：已通过修正 + 交互按钮落地，阶层 UI 可见（约 4% 权力，100K 人口）。仍有少量日志提示需后续收敛。

## 2. 主要改动清单
### 阶层定义与 Pop
- `in_game/common/estates/gacha_estate.txt`：最小化定义（颜色、power_per_pop、tax_per_pop、bank=no、characters_have_dynasty=sometimes），UTF-8 BOM。
- `in_game/common/pop_types/gacha_pop_type.txt`：定义 gacha Pop，禁迁徙/同化，映射到 `gacha_estate`。

### 权限与权力来源
- 自动修正：`in_game/common/auto_modifiers/gacha_estate.txt` → `gacha_estate_access` 允许入内阁/领兵，提供基础满意度与权力 (global_gacha_estate_power)。
- 阶层特权：`in_game/common/estate_privileges/gacha_estate.txt`
  - `gacha_in_administration`：内阁权限 + 满意度 + 少量 power。
  - `gacha_command_positions`：军职权限 + 满意度 + 少量 power。
- 国家修正：`main_menu/common/static_modifiers/gacha_modifiers.txt`
  - `gacha_estate_integration_modifier`：国家级允许入内阁/领兵，满意度，基础权力。
  - `gacha_core_modifier`：角色层放行（force_allow_as_leader / ignore_gender_block_cabinet / is_immortal）。

### 交互/入口
- `in_game/common/character_interactions/gacha_estate_privileges_interaction.txt`
  - 按钮“授予天外之人特权”：添加 `gacha_estate_integration_modifier`，并在首都添加少量 gacha Pop（确保阶层权力>0）。

### 类型与图标占位
- `main_menu/common/modifier_type_definitions/gacha_modifier_types.txt`：定义 `gacha_estate_*`、`global_gacha_estate_power` 等，并补占位类型（satisfaction/power/block_* 等）消除缺失报错。
- `main_menu/common/modifier_icons/gacha_modifier_icons.txt`：自定义与占位图标映射（复用劳工示例图标与通用图标）。

### 本地化
- `main_menu/localization/simp_chinese/eu_gacha_l_simp_chinese.yml`
  - 阶层、特权、交互、修正的中文键；`AUTO_MODIFIER_NAME_gacha_estate_access` 等占位名补全。
- `main_menu/common/customizable_localization/gacha_estates.txt`：绑定 `gacha_otherworldly_estate`（UTF-8 BOM）。

### 其他占位
- Goods 需求占位：`in_game/common/goods_demand/gacha_demand.txt` 与 `in_game/common/goods_demand_category/gacha_demand.txt`。

## 3. 操作流程（玩家侧）
1) 打开角色交互，点击“授予天外之人特权”。
2) 交互会：a) 加国家修正（权限+满意度+权力基线）；b) 在首都添加少量 gacha Pop。
3) 阶层面板可见“天外之人”，可任命内阁/将领。

## 4. 仍存问题 / TODO
- **goods_demand 提示**：`gacha_demand has no category scripted` 仍提示，虽已有占位文件，但类别未完全识别。可参考 vanilla 的 `pop_needs` 分类，补充更规范的脚本和本地化键。
- **基盘报错**（与阶层无关）：`add_mil_power/add_adm_power/add_dip_power/after/capital_scope` 等旧事件效果需替换为 EU5 支持的效果；`portrait_locked/animation_unlocked` 变量未设置；多处 orphaned event。
- **mipmap 提示**：`gfx/interface/icons/estates/gacha_estate.dds` 无 mipmaps，仅影响警告，可重新导出带 mipmap 的 DDS。
- **AUTO_MODIFIER_NAME_* 占位**：已补中文，但仍会在未覆盖语言下显示英文；如需彻底干净，可在其他语言文件补齐或隐藏自动修正。

## 5. 复盘与经验
- **显示权力需要实体 Pop/权重**：仅靠修正不显示阶层，需提供权力基线 + 实际 Pop。
- **权限需双层放行**：角色层（core_modifier）+ 国家层（integration 修正/特权），否则任命 UI 仍会阻挡。
- **占位与编码**：自定义文件必须 UTF-8 BOM；自定义类型/图标要有占位，避免 DB/图标缺失报错。

## 6. 后续可选优化
- 规范化 gacha_demand 分类（加入 pop_needs 或 special_demands）并添加本地化。
- 清理旧事件中的非法 effect，减少噪音报错。
- 给天外之人设计更多特权/议题/事件链，或动态调整权力（而非固定基线）。

## 7. 阶层修正设计与添加指南
### 7.1 需求拆解
- **目标**：为阶层提供清晰的权力来源、满意度调节、唯一性能力（内阁/军职）、与国家/Pop 的正反馈或约束。
- **层级**：
  - **角色层**：决定特定角色是否被阶层限制（如内阁/军职）。放行可用 `force_allow_as_leader`/`ignore_gender_block_cabinet` 等。
  - **阶层层**：通过特权或静态修正改变该阶层的权力、满意度、特殊能力。
  - **国家层**：通过国家修正、法律、事件影响阶层权力或满意度。

### 7.2 可用修正类型（参考劳工/哥萨克写法）
- **权力/满意度**：`global_*_estate_power`、`*_estate_target_satisfaction`、`*_estate_satisfaction_decay/recovery`。
- **权限/限制**：`*_estate_allowed_in_cabinet`、`*_estate_allowed_leading_military`、`*_estate_allowed_to_build_roads`、`*_estate_blocked_from_cabinet` 等。
- **税/征召**：`*_estate_max_tax/min_tax`、`*_estate_levy_size`。
- **议会/议程**：`*_estate_can_participate_in_parliament`、`*_estate_blocked_from_parliament`、`*_estate_agenda_impact`。
- **婚姻/转化**：`*_estate_cannot_marry`、`global_*_conversion_blocked/assimilation_blocked/migration_allowed`。
- **满意度/叛乱**：`monthly_*_estate_rebel_growth` 等。

> 当前 gacha 使用的自定义类型已在 `main_menu/common/modifier_type_definitions/gacha_modifier_types.txt` 声明；添加新修正时按需补充类型定义与图标。

### 7.3 添加新特权的步骤
1. **定义修正类型**（如需要新数值）：`main_menu/common/modifier_type_definitions/gacha_modifier_types.txt`。
2. **绑定图标**：`main_menu/common/modifier_icons/gacha_modifier_icons.txt`，确保不缺 icon。
3. **编写特权**：`in_game/common/estate_privileges/gacha_estate.txt` 中新增块，示例：
   ```paradox
   gacha_research_aid = {
     estate = gacha_estate
     country_modifier = {
       gacha_estate_target_satisfaction = medium_privilege_target_satisfaction
       global_gacha_estate_power = 0.25
       research_speed = 0.05          # 若需要基础类型，确保类型存在
     }
   }
   ```
4. **入口触发**：通过事件/交互/法律发放。例如在交互 `gacha_estate_privileges_interaction` 中添加 `add_country_modifier` 或事件选项中添加。
5. **本地化**：统一放在 `main_menu/localization/simp_chinese/eu_gacha_l_simp_chinese.yml`，包含名称与描述。

### 7.4 设计建议
- **权力来源**：避免完全靠修正叠加，最好配合实际 Pop（或事件动态增加 pop_size），否则 0 权力或显示异常。
- **满意度平衡**：使用 target_satisfaction + decay/recovery 控制阶层稳定性，避免长尾负面波动。
- **唯一性能力**：挑选 1-2 个“标志”能力（如内阁+军职），其余增益保持克制，方便数值审查。
- **发放渠道**：
  - 常驻：自动修正（auto_modifiers）或国家修正。
  - 条件式：特权、法律、事件选项。
  - 交互：按钮一次性解锁（当前“授予天外之人特权”）。
- **调试**：关注 error.log 缺失类型/图标/本地化；使用 `estate_power(estate_type:...)` 等触发检查权力；必要时临时增加 pop 观察 UI。

### 7.5 参考模板
- **特权模板**（内阁 + 满意度 + 少量 power）：
  ```paradox
  gacha_in_administration = {
    estate = gacha_estate
    country_modifier = {
      gacha_estate_allowed_in_cabinet = yes
      gacha_estate_target_satisfaction = medium_privilege_target_satisfaction
      global_gacha_estate_power = 0.1
    }
  }
  ```
- **国家修正模板**（权限 + 基线权力）：
  ```paradox
  gacha_estate_integration_modifier = {
    game_data = { category = country decaying = no }
    gacha_estate_allowed_in_cabinet = yes
    gacha_estate_allowed_leading_military = yes
    gacha_estate_target_satisfaction = medium_permanent_target_satisfaction
    global_gacha_estate_power = 5.0
  }
  ```
- **交互模板**（发放特权 + 加 Pop）：
  ```paradox
  effect = {
    add_country_modifier = { modifier = gacha_estate_integration_modifier years = -1 mode = add_and_extend }
    random_owned_location = {
      limit = { is_capital = yes }
      add_pop = {
        type = pop_type:gacha
        size = 100
        culture = owner.dominant_culture
        religion = owner.religion
      }
    }
  }
  ```
