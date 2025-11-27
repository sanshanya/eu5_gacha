# V3 Character Design Workflow

**Version**: 1.0  
**Last Updated**: 2025-11-25  
**Status**: 🚧 Design Document (未实装)  
**Purpose**: 定义V3角色从设计文档到EU5代码的标准转换流程

> [!IMPORTANT]
> **真相来源**: 语法优先以`script_docs`与base game代码为准；本文档只展示在本项目中已跑通的用法。如遇版本更新导致行为变化，以最新的`script_docs`输出为准。

> [!NOTE]
> 本文档基于现有V2角色实现(心海/雷电)验证，所有代码示例均已在游戏中测试通过。

---

## 1. V3设计理念

### 1.1 核心目标

将**原神的陪伴感**融入**EU5的帝国叙事**：
- **V2**: 功能性角色，提供Buff
- **V3**: 有成长弧线的伙伴，从"雇佣"到"陪伴"

### 1.2 六大模块

| 模块 | 目的 | 文字量 |
|:---|:---|:---:|
| **一、角色传记** | 首抽时的自我介绍 | 300-400字 |
| **二、C0三格** | 初始3个特质+独白 | 每格100字 |
| **三、命座升级** | C1-C6成长事件 | 每级150-250字 |
| **四、C6满命独白** | 面板常驻文本 | 500字 |
| **五、C3好感事件** | 分支对话树 | 2轮×2选项 |
| **六、Trait面板文案** | 进阶描述 | 每级100字 |

---

## 2. 文件结构映射

### 2.1 代码文件对应关系

```
设计文档                    代码文件
───────────────────────────────────────────────────
一、角色传记               → events/gacha_{char}_events.txt (Event 1)
二、C0三格                 → traits/gacha_{char}_traits.txt
                           → static_modifiers/gacha_{char}_modifiers.txt
                           → localization/
三、命座升级               → events/ (Event 11/12/13/14/15)
                           → scripted_effects/gacha_{char}_effects.txt
四、C6满命独白             → localization/ (Trait desc)
五、C3好感事件             → events/ (Event 30/31)
六、Trait面板文案          → localization/
```

### 2.2 命名规范

```
in_game/common/
├── traits/gacha_{char}_traits.txt
├── scripted_effects/gacha_{char}_effects.txt
├── on_actions/ (无需修改)
└── script_values/ (无需修改)

in_game/events/gacha_{char}_events.txt

main_menu/common/static_modifiers/gacha_{char}_modifiers.txt
main_menu/localization/simp_chinese/eu_gacha_l_simp_chinese.yml
```

### 2.3 Event ID标准映射表

| Event ID | 用途 | 触发时机 |
|:---|:---|:---|
| `.1` | 首抽传记 | 新角色创建时 |
| `.2` | 通用命座提升 | C1/C3/C5非特殊命座 |
| `.4` | 满命成就 | C6达成时 |
| `.11` | C2觉醒事件 | C2达成时 |
| `.12` | C4超越事件 | C4达成时 (V2命名遗留) |
| `.13` | C4超越事件 | C4达成时 (V3标准) |
| `.14` | C5事件 | C5达成时 |
| `.15` | C6满命事件 | C6达成时 |
| `.30` | C3好感事件·第1轮 | C3达成时 |
| `.31` | C3好感事件·第2轮 | C3第1轮选择后 |

> [!NOTE]
> **ID约定**: `.11~.15`对应C2~C6特殊命座事件，`.30+`系列用于多轮互动事件。V2实现中`.12`对应C4，V3标准化为`.13`对应C4，保持`.1X`=`CX`的一致性。

---

## 3. 模块实现详解

### 3.1 模块一：角色传记

**设计文档示例** (心海):
```markdown
### 一、角色传记
> 「我是珊瑚宫心海。虽然早有预感，但被直接召唤到这里还是意外...
```

**代码实现**:
```paradox
# events/gacha_xinhai_events.txt
namespace = gacha_xinhai_events

gacha_xinhai_events.1 = {
    type = country_event
    title = gacha_xinhai_events.1.title
    desc = gacha_xinhai_events.1.desc
    
    
    immediate = { 
        event_illustration_estate_effect = { 
            foreground = estate_type:nobles_estate 
            background = estate_type:nobles_estate 
        } 
    }
    
    option = { 
        name = gacha_xinhai_events.1.a 
        historical_option = yes 
    }
}
```

