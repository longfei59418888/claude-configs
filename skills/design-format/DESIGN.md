# Ayoa — Design System (DESIGN.md)

> 来源：xxx （分析页面：首页、Features、Education、Workplace、Ayoa and AI、Pricing，以及主题样式表 `Ayoa Redux/style.css`）
> Ayoa 是一款融合思维导图、任务管理与白板协作的效率工具，品牌语言明亮、圆润、色彩饱和。

---

## 1. Visual theme and atmosphere（视觉主题与氛围）

Ayoa 的界面传递的是 **"playful productivity"（充满活力的效率感）**。它刻意远离企业级工具那种冷峻、灰暗、密集的观感，转而用高饱和的渐变色块、完全圆角的胶囊按钮、大量留白和手写体点缀，营造一种**友好、鼓励创造、低门槛**的氛围。

设计哲学的核心：

- **色彩即情绪**：品牌不依赖单一主色，而是用一整套明亮渐变（青蓝、品红、紫、橙黄、绿）来区分功能模块与情绪——蓝色代表思维导图、紫色代表工作流、暖色代表行动号召。
- **圆润即亲和**：几乎所有交互元素（按钮、卡片、标签）都使用大圆角或完全胶囊化（100px），传递柔和、无压力的感觉。这与其"面向神经多样性人群、教育、创意"的定位一致。
- **手写体点缀人性化**：标题与强调处使用 `Caveat` 手写体，呼应"思维导图 / 头脑风暴"的手绘感，弱化数字工具的机械感。
- **白底 + 彩色块的呼吸感**：页面主体为纯白，靠大段留白和分区彩色插画切分内容，信息密度低、扫读轻松。

一句话：**它看起来像一个鼓励你自由思考的创意工具，而不是一个催你交付的管理后台。**

---

## 2. Color palette and roles（色彩体系与语义）

Ayoa 的调色板由多组亮色 + 渐变构成，而非单一 accent。以下为核心角色：

| Role（角色） | Token | Value | 说明 |
|---|---|---|---|
| 页面背景 | `--bg-primary` | `#FFFFFF` | 主体纯白 |
| 浅色分区背景 | `--bg-wash` | `#F7FBFC` / `#E7F6FC` | 青调浅色分区 |
| 主文本 | `--text-primary` | `#0D1F22` / `#000000` | 深墨绿黑 |
| 次要文本 | `--text-muted` | `#AEAEAE` | 说明、占位 |
| 深色区背景 | `--bg-dark` | `#002539` / `#00293D` | 深青色 footer / 深色 section |
| 品牌青（思维导图） | `--brand-cyan` | `#00C1FF` | 主功能色 |
| 品牌蓝 | `--brand-blue` | `#0092FF` / `#006FC4` | 链接、蓝色 CTA |
| 品牌紫（工作流） | `--brand-purple` | `#8839F6` / `#6A23CE` | 工作流 / Premium |
| 品牌品红（强调 CTA） | `--brand-pink` | `#FC1476` / `#CB004E` | 高优先行动、注册 |
| 品牌橙黄（辅助） | `--brand-amber` | `#FDB32B` / `#FF7F16` | 次级强调、亮点 |
| 品牌绿（成功） | `--brand-green` | `#2BBC64` / `#367B02` | 成功 / 免费方案 |
| 边框 / 分隔 | `--border-default` | `#ECECF4` / `#AEAEAE` | 浅灰分隔线 |

### 核心渐变（Signature Gradients）

Ayoa 的视觉签名在于渐变，而非纯色。请优先使用渐变作为大色块与 CTA：

| 渐变名 | 值 |
|---|---|
| Cyan（青蓝，思维导图） | `linear-gradient(65deg, #00C1FE 0%, #0092FF 100%)` |
| Sky（浅蓝） | `linear-gradient(85deg, #0093FF 0%, #00CDFF 100%)` |
| Purple（工作流 / Premium） | `linear-gradient(85deg, #6144F6 0%, #B344F6 100%)` |
| Lavender-Blue | `linear-gradient(70deg, #59C3FF 0%, #B08AFF 100%)` |
| Pink（强调 CTA） | `linear-gradient(145deg, #FC1476 0%, #DA0BC7 100%)` |
| Amber（暖色亮点） | `linear-gradient(75deg, #FAB23D 0%, #FDCA55 100%)` |
| Green（成功 / 免费） | `linear-gradient(90deg, #2BBC64 0%, #92E43A 100%)` |
| Ice（浅青分区背景） | `linear-gradient(115deg, #A5DADD 0%, #D3F2FE 0%, #E7F6FC 100%)` |

