# Now

_Last updated 2026-11-10._

## Start here

The new site is built on the `rebuild` branch and previewed at https://rl.rblt.io/
([docs/PREVIEW.md](docs/PREVIEW.md)), with a copy on Cloudflare at https://site.robotlantern.workers.dev.
robotlantern.com is still the old landing page. Design rules are in [docs/PAGES.md](docs/PAGES.md), the home
page in [docs/HOME.md](docs/HOME.md) and the brand in [docs/BRAND.md](docs/BRAND.md).

**The launch is now about four products made from a customer's photo** (RJ, 2026-11-10): lithophanes (an
ornament, and a lamp with slide-in photo tiles), a stereographic projector, pop-out photos and custom
cutouts. All four are ordered the same way, so the order flow is built once, as modules
([docs/ORDERS.md](docs/ORDERS.md)). Each product has a folder in `products/` ([docs/PRODUCTS.md](docs/PRODUCTS.md)),
and marketing follows [docs/MARKETING.md](docs/MARKETING.md). At launch RJ looks at every order, then makes
and ships it himself.

- `python3 tools/next.py` prints RJ's next steps; `python3 tools/products/board.py` shows each product's stage.
- To start an agent step, open a session here and say: "Read AGENTS.md and NOW.md, then do step N."
  Steps 9, 12 and 14 touch different files and can run at the same time.
- History before 2026-11-10 (the old road, task notes 1–20 and the log) is in [docs/LOG.md](docs/LOG.md).

### What changed while this was paused (checked 2026-11-10)

- **Git moved to Bilbo** in the LAN restructuring of 2026-10-28: the `bilbo` remote is now the primary.
  Pushing `rebuild` to `samwise` still publishes the preview, and the preview works.
- **The lithophane engine exists**: `~/work/lab/lithophane-maker` (2026-10-04) turns a photo into printable
  lithophanes (flat, curved, cylinder, globe), cuts them to a subject's outline, and has three product
  recipes, a test bench and a hosting report. Nothing from it has been printed. printdb lists only 25 g
  of white PLA; the four matte spools from early October aren't in it.
- **Photo orders were worked out once already**, for a photo jack-o'-lantern (memos of 2026-10-02 in
  `inbox/`). They hold Slant's API facts too: a Slant draft can't be cancelled or deleted, and processing
  an order is what charges. Both are folded into docs/ORDERS.md and docs/CHARGES.md.
- **The projector's reference files are CC BY-SA** (Thingiverse 2078413, by threonin). Prints can be
  sold, with credit.
- Shop work from October still stands: Stripe's sandbox, the order Worker and Stripe Tax
  ([docs/SHOP.md](docs/SHOP.md)), the Cloudflare copy, and the DNS records for cutover
  ([docs/HOSTING.md](docs/HOSTING.md)).

## Decisions (RJ, 2026-11-10)

RJ took all twelve as recommended on 2026-11-10. The docs cite them by number.

1. **Launch cut.** The site launches once the ornament can be ordered, plus cutouts if their prototype
   is ready in time. The lamp, pop-out photos and projector open as each prototype passes, aiming for all
   four by Black Friday, 2026-11-27. The other way is to hold launch until all four are ready.
2. **Merch waits.** The tee, mug, tote and blankets are parked until after launch.
3. **You make everything at first**, with Meltbot, your printer and the Cricut, and a weekly cap per
   product. A product moves to Slant only after one paid test order of it, on your go.
4. **Pay, then check, then make.** Customers pay at checkout. You look at every order before making it.
   If a photo won't work, you email the customer from help@ to swap it, or refund in full. There's no
   proof round by default.
5. **Uploads go to Cloudflare Workers KV on the free plan.** Nothing there can bill, and unpaid uploads
   delete themselves after two days.
6. **Photos are deleted 60 days after the order ships**, along with the files made from them. Order
   records without photos are kept seven years, as now. Customer photos never go into marketing without
   the customer's written OK.
