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
   as the subject's crop hint says (the head, for a pet). The browser re-encodes the crop as a 1024 × 1024 JPEG. That drops the camera's hidden
   details, GPS included. Nothing has left the phone yet.
2. **Drawing.** "Make my drawing" sends that JPEG to the Worker (`POST /api/drawings`). The Worker checks the
   caps, keeps the photo in KV for two days, and asks OpenAI's GPT Image to redraw it as a red-on-white stencil
   using the product's brief. It keeps the drawing and returns it. "Try again" makes another, up to three per
   photo. A drawing takes roughly half a minute to a minute, so the page shows that it's working.

   **Or the customer's own drawing** (decision 28). "I have my own drawing" takes an image the customer, or
   their AI assistant, made to our drawing spec (`/shop/cutout-ornament/drawing-spec.json`). The browser checks
   it (see "Own drawings"), squares it to 1024 × 1024, makes it exactly two colours and sends it
   (`POST /api/drawings` with `X-Source: upload`). No photo is sent and OpenAI isn't called. The rest of the
   flow is the same.
3. **Preview and choices.** The browser draws the ornament from the drawing in the customer's colours, with
   the name tag if they want one (see "The page"). The red in the drawing only marks what is stencil. Any two
   of Slant's colours can be chosen afterwards without a new drawing.
4. **Order.** An order holds one or more designs, each with a quantity (decision 26); "add another design"
   repeats steps 1–3. The page sends the designs (`POST /api/orders`), uploads each `preview.jpg` (the picture
   the customer approved), and asks for checkout. Stripe's page takes the payment, the address and the tax.
5. **Paid.** Stripe's webhook marks the order paid. The Worker keeps its photo, drawing and preview with no
   expiry, and adds it to the queue.
