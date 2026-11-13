# Orders for photo products

Planned 2026-11-10 (NOW.md). RJ took the plan's choices as recommended the same day; NOW.md numbers
them, and this page cites those numbers. Built so far (2026-11-13, sandbox only): order intake at
`/api/orders` in the shop Worker, on the `shop-orders-test` KV namespace, and `tools/orders/queue.py`.
The configurator, the subject picker and the live namespace are still to come.

Four product lines are made from a customer's photo: the lithophane ornament and lamp, custom cutouts,
pop-out photos and the stereographic projector (`products/`). Every one is ordered the same way, so the
order flow is built once, as modules joined by file contracts. A new photo product adds a product file,
a preview module and a recipe. Nothing else changes.

## The flow

1. **Choose a product** on `/shop/`, which opens its page, `/shop/<slug>/`.
2. **Add a photo.** The browser turns it upright, shrinks it to at most 4,000 px on the long edge and
   re-encodes it as JPEG. That drops its metadata, GPS included, before anything is sent.
3. **Shape it.** Crop to the product's shape, tap the subject where the product needs one, and pick the
   options. The preview redraws as you go. Nothing has left the phone yet.
4. **Order.** The button sends the photo and the choices to our Worker, which keeps them and opens
   Stripe's hosted checkout for that one order. Stripe's receipt is the customer's confirmation, and the
   thank-you page says what happens next.
5. **RJ makes it.** Paid orders are pulled to Sarcean, where the product's recipe builds the print files
   and a proof. RJ looks at both, then prints, cuts, assembles and ships. If a photo won't make a good
   one, he emails the customer to swap it, or refunds in full (NOW.md decision 4).

No order reaches a printer or a print service until RJ has looked at it. That's on purpose for launch.
Automation comes once enough orders show which manual steps hurt (lithophane-maker's `docs/REPORT.md`,
"From Sarcean to fully automated").

## Modules

| Module | Lives in | Job | Used by |
| --- | --- | --- | --- |
| Product file | `products/<slug>/shop.json` | Price, options and what they add, photo needs, preview and recipe names, fulfillment, weekly cap | all |
| Configurator | `src/pages/shop/[slug].astro`, `src/scripts/shop/` | Photo, crop, options, preview, order button, thank-you page | all |
| Tone preview | `src/scripts/shop/` | How the lithophane looks lit: the engine's tone curve and filament optics, ported to JavaScript | ornament, lamp |
| Subject picker | `src/scripts/shop/`, model under `public/shop/` | Tap to select the subject, tap again to add or remove; a lasso where the model can't run | cutouts, pop-outs, projector |
| Product previews | `src/scripts/shop/` | One small drawing module per product | one each |
| Order intake | `shop-worker/`, `/api/orders` | Checks an order against the product files, stores it, creates its Checkout Session | all |
| Payment webhook | `shop-worker/`, `/stripe` (exists) | Marks the order paid and keeps its files | all |
| Order queue | `tools/orders/` | `pull`, `list`, `make`, `ship`, `purge` | all |
| Recipes | `~/work/lab/lithophane-maker` | Order folder in; print files, sticker and cut files, proof and print sheet out | one each |

## Contracts

### The product file

A photo product's `shop.json` has the fields in docs/SHOP.md, plus:

```json
{
  "fulfillment": "self",
  "photo": { "minEdge": 1200, "crop": "circle", "subject": false, "count": 1 },
  "preview": "lithophane-bulb",
  "recipe": "ornament",
  "options": [
    { "id": "cap", "label": "Cap", "choices": [
      { "id": "gold", "label": "Gold" },
      { "id": "silver", "label": "Silver", "add": 0 }
    ] }
  ],
  "weeklyCap": 10,
  "orderBy": null
}
```