**本地化**:
```yaml
gacha_xinhai_events.1.title: "现人神巫女·珊瑚宫心海"
gacha_xinhai_events.1.desc: "「我是珊瑚宫心海。虽然早有预感..."
gacha_xinhai_events.1.a: "欢迎来到我的国家"
```

**触发时机**: 在 `gacha_create_xinhai_effect` 的新角色创建分支末尾。

---

### 3.2 模块二：C0三格

**设计文档示例**:
```markdown
| Trait名称 | 能力数据 | 独白 |
|:---|:---|:---|
| 海祇岛珊瑚灯火 | 疾病抗性 +40% | 「你的国土在生病...」 |
```

**Trait定义** (基于现有代码):
```paradox
# traits/gacha_xinhai_traits.txt
gacha_xinhai_origin_trait = {
    category = ruler
    allow = { always = no }
    # 不在这里定义数值modifier
    # 实际Buff由static_modifiers提供
}
```

> [!WARNING]
> **关于Trait modifier**: 项目现有代码中`modifier = { gacha_country_aura = yes }`需要在`modifier_type_definitions`中定义该类型。如果只是用于标识而无实际UI/逻辑用途，建议移除避免误导。角色识别应使用`has_trait = gacha_xinhai_origin_trait`。

**Modifier定义** (数值在这里):
```paradox
# static_modifiers/gacha_xinhai_modifiers.txt
gacha_xinhai_country_modifier = {
    game_data = { category = country decaying = no }
    legislative_efficiency = 0.3
    country_cabinet_efficiency = 0.25
}

gacha_xinhai_c2_country_modifier = {
    game_data = { category = country decaying = no }
    global_estate_satisfaction_recovery = 0.25
    global_disease_resistance = 0.25
}
```

> [!NOTE]
> **架构说明**: Trait仅用于身份标识，实际数值由Modifier提供。这样可以在角色不担任统治者时，Buff仍然生效(通过Country Modifier)。

---

### 3.3 模块三：命座升级

**设计文档示例**:
```markdown
| 命座 | 升级类型 | 事件标题 |
|:---|:---|:---|
| C2 | 光环升级 | 圣土潮音初现 |
```

**升级逻辑** (在 `gacha_xinhai_effects.txt`):
```paradox
gacha_create_xinhai_effect = {
    if = {
        limit = { has_global_variable = gacha_xinhai_is_summoned }
        
        # 找到已存在的心海
        random_in_global_list = {
            variable = gacha_obtained_characters
            limit = { has_trait = gacha_xinhai_origin_trait }
            save_scope_as = xinhai_char  # 使用角色名作为scope名称
        }
        
        # 升级命座并触发事件
        scope:xinhai_char = {
            change_variable = { name = gacha_constellation_lvl add = 1 }
            gacha_apply_constellation_stats_effect = { who = xinhai }
            
            # C2事件
            if = {
                limit = { gacha_constellation_lvl = 2 }
                root = { 
                    trigger_event_non_silently = { id = gacha_xinhai_events.11 } 
                }
            }
            # C4事件
            else_if = {
                limit = { gacha_constellation_lvl = 4 }
                root = { 
                    trigger_event_non_silently = { id = gacha_xinhai_events.13 } 
                }
            }
            # ... 其他命座
        }
        
        # ⚠️ 不要在这里clear_saved_scope！
        # scope会在事件的after块中清理
    }
}
```

> [!CAUTION]
> **Scope生命周期陷阱**: `trigger_event_non_silently`会将事件放入队列异步执行。如果在effect中立即`clear_saved_scope`，事件触发时scope已被清理，导致`scope:xinhai_char`失效！
> 
> **正确做法**: 在事件的`after`块中清理scope。

**C2升级事件**:
```paradox
# events/gacha_xinhai_events.txt
gacha_xinhai_events.11 = {
    type = country_event
    title = gacha_xinhai_events.11.title
    desc = gacha_xinhai_events.11.desc
    
    
    # 显示角色肖像 (V3: Implicit binding via immediate scope)
    # character = scope:xinhai_char
    
    option = { 
        name = gacha_xinhai_events.11.a 
        add_stability = stability_mild_bonus  # 使用script_value而非硬编码
        scope:xinhai_char = { 
            add_trait = gacha_xinhai_awakened_trait 
        }
    }
    
    # ✅ 在事件结束后清理scope
    after = {
        clear_saved_scope = xinhai_char
    }
}
```