6. **Made.** The `rl-orders` routine (PRODUCTION.md) does these in order:
   - builds both STLs for each design from its drawing and choices,
   - checks them, and compares the proof with `preview.jpg`,
   - uploads them to Slant and gets a quote (both free),
   - asks the Worker to draft one Slant order for all of it, shipped in one box,
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
| Fonts | `public/shop/fonts/` | The five stencil fonts (OFL), for the page and the builder alike: `allerta-stencil.ttf`, `saira-stencil-one.ttf`, `big-shoulders-stencil.ttf` (the variable font; use wght 800, opsz 72), `emblema-one.ttf`, `wallpoet.ttf`, each with its `OFL-<name>.txt`. Keys as in `nametag.py`: `allerta`, `saira`, `big-shoulders`, `emblema`, `wallpoet` |
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
  "drawing": { "model": "gpt-image-2.6-sunburst", "quality": "medium", "size": "1024x1024", "triesPerPhoto": 3,
               "subjects": [ { "id": "pet", "label": "Pet", "brief": "briefs/pet.md",
                               "crop": "Fit your pet's head and shoulders in the square" } ] },
  "pricing": { "tiers": [ { "from": 1, "each": 29 } ], "maxPerOrder": 50, "maxDesigns": 12 },
  "options": [
    { "id": "base", "label": "Base", "choices": [ { "id": "white", "label": "White", "slant": "<filament id>" } ] },
    { "id": "stencil", "label": "Stencil", "choices": [ "…the same colours…" ] },
    { "id": "tag", "label": "Name tag", "choices": [ { "id": "yes", "label": "Yes" }, { "id": "no", "label": "No" } ] },
    { "id": "font", "label": "Font", "choices": [ { "id": "allerta", "label": "Allerta Stencil" } ] }
  ],
  "text": { "max": 16, "allowed": "A-Za-z0-9 '&.,!?-", "minTagWidth": 64 },
  "weeklyCap": 25,
  "orderBy": "2026-12-10"
}
```

- **Colours:** Slant's PLAs, from the picker's `colours.json` (scratch folder), each with Slant's filament id,
  its hex value and whether it's offered. Clear is off, because the tree shows through it.
- **`drawing.subjects`** (decision 26): each subject is data, with its brief, label and crop hint. Adding `person`
  (decision 25) or `place` (a church, a school, a childhood home) is a brief and an entry here, not code. Nothing
  in the Worker, page or routine names a subject. `model` and `quality` live here too, so a cheaper model is a
  one-line change. A subject may set `"cropMode": "fit"` (the whole subject in the square, letterboxed in white)
  instead of the default `"fill"` (decision 27).
- **Ready-made subjects** (decision 30). A subject with `"source": "static"` has no brief, crop hint or tries. It
  lists designs that RJ drew and checked once, so an order from it makes no drawing:
  ```json
  { "id": "gag", "label": "Gag gifts", "source": "static",
    "designs": [ { "id": "toilet", "label": "Toilet", "drawing": "static/gag-toilet-1.png",
                   "sha256": "<hex of the PNG>", "text": "Never Forget", "font": "allerta",
                   "alt": "A toilet with its lid up" } ] }
  ```
  A subject's `source` is `made` when missing. `drawing` is a path under `products/cutout-ornament/`: a
  1024 × 1024 two-colour PNG that passed `make.py` with `text` in `font`. The file is public, because the page
  and `product.json` show it. A published drawing is never edited: a redraw is a new file name (`-2.png`), and
  `sha256` pins it. The page shows a ready-made subject's designs as a gallery in place of the photo step, with
  `text` as the tag's starting text.
- **Text:** 16 characters is a ceiling, not a promise. The text must also fit the tag in the chosen font (text
  at least 5 mm tall), so the page runs the builder's own fit function and offers only the fonts where the text
  fits. The tag is at least `minTagWidth` mm wide, however narrow the art. A ready-made design's `font` is the one
  its `text` was checked in (decisions 27 and 30).
- **`pricing`** (decision 26): each ornament in an order is priced by the tier its order's total count falls
  in, and shipping is included. `maxPerOrder` and `maxDesigns` cap an order. Step 19 sets the numbers; the
  values above are placeholders.
  - `pricing.modifiers` (decision 29): a list, empty at launch. Each design is priced on its own:
    `price(design)` is the tier's `each` plus the sum of the modifiers that apply to it (for example
    `{"when": {"kind": "inlay"}, "add": 3}`, `{"when": {"source": "static"}, "add": 0}`, or a per-extra-colour
    amount). The Worker and the page use the same
    function, so a logo inlay's surcharge is data, not code.
- **Price** comes from the product file, which is bundled into the Worker at deploy. The browser shows a price
  but never sets one.

### Drawings API (the Worker)

- **`POST /api/drawings`**: the body is the 1024 × 1024 JPEG (`image/jpeg`, at most 4 MB) with the header
  `X-Subject: <subject id>`, which has to be one of the product file's subjects. The answer is `201 {"id", "n": 1, "left": 2, "image"}`, where
  `image` is the drawing as base64 PNG and `id` is 12 characters from the order-ID alphabet.
- **`POST /api/drawings/<id>/again`**: the next try with the same photo, until `left` is 0.
- **`source`** on a drawing is `made` (GPT Image) or `upload` (an own drawing). `vector` (a customer's SVG or
  PDF) and `trace` (a flat raster traced on the page) are reserved for logos (decision 29). Those are stored
  the same way, plus `art.svg` and `layers.png` (an indexed PNG: 0 is the background, 1–4 the logo's colours)
  beside `<n>.png`. `make.py` ignores files it doesn't need. `static` (a ready-made design, decision 30) never
  goes through `/api/drawings`: no OpenAI call, no photo, no drawing record and no cap count, and
  `switch:drawings` doesn't stop it.
- **`POST /api/drawings` with `X-Source: upload`** (decision 28): the body is the customer's own drawing, a
  1024 × 1024 PNG (`image/png`, at most 4 MB) that the page made from their file. The Worker reads only the PNG
  signature and IHDR (width, height), never decodes it, and stores it as try 1:
  `201 {"id", "n": 1, "left": 0, "source": "upload"}`, with no image echoed back. There's no OpenAI call, and it
  counts only against `uploadsPerVisitorPerDay`. `/again` refuses an upload with `409`. It's stored as
  `drawing:<id>` with `source: "upload"` and `file:drawing:<id>/1.png`, with no `photo.jpg`, and expires after
  two days unless paid.
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
  - `agentDrawingsPerDay` (10, decision 28): a request with a `Signature-Agent` header counts here, across
    all agents, instead of `perVisitorPerDay`. Agent browsers such as ChatGPT's share cloud IP addresses, so a
    per-IP count would shut them all out after six drawings. An unverified header can only move a request
    into this smaller pool, never past a cap.
  - `uploadsPerVisitorPerDay` (20): own-drawing uploads, counted like `perVisitorPerDay`.
  - Free-plan KV allows 1,000 writes a day across everything, and a drawing writes about five keys, so a busy
    day hits that before the dollar cap. `GET /api/stats` reports writes today, and `rl-daily` warns above 600.
  - KV counters can overshoot by a few in a burst. The OpenAI balance is the hard cap behind them.
- **Switches:** KV `switch:drawings` and `switch:orders` set to `off` stop new drawings or new orders at once.
  The page then says to come back later.

### Orders

- **`POST /api/orders`** with a list of designs (decision 26), each with a quantity:

  ```json
  { "product": "cutout-ornament",
    "designs": [
      { "drawing": { "id": "k3v9q0m2x7ab", "n": 2 },
        "options": { "base": "white", "stencil": "red", "tag": "yes", "font": "allerta" },
        "text": "Tucker", "quantity": 1 },
      { "drawing": { "id": "p8w2c4h6j1rt", "n": 1 },
        "options": { "base": "white", "stencil": "matte-black", "tag": "no", "font": "allerta" },
        "quantity": 12 } ],
    "price": 29,
    "version": "<the page's build id>" }
  ```

  `price` is the total the page showed. The Worker works it out again from `pricing` and refuses a mismatch.
  A design's `drawing` is `{"id", "n"}` (a made or uploaded drawing) or `{"static": "<subject>/<design>"}`, for
  example `{"static": "gag/toilet"}` (decision 30). For a ready-made design, the Worker checks that the pair is in
  the product file, reads and writes no drawing record, and puts `source: "static"` and the product file's
  `sha256` in `design.json`. Its `text` starts as the design's `text` and follows the same rule as any other.
  For each design, the Worker checks that the drawing exists and try `n` was made, and that each option is one
  of the product file's choices: each key in `options` must be an option id in the product file, and each
  value one of its choices, with no option id named in code (decision 29). Base and stencil can't be the same
  colour. The text has to fit `text`: it's
  needed when the tag is `yes` and dropped when it's `no`. It also checks `maxPerOrder` and `maxDesigns`.
  Designs are numbered `1`, `2`, … in list order.
- `PUT /api/orders/<id>/<k>/preview.jpg` for each design `k`, then `POST /api/orders/<id>/checkout`. Checkout
  has one line per design, with its quantity.
- **Paid** (webhook): for each design `k`, `design.json` (the design as above, plus `product` and the drawing's `source`),
  `photo.jpg` (made drawings only), the
  chosen drawing as `drawing.png`, and `preview.jpg` are written again under `file:<id>/<k>/` with no expiry. The
  order then goes to `paid` and into the queue. Each `file:<id>/<k>/` folder is exactly what
  `tools/ornament/make.py` reads.
- **Paid, ready-made designs** (decision 30): the webhook writes `design.json` and `preview.jpg` under
  `file:<id>/<k>/`, and no `photo.jpg` or `drawing.png`. The routine copies the drawing from its checkout of the
  repo (`products/cutout-ornament/<drawing>`) into the build folder as `drawing.png`, checks its SHA-256
  against the design's, and sends a mismatch to `needs-rj`. Then `make.py` runs as for any design. The routine
  skips the logo and character check on ready-made designs, because RJ looked at each drawing when he added it,
  but keeps the proof-versus-preview comparison.
- **Order record** (KV `order:<id>`): as now, plus `state`, `history` (state, when, note) and `slant` (below).
  It never holds the address or email. Those stay in Stripe.

### Queue endpoints (the routine's; the queue token)

| Call | Does |
| --- | --- |
| `GET /api/queue` | Orders not yet `shipped`, `cancelled` or `purged`: id, product, state, paid date |
| `GET /api/orders/<id>` | The record (exists) |
| `GET /api/orders/<id>/<k>/<file>` | Design `k`'s `design.json`, `photo.jpg`, `drawing.png`, `preview.jpg`, or an `out/` file |
| `PUT /api/orders/<id>/<k>/out/<name>` | Stores design `k`'s `proof.png` (at most 5 MB), `build.json`, and each STL its `parts` list names (at most 25 MB each) |
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
`{"items": [{"design": 1, "part": "base", "fileId", "filamentId", "quantity"}, {"design": 1, "part": "stencil", …}, …]}`:
one item per part in each design's `build.json` `parts`, each with that design's quantity (decision 29). A
stencil design has two, the base and the stencil; other kinds will have more. The Worker checks that the items
match each design's parts list for list, and the order's quantities, rather than counting two a design.

1. The order must be `built`. If it already has `slant.state`, the call returns what's recorded and does
   nothing else, so a retry can never make a second draft.
2. The Worker writes `slant.state = "drafting"`, reads the shipping name and address from the order's Checkout
   Session, and drafts at Slant: all the print items, in one order and one box, `orders@robotlantern.com` as the email, and
   `SLANT_PLATFORM_ID`.
3. It records `slant: {orderId, printingCost, deliveryCost, drafted}`, moves the order to `drafted`, and
   returns that.
4. **In the sandbox, it never calls Slant.** It returns the request it would have sent, marked `dryRun`.
   Slant can't cancel or delete a draft (CHARGES.md).

Nothing in our code processes a Slant order. Only RJ does, in Slant's dashboard.

### The recipe (`tools/ornament/`)

`python3 tools/ornament/make.py <design folder>` (one per design: an order's `<k>/`) reads `design.json` and
`drawing.png` and writes `out/`:

- `base.stl` and `stencil.stl`, posed for printing: the base face up, the stencil face down with its pegs up.
- `proof.png`, the builder's preview in the order's colours, with the tag.
- `build.json`, the builder's report and the checks: the stencil is one piece, both meshes are watertight, no
  bridge is over 3 mm, the tag text fits (`nametag.tag_fit`), the base is within the size limit (`size_ok`),
  "white kept" is at least 0.8 (`white_kept`: the cut-out area in the proof ÷ that in the drawing, so the
  builder's tidying hasn't removed features the customer saw), and no warnings. It lists what Slant prints (decision 29):
  `"parts": [{"part": "base", "file": "base.stl", "colour": "white"}, {"part": "stencil", "file": "stencil.stl",
  "colour": "red"}]`. The routine uploads every listed file and never assumes two.

`design.json` has `kind`: `"stencil"`, the default when it's missing, or after launch `"inlay"` (a base with
pockets and loose insert pieces, for logos). `make.py` exits 2 on a kind it doesn't build.

It exits non-zero if a check fails. The same folder always gives the same files. The builder may drop specks,
thicken thin lines and add bridges, and the proof shows that. It never adds or removes a feature the customer
saw.

`tools/ornament/slant.py upload|quote <stl> --filament <id>` talks to Slant directly with `SLANT_API_KEY`,
or with no key where the cloud's proxy adds it (PRODUCTION.md). It has no draft or process command.

### The page

- Photo in, turned upright, then a square crop with drag and pinch. The hint is the subject's `crop` text from the
  product file. The page's wording comes from the subject's label, so no subject is named in code.
- One button makes the drawing, with a short wait message. The page then shows the tries as thumbnails, says
  how many are left, and lets the customer pick one.
- **The preview** (`stencil-ornament.js`) copies the builder's geometry, so the page and the print agree:
  - Ink is any pixel more than 120 (RGB distance) from white.
  - Crop to the ink with padding, and scale the ink to fit an 80 × 85 mm box (the builder's defaults).
  - The silhouette is the ink with its holes filled. The base is the silhouette grown by the 2 mm rim, in the
    base colour.
  - The stencil is the ink, in the stencil colour.
  - The 10 mm ring, with its 4 mm hole, sits at the top on the outline's centre line.
  - The tag is 17 mm tall and 0.8 of the art's width, held between 64 and 72 mm, with the text cut through in
    the base colour. The text is fitted as `nametag.tag_fit` does it (at least 5 mm tall in the chosen font).
  - A line under the preview says small details are tidied for printing.
  - The page runs the builder's drawing check (`tools/ornament/drawing.py`, `check_drawing`) on each try, made
    or uploaded, and doesn't offer a try that would fail it (an island too far to bridge, or "white kept" under
    0.8). It says why and suggests another try. So the customer never pays for a drawing the routine would
    refuse.
- The picker comes from the scratch folder (`picker/`): colours, suggested pairs, swap, the close-colours note,
  the name tag and the five fonts. The fonts load from `public/shop/fonts/`, never Google: the privacy page
  promises no requests to other sites.
- Quantity for each design, and "add another design" (up to `maxDesigns`). The order's total shows the tier
  price, and how much the next tier saves.
- Order: the price comes from the product file. The page renders `preview.jpg` (1024 px) from the canvas,
  then sends the order, uploads each design's preview and goes to checkout. If checkout reports a missing file, the page
  sends it again and retries.
- Nothing is stored in the browser. Tap targets are at least 44 px, it works at 375 px, and the selection
  ring doesn't rely on colour alone.
- **An agent can operate it** (decision 28):
  - two labelled file inputs, "Add a photo" and "I have my own drawing";
  - a crop that works without gestures (centred and filled by default, a zoom slider);
  - colours as labelled radio groups, the font as a `<select>`, and native, labelled controls for the tag,
    quantity, "add another design" and "Order";
  - drawing progress, tries left, upload-check results, tag fit and the total as text in an `aria-live`
    region;
  - the facts in the HTML: what it is, its size, the colours, the price tiers with shipping, US only, made to
    order, the order-by date and the remake promise;
  - `Product` and `Offer` JSON-LD, and `<link rel="alternate" type="application/json" href="product.json">`;
  - a line near the upload: "Using an AI assistant? Here's what it can do."

### Own drawings (decision 28)

An uploaded drawing goes through the same builder, so it meets the same spec. The page checks it before
sending, using the builder's own cleanup and bridge measurement from `tools/ornament/`, and says what's wrong
in words.

- **Refused:**
  - not PNG, JPEG or WebP;
  - not square (within 2%), under 1024 or over 4096 px, or over 4 MB;
  - transparent;
  - a photo or shaded art (more than 6% of pixels between ink and white);
  - fills the whole image (a frame, a background box, or a subject cut off at the edges), or one shape
    covers more than 80%;
  - no features (under 3% of the silhouette cut out);
  - more than one piece after the builder's cleanup, with an island the builder can't bridge, or "white kept"
    under 0.8 (both from `check_drawing`, as for a made drawing).
- **Warned, but allowed:**
  - art touching an edge;
  - more than six pieces to bridge;
  - ink that isn't red;
  - art under half the width.
- The page then squares it to 1024 × 1024 and maps every pixel more than 120 (RGB distance) from white to
  `#E01010`, and the rest to white. The preview is drawn from that, as for a made drawing.

