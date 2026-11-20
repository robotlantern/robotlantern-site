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
// tools/shop/sync.py writes the Stripe IDs and Payment Link URLs under "stripe". Products made from a
// customer's photo add the fields in docs/ORDERS.md ("The product file") and have no Payment Link:
// the order Worker prices them from these files and opens a Checkout Session per order.
const stripeIds = z.object({ url: z.string().url().optional() }).passthrough();
const id = z.string().regex(/^[a-z0-9][a-z0-9-]*$/);
// A fixed product's one choice, shown at checkout (docs/SHOP.md).
const fixedOptions = z.object({
  label: z.string(),
  choices: z.array(z.object({ label: z.string() }).passthrough()).min(1),
});
// A photo product's options: any number, each choice adding `add` dollars to the price.
const photoOptions = z.array(z.object({
  id,
  label: z.string(),
  choices: z.array(z.object({ id, label: z.string(), add: z.number().min(0).default(0) }).passthrough()).min(1),
}));
// A product made from a drawing (the stencil ornament; docs/ORDERS.md, "The product file"): the customer's
// photo becomes a drawing, an order holds several designs, and tiers price it instead of one price.
const subject = z.object({
  id,
  label: z.string(),
  source: z.enum(['made', 'static']).default('made'),
  brief: z.string().optional(),
  crop: z.string().optional(),
  cropMode: z.enum(['fill', 'fit']).default('fill'),
  designs: z.array(z.object({
    id, label: z.string(), drawing: z.string(), sha256: z.string().regex(/^[0-9a-f]{64}$/),
    text: z.string(), font: z.string(), alt: z.string(),
  })).optional(),
}).passthrough().superRefine((s, ctx) => {
  const need = (message: string) => ctx.addIssue({ code: 'custom', path: [s.id], message });
  if (s.source === 'static' && !s.designs?.length) need('a ready-made subject lists its designs');
  if (s.source === 'made' && (!s.brief || !s.crop)) need('a made subject needs a brief and a crop hint');
});
const drawing = z.object({
  model: z.string(),
  quality: z.string(),
  size: z.string(),
  triesPerPhoto: z.number().int().positive(),
  subjects: z.array(subject).min(1),
});
const pricing = z.object({
  tiers: z.array(z.object({ from: z.number().int().positive(), each: z.number().positive() })).min(1),
  maxPerOrder: z.number().int().positive(),
  maxDesigns: z.number().int().positive(),
  modifiers: z.array(z.object({ when: z.record(z.string(), z.string()), add: z.number() })).default([]),
});
const shop = defineCollection({
  loader: glob({ pattern: '*/shop.json', base: './products', generateId: folderId }),
  schema: z.object({
    name: z.string(),
    description: z.string().optional(),
    // A drawing product has pricing instead.
    price: z.number().positive().optional(),
    shipping: z.number().min(0),
    taxCode: z.string().optional(),
    fulfillment: z.enum(['gelato', 'self', 'slant']),
    stock: z.number().int().positive().optional(),
    options: z.union([fixedOptions, photoOptions]).optional(),
    // Photo products only (docs/ORDERS.md). A drawing product's is { via: "drawing", crop, edge }.
    photo: z.union([
      z.object({
        minEdge: z.number().int().positive(),
        crop: z.string().regex(/^(circle|free|rect:\d+x\d+)$/),
        subject: z.boolean(),
        count: z.number().int().positive().default(1),
      }),
      z.object({ via: z.literal('drawing'), crop: z.literal('square'), edge: z.number().int().positive() }),
    ]).optional(),
    drawing: drawing.optional(),
    pricing: pricing.optional(),
    preview: z.string().optional(),
    recipe: z.string().optional(),
    weeklyCap: z.number().int().min(0).optional(),
    orderBy: z.iso.date().nullable().optional(),
    // Why the price isn't final. The order Worker won't sell a provisional product live.
    provisional: z.string().optional(),
    images: z.array(z.string()).default([]),
    listed: z.boolean().default(false),
    stripe: z.object({ test: stripeIds.optional(), live: stripeIds.optional() }).default({}),
  }).passthrough().superRefine((p, ctx) => {
    const need = (path: string, message: string) => ctx.addIssue({ code: 'custom', path: [path], message });
    if (p.drawing) {
      if (!p.pricing) need('pricing', 'a drawing product is priced by pricing.tiers');
      if (p.price !== undefined) need('price', 'a drawing product has pricing, not price');
      if (!p.photo || !('via' in p.photo)) need('photo', 'a drawing product has photo.via "drawing"');
      if (p.weeklyCap === undefined) need('weeklyCap', 'a drawing product needs weeklyCap');
      return;
    }
    if (p.price === undefined) need('price', 'a product needs a price');
    if (!p.photo || 'via' in p.photo) return;
    for (const key of ['preview', 'recipe', 'weeklyCap'] as const) {
      if (p[key] === undefined) need(key, `a photo product needs ${key}`);
    }
    if (p.options && !Array.isArray(p.options)) need('options', 'a photo product lists its options as an array');
    if (p.stock) need('stock', 'a photo product has a weeklyCap, not stock');
    const options = Array.isArray(p.options) ? p.options : [];
    if (new Set(options.map((o) => o.id)).size < options.length) need('options', 'option ids repeat');
    for (const o of options) {
      if (new Set(o.choices.map((c) => c.id)).size < o.choices.length) need('options', `${o.id}: choice ids repeat`);
    }
  }),
});

export const collections = { conversations, essays, authors, pages, builds, shop };
