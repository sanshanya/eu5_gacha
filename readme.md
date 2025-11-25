<div align=center> <img src="https://sansme.oss-cn-beijing.aliyuncs.com/thumbnail.png" width="360" height="360"></div>

# EU5 Gacha Mod - 抽卡系统

将原神的抽卡系统带入Europa Universalis V

## ✨ 当前实装功能

### 🎲 抽卡系统 ✅ **完整可用**
- ✅ **概率系统**: 
  - 5星角色基础概率 0.6% 
  - 软保底机制（74抽起每抽+6%）
  - 硬保底机制（90抽必出）
  - 4星保底（9抽必出）
  - 块内保底（每10抽至少1个4/5星）
  - 50/50机制: 50%当期UP角色，50%常驻池（歪了）
- ✅ **保底系统**:
  - 垫子计数器正常工作
  - 大保底标记（歪了下次必中）
- ✅ **单抽/十连**:
  - 单抽: 16金币
  - 十连: 160金币
  - 允许负金币抽卡（支持借贷）
  - 十连3星静默，4/5星逐个弹窗

### 👤 角色系统
#### 当前实装角色
- ✅ **珊瑚宫心海 (Sangonomiya Kokomi)** - 5星水元素 (UP池)
- ✅ **雷电将军 (Raiden Shogun)** - 5星雷元素 (常驻池)

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

---


## 📂 项目结构

```
eu5_gacha/
├── in_game/
│   ├── common/
│   │   ├── scripted_effects/      # 抽卡逻辑、角色创建
│   │   ├── script_values/         # [已弃用] 概率计算
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
4. **点击"祈愿"交互**: 花费金币进行抽卡
   - 单抽: 16金币
   - 十连: 160金币
5. **查看结果**: 
   - 抽到新角色会自动创建并加入您的国家
   - 抽到重复角色会提升命座等级
   - 触发专属故事事件
6. **Debug查看**: 使用游戏内Debug Tool查看：
   - `gacha_pity_count` - 当前5星垫子（0-89）
   - `gacha_pity_4star` - 当前4星垫子（0-9）
   - `gacha_total_rolls` - 总抽卡次数
   - `gacha_is_guaranteed` - 大保底状态
   - `gacha_constellation_lvl` - 命座等级
   - `gacha_block_has_4star` - 当前块是否已出4/5星

---

## 🔄 下一步计划

### 高优先级
- [ ] **卡池系统**: 支持多期UP角色轮换
- [ ] **更多5星角色**: 添加第三、第四个角色
- [ ] **武器系统**: 实装武器池

### 中优先级
- [x] ~~4星奖励系统~~ ✅ **已完成**（金币/威望/正统性）
- [x] ~~十连系统~~ ✅ **已完成**
- [ ] 祈愿历史记录UI

### 低优先级/研究中
- [ ] 婚姻系统（C6角色可娶）
- [ ] 亲密度系统
- [ ] 自定义Estate系统（技术难度高）

---

## 📚 文档

## 📚 文档 (Documentation)
> **[文档总览 (Overview)](docs/spec/00_project_overview.md)**

### 📂 [Spec (规范与标准)](docs/spec/README.md)
*当前必须遵守的事实与标准*
- **[抽卡系统规范](docs/spec/spec_gacha_system.md)**: 核心机制、概率与奖池
- **[添加角色工作流](docs/spec/spec_workflow_add_character.md)**: 标准化开发流程
- **[脚本与Scope规范](docs/spec/spec_scope_management.md)**: 编码标准与避坑指南

### 📂 [Design (设计与分析)](docs/design/README.md)
*构想、逻辑与未来计划*
- **[剧情系统设计](docs/design/design_story_system.md)**
- **[特质与修正设计逻辑](docs/design/design_traits_and_modifiers.md)**
- **[婚姻与亲密度系统](docs/design/design_marriage_system.md)**

### 📂 [Archive (归档)](docs/archive/README.md)
*历史材料与日志*
- [RNG修复日志](docs/archive/archive_rng_fix_log.md)
- [旧技术参考](docs/archive/archive_technical_reference_old.md)

---

## 🔧 技术要点

### 随机数生成
使用质数混合算法确保分布均匀：
```
rand = 937 + 17×total_rolls + |treasury| + 13×pity + 7×block_index
```

### Silent内核架构
- 计算与展示分离
- Silent内核只负责逻辑计算
- Event层负责UI展示和玩家交互

### 概率公式
- 5星基础: 0.6% (6/1000)
- 5星软保底: 74抽起每抽+6%
- 5星硬保底: 90抽100%
- 4星基础: 5.1% (51/1000)
- 块内保底: 每10抽强制至少1个4/5星

---

## ⚖️ 版权声明

本mod为粉丝创作，仅供学习和娱乐用途。
- 角色设计版权归miHoYo所有
- Europa Universalis V版权归Paradox Interactive所有

**Mod Version**: 2.0.0  
**Last Updated**: 2025-11-23  
**Status**: 🟢 核心系统完整可用，经过重大Bug修复

