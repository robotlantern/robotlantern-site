# Orders for photo products

The flow for anything made from a customer's photo. It's built once, as modules joined by the contracts below,
and each product adds a product file, a preview module and a recipe. **The stencil ornament is the first, and
the only one at launch** (NOW.md, decisions 16–25). How it runs day to day, what's in the cloud and how RJ hears
about orders are in [PRODUCTION.md](PRODUCTION.md).

Built and tested in Stripe's sandbox (2026-11-13): order intake at `/api/orders` in the shop Worker on the
`shop-orders-test` KV namespace, the webhook's paid step, and `tools/orders/queue.py`. The rest of this page is
what NOW.md steps 7, 9 and 10 build, in parallel, against these contracts. If a contract has to change, change it
here first and say so in NOW.md's log.

## The flow (stencil ornament)

1. **Photo.** On `/shop/cutout-ornament/`, the browser turns the photo upright and the customer crops it square
   on the head. The browser re-encodes the crop as a 1024 × 1024 JPEG. That drops the camera's hidden
   details, GPS included. Nothing has left the phone yet.
2. **Drawing.** "Make my drawing" sends that JPEG to the Worker (`POST /api/drawings`). The Worker checks the
   caps, keeps the photo in KV for two days, and asks OpenAI's GPT Image to redraw it as a red-on-white stencil
   using the product's brief. It keeps the drawing and returns it. "Try again" makes another, up to three per
   photo. A drawing takes roughly half a minute to a minute, so the page shows that it's working.
3. **Preview and choices.** The browser draws the ornament from the drawing in the customer's colours, with
   the name tag if they want one (see "The page"). The red in the drawing only marks what is stencil. Any two
   of Slant's colours can be chosen afterwards without a new drawing.
4. **Order.** The page sends `design.json` (`POST /api/orders`), uploads `preview.jpg` (the picture the
   customer approved), and asks for checkout. Stripe's page takes the payment, the address and the tax.
5. **Paid.** Stripe's webhook marks the order paid. The Worker keeps its photo, drawing and preview with no
   expiry, and adds it to the queue.
6. **Made.** The `rl-orders` routine (PRODUCTION.md) does these in order:
   - builds both STLs from the drawing with the order's choices,
   - checks them, and compares the proof with `preview.jpg`,
   - uploads them to Slant and gets a quote (both free),
   - asks the Worker to draft the Slant order,
   - emails RJ.

   RJ processes the draft in Slant's dashboard, which is when Slant charges. Slant prints and ships.
7. **Shipped and purged.** `rl-daily` follows the Slant order to "shipped" and drafts the customer's shipping
   email for RJ to send. It deletes the photo and everything made from it 60 days later (decision 6).

No order reaches Slant until it has passed the checks and RJ has processed it.

## Modules

| Module | Lives in | Job |
| --- | --- | --- |
| Product file | `products/cutout-ornament/shop.json` | Price, options and what they add, photo needs, drawing model and brief, weekly cap, Stripe IDs |
| Briefs | `products/cutout-ornament/briefs/pet.md`, `person.md` | The GPT Image prompt for each subject. Bundled into the Worker at deploy, like the catalog |
| The page | `src/pages/shop/[slug].astro`, `src/scripts/shop/` | Photo, crop, drawing, preview, choices, order, thank-you page |
| Ornament preview | `src/scripts/shop/stencil-ornament.js` | Draws the ornament from a drawing (below) |
| Fonts | `public/shop/fonts/` | The five stencil fonts (OFL), for the page and the builder alike |
| Worker | `shop-worker/` | Drawings, orders, checkout, webhook, queue, Slant drafts |
| Recipe | `tools/ornament/` | Drawing and choices → `base.stl`, `stencil.stl`, `proof.png`, `build.json` |
| Order run | `tools/orders/` | The routine's scripts: list, build, check, Slant, state, purge |

Other photo products keep the earlier plan's modules (a tone preview, a subject picker, lithophane-maker's
recipes, `self` fulfilment). They come back when their lines open, and docs/LOG.md has that plan.

## Contracts

