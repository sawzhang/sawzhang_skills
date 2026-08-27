// 把 Inter + JetBrains Mono 下载到 slides/fonts/，并改用本地 @font-face。
//
// 为什么要做：shared.css 默认从 Google Fonts 拉字体。网络不通时浏览器**不报错**，
// 只是回落到系统字体 —— 字宽一变，所有溢出判据就失真了。离线/内网/要长期归档的 deck，
// 跑一次这个脚本把字体固化下来，从此渲染结果可复现。
//
//   node scripts/vendor-fonts.js          # 需要一次联网
const fs = require('fs');
const path = require('path');
const { SLIDES } = require('./deck');

// 用桌面 Chrome 的 UA 拿 woff2（给别的 UA 会返回 ttf/eot）
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const CSS_URL = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap';

(async () => {
  const fontsDir = path.join(SLIDES, 'fonts');
  fs.mkdirSync(fontsDir, { recursive: true });

  console.log('拉取 Google Fonts CSS …');
  const res = await fetch(CSS_URL, { headers: { 'User-Agent': UA } });
  if (!res.ok) { console.error(`失败：HTTP ${res.status}`); process.exit(1); }
  let css = await res.text();

  const urls = [...new Set([...css.matchAll(/url\((https:\/\/[^)]+\.woff2)\)/g)].map(m => m[1]))];
  if (!urls.length) { console.error('没在 CSS 里找到 woff2 链接'); process.exit(1); }
  console.log(`下载 ${urls.length} 个字体切片 …`);

  let n = 0;
  for (const u of urls) {
    const name = u.split('/').slice(-2).join('-');
    const dest = path.join(fontsDir, name);
    if (!fs.existsSync(dest)) {
      const r = await fetch(u, { headers: { 'User-Agent': UA } });
      if (!r.ok) { console.error(`  ✗ ${u} → HTTP ${r.status}`); process.exit(1); }
      fs.writeFileSync(dest, Buffer.from(await r.arrayBuffer()));
      n++;
    }
    css = css.split(u).join(`./fonts/${name}`);
  }

  fs.writeFileSync(path.join(SLIDES, 'fonts.css'),
    `/* 由 scripts/vendor-fonts.js 生成 —— 本地字体，渲染结果可复现。别手改。 */\n${css}`);

  // 关掉远端 @import，否则同名 @font-face 会被后加载的远端版本覆盖
  const sharedPath = path.join(SLIDES, 'shared.css');
  if (fs.existsSync(sharedPath)) {
    const shared = fs.readFileSync(sharedPath, 'utf8');
    const patched = shared.replace(
      /^@import url\('https:\/\/fonts\.googleapis\.com[^\n]*$/m,
      m => `/* 已本地化，见 fonts.css —— ${m} */`);
    if (patched !== shared) { fs.writeFileSync(sharedPath, patched); console.log('已注释掉 shared.css 里的远端 @import'); }
  }

  console.log(`完成：新下载 ${n} 个切片 → slides/fonts/ ，生成 slides/fonts.css`);
  console.log('现在断网也能 render / measure，判据仍然有效。');
})().catch(e => { console.error(e); process.exit(1); });
