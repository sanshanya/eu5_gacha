# Official Modding Guides Analysis & Recommendations

**Date**: 2025-11-25  
**Analyzed Documents**: 
- `modding.html` - General modding guide
- `modding2.html` - Advance modding guide

---

## 📊 官方文档的优秀模式

### 1. **明确的文档元数据**
```
This article is timeless and should be accurate for any version of the game.
This article has been verified for the current version (1.0) of the game.
```

**启发**: 
- ✅ **我们已经在做**: `spec_engine_basics.md` 有 `Last Verified: 2025-11-25`
- ⚠️ **可改进**: 添加"版本适用性"标记

---

### 2. **Technical Details 部分**

官方在每个技术主题开头都有:
```
Technical details
Advance definitions are stored in common/advances. 
They are usually placed in the common top folder.
Example of such a file: in_game/common/advances/0_age_of_discovery.txt
```

**启发**:
- **文件位置先行**: 告诉读者"东西在哪"
- **示例文件引用**: 指向实际代码文件

**对比我们的文档**:
- ✅ `spec_workflow_add_character.md` 有文件路径
- ❌ `spec_gacha_system.md` 缺少"Technical Details"导引

---

### 3. **Syntax 分层结构**

```
Syntax
├── Age requirement
├── Modifiers
├── Setting requirements
├── Controlling tree generation
├── Controlling AI bias
├── Research cost
└── Icon
```

**启发**: 
- **属性分类**: 每个配置项独立小节
- **渐进式复杂度**: 从简单到复杂排列

**对比我们的文档**:
- ❌ `spec_gacha_system.md` 混合了概念和实现

---

### 4. **Best Practices 独立章节**

```
Best practices
- Use proper indentation
- Add comments
- Avoid overwriting items you didn't change
```

**启发**:
- **工程建议前置**: 不是藏在最后
- **简洁bullet points**: 易扫描

**对比我们的文档**:
- ✅ `design_project_guidelines.md` 有类似内容
- ❌ 但在 design/ 而非 spec/,新人可能找不到

---

### 5. **Debugging 专门章节**

```
Debugging
- Read the error.log
- -debug_mode flag
- UTF-8 with BOM encoding
- Filename conventions
```

**启发**:
- **调试工具集中**: 所有debug技巧一处查
- **常见问题预判**: Common problems 章节

**对比我们的文档**:
- ❌ **完全缺失**: 我们没有专门的 Debugging/Troubleshooting 文档

---

### 6. **Script involving [topic]**

```
Script involving advances
- research_advance effect
- advance_type: data scope link
- can_research_advance trigger
- has_advance trigger
```

**启发**:
- **相关API集中列举**: 方便速查
- **Effect/Trigger分类**: 按类型组织

**对比我们的文档**:
- ✅ `spec_engine_basics.md` §5.6 有类似章节
- ⚠️ 但不够系统,可扩展

---

## 🎯 对我们文档的具体建议

### Priority 1: 立即可做

#### 1. 为 `spec_gacha_system.md` 添加 Technical Details

```markdown
## Technical Details

### File Locations
- **Gacha Entry Point**: `in_game/common/character_interactions/gacha_wish_interaction.txt`
- **Probability Logic**: `in_game/common/script_values/gacha_values.txt`
- **Core Effects**: `in_game/common/scripted_effects/gacha_logic_effects.txt`
- **Event UI**: `in_game/events/gacha_events.txt`

### Key Data Structures
- **Pity Counter**: Country variable `gacha_current_pity`
- **Character Pool**: Global list `gacha_obtained_characters`
- **Constellation**: Character variable `gacha_constellation_lvl`
```

#### 2. 创建 `spec_debugging.md`

```markdown
# Debugging & Troubleshooting

## Console Commands
- `script_docs` - Generate effect/trigger documentation
- `reload [file]` - Hot-reload modified files
- `clear_saved_scope` - Clean orphaned scopes

## Error Patterns
- "Scope leak": Check all `if/else` branches clear scopes
- "Dynasty pollution": Verify `existing_char` cleanup

## Debug Workflow
1. Enable `-debug_mode` in Steam
2. Check `error.log` for syntax errors
3. Use `debug_log` effect for variable inspection
4. Verify Scope chain with `debug_log_scopes`
```

