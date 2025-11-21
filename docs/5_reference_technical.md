# Technical Reference

## 1. Localization: Dynamic Variables (动态变量显示)

> ✅ **Verified for Jomini Engine**

要在本地化文本中显示脚本变量：

**Syntax**:
```
[Scope.Var('variable_name').GetValue]
```

**Example**:
```yaml
desc: "当前命座等级：[This.Var('gacha_constellation_lvl').GetValue]"
```

**Tips**:
*   确保 Scope 正确（通常是 `This` 或 `Root`）。
*   如果不确定 Scope，可以先 `set_variable` 到 Root 上再读取。

---

## 2. Troubleshooting & Lessons Learned (故障排查)

### A. 事件选项消失 / 条件失效
*   **原因**: 缺少 `namespace` 或 ID 冲突。
*   **解决**: 文件顶部必须声明 `namespace = gacha_events`。

### B. 模板参数失效 (The "Type Trap")
*   **原因**: 试图将复杂对象（如 `culture:xxx`）作为宏参数传递。
*   **解决**: 模板只接受简单字符串（如 `$who$`），复杂数据在 Wrapper 中写死。

### C. 概率永远为 0 或 100%
*   **原因**: 使用了静态的 `set_variable` 而非动态计算。
*   **解决**: 使用 `random_list` 配合 `value:script_value` 权重，确保每次调用时重新计算概率。
