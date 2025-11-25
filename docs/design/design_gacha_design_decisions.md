# Gacha System Design Decisions

> **Purpose**: 解释抽卡系统的设计决策和权衡  
> **Target Audience**: 开发者、设计者  
> **Status**: Active - 指导未来迭代

---

## Overview

本文档记录抽卡系统的关键设计决策及其背后的思考。这些决策塑造了当前的系统架构和用户体验。

---

## Decision 1: Silent Core Pattern (静默内核模式)

### What
将计算逻辑与UI展示分离:
- **Silent内核**: 只负责概率计算和状态更新
- **Event层**: 负责UI展示和玩家交互

### Why
**动机**:
1. **逻辑清晰**: 概率计算不受UI流程干扰
2. **代码复用**: 单抽/十连共享同一内核
3. **易于调试**: 可独立测试计算逻辑
4. **性能优化**: 十连时避免10次重复的Event初始化

**架构对比**:
```
传统模式:
触发Event → 在Event中计算 → 显示结果

Silent模式:
Silent内核计算 → 保存结果 → 触发Event → 读取结果展示
```

### Trade-offs
**优点**:
- ✅ 逻辑与UI解耦
- ✅ 十连性能提升
- ✅ 调试更容易（可单独测试Silent内核）

**缺点**:
- ❌ 需要维护额外的状态变量（`gacha_tier`, `gacha_is_4star_win`等）
- ❌ 代码量稍微增加

### Status
✅ **已采用** - 成为项目核心架构模式

---

## Decision 2: 4星直接发放 vs 5星延迟发放

### What
- **4星**: 在Silent内核中立即发放（金币/威望/正统性）
- **5星**: 在Event的option中由玩家点击后发放

### Why
**4星立即发放的原因**:
- 简单随机奖励，无复杂逻辑
- 不需要玩家交互
- 效率优先（十连时避免10次弹窗）

**5星延迟发放的原因**:
- 需要50/50判定（UP角色 vs 常驻角色）
- 需要大保底逻辑
- **仪式感**: 玩家需要"揭示命运"的交互体验
- 金光演出后再发放角色，符合原神体验

### Implementation
```paradox
# Silent内核
if = { limit = { var:gacha_tier = 1 }  # 4星
    gacha_grant_4star_reward = yes  # ✅ 立即发放
}
else_if = { limit = { var:gacha_tier = 2 }  # 5星
    # ❌ 不在这里发放
    set_variable = { name = gacha_pity_count value = 0 }  # 只重置pity
}

# Event层
gacha_events.5 = {
    title = "金光闪耀！"
    option = {
        name = "揭示命运..."
        gacha_handle_5star_outcome = yes  # ✅ 玩家点击后发放
    }
}
```

### Status
✅ **已采用** - 提供最佳用户体验

---

## Decision 3: 移除十连结算页面

### What
早期版本十连有结算页面（汇总10次结果），现已移除。

### Evolution
**初始设计** (已废弃):
```
十连 → 10次Silent计算 → 结算页面(汇总) → 逐个弹4/5星Event
```

**当前设计**:
```
十连 → 10次Silent计算 → 逐个弹4/5星Event → 3星静默跳过
```

### Why Removed
**原因**:
1. **反馈冗余**: 4/5星已通过单独弹窗提供足够反馈
2. **用户体验**: 结算页面显得多余，打断节奏
3. **代码简化**: 减少维护成本

**用户反馈** (2025-11-23):
> "十连已经有金光/紫光弹窗了，结算页面感觉重复了"

### Status
✅ **已移除** - 当前版本无结算页面

---

## Decision 4: 允许负金币抽卡

### What
抽卡时不检查金币是否足够，允许负金币抽卡。

### Why
**理由**:
1. **游戏机制**: EU5允许玩家借贷
2. **用户体验**: 负金币后可立即通过借贷/税收还款
3. **非破坏性**: 不会导致游戏崩溃或存档损坏

**代码体现**:
```paradox
gacha_wish_interaction = {
    allow = {
        # ❌ 不检查: gold >= 100
        always = yes  # ✅ 总是允许
    }
    
    effect = {
        add_gold = -100  # 直接扣除，允许为负
    }
}
```

### Alternative Considered
**方案A** (已否决): 严格检查金币
```paradox
allow = { gold >= 100 }
```
- ❌ 限制玩家自由
- ❌ 不符合EU5借贷机制

**方案B** (已采用): 允许负金币
- ✅ 玩家自主决策
- ✅ 符合游戏世界观

### Status
✅ **已采用** - 当前无金币限制

---

## Decision 5: 内联计算 vs Script Values

