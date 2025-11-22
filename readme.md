<div align=center> <img src="https://sansme.oss-cn-beijing.aliyuncs.com/thumbnail.png" width="360" height="360"></div>

# EU5 Gacha Mod - 抽卡系统

将原神的抽卡系统带入Europa Universalis V

## ✨ 当前实装功能

### 🎲 抽卡系统 ✅ **已完成**
- ✅ **概率系统**: 
  - 5星角色基础概率 0.6% 
  - 软保底机制（74抽起每抽+6%）
  - 硬保底机制（90抽必出）
  - 50/50机制: 50%当期UP角色，50%常驻池（歪了）
- ✅ **保底系统**:
  - 垫子计数器正常工作
  - 大保底标记（歪了下次必中）

### 👤 角色系统
#### 当前实装角色
- ✅ **珊瑚宫心海 (Sangonomiya Kokomi)** - 5星水元素

#### 角色特性
- ✅ 2D立绘显示 (基于特质系统)
- ✅ 专属属性buff
- ✅ 命座buff动态叠加
- ✅ 可担任将军、海军将领
- ✅ 可担任内阁职位
- ✅ 分配到Crown Estate (王权阶层)

### 🌟 命之座系统
**完整的7级命座系统**:
- C0 (基础) - C1 - C2 - C3 - C4 - C5 - C6 (满命)
- 每个命座提供独特的属性加成
- 命座升级触发专属故事事件
- 重复抽卡自动升级命座

### 📖 故事事件系统
#### 心海故事链
- ✅ 初次获得事件
- ✅ 命座2突破事件（海月之誓）
- ✅ 命座4突破事件（海祇姬君）
- ✅ 命座6突破事件（满命成就）


---


## 📂 项目结构

```
eu5_gacha/
├── in_game/
│   ├── common/
│   │   ├── scripted_effects/      # 抽卡逻辑、角色创建
│   │   ├── script_values/         # 概率计算
│   │   ├── character_interactions/ # 抽卡按钮
│   │   ├── character_modifiers/   # 角色buff
│   │   ├── on_actions/            # 游戏启动初始化
│   │   └── traits/                # 立绘触发特质
│   ├── events/                    # 故事事件
│   └── gfx/                       # 2D立绘资源
├── main_menu/
│   ├── common/
│   │   └── modifier_type_definitions/  # 命座等级显示
│   └── localization/              # 中文本地化
└── docs/                          # 设计文档与技术总结
```

---

## 🚀 使用方法

1. **启动游戏**: 在启动器中加载此mod
2. **进入游戏**: 开始或加载游戏
3. **打开角色面板**: 选择您的统治者
4. **点击\"祈愿\"交互**: 花费资源进行单次抽卡
5. **查看结果**: 
   - 抽到新角色会自动创建并加入您的国家
   - 抽到重复角色会提升命座等级
   - 触发专属故事事件
6. **Debug查看**: 使用游戏内Debug Tool查看：
   - `gacha_pity_count` - 当前垫子
   - `gacha_total_rolls` - 总抽卡次数
   - `gacha_is_guaranteed` - 大保底状态
   - `gacha_constellation_lvl` - 命座等级

---

## 🔄 下一步计划

### 高优先级
- [ ] **卡池系统**: 支持多期UP角色轮换
- [ ] **更多5星角色**: 添加第二个、第三个角色
- [ ] **角色添加工作流程**: 简化新角色创建流程

### 中优先级
- [ ] 4星角色系统
- [ ] 十连系统
- [ ] 祈愿历史记录

### 低优先级/研究中
- [ ] 婚姻系统（C6角色可娶）
- [ ] 亲密度系统
- [ ] 自定义Estate系统（技术难度高）

---

## 📚 文档

详细设计文档位于 `docs/` 目录：

---

## ⚖️ 版权声明

本mod为粉丝创作，仅供学习和娱乐用途。
- 角色设计版权归miHoYo所有
- Europa Universalis V版权归Paradox Interactive所有

**Mod Version**: 0.3.0 Alpha  
**Last Updated**: 2025-11-22  
**Status**: 🟢 抽卡系统雏形完成，可正常游玩
