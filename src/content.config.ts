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
        // post.json, beside the transcript, holds publishing facts that aren't part of the chat:
        // when it was posted here (which can differ from when the chat happened).
        const postFile = `${conversationDir}/${id}/post.json`;
        const post = fs.existsSync(postFile) ? JSON.parse(fs.readFileSync(postFile, 'utf8')) : {};
        const data = await parseData({ id, data: { ...parseYaml(match[1]), ...post }, filePath });
        store.set({ id, data, body: source.slice(match[0].length), filePath });
      }
    },
  },
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    time: z.string().optional(),
    source: z.string(),
    participants: z
      .array(
        z.object({
          id: z.string(),
          name: z.string(),
          kind: z.enum(['human', 'ai']),
          model: z.string().optional(),
          author: z.string(),
        }),
      )
      .min(2),
    timezone: z.string(),
    range: z.string(),
    // When it was posted here. Defaults to the chat's own date; a placeholder until launch.
    posted: z.coerce.date().optional(),
    postedPlaceholder: z.boolean().default(false),
  }),
});

// An essay folder holds article.md (the published Markdown, no frontmatter, because attribution
// offsets index into it), attribution.json from tools/attribution, and essay.json.
const essays = defineCollection({
  loader: glob({ pattern: '*/essay.json', base: './src/content/essays', generateId: folderId }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    // True until the real publication date is known (it's the launch date for the first essays).
    datePlaceholder: z.boolean().default(false),
    // Attribution participant id -> author id.
    authors: z.record(z.string(), z.string()),
  }),
});

// People and models who write here. The display name is what pages show; the full name is only
// for the bio.
const authors = defineCollection({
  loader: glob({ pattern: '*.json', base: './src/content/authors', generateId: ({ entry }) => entry.replace(/\.json$/, '') }),
  schema: z.object({
    name: z.string(),
    fullName: z.string(),
    kind: z.enum(['human', 'ai']),
    bio: z.string(),
    bioDraft: z.boolean().default(false),
  }),
});

// Standalone pages linked from the footer (privacy, terms, credits): plain Markdown with a title,
// a one-line description and the date they last changed.
const pages = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/pages' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    updated: z.coerce.date(),
  }),
});

// Builds (interactives). Each runs full screen from its own page in src/pages/builds/; this is
// what the Builds page's card shows, and the chat it came from.
const builds = defineCollection({
  loader: glob({ pattern: '*.json', base: './src/content/builds', generateId: ({ entry }) => entry.replace(/\.json$/, '') }),
  schema: z.object({
    title: z.string(),
    headline: z.string(),
    summary: z.string(),
    image: z.string(),
    chat: z.string().optional(),
    posted: z.coerce.date(),
  }),
});

// Shop listings: products/<slug>/shop.json, beside the product's pipeline file (docs/SHOP.md).
// tools/shop/sync.py writes the Stripe IDs and Payment Link URLs under "stripe".
const stripeIds = z.object({ url: z.string().url() }).passthrough();
const shop = defineCollection({
  loader: glob({ pattern: '*/shop.json', base: './products', generateId: folderId }),
  schema: z.object({
    name: z.string(),
    description: z.string().optional(),
    price: z.number().positive(),
    shipping: z.number().min(0),
    taxCode: z.string().optional(),
    fulfillment: z.enum(['gelato', 'self']),
    stock: z.number().int().positive().optional(),
    images: z.array(z.string()).default([]),
    listed: z.boolean().default(false),
    stripe: z.object({ test: stripeIds.optional(), live: stripeIds.optional() }).default({}),
  }).passthrough(),
});

export const collections = { conversations, essays, authors, pages, builds, shop };
