// "Exact Markdown": the essay's source, byte for byte, as the attribution counts were made.
import fs from 'node:fs';
import type { APIRoute } from 'astro';

const root = 'src/content/essays';

export function getStaticPaths() {
  return fs
    .readdirSync(root)
    .filter((slug) => fs.existsSync(`${root}/${slug}/article.md`))
    .map((slug) => ({ params: { slug } }));
}

export const GET: APIRoute = ({ params }) =>
  new Response(fs.readFileSync(`${root}/${params.slug}/article.md`), {
    headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
  });
