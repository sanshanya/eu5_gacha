# Technical Reference (技术参考)

> [!WARNING]
> **本文档包含混合内容**
> 
> 1. **引擎特性与限制**：关于本地化限制、Scope 作用域的部分仍然有效，可作为参考。
> 2. **已修复 Bug**：关于 RNG 修复等内容已过时，请参阅 `spec/spec_gacha_system.md` 获取最新实现。
> 
> 未来建议将有效部分拆分至 `spec/spec_engine_technical_notes.md`。
>
> <!-- TODO: Split this file into spec_engine_technical_notes.md (valid engine notes) and archive_technical_bugs_and_workarounds.md (old bugs) during a future documentation cleanup. -->

## 1. 重要教训：本地化限制 (Localization Limitations)

> [!CAUTION]
> **已证实无法实现的功能**

经过反复测试，已证实**无法在国家事件的描述文本（`desc`）中，通过任何已知语法动态显示一个由 `save_event_target` 传递的角色的名字**。

### 已尝试但失败的语法

以下语法均已测试，**全部无效**：

```yaml
# 尝试 1: Scope.Var 语法
[This.Var('variable_name').GetValue]
[Root.Var('variable_name').GetValue]

# 尝试 2: event_target 语法
[event_target:character_name.GetName]

# 尝试 3: scope 语法
[scope:character.GetName]
[sCharacter.GetName]
```

### 结果

游戏引擎不识别这些语法，只会显示：
- 错误代码原样输出
- 或回退为通用名词（如 "courtier"）

### 项目应对策略

因此，本项目中的事件描述必须：
- **使用静态文本**（例如直接写 "珊瑚宫心海"）
- **唯一能动态显示角色信息的地方**：事件窗口顶部的 UI 肖像区域（通过 `character = scope:character` 实现）

---

## 2. 已知核心 Bug 与故障排查 (Known Bugs & Troubleshooting)

### A. 事件选项消失 / 条件失效

**问题描述**：事件文件中的选项不显示，或条件判断完全失效。

**原因**：
- 缺少 `namespace` 声明
- 事件 ID 冲突

**解决方案**：
- ✅ 在事件文件顶部必须声明 `namespace = gacha_events`
- ✅ 确保每个事件 ID 在项目内唯一

---

### B. 模板参数失效 (The "Type Trap")

**问题描述**：尝试在 `scripted_effect` 中使用 `$parameter$` 传递复杂对象（如 `culture:han`）时失败。

**原因**：
- Jomini 引擎的模板系统只能处理**简单字符串**
- 无法传递类型化对象（如 `culture:xxx`、`trait:xxx`）

**解决方案**：
- ✅ 模板参数只用于传递简单标识符（如 `$who$ = xinhai`）
- ✅ 在角色专属的 Wrapper 文件（如 `gacha_xinhai_effects.txt`）中将复杂数据写死
- ✅ 通用逻辑使用 `if-else` 分支处理不同角色

**示例**：

```paradox
# ❌ 错误：尝试传递复杂对象
gacha_create_character_effect = {
    culture = $culture_type$  # 无法工作
}

# ✅ 正确：在 Wrapper 中写死
gacha_create_xinhai_effect = {
    gacha_create_character_template_effect = {
        who = xinhai
    }
    # 内部硬编码 culture:han
}
```

---

### C. 已知核心 Bug：抽卡概率系统失效 ⚠️

> [!WARNING]
> **这是当前项目中最严重的功能性 Bug**

**问题描述**：
- 点击"祈愿"按钮后，`gacha_execute_single_roll` 效果静默失败
- 不产生任何抽卡结果，既不触发 5 星事件，也不触发 4 星事件

**根本原因**：
- `in_game/common/scripted_effects/gacha_logic_effects.txt` 文件中的 `random_list` 使用了**非法的权重语法**
- 错误语法：`value:gacha_5star_threshold_value`
- 该语法为 AI 幻觉的产物，**不被游戏引擎支持**
- 导致整个 `random_list` 块解析失败，效果静默终止

**错误代码示例**（当前项目中的问题代码）：

```paradox
# ❌ 错误：非法权重语法
random_list = {
    value:gacha_5star_threshold_value = {  # 这个语法不存在！
        # 5星逻辑
    }
    value:gacha_5star_failure_value = {
        # 4星逻辑
    }
}
```

**后续计划**：
- 此问题将在未来的开发阶段被专门修复
- 正确的语法应为**直接使用 `script_value` 的名字作为权重**（例如 `gacha_5star_threshold_value = { ... }`）
- 但这需要进一步的测试和验证

**临时调试方案**：
- 使用事件中的"调试：直接获得【珊瑚宫心海】"选项绕过抽卡系统
- 测试角色创建、命座系统等其他功能

---

## 3. Scope 作用域最佳实践 (Scope Best Practices)

> [!TIP]
> **在 `script_value` 中避免使用 `root.var`**

### 问题

最初的代码中大量使用 `root.gacha_pity_count`，但这种写法在某些上下文中会失败。

### 正确做法

在 `script_value` 定义中，**直接读取当前作用域**的变量：

```paradox
# ✅ 正确
gacha_5star_threshold_value = {
    value = 6
    
    if = {
        limit = { gacha_pity_count >= 73 }  # 直接读取
        add = {
            value = gacha_pity_count
            subtract = 73
            multiply = 60
        }
    }
}

# ❌ 错误（可能导致作用域丢失）
gacha_5star_threshold_value = {
    value = 6
    
    if = {
        limit = { root = { gacha_pity_count >= 73 } }  # 过度嵌套
        add = {
            value = root.gacha_pity_count
            # ...
        }
    }
}
```

### 原因

`script_value` 在被调用时，其计算上下文已经是调用者的作用域（如国家），无需再通过 `root` 跳转。
