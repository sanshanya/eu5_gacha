# Gacha System Bug History

> **Status**: 归档 - 所有问题已修复  
> **Purpose**: 记录抽卡系统历史 Bug 及修复过程，供后人参考  
> **Last Updated**: 2025-11-25

---

## Overview

本文档记录了抽卡系统开发过程中遇到的所有重大 Bug。所有问题均已修复，本文档仅作历史参考。

**Bug 分类**:
- 🔴 严重: 核心功能失效
- 🟡 中等: 部分功能异常
- 🟢 已修复: 所有 Bug 均已修复

---

## Bug Timeline

### Bug #1: 随机数生成器失效 🟢 FIXED
**日期**: 2025-11-23  
**严重程度**: 严重

**表现**:
- 随机数永远等于5
- 所有抽卡都出5星

**根本原因**:
```paradox
# 旧代码: 随机数永远=5
rand = total_rolls + treasury + pity_count
     = 5 + 0 + 0 = 5

# 阈值 = 6 (0.6%)
# 判定: 5 < 6 → 永远出5星！
```

**修复方案**:
- 使用质数混合 + 固定偏移937
- 添加多个熵源（total_rolls×17, treasury, pity×13, block×7）
- 确保随机数在0-999范围均匀分布

**修复后代码**:
```paradox
set_variable = { name = gacha_rand value = 937 }
change_variable = { 
    name = gacha_rand 
    add = { value = var:gacha_total_rolls multiply = 17 }
}
change_variable = { name = gacha_rand add = abs_treasury }
change_variable = { 
    name = gacha_rand 
    add = { value = var:gacha_pity_count multiply = 13 }
}
change_variable = { 
    name = gacha_rand 
    add = { value = var:gacha_block_index multiply = 7 }
}
change_variable = { name = gacha_rand modulo = 1000 }
```

**文件**: `in_game/common/scripted_effects/gacha_logic_effects.txt:34-76`

---

### Bug #2: 硬保底失效 🟢 FIXED
**日期**: 2025-11-23  
**严重程度**: 严重

**表现**:
- 90抽未必出5星
- 保底计数超过91仍未出货

**根本原因**:
```paradox
# script_value在effects中返回none
gacha_curr_thresh5 = script_value:gacha_5star_threshold_value
# 结果: gacha_curr_thresh5 = none

# 判定失效
if (rand < none) → 永远false
```

**底层原因**: EU5 引擎不支持在 `scripted_effects` 中使用 `script_value:` 前缀访问 Script Values。

**修复方案**:
- 放弃 `script_value`，直接内联计算概率阈值
- 第90抽时强制设置阈值为1000（100%）

**修复后代码**:
```paradox
# 硬保底
if = {
    limit = { var:gacha_pity_count >= 89 }
    set_variable = { name = gacha_curr_thresh5 value = 1000 }  # 100%
}
else_if = {
    limit = { var:gacha_pity_count >= 73 }
    # 软保底计算...
}
else = {
    set_variable = { name = gacha_curr_thresh5 value = 6 }  # 0.6%
}
```

**文件**: `in_game/common/scripted_effects/gacha_logic_effects.txt:78-95`

**教训**: 
- ✅ Script Values 只能在 Triggers 和其他 Script Values 中使用
- ❌ 不能在 Effects 中动态访问
- 📖 详见 `spec_engine_basics.md` §2.2

---

### Bug #3: 块内保底失效 🟢 FIXED
**日期**: 2025-11-23  
**严重程度**: 高

**表现**:
- 10抽可能全是3星
- 块内保底机制完全无效

**根本原因**:
```paradox
# 使用了未定义的变量
limit = { var:gacha_block_index = 0 }  # block_index从未计算！
```

**修复方案**:
1. 初始化 `gacha_block_has_4star = 0`
2. 每抽计算 `block_index = total_rolls mod 10`
3. 每个新块重置标记

**修复后代码**:
```paradox
# 步骤1: 计算块索引
set_variable = { 
    name = gacha_block_index 
    value = var:gacha_total_rolls 
}
change_variable = { 
    name = gacha_block_index 
    modulo = 10 
}

# 步骤2: 新块重置标记
if = {
    limit = { var:gacha_block_index = 0 }
    set_variable = { name = gacha_block_has_4star value = 0 }
}

# 步骤3: 第10抽检查
if = {
    limit = { 
        var:gacha_block_index = 0 
        var:gacha_block_has_4star = 0 
    }
    set_variable = { name = gacha_is_4star_win value = yes }  # 强制4星
}
```

**文件**: `in_game/common/scripted_effects/gacha_logic_effects.txt:8, 21-32`

---

### Bug #4: 负金币影响随机数 🟢 FIXED
**日期**: 2025-11-23  
**严重程度**: 中

**表现**:
- 负金币时随机数偏小
- 轻微影响概率分布

**根本原因**:
```paradox
# 直接加上treasury
change_variable = { name = gacha_rand add = treasury }
# 如果treasury=-500，rand会减少500
```

**修复方案**:
- 使用 treasury 的绝对值
- 负数时先×(-1)再加到 rand

**修复后代码**:
```paradox
# 计算绝对值
set_variable = { name = abs_treasury value = treasury }
if = {
    limit = { treasury < 0 }
    change_variable = { name = abs_treasury multiply = -1 }
}

# 加入随机数池
change_variable = { name = gacha_rand add = var:abs_treasury }
```

