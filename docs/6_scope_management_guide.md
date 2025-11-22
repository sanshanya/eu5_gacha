# EU5 作用域管理规范 - 从RNG调试与Dynasty Bug中总结的经验

## 📚 概述

在EU5 Gacha系统的开发过程中，我们多次遇到作用域相关的问题。本文档总结了这些经验教训，提供明确的规范和最佳实践。

---

## ⚠️ 紧急警告：不要忘记清理作用域！(Don't Forget to Clear Scopes!)

**这是最重要的一条规则**：任何 `save_scope_as` 必须有对应的 `clear_saved_scope`。

### 🩸 血淋淋的教训：Dynasty Inheritance Bug
**现象**: 第二个抽到的角色（如心海）错误地继承了第一个角色（如雷电）的姓氏（变成了"胡心海"）。
**原因**: 在处理重复抽卡逻辑时，进入 `else` 分支（归属权冲突）后，**忘记清理 `existing_char` 作用域**。导致下一次抽卡时，引擎错误地复用了未清理的作用域上下文。

**错误代码**:
```paradox
if = {
    limit = { ... }
    # 正常逻辑
    clear_saved_scope = existing_char  # ✅ 这里清理了
}
else = {
    # 异常分支 (归属权冲突)
    add_gold = 100
    # ❌ 忘记清理 existing_char！
    # 下次抽卡时，existing_char 仍然指向这个旧角色，导致严重Bug
}
```

**正确代码**:
```paradox
else = {
    add_gold = 100
    # ✅ 必须清理！无论在哪个分支！
    clear_saved_scope = existing_char
}
```

---

## 🎯 核心原则

### 原则 1: 谁触发事件，谁出现在UI
**规则**: 事件会在**当前作用域**的上下文中显示UI元素。

**示例**:
```paradox
# ❌ 错误：临时角色会出现在事件中
create_character = {
    save_scope_as = temp_char
}
scope:temp_char = {
    root = {
        trigger_event_non_silently = { id = my_event.1 }
    }
}
# 此时 temp_char 还活着，会显示在事件UI中
```

```paradox
# ✅ 正确：先清理再触发
create_character = {
    save_scope_as = temp_char
}
scope:temp_char = {
    # 做一些逻辑...
}
kill_character = { target = scope:temp_char }
clear_saved_scope = temp_char

# 现在触发事件，temp_char 已经不存在了
root = {
    trigger_event_non_silently = { id = my_event.1 }
}
```

---

### 原则 2: 作用域切换必须清理
**规则**: 每次使用 `save_scope_as` 后，必须在不再需要时调用 `clear_saved_scope`。

**模式**:
```paradox
# 创建并保存作用域
create_character = {
    save_scope_as = my_temp_scope
}

# 使用作用域
scope:my_temp_scope = {
    # 做一些事情...
}

# !!! 关键 !!! 清理作用域
kill_character = { target = scope:my_temp_scope }  # 如果是角色
clear_saved_scope = my_temp_scope
```

**原因**:
- 防止内存泄漏
- 防止作用域引用已死亡/无效的对象
- 防止后续代码错误地引用旧作用域（如Dynasty Bug）

---

### 原则 3: `root` 始终指向调用者
**规则**: 在嵌套作用域中，`root` 始终指向**最外层的调用作用域**（通常是国家）。

**示例**:
```paradox
# 国家作用域 (this = DAI)
gacha_execute_single_roll = {
    # root = DAI, this = DAI
    
    create_character = {
        save_scope_as = temp_char
    }
    
    scope:temp_char = {
        # root = DAI (原始调用者)
        # this = temp_char (当前作用域)
        
        root = {
            # 现在 this = DAI
            set_variable = { name = some_var value = 1 }
        }
    }
}
```

---

## 🔴 常见错误模式

### 错误 1: 在角色作用域中触发国家事件
**问题**:
```paradox
scope:temp_char = {
    # ❌ 错误：在角色作用域触发country_event
    trigger_event_non_silently = { id = my_event.1 }
}
```

**表现**: 事件不触发，或者触发但上下文错误

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

