// The sitemap: every public page, listed from the same collections the pages are built from.
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async ({ site }) => {
  const paths = [
    '/', '/thoughts/', '/chats/', '/builds/', '/shop/', '/about/', '/authors/',
    '/builds/the-sky-unprojected/',
    ...(await getCollection('essays')).map((e) => `/thoughts/${e.id}/`),
    ...(await getCollection('conversations')).map((c) => `/chats/${c.id}/`),
    ...(await getCollection('pages')).map((p) => `/${p.id}/`),
  ];
  const urls = paths.map((p) => `  <url><loc>${new URL(p, site)}</loc></url>`).join('\n');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`, {
    headers: { 'Content-Type': 'application/xml' },
  });
};
