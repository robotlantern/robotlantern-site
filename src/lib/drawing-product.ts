// The public facts of a product made from a drawing (docs/ORDERS.md, "Agents"), worked out once from its
// products/<slug>/shop.json, so the page, product.json, llms.txt, the AI page and the home page all say the
// same prices and dates. Nothing here carries Stripe IDs, Slant filament IDs, briefs or caps.
import { getCollection, type CollectionEntry } from 'astro:content';

export type DrawingProduct = CollectionEntry<'shop'>;

export const drawingProducts = async () => (await getCollection('shop')).filter((p) => p.data.drawing);

export const money = (n: number) => `$${n % 1 ? n.toFixed(2) : n}`;

// "$22 each for 1; $17 each for 2; … $8.50 each for 50" (the page's wording).
export function tierText(p: DrawingProduct) {
  const { tiers, maxPerOrder } = p.data.pricing!;
  if (tiers.length === 1) return `${money(tiers[0].each)} each`;
  return tiers.map((t, i) => {
    const last = tiers[i + 1] ? tiers[i + 1].from - 1 : maxPerOrder;
    return `${money(t.each)} each for ${t.from}${last > t.from ? `–${last}` : ''}`;
  }).join('; ');
}

export const orderByText = (p: DrawingProduct) => p.data.orderBy
  ? new Date(`${p.data.orderBy}T12:00:00Z`).toLocaleDateString('en-US', { month: 'long', day: 'numeric', timeZone: 'UTC' })
  : null;

const option = (p: DrawingProduct, id: string) => (p.data.options as any[]).find((o) => o.id === id);

// product.json (decision 28): what an assistant needs to help a customer order, and no more.
export function publicProduct(p: DrawingProduct, site: URL) {
  const d = p.data;
  const slug = p.id;
  const abs = (path: string) => new URL(path, site).href;
  const page = abs(`/shop/${slug}/`);
  const subjects = d.drawing!.subjects;
  const text = (d as any).text;
  const colours = option(p, 'base').choices.map((c: any) => ({ id: c.id, label: c.label, hex: c.hex }));
  const stencil = option(p, 'stencil').choices.map((c: any) => c.id);
  return {
    spec: 'robotlantern-product',
    generated: 'at build time from the product file',
    name: d.name,
    description: d.description,
    page,
    instructions: abs(`/shop/${slug}/ai/`),
    drawingSpec: abs(`/shop/${slug}/drawing-spec.json`),
    madeToOrder: true,
    material: 'PLA, two parts: a stencil pressed onto a base in a second colour, with a ring to hang it',
    size: {
      artBoxMm: [80, 85],
      rimMm: 2,
      ringMm: 10,
      tag: { heightMm: 17, widthMm: [Math.max(64, text?.minTagWidth ?? 64), 72] },
    },
    fulfilment: 'printed and shipped by Slant 3D',
    shipsTo: ['US'],
    currency: 'USD',
    pricing: {
      perOrnament: d.pricing!.tiers.map((t) => ({ fromCount: t.from, each: t.each })),
      rule: "every ornament in an order is priced by the order's total count, across all its designs",
      shippingIncluded: true,
      salesTax: 'added at checkout where it applies',
      maxPerOrder: d.pricing!.maxPerOrder,
      maxDesigns: d.pricing!.maxDesigns,
      overMax: `write to help@robotlantern.com for a quote`,
      summary: `${tierText(p)}, with US shipping included`,
    },
    orderBy: d.orderBy ? { date: d.orderBy, for: 'Christmas' } : null,
    promise: "a free remake or a refund if it arrives broken or doesn't match the preview",
    subjects: subjects.map((s) => s.source === 'static'
      ? {
          id: s.id, label: s.label, kind: 'ready-made', blurb: (s as any).blurb ?? null,
          needs: 'nothing: no photo and no drawing',
          designs: s.designs!.map((x) => ({
            id: x.id, label: x.label, alt: x.alt, drawing: abs(`/shop/${slug}/${x.drawing}`),
            suggestedText: x.text, suggestedFont: x.font, order: { static: `${s.id}/${x.id}` },
          })),
        }
      : {
          id: s.id, label: s.label, kind: 'from a photo', blurb: (s as any).blurb ?? null,
          needs: 'a photo the customer has the right to use, or their own drawing to the drawing spec',
          crop: s.crop, cropMode: s.cropMode, triesPerPhoto: d.drawing!.triesPerPhoto,
        }),
    colours: { choices: colours, base: colours.map((c: any) => c.id), stencil, rule: 'the base and the stencil must be different colours' },
    suggestedPairs: ((d as any).pairs ?? []).map((x: any) => ({ label: x.label, base: x.base, stencil: x.stencil })),
    nameTag: {
      optional: true,
      maxCharacters: text.max,
      allowed: text.allowed,
      fonts: option(p, 'font').choices.map((c: any) => ({ id: c.id, label: c.label })),
      defaultFont: option(p, 'font').default ?? null,
      fit: 'the text must also fit the tag in the chosen font, with letters at least 5 mm tall; the page offers only the fonts where it fits',
    },
    payment: "a person pays on Stripe's hosted checkout page, or approves it in their own wallet; we take no card details or payment tokens any other way",
    policies: {
      privacy: abs('/privacy/'), terms: abs('/terms/'), shipping: abs('/shipping/'), returns: abs('/returns/'),
    },
    contact: 'help@robotlantern.com',
  };
}