7. **Ornaments are white at launch and for LED lights only.** Colours come after each one's test wedge.
   PLA softens at about 60 °C, and older incandescent bulbs can run hotter than that.
8. **The projector gets our own generator**, written from the maths rather than threonin's code, with
   credit to threonin's projector on the Credits page. You buy two or three small LEDs to try, once I've
   listed options and prices. None of Slant's lights is small enough.
9. **Lines that aren't ready show "coming soon"**, with an email link to signup@ ("tell me when it's
   ready"). There's no form, and nothing is stored on the site.
10. **Pictures are honest.** Listings show real prototypes, or renders marked as renders. Example photos
    are yours, family's with their OK, or AI-made stand-ins marked as such. No AI "lifestyle" pictures
    that redraw the product.
11. **The About rewrite and the style changes don't hold launch.** Do them when you can.
12. **Platforms:** Instagram, Facebook and Pinterest first, because personalised gifts sell from pictures
    and Pinterest is where people plan gifts. Change the list if you like.

## Road to launch

Steps in order. **RJ** steps are his; **Agent** steps are one session each. "After 6:" means the step
waits for step 6. Times are rough: agent time is wall-clock, RJ time is hands-on. Check a step off when
it's done.

Launching with the ornament takes about 8½ hours of agent time and 3–4 hours of RJ's, plus about 4
hours of printing. Cutouts add about 4 agent hours and 1 of RJ's. That's this week if the tax
registration is quick and the first ornament prints well; otherwise next week, still before Black
Friday. If the tax certificate is slow, the site can go live with the shop showing "coming soon" until
it arrives. Steps 21–29 bring in the other three products: about 9 more agent hours and 3 of RJ's.

### Accounts, tax and the domain

1. [x] **RJ** · The decisions above: taken as recommended (2026-11-10). *5 min*
2. [ ] **RJ** · Sales tax ([docs/SALES-TAX.md](docs/SALES-TAX.md)): check whether the LLC has a West
   Virginia Business Registration Certificate (MyTaxes). If it doesn't, get the EIN, then apply. Do this
   first: it's the step with outside waiting. *10 min to check; 1–2 h if both are needed*
3. [ ] **RJ** · Materials: are the four matte 1 kg spools (white, red, blue, black) on the shelf? Add
   them to printdb, or say they aren't there (every lithophane needs white). Say which inkjet printer,
   sticker paper and Cricut you have, and which lights are on your tree (mini LED, C7 or C9). *10 min*
4. [ ] **RJ** · Cloudflare: look at https://site.robotlantern.workers.dev; say yes or no to SPF and DMARC
   for mail ([docs/HOSTING.md](docs/HOSTING.md)); add robotlantern.com to Cloudflare (dashboard, free
   plan), or give the API token Zone and DNS edit for the change window. *15 min*
5. [ ] **Agent** · After 4: Enter the DNS records in Cloudflare and compare them with the old ones
   (docs/HOSTING.md, "Cutover"). *15 min*
6. [ ] **RJ** · After 5: Switch the nameservers at DomainRegistry.com to Cloudflare's. Changes can take up
   to a day to spread. *10 min*
7. [ ] **RJ** · After 2: Once the EIN arrives, change Stripe's business details to Robot Lantern LLC, and
   create the order Worker's restricted live key ([docs/ORDERS.md](docs/ORDERS.md), "Stripe"). *20 min*
8. [ ] **Agent** · After 2 and 7: Turn on West Virginia in Stripe Tax (live), with the registration's
   start date. *10 min*

### The order flow ([docs/ORDERS.md](docs/ORDERS.md))

9. [ ] **Agent** · After 1: Order intake in Stripe's sandbox: the photo products' `shop.json` files,
   `/api/orders` in the shop Worker (Workers KV, Checkout Sessions), the webhook's paid step, and
   `tools/orders/` (pull, list, make, ship, purge). Tested with Stripe's test card. *2 h*
