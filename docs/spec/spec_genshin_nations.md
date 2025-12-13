# 七国系统规范 (Genshin Nations Specification)

**Version**: 0.1  
**Last Updated**: 2025-12-13  
**Status**: 🟡 Prototype (璃月已跑通)  
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
  - `GL1` 的颜色与基础文化/宗教定义

### 2.2 附庸类型

- `in_game/common/subject_types/gacha_archon_vassal.txt`
  - 七国通用附庸类型（可复用）

### 2.3 交互门控（角色交互 → 事件 → 解锁）

- 角色交互：`in_game/common/character_interactions/gacha_keqing_liyue_plan_interaction.txt`
  - 变量锁：`gacha_liyue_plan_lock`
  - 一次性解锁：`gacha_liyue_plan_unlocked`
- 事件：`in_game/events/gacha_nation_events.txt`
  - `gacha_nation_events.10/11/12`：璃月计划两幕
  - `after` 中释放 `gacha_liyue_plan_lock`

### 2.4 内阁行动（创建/修复）

- `in_game/common/cabinet_actions/gacha_nation_actions.txt`
  - 内阁行动：`gacha_create_liyue_nation`（再造璃月）
  - 创建模式：在目标地点添加 `GL1` 核心并释放国家
  - 修复模式：璃月已存在但统治者不是刻晴/宗族缺失等

### 2.5 视觉资源（旗帜/CoA）

- 旗帜纹理：`main_menu/gfx/coat_of_arms/textured_emblems/te_gacha_GL1_liyue_flag.dds`
- 旗帜定义：`main_menu/common/flag_definitions/gacha_flag_definitions.txt`
- CoA 定义：`main_menu/common/coat_of_arms/coat_of_arms/gacha_coat_of_arms.txt`

### 2.6 国家修正（平衡用）

- `main_menu/common/static_modifiers/gacha_liyue_modifiers.txt`
  - `gacha_liyue_foundation_boom_modifier`（10年强力）
  - `gacha_liyue_trade_hub_modifier`（常驻温和）

### 2.7 本地化（避免重复键）

- 国家名/形容词集中：`main_menu/localization/*/gacha_country_names_l_*.yml`
- 七国系统/事件/修正文本：`main_menu/localization/*/eu_gacha_core_l_*.yml`

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

---

## 4. 命名与变量约定（推荐）

为便于扩展到其他国家，建议统一命名：

- 解锁变量：`gacha_<nation>_plan_unlocked`
- 防连点锁：`gacha_<nation>_plan_lock`
- 本次 action 是否“首次建国”：`gacha_<nation>_created_now`（action 内临时变量）
- 10年强力增益是否已用：`gacha_<nation>_foundation_boom_used`（写在目标国家上）
- 静态修正：
  - 常驻：`gacha_<nation>_trade_hub_modifier`（或更贴近定位的名称）
  - 10年：`gacha_<nation>_foundation_boom_modifier`

---

## 5. 常见坑位（必读）

1. **Cabinet Action scope**：不要在 root 直接执行 country effect；一律用 `scope:actor`。
2. **本地化重复键**：国家名/形容词只在一个文件里定义（推荐 `gacha_country_names_l_*`）。
3. **角色统治宗族**：如果角色没有 dynasty，会出现“不属于统治宗族”并影响联姻/王室系统显示。
4. **防连点**：交互/事件必须有锁变量，否则会生成多个事件实例或重复解锁。
5. **旧存档残留**：早期“多次 set_new_ruler”会污染历史列表，新实现只能止损，无法回滚旧历史。
