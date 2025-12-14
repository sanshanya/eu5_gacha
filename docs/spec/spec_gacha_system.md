# Gacha System Specification (抽卡系统规范)

> **Verified**: 2025-12-13 | 0.4.0 (V3)  
> **Purpose**: 定义抽卡系统的核心机制、概率模型与实现规范  
> **Characters**: 8位角色已实装 (详见 [spec_character_roster.md](spec_character_roster.md))

---

## Technical Details

### File Locations

| 类别 | 文件 | 说明 |
|:---|:---|:---|
| **抽卡入口** | `character_interactions/gacha_wish_interaction.txt` | 单抽/十连交互（含防连点锁） |
| **概率计算** | `script_values/gacha_eu_values.txt` | 阈值、RNG公式 |
| **核心逻辑** | `scripted_effects/gacha_logic_effects.txt` | Silent内核、池选择 |
| **公共效果** | `scripted_effects/gacha_common_effects.txt` | 初始化、注册、Estate分配 |
| **角色效果** | `scripted_effects/gacha_{char}_effects.txt` | 8角色专属Wrapper |
| **角色事件** | `events/gacha_{char}_events.txt` | 8角色故事链 |
| **主事件** | `events/gacha_events.txt` | 抽卡UI、结果展示 |
| **星辉事件** | `events/gacha_starlight_events.txt` | 星辉兑换系统 |

### Character Pool (角色池)

**UP池** (50%概率):
- 心海 (xinhai) - Index 0

**常驻池** (50%概率 / 歪了):
- 雷电 (raiden) - Index 1
- 刻晴 (keqing) - Index 2
- 芙宁娜 (furina) - Index 3
- 胡桃 (hutao) - Index 4
- 可莉 (klee) - Index 5
- 纳西妲 (nahida) - Index 6
- 菲谢尔 (fischl) - Index 7

### Key Data Structures

**Country Variables** (核心状态):
```paradox
set_variable = { name = gacha_total_rolls_count value = 0 }  # 总抽卡次数
set_variable = { name = gacha_pity_5star_count value = 0 }   # 5★保底计数 (0-89)
set_variable = { name = gacha_pity_4star_count value = 0 }   # 4★保底计数
set_variable = { name = gacha_is_guaranteed_bool value = 0 } # 大保底标记
set_variable = { name = gacha_starlight value = 0 }          # 星辉货币
set_variable = { name = gacha_event_lock value = yes }       # 交互事件锁（防连点）
```

**Legacy Global List**（已弃用）:
- `gacha_obtained_characters` 曾用于存“已获得角色”，但 **不要把 `Character` 存入 `global_variable_list`**（死亡后可能残留坏引用导致 CTD）。

**Current Pattern**（按 modifier 全局搜索）:
```paradox
random_country = {
  limit = { any_character = { is_alive = yes has_character_modifier = gacha_xinhai_modifier } }
  random_character = {
    limit = { is_alive = yes has_character_modifier = gacha_xinhai_modifier }
    save_scope_as = existing_char
  }
}
```

**Character Variables** (命之座):
```paradox
set_variable = { name = gacha_constellation_lvl value = 0 }  # 0-6
set_variable = { name = gacha_trait_id value = 1001 }        # 角色ID
```

### Dependencies

- **Required**: `spec_scope_management.md` - Scope清理规范
- **Required**: `spec_engine_basics.md` - Script Value机制
- **Optional**: `design_engine_pitfalls.md` - Random List陷阱

## Part 1: Probability Logic (概率逻辑)

我们采用 **"伪随机数生成 (PRNG) + 动态阈值判定"** 的逻辑，复刻《原神》的机制。

### 1. 核心变量

| 变量名 | 用途 | 范围 |
|--------|------|------|
| `gacha_total_rolls` | 总抽卡次数 | 0~∞ |
| `gacha_pity_count` | 5星保底计数 | 0~89 |
| `gacha_pity_4star` | 4星保底计数 | 0~9 |
| `gacha_block_has_4star` | 当前块是否已出4/5星 | yes/no |
| `gacha_is_guaranteed` | 大保底标识 | yes/no |

### 2. 概率模型

#### 5星概率
- **基础概率**: 0.6% (6/1000)
- **软保底 (Soft Pity)**: 从第74抽开始，每抽增加 6% 概率
- **硬保底 (Hard Pity)**: 第90抽概率为 100%

