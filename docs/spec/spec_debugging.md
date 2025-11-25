# Debugging & Troubleshooting

> **Purpose**: 调试工具、常见问题与解决方案  
> **Target Audience**: 所有开发者

---

## 1. 启用调试模式

### Steam 启动参数
在 Steam 中右键 Europa Universalis V → 属性 → 启动选项:
```
-debug_mode
```

**效果**:
- ✅ 激活游戏内控制台 (~键)
- ✅ 热重载修改的文件(无需重启游戏)
- ✅ 显示 error.log 行数统计按钮
- ✅ 启用游戏内dev工具

---

## 2. Console Commands (控制台命令)

### 文档生成
```
script_docs
```
- 生成所有 Effects, Triggers, Scopes 文档
- 输出位置: `Documents\Paradox Interactive\Europa Universalis V\docs`
- **用途**: 查询官方API签名

```
dump_data_types
```
- 导出所有数据类型定义
- 输出位置: `Documents\Paradox Interactive\Europa Universalis V\logs\data_types`
- **用途**: GUI脚本开发参考

### 调试工具
```
reload <filename>
```
- 热重载指定文件
- **示例**: `reload gacha_logic_effects.txt`
- **注意**: 某些文件(如 `on_action.txt`)不支持热重载

```
debug_log "message"
```
- 在代码中使用 `debug_log` effect 输出调试信息
- **示例**: `debug_log = "Current pity: [This.Var('gacha_current_pity')]"`

```
debug_log_scopes = yes
```
- 在代码中输出完整 scope 链信息
- **用途**: 排查 Scope 切换问题

---

## 3. 查看日志

### error.log
**位置**: `Documents\Paradox Interactive\Europa Universalis V\logs\error.log`

**查看方式**:
1. 游戏内: 点击右上角 🦌图标(启用`-debug_mode`后)
2. 手动打开: 用文本编辑器直接打开

**配置默认编辑器** (可选):
编辑 `Documents\Paradox Interactive\Europa Universalis V\pdx_settings.json`:
```json
{
  "System": {
    "editor": "C:\\Program Files\\Visual Studio Code\\Code.exe",
    "editor_postfix": ":$:1"
  }
}
```

### 常见错误模式

#### Syntax Error (语法错误)
```
[script_parser.cpp]: Unexpected token '=' at line 42
```
**原因**: 括号不匹配、缺少 `=` 或拼写错误  
**解决**: 检查第42行及其前后的语法

#### Scope Error (作用域错误)
```
[effect.cpp]: Effect 'add_gold' cannot be used in Character scope
```
**原因**: Effect 在错误的 Scope 中调用  
**解决**: 检查 `spec_engine_basics.md` §5.3 确认正确的 Scope

#### Undefined Reference
```
[scripted_effect.cpp]: Scripted effect 'foo_effect' not found
```
**原因**: 引用了不存在的 scripted effect  
**解决**: 检查文件名、拼写,确保文件在 `common/scripted_effects/` 中

---

## 4. Common Problems & Debugging Patterns

### Project-Specific Patterns

#### Pattern 1: Scope Leak 诊断

**症状**: 角色属性错误继承(如 Dynasty Bug)

**诊断步骤**:
1. 在可疑代码前后添加:
   ```paradox
   debug_log = "Before scope creation"
   save_scope_as = my_temp_scope
   # ... 使用 scope ...
   clear_saved_scope = my_temp_scope
   debug_log = "After scope cleanup"
   ```

2. 检查 `error.log` 是否所有log都出现

**参考**: `archive/archive_scope_errors_lessons.md`

#### Pattern 2: 抽卡概率验证

**验证方法**: 在 `gacha_logic_effects.txt` 中添加 debug_log 追踪pity和阈值变化

### General Problems

### Problem 1: 修改代码后无反应

**症状**: 
- 修改了 `.txt` 文件保存后,游戏内仍是旧行为
- 没有报错

**可能原因**:
1. **文件编码错误**: 文件不是 UTF-8 with BOM
2. **文件未保存**: 编辑器自动保存未触发
3. **缓存问题**: 某些文件需要完全重启

**解决方案**:
```
# 1. 检查编码 (VSCode)
File → Save with Encoding → UTF-8 with BOM

# 2. 控制台热重载
reload <filename>

# 3. 完全重启游戏
```

---

### Problem 2: Scope 错误但 error.log 无警告

**症状**:
- 代码静默失效
- `error.log` 干净

**原因**: 某些 Scope 错误只会导致 Effect 跳过,不报错

**诊断**:
使用 `debug_log_scopes` 追踪 Scope 链:
```paradox
debug_log_scopes = yes
scope:char = {
    debug_log = "Inside char scope"
    root = {
        debug_log = "Back to root"
    }
}
```

---

### Problem 3: 本地化不显示

**症状**:
- 事件显示 `gacha_events.1.t` 而非中文标题

**检查清单**:
- [ ] 文件名是否以 `_l_english.yml` 或 `_l_simp_chinese.yml` 结尾?
  - ⚠️ 注意是**小写L**,不是数字1或大写i!
- [ ] 文件编码是否为 **UTF-8 with BOM**?
- [ ] Key 是否拼写正确?
- [ ] 是否在正确的语言文件中? (简中 → `_l_simp_chinese.yml`)

---

### Problem 4: Character Interaction 不出现

**症状**:
- `gacha_wish_interaction.txt` 定义了,但游戏内无法使用

**检查清单**:
```paradox
gacha_wish_interaction = {
    potential = {
        # ← 这里的条件是否太严格?
        always = yes  # 临时改为 always 测试
    }
    
    is_shown = {
        # ← 这里控制是否在UI显示
        always = yes
    }
    
    allow = {
        # ← 这里控制是否可点击
        gold >= 100
    }
}
```

**诊断**: 逐步放宽条件,确定哪个trigger导致问题

---

## 5. Best Practices & Tools

**调试规范**: 详见 [design_project_guidelines.md](../design/design_project_guidelines.md) §调试原则

### 工具推荐

- **VSCode**: Paradox Highlight + CwTools
- **IntelliJ**: Paradox Language Support
- **语法高亮**: 使用Perl语法(最接近)

### 参考资源

| 资源 | 说明 |
|:---|:---|
| `error.log` | 第一手错误信息 |
| `script_docs` | 官方API文档 |
| [spec_engine_basics.md](spec_engine_basics.md) | 引擎底层机制 |
| [archive_scope_errors_lessons.md](../archive/archive_scope_errors_lessons.md) | 历史错误案例 |
| [design_engine_pitfalls.md](../design/design_engine_pitfalls.md) | 常见陷阱 |

### 快速参考卡

```
# 控制台快捷键
~          打开控制台
Ctrl+F     搜索 error.log
F5         重载当前界面

# 常用命令
script_docs
reload <file>
debug_log "message"

# 调试流程
1. 启用 -debug_mode
2. 修改代码 + 保存
3. reload <file>
4. 游戏内触发
5. 检查 error.log
6. 修复 → 重复2-5
```
