# Engine Pitfalls & Verified Behaviors

- **Version**: 2.0
- **Last Verified**: 2025-11-25
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
    limit = { scope:existing_char = { employer = root } }
    scope:existing_char = { change_variable = { name = gacha_constellation_lvl add = 1 } }
    clear_saved_scope = existing_char  # ✅ 分支 A 清理
}
else = {
    add_gold = 100
    clear_saved_scope = existing_char  # ✅ 分支 B 也要清理!
}
```

---

##§3. Template Parameters (The "Type Trap")

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