The routine runs `make.py` as for any design, and a failed build goes to `needs-rj`. An uploaded design has
no `photo.jpg`, so the routine compares the proof with `preview.jpg` only. It also looks for logos,
characters, text and brand marks.

### Agents (decision 28)

- **Public and static, with no Worker:**
  - `/llms.txt`;
  - `/shop/cutout-ornament/ai/` ("Ordering with an AI assistant");
  - `/shop/cutout-ornament/drawing-spec.json`;
  - `/shop/cutout-ornament/product.json`, built from `shop.json`: subjects, colours with hex values, fonts,
    the tag rule, price tiers, limits and the order-by date, but never Stripe IDs, filament IDs or caps. It
    also lists each ready-made design (id, label, `alt`, the drawing's URL, suggested `text`), so an assistant
    can order one by naming it, and `llms.txt` says those need no photo or drawing (decision 30).
- **A person pays.** Money moves only on Stripe's hosted Checkout, paid by the customer or by their own
  wallet with their approval. We take no card details, payment tokens or credentials through our API.
- **A person sees the preview.** Checkout is reachable only from the page, after it has rendered and uploaded
  `preview.jpg`. After launch, `POST /api/orders` also returns a review link (`/shop/cutout-ornament/?order=<id>`)
  for agents that don't browse.
- **Agents aren't blocked:**
  - no CAPTCHA;
  - Cloudflare allows "dots, OpenAI";
  - agents get their own pool in "Caps";
  - `llms.txt` points them to bringing their own drawing.

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
- With an own drawing (decision 28), we never get the photo. The customer's assistant, and whoever runs it,
  sees it under their own terms.
- Unpaid photos and drawings expire after two days. Photos and everything made from them are deleted from KV
  60 days after the order ships or is cancelled, except `preview.jpg` and `build.json`. Those stay 180 days
  after shipping as evidence of what the customer approved, because a card dispute can come up to about 120
  days after delivery (decision 28). The order record, without photos, stays for seven years.
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
