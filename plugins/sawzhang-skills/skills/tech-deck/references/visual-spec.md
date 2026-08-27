# tech-deck 视觉规范

改页前读这一份。它和 `assets/shared.css`、`scripts/measure.js` 是一一对应的 ——
**规范里写的每条硬判据，脚本里都有一行在查**。规范和代码对不上时以代码为准，并且回来改这份文档。

---

## 0. 这套版式的取舍

一页要经得起「把这张表放大给我看第三行」。为此**牺牲远距离可读性，换单页信息密度和可追证**
—— 这是 `review` profile。要拿去大场地讲，**必须换 `talk` profile 重新拆页，不要只改字号**。

两套 profile 靠 `<body data-profile="review|talk">` 切换，`deck.json` 里的 `profile` 字段只是备忘，
真正生效的是 HTML 上那个属性；`measure.js` 也从 DOM 读它来决定用哪套阈值。

---

## 1. 字号刻度

组件里**不写死 px**，全部走 `--fs-*` 变量，profile 只改变量。新增组件请照此办理。

| 变量 | review | talk | 用途 |
|---|---|---|---|
| `--fs-h1` | 64 | 76 | 封面主标题 |
| `--fs-h2` | 34 | 46 | 页面标题 |
| `--fs-h3` | 20 | 28 | 层名 / 阶段名 / 指标值 |
| `--fs-lead` | 16 | 26 | 导语、callout |
| `--fs-body` | 14 | 21 | 正文 |
| `--fs-small` | 12.5 | 18 | 表格、要点、图注 |
| `--fs-micro` | 11 | 17 | 注脚、pill |
| `--fs-mono` | 11 | 19 | 代码、终端 |
| `--fs-cap` | 11 | 16 | 图标题、表头 |
| `--fs-footer` | 11 | 13 | 页脚 |

**硬下限：review 9.3px / talk 16px**（`measure.js` 判 FAIL）。`.tagline` 固定 13px + `letter-spacing:.28em`
（talk 15px），是页与页之间的对齐基准，别改。

装不下时的正确顺序：**加宽栏 → 砍内容 → 拆成两页**。缩字号是最后手段，且不许跌破下限。

---

## 2. 色板与绑定规则

```
--bg #FFFFFF   --bg-alt #F4F6FA   --bg-panel #FAFBFD   --line rgba(21,25,43,.10)
--ink #15192B  --ink-2 .74  --ink-3 .50  --ink-4 .32
--accent #E8730A  ← 唯一的通用强调色
--green #16A34A 正面 · --red #DC3548 反面/风险 · --yellow #D9A005 待定
--s1 #2563EB  --s2 #0891B2  --s3 #16A34A  --s4 #E8730A  --s5 #7E55D6  --s6 #94A3B8
```

- 正文里想强调，只有两种手段：**橙色 `.hl`** 和**加粗**。别引入第四种颜色。
- **系列色 `s1..s6` 只服务「同一张图里的分类维度」**（层、阶段、泳道、数据系列）。
  一旦在某张图里把 `s3` 绑给某个含义，全 deck 的衍生图必须沿用同一绑定 —— 换色 = 换语义。
- ⚠ **`s4` 就是强调橙**。用到 `s4` 的那一页，橙色出现在图外会被读成"这是第 4 类"。
  这类页面的图外强调改用 **加粗 + `--ink`**。
- `.dim` 表示"这一层还没长出来" —— 是论点的一部分，不是省事。

---

## 3. 页面骨架

```html
<body data-profile="review">
  <div class="slide">          <!-- 或 .slide.center / .slide.cover / .slide.section -->
    <div class="chrome-top"></div>
    <div class="tagline">03 · 本页在讲什么</div>
    <h2>标题写结论，不写标签</h2>
    <div class="lead">一句话结论 —— 听众只记得住这一句</div>
    <div class="main c3"><div class="col">…</div><div class="col">…</div><div class="col">…</div></div>
    <div class="footer-bar"><span>P04 / 18</span><span>Source: …</span><span>Tech Sharing</span></div>
  </div>
</body>
```

### 3.1 为什么默认顶对齐（本版和上一代最重要的区别）

上一代默认 `justify-content: center`，页面装不下时溢出会**对称地推向上下两头**：
顶部的眉标和标题被裁掉，同时底部压上 footer，**两头都错**，而且