### What
概率阈值计算直接内联在Effects中，而非使用Script Values。

### Why
**技术限制**:
- EU5引擎不支持在Effects中使用`script_value:`前缀
- 会返回`none`导致逻辑失效

**教训**:
```paradox
# ❌ 错误用法 (在Effects中)
set_variable = { 
    name = gacha_curr_thresh5 
    value = script_value:gacha_5star_threshold_value 
}
# 结果: gacha_curr_thresh5 = none

# ✅ 正确用法 (内联计算)
if = { limit = { var:gacha_pity_count >= 89 }
    set_variable = { name = gacha_curr_thresh5 value = 1000 }
}
else_if = { limit = { var:gacha_pity_count >= 73 }
    set_variable = { name = gacha_curr_thresh5 value = 66 }
    change_variable = { 
        name = gacha_curr_thresh5 
        add = { value = var:gacha_pity_count subtract = 73 multiply = 60 }
    }
}
else = {
    set_variable = { name = gacha_curr_thresh5 value = 6 }
}
```

### Trade-offs
**Script Values方案** (理想但不可行):
- ✅ 代码可读性强
- ✅ 易于维护
- ❌ 引擎不支持

**内联计算方案** (已采用):
- ✅ 引擎支持
- ✅ 性能更好(无函数调用开销)
- ❌ 代码较长
- ❌ 修改概率需要编辑多处

### Status
✅ **已采用** - 引擎限制，无替代方案

**相关**: 详见 `archive_gacha_bug_history.md` Bug #2

---

## Decision 6: 质数混合 PRNG

### What
使用质数混合的伪随机数生成器:
```paradox
rand = 937 + 17×total_rolls + |treasury| + 13×pity + 7×block_index
rand = rand mod 1000
```

### Why
**动机**:
- EU5无内置`random()`函数
- 需要确保0-999均匀分布
- 避免可预测性

**设计要点**:
1. **固定偏移937**: 避免初始值过小
2. **质数系数**: 17, 13, 7 - 增加均匀性
3. **多熵源**: total_rolls, treasury, pity, block_index
4. **绝对值处理**: treasury可能为负

### Alternative Considered
**方案A** (已否决): 简单相加
```paradox
rand = total_rolls + treasury + pity
```
- ❌ 可预测
- ❌ 分布不均

**方案B** (已采用): 质数混合
- ✅ 分布均匀
- ✅ 难以预测
- ⚠️ 非密码学安全(但对游戏足够)

### Status
✅ **已采用** - 测试表明分布良好

**相关**: 详见 `archive_gacha_bug_history.md` Bug #1, #4

---

## Decision 7: 块内保底机制

### What
每10抽（一个"块"）至少保证1个4星或5星。

### Why
**原神机制**: 严格遵循原神的块内保底

**实现挑战**:
- 需要跟踪"当前块"状态
- 需要在第10抽时强制保底

**核心逻辑**:
```paradox
# 计算块索引 (0-9)
block_index = total_rolls mod 10

# 每个新块重置标记
if (block_index = 0) {
    block_has_4star = no
}

# 第10抽检查
if (block_index = 0 AND block_has_4star = no) {
    强制出4星
}

# 出4/5星时设置标记
if (tier >= 1) {
    block_has_4star = yes
}
```

### Trade-offs
**有块内保底**:
- ✅ 符合原神体验
- ✅ 用户体验更好(减少连续3星)
- ❌ 需要额外状态变量

**无块内保底**:
- ✅ 代码简单
- ❌ 可能连续多次3星
- ❌ 不符合原神

### Status
✅ **已采用** - 核心机制，不可移除

---

## Future Considerations

### 可能的改进方向

#### 1. 可配置概率
当前概率硬编码，未来可考虑:
- 使用Defines或Script Values配置
- 支持活动期间调整概率

#### 2. 多卡池切换
当前只有单一限定池，未来可能需要:
- 多个UP池切换
- 武器池(4星装备)
- 常驻池

#### 3. 抽卡记录
当前无历史记录，可能添加:
- 抽卡历史列表
- 统计面板(总抽数/5星数)

---

## 相关文档

- **规范**: [spec_gacha_system.md](../spec/spec_gacha_system.md) - 当前技术规范
- **Bug历史**: [archive_gacha_bug_history.md](../archive/archive_gacha_bug_history.md) - 历史Bug记录
- **引擎基础**: [spec_engine_basics.md](../spec/spec_engine_basics.md) - Script Value机制
- **项目指南**: [design_project_guidelines.md](design_project_guidelines.md) - 总体设计原则

---

**文档维护者**: AI + sansm  
**最后更新**: 2025-11-25
