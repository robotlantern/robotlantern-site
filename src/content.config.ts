// Content schemas. The files are plain Markdown and JSON; this is where their shape is
// written down and checked at build time (docs/FRAMEWORK.md).
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import fs from 'node:fs';
import { parse as parseYaml } from 'yaml';

const folderId = ({ entry }: { entry: string }) => entry.split('/')[0];

// conversation.md is read as frontmatter plus raw body; pages render it with
// src/lib/markdown.ts, so Astro's own Markdown pipeline stays out of it.
const conversationDir = './src/content/conversations';
const conversations = defineCollection({
  loader: {
    name: 'conversation-folders',
    async load({ store, parseData }) {
      store.clear();
      for (const id of fs.readdirSync(conversationDir)) {
        const filePath = `${conversationDir}/${id}/conversation.md`;
        if (!fs.existsSync(filePath)) continue;
        const source = fs.readFileSync(filePath, 'utf8');
        const match = /^---\n([\s\S]*?)\n---\n?/.exec(source);
        if (!match) throw new Error(`${filePath}: missing frontmatter`);
        const data = await parseData({ id, data: parseYaml(match[1]), filePath });
        store.set({ id, data, body: source.slice(match[0].length), filePath });
      }
    },
  },
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    source: z.string(),
    participants: z
      .array(
        z.object({
          id: z.string(),
          name: z.string(),
          kind: z.enum(['human', 'ai']),
          model: z.string().optional(),
        }),
      )
      .min(2),
    timezone: z.string(),
    range: z.string(),
  }),
});

// An essay folder holds article.md (the exact published Markdown, no frontmatter, because
// attribution offsets index into it), attribution.json from tools/attribution, and this file.
const essays = defineCollection({
  loader: glob({ pattern: '*/essay.json', base: './src/content/essays', generateId: folderId }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date().optional(),
  }),
});

export const collections = { conversations, essays };
