# Engine Pitfalls & Verified Behaviors

- **Version**: 2.2
- **Last Verified**: 2025-11-27
- **Purpose**: 记录开发过程中踩过的坑,将错误经验转化为工程规范。

---

## §1. Random List 行为 (The "Illegal Syntax" Trap)

### 官方/源头
- **机制**: `random_list` 接受 `weight = { effect }` 的结构。
- **限制**: 权重部分必须是整数或 `script_value` 的直接引用,**不支持** `value:xxx` 这种复杂语法。
- **参考**: [EU5 Wiki - Scripting](https://eu5.paradoxwikis.com/Scripting) (推断)

### 过去踩过的坑
- **错误代码**: `value:gacha_5star_threshold_value = { ... }`
- **后果**: 引擎解析失败,整个 `random_list` 块静默失效,导致抽卡无反应。
- **来源**: [Archive: RNG Fix Log](../archive/archive_rng_fix_log.md)

### 规避规范
- **DON'T**: 不要在 `random_list` 的权重中使用冒号语法 (`value:`)。
- **DO**: 直接使用 `script_value_name = { ... }`。
- **SAFEGUARD**: 在本项目中,核心 RNG 逻辑已移出 `random_list`,改用伪随机算法 (`gacha_logic_effects.txt`)。

---

## §2. Scope Leaks (The "Dynasty" Bug)

### 官方/源头解释
> **[ENGINE]** Saved Scopes persist across the current Effect chain (including triggered Events) until explicitly cleared.  
> (Source: [EU5 Wiki - Scope](https://eu5.paradoxwikis.com/Scope))

**生命周期**: `save_scope_as` 绑定一个对象到变量,直到调用 `clear_saved_scope`,否则引用持续存在。

### 历史教训
> **详细案例研究请参阅**: [`archive_scope_errors_lessons.md`](../archive/archive_scope_errors_lessons.md)

**Dynasty Bug 简述**: 第二个抽到的角色错误地继承了第一个角色的姓氏,原因是 `else` 分支忘记清理 Scope。

### 规避规范
- **DO**: 任何 `save_scope_as` 必须在**同一个 Effect 块**的结尾(或所有逻辑分支的末尾)有对应的 `clear_saved_scope`。
- **DO**: 在触发 UI 事件前,必须清理所有临时 Scope,防止死人出现在事件窗口中。
- **DO**: 代码审查时,检查 `if/else` 所有分支是否都清理了 Scope。

**正确代码**:
```paradox
if = {
    limit = { scope:existing_char ?= { employer = root } }
    scope:existing_char ?= { change_variable = { name = gacha_constellation_lvl add = 1 } }
    clear_saved_scope = existing_char  # ✅ 分支 A 清理
}
else = {
    add_gold = 100
    clear_saved_scope = existing_char  # ✅ 分支 B 也要清理!
}
```

---

## §3. Template Parameters (The "Type Trap")

### 官方/源头
- **机制**: Jomini 引擎的模板参数 (`$ARG$`) 本质上是简单的字符串替换。
- **限制**: 无法传递带类型的复杂对象(如 `culture:han`),只能传递标识符(如 `han`)。

### 过去踩过的坑
- **错误尝试**: `culture = $culture_type$` (传入 `culture:han`)
- **后果**: 脚本解析错误,无法正确赋值。
- **来源**: [Archive: Technical Reference](../archive/archive_technical_reference_old.md)

### 规避规范
- **DO**: 模板参数只用于传递 ID/Key(如 `xinhai`)。
- **DO**: 复杂数据类型(Culture, Religion)应在 Wrapper Effect 中硬编码,或通过 `if/else` 分支处理。

---

## §4. Localization Limitations (The "Dynamic Name" Wall)

### 官方/源头
- **限制**: 国家事件 (Country Event) 的 `desc` 文本无法通过 Scope 动态显示角色名字。
- **参考**: [Archive: Technical Reference](../archive/archive_technical_reference_old.md)

### 过去踩过的坑
- **错误尝试**: `[scope:char.GetName]` / `[This.Var('char').GetChar.GetName]`
- **后果**: 显示乱码或 fallback 文本。

### 规避规范
- **DO**: 事件正文使用静态文本。
- **DO**: 利用事件窗口顶部的 Portrait UI 来展示当前角色信息。

---

## §5. Common Hallucinations (CK3/EU4 Legacy)

> **Source**: [幻觉表.md](../幻觉表.md) - 详细记录了从 CK3/EU4 迁移时的思维误区。

### 5.1 Event Types
- **幻觉**: `type = character_event`
- **现实**: EU5 只有 `country_event`, `location_event`, `unit_event` 等。角色相关逻辑通常挂在 `country_event` 下。

### 5.2 Portrait Binding
- **幻觉**: `character = scope:my_char`
- **现实**: EU5 事件 UI 使用 **Illustration System**。
  - 机制: 引擎通常会抓取 `immediate` 块中保存的前几个 Scope (如 `save_scope_as`) 来决定显示内容。
  - 做法: 在 `immediate` 中 `save_scope_as` 目标角色，不要使用 `character = ...` 参数。

### 5.3 Variable Access Syntax
- **幻觉**: 在 `script_value` 或 `trigger` 中使用 `var:my_var` 获取数值。
- **现实**: 
  - `var:` 是 **Event Target Link** (用于切换 Scope)。
  - 获取数值直接使用 **变量名**。
  - **错误**: `add = { value = var:count }` (引擎尝试把 count 当作 scope)
  - **正确**: `add = { value = count }`

### 5.4 Triggered Only
- **幻觉**: `is_triggered_only = yes`
- **现实**: 该字段不存在。不挂在 `on_action` 且 `trigger = { always = no }` (可选) 即可实现仅脚本触发。

### 5.5 Scope Existence in Triggers
- **幻觉**: `limit = { scope:char = { ... } }` (假设 scope 永远存在)
- **现实**: 如果 scope 为空，会报错 "Invalid object"。
- **正确**: 使用 `?=` 操作符: `limit = { scope:char ?= { ... } }`。

### 5.6 Modulo Operator
- **幻觉**: 认为引擎不支持 `%` 或 `modulo`，必须用 `while` 循环模拟 (源自旧 Archive)。
- **现实**: `script_value` 完全支持 `modulo` 运算。
  - **代码证明**: `gacha_eu_values.txt` 中大量使用 `modulo = 10000`。
  - **修正**: 不要用 `while` 循环去模拟取模，直接用 `modulo`。

### 5.7 Interaction select_trigger
- **误区**: 看起来像 CK3 的 `select_trigger` (包含 `looking_for_a`, `column` 等) 是幻觉。
- **现实**: ✅ **已验证有效**。EU5 的 Interaction 系统确实支持这种复杂的选择器语法。
### 5.8 Flag Prefix Usage (`flag:`)
- **幻觉**: 认为 `value = flag:xxx` 是在引用某种布尔值标记或特殊变量。
- **现实**: `flag:` 前缀专门用于 **存储本地化键 (Localization Key)**。
  - `set_variable = { name = my_var value = flag:loc_key_name }`
  - 效果: 变量 `my_var` 存储了字符串键 `loc_key_name`。
  - 用途: 在 GUI 或文本中通过 `[Var('my_var').GetFlagName]` 动态显示对应的本地化文本。
- **警示**: 绝不要把 `flag:` 当作数值或布尔值来运算。

---

## §6. Global Variable List 存 Character → CTD（坏引用）

### 现象
- 角色死亡后，一切正常；但**只要某个 UI/按钮悬浮**（Tooltip）或某个事件选项需要遍历该列表，就可能直接闪退（CTD）。
- error.log 往往**没有明确脚本报错**（因为是引擎层崩溃）。

### 根本原因（工程解释）
- `global_variable_list` 存的是对象引用（类似“指针”）。  
- 角色死亡后，引擎会清理国家/宗族等一阶关系，但**不会自动清理你自定义的全局列表**。  
- 后续任何对该列表的访问/扫描，都可能命中“已销毁对象引用”从而崩溃。

### 规避规范
- **DON'T**: 不要把 `Character` 存进 `global_variable_list` 作为长期存储。
- **DO**: 改用“按 modifier 全局搜索”的方式定位角色：
  - `random_country` → `random_character` with `has_character_modifier = gacha_xxx_modifier`
- **DO**: 用 `on_character_death` 兜底清理相关状态（如 `*_is_summoned`、saved scopes）。

---

## §7. Tooltip / 预评估会跑脚本（Interaction / Event Option）

### 现象
- 玩家**只是悬浮按钮/选项**就触发异常，甚至 CTD。
- 典型触发点：交互按钮、事件选项（尤其当 trigger 成立、选项出现/变亮时）。

### 根本原因（工程解释）
- 引擎为了生成 tooltip / 预测效果，可能会对 `effect` 做预评估或局部执行。
- 如果 `effect` 里包含：
  - 创建对象（`create_character`）
  - 大量随机/遍历
  - 或“递归自调用兜底”
  
  在预评估模式下会非常不稳定，甚至无限递归导致栈溢出 → CTD。

### 规避规范
- **DO**: 把复杂逻辑放入 `hidden_effect`（交互 / 事件选项均适用）。
- **DO**: 避免递归兜底；改用“清旗标→让后续分支继续”。
- **DO**: 对可重复触发交互加锁，并在 `after`/`on_game_start` 解锁兜底（防止崩溃后永久锁死）。
