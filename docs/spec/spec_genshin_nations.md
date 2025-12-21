# 七国系统规范 (Genshin Nations Specification)

**Version**: 0.5  
**Last Updated**: 2025-12-20  
**Status**: 🟡 Prototype (璃月 / 稻妻已跑通)  
**Purpose**: 规范“七国附庸”类国家的创建、修复、视觉资源与交互门控方案，便于后续扩展到其他国家。

---

## 1. 核心原则

1. **使用静态 TAG**：国家必须是静态 TAG（例如 `GL1`），这样才能稳定控制颜色、旗帜、CoA 与本地化。
2. **交互门控**：国家创建相关的内阁行动不常驻显示，通过“角色交互 → 事件 → 解锁变量”来显隐，降低内阁噪音。
3. **可修复**：同一内阁行动同时支持“创建模式”和“修复模式”（例如统治者/宗族缺失时自动修复）。
4. **作用域正确**：Cabinet Action 的 base scope 是 `cabinet`，国家必须在 `scope:actor` 中处理（见 `spec_scope_management.md` 的 Cabinet Action 模式）。

---

## 2. 文件结构（原型：璃月）

### 2.1 国家定义（静态 TAG）

- `in_game/setup/countries/gacha_seven_nations.txt`
  - `GL1` / `GI1` 的颜色与基础文化/宗教定义
- `main_menu/setup/start/gacha_countries.txt`
  - `GL1` / `GI1` 的“开局国家模板”（不在开局生成，仅作为脚本建国的默认数据源）
  - 目的：避免建国后出现 `has no government type / no heir-selection / no marriage_law` 等初始化告警
  - 结构说明：`countries = { countries = { ... } }` 是原版 `main_menu/setup/start/10_countries.txt` 的标准写法，不是重复嵌套错误

### 2.2 附庸类型

- `in_game/common/subject_types/gacha_archon_vassal.txt`
  - 七国通用附庸类型（可复用）

### 2.3 交互门控（角色交互 → 事件 → 解锁）

- 角色交互：`in_game/common/character_interactions/gacha_keqing_liyue_plan_interaction.txt`
  - 变量锁：`gacha_liyue_plan_lock`
  - 一次性解锁：`gacha_liyue_plan_unlocked`
- 角色交互：`in_game/common/character_interactions/gacha_raiden_inazuma_plan_interaction.txt`
  - 变量锁：`gacha_inazuma_plan_lock`
  - 一次性解锁：`gacha_inazuma_plan_unlocked`
- 事件：`in_game/events/gacha_nation_events.txt`
  - `gacha_nation_events.10/11/12`：璃月计划两幕
  - `gacha_nation_events.20/21/22`：稻妻计划两幕
  - `after` 中释放 `gacha_liyue_plan_lock`
  - `after` 中释放 `gacha_inazuma_plan_lock`

### 2.4 内阁行动（创建/修复）

- `in_game/common/cabinet_actions/gacha_nation_actions.txt`
  - 内阁行动：`gacha_create_liyue_nation`（再造璃月）
  - 内阁行动：`gacha_create_inazuma_nation`（再造稻妻）
  - 创建模式：在目标地点添加 `GL1` 核心并释放国家
  - 创建模式：在目标地点添加 `GI1` 核心并释放国家
  - 修复模式：璃月已存在但统治者不是刻晴/宗族缺失等

### 2.5 视觉资源（旗帜/CoA）

- 旗帜纹理：`main_menu/gfx/coat_of_arms/textured_emblems/te_gacha_GL1_liyue_flag.dds`
- 旗帜定义：`main_menu/common/flag_definitions/gacha_flag_definitions.txt`
- CoA 定义：`main_menu/common/coat_of_arms/coat_of_arms/gacha_coat_of_arms.txt`

### 2.6 国家修正（平衡用）

- `main_menu/common/static_modifiers/gacha_liyue_modifiers.txt`
  - `gacha_liyue_foundation_boom_modifier`（10年强力）
  - `gacha_liyue_trade_hub_modifier`（常驻温和）
- `main_menu/common/static_modifiers/gacha_inazuma_modifiers.txt`
  - `gacha_inazuma_foundation_boom_modifier`（10年强力）

### 2.7 本地化（避免重复键）

- 国家名/形容词集中：`main_menu/localization/*/gacha_country_names_l_*.yml`
- 七国系统/事件/修正文本：`main_menu/localization/*/eu_gacha_core_l_*.yml`

### 2.8 局势（璃月筹建）

- 局势脚本：`in_game/common/situations/gacha_liyue_reconstruction.txt`
  - key：`gacha_liyue_reconstruction`
  - 由内阁行动激活（`activate_situation`），不会自然刷出