### The product file

`products/cutout-ornament/shop.json` has the fields in docs/SHOP.md, plus:

```json
{
  "fulfillment": "slant",
  "photo": { "via": "drawing", "crop": "square", "edge": 1024 },
  "drawing": { "model": "<GPT Image model>", "quality": "high", "size": "1024x1024",
               "subjects": ["pet"], "triesPerPhoto": 3 },
  "options": [
    { "id": "base", "label": "Base", "choices": [ { "id": "white", "label": "White", "slant": "<filament id>" } ] },
    { "id": "stencil", "label": "Stencil", "choices": [ "…the same colours…" ] },
    { "id": "tag", "label": "Name tag", "choices": [ { "id": "yes", "label": "Yes" }, { "id": "no", "label": "No" } ] },
    { "id": "font", "label": "Font", "choices": [ { "id": "allerta", "label": "Allerta Stencil" } ] }
  ],
  "text": { "max": 16, "allowed": "A-Za-z0-9 '&.-" },
  "weeklyCap": 25,
  "orderBy": "2026-12-10"
}
```

- **Colours:** Slant's PLAs, from the picker's `colours.json` (scratch folder), each with Slant's filament id,
  its hex value and whether it's offered. Clear is off, because the tree shows through it.
- **`drawing.subjects`:** add `"person"` when decision 25 says yes. `model` and `quality` live here, so a cheaper
  model is a one-line change.
- **Price** comes from the product file, which is bundled into the Worker at deploy. The browser shows a price
  but never sets one.

### Drawings API (the Worker)

- **`POST /api/drawings`**: the body is the 1024 × 1024 JPEG (`image/jpeg`, at most 4 MB) with the header
  `X-Subject: pet` (or `person` once allowed). The answer is `201 {"id", "n": 1, "left": 2, "image"}`, where
  `image` is the drawing as base64 PNG and `id` is 12 characters from the order-ID alphabet.
- **`POST /api/drawings/<id>/again`**: the next try with the same photo, until `left` is 0.
- **Refusals:**
  - `429 {"error", "retryAfter"}` when the visitor's or the day's cap is reached.
  - `503` when drawings are switched off.
  - `502` when OpenAI fails. A failed call doesn't use up a try.
- **Storage:** KV `drawing:<id>` (the record: subject, tries, created), `file:drawing:<id>/photo.jpg` and
  `file:drawing:<id>/<n>.png`, all expiring after two days unless an order is paid.
- **The OpenAI call:** images edit, `model`/`quality`/`size` from the product file, the brief for the subject,
  one image, PNG out. Send a `user` value: the visitor's daily hash (below).
- **CPU:** the free plan gives a request 10 ms of CPU. Build the multipart body from KV bytes without decoding the
  image, and don't `JSON.parse` OpenAI's answer of a megabyte or more in the Worker if that busts the limit.
  Instead, stream it into KV and to the page as it comes, and let the page and the routine take the PNG out.
  If neither fits, stop and tell RJ: Workers Paid is a charge (CHARGES.md).
- **Caps** (decision 21; numbers in `shop-worker/limits.json`, so changing one means a deploy):
  - `triesPerPhoto` (3).
  - `perVisitorPerDay` (6), counted under a SHA-256 of the IP address and that day's salt. It's kept one
    day and never logged.
  - `dollarsPerDay` (10), counted as `costPerDrawing` × drawings. `costPerDrawing` is set from OpenAI's price
    for the model and quality, rounded up.
  - KV counters can overshoot by a few in a burst. The OpenAI balance is the hard cap behind them.
- **Switches:** KV `switch:drawings` and `switch:orders` set to `off` stop new drawings or new orders at once.
  The page then says to come back later.

### Orders

- **`POST /api/orders`** with `design.json`:

  ```json
  { "product": "cutout-ornament",
    "drawing": { "id": "k3v9q0m2x7ab", "n": 2 },
    "options": { "base": "white", "stencil": "red", "tag": "yes", "font": "allerta" },
    "text": "Tucker",
    "price": 29,
    "version": "<the page's build id>" }
  ```

  The Worker checks that the drawing exists and try `n` was made, and that each option is one of the product
  file's choices. Base and stencil can't be the same colour. The text has to fit `text`: it's needed when the
  tag is `yes` and dropped when it's `no`. The only file the order takes is `preview.jpg`. The photo and the
  drawing come from the drawing record.