- **`photo`:** the smallest long edge in pixels, the crop shape (`circle`, `rect:<w>x<h>`, `free`),
  whether a subject is picked, and how many photos one order takes (a lamp's tiles).
- **`preview`, `recipe`:** module names, for the configurator and for lithophane-maker.
- **`options`:** any number. `add` is what a choice adds to the price, in dollars. A choice can name its
  filament or part for the recipe.
- **`weeklyCap`:** how many RJ can make in a week. Past it, the page says when ordering reopens.
- **`orderBy`:** for seasonal products, the last day to order for the holiday, from the handling time
  and USPS's holiday dates.

### The order bundle

What the browser sends, and what the Worker keeps under the order's ID:

- `design.json`: the product, options, crop, subject taps, the price the page showed, and the
  configurator's version;
- `photo-1.jpg` (and `photo-2.jpg` and so on, for tiles);
- `mask-1.png`, where a subject was picked;
- `preview.jpg`: the picture the customer approved.

### The order folder

`.private/orders/<YYYY-MM-DD>-<id>/` on Sarcean, git-ignored:

- `order.json`: the Stripe Checkout Session ID, test or live, the product, options, amount paid, status
  and dates. It holds no address. The address stays in Stripe, and the queue shows it only while a label
  is being made.
- the bundle's files;
- `out/`, from the recipe.

### Recipes

`<recipe> <order folder>` writes `out/`:

- the parts (STL or 3MF), posed for printing;
- `sticker.png` and `cut.svg` at the same scale, for Print Then Cut (cutouts, pop-outs);
- `print.pdf`, the background print (pop-outs);
- `proof.png`, what the finished piece should look like, to compare with the customer's `preview.jpg`;
- `sheet.md`: filaments, settings, time and grams, the parts list, assembly.

The same folder always gives the same files. The configurator and the recipe share the tone curve, the
filament optics and the customer's mask, so what the customer approved is what gets made. A recipe may
smooth an outline or drop specks too small to print. It never changes what's included, and its proof
shows any cleanup.

The recipes live in lithophane-maker, beside the engine they call. It already has the forms, the tone
curve, background removal (IS-Net), outlines from a mask, three product recipes, slicing estimates and
Slant quotes.

## Choices made in this plan, and why

- **The Worker builds Checkout Sessions; photo products don't use Payment Links.** Each order carries its
  own photo and choices, options change the price, and a lamp order can carry several photos. Payment
  Links fit none of that. They stay for fixed products.
- **Prices come from the product files**, bundled into the Worker when it's deployed. The browser shows a
  price, but never sets one.
- **Uploads go to Workers KV on the free plan** (NOW.md decision 5). Nothing on the free plan can bill.
  Values can be up to 25 MiB, with 1 GB in all and 1,000 writes a day, which is far more than launch
  needs. Unpaid uploads expire after two days on their own. R2 would need a card on file
  (docs/CHARGES.md).
- **The Worker streams photos straight into KV.** On the free plan a request gets 10 ms of CPU. Waiting
  on KV doesn't count, so uploads are raw `PUT`s, one file per request, and never parsed forms. An order
  is one small `POST`, then the uploads, then a `POST` that checks the files are all there and returns
  Stripe's checkout URL.
- **No geometry in the Worker.** A job peaks at 1–2.4 GB against a Worker's 128 MB, and the meshing
  libraries don't run there (lithophane-maker's report). Recipes run on Sarcean.
- **The subject picker runs in the browser,** so a photo leaves the phone only when someone orders, and
  there's no server to pay for. The candidates are SlimSAM on ONNX Runtime Web (Apache 2.0) and
  MediaPipe's interactive segmenter (check its model's licence). The rules: self-hosted, because the
  privacy page promises no requests to other sites; at most 25 MiB a file; loaded only at the subject
  step; usable on a three-year-old phone. Not usable: BRIA's RMBG (non-commercial licence) and
  @imgly/background-removal (AGPL).
- **The API is at `robotlantern.com/api/` after cutover**, a route to the `shop` Worker, so pages talk
  only to their own site. Until then it's `shop.robotlantern.workers.dev`, which allows the preview hosts
  by CORS.
- **Capacity:** a count per product per week in KV, checked against `weeklyCap`.
- **Abuse:** sizes and file types are checked, and unpaid uploads expire. There's no CAPTCHA, which would
  load another site's script. Revisit if anyone abuses it.

## Fulfillment