---

## 3. Typography rules（字体规则）

**字体家族：**
- UI / 正文：`Open Sans`（细分为 `open_sanslight` 正文、`open_sansregular`、`open_sansbold`、`open_sansextrabold`）
- 手写强调 / 装饰标题：`Caveat`（用于点缀性大标题、思维导图气质的引导语）
- 回退：`Arial, Helvetica, sans-serif`

正文默认使用 **light（细）** 字重，标题使用 **bold / extrabold**，形成轻正文 + 重标题的对比节奏。

| Level | Size | Weight | Line-height | 用途 |
|---|---|---|---|---|
| Display (H1) | 55px | extrabold (800) | 65px | 首页主标题 |
| H2 | 42px | bold (700) | ~1.2 | 分区大标题 |
| H3 | 30–32px | bold | ~1.3 | 子标题 |
| Feature title | 24–28px | bold | 1.3 | 模块标题 |
| Sub-heading | 20–22px | 600 | 1.4 | 小节标题 |
| Body large | 18px | light/400 | 1.6 | 引导正文 |
| Body | 15–16px | light/400 | 1.6 | 正文 |
| Small / label | 12–14px | regular | 1.5 | 说明、标签 |
| Handwritten accent | 24–40px | Caveat | — | 装饰性点缀语 |

规则：
- 正文使用 `open_sanslight`，保持轻盈感；不要让正文过重。
- 标题字距不刻意收紧（与 Linear 类工具相反），保持自然、友好。
- 手写体 `Caveat` 只用于装饰性短句，不用于长段落或功能文本。

---

## 4. Component styles（组件样式）

### Button — Primary（品红 / 注册）
- Background: `#CB004E`（或渐变 `linear-gradient(145deg,#FC1476,#DA0BC7)`）
- Color: `#FFFFFF`
- Padding: `12px 35px`
- Border-radius: `100px`（完全胶囊）
- Font: `open_sansbold`, 16–18px
- Hover: 亮度提升 / 轻微上浮 + 阴影加深
- 用途：注册、Get Started、最高优先行动

### Button — Purple（工作流 / Premium）
- Background: `#6A23CE`（或渐变 `linear-gradient(85deg,#6144F6,#B344F6)`）
- Color: `#FFFFFF`
- 其余同 Primary（胶囊、`12px 35px`）

### Button — Outline（次级）
- Background: `transparent`
- Border: `2px solid #07BFFD`
- Color: `#07BFFD`
- Border-radius: `100px`
- Hover: 填充为对应实色，文字转白

### Button — Read More（弱化）
- Background: `transparent`
- Border + color: `#9AB0C0`
- Border-radius: `5px`
- Padding: `5px 25px`
- 用途：低优先级的"了解更多"

### Card（内容卡片）
- Background: `#FFFFFF`
- Border-radius: `15px`–`25px`（大圆角）
- Shadow: `0 10px 30px rgba(0,0,0,0.08)`（柔和上浮，靠阴影而非边框建立层级）
- Padding: `24px`–`32px`

### Nav item（导航项）
- 文本导航：Pricing / Education / Workplace / Assistive Tech / Features / Resources
- 默认深色文字，hover 变品牌色
- 右侧：`Login`（文本）+ `Get Started`（品红胶囊 CTA）

### Badge / Pill（标签）
- Border-radius: `100px`
- 高对比背景（品红 / 绿 / 蓝）+ 白字
- 小尺寸：`font-size: 12px`

---

## 5. Layout principles（布局原则）

- **基础单位**：约 5px 网格（常见 `5 / 10 / 15 / 20 / 25 / 35` 的倍数节奏）
- **间距节奏**：`5, 10, 15, 20, 25, 35, 50` px
- **内容最大宽度**：~`1200px` 居中容器
- **分区间距**：段落分区之间大量留白（50px+），靠彩色 / 浅色分区块切换而非线条
- **网格**：功能区常用 2 列 / 3 列图文交错（zig-zag）布局
- **圆角尺度**：
    - `5px`（弱化按钮 / 小元素）
    - `8px`–`12px`（输入框、小卡片）
    - `15px`–`25px`（内容卡片、图片容器）
    - `40px`–`50px`（大图片 / 大插画块）
    - `100px`（按钮、标签胶囊）

