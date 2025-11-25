# Scope Management - Historical Errors and Lessons

> **Archive Date**: 2025-11-25  
> **Origin**: Extracted from `spec_scope_management.md` during documentation restructuring.  
> **Purpose**: Preserve historical mistakes and learning process for future reference.

---

## 血淋淋的教训: Dynasty Inheritance Bug

### 现象
第二个抽到的角色(如心海)错误地继承了第一个角色(如雷电)的姓氏(变成了"胡心海")。

### 原因
在处理重复抽卡逻辑时,进入 `else` 分支(归属权冲突)后,**忘记清理 `existing_char` 作用域**。导致下一次抽卡时,引擎错误地复用了未清理的作用域上下文。

### 错误代码
```paradox
if = {
    limit = { ... }
    # 正常逻辑
    clear_saved_scope = existing_char  # ✅ 这里清理了
}
else = {
    # 异常分支 (归属权冲突)
    add_gold = 100
    # ❌ 忘记清理 existing_char!
    # 下次抽卡时,existing_char 仍然指向这个旧角色,导致严重Bug
}
```

### 正确代码
```paradox
else = {
    add_gold = 100
    # ✅ 必须清理!无论在哪个分支!
    clear_saved_scope = existing_char
}
```

### 发生过程
1. 玩家第一次抽到雷电(姓氏:胡),归属给自己 → 正常清理 `existing_char`
2. 玩家第二次抽到心海(姓氏:珊瑚宫),但由于某个逻辑进入 `else` 分支 → **没有清理**
3. 玩家第三次抽到新角色时,引擎错误地继承了未清理的 `existing_char` 上下文 → 姓氏污染

---

## 常见错误模式示例

### 错误 1: 在角色作用域中触发国家事件
**问题**:
```paradox
scope:temp_char = {
    # ❌ 错误:在角色作用域触发country_event
    trigger_event_non_silently = { id = my_event.1 }
}
```

**表现**: 事件不触发,或者触发但上下文错误

**修复**:
```paradox
scope:temp_char = {
    # 回到国家作用域再触发
    root = {
        trigger_event_non_silently = { id = my_event.1 }
    }
}
```

---

### 错误 2: 触发事件后才清理作用域
**问题**:
```paradox
# ❌ 错误顺序
create_character = { save_scope_as = temp }
scope:temp = { ... }

root = {
    trigger_event_non_silently = { id = gacha_events.1 }
}

# 太晚了!事件已经触发,temp_char 会出现在UI中
kill_character = { target = scope:temp }
clear_saved_scope = temp
```

**修复**:
```paradox
# ✅ 正确顺序
create_character = { save_scope_as = temp }
scope:temp = { ... }

# 先清理
kill_character = { target = scope:temp }
clear_saved_scope = temp

# 再触发事件
root = {
    trigger_event_non_silently = { id = gacha_events.1 }
}
```

---

### 错误 3: 忘记检查作用域类型
**问题**:
```paradox
# ❌ 在国家作用域调用只支持角色的effect
add_trait = some_trait  # 这是角色effect!
```

**修复**:
```paradox
# ✅ 检查文档确认支持的作用域
# 如果需要角色作用域:
random_character = {
    add_trait = some_trait
}
```

---

### 错误 4: 临时角色出现在事件UI
**问题**:
```paradox
# ❌ 错误:临时角色会出现在事件中
create_character = {
    save_scope_as = temp_char
}
scope:temp_char = {
    root = {
        trigger_event_non_silently = { id = my_event.1 }
    }
}
# 此时 temp_char 还活着,会显示在事件UI中
```

**修复**:
```paradox
# ✅ 正确:先清理再触发
create_character = {
    save_scope_as = temp_char
}
scope:temp_char = {
    # 做一些逻辑...
}
kill_character = { target = scope:temp_char }
clear_saved_scope = temp_char

# 现在触发事件,temp_char 已经不存在了
root = {
    trigger_event_non_silently = { id = my_event.1 }
}
```

---

## Regency Interaction 案例研究

### 背景
在实现摄政系统时,需要切换统治者,涉及复杂的Scope管理。

### 挑战
1. 需要保存旧统治者的引用
2. 切换统治者后修改角色属性
3. 确保所有Scope在效果结束时清理

### 解决方案
```paradox
effect = {
    hidden_effect = {
        # 1. 保存当前统治者为旧统治者
        scope:actor = {
            ruler = { save_scope_as = gacha_old_ruler }
        }

        # 2. 清理旧统治者上的修正,并确保留在王权阶层
        scope:gacha_old_ruler = {
            remove_character_modifier = gacha_temp_regent_modifier
            remove_character_modifier = gacha_former_ruler_modifier
            change_character_estate = estate_type:crown_estate
        }

        # 3. 切换统治者到目标角色
        scope:actor = {
            set_new_ruler_with_union = { character = scope:recipient }
        }

        # 4. 给旧统治者打"前任统治者"修正
        scope:gacha_old_ruler = {
            add_character_modifier = { modifier = gacha_former_ruler_modifier years = -1 mode = add_and_extend }
        }

        # 5. 给新统治者打"代政中"修正,并放入王权阶层
        scope:recipient = {
            add_character_modifier = { modifier = gacha_temp_regent_modifier years = -1 mode = add_and_extend }
            change_character_estate = estate_type:crown_estate
        }

        # 6. 关键!清理保存的作用域
        clear_saved_scope = gacha_old_ruler
    }
}
```

### 教训
- 在复杂交互中,明确标注每一步的Scope状态
- 使用有意义的Scope名称(如 `gacha_old_ruler` 而非 `temp`)
- 在 `hidden_effect` 结束前必须清理所有自定义Scope

---

## 学到的原则

1. **清理即正义**: 任何 `save_scope_as` 必须有对应的 `clear_saved_scope`
2. **检查所有分支**: `if/else` 每个分支都要检查清理逻辑
3. **先清理后触发**: Event 触发前完成所有Scope清理
4. **嵌套要小心**: 由内向外清理嵌套的Scope
5. **命名要清晰**: 使用描述性名称而非 `temp`/`char`

---

## 参考
- 原始Spec: `spec/spec_scope_management.md` (现已重构)
- 官方文档: [EU5 Wiki - Scope](https://eu5.paradoxwikis.com/Scope)
- 相关文件: `in_game/common/character_interactions/gacha_regency_interactions.txt`
