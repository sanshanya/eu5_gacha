# Engine Truth: Basics & Verified Behaviors

- **Version**: 1.1
- **Last Verified**: 2025-12-04
- **Purpose**: 聚合官方 Wiki 结论与项目组实测的引擎行为，作为底层事实依据。
- **Official Source**: [Tinto Talks #85 - Modding](https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-85-22nd-of-october-modding.1864004/)

> [!IMPORTANT]
> **Jomini Framework**: EU5 使用与 CK3、Vic3、I:R 共享的 Jomini 脚本框架。
> 可参考这些游戏的Modding文档，但需注意EU5的特定实现差异。

---

## 1. Modifiers (修正)

### 1.1 数值型 Modifiers
- **默认值**: `0`
- **叠加规则**: 相同类型的 modifier 在同一 scope 上**相加** (Additive)。
- **来源**: [EU5 Wiki - Modifier Types](https://eu5.paradoxwikis.com/Modifier_Types)

### 1.2 布尔型 Modifiers
- **默认值**: `no`
- **取值范围**: 仅接受 `yes` / `no`。
- **叠加规则**: 只要有一个来源为 `yes`，结果即为 `yes` (OR Logic)。
- **来源**: [EU5 Wiki - Modifier Types](https://eu5.paradoxwikis.com/Modifier_Types)

### 1.3 定义位置
- **Type Definitions**: `common/modifier_type_definitions/`
- **Game Data 参数**:
    - `ai_value`: AI 评估该修正时的权重。
    - `translate`: 是否需要本地化翻译。
    - `type_set`: 归属的集合（如 `cultural_acceptance`）。

---

## 2. Script Values (脚本数值)

### 2.1 作用域行为
- **上下文**: `script_value` 计算时，`THIS` 指针直接指向调用者的作用域。
- **Root 访问**: 无需通过 `root.var` 访问变量，直接使用 `variable_name` 即可读取当前作用域变量。
- **验证状态**: ✅ **已验证** (Ref: `archive_technical_reference_old.md`)

### 2.2 限制
- **前缀限制**: 在 `scripted_effect` 中**不能**使用 `script_value:` 前缀来调用（引擎解析错误）。
- **替代方案**: 必须在 effect 中内联计算或使用 `value = script_value_name` (仅限支持 value 的语句)。
- **验证状态**: ✅ **已验证** (Ref: RNG Fix Log)

---

## 3. Random Lists (随机列表)

### 3.1 权重语法
- **正确**: 直接使用 `script_value_name = { ... }` 或常数权重
- **错误**: `value:script_value_name` (引擎不support)
- **验证状态**: ✅ **已验证** (详见 `design_engine_pitfalls.md`)

### 3.2 作用域锁定
- 随机种子通常与日期/Tag绑定，同一天内对同一 Tag 多次调用可能得相同结果

---

## 4. Scopes (作用域)

> **Official Reference**: [EU5 Wiki - Scope](https://eu5.paradoxwikis.com/Scope)

### 4.1 定义
- **Scope**: 代表游戏对象类型（Country, Character, Location 等）。
- **用途**: 大多数 Effects 和 Triggers 都需在特定 Scope 中执行。
- **例外**: 某些 Script 不需要特定 Scope（称为 "global" / "any" / "none" scope）。

### 4.2 Base Scope 与 ROOT
- **Base Scope**: 每个脚本元素（Event, Effect, Trigger）都包含一个 base scope。
- **ROOT**: 可用于调用 base scope，始终指向当前脚本执行链的顶层作用域。
- **验证状态**: ✅ **已验证** - 项目中大量使用 `root = { }` 从 Character Scope 回到 Country Scope。

### 4.3 Saved Scopes
- **创建**: 使用 `save_scope_as = name` 保存当前对象。
- **引用**: 使用 `scope:name` datalink 访问保存的作用域。
- **生命周期**: 在当前 Effect 链（包括触发的 Event）中持续存在，直到显式清除。
- **清理**: 使用 `clear_saved_scope = name` 清除引用。
- **验证状态**: ✅ **已验证** (Ref: `spec/spec_scope_management.md` §Scope Stacking)

### 4.4 Event Targets (传统机制，EU5 推荐使用 Saved Scopes)
- **用法**: 用于在作用域间传递引用。
- **注意**: 官方 Wiki 建议优先使用 `save_scope_as` 而非传统 Event Targets。

### 4.5 Scope Existence Checks
- **?= 操作符**: 检查 Scope 是否存在。
- **语法**: `scope:name ?= yes/no`
- **验证状态**: ✅ **推荐使用** (Ref: `spec_scope_management.md` & `design_engine_pitfalls.md`)

---

## 5. Effects (效果)

> **Official Reference**: [EU5 Wiki - Effect](https://eu5.paradoxwikis.com/Effect)

### 5.1 定义
- **Effects**: 改变当前游戏状态的指令 (creating/killing character, changing ownership等)。
- **官方描述**: "Effects change the current game state"

### 5.2 Effect 类型

#### Inline Effects
- **定义**: 接受简单目标的 Effect (如 scope, script value, 或 defined type)。
- **示例**: `add_gold = 100`, `kill_character = scope:temp_char`

#### Block Effects
- **定义**: 更复杂的 Effect,接受多个目标参数。
- **示例**:
```paradox
add_casus_belli = {
  target = <country_scope>
  type = <casus_belli_type>
  days = <script_value>
}
```

### 5.3 Scope 要求
> **[ENGINE]** All effects require a certain scope.

- **通用 Effects**: 某些 Effect 可以在任何 scope 使用 (标记为 "none")。
- **特定 Scope Effects**: 其他 Effect 只能在正确的 scope 中使用。
- **Scope 切换**: 某些 Effect 会改变当前 scope。

**常见 Scope 类型**:
- `none` / `any` - 通用 scope
- `country` - 国家 scope
- `character` - 角色 scope  
- `location` - 位置 scope
- `international_organization` - 国际组织 scope

### 5.4 Iterator Effects
> **[ENGINE]** Iterators examine all relevant scopes and output one or more.

**四种迭代器前缀**:

| 前缀 | 类型 | 功能 |
|:---|:---|:---|
| `every_` | Effect | 对所有返回的 scope 执行 effects |
| `random_` | Effect | 对单个随机返回的 scope 执行 effects |
| `ordered_` | Effect | 对排序后的 scope 执行 effects |
| `any_` | Trigger | 检查是否有任何 scope 满足条件 |

**常用模式**:
```paradox
# every_ - 遍历所有
every_character = {
  limit = { has_trait = some_trait }
  add_gold = 100
}

# random_ - 随机选择一个
random_owned_location = {
  limit = { development > 10 }
  change_prosperity = 5
}

# ordered_ - 按顺序选择
ordered_province = {
  order_by = development
  limit = { is_core = root }
  position = 0  # 第一个
  add_core = scope:target
}
```

### 5.5 Flow Effects
> **[ENGINE]** Flow effects control how other effects are used.

**条件控制**:
- `if` / `else_if` / `else` - 条件分支
- `limit` - 过滤条件

**特殊 Effects**:
- `hidden_effect` - 隐藏 tooltip 的 effects
- `custom_tooltip` - 自定义 tooltip 文本
- `conditional_effect` - 始终显示条件和效果的 effect

### 5.6 项目常用 Effects

#### Character Management
- `create_character` - 创建角色 (Country Scope)
- `kill_character` - 杀死角色 (None Scope, Target: character)
- `add_trait` - 添加特质 (Character Scope)

#### Scope Management  
- `save_scope_as` - 保存当前 scope (见 §4.3)
- `clear_saved_scope` - 清理保存的 scope (见 §4.3)

#### Country Operations
- `add_gold` - 增加金币 (Country/IO Scope)
- `add_prestige` - 增加威望 (Country/IO Scope)
- `trigger_event_non_silently` - 触发事件

#### Variable Operations
- `change_variable` - 修改变量值 (Any Scope)
- `add_to_list` - 添加到列表 (None Scope)

### 5.7 验证状态
- ✅ **Iterator Effects**: 项目中正确使用 `every_`, `random_` 模式
- ✅ **Scope Requirements**: 所有 Effects 在正确 Scope 中调用
- ✅ **Flow Control**: `hidden_effect` 用于清理逻辑

---

## 6. Unverified / Pending (存疑区)

> [!NOTE]
> 本节列出尚待验证的引擎行为。验证后请移至上方章节。

- [ ] **Modifier Scope**: `gacha_xinhai_country_modifier` 在海战 (Battle Scope) 中是否生效？
    - *猜想*: 应该生效，因为是 Country Modifier。
    - *验证计划*: 观察海战界面修正列表。

- [ ] **Event Target Persistence**: `save_event_target` 在跨月/跨年后的持久性如何？
    - *猜想*: 存档兼容，但需测试。
