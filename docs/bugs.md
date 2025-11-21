## 已修复-Bug 1：按钮只剩一个 & 金钱条件无效

### 现象

* 早期版本里，抽卡事件/召唤事件：
  * 不管金币是 0 还是 9999，弹出的事件里 **只有一个选项** （通常是 A），B 不见了；
  * 或者 A 按钮文本看起来有条件，但实际上条件没生效；
* 有时只有在  **debug 模式下修改脚本** ，事件窗口才会突然变正常。

### 根因

最后我们锁定了两个核心点，真正致命的是第一个：

1. **事件文件缺失 `namespace`**
   * `gacha_events.txt` 里一开始是直接写：

     <pre class="overflow-visible!" data-start="432" data-end="475"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>gacha_wish.1 = { ... }
     </span></span></code></div></div></pre>

     而没有：

     <pre class="overflow-visible!" data-start="493" data-end="564"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>namespace = gacha_wish
     gacha_wish.1 = { ... }
     </span></span></code></div></div></pre>
   * 对 Jomini 的事件系统来说：

     * 没 namespace → 事件 ID 容易跟别的文件冲突 / 没被完整登记；
     * 在调试模式热重载时，索引方式又略有差异，于是出现了你看到的那种：
       > “正常启动 -> 行为怪；
       >
       > 改了文件 -> 热加载 -> 瞬间正常”。
       >
2. **早期我们对 `option.trigger` 语义一度有认知偏差**
   * 一开始我误以为 EU5 必须用 `is_shown`/`is_valid` 之类字段；
   * 你拿官方 readme 和 random_event 代码对回来，证实了：
     * **在 EU5 里 `trigger = { ... }` 正是选项是否出现的条件** ；
     * 文档写得很清楚：“Only visible if the triggers here are fulfilled”。
   * 所以后来我们统一认识：
     * `type = country_event` 顶层用 `trigger` 控制能否触发；
     * `option` 里用 `trigger` 控制“这个选项是否显示”。

### 修复

* 在事件文件顶部加上 namespace，例如：
  <pre class="overflow-visible!" data-start="1135" data-end="1237"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>namespace = gacha_events

  gacha_events.1 = {
      type = country_event
      ...
  }
  </span></span></code></div></div></pre>
* 确保所有调用都用完整 ID：
  <pre class="overflow-visible!" data-start="1258" data-end="1316"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>trigger_event_non_silently = gacha_events.1
  </span></span></code></div></div></pre>
* 继续保留 `option` 里的 `trigger = { gold >= 100 }`，让选项按金币条件出现或隐藏。

修复之后：

* 事件选项 A/B 会按金币条件正确显示；
* 不再出现“只有 debug 修改后才正常”的鬼畜状态。

### 经验教训

* **事件脚本第一行先写 namespace** ，不写迟早翻车；
* 不要怀疑 `trigger` 本身，在 EU5 里它就是干这个用的；
* 出现“奇怪只有一半行为”的时候，优先看：
  * namespace
  * ID 是否重复
  * `error.log` 里有没有 parse error。

---

## 已修复-Bug 2：模板化传参翻车（“类型陷阱”）

这个是你重点提到的「传 culture、event_id 进去结果事件整块失效」。

### 现象

在你把角色创建逻辑抽成模板之后：

* 抽卡弹窗 **又变成只有一个选项** （或者只剩一个能正常渲染的 option）；
* 点击抽卡：
  * 金币会扣；
  * 但不创角、不弹心海事件、不加任何 trait；
* 有时只有在 debug 模式修改脚本后才暂时恢复正常。

### 根因

这块其实是多个小坑叠加，但你总结的那句“ **参数传递的类型陷阱** ”说得非常到位——Jomini 的宏系统对“参数里装什么东西”非常挑。

核心有三点：

