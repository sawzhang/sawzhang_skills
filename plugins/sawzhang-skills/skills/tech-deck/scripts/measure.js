// 版式体检 —— 这套工具链的核心。
//
// 为什么必须有它：溢出、footer 折行、页码对不上、图内字号被压到不可读，这些**看 HTML 看不出来**，
// 肉眼看 PNG 也会漏几 px 的相撞。所以把「完成后自检清单」全部沉进这个脚本，改完必跑。
//
//   node scripts/measure.js              # 全部页
//   node scripts/measure.js P02 A3       # 只体检这些前缀
//   node scripts/measure.js --json       # 机器可读，给 agent 自动读判据
//   node scripts/measure.js P05 --sel .tbl   # 额外打印指定选择器的盒子
//   node scripts/measure.js --allow-fallback # 字体没加载也测（判据仅供参考）
//
// 判据三档：
//   ✗ FAIL  必须改，改完再测      △ NOTE  排满/存疑，必须配一次肉眼看 PNG 才放行      ✓ 过
const puppeteer = require('puppeteer-core');
const path = require('path');
const { findChrome, LAUNCH_ARGS, newDeckPage } = require('./chrome');
const { assertFonts } = require('./fonts');
const { SLIDES, parseArgs, loadDeck, listSlides } = require('./deck');

// 几何硬线（px，1920×1080 画布）
const K = {
  HARD_TOP: 8,        // 再往上就压到顶部 4px 渐变条
  NOM_TOP: 52,        // 标称内容上沿
  NOM_BOT: 1008,      // 标称内容下沿
  HARD_BOT: 1046,     // 再往下就压到 footer 墨迹
  FOOTER_H: 24,       // 超过即 footer 折行
  RAGGED: 140,        // 两栏列底差，超过肉眼可见
  SPARSE: 700,        // 内容下沿低于此值算「太空」
  SIDE_R: 1848,       // 右侧越界
  SIDE_L: 72,         // 左侧越界
};
// profile 相关的阈值
const PROFILE = {
  review: { fontFloor: 9.3, maxCols: 3, maxCodeLines: 24 },
  talk:   { fontFloor: 16,  maxCols: 2, maxCodeLines: 12 },
};

const { flags, filters } = parseArgs();
const files = listSlides(filters);
const deck = loadDeck();
const taglineOffset = deck.taglineOffset === undefined ? -1 : deck.taglineOffset;
const extraSel = flags.sel ? flags.sel.split(',').map(s => s.trim()).filter(Boolean) : [];

// 页码判据从文件名推导：P02-xxx.html → 组 P、序号 2；分母 = 同组最大序号。
// 这样改了页序/加减页，footer 对不上会立刻被抓到，不需要另开配置。
// 分母按 deck.json 的**完整大纲**算，不按已写完的页算 —— 否则写到第 3 页时 footer 的
// "/ 17" 会被判成错，写完最后一页又得全部改回来。
const all = deck.pages && deck.pages.length
  ? deck.pages.map(n => n.replace(/\.(html|png)$/, '') + '.html')
  : listSlides([]);
const groupMax = {};
for (const f of all) {
  const m = f.match(/^([A-Za-z]*)(\d+)/);
  if (!m) continue;
  const g = m[1] || '';
  groupMax[g] = Math.max(groupMax[g] || 0, parseInt(m[2], 10));
}