**文件**: `in_game/common/scripted_effects/gacha_logic_effects.txt:44-54`

---

### Bug #5: 4星奖励池随机数源错误 🟢 FIXED
**日期**: 2025-11-23  
**严重程度**: 中

**表现**:
- 4星奖励可能不随机
- error.log 报错变量不存在

**根本原因**:
```paradox
# 使用了不存在的变量
set_variable = { name = gacha_4star_choice value = var:gacha_rand_ones }
# gacha_rand_ones从未定义！
```

**修复方案**:
- 改用已存在的 `gacha_rand`
- 通过 mod 3 来随机选择奖励类型（金币/威望/正统性）

**修复后代码**:
```paradox
set_variable = { 
    name = gacha_4star_choice 
    value = var:gacha_rand 
}
change_variable = { 
    name = gacha_4star_choice 
    modulo = 3 
}

# 0=金币, 1=威望, 2=正统性
if = { limit = { var:gacha_4star_choice = 0 } add_gold = 100 }
else_if = { limit = { var:gacha_4star_choice = 1 } add_prestige = 50 }
else = { add_legitimacy = 10 }
```

**文件**: `in_game/common/scripted_effects/gacha_pools.txt:19`

---

### Bug #6: 事件顺序错误 🟢 FIXED
**日期**: 早期版本  
**严重程度**: 中

**表现**:
- 5星抽卡时，角色事件先于金光事件弹出
- 顺序不符合原神体验（应该先金光→再角色）

**根本原因**:
- Silent内核错误地调用了 `gacha_handle_5star_outcome`
- 导致角色在金光演出前就发放

**修复方案**:
- Silent内核只负责计算和更新保底计数，**不发放**5星角色
- 角色发放移到 `gacha_events.txt event.5` 的 option 中

**架构调整**:
```
修复前:
Silent内核 → 发放角色 → 触发金光事件

修复后:
Silent内核 → 重置pity → 触发金光事件 → 玩家点击 → 发放角色
```

**修复后代码**:
```paradox
# gacha_logic_effects.txt - Silent内核
gacha_execute_single_roll_silent = {
    # ... 计算逻辑 ...
    
    if = {
        limit = { var:gacha_tier = 2 }  # 5星
        set_variable = { name = gacha_pity_count value = 0 }
        # ❌ 删除: gacha_handle_5star_outcome = yes
        # ✅ 只重置pity，不发放角色
    }
}

# gacha_events.txt - Event层
gacha_events.5 = {
    title = "金光闪耀！"
    option = {
        name = "揭示命运..."
        gacha_handle_5star_outcome = yes  # ✅ 在这里发放角色
    }
}
```

**文件**: 
- `in_game/common/scripted_effects/gacha_logic_effects.txt:146-149`
- `in_game/events/gacha_events.txt:140-158`

---

## Lessons Learned

### 1. Script Value 的作用域限制
> **[ENGINE]** Script Values 不能在 Effects 中动态访问（会返回 `none`）。

**正确用法**:
- ✅ 在 Triggers 中: `trigger = { script_value:foo > 10 }`
- ✅ 在其他 Script Values 中: `value = script_value:bar`
- ❌ 在 Effects 中: `set_variable = { value = script_value:foo }`

**解决方案**: 直接内联计算，或预先在 Trigger 中计算后保存到变量。

---

### 2. 变量初始化的重要性
所有变量在使用前**必须**初始化，即使默认值为0。

**错误示例**:
```paradox
if = { limit = { var:foo = 0 } ... }  # 如果foo未初始化，limit失败
```

**正确模式**:
```paradox
# 初始化
set_variable = { name = foo value = 0 }

# 使用
if = { limit = { var:foo = 0 } ... }
```

---

### 3. Silent Core 架构模式
**原则**: 计算与展示分离

| 层次 | 职责 | 禁止操作 |
|:---|:---|:---|
| Silent内核 | 计算、更新状态 | 发放奖励、触发UI事件 |
| Event层 | UI展示、玩家交互 | 概率计算、保底逻辑 |

**好处**:
- 逻辑清晰，易于调试
- 单抽/十连可复用同一内核
- Event 可独立测试 UI/UX

---

### 4. 随机数生成的熵源
单一熵源（如只用 `total_rolls`）会导致可预测性。

**推荐模式**:
```paradox
rand = 固定偏移 + 质数1×熵源1 + 熵源2 + 质数2×熵源3 + ...
rand = rand mod 范围
```

**本项目实现**:
```paradox
rand = 937 + 17×total_rolls + |treasury| + 13×pity + 7×block_index
rand = rand mod 1000
```

---

## 统计数据

| 指标 | 数值 |
|:---|:---:|
| **总Bug数** | 6 |
| **严重Bug** | 3 (50%) |
| **中等Bug** | 3 (50%) |
| **平均修复时间** | 1-2小时 |
| **最难调试** | Bug #2 (Script Value限制) |

---

## 相关文档

- **规范**: [spec_gacha_system.md](../spec/spec_gacha_system.md) - 当前规范
- **设计**: [design_gacha_design_decisions.md](../design/design_gacha_design_decisions.md) - 设计决策
- **引擎**: [spec_engine_basics.md](../spec/spec_engine_basics.md) - Script Value 机制
- **调试**: [spec_debugging.md](../spec/spec_debugging.md) - 调试技巧

---

**文档维护者**: AI + sansm  
**归档日期**: 2025-11-25
