---
name: tech-deck
description: 技术分享幻灯片工作流。用 HTML/CSS 写 1920×1080 的页面，机器体检版式，再导出 PPTX（位图）和 PDF（文字可选中）。当用户说"做 PPT"、"做幻灯片"、"做演示文稿"、"技术分享"、"架构评审"、"技术简报"、"做 slides"、"make a deck"、"presentation"，或要改/扩一套已有的这种 deck 时使用。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# tech-deck — 技术分享幻灯片

把幻灯片当代码写：**HTML/CSS → Chrome 渲染 → 机器体检 → PPTX / PDF**。

核心不是配色，是那条**度量闭环**：溢出、footer 折行、页码对不上、字号被压到不可读、
彩色 emoji、纯文字页 —— 这些看 HTML 看不出来，肉眼看 PNG 会漏，全部由 `measure.js` 判定。
**改完一页必须量一遍**，这是这套东西唯一不能省的步骤。

## 第一步：先定 profile（这是分叉点，不要跳过）

| | `review` 密排 | `talk` 疏排 |
|---|---|---|
| 场景 | 会议室 / 投屏 / 客户自己翻 PDF / 被追问细节的评审 | 大礼堂、大会 talk、几十米开外 |
| 正文字号 | 14px，图内最低 9.3px | ≥ 18px，最低 16px |
| 栏数 | 最多三栏，密排页**一上手就三栏** | 最多两栏，写三栏直接判 FAIL |
| 一页信息量 | 一张大表 + 两块图 | 一个论点 + 一张图 |
| 代码块 | ≤ 24 行 | ≤ 12 行 |

用户没说场景就问一句。**两套的字号底线直接冲突，选错了只能重排，不能靠改字号补救。**

## 建工作目录

```bash
node <本 skill 目录>/scripts/new-deck.js ./my-deck          # review
node <本 skill 目录>/scripts/new-deck.js ./my-deck --talk   # talk
cd my-deck && npm install
node scripts/vendor-fonts.js      # 可选，一次联网；之后离线也能渲染且判据仍有效
```

建出来：`slides/`（HTML + shared.css）· `templates/`（**已按 profile 改好的页型模板**）·
`scripts/` · `deck.json`（页顺序与元数据）· `package.json`

## 单页工作流（改一页就走一遍）

1. `cp templates/<页型>.html slides/P07-xxx.html`
   （**文件名里的编号就是页码**，`measure.js` 拿它校验 footer 和眉标）
2. 改内容。**第一件事是改 footer 的 `P07 / 18` 和眉标编号**，模板里那些是占位符
3. `node scripts/render.js P07` — 只渲染这一页
4. `node scripts/measure.js P07` — 拿判据。有 `--json` 给自动处理
5. **只有 △ / ✗ 的页才** `Read screenshots/P07-xxx.png` 肉眼复核
6. 全 deck 无 ✗ 后：`node scripts/export-pptx.js` + `node scripts/export-pdf.js`

三档判据：`✗` 必须改 · `△` 排满或存疑，**必须配一次肉眼看 PNG 才放行** · `✓` 过。

## 页型（建好目录后在 `./templates/` 下）

| 模板 | 用途 | 什么时候用 |
|---|---|---|
| `cover.html` | 封面 | 标题写"要解决什么问题"，不写"XX 介绍" |
| `A-hero.html` | 主图页 | 一张骨架图撑满 + 三条要点收口 |
| `B-compare.html` | 对照页 | 两个方案/两种口径并排，**必须用同一组指标** |
| `C-dense.html` | 密排页 | 大表、证据清单。三栏起手 |
| `E-code.html` | 代码页 | 代码 + 终端输出同页，**只贴要讲的那几行** |
| `D-close.html` | 收束页 | 结论 / 下一步 / 要听众做什么。每场至少一页，放最后 |
| `section.html` | 转场页 | 只说"上一段结束了"，不塞内容 |

叙事结构、页型怎么配比、数字与出处的规矩 → 读 `references/authoring.md`。

## 不可动摇的几条

- **强调色只有橙 `#E8730A`**；红只给风险/反面，绿只给正面。系列色 `s1..s6` 只在同一张图的分类维度里用，
  一旦绑定就全 deck 一致（⚠ `s4` = 强调橙，用到它的那页，图外强调改用**加粗 + `--ink`**）
- **密排页三栏起步**（`.main.c3`）。两栏塞满再删内容或一路缩字号，都是把已核实的证据缩到不可读
- **溢出只能砍内容**。本版页面顶对齐，装不下就往下溢，`measure.js` 直接 FAIL —— 改 padding 没用
- **所有数字有出处**，footer 中段写「哪个文件 · 哪一节 · 复核日期」，短到不折行（`h ≤ 24px`）
- **截断轴必须在图头声明**；不可比口径的两个数**不许相减**、不许说"增长"
- **别用彩色 emoji**（`⭐ ✅ 🔵 ❌`）—— Chromium 走彩色字体、无视 CSS `color`。用 `✓ ✗ △ ○ ★ ①②③`
- **代码块关连字已在 CSS 里做掉**；行号由 `<ol>` 自动出，别手写（一改就错位）
- **字体没加载就停**。回落到系统字体后字宽变了，所有像素判据失真而 PNG 看着"还行"

完整规范、组件清单、踩坑成因 → `references/visual-spec.md`（改页前必读）。

## 两种产物，分别对应两种场合

| | 用途 | 代价 |
|---|---|---|
| `deck.pptx` | 上台讲。每页一张全铺满位图，投影与 PNG 逐像素一致 | 文字不可选、不可改 |
| `deck.pdf` | 发出去让人自己翻。**文字可选中、可搜索、可复制代码** | 无 |

两者同源于同一份 HTML，不会走样。技术分享通常两个都要出。

## 交付

整个 skill 目录自包含，可直接打包给别人：
`zip -r tech-deck.zip <本 skill 目录>`，对方放进自己的 `.claude/skills/` 即可复用同一套风格与判据。
