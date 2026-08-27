// 找一个能用的 Chrome/Chromium。优先 CHROME_PATH，其次 playwright/puppeteer 缓存，最后系统安装位置。
const fs = require('fs');
const path = require('path');
const os = require('os');

function fromCache() {
  const bases = [
    process.env.PLAYWRIGHT_BROWSERS_PATH,
    path.join(os.homedir(), '.cache', 'ms-playwright'),
    path.join(os.homedir(), 'Library', 'Caches', 'ms-playwright'),
    path.join(os.homedir(), 'AppData', 'Local', 'ms-playwright'),
    path.join(os.homedir(), '.cache', 'puppeteer'),
    path.join(os.homedir(), 'Library', 'Caches', 'puppeteer'),
  ].filter(Boolean);
  const hits = [];
  for (const base of bases) {
    if (!fs.existsSync(base)) continue;
    for (const dir of fs.readdirSync(base)) {
      if (!/^chrom/i.test(dir)) continue;
      for (const rel of [
        'chrome-linux/chrome', 'chrome-linux64/chrome',
        'chrome-mac/Chromium.app/Contents/MacOS/Chromium',
        'chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
        'chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
        'chrome-win/chrome.exe', 'chrome-win64/chrome.exe',
      ]) {
        const p = path.join(base, dir, rel);
        if (fs.existsSync(p)) hits.push(p);
      }
    }
  }
  return hits.sort().pop();
}

function findChrome() {
  const candidates = [
    process.env.CHROME_PATH,
    fromCache(),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser',
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
  ].filter(Boolean);
  const found = candidates.find(p => { try { return fs.existsSync(p); } catch { return false; } });
  if (!found) {
    console.error('找不到 Chrome/Chromium。设 CHROME_PATH 指向可执行文件，或 npx playwright install chromium。');
    process.exit(1);
  }
  return found;
}

const LAUNCH_ARGS = ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none'];

async function newDeckPage(browser) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  return page;
}

module.exports = { findChrome, LAUNCH_ARGS, newDeckPage };
