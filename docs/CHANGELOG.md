# Changelog

本文件记录 **EU5 Gacha Mod** 的对外版本变更（`metadata.json`）。  
内部架构仍沿用“V3 角色工作流/抽卡内核”的称呼，不与对外版本号强绑定。

---

## 0.4.0 (2025-12-16)

### Added
- **原神七国系统原型（璃月）**
  - 静态国家 TAG：`GL1`（颜色、旗帜、名字可控）
  - 附庸类型：`gacha_archon_vassal`
  - 刻晴专属交互「璃月计划」→ 事件两幕 → 解锁内阁行动「再造璃月」
  - 内阁行动创建/修复璃月：首都东莞 `dongguan` (10778)，并自动成为玩家附庸
  - 建国后 **10 年强力增益** + **常驻温和增益**（贸易/建造/生产）
- **璃月筹建局势（Situation）**
  - 局势：`gacha_liyue_reconstruction`
  - 必做前置：局势行动 `gacha_liyue_build_market`（让东莞成为独立市场所在地）
  - 进度系统：基础 5/月（受内阁效率影响）+ 投入加速（50/200/500）
  - 达到 100：立即建国并结束局势（无需等待下月 tick）
- **璃月国家修正**
  - `gacha_liyue_foundation_boom_modifier`（10 年，起飞期）
  - `gacha_liyue_trade_hub_modifier`（常驻，贸易港）

### Changed
- **角色身份标准化（全角色通用）**
  - 角色创建/重复抽取路径统一补齐宗族（dynasty）与阶层（estate）
  - 仅在角色不是统治者时分配到 `gacha_estate`（避免“抽出来变贵族/王权混乱”）
  - 重复抽取时不强行把“已成为统治者的角色”拖回玩家国（为七国君主预留）
- **璃月行动从常驻列表迁移为解锁式**
  - 需要先通过刻晴交互解锁，减少内阁列表噪音

### Fixed
- **Cabinet Action 作用域错误**
  - 内阁行动的 `root` 为 `cabinet`，需要使用 `scope:actor` 才能在国家作用域执行建国相关 effect
- **刻晴统治宗族/王权显示异常**
  - 确保刻晴成为璃月统治者，并拥有可显示的命名宗族；清理建国时残留的默认王室成员
- **重复点击触发多事件实例**
  - 交互增加锁变量，事件 `after` 释放锁；一次性解锁后按钮置灰
- **本地化重复键**
  - `GL1/GL1_ADJ` 统一集中到 `gacha_country_names_l_*`，避免重复定义
- **英文本地化静态检查报错（CWTools/CW266）**
  - 移除 `gacha_events_interaction_desc` 中的 `[actor.GetName]`，避免 IDE 扩展误报（游戏内可用性以引擎为准）
- **GUI 日志刷屏（BlockList.GetBlocks / messages.gui:54）**
  - 新增 `in_game/gui/zz_gacha_messages_patch.gui`：为 message popup 的描述区补齐 `BlockList` 上下文（纯 UI 修复）
  - ⚠️ 注意：该文件会覆盖原版 `template message_template`，与其他改 messages 的 UI 模组可能冲突（需要时可临时移除验证）

### Assets / Notes
- 新增事件图：`main_menu/gfx/event_pictures/gecha_LiY.dds`（璃月计划两幕使用）
- 旗帜管线（静态 TAG）：
  - 旗帜纹理：`main_menu/gfx/coat_of_arms/textured_emblems/te_gacha_GL1_liyue_flag.dds`
  - 旗帜定义：`main_menu/common/flag_definitions/gacha_flag_definitions.txt`
  - CoA 定义：`main_menu/common/coat_of_arms/coat_of_arms/gacha_coat_of_arms.txt`

### Known Issues
- 旧存档若经历过早期“多次 set_new_ruler”方案，历史列表里可能仍残留重复的旧王条目；新实现不会继续制造更多重复条目。

---

## Lessons Learned (经验与教训)

1. **先确认 Base Scope，再写 effect**：内阁行动/交互/事件的 base scope 不同；错误 scope 会直接导致脚本系统报错。
2. **一切交互都要有“防连点”机制**：用锁变量 + 事件 `after` 释放锁是最稳的通用方案。
3. **角色身份要“收口”**：dynasty/estate/culture/religion 等应由一个公共 effect 统一兜底，避免分散逻辑导致状态漂移。
4. **本地化键集中管理**：国家名/形容词等公共键应放在单独文件，避免多人协作产生重复定义。
5. **以代码为真相，文档随代码走**：`docs/` 中的旧结论可能失效；遇到冲突以 base game + 本项目已跑通实现为准。
6. **把“悬浮也会执行脚本”当成默认**：交互/事件选项的复杂逻辑统一放 `hidden_effect`；避免递归兜底；不要把 `Character` 存入 `global_variable_list`。
7. **Situation 里 scope 很容易“跑偏”**：进入 `location:` 后再访问 `var:target_country` 会读到 location 自己的变量；需要用 `root.var:target_country` 回到 Situation 上的变量。
8. **UI 条件输出要可读**：避免让复杂 trigger 被引擎自动“展开成 25%/是广州/is_ai”这种误导文本；对玩家展示统一用 `custom_tooltip`，逻辑判断放脚本内部。
9. **尽量不 Patch 原版；Patch 必须可回滚**：能用新增内容解决就不覆盖原版；若不得不覆盖（如 message_template 修复日志），必须在文档里标注原因、文件路径和兼容性风险。