> 中心线恒在 530，对称缩 padding（52/72 → 40/60）一点用都没有。
> 「超出标称 padding」这件事**改 padding 修不了**。

本版改成顶对齐：溢出只可能发生在底部，`measure.js` 量得到，修法只有一种 —— 砍内容。
内容确实少的页面手动加 `class="center"`（`measure.js` 会在内容偏空时提醒你加）。

### 3.2 栏

```css
.main.c1 { 1fr }   .main.c2 { 1fr 1fr }   .main.c3 { 1fr 1.02fr 1.02fr }
```

- **密排页一上手就 `c3`**。单栏可用高度约 790–960px，两栏放同样内容必然溢出，
  而溢出的修法只有「砍内容」和「一路缩字号」，两条都会把已核实的证据缩到不可读。
  **三栏是结构性解法，缩字号是补救。**
- `.main` 已经写死 `align-items: start`，别覆盖 —— 否则栏被拉齐高、内部块被撑开。
- `.main` 的直接子元素一律是 `.col`。**裸文本节点会被提升成 grid item，多出一格**。
- talk profile 写 `c3` 会真的渲染成三栏并被判 FAIL —— CSS **故意不做静默降级**，
  偷偷改成两栏等于把违规藏起来，比违规本身更糟。

### 3.3 禁止项

- ❌ 密排页开两栏
- ❌ `.fig { flex: 1 }` —— 会在图下方造出一块死白。图的高度让内容决定
- ❌ 整页上下堆（标题 → 文字 → 文字 → 图）
- ❌ 竖向百分比柱条放进 flex 列 —— 会被 flex-shrink 压扁。用 `.bars` 的横向条，或自己写 `grid-template-rows`

---

## 4. 页脚

三段式 `1fr auto 1fr`：`页码` / `Source:` / `品牌`，由 `shared.css` 统一定位，别在页面里重写。

- 正文 `P07 / 18`，附录 `A3 / A8`。**分子分母都由文件名校验**：`P07-xxx.html` → 页码 7，
  分母 = 同组（同字母前缀）最大编号。改了页序忘改 footer，`measure.js` 直接 FAIL。
- 眉标编号 = 页码 + `deck.json` 的 `taglineOffset`（默认 `-1`，即封面不占号）。
  眉标不以数字开头就跳过这条检查。
- ⚠ **长 Source 串陷阱**：中间那段先把左右两段挤扁，再折行；一折行 footer 高度从 16px 变 30px+，
  撞上正文最后一行。判据：`h > 24px` 判 FAIL，中段宽 > 1200px 先给 △ 预警。
  修法是**缩短字符串**，不是缩字号 —— 删版本号、删第二个文件名，只留「哪个文件 + 哪一节 + 复核日期」。

---

## 5. 组件清单

全部定义在 `assets/shared.css`，用法见 `assets/templates/`。

| 组件 | 类名 | 用途 |
|---|---|---|
| 分层堆叠 | `.fig-stack > .lyr.s1` | 架构层次。`.focus` 高亮本次改动层，`.dim` 表示缺口 |
| 阶梯 | `.fig-ladder > .step.s1`（`--steps` 定格数） | 成熟度 / 能力线 / 阶段 |
| 流程 | `.arch-flow > .acol.s1` | 左→右管线，自动带箭头 |
| 结论三块 | `.close3 > .cbox.good/.warn` | 每页收口。放页面最后一行 |
| 要点条 | `.takeaways.c3 > .tk-item` | 三条以内的 takeaway |
| 表格 | `.tbl` + `col.w-code/.w-tight` | 证据表。**列窄了加宽列，不要缩字号** |
| 指标 | `.stat-row > .stat.ok/.mid/.bad` | 一行关键数字 |
| 横向条 | `.bars > .bar > .bt > i[style="--w:78%"]` | 比例对比。截断轴写 `.axis-note` |
| 代码 | `.code > .code-hd + ol > li.on/.add/.del` | 行号自动出；`.on` 高亮重点行 |
| 终端 | `.term > .term-hd + .body > .cmd/.out.ok/.out.err` | 命令与输出 |
| 论断 | `.callout` / `.callout.bad` | 整页就这一句话时用 |
| 行内 | `.hl` `.num` `code` `.pill` `.src` | 强调 / 数字 / 代码 / 标签 / 出处 |

