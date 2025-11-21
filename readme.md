<div align=center> <img src="https://sansme.oss-cn-beijing.aliyuncs.com/thumbnail.png" width="360" height="360"></div>
# EU5 Gacha Mod - 原神抽卡系统

试图将原神的抽卡系统带入Europa Universalis V

## ✨ 

### 🎲 核心抽卡系统-存在BUG未实装
- ✅ **单抽交互**: 花费金币进行单次抽卡
- ✅ **概率系统**: 
  - 5星角色 2.4% (50/50机制: 50%当期UP角色，50%常驻角色)
  - 4星角色 97.6%
- ✅ **命之座系统**: 
  - 抽到重复角色时自动升级命之座
  - 支持C0-C6共7个等级
  - 命座等级影响角色属性

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

### 📖 故事事件系统

#### 心海故事链
- ✅ 初次获得事件
- ✅ 命座2突破事件
- ✅ 命座4突破事件
- ✅ 命座6突破事件

### 🎨 2D立绘系统
- ✅ 基于Trait的立绘触发
- ✅ 角色专属2D图像显示
- ✅ 图像自动缩放和裁剪工具

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
│   │   └── traits/                # 立绘触发特质
│   ├── events/                    # 故事事件
│   └── gfx/                       # 2D立绘资源
├── main_menu/
│   ├── common/
│   │   └── modifier_type_definitions/  # 命座等级显示
│   └── localization/              # 中文本地化
└── docs/                          # 设计文档
```

---

## 🚀 使用方法

1. **启动游戏**: 加载此mod
2. **打开角色面板**: 在游戏中选择您的统治者
3. **点击"祈愿"交互**: 进行单次抽卡
4. **查看结果**: 
   - 抽到新角色会自动创建并加入您的国家
   - 抽到重复角色会提升命座等级
   - 触发专属故事事件


### 计划中 🔄
- [ ] 更多5星角色
- [ ] 修复抽卡环节BUG
- [ ] 更多4星角色
- [ ] 十连系统
- [ ] 保底机制
- [ ] 祈愿历史记录
- [ ] 自定义Estate系统 (技术评估中)

---

## 📚 文档

详细设计文档位于 `docs/` 目录：
- `1_project_overview.md` - 项目总览
- `2_design_gacha_system.md` - 抽卡系统设计
- `3_design_story_system.md` - 故事系统设计
- `4_design_constellation_system.md` - 命座系统设计
- `5_reference_technical.md` - 技术参考
- `6_design_marriage_system.md` - 婚姻系统设计
- `7_advanced_features_analysis.md` - 高级功能分析
- `8_design_affinity_system.md` - 亲密度系统设计



---

## ⚖️ 版权声明

本mod为粉丝创作，仅供学习和娱乐用途。侵删。

**Mod Version**: 0.2.0 Alpha  
**Last Updated**: 2025-11-22