- `PUT /api/orders/<id>/preview.jpg`, then `POST /api/orders/<id>/checkout`, as they work now.
- **Paid** (webhook): `photo.jpg`, the chosen drawing as `drawing.png`, and `preview.jpg` are written again under
  `file:<id>/` with no expiry, and the order goes to `paid` and into the queue.
- **Order record** (KV `order:<id>`): as now, plus `state`, `history` (state, when, note) and `slant` (below).
  It never holds the address or email. Those stay in Stripe.

### Queue endpoints (the routine's; the queue token)

| Call | Does |
| --- | --- |
| `GET /api/queue` | Orders not yet `shipped`, `cancelled` or `purged`: id, product, state, paid date |
| `GET /api/orders/<id>` | The record (exists) |
| `GET /api/orders/<id>/<file>` | `design.json`, `photo.jpg`, `drawing.png`, `preview.jpg`, or an `out/` file (exists) |
| `PUT /api/orders/<id>/out/<name>` | Stores `proof.png` (at most 5 MB), `base.stl`, `stencil.stl` (at most 25 MB), `build.json` |
| `PATCH /api/orders/<id>` | `{"state", "note"}`, only along the arrows in "States" below |
| `POST /api/orders/<id>/slant` | Drafts the Slant order (below) |
| `GET /api/orders/<id>/contact` | The customer's name and email from Stripe, only for a shipping email, and only once shipped |
| `GET /api/orders/<id>/link/proof.png` | A signed link to the proof that lasts seven days, for RJ's email |
| `GET /api/stats` | Drawings and estimated dollars today and this month, orders this week, the switches |
| `DELETE /api/orders/<id>` | Purge (exists). Now also the `out/` files and the drawing's files. The record stays, without the design's photo or drawing references |

**States:** `paid → built → drafted → processed → shipped → purged`. `needs-rj` can come from any state before
`processed`, and goes back to `built` once RJ has sorted it out. `cancelled` follows a full refund.

### Slant drafts (the Worker)

`POST /api/orders/<id>/slant` with
`{"items": [{"fileId", "filamentId", "part": "base"}, {"fileId", "filamentId", "part": "stencil"}]}`.

1. The order must be `built`. If it already has `slant.state`, the call returns what's recorded and does
   nothing else, so a retry can never make a second draft.
2. The Worker writes `slant.state = "drafting"`, reads the shipping name and address from the order's Checkout
   Session, and drafts at Slant: the two print items, `orders@robotlantern.com` as the email, and
   `SLANT_PLATFORM_ID`.
3. It records `slant: {orderId, printingCost, deliveryCost, drafted}`, moves the order to `drafted`, and
   returns that.
4. **In the sandbox, it never calls Slant.** It returns the request it would have sent, marked `dryRun`.
   Slant can't cancel or delete a draft (CHARGES.md).

Nothing in our code processes a Slant order. Only RJ does, in Slant's dashboard.

### The recipe (`tools/ornament/`)

`python3 tools/ornament/make.py <order folder>` reads `design.json` and `drawing.png` and writes `out/`:

- `base.stl` and `stencil.stl`, posed for printing: the base face up, the stencil face down with its pegs up.
- `proof.png`, the builder's preview in the order's colours, with the tag.
- `build.json`, the builder's report and the checks: the stencil is one piece, both meshes are watertight, no
  bridge is over 3 mm, the tag text fits, and no warnings.

It exits non-zero if a check fails. The same folder always gives the same files. The builder may drop specks,
thicken thin lines and add bridges, and the proof shows that. It never adds or removes a feature the customer
saw.

`tools/ornament/slant.py upload|quote <stl> --filament <id>` talks to Slant directly with `SLANT_API_KEY`,
or with no key where the cloud's proxy adds it (PRODUCTION.md). It has no draft or process command.

