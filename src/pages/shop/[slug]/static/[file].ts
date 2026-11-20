// The ready-made designs' drawings (decision 30), published at /shop/<slug>/static/<file> straight from
// products/<slug>/static/, so the gallery, the shop card and product.json all point at the files the
// routine builds from. A published drawing is never edited (docs/ORDERS.md), so they cache for a year.
import type { APIRoute, GetStaticPaths } from 'astro';
import { getCollection } from 'astro:content';
import fs from 'node:fs';

export const getStaticPaths = (async () => {
  const paths = [];
  for (const p of await getCollection('shop')) {
    for (const s of p.data.drawing?.subjects ?? []) {
      for (const d of s.designs ?? []) {
        if (!d.drawing.startsWith('static/')) throw new Error(`${p.id}/${s.id}/${d.id}: drawing must be under static/`);
        paths.push({ params: { slug: p.id, file: d.drawing.slice('static/'.length) }, props: { path: `products/${p.id}/${d.drawing}` } });
      }
    }
  }
  return paths;
}) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) =>
  new Response(fs.readFileSync(props.path as string), { headers: { 'Content-Type': 'image/png' } });
