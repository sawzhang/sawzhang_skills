// 目录约定 + 参数解析 + deck.json 读取。四个脚本共用，避免各写各的前缀过滤。
const fs = require('fs');
const path = require('path');

const SLIDES = process.env.SLIDES_DIR || path.resolve('slides');
const SHOTS  = process.env.SHOTS_DIR  || path.resolve('screenshots');
const DECK   = process.env.DECK_JSON  || path.resolve('deck.json');

// 已知的带值参数（--sel .foo）。其余 --xxx 一律当布尔开关。
const VALUED = new Set(['--sel', '--out']);

function parseArgs(argv = process.argv.slice(2)) {
  const flags = {}, filters = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      if (VALUED.has(a)) { flags[a.slice(2)] = argv[++i]; }
      else { flags[a.slice(2)] = true; }
    } else {
      filters.push(a);          // 位置参数一律是页面前缀，一个都不许吞
    }
  }
  return { flags, filters };
}

function loadDeck() {
  if (!fs.existsSync(DECK)) return {};
  try { return JSON.parse(fs.readFileSync(DECK, 'utf8')); }
  catch (e) { console.error(`deck.json 解析失败：${e.message}`); process.exit(1); }
}

// 页顺序：deck.json 的 pages 优先（显式可控），否则退回文件名排序。
//
// requireAll 的分工：写作期（render / measure）deck.json 通常先把大纲写全、页面一张一张补，
// 缺页只警告并跳过；导出期（pptx / pdf）缺页是硬错误 —— 绝不产出一份少页的交付物。
function listSlides(filters = [], { requireAll = false } = {}) {
  if (!fs.existsSync(SLIDES)) {
    console.error(`没有 slides 目录：${SLIDES}（先跑 node scripts/new-deck.js <dir> 建骨架）`);
    process.exit(1);
  }
  const onDisk = fs.readdirSync(SLIDES).filter(f => f.endsWith('.html')).sort();
  const deck = loadDeck();
  let ordered = onDisk;
  if (Array.isArray(deck.pages) && deck.pages.length) {
    const want = deck.pages.map(n => n.replace(/\.(html|png)$/, '') + '.html');
    const missing = want.filter(f => !onDisk.includes(f));
    if (missing.length) {
      if (requireAll) {
        console.error(`deck.json 里有 ${missing.length} 页在 slides/ 下不存在：${missing.join(', ')}`);
        process.exit(1);
      }
      console.warn(`⚠ deck.json 里 ${missing.length} 页还没写，本次跳过：${missing.join(', ')}`);
    }
    const extra = onDisk.filter(f => !want.includes(f));
    if (extra.length) console.warn(`⚠ ${extra.length} 页不在 deck.json 的 pages 里，本次忽略：${extra.join(', ')}`);
    ordered = want.filter(f => onDisk.includes(f));
  }
  if (!filters.length) return ordered;
  const hit = ordered.filter(f => filters.some(p => f.startsWith(p)));
  if (!hit.length) { console.error(`没有匹配 ${filters.join(' / ')} 的页面`); process.exit(1); }
  return hit;
}

module.exports = { SLIDES, SHOTS, DECK, parseArgs, loadDeck, listSlides };