### The page

- Photo in, turned upright, then a square crop with drag and pinch. The hint is: fill the square with the
  head.
- One button makes the drawing, with a short wait message. The page then shows the tries as thumbnails, says
  how many are left, and lets the customer pick one.
- **The preview** (`stencil-ornament.js`) copies the builder's geometry, so the page and the print agree:
  - Ink is any pixel more than 120 (RGB distance) from white.
  - Crop to the ink with padding, and scale so the ink is 80 mm wide.
  - The silhouette is the ink with its holes filled. The base is the silhouette grown by the 2 mm rim, in the
    base colour.
  - The stencil is the ink, in the stencil colour.
  - The 10 mm ring, with its 4 mm hole, sits at the top on the outline's centre line.
  - The tag is 17 mm tall and 0.8 of the art's width (50–72 mm), with the text cut through in the base colour.
    The text is fitted the way the picker and `nametag.fit` do it.
  - A line under the preview says small details are tidied for printing.
- The picker comes from the scratch folder (`picker/`): colours, suggested pairs, swap, the close-colours note,
  the name tag and the five fonts. The fonts load from `public/shop/fonts/`, never Google: the privacy page
  promises no requests to other sites.
- Order: the price comes from the product file. The page renders `preview.jpg` (1024 px) from the canvas,
  then sends the order, uploads the preview and goes to checkout. If checkout reports a missing file, the page
  sends it again and retries.
- Nothing is stored in the browser. Tap targets are at least 44 px, it works at 375 px, and the selection
  ring doesn't rely on colour alone.

## Choices made, and why

- **The drawing is made before payment**, because the customer needs to see their ornament to buy it. The caps
  and the OpenAI balance limit what previews from people who don't buy can cost.
- **One red-on-white drawing serves every colour pair.** The ink only says what is stencil, and the page and
  the builder recolour it.
- **The Worker drafts at Slant, not the routine.** The address goes from Stripe to Slant inside Cloudflare, so
  the agent never sees it. It's also the single writer, which makes the "never a second draft" check
  reliable.
- **No geometry in the Worker.** Meshing needs Python libraries and more memory than a Worker has, so the
  routine does it in the cloud.
- **Uploads stream into KV, never parsed** (10 ms of CPU on the free plan), as before.
- **The API is at `robotlantern.com/api/` after cutover**, a route to the `shop` Worker. Until then it's
  `shop.robotlantern.workers.dev`, which allows the preview hosts by CORS. The host sets the mode:
  robotlantern.com is live, workers.dev is the sandbox.
- **Abuse:** sizes, types and caps are checked, and unpaid files expire. There's no CAPTCHA, which would load
  another site's script. Revisit if someone abuses it.

## Privacy and retention (decision 6)

- Photos are personal data, often of children. The people and services that see them:
  - OpenAI, which makes the drawing.
  - RJ, and the agents that run his orders. Anthropic processes what an agent looks at.
  - Slant, which sees the STLs and never the photo.
- Unpaid photos and drawings expire after two days. Photos and everything made from them are deleted from KV
  60 days after the order ships or is cancelled. The order record, without photos, stays for seven years.
- OpenAI keeps API inputs and outputs for up to 30 days to monitor abuse, and doesn't train on them by default
  (check its current policy when writing the privacy page).
- The privacy page says all this (NOW.md step 11). Keep it true when anything here changes.
- Logs carry IDs, never order contents. Cloudflare shows us the Worker's logs for three days.

## Testing

- `python3 tools/orders/test_order.py` places a photo order end to end in the sandbox. It uses a drawn test
  picture, never anyone's photo, and refuses a live key. Step 9 extends it to drawings, with OpenAI stubbed
  unless `--real-drawing` is given. A real drawing costs money and counts against the cap.
- Stripe's sandbox and test cards for every checkout, and the sandbox KV namespace for test orders.
- Slant: upload and quote freely. Drafts only as dry runs in tests.
- The recipe: a drawing made for the test, in Git; family drawings only locally.
