# 抽卡系统完整设计文档 v2.0

# 注意本文档里充满幻觉比如mod是否能实现之类的

## 概览 (Overview)

本文档描述 EU5 Gacha Mod 的完整抽卡系统设计，包括概率计算、随机数生成、保底机制、奖池架构。

---

## 1. 核心变量 (Core Variables)

| 变量名                     | 类型    | 说明                |
| -------------------------- | ------- | ------------------- |
| `gacha_pity_count`       | Integer | 5星保底计数 (0-89)  |
| `gacha_pity_4star_count` | Integer | 4星保底计数 (0-10)  |
| `gacha_total_rolls`      | Integer | 累计抽卡总次数      |
| `gacha_is_guaranteed`    | Boolean | 大保底标识 (yes/no) |
| `gacha_rand`             | Integer | 伪随机数 (0-999)    |
| `gacha_thresh5`          | Integer | 5星阈值 (6-1000)    |

---

## 2. 概率模型 (Probability Model)

### 2.1 五星概率

| 抽数范围 | 基础概率 | 软保底增量 | 实际概率                |
| -------- | -------- | ---------- | ----------------------- |
| 0-72     | 0.6%     | -          | 0.6%                    |
| 73       | 0.6%     | +6%        | 6.6%                    |
| 74       | 0.6%     | +12%       | 12.6%                   |
| ...      | ...      | ...        | ...                     |
| 89       | -        | -          | **100%** (硬保底) |

**公式 (Implementation):**

```paradox
gacha_5star_threshold_value = {
    value = 6  # 基础 0.6% (6/1000)
  
    # 软保底: 73+ 每抽 +6%
    if = {
        limit = { var:gacha_pity_count >= 73 }
        add = {
            value = var:gacha_pity_count
            subtract = 73
            multiply = 60  # 每抽 +60/1000 = +6%
        }
    }
  
    # 硬保底: 89+ 强制 100%
    if = {
        limit = { var:gacha_pity_count >= 89 }
        set = 1000
    }
}
```

### 2.2 四星概率

| 条件          | 概率           |
| ------------- | -------------- |
| 基础概率      | 5.1% (51/1000) |
| 硬保底 (10抽) | 100%           |

### 2.3 三星概率

**残余概率**: 100% - 5星概率 - 4星概率

---

## 3. 伪随机数生成 (PRNG)

### 3.1 设计要求

❌ **禁止使用**:

- `random_list` (与游戏日期绑定，导致可预测性)
- `while` 循环取模 (国库大值时性能崩溃)

✅ **采用方案**:

- **种子混合**: `total_rolls + pity_count + gold`
- **数学法取模**: `O(1)` 复杂度，无循环

### 3.2 实现代码

```paradox
# 步骤 1: 生成种子
set_variable = { name = gacha_rand value = var:gacha_total_rolls }
change_variable = { name = gacha_rand add = var:gacha_pity_count }
change_variable = { name = gacha_rand add = gold }  # 动态组件

# 步骤 2: 数学法取模 1000 (O(1))
# 公式: Rand = Seed - (1000 * (Seed / 1000))
set_variable = { name = gacha_temp_calc value = var:gacha_rand }
change_variable = { name = gacha_temp_calc divide = 1000 }  # 整数除法自动取整
change_variable = { name = gacha_temp_calc multiply = 1000 }
change_variable = { name = gacha_rand subtract = var:gacha_temp_calc }
remove_variable = gacha_temp_calc

# 现在 gacha_rand ∈ [0, 999]
```

**性能对比**:

| 方法      | 国库=1000 | 国库=1,000,000 | 国库=100,000,000 |
| --------- | --------- | -------------- | ---------------- |
| while循环 | ~1次      | ~1000次        | ~100,000次 💥    |
| 数学法    | 4步       | 4步 ✅         | 4步 ✅           |

### 3.3 随机性验证

**种子变化性**:

- `total_rolls`: 每次抽卡 +1
- `pity_count`: 每次未中5星 +1
- `gold`: 受收入/支出/战争/建筑影响

**分布均匀性**:

- 1000 种可能结果 (0-999)
- 与阈值直接对比，无精度损失

---

## 4. 五星判定流程 (5-Star Logic)

```
开始抽卡
  ↓
生成 gacha_rand (0-999)
  ↓
获取 gacha_thresh5
  ↓
rand < thresh5?
  ├─ 是 → 触发5星动画事件 → gacha_handle_5star_outcome
  │         ├─ is_guaranteed? 是 → 必定UP (心海)
  │         └─ is_guaranteed? 否 → 50/50判定
  │                              ├─ 偶数 → UP (心海)
  │                              └─ 奇数 → 常驻 (雷电) + 设置 is_guaranteed=yes
  │
  └─ 否 → pity_count + 1 → 检查4星
```

---

## 5. 50/50 机制 (UP vs Standard)

### 5.1 问题：奇偶性陷阱

❌ **错误实现**:

```paradox
# 只用 gold
set_variable = { name = gacha_r50 value = gold }
# 取模 2...
```

**问题**: 如果抽卡消耗是偶数 (100金)，gold 奇偶性永不改变 → 玩家永远歪或永不歪。

### 5.2 正确实现

✅ **修复方案**: 混合 `gold + total_rolls`

