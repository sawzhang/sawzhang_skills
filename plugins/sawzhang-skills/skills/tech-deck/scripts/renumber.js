// 按 deck.json 的页顺序，重写每页 footer 的页码和眉标编号。
//
// 为什么要有它：模板里的页码是占位符，插页/删页/调序之后每一页都得手改，
// 而 measure.js 会把每一处不一致都判 ✗。这活儿是纯机械的，交给脚本。
//
//   node scripts/renumber.js            # 按 deck.json 重写全部页
//   node scripts/renumber.js --dry      # 只报告会改什么，不落盘
//
// 规则（和 measure.js 的判据一一对应）：
//   footer 第一段  →  `<组><序号> / <组><该组最大序号>`，如 `P07 / 18`、`A1 / A2`
//   眉标前导数字   →  序号 + deck.json 的 taglineOffset（默认 -1）；眉标不以数字开头就不动
const fs = require('fs');
const path = require('path');
const { SLIDES, parseArgs, loadDeck, listSlides } = require('./deck');

const { flags } = parseArgs();
const deck = loadDeck();
const taglineOffset = deck.taglineOffset === undefined ? -1 : deck.taglineOffset;
const files = listSlides([]);

// 分母按 deck.json 的**完整大纲**算，不按已写完的页算 —— 大纲写全、页面一张张补时，
// 按已写的页算会得出 "P02 / 2"，写完最后一页又要全部改回来。
const outline = deck.pages && deck.pages.length
  ? deck.pages.map(n => n.replace(/\.(html|png)$/, '') + '.html')
  : files;

// 组内最大序号 = 该组分母；第一个出现的组视为正文（分母默认不带字母）
const groupMax = {};
let firstGroup = null;
for (const f of outline) {
  const m = f.match(/^([A-Za-z]*)(\d+)/);
  if (!m) continue;
  const g = m[1] || '';
  if (firstGroup === null) firstGroup = g;
  groupMax[g] = Math.max(groupMax[g] || 0, parseInt(m[2], 10));
}

let changed = 0, skipped = 0;
for (const file of files) {
  const m = file.match(/^([A-Za-z]*)(\d+)/);
  if (!m) { skipped++; continue; }
  const group = m[1] || '', num = parseInt(m[2], 10), raw = m[0];
  const total = groupMax[group];
  const pad = m[2].length;

  const p = path.join(SLIDES, file);
  const before = fs.readFileSync(p, 'utf8');

  // 分母带不带组字母，沿用这一页原本的写法：正文习惯 `P07 / 17`，附录习惯 `A1 / A2`。
  // 两种 measure.js 都认，所以脚本只改数字，不替作者改风格。
  const curLabel = (before.match(/<div class="footer-bar">\s*<span>([^<]*)<\/span>/) || [])[1] || '';
  const parsed = curLabel.match(/^\s*[A-Za-z]*\s*\d+\s*\/\s*([A-Za-z]*)\s*\d+\s*$/);
  const denomPrefix = parsed ? parsed[1] : (group === firstGroup ? '' : group);
  const label = `${raw} / ${denomPrefix}${String(total).padStart(pad, '0')}`;
  let after = before;
  const edits = [];

  // footer 第一段
  after = after.replace(
    /(<div class="footer-bar">\s*<span>)([^<]*)(<\/span>)/,
    (whole, open, cur, close) => {
      if (cur.trim() === label) return whole;
      edits.push(`footer 「${cur.trim()}」→「${label}」`);
      return open + label + close;
    });

  // 眉标前导数字
  if (taglineOffset !== null) {
    after = after.replace(
      /(<div class="tagline">)(\s*)(\d+)/,
      (whole, open, sp, cur) => {
        const want = String(num + taglineOffset).padStart(cur.length, '0');
        if (cur === want) return whole;
        edits.push(`眉标 ${cur} → ${want}`);
        return open + sp + want;
      });
  }

  if (!edits.length) continue;
  changed++;
  console.log(`${flags.dry ? '·' : '✓'} ${file}`);
  for (const e of edits) console.log(`    ${e}`);
  if (!flags.dry) fs.writeFileSync(p, after);
}

console.log(`\n${files.length} 页：${changed} 页${flags.dry ? '需要改' : '已改'}${skipped ? ` · ${skipped} 页文件名无编号，跳过` : ''}`);
if (!flags.dry && changed) console.log('改完记得重新 render + measure。');