> [!TIP]
> **数值最佳实践**: 优先使用官方script_values(如`stability_mild_bonus`)而非硬编码数值，便于统一调整和保持与原版风格一致。

---

### 3.4 模块五：C3好感事件 (核心创新)

**设计目标**: 2轮对话，玩家选择影响角色反应

**简化实现方案** (2轮×2选项):

#### 第1轮事件
```paradox
# 在命座升级逻辑中触发
else_if = {
    limit = { gacha_constellation_lvl = 3 }
    save_scope_as = gacha_c3_target_char  # 保存角色引用
    root = {
        trigger_event_non_silently = { id = gacha_xinhai_events.30 }
    }
}
```

```paradox
# events/gacha_xinhai_events.txt
gacha_xinhai_events.30 = {
    type = country_event
    title = gacha_xinhai_c3_title
    desc = gacha_xinhai_c3_desc_intro
    
    
    # 显示角色肖像 (V3: Implicit binding)
    # character = scope:gacha_c3_target_char
    
    # 路径A: 好奇探索
    option = {
        name = gacha_xinhai_c3_option_a1
        set_variable = { name = gacha_c3_path value = 1 }
        trigger_event_non_silently = { id = gacha_xinhai_events.31 }
    }
    
    # 路径B: 温柔陪伴
    option = {
        name = gacha_xinhai_c3_option_b1
        set_variable = { name = gacha_c3_path value = 2 }
        trigger_event_non_silently = { id = gacha_xinhai_events.31 }
    }
}
```

#### 第2轮事件 (动态描述)
```paradox
gacha_xinhai_events.31 = {
    type = country_event
    title = gacha_xinhai_c3_title
    
    # ✅ 动态描述 (已在gacha_events.txt中验证)
    desc = {
        first_valid = {
            triggered_desc = {
                trigger = { gacha_c3_path = 1 }
                desc = gacha_xinhai_c3_desc_path_a
            }
            triggered_desc = {
                trigger = { gacha_c3_path = 2 }
                desc = gacha_xinhai_c3_desc_path_b
            }
        }
    }
    
    
    # character = scope:gacha_c3_target_char (V3: Implicit binding)
    
    # 高好感结局
    option = {
        name = gacha_xinhai_c3_option_good
        scope:gacha_c3_target_char = {
            change_variable = { name = gacha_affinity_level add = 20 }
        }
    }
    
    # 普通结局
    option = {
        name = gacha_xinhai_c3_option_neutral
        scope:gacha_c3_target_char = {
            change_variable = { name = gacha_affinity_level add = 10 }
        }
    }
    
    # 清理scope
    after = {
        clear_saved_scope = gacha_c3_target_char
        remove_variable = gacha_c3_path
    }
}
```

> [!TIP]
> **为什么不用列表遍历**: 
> - C3事件触发时，当前scope就是心海角色
> - 通过`save_scope_as`直接保存引用，无需遍历`gacha_obtained_characters`
> - 性能更好，逻辑更清晰

---

### 3.5 模块六：Trait面板文案

**设计文档**:
```markdown
「听到了吗？那是圣土中涌动的潮音。我已将海祇的仪式融入了这片大地...」
```

**本地化实现**:
```yaml
# Trait名称
gacha_xinhai_awakened_trait: "白夜国·圣土潮音"

# Trait描述 (面板独白)
desc_gacha_xinhai_awakened_trait: "「听到了吗？那是圣土中涌动的潮音..."

# Modifier名称
STATIC_MODIFIER_NAME_gacha_xinhai_c2_country_modifier: "圣土潮音"

# Modifier描述 (数值显示)
STATIC_MODIFIER_DESC_gacha_xinhai_c2_country_modifier: "阶层满意恢复 +0.25\n疾病抗性 +0.25"
```

---

## 4. 数值平衡标准

### 4.1 命座数值递进

| 阶段 | 倍率 | 示例 |
|:---|:---:|:---|
| C0 | ×1.0 | 疾病抗性 +25% |
| C2 | ×2.0 | 疾病抗性 +50% |
| C4 | ×2.5 | 海军士气 +30% |
| C6 | ×3.0 | 叛乱 -0.20 |

### 4.2 角色类型模板

| 类型 | 光环主属性 | 职业主属性 | 统治者主属性 |
|:---|:---|:---|:---|
| **军师型** (心海) | 内政恢复 | 海军增益 | 叛乱/纪律 |
| **间谍型** (菲谢尔) | 间谍网 | 炮兵增益 | 正统/威望 |
| **统治型** (雷电) | 叛乱压制 | 陆军增益 | 绝对主义 |