# 太晚了！事件已经触发，temp_char 会出现在UI中
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
add_trait = some_trait  # 这是角色effect！
```

**修复**:
```paradox
# ✅ 检查文档确认支持的作用域
# 如果需要角色作用域：
random_character = {
    add_trait = some_trait
}
```

---

## ✅ 最佳实践模式

### 模式 1: 临时角色模式 (已弃用，但作为反面教材)
```paradox
gacha_execute_single_roll = {
    # 1. 创建临时角色
    create_character = {
        first_name = temp_name
        age = 18
        create_in_limbo = yes
        save_scope_as = temp_char
    }
    
    # 2. 在临时角色作用域执行逻辑
    scope:temp_char = {
        random_list = {
            50 = {
                root = { set_variable = { name = result value = 1 } }
            }
            50 = {
                root = { set_variable = { name = result value = 0 } }
            }
        }
    }
    
    # 3. !!! 关键 !!! 先清理，再处理结果
    kill_character = { target = scope:temp_char }
    clear_saved_scope = temp_char
    
    # 4. 根据结果执行后续逻辑（包括触发事件）
    if = {
        limit = { var:result = 1 }
        trigger_event_non_silently = { id = success_event.1 }
    }
}
```

**为什么这个模式失败了**:
- `random_list` 在EU5中是日期锁定的，与作用域无关
- 但这个模式展示了正确的作用域清理顺序

---

### 模式 2: 存在的角色模式
```paradox
gacha_execute_single_roll = {
    # 1. 选择一个存在的角色
    random_character = {
        limit = { is_alive = yes }
        save_scope_as = random_char
    }
    
    # 2. 在该角色作用域执行逻辑
    scope:random_char = {
        # 做一些事情...
        root = { set_variable = { name = result value = 1 } }
    }
    
    # 3. 清理作用域引用（不需要kill，因为不是临时创建的）
    clear_saved_scope = random_char
    
    # 4. 触发事件
    trigger_event_non_silently = { id = my_event.1 }
}
```

---

### 模式 3: 纯国家作用域模式 (当前使用)
```paradox
gacha_execute_single_roll = {
    # 所有逻辑都在国家作用域执行
    # 不创建临时角色，不切换作用域
    
    # 1. 计算伪随机数
    set_variable = { name = rand value = treasury }
    change_variable = { name = rand add = var:total_rolls }
    
    # 2. 判断结果
    if = {
        limit = { var:rand < 100 }
        set_variable = { name = result value = 1 }
    }
    
    # 3. 直接触发事件（无需担心作用域问题）
    trigger_event_non_silently = { id = my_event.1 }
}
```

**优点**:
- 无作用域切换，无清理负担
- 代码简洁，不易出错
- 性能最优

---

## 📋 作用域清理检查清单

在编写涉及作用域切换的代码时，使用此检查清单：

- [ ] **创建时保存**: 每个 `create_X` 都配有 `save_scope_as`？
- [ ] **使用后清理**: 每个 `save_scope_as` 最终都有对应的 `clear_saved_scope`？
- [ ] **分支检查**: `if/else` 的所有分支都包含清理逻辑吗？(特别是异常分支！)
- [ ] **顺序正确**: 清理在事件触发**之前**？
- [ ] **角色已销毁**: 临时角色在清理作用域前已 `kill_character`？
- [ ] **类型匹配**: 在正确的作用域类型中调用effect？
- [ ] **返回正确**: 需要返回外层作用域时用了 `root`？

---

## 🎓 从RNG调试中学到的教训

### 教训 1: 不要过度依赖作用域切换
**问题**: 我们尝试通过创建大量临时角色来"欺骗"RNG系统。

**学到的**: 
- 作用域切换不影响 `random_list` 的结果（日期锁定）
- 简单的方案往往更好（纯国家作用域）

---

### 教训 2: 调试时保留中间变量
**问题**: 一开始我们清理所有临时变量，导致无法通过Debug Tool查看。

**学到的**:
```paradox
# ❌ 过度清理
remove_variable = gacha_rand
remove_variable = gacha_thresh5
remove_variable = gacha_result

# ✅ 保留关键变量用于调试
# gacha_rand, gacha_thresh5 保留
remove_variable = gacha_temp_result  # 只清理真正临时的
```

---

### 教训 3: 事件触发的作用域很敏感
**问题**: "死人出现在事件UI"

**学到的**:
- 事件UI会捕捉触发时所有活着的作用域引用
- 必须在触发事件**之前**完全清理不需要的角色

**正确做法**:
```paradox
# 1. 逻辑
scope:temp = { ... }

# 2. 清理 (关键!)
kill_character = { target = scope:temp }
clear_saved_scope = temp

# 3. 触发事件
trigger_event_non_silently = { id = event.1 }
```

---

## 🔧 调试作用域问题的技巧

### 技巧 1: 使用Debug Tool实时查看
- F12 打开Debug Tool
- 选择国家 → Script Variables
- 检查哪些变量/作用域还存活

### 技巧 2: 分步测试
```paradox
# 在每个关键步骤后触发测试事件
create_character = { save_scope_as = test }
trigger_event_non_silently = { id = debug_event.1 }  # 看看test是否出现

scope:test = { ... }
trigger_event_non_silently = { id = debug_event.2 }  # 再次检查

kill_character = { target = scope:test }
trigger_event_non_silently = { id = debug_event.3 }  # test应该消失了
```

### 技巧 3: 添加注释标记作用域
```paradox
# [SCOPE: country] START
gacha_execute_single_roll = {
    # [SCOPE: country] this = DAI
    
    create_character = { save_scope_as = temp }
    
    # [SCOPE: character] START
    scope:temp = {
        # [SCOPE: character] this = temp
        
        # [SCOPE: country] START (via root)
        root = {
            # [SCOPE: country] this = DAI (back to country)
        }
        # [SCOPE: country] END
    }
    # [SCOPE: character] END
    
    # [SCOPE: country] this = DAI (back automatically)
}
# [SCOPE: country] END
```

---

## 📊 作用域类型速查表

| 作用域类型 | 常见创建方式 | 常见切换方式 | 需要清理？ |
|----------|------------|------------|----------|
| `country` | 游戏自动 | - | ❌ |
| `character` | `create_character` | `scope:X`, `random_character` | ✅ (如果临时创建) |
| `province` | 游戏自动 | `capital_scope`, `random_owned_province` | ❌ |
| `saved scope` | `save_scope_as` | `scope:name` | ✅ (必须) |

---

## 🎯 总结

### 黄金规则
1. **创建谁，清理谁**: 创建的临时对象必须清理
2. **先清理，后触发**: 事件触发前完成所有清理
3. **检查所有分支**: `else` 分支也要清理！
4. **保持简单**: 能不切换作用域就不切换
5. **检查类型**: 确保在正确的作用域类型调用effect
6. **调试友好**: 保留关键变量，添加清晰注释

### 优先级
1. **最优**: 完全在国家作用域工作（当前方案）
2. **次优**: 使用现有对象的作用域（如random_character）
3. **避免**: 创建临时对象切换作用域（除非必要）

---

**记住**: 作用域就像房间，进去了就要出来，用完了就要打扫干净！🧹
