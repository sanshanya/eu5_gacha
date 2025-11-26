**EU5 Gacha System V3**

请注意一定要摒弃eu4和ck3的过期知识！！！！

请注意一定要摒弃eu4和ck3的过期知识！！！！

请注意一定要摒弃eu4和ck3的过期知识！！！！

**这里唯一的“未证问题”是：save_scope_as 的生命周期细节。**

* EU5 文档只明确 “saved scopes can be referenced via scope:name 并可用 clear_saved_scope 清理，挂在 top scope 上”
* 没有官方写清「跨 event 一定能带过去」——你这里并没有依赖跨 event 的 persisted saved scope（你在 wrapper 里触发事件前就用它），所以是安全用法。
* 真正跨 event 的是 `gacha_event_target_char`，那是由 event 的 `immediate` 自己去 `save_scope_as` 的，这个 pattern 是 wiki 认可的（即 event 自己管理自己的 saved scopes）。

> 假设 H1：在事件的 immediate 块中执行 save_scope_as = X 会创建一个事件局部的 saved scope / event target，可在同一事件的 desc、option、after 中通过 scope:X 访问，不会与其他事件互相覆盖。

同时把原先你说的那句：

> “这里唯一的未证问题是 save_scope_as 的生命周期细节”

改成更精确一点：

> H1（事件级 saved scope）需要 Demo 验证H2（Effect 链内 save_scope_as -> trigger_event -> immediate 能看到 scope）也需要 Demo 验证

从“只看 EU5 文档”的角度，这种用法是合理的、没有明显越界。如果遇到BUG优先考虑这里。

一定要查看文档