| 抽数 | 概率 | 累计期望 |
|------|------|----------|
| 1-73 | 0.6% | - |
| 74 | 6.6% | - |
| 80 | 42.6% | - |
| 90 | 100% | 保底 |

#### 4星概率
- **基础概率**: 5.1% (51/1000)
- **软保底**: 第9抽开始概率暴涨
- **块内保底**: 每10抽必有至少1个4星或5星

### 3. 随机数生成

**公式** (千分制):
```
rand = 937 + 17×total_rolls + |gold| + 13×pity_count + 7×block_index
rand = rand mod 1000
```

**熵源说明**:
- `937`: 质数偏移，确保初始值够大
- `17×total_rolls`: 线性增长因子
- `|gold|`: 国库金币的绝对值（避免负数影响）
- `13×pity_count`: 保底计数的质数混淆
- `7×block_index`: 块索引的质数混淆

### 4. 核心流程

```
1. Silent内核计算 (gacha_execute_single_roll_silent)
   ├─ 生成随机数 (0-999)
   ├─ 计算5星/4星阈值
   ├─ 判定结果 (tier: 0=3星, 1=4星, 2=5星)
   ├─ 更新保底计数
   └─ 发放4星奖励（5星延迟）

2. 事件触发 (gacha_execute_single_roll)
   ├─ 如果tier=2: 触发event.5（金光演出）
   ├─ 如果tier=1: 触发event.20（4星展示）
   └─ 如果tier=0: 触发event.2（凡铁）

3. 玩家确认 (event option)
   └─ event.5点击后才发放5星角色
```

---

## Part 2: Architecture (架构设计)

### 1. Silent内核模式

**设计原则**: 计算与展示分离

- **Silent内核** (`gacha_execute_single_roll_silent`):
  - 只负责计算和状态更新
  - 不触发任何事件
  - 不发放5星奖励

- **Event层**:
  - 负责UI展示
  - 发放5星角色（在option中）
  - 提供玩家交互

**好处**:
- 逻辑清晰，易于调试
- Silent内核可被单抽/十连复用
- 事件可独立测试

### 2. 十连优化

**设计**:
```
gacha_execute_ten_rolls {
    Loop 10次 {
        Silent内核计算
        If 5星 → 弹event.5
        If 4星 → 弹event.20
        If 3星 → 静默跳过
    }
    // 不再有十连结算页面
}
```

**特点**:
- 3星静默（不弹窗）
- 4/5星逐个弹窗
- 无金币限制（允许负金币）

### 3. 块内保底机制

**规则**: 每10抽至少1个4星或5星

**实现**:
```paradox
# 每抽计算块索引 (0-9)
block_index = total_rolls mod 10

# 第10抽(index=0)时检查
if (block_index = 0 AND block_has_4star = no) {
    强制出4星
}
```

---

## Part 3: File Structure (文件结构)

### 1. 核心文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `in_game/common/scripted_effects/gacha_logic_effects.txt` | 核心逻辑（Silent内核、十连等） | ✅ 使用中 |
| `in_game/common/scripted_effects/gacha_logic_effects.txt` | 奖池定义（5星/4星/3星） | ✅ 集成在逻辑中 |
| `in_game/events/gacha_events.txt` | 主事件（菜单、结果展示） | ✅ 使用中 |
| `in_game/common/script_values/gacha_eu_values.txt` | 概率计算器 | ✅ 使用中 |

### 2. 为什么弃用gacha_values.txt？

**原因**: EU5引擎不支持在`scripted_effects`中使用`script_value:`前缀

**表现**:
```paradox
# 这样写会返回none
set_variable = { 
    name = gacha_curr_thresh5 
    value = script_value:gacha_5star_threshold_value 
}
```

### 硬保底判定
```paradox
if = {
    limit = { gacha_pity_count >= 89 }
    set_variable = { name = gacha_curr_thresh5 value = 1000 }  # 100%
}
```

### 块内保底
```paradox
if = {
    limit = { gacha_block_index = 0 gacha_block_has_4star = no }
    set_variable = { name = gacha_is_4star_win value = yes }  # 强制4星
}
```

---

**文档维护者**: AI + sansm  
**许可**: MIT
