// slides/*.html → 单个 16:9 PDF，**文字可选中、可搜索、可复制**。
//
// 和 PPTX 那条路的分工：
//   PPTX  位图，投影/改不了，但和 PNG 逐像素一致 —— 适合上台讲
//   PDF   真文本，能选能搜能复制代码 —— 适合发出去让人自己翻（技术分享的主要分发形态）
// 两条路同源于同一份 HTML，不会走样。
//
//   node scripts/export-pdf.js
const puppeteer = require('puppeteer-core');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');
const path = require('path');
const { findChrome, LAUNCH_ARGS, newDeckPage } = require('./chrome');
const { assertFonts } = require('./fonts');
const { SLIDES, parseArgs, loadDeck, listSlides } = require('./deck');

const { flags } = parseArgs();
const meta = loadDeck();
const files = listSlides([], { requireAll: true });

(async () => {
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: 'new', args: LAUNCH_ARGS });
  const merged = await PDFDocument.create();
  let fontChecked = false;

  for (const file of files) {
    const page = await newDeckPage(browser);
    await page.goto('file://' + path.join(SLIDES, file), { waitUntil: 'networkidle0', timeout: 30000 });
    if (!fontChecked) {
      if (!await assertFonts(page, { allowFallback: flags['allow-fallback'] })) { await browser.close(); process.exit(1); }
      fontChecked = true;
    }
    await new Promise(r => setTimeout(r, 200));

    const buf = await page.pdf({
      width: '1920px', height: '1080px',
      printBackground: true, pageRanges: '1',
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
    });
    const src = await PDFDocument.load(buf);
    const [p] = await merged.copyPages(src, [0]);
    merged.addPage(p);
    console.log(`  ✓ ${file}`);
    await page.close();
  }

  await browser.close();
  merged.setTitle(meta.title || 'Deck');
  merged.setAuthor(meta.author || 'tech-deck');
  if (meta.subject) merged.setSubject(meta.subject);

  const out = path.resolve(meta.out ? meta.out.replace(/\.pptx$/, '.pdf') : 'deck.pdf');
  fs.writeFileSync(out, await merged.save());
  console.log(`PDF: ${out}`);
  console.log(`${files.length} 页 · ${(fs.statSync(out).size / 1024 / 1024).toFixed(1)} MB · 文字可选中`);
})().catch(e => { console.error(e); process.exit(1); });
