// node shop-worker/tagfit.test.mjs: the Worker's tag fit against nametag.tag_fit()'s own answers.
import { readFileSync } from 'node:fs';

const metrics = JSON.parse(readFileSync(new URL('./tag-metrics.json', import.meta.url)));
// tagfit.js imports the JSON the way wrangler bundles it; give node the same module.
const src = readFileSync(new URL('./tagfit.js', import.meta.url), 'utf8')
  .replace("import metrics from './tag-metrics.json';", `const metrics = ${JSON.stringify(metrics)};`);
const { tagFit, CASES } = await import(`data:text/javascript,${encodeURIComponent(src)}`);

let bad = 0;
for (const c of CASES) {
  const r = tagFit(c.text, c.font);
  if (r.fits !== c.fits || Math.abs(r.textMm - c.text_mm) > 0.011) {
    bad++;
    console.log(`FAIL ${c.font} ${JSON.stringify(c.text)}: Python ${c.fits} ${c.text_mm} mm, Worker ${r.fits} ${r.textMm} mm`);
  }
}
console.log(`${CASES.length - bad} of ${CASES.length} cases agree with nametag.tag_fit()`);
process.exit(bad ? 1 : 0);