10. [ ] **Agent** · After 9: The configurator: product page, photo step (upright, crop, resize), options,
    a slot for the product's preview, order button and thank-you page. Checked at phone size. *1.5 h*
11. [ ] **Agent** · After 10: The subject picker: tap to select, running in the browser on a self-hosted
    model, with a lasso fallback. *2 h*
12. [x] **Agent** · After 1: Shop policies: shipping, returns and refunds, with personalised items final
    sale except for defects and shipping damage. Privacy and terms rewritten for Stripe, uploaded photos
    and Slant (detail in docs/LOG.md, task 13). *45 min*
13. [ ] **RJ** · After 10 and 14: On your phone at https://rl.rblt.io/shop/, order an ornament and pay
    with test card 4242 4242 4242 4242. Check that it shows in `python3 tools/orders/queue.py list`.
    *20 min*

### The first two products

14. [ ] **Agent** · Ornament: the bulb-and-cap recipe in lithophane-maker, the configurator's lithophane
    preview, renders, a white calibration wedge sliced and uploaded to Meltbot, and the feasibility
    numbers with a proposed price and weekly cap (`products/lithophane-ornament/`). *2 h*
15. [ ] **RJ** · After 3 and 14: Print the wedge, then a bulb and a cap. Photograph the wedge on a light,
    and the ornament lit on your tree, as the product file asks. If you like it, confirm or change its
    price and weekly cap. *45 min hands-on; about 4 h of printing*
16. [ ] **Agent** · After 11: Cutouts: the standee and ornament recipe, sticker and cut files for Print
    Then Cut, the preview, and feasibility with a proposed price and weekly cap (`products/photo-cutout/`).
    *1.5 h*
17. [ ] **RJ** · After 3 and 16: Print a cutout and its base, print the photo and cut it on the Cricut, and
    put it together. Photograph it as the product file asks. If you like it, confirm its price and weekly
    cap. *1 h hands-on; 1–2 h of printing*
18. [ ] **Agent** · After 15: Ornament listing: calibrate from the wedge, then the product page, listing
    photos and copy, the order-by date for Christmas, its marketing kit, and the counted short links
    before the first post (docs/MARKETING.md; docs/LOG.md, task 17). *1 h*
19. [ ] **Agent** · After 17: Cutouts listing, the same way. *45 min*

### Launch

20. [ ] **Agent** · After 6, 8, 12, 13 and 18: Launch, once RJ says go. Set the launch dates, rerun the
    privacy pass, remove the frozen prototype and the `CNAME` file, switch the shop to live
    ([docs/SHOP.md](docs/SHOP.md), "Launch"; docs/LOG.md, task 9), merge `rebuild` into `main`, push, and
    deploy to Cloudflare. Check the site, an upload and one live checkout page. *45 min*

### The other three, each opening when its prototype passes

21. [ ] **Agent** · After 14: Lithophane lamp: base designs sharing one tile size, the tile recipe, the
    light, preview and feasibility (`products/lithophane-lamp/`). It shares lithophane-maker with step 14,
    so it follows it. *2 h*
22. [ ] **Agent** · After 11: Pop-out photos: the silhouette, tab and shim recipe for 4×6, 5×7 and 8×10;
    sticker, cut and background-print files; preview and feasibility (`products/popout-photo/`). *2 h*
23. [ ] **Agent** · After 11: Projector: the generator (text, logo or silhouette into a shell), a lamp
    base for a small LED, preview, feasibility, and two or three LED options with prices
    (`products/stereographic-projector/`). *3 h*
24. [ ] **RJ** · After 21: Print the lamp prototype, light it and swap a tile. Confirm its price and cap
    if you like it. *1 h*
25. [ ] **RJ** · After 22: Pop-out prototype from the fisherman photo, in real 4×6, 5×7 and 8×10 frames
    (buy three cheap ones if you have none). Confirm its price and cap if you like it. *1 h*