1. **试图把复杂标识符当模板参数传递**
   比如你早期版本里类似这样：

   <pre class="overflow-visible!" data-start="1962" data-end="2263"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>gacha_create_common_effect = {
       create_character = {
           first_name = $first_name_key$
           last_name  = $last_name_key$
           culture    = $culture$
           religion   = $religion$
           ...
       }
       trigger_event_non_silently = $event_id$
   }
   </span></span></code></div></div></pre>

   然后调用时：

   <pre class="overflow-visible!" data-start="2279" data-end="2573"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>gacha_create_common_effect = {
       who = xinhai
       first_name_key = gacha_first_name_xinhai
       last_name_key  = gacha_last_name_xinhai
       culture        = culture:tougokud
       religion       = religion:shintō
       event_id       = gacha_xinhai_events.1
   }
   </span></span></code></div></div></pre>

   问题就来了：

   * `$first_name_key$` 这种纯 ID 字符串 → 它能替换，很安全；
   * `culture:tougokud` / `gacha_xinhai_events.1` 这种带冒号/点号的“复合记号”，在宏展开时：
     * 要么会被拆坏；
     * 要么整行变成解析器认不出的东西，导致 `create_character` 或 `trigger_event` 那一整行被视为“语法错误”。

   **结果就是** ：隐藏效果在解析期被整块丢掉，运行时只剩下：

   * 事件本体 + 扣钱那个 `add_gold`；
   * 模板逻辑完全没执行。
2. **模板参数命名前后不一致**
   你中途有一版是这样：

   * 模板里用 `$first_name_key$` / `$last_name_key$`；
   * 另一个 wrapper 还在用 `first_name` / `last_name` 参数名；
   * 预处理找不到 `$first_name_key$` 的替换 → 再次让那行代码异常。

   这类“宏名写错”不会导致引擎崩溃，但会让那个 effect 逻辑根本没跑过。
3. （次要）debug 文本写成字符串常量
   像：

   <pre class="overflow-visible!" data-start="3148" data-end="3207"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>custom_tooltip = "DEBUG: 检测到已拥有，尝试升级命座..."
   </span></span></code></div></div></pre>

   在很多 P 社脚本里，`custom_tooltip` 期待的是一个本地化 key。

   视具体游戏实现，这可能：

   * 要么能容忍（当成奇怪的 key）；
   * 要么直接当语法错误。

   这在我们调试过程中也怀疑过是潜在雷点，不过你后面已经通过删掉这些 debug 行 + 简化模板确认：真正的大雷还是 **复杂对象的模板传参** 。

### 修复

你后来做的是非常正确的一步：

1. **收紧模板，只处理简单符号拼接**

   <pre class="overflow-visible!" data-start="3440" data-end="3684"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>gacha_create_common_effect = {
       create_character = {
           first_name = gacha_first_name_$who$
           last_name  = gacha_last_name_$who$
           ...
       }
       trigger_event_non_silently = $event_id$
   }
   </span></span></code></div></div></pre>

   也就是说：

   * 模板只接收简单参数 `$who$` 和 `$event_id$`；
   * 名字这种用“命名约定”拼出来；
   * 不再尝试传 `culture:tougokud` / `religion:shintō` 这类复杂 token 做宏替换。
2. **用 wrapper 传事件 ID，而不是把整个 ID 当宏跑来跑去**

   <pre class="overflow-visible!" data-start="3869" data-end="4051"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-txt"><span><span>gacha_create_xinhai_effect = {
       gacha_create_common_effect = {
           who = xinhai
           event_id = gacha_xinhai_events.1
           ...
       }
   }
   </span></span></code></div></div></pre>

   wrapper 自己写 `event_id = gacha_xinhai_events.1`，模板那边只是把 `$event_id$` 换成字面量，这样就安全多了。

### 经验教训

* P 语言的宏系统 **适合的是：简单 ID/数字的文本拼接** ；
* 不要指望它安全地传递：
  * `culture:xxx`
  * `religion:yyy`
  * `event_namespace.id`

    这种带冒号 / 点号的结构；
* 模板就干两件事：
  * 用 `$who$` 拼接 ID 名；
  * 调简单的效果；
* 真要传复杂内容，就在 wrapper 里写死，不要把它变成宏参数。



## 未修复-Bug 3：概率系统永远 100% 出无锋剑

### 现象

你实现了一整套看起来很正确的 gacha 数学：

* `gacha_5star_threshold_value` 里有软保底 / 硬保底；
* 每抽一发：
  * 生成 `gacha_rng_roll ∈ [1,1000]`；
  * 计算当前阈值；
  * 如果命中 5★ → 进入 `gacha_handle_5star_outcome`；
  * 否则 → 进入 `gacha_events.2`（无锋剑）。

**但实际游戏效果：**

* 每次都是 `gacha_events.2`；
* 心海和 5★ 完全不出现；
* 你用调试文本看了一眼感觉 RNG 在变，但逻辑就是不进 5★ 分支。
