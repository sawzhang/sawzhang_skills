// slides/*.html → screenshots/*.png（1920×1080）
//
//   node scripts/render.js              # 全部页
//   node scripts/render.js P02          # 只渲染 P02 开头的页
//   node scripts/render.js P02 A3       # 多个前缀
//   node scripts/render.js --allow-fallback   # 字体没加载也照渲（判据不可信）
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const { findChrome, LAUNCH_ARGS, newDeckPage } = require('./chrome');
const { assertFonts } = require('./fonts');
const { SLIDES, SHOTS, parseArgs, listSlides } = require('./deck');

const { flags, filters } = parseArgs();
const files = listSlides(filters);
if (!fs.existsSync(SHOTS)) fs.mkdirSync(SHOTS, { recursive: true });

(async () => {
  console.log(`Rendering ${files.length} slide(s)${filters.length ? ` [${filters.join(' ')}]` : ''}`);
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: 'new', args: LAUNCH_ARGS });
  let fontChecked = false;

  for (const file of files) {
    const page = await newDeckPage(browser);
    await page.goto('file://' + path.join(SLIDES, file), { waitUntil: 'networkidle0', timeout: 30000 });

    if (!fontChecked) {                       // 只验一次，四个脚本行为一致
      if (!await assertFonts(page, { allowFallback: flags['allow-fallback'] })) { await browser.close(); process.exit(1); }
      fontChecked = true;
    }
    await new Promise(r => setTimeout(r, 250));   // 等 web font 真正上屏

    const out = path.join(SHOTS, file.replace(/\.html$/, '.png'));
    await page.screenshot({ path: out, type: 'png', clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    console.log(`  ✓ ${file} → ${path.basename(out)}`);
    await page.close();
  }

  await browser.close();
  console.log('Done. 下一步：node scripts/measure.js' + (filters.length ? ` ${filters.join(' ')}` : ' --all'));
})().catch(e => { console.error(e); process.exit(1); });
