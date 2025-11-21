# Gacha System Design (抽卡系统设计)

## Part 1: Probability Logic (概率逻辑)

我们采用 **“伪随机数生成 (PRNG) + 动态阈值判定”** 的逻辑，复刻《原神》的机制。

### 1. 核心变量
*   **`gacha_pity_count`**：当前垫了多少抽（0~89）。
*   **`gacha_is_guaranteed`**：大保底标识（yes = 下次必出 UP，no = 50% 歪）。
*   **`gacha_5star_threshold_value`**：动态计算的当前出货率（千分比）。

### 2. 概率模型
*   **基础概率**：0.6% (6/1000)
*   **软保底 (Soft Pity)**：从第 74 抽开始，每抽增加 6% 概率。
*   **硬保底 (Hard Pity)**：第 90 抽概率为 100%。

### 3. 核心流程
1.  **Roll**: 生成 1-1000 的随机数。
2.  **Compare**: 对比 `gacha_5star_threshold_value`。
3.  **Outcome**:
    *   **Success**: 进入 50/50 或大保底逻辑。
    *   **Failure**: Pity + 1，发放 3星/4星 奖励。

---

## Part 2: Pool Architecture (奖池架构)

为了解耦“概率逻辑”与“奖池内容”，我们设计了分层架构。

### 1. 架构层级
1.  **Logic Layer**: 决定“中不中” (Win/Loss)。
2.  **Interface Layer**: 调用 `gacha_grant_5star_reward` 等接口。
3.  **Content Layer**: `gacha_pools.txt` 定义具体奖池。

### 2. 奖池定义 (gacha_pools.txt)

```paradox
# 5星 UP 池
gacha_pool_5star_limited = {
    # 单UP 或 双UP (random_list)
    gacha_create_xinhai_effect = yes
}

# 5星 常驻池
gacha_pool_5star_standard = {
    random_list = {
        10 = { gacha_create_keqing_effect = yes }
        10 = { gacha_create_qiqi_effect = yes }
    }
}

# 3星 填充池
gacha_pool_3star_trash = {
    random_list = {
        33 = { add_gold = 10 }
        33 = { add_prestige = 5 }
    }
}
```

### 3. 扩展性
添加新角色只需在 `gacha_pools.txt` 中修改对应的 `random_list`，无需触碰核心概率代码。
