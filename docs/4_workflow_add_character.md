# 工作流：如何添加新角色 (Add New Character)

本文档详细说明如何向卡池中添加一位新角色（以“雷电将军” `raiden` 为例）。

## 1. 核心文件清单 (Checklist)

你需要创建或修改以下文件：

| 类别 | 路径 | 说明 |
| :--- | :--- | :--- |
| **特质** | `common/traits/gacha_raiden_traits.txt` | 定义角色的核心特质与属性加成 |
| **修正** | `common/static_modifiers/gacha_raiden_modifiers.txt` | 定义角色的永久修正 (可选) |
| **立绘** | `gfx/portraits/portrait_modifiers/gacha_raiden_portrait.txt` | 定义角色的 2D/3D 立绘绑定 |
| **本地化** | `localization/simp_chinese/gacha_raiden_l_simp_chinese.yml` | 名字、描述、事件文本 |
| **事件** | `events/gacha_raiden_events.txt` | 初次见面、命座提升、满命事件 |
| **逻辑** | `common/scripted_effects/gacha_common_effects.txt` | 复制并修改创建角色的 Wrapper |
| **奖池** | `common/scripted_effects/gacha_pools.txt` | 将角色加入卡池 |

---

## 2. 详细步骤 (Step-by-Step)

### 步骤 1：定义特质 (Traits)

创建 `common/traits/gacha_raiden_traits.txt`。
这是角色最核心的属性来源。

```paradox
gacha_raiden_origin_trait = {
    category = ruler
    allow = { always = no } # 只通过脚本添加

    modifier = {
        # 在这里写角色的强力 Buff
        global_tax_modifier = 0.20      # 税收 +20%
        land_morale_modifier = 0.10     # 士气 +10%
    }
}
```

### 步骤 2：配置立绘 (Portraits)

创建 `gfx/portraits/portrait_modifiers/gacha_raiden_portrait.txt`。
让游戏知道当角色拥有 `gacha_raiden_origin_trait` 时显示哪张图。

```paradox
gacha_raiden_portrait = {
    trigger = {
        has_trait = gacha_raiden_origin_trait
    }
    dna = "" # 如果使用 2D 立绘，留空或指向预设 DNA
    weight = {
        base = 100
    }
    # 这里通常配合 texture 路径，具体视美术资源而定
}
```

### 步骤 3：本地化 (Localization)

创建 `localization/simp_chinese/gacha_raiden_l_simp_chinese.yml`。
**注意**：文件名必须以 `l_simp_chinese.yml` 结尾。

```yaml
l_simp_chinese:
 # 名字
 gacha_first_name_raiden: "影"
 gacha_last_name_raiden: "雷电"
 
 # 特质
 gacha_raiden_origin_trait: "御建鸣神主尊"
 gacha_raiden_origin_trait_desc: "稻妻的雷神，追求永恒的统治者。\n§Y效果：§!\n税收：§G+20%§!\n士气：§G+10%§!"

 # 事件标题
 gacha_raiden_events.1.title: "雷霆的威光"
 gacha_raiden_events.1.desc: "一道紫色的雷光划破天际..."
 gacha_raiden_events.1.a: "直面雷光"
```

### 步骤 4：创建事件 (Events)

创建 `events/gacha_raiden_events.txt`。
你需要至少 3 个事件：
1.  `.1`: 初次获得 (First Meeting)
2.  `.2`: 命座提升 (Constellation Up)
3.  `.4`: 满命 (Max Constellation)

```paradox
namespace = gacha_raiden_events

# 1. 初次见面
gacha_raiden_events.1 = {
    type = country_event
    title = gacha_raiden_events.1.title
    desc = gacha_raiden_events.1.desc
    option = {
        name = gacha_raiden_events.1.a
    }
}

# 2. 命座提升
gacha_raiden_events.2 = {
    type = country_event
    title = gacha_raiden_events.2.title
    desc = gacha_raiden_events.2.desc
    option = { name = "OK" }
}

# 4. 满命
gacha_raiden_events.4 = {
    type = country_event
    title = gacha_raiden_events.4.title
    desc = gacha_raiden_events.4.desc
    option = { name = "OK" }
}
```

### 步骤 5：编写逻辑 Wrapper (Scripted Effects)

打开 `common/scripted_effects/gacha_common_effects.txt`。
复制 `gacha_create_xinhai_effect`，重命名为 `gacha_create_raiden_effect`。

**需要修改的关键点**：
1.  **全局变量锁**: `gacha_xinhai_is_summoned` -> `gacha_raiden_is_summoned`
2.  **特质检查**: `gacha_xinhai_origin_trait` -> `gacha_raiden_origin_trait`
3.  **事件 ID**: `gacha_xinhai_events.1/2/4` -> `gacha_raiden_events.1/2/4`
4.  **名字 Key**: `gacha_first_name_xinhai` -> `gacha_first_name_raiden`
5.  **注册调用**: `gacha_register_new_character = { who = raiden }`
6.  **数值**: 修改 `adm/dip/mil` 属性。

### 步骤 6：加入奖池 (Pools)

打开 `common/scripted_effects/gacha_pools.txt` (如果尚未创建，则在 `gacha_logic_effects.txt` 中修改)。

在 5 星池中加入一行：

```paradox
random_list = {
    # ... 其他角色 ...
    10 = { gacha_create_raiden_effect = yes }
}
```

---

## 3. 常见问题 (FAQ)

*   **Q: 角色名字显示乱码？**
    *   A: 检查 `.yml` 文件是否以 UTF-8 BOM 格式保存。
*   **Q: 抽到了但是没弹窗？**
    *   A: 检查 `gacha_raiden_events.txt` 顶部是否写了 `namespace = gacha_raiden_events`。
*   **Q: 角色没有特质？**
    *   A: 检查 `gacha_common_effects.txt` 里的 `gacha_register_new_character` 调用参数是否正确。
