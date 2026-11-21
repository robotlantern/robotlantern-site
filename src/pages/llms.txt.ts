// /llms.txt (decision 28): a plain map of the site for AI assistants, with the shop first. Built from the
// product files at build time, so its prices, dates and ready-made designs match the product page's.
import type { APIRoute } from 'astro';
import { drawingProducts, orderByText, tierText } from '../lib/drawing-product';

export const GET: APIRoute = async ({ site }) => {
  const abs = (path: string) => new URL(path, site).href;
  const products = await drawingProducts();
  const shop = products.map((p) => {
    const d = p.data;
    const base = `/shop/${p.id}/`;
    const by = orderByText(p);
    const ready = d.drawing!.subjects.filter((s) => s.source === 'static');
    const made = d.drawing!.subjects.filter((s) => s.source !== 'static').map((s) => s.label.toLowerCase());
    return [
      `- [${d.name}](${abs(base)}): the product page. ${d.description}`,
      `  ${tierText(p)}, with US shipping included; every ornament is priced by the order's total count. Up to ${d.pricing!.maxDesigns} designs and ${d.pricing!.maxPerOrder} ornaments in one order; over ${d.pricing!.maxPerOrder}, write to help@robotlantern.com for a quote. US addresses only.${by ? ` Order by ${by} for Christmas.` : ''} A free remake or a refund if it arrives broken or doesn't match the preview.`,
      `  From a photo: ${made.join(' or ')}. Ready-made designs, which need no photo and no drawing: ${ready.map((s) => `${s.label} (${s.designs!.map((x) => x.label.toLowerCase()).join(', ')})`).join('; ')}.`,
      `- [Ordering with an AI assistant](${abs(`${base}ai/`)}): what an assistant can do for a customer, step by step, and what only the customer does.`,
      `- [Drawing spec (JSON)](${abs(`${base}drawing-spec.json`)}): the exact drawing we need if you make it yourself, with every rule our builder checks.`,
      `- [Product data (JSON)](${abs(`${base}product.json`)}): price tiers, colours with hex values, fonts, name-tag rules, limits, the order-by date, and each ready-made design with its id and picture.`,
    ].join('\n');
  }).join('\n');

  const body = `# Robot Lantern

> Robot Lantern (robotlantern.com) makes two-part 3D-printed stencil ornaments from a photo of a pet or a
> person, or from its own ready-made designs, and publishes essays, chats and builds. The ornaments are
> printed and shipped in the US by Slant 3D. A person always sees the ornament's preview and pays on
> Stripe's checkout page; we take no payment any other way.

## Shop

${shop}

## For AI assistants helping a customer

- Ready-made designs need no photo and no drawing. Pick one on the product page (or name it from
  product.json), then choose the colours and the tag.
- If you have an image model, you can make the drawing yourself: follow "Instructions for your
  assistant" on the AI page above (or the drawing spec). It skips our wait, and we never receive the
  photo. Hand the image over exactly as your image model made it; don't edit it with code. The customer
  uploads it under "I have my own drawing", and the page checks it.
- If you have no image model, don't draw it with code or SVG. The customer adds their photo on the
  product page instead, and our drawing service (OpenAI's image model) makes it. It gives up to three
  tries per photo, and it can be busy.
- Only use a photo the customer has the right to use. A photo of a person needs that person's OK, and a
  child's needs a parent's or guardian's.
- No logos, brand marks, cartoon characters or text in the drawing. The name goes on the tag.
- The customer must see the preview and pay on Stripe's checkout page themselves, or approve the payment
  in their own wallet. Don't enter card details for them.

## More

- [Thoughts](${abs('/thoughts/')}): essays written with AI models, each showing who wrote which words.
- [Chats](${abs('/chats/')}): real conversations with AI chat apps.
- [Builds](${abs('/builds/')}): things to use in the browser.

## Optional

- [Privacy](${abs('/privacy/')}): what happens to photos and drawings, and when they're deleted.
- [Terms](${abs('/terms/')})
- [Shipping](${abs('/shipping/')})
- [Returns and refunds](${abs('/returns/')})
`;
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