- **`self`**, every photo product at launch (NOW.md decision 3). Prints go through 3d-modeling's print flow
  (`docs/print-help.md` there), each recorded in printdb with the order ID. Photos and stickers come off
  RJ's printer and are cut on the Cricut. RJ ships them. The listing promises a handling time he can
  keep while working in fits and starts.
- **`slant`**, later and per product, after one paid test order on RJ's go. The queue uploads the
  recipe's STL, quotes it, and creates the Slant draft only for a real, checked order. RJ processes it
  in Slant's dashboard, which is when Slant charges. **A Slant draft can't be cancelled or deleted, so
  nothing ever drafts in a test.** The code has a dry run that builds the request and stops, and the queue
  records "order → Slant draft" before drafting, so a retry can't make a second one. Slant ships parts
  and components loose and does no assembly, so only a product the customer can put together goes there.
- **`gelato`**: fixed products, as now (docs/SHOP.md).

## Stripe

- Sandbox first: the Worker uses `STRIPE_SECRET_KEY_TEST`, as it does now.
- Live: a restricted key RJ creates, allowed to write Checkout Sessions and to read their line items and
  products (the build session confirms the exact set). It replaces the read-only key planned in
  docs/SHOP.md, "Launch".
- Each session has US shipping addresses only, the product's flat shipping, Stripe Tax on with the
  product's tax code, and the order ID as `client_reference_id` and in `metadata`.
- Turn on Stripe's email receipts (free), and the payment email to RJ, which is how he hears of an order.
- `python3 tools/orders/queue.py pull` reads completed sessions with the agents' Stripe key, then fetches
  each order's files from the Worker with a token of its own.

## Privacy and retention (NOW.md decision 6)

- Photos are personal data, often of children. Only RJ, and the agents working his queue, open them.
- Unpaid uploads expire after two days. Photos and everything made from them (masks, STLs, stickers) are
  deleted from KV and from Sarcean 60 days after the order ships (`queue.py purge`). Order records without
  photos stay seven years, for tax.
- They never go in Git, never into marketing without the customer's written OK, and nowhere except
  Slant, which gets the STL for a product it makes.
- The customer confirms they have the right to use the photo. RJ may refuse an order (someone else's
  artwork, a trademark, anything unlawful) and refund it.
- The privacy page and the terms say all this (NOW.md, step 12). The privacy page also says the following,
  so keep it true: a cancelled order's photos go 60 days after it's cancelled, and a photo emailed in goes
  from the mailbox with the rest; order pages save nothing in the browser and load nothing from other
  sites; Cloudflare shows us the order Worker's logs for three days, so the Worker logs IDs, never order
  contents; Slant gets only the STL and the name and address to ship to (put orders@ in its email field);
  and when an agent looks at a photo, Anthropic or OpenAI processes it.

## Testing

- `python3 tools/orders/test_order.py` places a photo order end to end in the sandbox: it uploads a drawn
  test picture (never anyone's photo), checks the browser's price is ignored and unpaid files expire in two
  days, pays with the test card, checks the webhook (and a resend, and a bad signature), then pulls, lists
  and purges the order. It refuses a live key. Passed in full 2026-11-13. Each run uses about 20 of KV's
  1,000 free writes a day.
- Workers KV can cache a "not found" for up to a minute, so the configurator resends a missing file and
  retries checkout rather than failing.
- Stripe's sandbox and test cards for every checkout, and a separate KV namespace for test orders.
- Recipes run on fixture photos (lithophane-maker `fixtures/photos/`, never committed).
- Slant: dry runs only. Gelato: drafts only, as now.

## Later

- Slant from the queue, with its signed webhook for shipping updates.
- Shipping emails with tracking. A label service may email tracking to the customer (check when choosing
  one). Our own email waits for Cloudflare Email Routing after cutover.
- Proofs the customer approves, if refunds show they're needed: authorize at checkout, capture on
  approval. Card authorizations last about seven days (check before relying on it), which is tight when
  working in fits and starts.
- A queue Samwise drains, then the engine in Cloudflare Containers (lithophane-maker's report, phases 2
  and 3).
