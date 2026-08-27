// 一条命令把工作目录建好，省掉「复制 4 个东西」的手工步骤。
//
//   node <skill>/scripts/new-deck.js ./my-deck              # 默认 review profile
//   node <skill>/scripts/new-deck.js ./my-deck --talk       # 大场地演讲 profile
//
// 建成：my-deck/{slides/{shared.css,P01-cover.html},scripts/*,package.json,deck.json}
const fs = require('fs');
const path = require('path');

const SKILL = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const profile = args.includes('--talk') ? 'talk' : 'review';
const target = path.resolve(args.find(a => !a.startsWith('--')) || 'deck');

if (fs.existsSync(target) && fs.readdirSync(target).length) {
  console.error(`目标目录非空：${target}`); process.exit(1);
}

const copy = (from, to) => { fs.mkdirSync(path.dirname(to), { recursive: true }); fs.copyFileSync(from, to); };

copy(path.join(SKILL, 'assets/shared.css'), path.join(target, 'slides/shared.css'));
copy(path.join(SKILL, 'assets/package.json'), path.join(target, 'package.json'));
for (const f of fs.readdirSync(path.join(SKILL, 'scripts'))) {
  copy(path.join(SKILL, 'scripts', f), path.join(target, 'scripts', f));
}

// 模板整套复制进工作目录，并把 profile 换好 —— 之后加页只需 cp ./templates/X.html slides/，
// 不用再回头找 skill 目录，也不会漏改 data-profile。
const tplDir = path.join(SKILL, 'assets/templates');
for (const f of fs.readdirSync(tplDir)) {
  const html = fs.readFileSync(path.join(tplDir, f), 'utf8')
    .replace('data-profile="review"', `data-profile="${profile}"`);
  fs.mkdirSync(path.join(target, 'templates'), { recursive: true });
  fs.writeFileSync(path.join(target, 'templates', f), html);
}
// 封面直接落成第一页
fs.copyFileSync(path.join(target, 'templates/cover.html'), path.join(target, 'slides/P01-cover.html'));

const deck = JSON.parse(fs.readFileSync(path.join(SKILL, 'assets/deck.json.example'), 'utf8'));
deck.profile = profile;
deck.pages = ['P01-cover'];
fs.writeFileSync(path.join(target, 'deck.json'), JSON.stringify(deck, null, 2) + '\n');

console.log(`建好了：${target}  (profile: ${profile})`);
console.log('下一步：');
console.log(`  cd ${target} && npm install`);
console.log(`  # 需要离线可复现：node scripts/vendor-fonts.js`);
console.log(`  # 每加一页：cp templates/<页型>.html slides/P0N-xxx.html  → 改 footer 页码 → render → measure`);
console.log(`  # 页型：cover / A-hero / B-compare / C-dense / E-code / D-close / section`);