等宽字体**已全局关连字**（`font-variant-ligatures: none`）—— JetBrains Mono 默认把 `--` `!=` `->`
连成单个字形，贴命令行时那是在改事实（`--rps` 会显示成 `—rps`）。新增等宽组件记得加进那条规则。

---

## 6. 判据表（`measure.js` 实际在查的东西）

### ✗ FAIL — 必须改

| 判据 | 阈值 | 修法 |
|---|---|---|
| 顶部裁切 | `top < 8` | 砍内容 |
| 底部压 footer | `bottom > 1046` | **只能砍内容**，改 padding 无效 |
| 左右越界 | `right > 1848` / `left < 72` | 检查负 margin 或固定宽度 |
| 栏数超限 | review > 3 / talk > 2 | 拆页 |
| 字号跌破下限 | review < 9.3 / talk < 16 | 加宽栏 → 砍内容 → 拆页 |
| 彩色 emoji | `\p{Emoji_Presentation}` 或 `️` | 换 `✓ ✗ △ ○ ★ ①②③` |
| footer 折行 | `h > 24` | 缩短 Source 串 |
| 页码 / 分母对不上 | 与文件名不符 | 改 footer |
| 眉标编号错 | ≠ 页码 + `taglineOffset` | 改眉标 |

### △ NOTE — 不算失败，但**必须配一次肉眼看 PNG 才放行**

| 判据 | 阈值 | 含义 |
|---|---|---|
| 越过标称下沿 | `bottom > 1008` | 排满了 |
| 内容偏空 | `bottom < 700` | 加 `class="center"` 或补内容 |
| 列底不齐 | `spread > 140` | 建议补内容而非拉伸；90–140px 肉眼基本无感 |
| 两栏已塞满 | review + c2 + 超下沿 | 改三栏 |
| footer 中段过宽 | `> 1200px` | 快挤到左右两段了 |
| 没有 Source | 中段不含 source/来源/出处 | 本页数字追不到出处 |
| 纯文字页 | 没有表/图/代码块 | 这一页不该存在 |
| 代码块过长 | review > 24 行 / talk > 12 行 | 只贴要讲的那几行 |

---

## 7. 字体：最容易静默出错的地方

`shared.css` 默认从 Google Fonts 拉 Inter + JetBrains Mono。**网络不通时浏览器不报错**，
只是回落到 PingFang SC / 系统等宽 —— 字宽一变，行数变、溢出判据全部失真，而 PNG 看上去"还行"。

所以 `render.js` / `measure.js` / `export-pdf.js` 都会先做字体预检（量宽度，不用
`document.fonts.check`，后者对页面没实际用到的字重会误报），验不过直接停。

- 离线 / 内网 / 要长期归档：`node scripts/vendor-fonts.js`（一次联网），
  字体落到 `slides/fonts/`，生成 `slides/fonts.css`，并注释掉 `shared.css` 里的远端 `@import`。
- 明知回落也要渲染：加 `--allow-fallback`，此时**所有像素判据仅供参考**。

---

## 8. 命令与文件

```
slides/            P01-xxx.html … A3-xxx.html + shared.css (+ fonts.css, fonts/)
screenshots/       render.js 的产物，1920×1080 PNG
scripts/           new-deck / render / measure / export-pptx / export-pdf / vendor-fonts / chrome / fonts / deck
deck.json          页顺序 + 元数据
deck.pptx          位图，上台讲
deck.pdf           真文本，发出去让人翻
```

```bash
node scripts/render.js [前缀…]          # 渲染，不带前缀=全部
node scripts/measure.js [前缀…] [--json] [--sel .foo]
node scripts/export-pptx.js             # 位图 PPTX
node scripts/export-pdf.js              # 文字可选中的 PDF
node scripts/vendor-fonts.js            # 字体本地化
npm run build                           # render → measure → pptx → pdf
```

`deck.json` 字段：`title` / `author` / `subject` / `company` / `out`（输出文件名，`.pptx` 与 `.pdf`
自动互换）/ `profile` / `taglineOffset`（默认 -1，设 `null` 关掉眉标编号检查）/ `pages`（**页顺序的唯一来源**，
不含扩展名；缺页直接报错退出，多出来的页会警告并跳过）。
