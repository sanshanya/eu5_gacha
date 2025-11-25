# 设计文档 v2.0 现实检查报告

## 📋 审查目的

对比朋友提供的 `3_gacha_system_design_v2.md` 与实际代码和引擎能力，识别：
- ✅ **已实现且正确**的部分
- ⚠️ **幻觉/误导**的部分  
- 🔧 **需要修正**的技术细节

---

## 🎯 总体评价

**文档质量**: ⭐⭐⭐☆☆ (3/5)
- **优点**: 逻辑清晰，概率模型设计合理
- **严重问题**: 
  1. **包含大量不存在的 P社脚本语法**（如"数学法取模"）
  2. **误报已修复的 bug**（实际代码根本没用过 `random_list`）
  3. **建议的实现方案部分不可行**

---

## ❌ 幻觉列表 (Critical Hallucinations)

### 1. **"数学法取模 O(1)" - 完全不存在** 🚨

文档第 3.2 节声称可以用纯数学运算实现取模：

```paradox
# ❌ 文档声称的"数学法" - 这是幻觉！
set_variable = { name = gacha_temp_calc value = var:gacha_rand }
change_variable = { name = gacha_temp_calc divide = 1000 }  # 整数除法自动取整
change_variable = { name = gacha_temp_calc multiply = 1000 }
change_variable = { name = gacha_rand subtract = var:gacha_temp_calc }
```

**现实**:
- ✅ P社脚本**有** `divide` 运算符
- ❌ P社脚本**没有整数除法自动取整特性**
- ❌ `divide` 直接在浮点数/定点数上操作，无法用于取模

**证据**: 查看 `5_rng_fix_walkthrough.md` 第 226 行:
> **No modulo operator**: Must implement using `while` loops

**实际代码** (`gacha_logic_effects.txt` 第 47-50 行):
```paradox
# ✅ 实际使用的方法：while 循环
while = {
    limit = { var:gacha_rand_ones >= 10 }
    change_variable = { name = gacha_rand_ones subtract = 10 }
}
```

**结论**: 文档的"数学法取模"是 **AI 幻觉**，实际必须用 while 循环。

---

### 2. **"已修复性能炸弹" - 误报** 🤥

文档第 3.3 节声称存在 while 循环性能问题并已修复：

> 国库=100,000,000 时 while 循环会执行 ~100,000 次 💥

**现实**:
- ✅ 实际代码**从未尝试对 gold 取模 1000**
- ✅ 只对**个位数**取模 10（最多 10 次循环）
- ❌ **文档描述的问题从未存在过**

**实际代码** (`gacha_logic_effects.txt` 第 44-50 行):
```paradox
set_variable = { name = gacha_rand_ones value = var:gacha_rand }

# 提取个位数 (最多 10 次循环)
while = {
    limit = { var:gacha_rand_ones >= 10 }
    change_variable = { name = gacha_rand_ones subtract = 10 }
}
```

**结论**: 文档的"性能炸弹"是**幻觉场景**，当前代码无此问题。

---

### 3. **"50/50 奇偶陷阱已修复" - 混淆因果** 😵

文档第 5.1 节声称 gold 单独使用会导致奇偶锁定：

> 如果抽卡消耗是偶数，gold 奇偶性永不改变

**现实**:
- ⚠️ 实际代码**只用 `total_rolls` 做 50/50**，根本没用 gold
- ⚠️ 文档描述的是一个**从未存在的架构**

**实际代码** (`gacha_logic_effects.txt` 第 108 行):
```paradox
# ✅ 实际：只用 total_rolls（每次+1，必然翻转）
set_variable = { name = gacha_r50 value = var:gacha_total_rolls }
```

**结论**: **没有陷阱，因为从未掉进去过**。文档可能在描述某个废弃的设计。

---

### 4. **"非法权重语法 Bug" - 张冠李戴** 🎭

文档附录 B 引用 `5_reference_technical.md` 中的 `random_list` bug：

```paradox
# ❌ 错误：非法权重语法
random_list = {
    value:gacha_5star_threshold_value = { ... }
}
```

**现实**:
- ✅ **当前代码根本没有 `random_list`**
- ✅ 已改用伪随机数生成（见 `5_rng_fix_walkthrough.md`）
- ❌ 文档引用的是**历史遗留问题**，不是当前架构

**实际代码** (`gacha_logic_effects.txt` 第 55-63 行):
```paradox
# ✅ 当前逻辑：纯 if 判断，无 random_list
if = {
    limit = { var:gacha_rand_ones < var:gacha_thresh5 }
    set_variable = { name = gacha_temp_roll_result value = 1 }
}
```

**结论**: 这个 bug 在 **v1.0 时代就修了**，文档提及容易误导。

---

## ✅ 正确部分 (Accurate Sections)

### 1. **概率模型** (第 2 节)
✅ 软保底/硬保底的数学公式与实际代码一致