#### 3. 重组 `spec_gacha_system.md` 结构

**当前结构** (混乱):
```
1. 核心概念
2. 保底机制
3. 多角色支持
4. [规范] 标签
```

**建议结构** (清晰):
```
1. Technical Details (文件位置)
2. Core Concepts (概念)
3. Syntax (配置语法)
   3.1 Probability Values
   3.2 Pity System
   3.3 Multi-Character Pool
4. Best Practices (编码建议)
5. Script API (相关Effect/Trigger)
6. Troubleshooting (常见问题)
```

---

### Priority 2: 中期优化

#### 4. 统一"验证状态"标记

官方使用:
```
✅ "verified for version 1.0"
⏳ "timeless" (永久有效)
```

我们可以采用:
```
✅ **Verified**: 2025-11-25, Game v1.0.0
🔄 **Partial**: Scope behavior verified, Effect examples pending
⚠️ **Unverified**: Theoretical, needs testing
```

#### 5. 添加"相关API"速查表

在每个 spec 文档末尾添加:

```markdown
## Script API Reference

### Effects
| Effect | Scope | Description |
|:---|:---|:---|
| `gacha_execute_roll` | Country | Execute single gacha roll |
| `save_scope_as` | Any | Save current scope |

### Triggers
| Trigger | Scope | Description |
|:---|:---|:---|
| `has_trait` | Character | Check character trait |

### Script Values
| Value | Returns | Description |
|:---|:---|:---|
| `gacha_5star_threshold_value` | 0-100 | Current 5★ probability |
```

---

### Priority 3: 长期完善

#### 6. 创建 `spec_file_structure.md`

模仿官方的 "Mod structure" 指南:

```markdown
# Project File Structure

## Top-Level Organization
```
in_game/
├── common/
│   ├── character_interactions/  # Player-facing actions
│   ├── scripted_effects/        # Reusable logic
│   ├── script_values/           # Probability calculations
│   └── ...
├── events/                      # UI popups
└── localization/                # Text translations
```

## Naming Conventions
- Prefix all files with `gacha_`
- Character-specific: `gacha_xinhai_*.txt`
- System-wide: `gacha_common_*.txt`
```

#### 7. 扩展 `design_engine_pitfalls.md`

添加官方常见问题:
- UTF-8 BOM encoding issues
- File path non-ASCII problems
- Mod load order conflicts

---

## 📋 Action Items

### Immediate (本周)
- [ ] 为 `spec_gacha_system.md` 添加 Technical Details 章节
- [ ] 创建 `spec_debugging.md`
- [ ] 在 `spec/README.md` 中索引 debugging 文档

### Short-term (下周)
- [ ] 重组 `spec_gacha_system.md` 结构
- [ ] 为所有 spec 添加"验证状态"标记
- [ ] 创建 `spec_file_structure.md`

### Long-term (下个月)
- [ ] 为每个 spec 添加 "Script API" 速查表
- [ ] 扩展 pitfalls 文档包含官方常见问题
- [ ] 建立文档版本追踪机制

---

## 🎨 文档模板建议

基于官方模式,我们的 spec 文档应遵循:

```markdown
# [Topic Name]

> **Verified**: 2025-11-25 | Game v1.0.0  
> **Official Ref**: [EU5 Wiki - Topic](link)

## Technical Details
- File locations
- Key data structures
- Dependencies

## Core Concepts
- What it is
- Why it matters

## Syntax
### [Feature A]
### [Feature B]

## Best Practices
- Do's and Don'ts

## Script API
- Effects
- Triggers  
- Values

## Troubleshooting
- Common errors
- Debug workflow

## References
- Related specs
- Official docs
```

---

## 💡 关键启发总结

| 官方特点 | 我们的现状 | 改进方向 |
|:---|:---|:---|
| **File locations先行** | 部分文档缺失 | 统一添加 Technical Details |
| **Best Practices前置** | 藏在design目录 | 提升到spec可见性 |
| **Debugging专章** | 完全缺失 | 创建troubleshooting文档 |
| **API速查表** | 零散分布 | 集中整理到各spec末尾 |
| **验证状态明确** | 部分标记 | 统一verification标准 |

**核心理念**: **先告诉读者"东西在哪"和"怎么debug",再讲原理**
