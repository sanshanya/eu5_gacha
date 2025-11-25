# Documentation Review & Optimization Report

**Date**: 2025-11-25  
**Scope**: Complete review of 23 markdown files across spec/, design/, and archive/

---

## 📊 Current Status

### File Distribution
- **Spec** (6 files): 规范性文档
- **Design** (10 files): 设计与分析文档
- **Archive** (7 files): 历史归档文档

---

## ⚠️ 发现的问题

### 1. 冗余文件 (Critical)

#### Problem: `scope_alignment_report.md` 在 spec/ 目录中
- **位置**: `docs/spec/scope_alignment_report.md`
- **问题**: 这是一次性对齐报告,应该归档
- **影响**: 混淆 spec 目录的规范性定位
- **已有归档**: `docs/archive/archive_scope_alignment_2025.md` 已存在

**Action Required**: 删除 `docs/spec/scope_alignment_report.md`

---

### 2. README 索引不完整 (Medium)

#### spec/README.md
**缺失文档**:
- `spec_engine_basics.md` - ✅ 已存在但未索引
- `spec_scope_management.md` - ✅ 已索引
- `spec_workflow_add_character.md` - ✅ 已索引

**错误索引**:
- `spec_traits_and_modifiers.md` - ❌ 不存在(应该是 `design/design_traits_and_modifiers.md`)

#### design/README.md
**缺失文档**:
- `design_engine_pitfalls.md` - ✅ 已存在但未索引
- `design_project_guidelines.md` - ✅ 已存在但未索引
- `analysis_reference_snow.md` - ✅ 已存在但未索引
- `analysis_tech_wrappers.md` - ✅ 已存在但未索引

#### archive/README.md
**缺失文档**:
- `archive_scope_alignment_2025.md` - ✅ 已存在但未索引
- `archive_scope_errors_lessons.md` - ✅ 已存在但未索引

---

### 3. 文档定位模糊 (Medium)

#### `design_engine_pitfalls.md`
- **当前位置**: `design/`
- **问题**: 虽然名为 "design",但内容主要是已验证的引擎陷阱(规范性知识)
- **建议**: 考虑重命名为 `design_lessons_from_pitfalls.md` 以明确其设计反思定位,或移至 spec/

#### `design_project_guidelines.md`
- **当前位置**: `design/`
- **问题**: 这是"项目圣经",实际上是规范性文档
- **建议**: 考虑移至 spec/ 或在 spec/README 中明确交叉引用

---

### 4. 缺少顶层导航 (Low)

**问题**: `docs/` 根目录下没有总README,新人不知道从哪里开始阅读

**建议**: 创建 `docs/README.md` 作为总入口,引导读者:
1. 新手 → `spec/00_project_overview.md`
2. 开发者 → `spec/README.md`
3. 设计讨论 → `design/README.md`
4. 考古 → `archive/README.md`

---

## ✅ 优化建议

### Priority 1: 立即修复

1. **删除冗余文件**
   ```bash
   rm docs/spec/scope_alignment_report.md
   ```

2. **修复 spec/README.md 索引**
   - 添加 `spec_engine_basics.md`
   - 移除 `spec_traits_and_modifiers.md` (不存在)

### Priority 2: 短期优化

3. **完善 design/README.md 索引**
   - 添加所有缺失的 design 和 analysis 文档
   - 按类别分组(Design Systems, Analysis Reports, Guidelines)

4. **完善 archive/README.md 索引**
   - 添加所有 Scope 相关归档文档
   - 添加归档时间戳

5. **创建 docs/README.md 总导航**

### Priority 3: 长期优化

6. **重新评估文档定位**
   - `design_engine_pitfalls.md`: 确定是保留在 design/ 还是移至 spec/
   - `design_project_guidelines.md`: 在 spec/ 中增加引用

---

## 📝 推荐的文档结构

### spec/ (规范性,必须遵守)
```
spec/
├── README.md                         ✅ 需更新索引
├── 00_project_overview.md            ✅ 正确
├── spec_engine_basics.md             ✅ 需加入索引
├── spec_gacha_system.md              ✅ 正确
├── spec_scope_management.md          ✅ 正确
└── spec_workflow_add_character.md    ✅ 正确
```

### design/ (设计与分析,参考性)
```
design/
├── README.md                         ⚠️ 需扩充索引
├── design_engine_pitfalls.md         ⚠️ 需评估定位
├── design_project_guidelines.md      ⚠️ 需spec引用
├── design_*.md (系统设计)           ✅ 正确
└── analysis_*.md (可行性分析)       ✅ 正确
```

### archive/ (历史归档,仅供参考)
```
archive/
├── README.md                         ⚠️ 需添加新归档
├── archive_scope_*.md               ✅ 正确但未索引
├── archive_gacha_v2_draft.md        ✅ 正确
└── archive_*.md                     ✅ 正确
```

---

## 🎯 关键指标

| 指标 | 当前 | 优化后 |
|:---|:---:|:---:|
| **冗余文件** | 1 | 0 |
| **未索引文件** | 8 | 0 |
| **错误索引** | 1 | 0 |
| **文档可发现性** | 60% | 100% |

---

## 📋 Action Items Checklist

- [ ] 删除 `spec/scope_alignment_report.md`
- [ ] 更新 `spec/README.md` 索引
- [ ] 更新 `design/README.md` 索引  
- [ ] 更新 `archive/README.md` 索引
- [ ] 创建 `docs/README.md` 总导航
- [ ] 评估 `design_engine_pitfalls.md` 定位
- [ ] 在 spec 中引用 `design_project_guidelines.md`
