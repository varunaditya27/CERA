// Scans every route with axe-core at desktop and phone width, then walks the Tab order of /experiments.
// Needs the frontend and backend running. Usage: CHROME_PATH=/usr/bin/google-chrome npm run check:a11y
import { chromium } from 'playwright-core';
import axe from 'axe-core';

const base = process.env.CERA_WEB_URL ?? 'http://127.0.0.1:3000';
const routes = ['/', '/datasets', '/datasets/amylase', '/workflow', '/results', '/predict', '/experiments', '/goals'];
const sizes = { desktop: { width: 1440, height: 900 }, phone: { width: 375, height: 800 } };
const tags = ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice'];

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH, args: ['--no-sandbox'] });
let failures = 0;

for (const [label, viewport] of Object.entries(sizes)) {
  const page = await (await browser.newContext({ viewport })).newPage();
  for (const route of routes) {
    await page.goto(base + route, { waitUntil: 'networkidle' });
    await page.evaluate(axe.source);
    const { violations } = await page.evaluate((runOnly) => axe.run(document, { runOnly }), tags);
    failures += violations.length;
    console.log(label, route, violations.length ? violations.map((v) => `${v.id} x${v.nodes.length}`).join(', ') : 'ok');
  }
}

const page = await (await browser.newContext({ viewport: sizes.desktop })).newPage();
await page.goto(base + '/experiments', { waitUntil: 'networkidle' });
for (let i = 0; i < 20; i++) {
  await page.keyboard.press('Tab');
  const stop = await page.evaluate(() => {
    const el = document.activeElement;
    const style = getComputedStyle(el);
    const interactive = el.matches('a, button, input, select, textarea, summary');
    return { name: (el.innerText || el.id || el.tagName).trim().slice(0, 30), hidden: interactive && style.outlineStyle === 'none' };
  });
  if (stop.hidden) {
    failures += 1;
    console.log('no visible focus ring on', stop.name);
  }
}

await browser.close();
console.log(failures ? `${failures} problem(s)` : 'no problems found');
process.exit(failures ? 1 : 0);
