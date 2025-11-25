# Trait & Modifier 设计说明：从“职位特效”到“全局加成”

> 目的：解释 EU5 中 trait 的实际生效范围，以及本 Mod 为什么将数值效果迁移到静态修正（character / country modifier），并以心海为例说明具体落地方案。后续所有角色数值与设计，应以本文为准进行评估与复盘。

---

## 1. 引擎机制回顾：Trait 不是“永远生效”

在最初的设计中，我们直觉上认为：

- “给角色加 trait = 给这个人加一串永久的数值加成”。

后来查阅官方 Wiki（例如：[EU5 Wiki – Characters > General traits](https://eu5.paradoxwikis.com/Characters#General_traits)）并实测之后发现：

> **Trait 的数值只在该角色担任特定“职位”时才生效。**

### 1.1 Trait Category 与职位绑定

EU5 中，trait 通过 `category = xxx` 来区分不同类型，常见有：

- `category = ruler`       → 只有在角色是“统治者”时生效  
- `category = general`     → 只有担任陆军将领时生效  
- `category = admiral`     → 只有担任海军将领时生效  
- `category = explorer`    → 只有担任探险家时生效  

这意味着：

- 角色虽然一直“拥有”这个 trait，但**只有当他当前的“职位”匹配对应 category 时，modifier 才会被纳入计算**；
- 比如一个 `category = general` 的 trait，在角色回到宫廷、不再担任将领的时候，其加成就不再生效。

### 1.2 直接把所有数值写进 trait 的问题

如果我们简单地把所有加成都堆在 `category = ruler` 的 trait 上，就会遇到几个问题：

1. **职位依赖**  
   - 一旦角色不再是统治者（比如被换下、改任顾问或将领），这些加成都不再作用于国家；
   - 对“陪伴向”角色来说，这违背了“只要人在你朝，Buff 就在”的体验预期。

2. **多职位冲突**  
   - 同一个角色可能既当统治者，又当将领/海军；  
   - 不同 category 的 trait 在切换职位时会来回生效/失效，数值表现很难控制。

3. **复用 & 调试困难**  
   - trait 既承担“人物性格/背景叙事”的职责，又承担一大堆数值，阅读和调试都非常不友好。

因此，我们最终选择了“**Trait 负责身份与叙事，真正的属性走静态修正**”的架构。

---

## 2. 本 Mod 的三层加成结构

为了既符合引擎机制，又达到“角色只要在你国就有影响力”的体验，我们把角色能力拆成三个层级：

1. **Trait（特质）** – 用于：
   - 展示角色身份、称号、命座等；
   - 触发立绘（通过 `ls_gacha_portrait_trigger`）；
   - 触发事件逻辑（某些 on_action / story event 可直接判断 trait）。
   - **不再承担主要数值加成。**

2. **Character Modifier（角色修正）** – 用于：
   - 给角色本身挂永久 Buff（无论当前担任何种职位）；
   - 例如：`gacha_xinhai_modifier`、`gacha_temp_regent_modifier`、`gacha_former_ruler_modifier`；
   - 可以在 UI 中看到对应图标和名称，方便玩家理解是谁在加成。

3. **Country Modifier（国家修正）** – 用于：
   - 表达“角色存在即影响整个国家”的光环效果；
   - 例如：心海的 `gacha_xinhai_country_modifier`、命座 C2/C4 的全局修正；
   - 挂在国家上，与角色当前职位无关，只要脚本逻辑认定她在你国、满足条件，就可以生效。

整体原则是：

> **Trait 主要负责“是谁”，Modifier 负责“加了什么”，Country Modifier 负责“全局影响”。**

---

## 3. 心海案例：从 Trait 转移到 Modifier 的完整过程

### 3.1 原始设计（错误假设）

最开始，心海的数值全部写在 trait 里：

文件：`in_game/common/traits/gacha_xinhai_traits.txt`（旧版）

```paradox
gacha_xinhai_origin_trait = {
    category = ruler
    allow = { always = no }
    modifier = {
        legislative_efficiency       = 0.3
        character_cabinet_efficiency = 0.75
        country_cabinet_efficiency   = 0.25
        cultural_influence_modifier  = 0.15
    }
}
```

问题在于：

- 一旦心海不是统治者（比如被你用代政系统换下去），这些加成都完全消失；
- C2/C4 等命座的效果同样受职位限制，导致“她还在你宫里，但 Buff 不再生效”的违和感。

### 3.2 调整方案：把数值迁移到静态修正

我们采用如下拆分：

1. **Trait 变为“空壳 + 叙事”**

```paradox
gacha_xinhai_origin_trait = {
    category = ruler
    allow = { always = no }
    modifier = { } # 数值全部迁出，改用修正承担
}
```

她的具体说明和“看起来很强”的描述，放在本地化里，而不是直接挂数值。

2. **角色级修正：`gacha_xinhai_modifier`**

文件：`main_menu/common/static_modifiers/gacha_xinhai_modifiers.txt`

```paradox
gacha_xinhai_modifier = {
    game_data = { category = character decaying = no }
    gacha_core = yes
    gacha_water_godeye = yes
    character_cabinet_efficiency = 0.75
}
```

- 这个修正由通用注册内核 `gacha_register_new_character` 挂在角色身上；
- 只要心海存在于你国宫廷，无论是不是统治者/顾问/将领，都拥有这部分“个人能力”。

3. **国家级修正：`gacha_xinhai_country_modifier` + 命座扩展**

同一文件中新增：

```paradox
gacha_xinhai_country_modifier = {
    game_data = { category = country decaying = no }
    legislative_efficiency      = 0.3
    country_cabinet_efficiency  = 0.25
    cultural_influence_modifier = 0.15
}

gacha_xinhai_c2_country_modifier = {
    game_data = { category = country decaying = no }
    global_estate_satisfaction_recovery = 0.25
    global_disease_resistance           = 0.25
    global_devastation_recovery         = 0.5
}

gacha_xinhai_c4_country_modifier = {
    game_data = { category = country decaying = no }
    naval_morale_modifier = 0.3
    navy_movement_speed   = 0.3
    navy_repair_cost      = -0.5
}
```

- `gacha_xinhai_country_modifier` 表达心海“作为军师，对整个国家行政/内阁/文化的持续影响”；
- C2/C4 的国家修正在达到对应命座等级时挂上，确保“命座提升 = 国家层面得到新能力”，而非仅仅是她个人数值上涨。

4. **挂载逻辑：在心海专属 effect 中统一处理**

文件：`in_game/common/scripted_effects/gacha_xinhai_effects.txt`  
（伪代码示意）

```paradox
gacha_xinhai_apply_country_modifiers = {
    root = {
        remove_country_modifier = gacha_xinhai_country_modifier
        remove_country_modifier = gacha_xinhai_c2_country_modifier
        remove_country_modifier = gacha_xinhai_c4_country_modifier
    }

    root = {
        add_country_modifier = { modifier = gacha_xinhai_country_modifier years = -1 }
    }
    if = {
        limit = { var:gacha_constellation_lvl >= 2 }
        root = { add_country_modifier = { modifier = gacha_xinhai_c2_country_modifier years = -1 } }
    }
    if = {
        limit = { var:gacha_constellation_lvl >= 4 }
        root = { add_country_modifier = { modifier = gacha_xinhai_c4_country_modifier years = -1 } }
    }
}
```

每当心海创建 / 命座变化时调用这个 helper，使国家修正与命座等级保持同步。

### 3.3 心海的“UI 表现”与“实际计算”的分离

现在，心海相关的“表层信息”和“底层数值”是这样分工的：

- **Trait + 本地化**：负责告诉玩家“她是谁、她的称号/命座叫啥、故事氛围如何”；
- **角色修正 `gacha_xinhai_modifier`**：标记她是抽卡角色、拥有水元素神之眼，并附带一部分“个人能力”；
- **国家修正 `gacha_xinhai_country_modifier` / C2 / C4**：真正承载她作为军师/舰队指挥对整个国家的硬数值加成；
- **命座脚本**：通过 `gacha_constellation_lvl` 控制何时给国家挂上额外的修正。

---

## 4. 对未来角色设计的约束与建议

为避免后续角色再走一遍“把所有数值塞进 trait 再迁移出来”的弯路，建议后续设计统一遵守以下规则：

1. **Trait 只写“身份/风味”，不写主要战力**
   - 如果确实需要极少量补充（例如 +1 声望之类），也要确保不会因为职位切换而导致体验割裂；
   - 大部分战力应放在 static modifiers 中。

2. **所有“角色在就有”的 Buff 一律走修正**
   - 角色本体 → `gacha_<id>_modifier`（character modifier）；
   - 全局光环 → `gacha_<id>_country_modifier` 等（country modifier）。

3. **命座/突破等长线成长用修正叠加实现**
   - 命座等级变量只用来控制“应该挂哪几个修正”；
   - 不要在命座 trait 自身的 modifier 里堆数值。

4. **判定逻辑尽量使用修正而非 trait**
   - `has_character_modifier = gacha_<id>_modifier` / `gacha_former_ruler_modifier`  
   比 `has_trait = ...` 更直观可控，不受职位影响。

5. **特殊角色（如代政前统治者）优先用专门修正标记**
   - 本案例中，`gacha_former_ruler_modifier` 就同时作为：
     - UI 显示（“前任统治者”）  
     - 逻辑判定（是否在“可再次被任命为统治者”的候选池）

---

## 5. 后续工作：数值与角色设计再评估

在统一了上述设计之后，接下来需要做的事情是：

1. **逐个角色审查 trait 中的 modifier**
   - 列出所有 `gacha_*_traits.txt` 中仍带有显著数值的 trait；
   - 判断这些数值是否应该迁移到 `gacha_*_modifier` 或新的国家修正。

2. **对比静态修正的数值强度**
   - 按“单个角色能带来的总战力”维度，而不是“单个 trait 的数值”；
   - 考虑命座阶段（C0/C2/C4/C6）如何平滑递进。

3. **统一 UI 文案和图标语义**
   - trait 名 / 修正名 / 国家修正名 在本地化中要清晰区分“个人实力”和“国家光环”；
   - 图标可以共享，但描述里要明确这是“角色修正”还是“国家修正”。

等这轮梳理完成后，本 Mod 的角色设计就会从“堆 trait 数值”彻底过渡到“清晰的三层结构”。这不仅方便未来扩展新角色，也让玩家更容易理解每个角色真正提供了哪些能力。  
