import { getCollection } from 'astro:content';

export type Author = { id: string; name: string; fullName: string; kind: 'human' | 'ai'; bio: string; bioDraft: boolean };

export async function getAuthors(): Promise<Record<string, Author>> {
  const entries = await getCollection('authors');
  return Object.fromEntries(entries.map((e) => [e.id, { id: e.id, ...e.data }]));
}

export function authorOf(authors: Record<string, Author>, id: string, where: string): Author {
  const a = authors[id];
  if (!a) throw new Error(`${where}: no author "${id}" in src/content/authors/`);
  return a;
}

// Dates read as M.D.YYYY (9.16.2026).
export const shortDate = (d: Date) => `${d.getUTCMonth() + 1}.${d.getUTCDate()}.${d.getUTCFullYear()}`;
