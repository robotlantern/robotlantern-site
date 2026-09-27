// Serves a conversation's images from its content folder, so they live next to
// conversation.md and are published at /conversations/<slug>/<file>.
import fs from 'node:fs';
import path from 'node:path';
import type { APIRoute } from 'astro';

const root = 'src/content/conversations';
const types: Record<string, string> = {
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.avif': 'image/avif',
};

export function getStaticPaths() {
  return fs.readdirSync(root).flatMap((slug) =>
    fs
      .readdirSync(path.join(root, slug))
      .filter((file) => path.extname(file).toLowerCase() in types)
      .map((file) => ({ params: { slug, file } })),
  );
}

export const GET: APIRoute = ({ params }) => {
  const file = path.join(root, params.slug!, params.file!);
  return new Response(fs.readFileSync(file), {
    headers: { 'Content-Type': types[path.extname(file).toLowerCase()] },
  });
};
