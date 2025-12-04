# EU5 Official Modding Tutorial Reference

**Source**: [Tinto Talks #85 - Modding](https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-85-22nd-of-october-modding.1864004/)  
**Author**: PDX Ryagi / Stiopa866  
**Extracted**: 2025-12-04  
**Status**: 🔴 Official Reference

---

## 1. Jomini Framework

EU5 使用 **Jomini Framework**，与以下游戏共享核心机制：
- Crusader Kings 3 (CK3)
- Victoria 3 (Vic3)
- Imperator: Rome (I:R)

这意味着很多脚本语法和概念是通用的，但具体实现可能有差异。

---

## 2. Mod 设置

### 2.1 创建Mod Stub
通过游戏内工具创建：
1. 打开启动器 → Mods
2. 创建新Mod
3. 设置metadata和目录结构

### 2.2 Playset 配置
- 每个Mod需要加入Playset才能生效
- 可以在启动器中管理多个Playset

---

## 3. Event 语法 (官方示例)

### 3.1 基础结构

```paradox
country_event = {
    id = my_mod.1
    
    # 动态历史事件 - 不使用 mean_time_to_happen
    dynamic_historical_event = yes
    
    trigger = {
        # 触发条件
        has_country_flag = some_flag
    }
    
    # 插图标签 - 控制事件图片
    illustration_tags = { event_picture_tag }
    
    immediate = {
        # 事件触发时立即执行
        set_variable = { name = my_var value = 1 }
    }
    
    option = {
        name = my_mod.1.option_a
        
        # 选项效果
        grant_estate_privilege = {
            estate = estate_type:some_estate
            privilege = some_privilege
        }
    }
}
```

### 3.2 关键语法点

| 语法 | 说明 |
|:---|:---|
| `dynamic_historical_event = yes` | 替代旧的MTTH机制 |
| `illustration_tags = { ... }` | 事件插图标签 |
| `grant_estate_privilege` | 授予阶层特权 |
| `estate_type:xxx` | 阶层类型引用 |

> [!IMPORTANT]
> EU5 **没有** `character_event` 类型，只有 `country_event`、`location_event` 等。

---

## 4. Situations 系统

### 4.1 定义文件
位置: `common/situations/`

```paradox
my_situation = {
    # Situation 定义
    trigger = {
        # 何时激活
    }
    
    on_start = {
        # 开始时执行
    }
    
    on_end = {
        # 结束时执行
    }
}
```

### 4.2 本地化
需要为Situation提供对应的本地化键。

---

## 5. Script Values 带参数

### 5.1 定义 (common/script_values)

```paradox
my_script_value = {
    # 接受参数的写法
    value = "$arg1$"
    multiply = "$multiplier$"
}
```

### 5.2 调用

使用 `""` 语法传递参数：

```paradox
# 在其他地方调用
some_value = {
    value = my_script_value
    arg1 = 10
    multiplier = 2
}
```

---

## 6. Mapmodes 自定义

位置: `gfx/map/mapmodes/`

可以创建自定义地图模式，语法类似Situations：
- 定义颜色
- 定义Tooltip
- 需要对应本地化

---

## 7. File Watchers (即时更新)

游戏内置 **文件监视器**：
- 修改Mod文件后，游戏可以**即时刷新**
- 无需重启游戏即可看到变化
- 对脚本文件生效

使用方法：
1. 保存脚本文件
2. 在游戏中触发相关内容
3. 观察新变化

> [!TIP]
> 这大大加速了Mod开发迭代速度。

---

## 8. 与我们项目的对照

### 8.1 已确认正确的做法

| 我们的实现 | 官方确认 |
|:---|:---|
| 使用 `country_event` | ✅ 正确 |
| 使用 `trigger = { ... }` | ✅ 正确 |
| 使用 `immediate = { ... }` | ✅ 正确 |
| 使用 `set_variable` | ✅ 正确 |
| 使用 `estate_type:xxx` 引用 | ✅ 正确 |

### 8.2 需要注意的点

| 问题 | 官方说明 |
|:---|:---|
| `illustration_tags` | 我们使用trait系统做立绘，不使用illustration_tags |
| `dynamic_historical_event` | 我们的事件不需要这个标记 |
| Script Value参数 | 可以用 `$arg$` 语法传递参数 |

### 8.3 新发现

1. **Jomini Framework** - 可以参考CK3/Vic3的文档和模式
2. **File Watchers** - 利用即时刷新加速调试
3. **Situations** - 未来可探索用于状态管理

---

## 9. 下一步行动

- [ ] 验证 Script Value 参数语法是否在我们场景适用
- [ ] 探索 illustration_tags 替代当前trait立绘方案
- [ ] 测试 file watcher 功能加速开发

---

**文档维护者**: AI  
**最后更新**: 2025-12-04
