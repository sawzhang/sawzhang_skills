// 字体预检 —— 本工具链最容易「静默变形」的地方。
//
// shared.css 从 Google Fonts 拉 Inter + JetBrains Mono。网络不通时浏览器**不会报错**，
// 只会回落到 PingFang SC / 系统等宽字体，于是：字宽变了 → 行数变了 → 溢出判据全部失真，
// 而渲染出来的 PNG 看上去「还行」。所以渲染/体检前一律先验字体，验不过就停。
//
// 怎么验：不用 document.fonts.check（它对页面没实际用到的字重会误报），
// 改成量宽度 —— 同一串字，用 "<目标字体>, serif" 和纯 "serif" 各量一次，
// 宽度相同就说明目标字体压根没生效。
//
// 离线环境：先跑 node scripts/vendor-fonts.js 把字体落到 slides/fonts/，
// 或加 --allow-fallback 显式接受回落字体（此时所有像素判据仅供参考）。
const FAMILIES = ['Inter', 'JetBrains Mono'];

async function checkFonts(page) {
  return page.evaluate(async (families) => {
    if (document.fonts) {
      // 先触发按需加载，再等全部 pending 完成
      await Promise.all(families.flatMap(f =>
        ['400 16px', '700 16px'].map(w =>
          document.fonts.load(`${w} "${f}"`).catch(() => null))));
      await document.fonts.ready;
    }
    const probe = document.createElement('span');
    probe.style.cssText = 'position:absolute;left:-9999px;top:0;font-size:80px;white-space:nowrap;visibility:hidden';
    probe.textContent = 'MMMWWWiiill1100Ooo—技术分享';
    document.body.appendChild(probe);
    const widthOf = (stack) => { probe.style.fontFamily = stack; return probe.getBoundingClientRect().width; };

    const missing = [];
    for (const f of families) {
      // 两个基准字体都比一遍，避免目标字体碰巧与某一个基准同宽造成误判
      const same = ['serif', 'monospace'].every(base =>
        Math.abs(widthOf(`"${f}", ${base}`) - widthOf(base)) < 0.5);
      if (same) missing.push(f);
    }
    probe.remove();
    return { ok: missing.length === 0, missing };
  }, FAMILIES);
}

// 返回 true 表示可以继续。allowFallback 时只警告。
async function assertFonts(page, { allowFallback = false, quiet = false } = {}) {
  const r = await checkFonts(page);
  if (r.ok) return true;
  const msg = `字体未生效：${r.missing.join(', ')}`;
  if (allowFallback) {
    if (!quiet) console.warn(`  ⚠ ${msg} —— 已按 --allow-fallback 继续，像素判据不可信`);
    return true;
  }
  console.error(`✗ ${msg}`);
  console.error('  排版判据是按真字体标定的，回落字体会让溢出判断失真。');
  console.error('  离线请跑：node scripts/vendor-fonts.js   或显式加 --allow-fallback');
  return false;
}

module.exports = { checkFonts, assertFonts, FAMILIES };