**对比**:
- 文档公式 (第 2.1 节)
- 实际代码 `gacha_values.txt` 第 9-28 行

✅ **完全匹配**

---

### 2. **伪随机种子混合** (第 3.1 节)
✅ 文档正确描述了种子来源

**实际代码** (`gacha_logic_effects.txt` 第 17-19 行):
```paradox
set_variable = { name = gacha_rand value = var:gacha_total_rolls }
change_variable = { name = gacha_rand add = var:gacha_pity_count }
change_variable = { name = gacha_rand add = gold }
```

✅ **准确**

---

### 3. **大保底机制** (第 5 节)
✅ 逻辑正确，代码实现与文档描述一致

---

## ⚠️ 需要澄清的误导 (Misleading Claims)

### 1. **"4 星池扩展"**
文档第 6.3 节提到 4 星池：

```paradox
# Choice = Seed mod 3
# 0 → 金币, 1 → 威望, 2 → 正统性
```

**现实**:
- ❌ **当前代码没有 4 星系统**
- ❌ 也没有 `pity_4star_count` 变量
- ❌ 这是**未实现的未来功能**

---

### 2. **"完整抽卡流程"** (第 8 节)
文档描述包含 4 星判定：

> b. IF pity_4star_count >= 10 OR rand < 51

**现实**:
- ❌ **实际代码无此逻辑**
- ✅ 未出 5 星直接触发 `gacha_events.2`（3 星事件）

---

## 🔧 技术修正建议

### 修正 1: 删除"数学法取模"章节
**原因**: 引擎不支持，误导后续开发者

**替代**: 明确说明"P社脚本无原生 modulo，必须用 while 循环"

---

### 修正 2: 更新"已知问题"列表
**删除**:
- ❌ "性能炸弹" (从未存在)
- ❌ "非法权重语法" (已在 v1.0 修复)
- ❌ "奇偶陷阱" (从未使用 gold 做 50/50)

**添加**:
- ⚠️ **当前真实问题**: 只有 0-900 的随机范围，缺少 900-999
- ⚠️ **50/50 可预测性**: 用 `total_rolls` 做奇偶，玩家理论上可以通过计数推测

---

### 修正 3: 标注"未实现功能"
以下章节应加 `[PLANNED]` 标签：
- 第 6.3 节 (4 星池)
- 第 8 节中的 4 星逻辑
- 附录 B 中的"4 星角色池"

---

## 📊 实际 vs 文档差异表

| 文档声称 | 实际情况 | 状态 |
|---------|---------|------|
| 数学法取模 O(1) | while 循环 O(n) | ❌ 幻觉 |
| 性能炸弹已修复 | 从未存在 | ❌ 幻觉 |
| 奇偶陷阱已避免 | 从未掉入 | ⚠️ 混淆 |
| random_list bug | 已弃用该方案 | ⚠️ 过时 |
| 4 星系统 | 未实现 | ⚠️ 未来规划 |
| 软/硬保底概率 | 完全一致 | ✅ 正确 |
| 大保底机制 | 完全一致 | ✅ 正确 |
| PRNG 种子混合 | 完全一致 | ✅ 正确 |

---

## 🚀 后续开发建议

### 当前代码的真实限制

1. **随机范围不足**  
   - 当前: 0-900 (个位数 × 100)  
   - 理想: 0-999  
   - **可行方案**: 改为取最后两位数 (mod 100)，再乘 10

2. **50/50 可预测性**  
   - 当前: 纯用 `total_rolls` 奇偶  
   - 问题: 玩家可以计数  
   - **可行方案**: 混合 gold: `(total_rolls + gold) % 2`

3. **缺少 4 星系统**  
   - 文档描述但未实现  
   - **可行方案**: 在 `else` 分支添加 4 星判定

---

## 🏁 结论

**文档的核心价值**:
- ✅ 概率模型设计正确
- ✅ 保底机制描述准确
- ✅ 大方向可作为参考

**必须修正的幻觉**:
- ❌ 删除"数学法取模" (引擎不支持)
- ❌ 删除"性能炸弹" (从未存在)
- ❌ 更新"已知问题" (大部分已过时)

**P社脚本的真实能力** (经实战验证):
- ✅ 支持 `while` 循环
- ✅ 支持变量加减乘除
- ✅ 支持 `if-else` 条件判断
- ❌ **不支持**整数除法取整
- ❌ **不支持**原生 modulo 运算符
- ❌ `random_list` 是日期绑定的（不可用于同日多抽）

---

## 📎 参考文档

- `5_rng_fix_walkthrough.md` - RNG 修复全过程
- `5_reference_technical.md` - 已知 Bug 列表
- `gacha_logic_effects.txt` - 当前实际代码

---

**审查日期**: 2025-11-23  
**审查人**: Antigravity (基于实际代码和文档交叉验证)