- 局势行动：`in_game/common/generic_actions/gacha_liyue_reconstruction_actions.txt`
  - `gacha_liyue_build_market`（必做：在东莞建立独立市场）
  - `gacha_liyue_invest_50/200/500`（可选：投入加速）
- 价格定义：`in_game/common/prices/gacha_liyue_reconstruction_prices.txt`
- 局势本地化：`main_menu/localization/*/eu_gacha_situations_l_*.yml`
- 局势 UI 资源（按 key 自动取图，无需额外脚本）：
  - **局势图标**（告警/列表用）：`main_menu/gfx/interface/icons/situations/gacha_liyue_reconstruction.dds`
  - **局势背景图**（面板顶部插画）：`main_menu/gfx/interface/illustrations/situation/gacha_liyue_reconstruction.dds`
  - 建议：分辨率跟随原版（常见 `1080x440`），并使用与原版一致的 DDS 压缩格式（减少纹理警告与兼容问题）

### 2.9 局势（稻妻筹建）

- 局势脚本：`in_game/common/situations/gacha_inazuma_reconstruction.txt`
  - key：`gacha_inazuma_reconstruction`
  - 由内阁行动激活（`activate_situation`），不会自然刷出
- 局势行动：`in_game/common/generic_actions/gacha_inazuma_reconstruction_actions.txt`
  - `gacha_inazuma_build_market`（必做：在丰岛建立独立市场）
  - `gacha_inazuma_invest_50/200/500`（可选：投入加速）
- 价格定义：`in_game/common/prices/gacha_inazuma_reconstruction_prices.txt`
- 局势本地化：`main_menu/localization/*/eu_gacha_situations_l_*.yml`
- 局势 UI 资源：
  - **局势图标**：`main_menu/gfx/interface/icons/situations/gacha_inazuma_reconstruction.dds`
  - **局势背景图**：`main_menu/gfx/interface/illustrations/situation/gacha_inazuma_reconstruction.dds`

### 2.10 国家建筑（首都型建筑）

- 璃月：`in_game/common/building_types/gacha_liyue_buildings.txt`
  - `gacha_liyue_harbor`（首都时提供全国增益）
- 稻妻：`in_game/common/building_types/gacha_inazuma_buildings.txt`
  - `gacha_inazuma_tenshukaku`（首都时提供全国增益）
- 需求定义：`in_game/common/goods_demand/gacha_demand.txt`
- 图标：`main_menu/gfx/interface/icons/buildings/*.dds`

---

## 3. 标准流程（以璃月为例）

### 3.1 解锁（刻晴交互）

目标：玩家先与刻晴交互，获得剧情反馈，并解锁内阁行动。

- 交互 `allow` 需要同时满足：
  - `NOT = { has_variable = gacha_liyue_plan_unlocked }`（一次性）
  - `NOT = { has_variable = gacha_liyue_plan_lock }`（防连点）
  - 拥有目标地点（璃月为东莞 `dongguan` / 10778），否则交互按钮置灰
- 交互 `effect`：
  - `set_variable = { name = gacha_liyue_plan_lock value = yes }`
  - `trigger_event_non_silently = gacha_nation_events.10`
- 事件第二幕：
  - 立约分支设置 `gacha_liyue_plan_unlocked = yes`
  - `after` 释放 `gacha_liyue_plan_lock`

### 3.2 创建/修复（内阁行动）

目标：在指定地点释放静态 TAG 国家，设置正确统治者/宗族，并成为玩家附庸。

关键要点：

1. **显隐门控**：在 `potential/allow` 中都要检查 `has_variable = gacha_liyue_plan_unlocked`。
2. **正确作用域**：在 `on_fully_activated` 内用 `scope:actor = { ... }` 执行国家 effect。
3. **建国方式**：
   - `location:<target> = { add_core = c:GL1 }`
   - `create_country_from_cores_in_our_locations = c:GL1`
4. **兜底转移地点**：建国后若地点仍属于玩家，手动 `change_location_owner = c:GL1`。
5. **统治者与宗族**：
   - 把角色 `move_country = c:GL1`
   - 给角色分配命名宗族 `create_named_dynasty` + `change_dynasty`
   - `set_new_ruler = scope:<character>`
6. **附庸关系**：
   - `make_subject_of = { target = scope:actor type = subject_type:gacha_archon_vassal }`
7. **平衡修正**：
   - 常驻：`add_country_modifier`，`years = -1`
   - 起飞期：`add_country_modifier`，`years = 10`

### 3.3 创建/修复（稻妻差异）

- 目标地点：丰岛 `toshima_kanto` / 9221
- 角色入口：雷电将军交互 → `gacha_nation_events.20/21/22`
- 事件图片：`gacha_raiden_intro_special.dds` / `gacha_raiden_intro_special2.dds`
- 稻妻建国时额外行为：
  - 自动建成 `gacha_inazuma_tenshukaku`
  - 追加 `gacha_inazuma_foundation_boom_modifier`（10年）

