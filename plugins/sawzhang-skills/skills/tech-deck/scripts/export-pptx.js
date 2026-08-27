// screenshots/*.png → 16:9 PPTX（每页一张全铺满的位图）
//
// 为什么是位图而不是可编辑文本框：全部版式在 HTML/CSS 里，pptxgenjs 复刻不了三栏密排图；
// 位图保证投影出来和 PNG 逐像素一致。代价是文字不可选、不可改 —— 需要可选文字就出 PDF
// （node scripts/export-pdf.js，那条路是真文本）。
//
//   node scripts/export-pptx.js
const PptxGenJS = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const { SHOTS, loadDeck, listSlides } = require('./deck');

if (!fs.existsSync(SHOTS)) { console.error(`没有 screenshots 目录：${SHOTS}（先跑 node scripts/render.js）`); process.exit(1); }

const meta = loadDeck();
const pages = listSlides([]).map(f => f.replace(/\.html$/, ''));

const missing = pages.filter(n => !fs.existsSync(path.join(SHOTS, `${n}.png`)));
if (missing.length) {                       // 缺图就停，不要产出一份少页的 pptx
  console.error(`缺少 ${missing.length} 张截图，先跑 node scripts/render.js：`);
  for (const n of missing) console.error(`  - screenshots/${n}.png`);
  process.exit(1);
}

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';                // 13.333 × 7.5 in = 16:9，与 1920×1080 同比
pptx.author  = meta.author  || 'tech-deck';
pptx.title   = meta.title   || 'Deck';
if (meta.subject) pptx.subject = meta.subject;
if (meta.company) pptx.company = meta.company;

for (const name of pages) {
  pptx.addSlide().addImage({
    data: 'image/png;base64,' + fs.readFileSync(path.join(SHOTS, `${name}.png`)).toString('base64'),
    x: 0, y: 0, w: '100%', h: '100%',
  });
}

const out = path.resolve(meta.out ? meta.out.replace(/\.pdf$/, '.pptx') : 'deck.pptx');
pptx.writeFile({ fileName: out }).then(() => {
  const mb = fs.statSync(out).size / 1024 / 1024;
  console.log(`PPTX: ${out}`);
  console.log(`${pages.length} 页 · ${mb.toFixed(1)} MB`);
  if (mb > 20) console.warn('⚠ 超过 20 MB，邮件附件可能被拦 —— 考虑压 PNG 或改发 PDF');
}).catch(e => { console.error('Error:', e); process.exit(1); });
