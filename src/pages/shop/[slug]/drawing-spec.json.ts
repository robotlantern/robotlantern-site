// /shop/<slug>/drawing-spec.json (decision 28): the drawing an assistant makes for "I have my own drawing",
// from products/<slug>/drawing-spec.json. The build stops if the spec's subjects aren't exactly the product
// file's photo subjects, so adding one (a place, say) means writing its drawing rules too.
import type { APIRoute, GetStaticPaths } from 'astro';
import fs from 'node:fs';
import { drawingProducts } from '../../../lib/drawing-product';

export const getStaticPaths = (async () => {
  const paths = [];
  for (const p of await drawingProducts()) {
    const file = `products/${p.id}/drawing-spec.json`;
    if (!fs.existsSync(file)) continue;
    const spec = JSON.parse(fs.readFileSync(file, 'utf8'));
    const made = p.data.drawing!.subjects.filter((s) => s.source !== 'static').map((s) => s.id).sort();
    const specced = spec.subjects.map((s: { id: string }) => s.id).sort();
    if (made.join() !== specced.join()) throw new Error(`${file}: subjects ${specced} but shop.json's photo subjects are ${made}`);
    if (spec.product !== p.id) throw new Error(`${file}: product is ${spec.product}, not ${p.id}`);
    paths.push({ params: { slug: p.id }, props: { body: `${JSON.stringify(spec, null, 2)}\n` } });
  }
  return paths;
}) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) =>
  new Response(props.body as string, { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