[https://eu5.paradoxwikis.com/Scope](https://eu5.paradoxwikis.com/Scope)

[https://eu5.paradoxwikis.com/Event_modding](https://eu5.paradoxwikis.com/Event_modding)

[https://eu5.paradoxwikis.com/Script_value](https://eu5.paradoxwikis.com/Script_value)

[https://eu5.paradoxwikis.com/Variable](https://eu5.paradoxwikis.com/Variable)

本抽卡系统理论上5星抽卡期望为42抽左右

## 1. 设计规范 (Design Specifications)

### 1.1 核心架构：声明式逻辑 (Declarative Architecture)

本系统摒弃了旧时代（EU4/CK3）的过程式脚本堆砌，采用 **"Logic as Data"** 原则：

* **数据层 (Script Values)** ：所有的概率曲线、熵值计算、池子索引轮询，全部封装为独立的数学对象。Effect 层**禁止**进行任何算术运算。
* **流程层 (Scripted Effects)** ：只负责变量的赋值（Snapshot）、逻辑判断（If/Else）和状态更新。
* **表现层 (Events)** ：只负责通知和展示。利用 Scope 快照机制解决异步 UI 的显示问题。

### 1.2 变量命名标准 (V3 Standard)

为了在无类型的 Jomini 脚本中确保类型安全，所有变量名必须遵守以下后缀契约：

| 后缀                 | 类型               | Jomini 实体      | 生命周期        | 用途                        |
| -------------------- | ------------------ | ---------------- | --------------- | --------------------------- |
| **`_sv`**    | Formula            | Script Value     | 静态公式        | 定义计算规则 (如概率阈值)   |
| **`_val`**   | Value              | Local Variable   | 瞬时 (Effect链) | 存储计算中间值 (如当前熵值) |
| **`_idx`**   | Index              | Local Variable   | 瞬时 (Effect链) | 列表/池子指针 (0..N)        |
| **`_count`** | Counter            | Regular Variable | 持久 (存档)     | 累加器 (如保底计数、总抽数) |
| **`_bool`**  | Boolean            | Regular Variable | 持久 (存档)     | 逻辑状态 (0/1)，替代 Flag   |
| **`_amt`**   | Amount             | Regular Variable | 持久 (存档)     | 资源存量 (如虚拟熵资源)     |
| **_bool_val**  | **临时状态** | Local Variable   | 瞬时判断 (0/1)  | 瞬时判断 (0/1)              |

但实现里有几处小偏差：

1. **`gacha_calc_block_idx_val`**
   * 表里定义：索引类 Local 用 `_idx` 后缀。
   * 代码里：`gacha_calc_block_idx_val`，逻辑上它是 0..9 的索引。
     → 建议改名为 `gacha_block_idx_idx` 或 `gacha_block_idx`，保持 `_idx` 后缀，减少混淆。
2. **`gacha_standard_5_idx` vs `_idx_val`**
   * 在 Data Layer 里是 `gacha_calc_standard_5_idx_sv`
   * 在 Resolver 里是 `gacha_standard_5_idx`（local）
     这个是符合 `_idx` 约定的，没问题，反而比 `_idx_val` 更统一。
     → 建议把所有「本质是索引」的 Local 都用 `_idx` 结尾。
3. **`_bool_val` 行为未落地**
   * 表里有 `_bool_val`，但实现用的是 `gacha_is_up_bool_var` 这种名字。
   * 要么表里就写 `_bool_var`，要么代码里统一用 `_bool_val`。
     现在属于“没人真的照着表写”的状态。

这些都不影响运行，但对你想要的“命名即类型系统”是减分的。**启动报告里最好给一个「已知命名差异」的小列表，或者直接修一版统一。**

### 1.3 初始化与安全 (Safety Protocols)

* **卫兵模式 (Gatekeeper)** ：拒绝全局初始化。仅在玩家点击交互入口时，通过 `gacha_ensure_state_initialized` 进行懒加载。
* **作用域一致性 (Scope Consistency)** ：全链路保持在 **Country Scope** 运行。不依赖未文档化的 Scope 自动切换。
* **清理闭环 (Cleanup)** ：遵循“谁使用，谁清理”原则，Scope 的清理权下放至 Event 的 `after` 块。

---

## 2. 核心假设 (Core Assumptions)

本设计基于对 **Project Caesar (Jomini)** 引擎特性的以下确认与推演：

1. **Script Value 能力** ：假设 `script_value` 支持嵌套 Math Blocks (`add = { ... }`)、条件逻辑 (`if`) 以及原生取模 (`modulo`)。
2. **Local Variable 隔离** ：假设 `set_local_variable` 创建的变量仅在当前 Effect Chain 中有效，不会污染存档。
3. **Event 触发机制** ：假设 `country_event` 是 EU5 的标准事件类型；假设 `trigger_event` 是异步入队，但 `immediate` 块是在触发瞬间同步执行的（用于快照）。
4. **UI 绑定** ：假设 UI 肖像显示需要通过 `character = scope:xxx` 显式指定。

---

## 3. 数据层代码 (The Data Layer)

 **文件路径** : `in_game/common/script_values/gacha_values.txt`

### 3.1 熵值与概率公式

```
# ===================================================
# 1. 主熵计算 (0-9999)
# 逻辑：(937 + 总抽数*17 + 5星垫子*13 + |熵资源|) % 10000
# ===================================================
gacha_calc_entropy_sv = {
    value = 937

    add = {
        value = var:gacha_total_rolls_count
        multiply = 17
    }

    add = {
        value = var:gacha_pity_5star_count
        multiply = 13
    }

    add = {
        value = var:gacha_entropy_gold_amt
        abs = yes
    }

    modulo = 10000
}

# ===================================================
# 2. 5星动态概率阈值 (0-10000)
# 基础 0.6% (60)，74抽开始软保底，89抽硬保底
# ===================================================
gacha_calc_5star_prob_sv = {
    value = 60

    # 软保底逻辑
    if = {
        limit = { var:gacha_pity_5star_count >= 73 }
        add = {
            value = var:gacha_pity_5star_count
            subtract = 73
            multiply = 600
        }
    }

    # 硬保底哨兵值 (确保 > 9999)
    if = {
        limit = { var:gacha_pity_5star_count >= 89 }
        value = 10001
    }
}

# ===================================================
# 3. 4星动态概率阈值 (0-10000)
# 基础 5.1% (510)，8抽开始软保底
# ===================================================
gacha_calc_4star_prob_sv = {
    value = 510

    # 软保底逻辑
    if = {
        limit = { var:gacha_pity_4star_count >= 8 }
        add = {
            value = var:gacha_pity_4star_count
            subtract = 8
            multiply = 5000
        }
    }

    max = 10001
}

```

### 3.2 衍生计算逻辑

```
# ===================================================
# 4. 十连块索引 (0-9)
# ===================================================
gacha_calc_block_idx_sv = {
    value = var:gacha_total_rolls_count
    modulo = 10
}

# ===================================================
# 5. 二级熵 (用于 50/50 判定)
# ===================================================
gacha_calc_entropy2_sv = {
    # 引用主熵公式
    value = gacha_calc_entropy_sv
    multiply = 31
    add = {
        value = var:gacha_total_rolls_count
        multiply = 13
    }
    modulo = 10000
}

```

### 3.3 池子配置与索引

```
# ===================================================
# 6. 池子配置
# ===================================================

# --- 常驻 5 星池 ---
gacha_pool_size_standard_5_sv = { value = 8 }

# 索引计算: (歪次数 * 17) % 池子大小
gacha_calc_standard_5_idx_sv = {
    value = var:gacha_std5_result_count
    multiply = 17
    modulo = gacha_pool_size_standard_5_sv
}

# --- 4 星奖励池 ---
gacha_pool_size_4star_sv = { value = 4 }

# 索引计算
gacha_calc_4star_idx_sv = {
    value = var:gacha_4star_result_count
    multiply = 17
    modulo = gacha_pool_size_4star_sv
}

```

## 4. 通用逻辑定义 (Common Logic)

 **文件** : `in_game/common/scripted_effects/gacha_common_effects.txt`

### 4.1 状态卫兵 (The Gatekeeper)

 **职责** : 幂等初始化。确保后续逻辑运行时，所有持久化变量 (`_count`, `_bool`, `_amt`) 均已存在。

```
# =======================================================
# [Gatekeeper] Gacha State Initialization
# 必须在 Country Scope 下调用
# =======================================================
gacha_ensure_state_initialized = {
    # --- 计数器 (_count) ---
    if = { limit = { NOT = { has_variable = gacha_total_rolls_count } }  set_variable = { name = gacha_total_rolls_count value = 0 } }
    if = { limit = { NOT = { has_variable = gacha_pity_5star_count } }   set_variable = { name = gacha_pity_5star_count value = 0 } }
    if = { limit = { NOT = { has_variable = gacha_pity_4star_count } }   set_variable = { name = gacha_pity_4star_count value = 0 } }

    # --- 结果统计 (_count) ---
    if = { limit = { NOT = { has_variable = gacha_std5_result_count } }  set_variable = { name = gacha_std5_result_count value = 0 } }
    if = { limit = { NOT = { has_variable = gacha_4star_result_count } } set_variable = { name = gacha_4star_result_count value = 0 } }

    # --- 状态旗标 (_bool) ---
    if = { limit = { NOT = { has_variable = gacha_is_guaranteed_bool } }  set_variable = { name = gacha_is_guaranteed_bool value = 0 } }
    if = { limit = { NOT = { has_variable = gacha_block_pity_met_bool } } set_variable = { name = gacha_block_pity_met_bool value = 0 } }

    # --- 熵资源 (_amt) ---
    if = { limit = { NOT = { has_variable = gacha_entropy_gold_amt } }   set_variable = { name = gacha_entropy_gold_amt value = 10000 } }
}

```

### 4.2 角色注册契约 (The Registration Contract)

 **职责** : 任何新角色的创建逻辑最终都必须调用此 Effect，以确保 Scope 被正确保存供 UI 使用。

```
gacha_register_new_character = {
    # ... (常规的 Add Trait / Modifier 逻辑，此处省略) ...

    # 确保角色归属于当前国家
    move_country = root

    # 【核心契约】保存 Scope
    # 这是 UI 事件 (Part 3) 能显示立绘的关键
    save_scope_as = gacha_last_pulled_char
}

```

---

## 5. 核心逻辑内核 (The Logic Kernel)

 **文件** : `in_game/common/scripted_effects/gacha_logic_effects.txt`

### 5.1 单抽静默内核 (Silent Kernel)

 **职责** : 状态步进 -> 获取数学结果 -> 判定星级 -> 更新保底 -> 分发结算。
 **规范** : 全程在 Country Scope 运行，不进行任何 Scope 切换。

```
gacha_execute_single_roll_silent = {
    # --------------------------------------------------------
    # Step 0: 状态步进
    # --------------------------------------------------------
    change_variable = { name = gacha_total_rolls_count add = 1 }
    change_variable = { name = gacha_entropy_gold_amt subtract = 16 }

    # --------------------------------------------------------
    # Step 1: 数据快照 (从 _sv 获取值存入 _val)
    # --------------------------------------------------------
    set_local_variable = { name = gacha_calc_entropy_val value = gacha_calc_entropy_sv }
    set_local_variable = { name = gacha_threshold_5star_val value = gacha_calc_5star_prob_sv }
    set_local_variable = { name = gacha_threshold_4star_val value = gacha_calc_4star_prob_sv }
    set_local_variable = { name = gacha_calc_block_idx_val value = gacha_calc_block_idx_sv }

    # 新十连块重置逻辑
    if = {
        limit = { local_var:gacha_calc_block_idx_val = 1 }
        set_variable = { name = gacha_block_pity_met_bool value = 0 }
    }

    # --------------------------------------------------------
    # Step 2: 星级判定 (Tier Decision)
    # 0=3星, 1=4星, 2=5星
    # --------------------------------------------------------
    set_local_variable = { name = gacha_calc_tier_idx value = 0 }

    if = {
        # 5星判定
        limit = { local_var:gacha_calc_entropy_val < local_var:gacha_threshold_5star_val }
        set_local_variable = { name = gacha_calc_tier_idx value = 2 }
    }
    else_if = {
        # 4星判定 (概率 OR 块保底)
        limit = {
            OR = {
                local_var:gacha_calc_entropy_val < local_var:gacha_threshold_4star_val
                AND = {
                    local_var:gacha_calc_block_idx_val = 0
                    var:gacha_block_pity_met_bool = 0
                }
            }
        }
        set_local_variable = { name = gacha_calc_tier_idx value = 1 }
    }

    # --------------------------------------------------------
    # Step 3: 结算分发 (Resolve & Update)
    # --------------------------------------------------------
    if = {
        limit = { local_var:gacha_calc_tier_idx = 2 }
        # 更新保底
        set_variable = { name = gacha_pity_5star_count value = 0 }
        set_variable = { name = gacha_block_pity_met_bool value = 1 }
        change_variable = { name = gacha_pity_4star_count add = 1 }

        # 解析并生成角色 Scope
        gacha_resolve_5star_and_save_scope = yes
    }
    else_if = {
        limit = { local_var:gacha_calc_tier_idx = 1 }
        # 更新保底
        set_variable = { name = gacha_pity_4star_count value = 0 }
        set_variable = { name = gacha_block_pity_met_bool value = 1 }
        change_variable = { name = gacha_pity_5star_count add = 1 }

        # 解析并发放奖励
        gacha_resolve_4star_logic = yes
    }
    else = {
        # 3星: 仅增加垫子
        change_variable = { name = gacha_pity_5star_count add = 1 }
        change_variable = { name = gacha_pity_4star_count add = 1 }
    }
}

```

---

## 6. 结果解析器 (Resolvers)

 **文件** : `in_game/common/scripted_effects/gacha_logic_effects.txt` (续)

### 6.1 五星解析 (Resolve & Save)

 **职责** : 判定 UP/歪 -> 轮询常驻 -> 发放角色 ->  **确保保存 Scope** 。

```
gacha_resolve_5star_and_save_scope = {
    # 1. 获取二级熵 (用于 50/50)
    set_local_variable = { name = gacha_calc_entropy2_val value = gacha_calc_entropy2_sv }
    set_local_variable = { name = gacha_is_up_bool_var value = 0 }

    # 2. 判定逻辑
    if = {
        # 情况 A: 大保底生效
        limit = { var:gacha_is_guaranteed_bool = 1 }
        set_local_variable = { name = gacha_is_up_bool_var value = 1 }
        set_variable = { name = gacha_is_guaranteed_bool value = 0 } # 消耗保底
    }
    else = {
        # 情况 B: 概率判定 (阈值 5000/10000)
        if = {
            limit = { local_var:gacha_calc_entropy2_val < 5000 }
            set_local_variable = { name = gacha_is_up_bool_var value = 1 }
        }
        else = {
            set_local_variable = { name = gacha_is_up_bool_var value = 0 }
            set_variable = { name = gacha_is_guaranteed_bool value = 1 } # 设为大保底
        }
    }

    # 3. 发放角色
    # 注意：被调用的 Effect 内部必须执行 save_scope_as = gacha_last_pulled_char
    if = {
        limit = { local_var:gacha_is_up_bool_var = 1 }
        gacha_create_xinhai_effect = yes # 当期 UP
    }
    else = {
        # 歪常驻：轮询
        change_variable = { name = gacha_std5_result_count add = 1 }
        set_local_variable = { name = gacha_standard_5_idx value = gacha_calc_standard_5_idx_sv }

        if = { limit = { local_var:gacha_standard_5_idx = 0 } gacha_create_keqing_effect = yes }
        else_if = { limit = { local_var:gacha_standard_5_idx = 1 } gacha_create_raiden_effect = yes }
        else_if = { limit = { local_var:gacha_standard_5_idx = 2 } gacha_create_furina_effect = yes }
        else_if = { limit = { local_var:gacha_standard_5_idx = 3 } gacha_create_hutao_effect = yes }
        else_if = { limit = { local_var:gacha_standard_5_idx = 4 } gacha_create_klee_effect = yes }
        else_if = { limit = { local_var:gacha_standard_5_idx = 5 } gacha_create_nahida_effect = yes }
        else_if = { limit = { local_var:gacha_standard_5_idx = 6 } gacha_create_fischl_effect = yes }
        else = { gacha_create_ayaka_effect = yes } # Index 7
    }
}

```

### 6.2 四星解析 (Resolve Reward)

 **职责** : 计算索引 ->  **直接发放资源** 。

```
gacha_resolve_4star_logic = {
    # 1. 轮询索引
    change_variable = { name = gacha_4star_result_count add = 1 }
    set_local_variable = { name = gacha_4star_idx_val value = gacha_calc_4star_idx_sv }

    # 2. 实发奖励 (不再依赖 Event Option)
    if = { limit = { local_var:gacha_4star_idx_val = 0 } add_gold = 240 }
    else_if = { limit = { local_var:gacha_4star_idx_val = 1 } add_prestige = 8 }
    else_if = { limit = { local_var:gacha_4star_idx_val = 2 } add_legitimacy = 8 }
    else = { add_stability = 0.25 }
}

```

---

## 7. 逻辑包装器 (Wrappers)

 **文件** : `in_game/common/scripted_effects/gacha_logic_effects.txt` (续)

 **职责** : 循环调用内核，并根据结果 **触发对应的 UI 事件** 。
 **关键** : 使用 `trigger_event_non_silently` 将事件放入 UI 队列，利用事件自身的 `immediate` 机制抓取快照。

### 7.1 十连包装器 (Ten Pull)

```
gacha_wrapper_ten_pull = {
    set_local_variable = { name = gacha_loop_idx value = 0 }

    while = {
        limit = { local_var:gacha_loop_idx < 10 }

        # A. 运行内核 (结算并产生 gacha_last_pulled_char)
        gacha_execute_single_roll_silent = yes

        # B. 事件分发
        if = {
            limit = { local_var:gacha_calc_tier_idx = 2 } # 5星
            trigger_event_non_silently = gacha_events.5
        }
        else_if = {
            limit = { local_var:gacha_calc_tier_idx = 1 } # 4星
            # ID 分流，对应不同的静态文本
            if = { limit = { local_var:gacha_4star_idx_val = 0 } trigger_event_non_silently = gacha_events.21 }
            else_if = { limit = { local_var:gacha_4star_idx_val = 1 } trigger_event_non_silently = gacha_events.22 }
            else_if = { limit = { local_var:gacha_4star_idx_val = 2 } trigger_event_non_silently = gacha_events.23 }
            else = { trigger_event_non_silently = gacha_events.24 }
        }
        # 3星静默

        change_local_variable = { name = gacha_loop_idx add = 1 }
    }
}

```

### 7.2 单抽包装器 (Single Pull)

```
gacha_wrapper_single_pull = {
    gacha_execute_single_roll_silent = yes

    if = {
        limit = { local_var:gacha_calc_tier_idx = 2 }
        trigger_event_non_silently = gacha_events.5
    }
    else_if = {
        limit = { local_var:gacha_calc_tier_idx = 1 }
        # 保持与十连一致的分流
        if = { limit = { local_var:gacha_4star_idx_val = 0 } trigger_event_non_silently = gacha_events.21 }
        else_if = { limit = { local_var:gacha_4star_idx_val = 1 } trigger_event_non_silently = gacha_events.22 }
        else_if = { limit = { local_var:gacha_4star_idx_val = 2 } trigger_event_non_silently = gacha_events.23 }
        else = { trigger_event_non_silently = gacha_events.24 }
    }
    else = {
        # 3星弹窗
        trigger_event_non_silently = gacha_events.2
    }
}

```

## 7. 表现层代码 (The Presentation Layer)

### 7.1 交互入口 (Interaction Entry)

 **文件** : `in_game/common/character_interactions/gacha_wish_interaction.txt`

 **核心职责** ：懒加载初始化。这是系统的唯一安全入口。

```
gacha_wish_interaction = {
    category = interaction_category_personal

    # 基础检查
    potential = {
        scope:actor = { has_ruler = yes }
    }

    # 始终允许点击，资源扣除在事件选项中处理
    allow = { always = yes }

    effect = {
        scope:actor = {
            # 1. [Gatekeeper] 数据初始化
            # 必须在打开菜单前执行，确保 UI 文本能读取到变量
            gacha_ensure_state_initialized = yes

            # 2. [UI] 打开祈愿主菜单
            trigger_event_non_silently = gacha_events.1
        }
    }
}

```

### 7.2 祈愿主菜单 (Main Menu)

 **文件** : `in_game/events/gacha_events.txt`

 **核心职责** ：展示保底状态，提供抽卡选项。

```
namespace = gacha_events

# ==========================================
# Event 1: 祈愿主界面
# ==========================================
gacha_events.1 = {
    type = country_event
    title = gacha_events.1.t

    # 无 trigger (脚本调用)

    # 动态描述：显示保底进度
    desc = {
        first_valid = {
            triggered_desc = {
                trigger = { var:gacha_is_guaranteed_bool = 1 }
                desc = gacha_events.1.desc_guaranteed
            }
            triggered_desc = {
                desc = gacha_events.1.desc_normal
            }
        }
    }

    # --- 选项 A: 单抽 ---
    option = {
        name = gacha_events.1.a
        add_gold = -16
        hidden_effect = {
            gacha_wrapper_single_pull = yes
        }
    }

    # --- 选项 B: 十连 ---
    option = {
        name = gacha_events.1.b
        add_gold = -160
        hidden_effect = {
            gacha_wrapper_ten_pull = yes
        }
    }

    # --- 选项 C: 新手免费福利 (一次性) ---
    option = {
        name = gacha_events.1.novice
        trigger = {
            NOT = { has_variable = gacha_novice_used_bool }
        }
        hidden_effect = {
            set_variable = { name = gacha_novice_used_bool value = 1 }

            # 1. 调用解析逻辑生成角色 (Part 2)
            # 内部会自动: create/upgrade -> save_scope_as = gacha_last_pulled_char
            gacha_resolve_5star_and_save_scope = yes

            # 2. 触发 Scope 锁定的展示事件
            # 注意：利用 Immediate 快照机制，此处直接触发即可
            trigger_event_non_silently = gacha_events.5
        }
    }

    # --- 选项 D: 离开 ---
    option = {
        name = gacha_events.1.exit
    }
}

```

### 7.3 五星展示事件 (5-Star Reveal)

 **文件** : `in_game/events/gacha_events.txt` (续)

 **核心机制** ： **Scope Snapshot (快照)** 。
这是解决十连抽“时间错位”的终极方案。在事件触发瞬间 (`immediate`)，将易变的全局指针转存为事件实例的私有变量。

```
# ==========================================
# Event 5: 五星展示
# ==========================================
gacha_events.5 = {
    type = country_event
    title = gacha_events.5.t
    desc = gacha_events.5.desc

    # 无 trigger (脚本调用)

    # 【Scope Snapshot】
    # 关键：在 Wrapper 触发事件的瞬间执行
    # 将当前的全局指针 gacha_last_pulled_char 锁定为本窗口的 target
    immediate = {
        scope:gacha_last_pulled_char = {
            save_scope_as = gacha_event_target_char
        }
    }

    # 【UI Binding】
    # 显式绑定：告诉 UI 使用哪个 Scope 渲染 3D/2D 立绘
    character = scope:gacha_event_target_char

    option = {
        name = gacha_events.5.a # "揭示命运"
        # 奖励已在内核发放，此处为空
    }

    # 【Cleanup】
    # 窗口关闭后清理，防止 Scope 泄漏
    after = {
        clear_saved_scope = gacha_event_target_char
        clear_saved_scope = gacha_last_pulled_char
    }
}

```

### 7.4 资源展示事件 (4-Star/3-Star)

 **核心机制** ： **Event ID 分流** 。
通过触发不同的事件 ID 来对应不同的静态文本，规避了动态文本在异步队列中的更新延迟问题。

```
# --- 4星：金币 ---
gacha_events.21 = {
    type = country_event
    title = gacha_events.4star_gold.t
    desc = gacha_events.4star_gold.desc
    option = { name = gacha_events.ok } # 奖励已在内核发放
}

# --- 4星：威望 ---
gacha_events.22 = {
    type = country_event
    title = gacha_events.4star_prestige.t
    desc = gacha_events.4star_prestige.desc
    option = { name = gacha_events.ok }
}

# --- 4星：正统性 ---
gacha_events.23 = {
    type = country_event
    title = gacha_events.4star_legitimacy.t
    desc = gacha_events.4star_legitimacy.desc
    option = { name = gacha_events.ok }
}

# --- 4星：稳定度 ---
gacha_events.24 = {
    type = country_event
    title = gacha_events.4star_stability.t
    desc = gacha_events.4star_stability.desc
    option = { name = gacha_events.ok }
}

# --- 3星：凡铁 ---
gacha_events.2 = {
    type = country_event
    title = gacha_events.3star.t
    desc = gacha_events.3star.desc
    option = {
        name = gacha_events.ok
        # 3星作为安慰奖，可以在这里发点小钱
        add_gold = 10
    }
}

```

---

## 8. 集成与扩展指南 (Integration Guide)

### 8.1 如何添加新角色 (Adding a Character)

假设要添加角色  **神里绫华 (ayaka)** 。你需要遵守以下**“对接契约”**。

**步骤 1: 创建 Wrapper Effect**
文件: `in_game/common/scripted_effects/gacha_ayaka_effects.txt`

```
gacha_create_ayaka_effect = {
    # === A. 重复获得 (Upgrade) ===
    if = {
        limit = { has_global_variable = gacha_ayaka_is_summoned }
        random_in_global_list = {
            variable = gacha_obtained_characters
            limit = { has_character_modifier = gacha_ayaka_modifier }
            save_scope_as = existing_char
        }
        scope:existing_char = {
            # 升级逻辑...
            change_variable = { name = gacha_constellation_lvl add = 1 }

            # 【契约 1】必须保存 Scope
            save_scope_as = gacha_last_pulled_char
        }
    }

    # === B. 新创建 (New) ===
    else = {
        create_character = { ... save_scope_as = new_char }
        scope:new_char = {
            # 调用注册内核 (内部已包含 save_scope_as = gacha_last_pulled_char)
            gacha_register_new_character = { who = ayaka }
        }
        set_global_variable = { name = gacha_ayaka_is_summoned value = 1 }
    }
}

```

**步骤 2: 注册进池子**
文件: `in_game/common/scripted_effects/gacha_logic_effects.txt` (五星解析器)

```
gacha_resolve_5star_and_save_scope = {
    # ...
    else = {
        # 常驻分支
        # 假设 Ayaka 是常驻池 Index 8
        else_if = { limit = { local_var:gacha_standard_5_idx = 8 } gacha_create_ayaka_effect = yes }
    }
}

```

**步骤 3: 更新池子大小**
文件: `in_game/common/script_values/gacha_values.txt`

```
gacha_pool_size_standard_5_sv = { value = 9 } # 8 -> 9

```

修订案：

 **机制确认** ：

1. **Implicit Binding (隐式绑定)** ：事件 UI 自动抓取 immediate 块中**前两个**保存的角色/Pop Scope 进行展示。
2. **Order Matters (顺序即真理)** ：我们必须确保 gacha_event_target_char 是 immediate 中**第一个**被保存的 Scope。

以下是基于此机制修正的  **Rev 4.7 (Final UI Patch)** 。

---

# EU5 Gacha System Final Report (v1.0) - Rev 4.7

 **核心修正** : **Implicit Portrait Binding** (移除 character =，利用 immediate 顺序绑定)。

---

## Part 3: 表现层代码 (UI Layer)

 **文件** : in_game/events/gacha_events.txt

### 7.3 五星展示事件 (Corrected)

codeParadox

`# ==========================================

# Event 5: 五星展示

# ==========================================

gacha_events.5 = {
type = country_event
title = gacha_events.5.t
desc = gacha_events.5.desc

```
# 脚本调用，无 Trigger
# trigger = { ... } 

# 【UI Binding via Scope Order】
# EU5 机制：UI 会自动读取 immediate 中保存的前两个 Character/Pop Scope 并显示立绘
# 因此，必须确保目标角色是 *第一个* 被保存的
immediate = {
    scope:gacha_last_pulled_char = {
        save_scope_as = gacha_event_target_char
    }
}

# ❌ 删除：character = scope:gacha_event_target_char (CK3 旧语法)
# ✅ 机制：引擎自动渲染 gacha_event_target_char 的立绘

option = {
    name = gacha_events.5.a # "揭示命运"
}

# 【Cleanup】
after = {
    clear_saved_scope = gacha_event_target_char
    clear_saved_scope = gacha_last_pulled_char
}
```

}`

### 7.4 资源展示事件 (无需变动)

对于 4 星/3 星事件（Event 2, 21-24），因为它们在 immediate 中 **没有保存任何 Character Scope** ，UI 将默认显示国家背景图或 generic illustration，

**`character = scope:xxx` 在 EU5 官方 wiki 中没有文档记录。**

可能的情况：

1. **未文档化但有效** — Paradox 游戏经常有未写入 wiki 的功能
2. **CK3 语法误用** — CK3 事件用 `left_portrait = { character = scope:xxx }` 显示立绘
3. **完全无效** — 会被引擎忽略，立绘显示可能是靠 saved scope 自动生成在工作

# V3 角色模板实现规范

🚧 **Design Document** (未实装)

 **Version** : 3.0

 **Last Updated** : 2025-11-26

 **Purpose** : 定义 V3 角色设计文档到 EU5 Mod 代码的标准转换流程

> [!IMPORTANT]

> **真相来源** : 语法优先以 `script_docs` 与 base game 代码为准；本文档只展示在本项目中已跑通的用法。如遇版本更新导致行为变化，以最新的 `script_docs` 输出为准。

---

首先clear_saved_scope 永远写 clear_saved_scope = existing_char，不要加 scope:。

在 effect 里对那个角色做事，要用 scope:existing_char = { ... }，而不是 existing_char = { ... }。，其次character = scope:gacha_c3_target_char是幻觉。


首先clear_saved_scope 永远写 clear_saved_scope = existing_char，不要加 scope:。

在 effect 里对那个角色做事，要用 scope:existing_char = { ... }，而不是 existing_char = { ... }。，其次character = scope:gacha_c3_target_char是幻觉。


首先clear_saved_scope 永远写 clear_saved_scope = existing_char，不要加 scope:。

在 effect 里对那个角色做事，要用 scope:existing_char = { ... }，而不是 existing_char = { ... }。，其次character = scope:gacha_c3_target_char是幻觉。

## 1. V3 设计理念

### 1.1 核心目标

将**原神的陪伴感**融入 **EU5的帝国叙事** ：

* **V2** : 功能性角色，提供 Buff
* **V3** : 有成长弧线的伙伴，从"雇佣"到"陪伴"

### 1.2 V2 → V3 演进

| 维度                 | V2                 | V3                     |
| -------------------- | ------------------ | ---------------------- |
| :---                 | :---               | :---                   |
| **核心体验**   | 功能性（数值加成） | 陪伴感（角色成长叙事） |
| **事件密度**   | 命座升级才触发     | C3 好感事件 + 日常互动 |
| **文案风格**   | 简短提示           | 长独白 + 分支对话      |
| **Trait 描述** | 纯数值说明         | 角色视角独白           |

### 1.3 六大设计模块

| 模块                         | 目的                  | 文字量        |
| ---------------------------- | --------------------- | ------------- |
| :---                         | :---                  | :---:         |
| **一、角色传记**       | 首抽时的自我介绍      | 300-400字     |
| **二、C0 四格**        | 1 Core + 3 功能 Trait | 每格100字     |
| **三、命座升级**       | C1-C6 成长事件        | 每级150-250字 |
| **四、C6 满命独白**    | 面板常驻文本          | 500字         |
| **五、C3 好感事件**    | 分支对话树            | 2轮×2选项    |
| **六、Trait 面板文案** | 进阶描述              | 每级100字     |

---

## 2. Trait 架构 (4层)

### 2.1 Trait 体系

| Trait                             | 用途          | Category          | 生效条件           |
| --------------------------------- | ------------- | ----------------- | ------------------ |
| :---                              | :---          | :---              | :---               |
| `gacha_core_trait`              | 2D头像mod识别 | 通用标识          | 持有即生效         |
| `gacha_{char}_aura_trait`       | 光环效果      | country modifier  | 角色在职即生效     |
| `gacha_{char}_ruler_trait`      | 统治者加成    | ruler             | 担任统治者时生效   |
| `gacha_{char}_profession_trait` | 职业能力      | advisor/commander | 担任对应职位时生效 |

### 2.2 Trait 定义示例

```
# traits/gacha_xinhai_traits.txt

# Core Trait (所有角色共用定义在 gacha_core_traits.txt)
gacha_core_trait = {
    category = ruler
    allow = { always = no }
    # 2D头像mod通过此trait识别gacha角色
}

# 光环 Trait
gacha_xinhai_aura_trait = {
    category = ruler
    allow = { always = no }
    # 实际数值由 country_modifier 提供
}

# 统治者 Trait
gacha_xinhai_ruler_trait = {
    category = ruler
    allow = { always = no }
    modifier = {
        monthly_rebellion = -0.10
        land_morale = 0.05
    }
}

# 职业 Trait
gacha_xinhai_profession_trait = {
    category = commander
    allow = { always = no }
    modifier = {
        naval_morale = 0.10
        blockade_efficiency = 0.15
    }
}
```

### 2.3 角色创建时添加

```
create_character = {
    ...
    traits = {
        gacha_core_trait              # 通用识别
        gacha_xinhai_aura_trait       # 光环
        gacha_xinhai_ruler_trait      # 统治者
        gacha_xinhai_profession_trait # 职业
    }
}
```

---

## 3. 文件结构映射

### 3.1 代码文件对应关系

```
设计文档                    代码文件
───────────────────────────────────────────────────
一、角色传记               → events/gacha_{char}_events.txt (Event 1)
二、C0 四格                → traits/gacha_{char}_traits.txt
                           → static_modifiers/gacha_{char}_modifiers.txt
                           → localization/
三、命座升级               → events/ (Event 11/12/13/14/15)
                           → scripted_effects/gacha_{char}_effects.txt
四、C6 满命独白            → localization/ (Trait desc)
五、C3 好感事件            → events/ (Event 30/31)
六、Trait 面板文案         → localization/
```

### 3.2 目录结构

```
in_game/
├── common/
│   ├── traits/
│   │   ├── gacha_core_traits.txt
│   │   └── gacha_{char}_traits.txt
│   └── scripted_effects/
│       └── gacha_{char}_effects.txt
├── events/
│   └── gacha_{char}_events.txt
main_menu/
├── common/static_modifiers/
│   └── gacha_{char}_modifiers.txt
└── localization/simp_chinese/
    └── eu_gacha_l_simp_chinese.yml
```

### 3.3 Event ID 标准映射表

| Event ID | 用途               | 触发时机            |
| -------- | ------------------ | ------------------- |
| :---     | :---               | :---                |
| `.1`   | 首抽传记           | 新角色创建时        |
| `.2`   | 通用命座提升       | C1/C3/C5 非特殊命座 |
| `.4`   | 满命成就           | C6 达成时           |
| `.11`  | C2 觉醒事件        | C2 达成时           |
| `.13`  | C4 超越事件        | C4 达成时           |
| `.14`  | C5 事件            | C5 达成时           |
| `.15`  | C6 满命事件        | C6 达成时           |
| `.30`  | C3 好感事件·第1轮 | C3 达成时           |
| `.31`  | C3 好感事件·第2轮 | C3 第1轮选择后      |

> [!NOTE]

> **ID约定** : `.1X` 对应 `CX` 特殊命座事件，`.30+` 系列用于多轮互动事件。

---

## 4. 已验证的语法

> 以下语法均已在 V2 实现中验证通过 (`error.log` 干净)

### 4.1 Scope 管理

```
# ✅ 保存/清理 scope
save_scope_as = gacha_c3_target_char
clear_saved_scope = gacha_c3_target_char

# ✅ 访问国家 scope
root = {
    trigger_event_non_silently = { id = gacha_xinhai_events.30 }
}

# ✅ 通过 scope 访问角色
scope:gacha_c3_target_char = {
    change_variable = { name = gacha_affinity_level add = 20 }
}
```

### 4.2 动态事件描述

```
desc = {
    first_valid = {
        triggered_desc = {
            trigger = { var:gacha_c3_path = 1 }
            desc = gacha_xinhai_c3_desc_path_a
        }
        triggered_desc = {
            trigger = { var:gacha_c3_path = 2 }
            desc = gacha_xinhai_c3_desc_path_b
        }
    }
}
```

### 4.3 角色迭代器

```
# ✅ Effect 迭代器
random_character = {
    limit = { has_trait = gacha_xinhai_aura_trait }
    save_scope_as = xinhai_char
}

every_character = {
    limit = { 
        has_trait = gacha_core_trait 
        employer ?= root
    }
    change_variable = { name = gacha_affinity_level add = 20 }
}

# ⚠️ any_character 是 Trigger 迭代器，只能在 trigger = { } 中使用
```

### 4.4 Modifier 替换

```
# ✅ 先移除再添加
root = {
    remove_country_modifier = gacha_xinhai_c0_aura_modifier
    add_country_modifier = {
        modifier = gacha_xinhai_c2_aura_modifier
        years = -1
    }
}
```

### 4.5 语法验证表

| 语法                      | 状态  | 验证文件                     |
| ------------------------- | ----- | ---------------------------- |
| :---                      | :---: | :---                         |
| `random_in_global_list` | ✅    | `gacha_xinhai_effects.txt` |
| `save_scope_as`         | ✅    | 所有 effects 文件            |
| `triggered_desc`        | ✅    | `gacha_events.txt`         |
| `character = scope:xxx` | ⚠️  | 待测试移除                   |
| `after = {}`            | ✅    | 事件后清理                   |

---

## 5. 模块实现模板

### 5.1 模块一：首抽传记事件

```
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

### 5.2 模块三：命座升级逻辑

```
# gacha_xinhai_effects.txt
gacha_create_xinhai_effect = {
    if = {
        limit = { has_global_variable = gacha_xinhai_is_summoned }
    
        # 找到已存在的心海
        random_in_global_list = {
            variable = gacha_obtained_characters
            limit = { has_trait = gacha_xinhai_aura_trait }
            save_scope_as = xinhai_char
        }
    
        # 升级命座并触发事件
        scope:xinhai_char = {
            change_variable = { name = gacha_constellation_lvl add = 1 }
            gacha_apply_constellation_stats_effect = { who = xinhai }
        
            # C2事件
            if = {
                limit = { var:gacha_constellation_lvl = 2 }
                root = { 
                    trigger_event_non_silently = { id = gacha_xinhai_events.11 } 
                }
            }
            # C3好感事件
            else_if = {
                limit = { var:gacha_constellation_lvl = 3 }
                save_scope_as = gacha_c3_target_char
                root = {
                    trigger_event_non_silently = { id = gacha_xinhai_events.30 }
                }
            }
            # C4事件
            else_if = {
                limit = { var:gacha_constellation_lvl = 4 }
                root = { 
                    trigger_event_non_silently = { id = gacha_xinhai_events.13 } 
                }
            }
        }
        # ⚠️ 不要在这里 clear_saved_scope！
        # scope 会在事件的 after 块中清理
    }
}
```

> [!CAUTION]

> **Scope 生命周期陷阱** : `trigger_event_non_silently` 会将事件放入队列异步执行。如果在 effect 中立即 `clear_saved_scope`，事件触发时 scope 已被清理！

> **正确做法** : 在事件的 `after` 块中清理 scope。

### 5.3 模块五：C3 好感事件 (2×2)

### 第1轮事件

```
gacha_xinhai_events.30 = {
    type = country_event
    title = gacha_xinhai_c3_title
    desc = gacha_xinhai_c3_desc_intro
  
  
  
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

### 第2轮事件 (动态描述)

```
gacha_xinhai_events.31 = {
    type = country_event
    title = gacha_xinhai_c3_title
  
    desc = {
        first_valid = {
            triggered_desc = {
                trigger = { var:gacha_c3_path = 1 }
                desc = gacha_xinhai_c3_desc_path_a
            }
            triggered_desc = {
                trigger = { var:gacha_c3_path = 2 }
                desc = gacha_xinhai_c3_desc_path_b
            }
        }
    }
  
  
  
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
  
    # ✅ 清理 scope
    after = {
        clear_saved_scope = gacha_c3_target_char
        remove_variable = gacha_c3_path
    }
}
```

> [!TIP]

> **为什么不用列表遍历** : C3 事件触发时，当前 scope 就是心海角色。通过 `save_scope_as` 直接保存引用，无需遍历 `gacha_obtained_characters`。

---

## 6. 数值平衡标准

### 6.1 命座数值递进

| 阶段 | 倍率  | 示例          |
| ---- | ----- | ------------- |
| :--- | :---: | :---          |
| C0   | ×1.0 | 疾病抗性 +25% |
| C2   | ×2.0 | 疾病抗性 +50% |
| C4   | ×2.5 | 海军士气 +30% |
| C6   | ×3.0 | 叛乱 -0.20    |

### 6.2 角色类型模板

| 类型                     | 光环主属性 | 职业主属性 | 统治者主属性 |
| ------------------------ | ---------- | ---------- | ------------ |
| :---                     | :---       | :---       | :---         |
| **军师型**(心海)   | 内政恢复   | 海军增益   | 叛乱/纪律    |
| **间谍型**(菲谢尔) | 间谍网     | 炮兵增益   | 正统/威望    |
| **统治型**(雷电)   | 叛乱压制   | 陆军增益   | 绝对主义     |

---

## 7. 常见错误

### 7.1 Scope 泄漏

```
# ❌ 忘记清理
option = {
    scope:xinhai_char = { ... }
    # 忘记 clear_saved_scope
}

# ✅ 在 after 块清理
after = {
    clear_saved_scope = xinhai_char
}
```

### 7.2 Modifier 叠加

```
# ❌ 直接添加导致双重生效
add_country_modifier = { modifier = gacha_xinhai_c2_aura_modifier }

# ✅ 先移除再添加
remove_country_modifier = gacha_xinhai_c0_aura_modifier
add_country_modifier = { 
    modifier = gacha_xinhai_c2_aura_modifier 
    years = -1 
}
```

### 7.3 迭代器误用

```
# ❌ any_character 不是 effect
immediate = {
    any_character = { ... }  # 错误！
}

# ✅ 使用 random_character 或 every_character
immediate = {
    random_character = { ... }
}
```

### 7.4 Scope 提前清理

```
# ❌ 在 effect 中清理 (事件异步执行时 scope 已失效)
scope:xinhai_char = { ... }
trigger_event_non_silently = { id = xxx }
clear_saved_scope = xinhai_char  # 太早！

# ✅ 在事件 after 块中清理
after = {
    clear_saved_scope = xinhai_char
}
```

---

## 8. 单角色实现清单

```markdown
## V3角色: {char_name}

### 代码文件
- [ ] `traits/gacha_{char}_traits.txt` (4个trait)
- [ ] `static_modifiers/gacha_{char}_modifiers.txt`
- [ ] `scripted_effects/gacha_{char}_effects.txt`
- [ ] `events/gacha_{char}_events.txt`

### Trait 定义
- [ ] gacha_core_trait (共用)
- [ ] gacha_{char}_aura_trait
- [ ] gacha_{char}_ruler_trait
- [ ] gacha_{char}_profession_trait

### 事件 ID
- [ ] Event .1: 首抽传记
- [ ] Event .2: 通用命座提升 (C1/C3/C5)
- [ ] Event .11: C2 觉醒
- [ ] Event .13: C4 超越
- [ ] Event .14: C5 事件
- [ ] Event .15: C6 满命
- [ ] Event .30-.31: C3 好感事件

### 本地化
- [ ] 所有 Trait 名称/描述
- [ ] 所有 Modifier 名称/描述
- [ ] 所有 Event 标题/描述/选项
- [ ] 使用 script_values 引用

### 测试
- [ ] 首抽流程完整
- [ ] C1-C6 升级事件触发
- [ ] C3 分支对话两条路径
- [ ] scope 在事件 after 块正确清理
- [ ] error.log 无报错
```

---

## 9. 实现路线图

### Phase 1: 心海 V3 改造 (2周)

* [ ] 扩展传记事件文本
* [ ] 添加 C1/C5 命座事件
* [ ] 实现 C3 好感事件
* [ ] 完善 Trait 面板文案

### Phase 2: V3 模板化 (1周)

* [ ] 更新 `character_[generator.py](<http://generator.py>)` 支持 V3
* [ ] 创建 V3 JSON 配置示例
* [ ] 测试自动生成流程

### Phase 3: 菲谢尔 V3 实装 (2周)

* [ ] 双声部演出系统 (菲谢尔+奥兹)
* [ ] 完整 C1-C6 事件链
* [ ] C3 雨中花园分支事件

---

## 10. V2 vs V3 对比

| 维度                 | V2 实现  | V3 设计       | 提升  |
| -------------------- | -------- | ------------- | ----- |
| :---                 | :---     | :---          | :---: |
| **Trait 数量** | 3个      | 4个 (含 core) | +1    |
| **传记长度**   | ~100字   | ~300字        | 3×   |
| **命座事件**   | C2/C4/C6 | C1-C6 全覆盖  | 2×   |
| **玩家互动**   | 无       | C3 分支对话   | 新增  |
| **叙事深度**   | 功能介绍 | 成长弧线      | 质变  |

---

## 相关文档

* [Spec: Gacha System](spec_gacha_system.md) - 抽卡核心逻辑
* [Spec: Scope Management](spec_scope_management.md) - Scope 管理规范
* [Design: Affinity System](design_affinity_system.md) - 好感度系统设计

---

 **文档维护者** : AI + sansm

 **创建日期** : 2025-11-25

 **最后更新** : 2025-11-26

现人神巫女 · 珊瑚宫心海

### 一、抽到她时弹出的完整角色传记（第一人称长文）

 **标题** ：现人神巫女·珊瑚宫心海 — 临时战略顾问

 **正文** ：

> 「我是珊瑚宫心海。虽然早有预感，但被直接召唤到这里还是意外。
>
> 刚才看了您的疆域图。补给线比海祇岛复杂百倍，列强外交盘根错节。这些行政文书堆成山，我的能量快耗尽了。
>
> 您用了召唤仪式，想必是遇到了死局。作为军师，我无法对混乱战局坐视不理。我会试着推演局势。
>
> 但请记住，胜局已定后，务必准许我回房间休息。一定要准许。」

### 二、C0 初始三格（完整长段独白）

| Trait 名称               | 能力数据                                                       | 完整独白（原版语感长文）                                                                                                               |
| ------------------------ | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **海祇岛珊瑚灯火** | 疾病抗性 +40%`<br>`荒废恢复 +0.06 `<br>`阶层满意恢复 +0.02 | 「你的国土在生病……就像以前圣土白化一样。望泷村的珊瑚灯亮着的时候，我总觉得一切都会好起来。或许……我可以把那种感觉也带到这里来。」   |
| **望泷村军师少女** | 海军士气 +20%`<br>`海军移动 +20%`<br>`海军损耗 -20%        | 「在望泷村的海风里推演兵书，感觉敌人都会被浪花冲走呢……你的战场比我想的要大很多。我试着庙算一次，只是这一次，打完我就想回去睡觉了。」 |
| **现人神巫女之位** | 全局叛乱 -0.10 `<br>`战争耗损 -0.10 `<br>`纪律 +0.10       | 「您让我坐在这个显眼位置，但我不习惯万众朝拜。比起统治，我更希望像御灵祭那样，让人们心灵平静。民心安定，叛乱火种自然熄灭。」           |

### 三、命座升级长事件与面板进阶

| 命座         | 升级类型   | 进阶 Trait / 能力变化                                                                                            | 事件标题                           | 完整事件独白 / 面板变更文案                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------ | ---------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **C1** | 专属机制   | **内阁席位 +1**                                                                                            | **意外多出的位置**           | 「没想到……我的推演让你的内阁多出了一个位置。谢谢你陪我散步这么久，既宝贵又难得的时间。望泷村的晚风吹过来的时候，我总觉得……多一个人商量，战争或许能少死一些人。」                                                                                                                                                                                                                                                                                                |
| **C2** | 光环升级   | **白夜国 · 圣土潮音** `<br>`疾病抗性 +80%`<br>`荒废恢复 +0.12 `<br>`阶层满意恢复 +0.04              | **圣土潮音初现**             | **[事件独白]** `<br>`「你的土地开始白化了……这比圣土还严重。我以前在海祇岛也见过那样的景象。大海总能给我带来不同的心境，可现在……我得再想想办法，不能让这里也变成沙漠。」`<br><br>` **[面板文案]** `<br>`「听到了吗？那是圣土中涌动的潮音。我已将海祇的仪式融入了这片大地。瘟疫会被海水 **洗净** ，废墟会在潮汐中 **重生** 。只要这声音不停，各阶层的**人心**便不会干涸。请放心，这片土地正在呼吸。」                         |
| **C3** | 好感事件   | 解锁好感剧情                                                                                                     | **望泷村的月亮，和我的王座** | （详见下文独立章节：C3 好感事件分支）                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **C4** | 职业升级   | **渊下宫 · 抗狩龙王** `<br>`海军士气 +40%`<br>`海军移动 +40%`<br>`海军损耗 -40%`<br>`船耐久 +0.08 | **渊下龙王觉醒**             | **[事件独白]** `<br>`「我又梦见渊下宫的灯火了……映在水面上，像长出了鳞片。你的舰队在海上排开阵型的时候，我突然就知道该怎么做了。兵法之道，在于庙算于未雨绸缪之际……只是，我有点累了。」`<br><br>` **[面板文案]** `<br>`「我梦见过深海龙蜥的狩猎……那种在黑暗中潜游的压迫感。现在，我将这种战术赋予您的舰队。它们将如幽灵般 **迅捷** ，如礁石般 **坚固** 。在这片大海上，没有风浪能**损耗**您的意志——因为舵盘，在我手中。」 |
| **C5** | 专属机制   | **国策槽位 +1**                                                                                            | **意外多出的国策位**         | 「没想到国策多出了一个位置……我不太擅长应付这么多目光。我明明说过我只是军师而已……不过，弱者要团结，才能反抗。既然来了，我就再陪你走一段吧。」                                                                                                                                                                                                                                                                                                                    |
| **C6** | 统治者升级 | **奥罗巴斯 · 现人神** `<br>`叛乱 -0.20 `<br>`战争耗损 -0.20 `<br>`纪律 +0.20                        | **奥罗替身一心**             | **[事件独白]** `<br>`（见下方 C6 满命完整长独白）`<br><br>` **[面板文案]** `<br>`「曾经，我视『现人神巫女』之位为一种不得不背负的责任。但如今……看着您的背影，我明白了『统治』的真意。不必担忧**叛乱**与 **疲惫** ，我会像奥罗巴斯守护海祇岛一样，用绝对的**纪律**与温柔，为您守住这万世太平。」                                                                                                                               |

### 四、C6 满命后，角色面板常驻长独白

> 「我是珊瑚宫心海。
>
> 以前在海祇岛，我总躲在渊下宫推演兵书。只要算尽变数，就能保护大家，维持和平假象。
>
> 那天你把我召唤来，面对这个比稻妻庞大百倍的帝国，我其实害怕。害怕庙算出错，害怕陌生目光，害怕辜负期待。
>
> 但你从未催促，也从未怀疑。你陪我在深夜的地图桌前看月亮，为我在内阁加了一把椅子。
>
> 不知从何时起，我不再想着『打完这一仗就回去睡觉』了。
>
> 我看遍这片大陆的日出日落，你的舰队学会像海祇岛鱼群那样呼吸，你的疆土上开满不再枯萎的花。
>
> ……谢谢你。谢谢你陪我走这么远。
>
> 能不能……再多陪我散散步？以前，大海总能给我带来不同的心境。
>
> 而现在……
> **看着你的背影，我就像看到了大海。因为这片海，已经在你的国土里，也在我的心里了。** 」

### 五、珊瑚宫心海 · C3 好感事件（分支对话树）

 **事件名称** ：月光下的异世界闲聊
 **触发条件** ：心海命之座 C3
 **事件时长** ：约 2 分钟

**事件开场（玩家视角）：**
处理完朝政，我走到露台吹风。月亮圆得异常。身后脚步轻柔，心海抱着兵书出现。她愣住，想逃又停下。
我拍拍石阶，她坐下，夜风吹来，我披上披风给她。她耳尖红了，低头小声：「谢谢……」
我们沉默看月。她忽然开口：「这个月亮……让我想起故乡。」

### 【第 1 轮：玩家开场白】

* **A. 「看你看得出神……是想起了故乡的月色吗？」** （好奇探索）
* **心海** （眼睛亮起）：「嗯……海祇岛的月亮下面，是望泷村的珊瑚灯。孩子们放进海里，像星星掉进大海。我总坐在岸边看，感觉烦恼都会被浪花冲走。」
* **B. 「今晚难得安静，一起坐坐？」** （温柔陪伴）
* **心海** （放松肩）：「好……谢谢你陪我这么久，既宝贵又难得的时间。大海总能给我带来不同的心境，今晚的风，也很温柔。」
* **C. 「兵书看得累了？休息会儿。」** （关心日常）
* **心海** （抱紧书，害羞笑）：「有点……我不太擅长和人相处，但兵法之道，在于庙算于未雨绸缪之际。今晚不推演了，就看看月亮吧。」

### 【第 2 轮：根据上轮回应展开】

* **若 A（好奇）** ：
* **A1. 「珊瑚灯？听起来很美，说说你的世界。」**
  * **心海** ：「海祇岛很小，但岛民团结。弱者要团结，才能反抗……就像我推演兵书，总想用最小代价守护最大宁静。」
* **B1. 「比我的王座美多了。」** （自嘲拉近）
  * **心海** （轻笑）：「王座……我不太习惯那么显眼的地方。望泷村的灯火才安静。」
* **若 B（陪伴）** ：
* **A2. 「你的世界，有大海吗？」**
  * **心海** ：「有……沧海明月，我总去海边散步。谢谢陛下今晚陪我。」
* **B2. 「风冷了，再靠近点。」** （暧昧推进）
  * **心海** （耳红，低头）：「……嗯。我本来想打完仗就回去的，可你总在这种时候出现。」
* **若 C（关心）** ：
* **A3. 「推演我的战争，累坏了吧？」**
  * **心海** ：「有点……但兵书让我觉得，一切都能有解。陛下，你的战场……我试着守护。」
* **B3. 「今晚不谈战争，说说你吧。」**
  * **心海** （惊讶开心）：「我？渊下宫的灯火很安静，我本想一辈子躲在那里看书……」

### 【第 3 轮：最终玩家台词与结局】

* **高好感路径（承接 A 系列）：**
  * **玩家** ：「听你说故乡，我都想去看看了。」
  * **心海** （脸红，声音软）：「欸？！海祇岛很小……但如果你想去，我可以尝试推演怎么回去。今晚……真的很开心。望泷村的月亮，和陛下的王座，好像也没那么远了。」
* **中好感路径（承接 B 系列）：**
  * **玩家** ：「下次再陪你看月亮。」
  * **心海** （慌张低头）：「明天还有战争……不过，如果你坚持的话……谢谢你。」
* **低好感路径（承接 C 系列）：**
  * **玩家** ：「早点休息，明天继续推演。」
  * **心海** （小哈欠，微笑）：「嗯……晚安。谢谢陛下。」

 **事件结尾** ：
她抱着书小跑离开，回头挥手：「晚安！」
我看着月亮，笑了笑。
这个异世界的少女，让铁血王座，多了一丝海风的温柔。