(async () => {
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: 'new', args: LAUNCH_ARGS });
  let fontChecked = false;
  const report = [];

  for (const file of files) {
    const page = await newDeckPage(browser);
    await page.goto('file://' + path.join(SLIDES, file), { waitUntil: 'networkidle0', timeout: 30000 });
    if (!fontChecked) {
      if (!await assertFonts(page, { allowFallback: flags['allow-fallback'] })) { await browser.close(); process.exit(1); }
      fontChecked = true;
    }
    await new Promise(r => setTimeout(r, 200));

    const m = file.match(/^([A-Za-z]*)(\d+)/);
    const expect = m
      ? { group: m[1] || '', num: parseInt(m[2], 10), raw: m[0], total: groupMax[m[1] || ''] }
      : null;

    const r = await page.evaluate((ctx) => {
      const { K, PROFILE, extraSel, expect, taglineOffset } = ctx;
      const out = { fails: [], notes: [], info: {}, extra: [] };
      const box = el => { const b = el.getBoundingClientRect(); return { t: Math.round(b.top), b: Math.round(b.bottom), l: Math.round(b.left), r: Math.round(b.right), h: Math.round(b.height), w: Math.round(b.width) }; };
      const slide = document.querySelector('.slide');
      if (!slide) { out.fails.push('页面里没有 .slide 容器'); return out; }

      const profile = document.body.dataset.profile || 'review';
      const P = PROFILE[profile] || PROFILE.review;
      out.info.profile = profile;
      const isCover   = slide.classList.contains('cover');
      const isSection = slide.classList.contains('section');
      const isChrome  = slide.classList.contains('center');
      out.info.kind = isCover ? 'cover' : isSection ? 'section' : 'content';

      // ── 1. 垂直边界 ────────────────────────────────────────────────
      // 只看正常流里的直接子元素（绝对定位的 chrome-top / footer-bar 不参与）
      const flowKids = [...slide.children].filter(el => {
        const cs = getComputedStyle(el);
        return cs.position !== 'absolute' && cs.position !== 'fixed' && el.getBoundingClientRect().height > 0;
      });
      const tops = flowKids.map(el => box(el).t);
      const bots = flowKids.map(el => box(el).b);
      const top = tops.length ? Math.min(...tops) : null;
      const bot = bots.length ? Math.max(...bots) : null;
      out.info.top = top; out.info.bottom = bot;

      if (top !== null && top < K.HARD_TOP) out.fails.push(`顶部裁切 top=${top} < ${K.HARD_TOP}（压到顶部渐变条）`);
      if (bot !== null) {
        if (bot > K.HARD_BOT) out.fails.push(`底部压到 footer：bottom=${bot} > ${K.HARD_BOT} —— 只能砍内容，缩 padding 没用`);
        else if (bot > K.NOM_BOT) out.notes.push(`越过标称下沿 ${bot - K.NOM_BOT}px（bottom=${bot}）—— 排满了，需肉眼复核一次`);
        else if (bot < K.SPARSE && !isCover && !isSection && !isChrome)
          out.notes.push(`内容偏空 bottom=${bot} —— 加 class="center" 居中，或补一块内容`);
      }

      // ── 2. 水平越界 ────────────────────────────────────────────────
      for (const el of flowKids) {
        const b = box(el);
        if (b.r > K.SIDE_R) out.fails.push(`${el.className || el.tagName} 右侧越界 right=${b.r} > ${K.SIDE_R}`);
        if (b.l < K.SIDE_L) out.fails.push(`${el.className || el.tagName} 左侧越界 left=${b.l} < ${K.SIDE_L}`);
      }

      // ── 3. 栏数与列底 ──────────────────────────────────────────────
      const main = slide.querySelector('.main');
      if (main) {
        const cols = getComputedStyle(main).gridTemplateColumns.split(' ').filter(Boolean).length;
        out.info.cols = cols;
        if (cols > P.maxCols) out.fails.push(`${profile} profile 最多 ${P.maxCols} 栏，当前 ${cols} 栏`);
        const kids = [...main.children].map(box).filter(x => x.h > 40);
        out.info.colBottoms = kids.map(x => x.b);
        if (kids.length > 1) {
          const spread = Math.max(...kids.map(x => x.b)) - Math.min(...kids.map(x => x.b));
          if (spread > K.RAGGED) out.notes.push(`列底不齐 spread=${spread}px —— 建议补内容而不是拉伸`);
        }
        if (profile === 'review' && cols === 2 && bot > K.NOM_BOT)
          out.notes.push('两栏已经塞满 —— 改三栏（.main.c3）是结构性解法，缩字号是补救');
      }

      // ── 4. 字号下限 ────────────────────────────────────────────────
      // 页脚/眉标是版式 chrome，尺寸由系统定，不参与正文字号判据。
      let minFs = Infinity, minEl = null;
      const skip = el => el.closest('.footer-bar, .tagline');
      for (const el of slide.querySelectorAll('*')) {
        if (skip(el)) continue;
        const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
        if (!hasText) continue;
        const b = el.getBoundingClientRect();
        if (b.width < 1 || b.height < 1) continue;
        const fs = parseFloat(getComputedStyle(el).fontSize);
        if (fs < minFs) { minFs = fs; minEl = el; }
      }
      if (minEl) {
        out.info.minFontSize = Math.round(minFs * 10) / 10;
        out.info.minFontAt = (minEl.tagName.toLowerCase() + (minEl.className ? '.' + String(minEl.className).trim().split(/\s+/).join('.') : '')).slice(0, 60);
        if (minFs < P.fontFloor)
          out.fails.push(`字号 ${out.info.minFontSize}px < ${P.fontFloor}px 下限（${out.info.minFontAt}）—— 优先加宽栏/砍内容，不要继续缩`);
      }

      // ── 5. 彩色 emoji ──────────────────────────────────────────────
      // Chromium 对这类字符走彩色字体、无视 CSS color，想让它跟着层色变一定失败。
      const EMO = /\p{Emoji_Presentation}|\uFE0F/u;   // \uFE0F = 变体选择符，会把普通符号强制变成彩色 emoji
      const hits = new Set();
      const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
      for (let n = walker.nextNode(); n; n = walker.nextNode()) {
        for (const ch of n.textContent) if (EMO.test(ch)) hits.add(ch);
      }
      for (const el of slide.querySelectorAll('*')) {
        for (const pseudo of ['::before', '::after']) {
          const c = getComputedStyle(el, pseudo).content;
          if (c && c !== 'none') for (const ch of c) if (EMO.test(ch)) hits.add(ch);
        }
      }
      if (hits.size) out.fails.push(`彩色 emoji 字符 ${[...hits].map(c => `U+${c.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')}`).join(' ')} —— 换成 ✓ ✗ △ ○ ★ ①②③`);

      // ── 6. 页脚 ────────────────────────────────────────────────────
      const footer = slide.querySelector('.footer-bar');
      if (!footer) {
        if (!isCover) out.notes.push('没有 .footer-bar —— 正文页应当有页码与出处');
      } else {
        const fb = box(footer);
        out.info.footerH = fb.h;
        if (fb.h > K.FOOTER_H) out.fails.push(`footer 折行 h=${fb.h} > ${K.FOOTER_H} —— 缩短中间那段 Source 串，不要缩字号`);
        // footer 是 1fr auto 1fr：中间那段先把左右两段挤扁，再折行。等它折行才报就晚了，
        // 所以宽度过半就提前提醒（量出来的：可用宽约 1562px，超 1200 已经很挤）。
        const mid = footer.children[1];
        if (mid && mid.getBoundingClientRect().width > 1200)
          out.notes.push(`footer 中段已 ${Math.round(mid.getBoundingClientRect().width)}px 宽，快挤到左右两段 —— 只留「哪个文件 + 哪一节 + 复核日期」`);
        const spans = [...footer.children].map(s => s.textContent.trim());
        out.info.footer = spans;
        if (expect && spans[0]) {
          const mm = spans[0].match(/^\s*([A-Za-z]*)\s*0*(\d+)\s*\/\s*([A-Za-z]*)\s*0*(\d+)\s*$/);
          if (!mm) out.notes.push(`页码格式看不懂：「${spans[0]}」，期望「${expect.group}${expect.num} / ${expect.group}${expect.total}」`);
          else {
            if (parseInt(mm[2], 10) !== expect.num) out.fails.push(`页码对不上：footer 写 ${mm[2]}，文件名是 ${expect.raw}`);
            if (parseInt(mm[4], 10) !== expect.total) out.fails.push(`页码分母对不上：footer 写 ${mm[4]}，本组共 ${expect.total} 页`);
          }
        }
        if (!isCover && !isSection && spans[1] && !/source|来源|出处/i.test(spans[1]))
          out.notes.push('footer 中段没有 Source —— 本页的数字/断言追不到出处');
      }

      // ── 7. 眉标编号 ────────────────────────────────────────────────
      const tag = slide.querySelector('.tagline');
      if (tag && expect && taglineOffset !== null) {
        const tm = tag.textContent.trim().match(/^0*(\d+)/);
        if (tm && parseInt(tm[1], 10) !== expect.num + taglineOffset)
          out.fails.push(`眉标编号 ${tm[1]} ≠ 页码 ${expect.num} ${taglineOffset >= 0 ? '+' : '−'} ${Math.abs(taglineOffset)}`);
      }

      // ── 8. 纯文字页 ────────────────────────────────────────────────
      const VISUAL = '.fig, .fig-stack, .fig-ladder, .arch-flow, .bars, .tbl, .stat-row, .code, .term, .close3, .takeaways, svg, img, canvas, table';
      if (!isCover && !isSection && !slide.querySelector(VISUAL))
        out.notes.push('纯文字页 —— 至少要有一个表/图/代码块，否则这一页不该存在');

      // ── 9. 代码块长度 ──────────────────────────────────────────────
      slide.querySelectorAll('.code ol').forEach((ol, i) => {
        const n = ol.children.length;
        if (n > P.maxCodeLines) out.notes.push(`第 ${i + 1} 个代码块 ${n} 行 > ${P.maxCodeLines}（${profile}）—— 只贴要讲的那几行，用 .on 高亮`);
      });

      for (const s of extraSel) {
        slide.querySelectorAll(s).forEach((e, i) => { const b = box(e); out.extra.push(`${s}[${i}] top=${b.t} bottom=${b.b} h=${b.h} w=${b.w}`); });
      }
      return out;
    }, { K, PROFILE, extraSel, expect, taglineOffset });

    r.file = file;
    r.mark = r.fails.length ? '✗' : (r.notes.length ? '△' : '✓');
    report.push(r);
    await page.close();
  }

  await browser.close();

  const bad = report.filter(r => r.fails.length).length;
  const tight = report.filter(r => !r.fails.length && r.notes.length).length;

  if (flags.json) {
    console.log(JSON.stringify({ pass: report.length - bad - tight, note: tight, fail: bad, pages: report }, null, 2));
  } else {
    for (const r of report) {
      console.log(`${r.mark} ${r.file}`);
      if (r.fails.length || r.notes.length || extraSel.length) {
        const i = r.info;
        console.log(`    ${i.profile}/${i.kind}  top=${i.top} bottom=${i.bottom}  cols=${i.cols ?? '—'}  ` +
                    `minFont=${i.minFontSize ?? '—'}  footerH=${i.footerH ?? '—'}  列底=[${(i.colBottoms || []).join(', ')}]`);
      }
      for (const x of r.fails) console.log(`    ✗ ${x}`);
      for (const x of r.notes) console.log(`    △ ${x}`);
      for (const x of r.extra) console.log(`      · ${x}`);
    }
    console.log(`\n${report.length} 页：${report.length - bad - tight} 合规 · ${tight} 需肉眼复核（△）· ${bad} 不合规（✗）`);
    if (tight) console.log(`△ 的页请 Read screenshots/<页>.png 复核一次再放行：` +
      report.filter(r => r.mark === '△').map(r => r.file.replace(/\.html$/, '.png')).join(' '));
  }
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