### 3.3 筹建（局势 + 局势行动）

目标：用“可视化进度条 + 强制前置（东莞独立市场）+ 可选投入加速”的方式，引导玩家完成建国准备。

- 启动方式：
  - 玩家启动内阁行动 `gacha_create_liyue_nation`
  - `on_activate` 里激活局势 `gacha_liyue_reconstruction`
- 硬性前置：
  - 必须先执行局势行动 `gacha_liyue_build_market`，使 `dongguan` 成为 `market.location`
  - 未满足前置时：局势每月进度为 0（UI 明确提示“必做”）
- 每月基础推进：
  - 基础 5/月
  - 乘以 `(1 + country_cabinet_efficiency)`（最低 0.1）
  - 加上 `invest/200`（局势变量累加）
- 投入加速：
  - 通过 `gacha_liyue_invest_50/200/500` 直接提高进度并记录总投入档位（用于后续收益扩展）
- 完成收束：
  - 进度达到 100 时立即触发 `gacha_create_liyue_nation_from_plan`
  - 成功后写入 `gacha_liyue_preparations_complete` 并结束局势/完成内阁行动

---

## 4. 经验总结（璃月 / 稻妻）

### 成功经验（可复用）

1. **两幕事件 + 交互锁**：先剧情后解锁，避免内阁噪音与连点。
2. **建国流程与角色绑定**：先 `move_country` 再 `set_new_ruler`，并显式创建宗族。
3. **自动建首都建筑**：AI 很难自行建造，建国时直接 `change_building_level_in_location`。
4. **读档兜底**：`on_game_start` 补建首都建筑、重建“世界唯一”标记、重挂国家修正。
5. **局势引导**：先建独立市场，再推进进度条，行动清晰、操作可预期。

### 失败经验（必须规避）

1. **作用域错误**：从 `situation` 直接调用 country effect 会报错；必须用 `scope:actor` / `scope:recipient.var:target_country`。
2. **角色国家修正绑定错误**：国家修正必须挂在 `employer`，而不是 `root`（避免 root 为空）。
3. **国家建筑不可建**：
   - 目标地点不是 town/city 时必须 `rural_settlement = yes`
   - `country_potential`/`remove_if` 使用 `tag = GI1/GL1` 更稳
4. **静态修正编码**：`main_menu/common/static_modifiers/*.txt` 必须是 UTF-8 BOM。
5. **建国后地点未转移**：`create_country_from_cores_in_our_locations` 仍可能失败，需要兜底 `change_location_owner`。

---

## 5. 命名与变量约定（推荐）

为便于扩展到其他国家，建议统一命名：

- 解锁变量：`gacha_<nation>_plan_unlocked`
- 防连点锁：`gacha_<nation>_plan_lock`
- 本次 action 是否“首次建国”：`gacha_<nation>_created_now`（action 内临时变量）
- 10年强力增益是否已用：`gacha_<nation>_foundation_boom_used`（写在目标国家上）
- 静态修正：
  - 常驻：`gacha_<nation>_trade_hub_modifier`（或更贴近定位的名称）
  - 10年：`gacha_<nation>_foundation_boom_modifier`

---

## 6. 常见坑位（必读）

1. **Cabinet Action scope**：不要在 root 直接执行 country effect；一律用 `scope:actor`。
2. **本地化重复键**：国家名/形容词只在一个文件里定义（推荐 `gacha_country_names_l_*`）。
3. **角色统治宗族**：如果角色没有 dynasty，会出现“不属于统治宗族”并影响联姻/王室系统显示。
4. **防连点**：交互/事件必须有锁变量，否则会生成多个事件实例或重复解锁。
5. **旧存档残留**：早期“多次 set_new_ruler”会污染历史列表，新实现只能止损，无法回滚旧历史。
6. **UI 条件直出**：避免让引擎自动把复杂 trigger 展开到界面（容易出现“25%/是广州/is_ai”之类的误导文本）；优先用 `custom_tooltip` 输出可读提示，把复杂条件放进脚本内部判断。

---

## 7. ⚠️ 原版覆盖（必须知悉）

本原型包含一次 **Vanilla GUI 覆盖**（用于消除引擎日志刷屏）：

- `in_game/gui/zz_gacha_messages_patch.gui`
  - 覆盖原版 `template message_template`（来自 base game `in_game/gui/messages.gui`）
  - 修复：描述区 `TooltipBlockListContent` 未设置 `BlockList` 上下文导致的 `BlockList.GetBlocks` 报错

**兼容性提示**：该覆盖会与其他“改消息弹窗”的 UI 模组产生冲突；如遇 UI 兼容问题，优先把该文件临时移除做 A/B 验证。
