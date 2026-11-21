// /shop/<slug>/product.json (decision 28; docs/ORDERS.md, "Agents"): the product's public facts for AI
// assistants, built from products/<slug>/shop.json at build time, so its prices can't drift from the page's.
import type { APIRoute, GetStaticPaths } from 'astro';
import { drawingProducts, publicProduct, type DrawingProduct } from '../../../lib/drawing-product';

export const getStaticPaths = (async () =>
  (await drawingProducts()).map((p) => ({ params: { slug: p.id }, props: { p } }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props, site }) =>
  new Response(`${JSON.stringify(publicProduct(props.p as DrawingProduct, site!), null, 2)}\n`, {
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