26. [ ] **RJ** · After 23: Buy the LED you pick, print the projector, and try it in a dark room. Confirm
    its price and cap if you like it. *1 h*
27. [ ] **Agent** · After 24: Lamp listing, as in step 18. *45 min*
28. [ ] **Agent** · After 25: Pop-out listing, as in step 18. *45 min*
29. [ ] **Agent** · After 26: Projector listing, as in step 18. *45 min*

### Not needed for launch

Any time, in any order:

- **RJ** · The style changes document, dropped in `inbox/`. An agent then makes the changes.
- **Agent** · About's prose into Markdown RJ can edit (`src/content/about.md`; docs/LOG.md, task 14);
  then **RJ** rewrites it.
- **RJ** · Delete the two test drafts that the shop build left in Gelato (Orders → Drafts).
- **RJ** · Sign the assignment to the LLC (`.private/legal/assignment-to-llc.md`; full legal name), scan
  it, and keep it with the LLC's papers.
- **RJ** · Trim the Cloudflare token's Billing and Registrar access, or leave it (agents won't call them;
  docs/CHARGES.md).
- **RJ** · Delete `shopify.env` from the secrets folder.
- **RJ** · Untracked files from 2026-09-30 and 10-01: `design/brand/BRAND-GUIDE.md`, `masters/`,
  `_archive/`, `favicon-logo.svg` and `prompts/`. Commit them, move them to `.private/`, or delete them.
- **RJ** · Ask QPMN for its API docs (Developer Center, Integration with API); ask Lulu for API access
  when books come up.
- **Optional** · `design/brand/mark-blob.*` can go when RJ's done with it.

## Parked

- Brand merch (wordmark tee, logo mug, wordmark tote) and the stargazing blankets, until after launch
  (`products/`; decision 2). Night sky prints wait for photos RJ wants printed.
- The photo jack-o'-lantern (3d-modeling `jack-o-lantern/`, designed 2026-10-07, not printed), for
  Halloween 2027. It would order through the same flow.
- Essay: why the machines have names (RJ says there's a practical reason; the About page promises it).
- Post: what "the model" means in a chat app. Per-turn routing, personalization and the in-app context
  all shape a reply, and only the account export records which model answered.
- `unprojection-astra`, the other build of the sky visualization (GPT-6-Astra, open brief), is previewed
  on Samwise and stays off the site for now. The Opus build is live as a build.
- Large files as the site grows: video on YouTube; big downloads or self-hosted video on Cloudflare R2
  behind a subdomain (free tier 10 GB; it needs a card on file, so add it to docs/CHARGES.md first).

## Log

Entries before 2026-11-10 are in [docs/LOG.md](docs/LOG.md).

- 2026-11-10: RJ is back after five weeks away, and the launch now centres on four products made from a
  customer's photo (his memo in the 3d-modeling repo, `ideas/ideas-products-nov-2026.md`). Re-planned:
  one order flow built as modules (docs/ORDERS.md), a folder per product, a marketing kit per product
  (docs/MARKETING.md), and a new road to launch with twelve proposed decisions. Merch parked. Old road,
  task notes and log moved to docs/LOG.md. Checked on the way: the preview and the Cloudflare copy work
  after the LAN move (Git primary now on Bilbo); lithophane-maker, the jack-o'-lantern engine and printdb
  have nothing printed; the projector files are CC BY-SA; Slant has no light small enough for a
  projector; Workers KV's free plan and the 10 ms CPU limit set how uploads work.
- 2026-11-10: RJ took the twelve decisions as recommended (step 1), and the docs no longer mark them
  as proposed. The ornament recipe (step 14) started in its own session.
- 2026-11-10: Shop policies (step 12): new Shipping, Returns and Contact pages in the footer; privacy and
  terms rewritten for Stripe and photo orders, with nothing left that says Shopify. Not legal advice: RJ's
  reading list and the points for a lawyer are in `.private/legal/policies-2026-11-10.md`, and
  docs/ORDERS.md lists the privacy promises the order code must keep.