---

## 6. Depth and elevation（深度与层级）

层级主要靠**柔和阴影**而非边框建立，阴影颜色偏中性冷灰。

| Level | 用途 | Shadow |
|---|---|---|
| Level 0 | 页面背景 | none |
| Level 1 | 轻微分隔 / hover | `0 0 10px rgba(0,0,0,0.06)` |
| Level 2 | 内容卡片 | `0 10px 30px rgba(0,0,0,0.08)` |
| Level 3 | 突出卡片 / 悬浮 | `0 10px 30px rgba(0,0,0,0.13)` |
| Level 4 | 大图 / 弹层 | `0 20px 50px rgba(0,0,0,0.32)` |
| 特殊 | 深色区反光内阴影 | `inset 0 1px 1px rgba(255,255,255,0.07)` |

---

## 7. Do's and don'ts（该做与不该做）

**Do：**
- 用完全圆角（100px）做按钮和标签，保持品牌的圆润亲和感
- 用明亮渐变做主色块与 CTA，而不是单一扁平色
- 正文用 Open Sans light，标题用 bold/extrabold，形成轻重对比
- 用柔和阴影建立卡片层级，用留白切分内容
- 保持白底 + 彩色分区块的呼吸感

**Don't：**
- 不要用冷峻的暗色 UI / 高信息密度网格（那是它刻意回避的风格）
- 不要在矩形内容区滥用 100px 胶囊圆角（胶囊只给按钮 / 标签）
- 不要让正文使用重字重，破坏轻盈感
- 不要用生硬的 1px 灰线做主要分隔，优先用留白 + 阴影
- 手写体 Caveat 不要用于长文本或关键功能标签
- 不要混用过多渐变在同一视觉区域，一个区块聚焦一种情绪色

---

## 8. Responsive behavior（响应式）

主要断点（来自样式表 media queries）：

| Breakpoint | Width | 行为 |
|---|---|---|
| Mobile | ≤ 600px | 单列堆叠，导航收起为汉堡菜单，CTA 占满宽度 |
| Tablet | ≤ 800px | 图文交错转为单列，间距压缩 |
| Small desktop | ≤ 960–1000px | 容器收窄，多列降为 2 列 |
| Desktop | ≥ 1200px | 完整多列 zig-zag 布局，容器 ~1200px 居中 |

- 常用断点集中在 `600 / 800 / 900 / 960 / 1200`px
- 触摸目标保持胶囊按钮的大 padding，天然满足 44px 最小点击区
- 移动端正文不低于 14px

---

## 9. Agent prompt guide（Agent 快查指南）

**快速调色板：** bg=`#FFFFFF`，text=`#0D1F22`，青=`#00C1FF`，蓝=`#0092FF`，紫=`#8839F6`，品红=`#FC1476`，橙黄=`#FDB32B`，绿=`#2BBC64`
**签名渐变：** 青蓝 `#00C1FE→#0092FF`，紫 `#6144F6→#B344F6`，品红 `#FC1476→#DA0BC7`
**字体：** Open Sans（正文 light / 标题 bold），Caveat（手写点缀）
**形状：** 按钮/标签 100px 胶囊；卡片 15–25px 圆角；柔和阴影建立层级

### Ready-to-use prompts：

- **"做一个落地页 Hero"** → 白底，55px extrabold 主标题 + Caveat 手写点缀语，一句 18px light 副标题，品红胶囊主 CTA（`Get Started`）+ 蓝色描边次级按钮，右侧配彩色渐变插画。
- **"做一个定价卡"** → 白色卡片，25px 圆角，柔和上浮阴影；免费方案用绿色，付费方案用紫色渐变 CTA；标题 bold，价格数字大而醒目，特性列表 15px light。
- **"做一个功能介绍区"** → 图文交错（zig-zag）2 列，每区一种情绪渐变色块背景（青 / 紫 / 橙），24–28px bold 标题 + light 正文 + `Read More` 弱化按钮。
- **"做一个导航栏"** → 白底，左 logo，中部深色文字菜单（Features / Pricing / Education…），右侧 `Login` 文本 + 品红胶囊 `Get Started`；hover 文字变品牌色。
- **"做一个 CTA 区块"** → 深青色背景块（`#002539`），白色 bold 标题，品红或渐变胶囊按钮居中，充足上下留白。