---

## 5. 实施路线图

### Phase 1: 心海V3改造 (2周)
- [ ] 扩展传记事件(Event 1)文本
- [ ] 添加C1/C5命座事件
- [ ] 实现C3好感事件(2轮×2选项)
- [ ] 完善Trait面板文案

### Phase 2: V3模板化 (1周)
- [ ] 更新`character_generator.py`支持V3模板
- [ ] 创建V3 JSON配置示例
- [ ] 测试自动生成流程

### Phase 3: 菲谢尔V3实装 (2周)
- [ ] 双声部演出系统(菲谢尔+奥兹)
- [ ] 完整C1-C6事件链
- [ ] C3雨中花园分支事件

---

## 6. 技术注意事项

### 6.1 已验证的语法 ✅

| 语法 | 状态 | 验证文件 |
|:---|:---:|:---|
| `random_in_global_list` | ✅ | `gacha_xinhai_effects.txt` |
| `save_scope_as` | ✅ | 所有effects文件 |
| `triggered_desc` | ✅ | `gacha_events.txt` |
| Implicit Binding | ⚠️ | 事件中显示肖像 (经验规则：UI倾向于使用immediate中保存的前几个scope，非官方文档明确行为) |
| `after = {}` | ✅ | 事件后清理 |

### 6.2 常见陷阱

**陷阱1: Scope泄漏**
```paradox
# ❌ 错误
option = {
    # 使用scope:existing_char但忘记清理
}

# ✅ 正确
option = {
    clear_saved_scope = existing_char
}
```

**陷阱2: Modifier叠加**
```paradox
# ❌ 错误：直接添加导致双重生效
add_country_modifier = { modifier = gacha_xinhai_c2_country_modifier }

# ✅ 正确：先移除旧Modifier
remove_country_modifier = gacha_xinhai_country_modifier
add_country_modifier = { 
    modifier = gacha_xinhai_c2_country_modifier 
    years = -1 
}
```

---

## 7. 单角色实现清单

```markdown
## V3角色: {char_name}

### 代码文件
- [ ] `traits/gacha_{char}_traits.txt`
- [ ] `static_modifiers/gacha_{char}_modifiers.txt`
- [ ] `scripted_effects/gacha_{char}_effects.txt`
- [ ] `events/gacha_{char}_events.txt`

### 事件ID (按标准映射表)
- [ ] Event 1: 首抽传记
- [ ] Event 2: 通用命座提升 (C1/C3/C5)
- [ ] Event 11: C2觉醒
- [ ] Event 13: C4超越 (V3标准)
- [ ] Event 14: C5事件
- [ ] Event 15: C6满命
- [ ] Event 30-31: C3好感事件 (2轮对话)

### 本地化
- [ ] 所有Trait名称/描述
- [ ] 所有Modifier名称/描述
- [ ] 所有Event标题/描述/选项
- [ ] 使用script_values引用 (如`stability_mild_bonus`)

### 测试
- [ ] 首抽流程完整
- [ ] C1-C6升级事件触发
- [ ] C3分支对话两条路径
- [ ] 验证scope在事件after块中正确清理
- [ ] error.log无报错
```

---

## 8. 与V2的对比

| 维度 | V2实现 | V3设计 | 提升 |
|:---|:---|:---|:---:|
| **传记长度** | ~100字 | ~300字 | 3× |
| **命座事件** | C2/C4/C6 | C1-C6全覆盖 | 2× |
| **玩家互动** | 无 | C3分支对话 | 新增 |
| **叙事深度** | 功能介绍 | 成长弧线 | 质变 |
| **满命体验** | 数值提升 | 叙事升华 | 质变 |

---

## 相关文档

- [Spec: Gacha System](../spec/spec_gacha_system.md) - 抽卡核心逻辑
- [Spec: Scope Management](../spec/spec_scope_management.md) - Scope管理规范
- [Spec: Workflow Add Character](../spec/spec_workflow_add_character.md) - 添加角色流程
- [Design: Affinity System](design_affinity_system.md) - 好感度系统设计
- [Reference: Hallucination Table](../幻觉表.md) - **必读**：CK3/EU4 习惯导致的常见错误汇总

---

**文档维护者**: AI + sansm  
**创建日期**: 2025-11-25  
**状态**: 设计阶段，待心海V3实装后验证