```paradox
# 混合种子 (关键：total_rolls 每次+1，打破锁定)
set_variable = { name = gacha_r50 value = gold }
change_variable = { name = gacha_r50 add = var:gacha_total_rolls }

# 数学法取模 2
set_variable = { name = gacha_r50_calc value = var:gacha_r50 }
change_variable = { name = gacha_r50_calc divide = 2 }
change_variable = { name = gacha_r50_calc multiply = 2 }
change_variable = { name = gacha_r50 subtract = var:gacha_r50_calc }
remove_variable = gacha_r50_calc

# gacha_r50 = 0 (偶数) → UP
# gacha_r50 = 1 (奇数) → 常驻
```

**验证表格**:

| 抽数 | gold | total_rolls | 种子和 | mod 2 | 结果 |
| ---- | ---- | ----------- | ------ | ----- | ---- |
| 1    | 1001 | 1           | 1002   | 0     | UP   |
| 2    | 901  | 2           | 903    | 1     | 歪   |
| 3    | 801  | 3           | 804    | 0     | UP   |

→ **奇偶性每次翻转，保证公平性**

---

## 6. 奖池架构 (Pool Architecture)

### 6.1 五星池

```paradox
# 在 gacha_handle_5star_outcome 中处理
if = { limit = { var:gacha_is_guaranteed = 1 }
    gacha_create_xinhai_effect = yes  # 必定UP
}
else = {
    # 50/50 (见上节)
}
```

### 6.2 五星常驻池

```paradox
gacha_standard_5star_pool = {
    # 目前只有雷电将军
    gacha_create_raiden_effect = yes
  
    # 未来扩展: 使用 (gold + total_rolls) mod N
    # if = { limit = { var:choice = 0 } ... }
}
```

### 6.3 四星池

```paradox
gacha_4star_pool = {
    # Seed = gold + total_rolls
    # Choice = Seed mod 3
    # 0 → 金币, 1 → 威望, 2 → 正统性
}
```

---

## 7. 保底机制 (Pity System)

### 7.1 五星保底

| 类型   | 触发条件 | 重置条件   |
| ------ | -------- | ---------- |
| 软保底 | 73+      | 获得5星    |
| 硬保底 | 89+      | 获得5星    |
| 大保底 | 歪了之后 | 获得UP角色 |

**特殊规则**: 5星不重置4星保底 (只延后)

### 7.2 四星保底

| 类型   | 触发条件 | 重置条件 |
| ------ | -------- | -------- |
| 硬保底 | 10抽     | 获得4星  |

**独立计数**: 与5星保底互不影响

---

## 8. 完整抽卡流程

```
1. 初始化变量 (pity_count, total_rolls, pity_4star_count)
2. total_rolls + 1, pity_4star_count + 1
3. 生成伪随机数 gacha_rand ∈ [0, 999]
4. 计算5星阈值 gacha_thresh5
5. IF rand < thresh5:
   a. 触发5星动画事件 (gacha_events.5)
   b. 事件选项调用 gacha_handle_5star_outcome
   c. 判定UP/常驻
   d. 重置 pity_count = 0
6. ELSE (未中5星):
   a. pity_count + 1
   b. IF pity_4star_count >= 10 OR rand < 51:
      - 调用 gacha_4star_pool
      - 重置 pity_4star_count = 0
   c. ELSE:
      - 触发3星事件 (gacha_events.2)
```

---

## 9. 关键文件映射

| 文件                        | 职责                         |
| --------------------------- | ---------------------------- |
| `gacha_logic_effects.txt` | 核心抽卡逻辑、PRNG、判定流程 |
| `gacha_pools.txt`         | 奖池定义 (5星常驻、4星)      |
| `gacha_values.txt`        | 5星概率计算 (软保底/硬保底)  |
| `gacha_events.txt`        | 事件定义 (动画、结果、奖励)  |

---

## 10. 测试验证清单

- [ ] **基础概率**: 100 次抽卡 (pity 0-72) → ~0.6% 5星
- [ ] **软保底**: pity=73 单抽 → ~6.6% 5星
- [ ] **硬保底**: pity=89 单抽 → 100% 5星
- [ ] **4星保底**: 连续 10 抽无5星 → 必出4星
- [ ] **50/50 公平性**: 100 次5星 → ~50% UP, ~50% 常驻
- [ ] **大保底**: 歪了之后再中5星 → 必定UP
- [ ] **性能测试**: 国库 1,000,000+ → 无卡顿
- [ ] **奇偶陷阱**: 连续抽卡 → 结果应随机变化

---

## 附录 A: 概率期望计算

**平均5星出货抽数** (有软保底):

- 期望值 ≈ 62.5 抽

**最差情况** (欧皇):

- 硬保底 90 抽

**大保底期望**:

- 2 次5星必得1个UP
- 期望 UP 抽数 ≈ 125 抽

---

## 附录 B: 已知问题与未来优化

### 已修复

- ✅ 性能炸弹 (while 循环)
- ✅ 奇偶陷阱 (50/50 锁定)
- ✅ random_list 日期绑定

### 未来优化

- [ ] 添加更多5星常驻角色 (需实现 mod N 选择逻辑)
- [ ] 4星角色池 (目前只有资源奖励)
- [ ] 抽卡历史记录 (用于debug)
