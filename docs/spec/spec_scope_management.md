# Scope Management Standards (作用域管理规范)

- **Version**: 2.0
- **Last Verified**: 2025-11-25
- **Official Reference**: [EU5 Wiki - Scope](https://eu5.paradoxwikis.com/Scope)
- **Engine Truth**: [`spec_engine_basics.md` §4](spec_engine_basics.md)

---

## 1. 官方标准 (Official Standards)

### 1.1 什么是 Scope?
> **[ENGINE]** Scopes represent game object types. Most effects and triggers must be run in a relevant scoped object.  
> (Source: [EU5 Wiki](https://eu5.paradoxwikis.com/Scope))

**定义**: Scope (作用域) 代表游戏对象类型,如 Country, Character, Location 等。

### 1.2 BASE SCOPE 与 ROOT
> **[ENGINE]** Each scripted element contains a base scope, callable with `root`.  
> (Source: [EU5 Wiki - Base Scope](https://eu5.paradoxwikis.com/Scope))

- **root**: 始终指向当前脚本执行链的**顶层作用域**
- **用途**: 在嵌套Scope中回溯到原始调用者
- **稳定性**: `root` 指针在整个Effect链中不变

**示例**:
```paradox
# Country Scope (root = DAI)
gacha_execute_roll = {
    random_character = { save_scope_as = char }
    
    scope:char = {
        # this = char, root = DAI
        root = {
            # 回到 Country Scope
            set_variable = { name = result value = 1 }
        }
    }
}
```

### 1.3 SAVED SCOPES
> **[ENGINE]** Saved Scopes are created with `save_scope_as` and referenced with `scope:name`.  
> (Source: [EU5 Wiki - Scope](https://eu5.paradoxwikis.com/Scope))

> **[PROJECT]** 基于本项目实测: Saved Scopes在当前Effect链中持续存在，**触发Event时也会携带过去**，直到显式`clear_saved_scope`。该行为在EU5 Wiki目前未明确定义，以下结论来自多次测试总结。

**生命周期规则**:
1. **创建**: `save_scope_as = name`
2. **引用**: `scope:name`
3. **清理**: `clear_saved_scope = name`
4. **持久性**: [实测] 跨越`trigger_event`直到显式清除

---

## 2. 项目规范 (Project Standards)

### 2.1 黄金法则
> **[SAFEGUARD]** 任何 `save_scope_as` 必须有对应的 `clear_saved_scope`。  
> (Ref: `archive/archive_scope_errors_lessons.md` - Dynasty Bug)

**原因**: 防止Scope泄漏导致对象引用污染(详见Archive历史教训)。

**例外情况**: 作为「长期事件目标」使用的全局scope (极少见)，必须有**单独的设计文档**说明生命周期，否则一律视为泄漏。

### 2.2 分支清理规则
> **[SAFEGUARD]** 所有 `if/else` 分支都必须清理Scope。

```paradox
if = {
    limit = { scope:char ?= { employer = root } }
    # 分支 A 逻辑
    clear_saved_scope = char  # ✅ 必须
}
else = {
    # 分支 B 逻辑
    clear_saved_scope = char  # ✅ 也必须
}
```

### 2.3 Scope清理时序规则

#### 规则A: 临时Scope - 在触发Event**之前**清理
> **[SAFEGUARD]** 所有「仅在当前effect使用的临时scope」必须在触发event之前清理。

```paradox
# ✅ 正确: 临时scope不给Event用
create_character = { save_scope_as = temp_char }
scope:temp_char = { 
    # 仅在effect中使用
    add_gold = 100 
}
clear_saved_scope = temp_char  # 1. 先清理
trigger_event_non_silently = { id = event.1 }  # 2. 后触发
```

**原因**: 避免Event UI捕捉不需要的Scope引用。

#### 规则B: Event-bound Scope - 在Event的`after`中清理
> **[SAFEGUARD]** 如果 Scope 是为了在 Event UI 中显示（如立绘），则必须在 Event 的 `after` 块中清理。如果在触发前清理，UI 将无法获取该对象。

```paradox
# Effect中保存scope
random_in_global_list = {
    variable = gacha_obtained_characters
    limit = { has_trait = gacha_xinhai_origin_trait }
    save_scope_as = xinhai_char  # 保存但不清理
}

scope:xinhai_char = {
    change_variable = { name = gacha_constellation_lvl add = 1 }
    root = {
        trigger_event_non_silently = { id = gacha_xinhai_events.30 }
    }
}
# ❌ 不要在这里 clear_saved_scope !
```

```paradox
# Event中使用并清理
gacha_xinhai_events.30 = {
    type = country_event
    # character = scope:xinhai_char  # (V3: Implicit binding)
    
    option = {
        scope:xinhai_char = { add_trait = some_trait }
    }
    
    # ✅ 在after中统一清理
    after = {
        clear_saved_scope = xinhai_char
    }
}
```

**原因**: 
- `trigger_event_non_silently`异步执行，提前清理会导致Event中`scope:xinhai_char`失效
- `after`块在任何option选择后执行，是官方推荐的清理位置
- 集中清理避免多分支时遗漏

---

## 3. 标准模式 (Standard Patterns)

### 3.1 基础模式: 创建-使用-清理
```paradox
# 场景1: Effect内临时使用
any_character = {
    limit = { has_trait = gacha_xinhai_origin_trait }
    save_scope_as = existing_char
}

scope:existing_char ?= {
    change_variable = { name = gacha_constellation_lvl add = 1 }
}

clear_saved_scope = existing_char
```

```paradox
# 场景2: 传递给Event使用 (推荐模式)
random_in_global_list = {
    variable = gacha_obtained_characters
    limit = { has_trait = gacha_xinhai_origin_trait }
    save_scope_as = xinhai_char
}

scope:xinhai_char = {
    root = { trigger_event_non_silently = { id = gacha_xinhai_events.11 } }
}
# 不在这里清理,在event.after中清理
```

### 3.2 嵌套模式: 由内向外清理
```paradox
scope:char_a = {
    random_character = {
        limit = { has_trait = some_trait }
        save_scope_as = char_b
    }
    
    scope:char_b = { # 使用 char_b }
    clear_saved_scope = char_b  # 先清理内层
}
clear_saved_scope = char_a  # 再清理外层
```

### 3.3 ROOT 回溯模式
```paradox
scope:char = {
    # Character Scope
    root = {
        # Country Scope
        trigger_event_non_silently = { id = my_event.1 }
    }
}
```

### 3.4 Regency Interaction 模式
```paradox
effect = {
    # 1. 保存
    scope:actor = { ruler = { save_scope_as = old_ruler } }
    
    # 2. 使用
    scope:old_ruler = { remove_character_modifier = modifier_name }
    
    # 3. 执行其他逻辑...
    
    # 4. 清理 (最后一步)
    clear_saved_scope = old_ruler
}
```

---

## 4. Scope 检查清单 (Checklist)

在提交代码前,检查以下项目:

- [ ] 每个 `save_scope_as` 都有对应的 `clear_saved_scope`?
- [ ] 所有 `if/else` 分支都包含清理逻辑?
- [ ] **临时scope**在最后一次使用后立即清理?
- [ ] **Event-bound scope**在Event的`after`块中清理?
- [ ] 临时角色在清理前已 `kill_character`?
- [ ] 嵌套Scope按正确顺序清理(由内向外)?

---

## 5. 优先级指导

**最优**: 完全在Country Scope工作(项目主要模式)
```paradox
gacha_execute_roll = {
    set_variable = { name = result value = gold }
    if = { limit = { result < 100 } ... }
    trigger_event_non_silently = { id = event.1 }
}
```

**次优**: 使用现有对象的Scope,确保清理

**避免**: 创建临时对象切换Scope(除非必要)

---

## 6. 参考文档

| 文档 | 说明 |
|:---|:---|
| [EU5 Wiki - Scope](https://eu5.paradoxwikis.com/Scope) | 官方标准 |
| [`spec_engine_basics.md`](spec_engine_basics.md) | 引擎真理 |
| [`archive_scope_errors_lessons.md`](../archive/archive_scope_errors_lessons.md) | 历史教训 |
| [`design_engine_pitfalls.md`](../design/design_engine_pitfalls.md) | 陷阱指南 |
