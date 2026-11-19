# Now

_Last updated 2026-11-17._

## Start here

The new site is built on the `rebuild` branch and previewed at https://rl.rblt.io/
([docs/PREVIEW.md](docs/PREVIEW.md)), with a copy on Cloudflare at https://site.robotlantern.workers.dev.
robotlantern.com is still the old landing page. Design rules are in [docs/PAGES.md](docs/PAGES.md), the home
page in [docs/HOME.md](docs/HOME.md) and the brand in [docs/BRAND.md](docs/BRAND.md).

**The launch is about products made from a customer's photo** (RJ, 2026-11-10), ordered through one flow
built as modules ([docs/ORDERS.md](docs/ORDERS.md)), each with a folder in `products/`
([docs/PRODUCTS.md](docs/PRODUCTS.md)) and a marketing kit ([docs/MARKETING.md](docs/MARKETING.md)).

**The first product is a two-part pet ornament, printed and shipped by Slant 3D** (decisions 13 and 14;
[products/cutout-ornament/product.md](products/cutout-ornament/product.md)). A base in one PLA colour and a
stencil sheet in another press together with pegs, no glue. The pet is drawn as cut-outs in the stencil, and
an optional name tag hangs below. GPT Image redraws the photo as a two-colour stencil, and a builder turns
that into two STLs. Ten family pets are designed and quoted at Slant ($3.56–4.01 each with a name tag, before
shipping). RJ approved the design on 2026-11-17 after seeing all ten printed at actual size on paper. It
replaced the mosaic design of 2026-11-13, which had too many pieces ([docs/LOG.md](docs/LOG.md)).

**Pick up here (2026-11-17): more ornament design work with RJ, interactively** (step 35). He wants more
than one ornament prototyped for launch photos, even if the others say "coming soon". The fit test (step 33)
waits until RJ is ready to print: he doesn't want prints running while he works.

### The scratch folder (not in Git, not in printdb)

The ornament work lives in `../ornaments-design-session/`, next to this repo. It stays untracked because the
designs come from family photos (decision 15). Don't copy it into the repo or commit it. What's there:

- `tools/`: `build.py` (drawing → `base.stl` + `stencil.stl` + preview + picker SVGs, with the one-piece and
  watertight checks), `nametag.py` (stencil fonts to outlines, fitted to the tag), `run_palette.py` (builds
  every pet in a palette file), `plates.py` (packs parts onto Meltbot plates by colour), `quote.py` (Slant
  quotes and Orca slices through `~/work/3d-modeling/tools/estimate.py`). They run with
  `~/work/lab/lithophane-maker/.venv/bin/python`. The builder's defaults are the approved design.
- `batch-01/`: the ten pets. `<pet>/BRIEF.md` is each GPT Image brief, `art-N.png` the drawings, `picks.txt`
  the chosen ones, `palette.json` the colours, names and fonts. **`build-v3/` is the approved build** (parts,
  previews, quotes, plates). `build-v1`, `v2`, `v4` and `v5` are superseded tries (no tag; no ring neck; a tag
  border; a tag rule).
- `proto-01/`: the first Tucker prototype and the font trials.
- `picker/`: the customer's colour and name-tag picker, a front-end prototype that sends nothing
  (`python3 -m http.server` in that folder). Its spec is `briefs/colour-picker.md`.
- `people-01/`: people as head ornaments (step 35). `rj/` and `heads/<subject>/` hold a `BRIEF.md`, three
  tries and their builds. `group/` is a three-person round bauble, too fine to read at 80 mm.
- `PRINT-QUEUE.md`: the nine Meltbot plates for build-v3, fit test first. RJ prints them himself in Creality
  Print (the upload tool needs printdb, and these stay out of it). An agent hands him files and marks rows.
- `print-proof/proof.pdf`: the ten designs at actual size, as printed on Inkbot Alpha.
- `research/sticker-pod.md`: sticker print-on-demand APIs for the printed-photo version (summarised in
  `products/photo-cutout/product.md`).
- `svg-edit/`: copies of the build-v5 SVGs RJ took for hand editing (superseded).

### Running things

- `python3 tools/next.py` prints RJ's next steps; `python3 tools/products/board.py` shows each product's stage.
- To start an agent step, open a session here and say: "Read AGENTS.md and NOW.md, then do step N."
  Start agent sessions at medium effort; three at once on Max used up the 5-hour window on 2026-11-10.
- History, older logs and the mosaic design are in [docs/LOG.md](docs/LOG.md).

## Decisions

RJ took 1–12 as recommended on 2026-11-10. The docs cite them by number.

1. **Launch cut.** The site launches once the first product can be ordered, plus cutouts if their prototype
   is ready in time. The lamp, pop-out photos and projector open as each prototype passes, aiming for all
   by Black Friday, 2026-11-27. The other way is to hold launch until all are ready.
2. **Merch waits.** The tee, mug, tote and blankets are parked until after launch.
3. **You make everything at first**, with Meltbot, your printer and the Cricut, and a weekly cap per
   product. A product moves to Slant only after one paid test order of it, on your go. (The pet ornament is
   the exception: decision 14.)
4. **Pay, then check, then make.** Customers pay at checkout. You look at every order before making it.
   If a photo won't work, you email the customer from help@ to swap it, or refund in full. There's no
   proof round by default.
5. **Uploads go to Cloudflare Workers KV on the free plan.** Nothing there can bill, and unpaid uploads
   delete themselves after two days.
6. **Photos are deleted 60 days after the order ships**, along with the files made from them. Order
   records without photos are kept seven years. Customer photos never go into marketing without the
   customer's written OK.
7. **Lithophane ornaments are white at launch and for LED lights only.** Colours come after each one's test
   wedge. PLA softens at about 60 °C, and older incandescent bulbs can run hotter than that.
8. **The projector gets our own generator**, written from the maths rather than threonin's code, with
   credit to threonin's projector on the Credits page.
9. **Lines that aren't ready show "coming soon"**, with an email link to signup@. There's no form, and
   nothing is stored on the site.
10. **Pictures are honest.** Listings show real prototypes, or renders marked as renders. Example photos
    are yours, family's with their OK, or AI-made stand-ins marked as such. No AI "lifestyle" pictures
    that redraw the product.
11. **The About rewrite and the style changes don't hold launch.**
12. **Platforms:** Instagram, Facebook and Pinterest first.
13. **First product: the pet ornament** (RJ, 2026-11-13), in place of the lithophane ornament, which waits
    until after launch. Still open (step 36): whether it gets a proof by email before it's made (an
    exception to decision 4), and whether a customer's photo may go to GPT Image, a hosted model, which
    means changing the privacy page first.
14. **Slant fulfils the pet ornament from launch** (RJ, 2026-11-17). Two parts, any two of Slant's 20 PLA
    colours, which the customer picks (we suggest pairs). The listing photos are our own Meltbot prints in the
    nearest shelf colours, marked as examples, and the listing says who makes what. Slant photos replace them
    once we have some.
15. **The pet ornament designs stay out of printdb and Git** (RJ, 2026-11-17). They come from family photos
    and live in the scratch folder. Only the product file and the decisions are in the repo.

## Road to launch

Steps in order. **RJ** steps are his; **Agent** steps are one session each. "After 6:" means the step
waits for step 6. Times are rough: agent time is wall-clock, RJ time is hands-on. Check a step off when
it's done.

The pet ornament's remaining path is steps 33–36, then 13 and 20. If the tax certificate is slow, the site can
go live with the shop showing "coming soon" until it arrives.

### Accounts, tax and the domain

1. [x] **RJ** · The decisions above: 1–12 taken as recommended (2026-11-10). *5 min*
2. [ ] **RJ** · Sales tax ([docs/SALES-TAX.md](docs/SALES-TAX.md)): the LLC is registered with West Virginia
   (certificate 2025-12-16, monthly sales and use tax account), and the $0 returns for Dec 2025 through
   Oct 2026 were submitted by 2026-11-12. Left: check the December 2025 receipt is in your tax folder, and ask
   the Tax Department whether quarterly or annual filing is allowed. Until then, file a $0 return each month
   by the 20th. The EIN is not a launch blocker. *15 min*
3. [ ] **RJ** · Materials: say whether to buy PLA in tan, brown and bone white, so three of the ten
   pets can be printed for photos (a charge; the product file and the print queue list them). Also which sticker paper and
   Cricut you have, and which lights are on your tree (mini LED, C7 or C9). *10 min*
4. [ ] **RJ** · Cloudflare: look at https://site.robotlantern.workers.dev; say yes or no to SPF and DMARC
   for mail ([docs/HOSTING.md](docs/HOSTING.md)); add robotlantern.com to Cloudflare (dashboard, free
   plan), or give the API token Zone and DNS edit for the change window. *15 min*
5. [ ] **Agent** · After 4: Enter the DNS records in Cloudflare and compare them with the old ones
   (docs/HOSTING.md, "Cutover"). *15 min*
6. [ ] **RJ** · After 5: Switch the nameservers at DomainRegistry.com to Cloudflare's. Changes can take up
   to a day to spread. *10 min*
7. [ ] **RJ** · After 2: Stripe: create the order Worker's restricted live key ([docs/ORDERS.md](docs/ORDERS.md),
   "Stripe"). Changing the business details to Robot Lantern LLC needs an EIN and is optional. *20 min*
8. [ ] **RJ** · After 2 and 7: Turn on West Virginia in Stripe Tax (live) in the Dashboard, choosing "Start
   collecting immediately" with the Combined Sales and Use account number (docs/SALES-TAX.md, step 5). An
   agent then reads the registration back. *10 min*

### The order flow ([docs/ORDERS.md](docs/ORDERS.md))

9. [x] **Agent** · After 1: Order intake in Stripe's sandbox: the photo products' `shop.json` files,
   `/api/orders` in the shop Worker (Workers KV, Checkout Sessions), the webhook's paid step, and
   `tools/orders/` (pull, list, make, ship, purge). Tested with Stripe's test card. *2 h*
10. [ ] **Agent** · After 9: The configurator: product page, photo step (upright, crop, resize), options,
    a slot for the product's preview, order button and thank-you page. Checked at phone size. The pet
    ornament's picker prototype (scratch folder, `picker/`) is its first options-and-preview module. *1.5 h*
11. [ ] **Agent** · After 10: The subject picker: tap to select, running in the browser on a self-hosted
    model, with a lasso fallback. *2 h*
12. [x] **Agent** · After 1: Shop policies: shipping, returns and refunds, with personalised items final
    sale except for defects and shipping damage. Privacy and terms rewritten for Stripe, uploaded photos
    and Slant (docs/LOG.md, task 13). *45 min*
13. [ ] **RJ** · After 10 and 34: On your phone at https://rl.rblt.io/shop/, order a pet ornament and pay
    with test card 4242 4242 4242 4242. Check that it shows in `python3 tools/orders/queue.py list`.
    *20 min*

### The other photo products

14. [ ] **Agent** · After 30: Paused by RJ on 2026-11-13 (decision 13). Lithophane ornament: the recipe,
    preview and numbers are done in lithophane-maker; renders and the feasibility section are left
    (`products/lithophane-ornament/`). *2 h*
15. [ ] **RJ** · After 3 and 14: Print the wedge, then a bulb and a cap. Photograph the wedge on a light,
    and the ornament lit on your tree. If you like it, confirm or change its price and weekly cap.
    *45 min hands-on; about 4 h of printing*
16. [ ] **Agent** · After 11: Cutouts: the standee and ornament recipe, sticker and cut files for Print
    Then Cut (or a sticker print-on-demand service; the product file has the research), the preview,
    and feasibility with a proposed price and weekly cap (`products/photo-cutout/`). *1.5 h*
17. [ ] **RJ** · After 3 and 16: Print a cutout and its base, print the photo and cut it on the Cricut, and
    put it together. Photograph it as the product file asks. If you like it, confirm its price and weekly
    cap. *1 h hands-on; 1–2 h of printing*
18. [ ] **Agent** · After 15: Lithophane ornament listing: calibrate from the wedge, then the product page,
    photos, copy, order-by date and marketing kit (docs/MARKETING.md). *1 h*
19. [ ] **Agent** · After 17: Cutouts listing, the same way. *45 min*

### Launch

20. [ ] **Agent** · After 6, 8, 12, 13 and 34: Launch, once RJ says go. Set the launch dates, rerun the
    privacy pass, remove the frozen prototype and the `CNAME` file, switch the shop to live
    ([docs/SHOP.md](docs/SHOP.md), "Launch"; docs/LOG.md, task 9), merge `rebuild` into `main`, push, and
    deploy to Cloudflare. Check the site, an upload and one live checkout page. *45 min*

### The other three, each opening when its prototype passes

21. [ ] **Agent** · After 14: Lithophane lamp: base designs sharing one tile size, the tile recipe, the
    light, preview and feasibility (`products/lithophane-lamp/`). *2 h*
22. [ ] **Agent** · After 11: Pop-out photos: the silhouette, tab and shim recipe for 4×6, 5×7 and 8×10;
    sticker, cut and background-print files; preview and feasibility (`products/popout-photo/`). *2 h*
23. [ ] **Agent** · After 11: Projector: the generator, a lamp base for a small LED, preview, feasibility,
    and two or three LED options with prices (`products/stereographic-projector/`). *3 h*
24. [ ] **RJ** · After 21: Print the lamp prototype, light it and swap a tile. Confirm its price and cap
    if you like it. *1 h*
25. [ ] **RJ** · After 22: Pop-out prototype from the fisherman photo, in real 4×6, 5×7 and 8×10 frames.
    Confirm its price and cap if you like it. *1 h*
26. [ ] **RJ** · After 23: Buy the LED you pick, print the projector, and try it in a dark room. Confirm
    its price and cap if you like it. *1 h*
27. [ ] **Agent** · After 24: Lamp listing, as in step 18. *45 min*
28. [ ] **Agent** · After 25: Pop-out listing, as in step 18. *45 min*
29. [ ] **Agent** · After 26: Projector listing, as in step 18. *45 min*

### The pet ornament ([products/cutout-ornament/product.md](products/cutout-ornament/product.md))

30. [x] **RJ** · Go or no-go on the pet ornament as the first product: go (decision 13, 2026-11-13). *15 min*
31. [x] **RJ** · Choose and label better photos (in `.private/products/cutout-ornament/pet-photos-selected/`). *1 h*
32. [x] **Agent** · After 31: The design and its pipeline (2026-11-17): the two-part stencil (pegs, pocket,
    ring, name tag in five stencil fonts), GPT Image briefs, the builder and its checks, ten pets designed,
    Slant quotes for all twenty parts with no supports flagged, colour plates and a print queue, the picker
    prototype, and an actual-size paper proof RJ approved. All in the scratch folder. *a day*
33. [ ] **RJ** · After 32: When you're ready to print, the fit test: plates 1 and 2 of the scratch folder's
    `PRINT-QUEUE.md` in Creality Print, then put Tucker together and answer its questions (pegs, pocket,
    ring, thin spots). If the fit is right, print the rest and photograph them on the tree for the listing.
    *1 h hands-on; about 7 h of printing, spread out*
34. [ ] **Agent** · After 10, 33 and 36: Pet ornament listing: the picker into the configurator as its options
    and preview, `shop.json`, and the order path (the photo through GPT Image, the builder, a person checking
    the preview, the parts to Slant, priced and drafted only for a real order that RJ processes;
    docs/ORDERS.md, docs/CHARGES.md). Then the product page, photos, copy, order-by date and marketing kit.
    *3 h*
35. [ ] **Agent** · After 32: Design work with RJ, interactively, in the scratch folder: more ornaments for
    launch photos ("coming soon" is fine for the rest). On the table: standard shapes (star, bell, round)
    for designs without a pet silhouette, recesses or holes in the base for shadow detail, and the plain
    backing for the printed-photo sticker version (`products/photo-cutout/`). *open-ended; size it with RJ first*
36. [ ] **RJ** · After 32: Decide the ornament's price, whether customer photos may go to GPT Image (the
    privacy page changes first if so), and whether there's a proof by email (decision 13). *15 min*

### Not needed for launch

Any time, in any order:

- **RJ** · The style changes document, dropped in `inbox/`. An agent then makes the changes.
- **Agent** · About's prose into Markdown RJ can edit (`src/content/about.md`; docs/LOG.md, task 14);
  then **RJ** rewrites it.
- **RJ** · Delete the two test drafts that the shop build left in Gelato (Orders → Drafts).
- **RJ** · Sign the assignment to the LLC (`.private/legal/assignment-to-llc.md`; full legal name), scan
  it, and keep it with the LLC's papers.
- **RJ** · Trim the Cloudflare token's Billing and Registrar access, or leave it (docs/CHARGES.md).
- **RJ** · Delete `shopify.env` from the secrets folder.
- **RJ** · Untracked files from 2026-09-30 and 10-01: `design/brand/BRAND-GUIDE.md`, `masters/`,
  `_archive/`, `favicon-logo.svg` and `prompts/`. Commit them, move them to `.private/`, or delete them.
- **RJ** · Ask QPMN for its API docs; ask Lulu for API access when books come up.
- **RJ** · A Printful die-cut sticker sample (3×3 in, about $4 plus shipping) to test the printed-photo
  version. It's a charge: add it to docs/CHARGES.md first.
- **Optional** · `design/brand/mark-blob.*` can go when RJ's done with it.

## Parked

- Brand merch (wordmark tee, logo mug, wordmark tote) and the stargazing blankets, until after launch
  (`products/`; decision 2). Night sky prints wait for photos RJ wants printed.
- The photo jack-o'-lantern (3d-modeling `jack-o-lantern/`, designed 2026-10-07, not printed), for
  Halloween 2027. It would order through the same flow.
- Essay: why the machines have names (the About page promises it).
- Post: what "the model" means in a chat app.
- `unprojection-astra`, the other build of the sky visualization, is previewed on Samwise and stays off
  the site for now.
- Large files as the site grows: video on YouTube; big downloads on Cloudflare R2 behind a subdomain
  (needs a card on file, so add it to docs/CHARGES.md first).
- The mosaic pet ornament engine, `tools/cutout/`, superseded and kept for reference (docs/LOG.md).
- Secret Santa QR snowflakes (`tools/qr-ornament/`), parked 2026-11-19 in favour of the stacked tag
  pair. The square and dotted QR codes both scanned in simulation, but RJ didn't like either look. A
  custom code read in the browser had enough room for a name but didn't look enough like a snowflake.
- Secret Santa tag pair (`tools/tag-pair/`): two one-colour tags printed stacked as one piece, with the
  recipient's name hidden on the inner face. Test v1 (print 162) failed: the full seam wall sealed shut and
  pillars alone were too weak. Next is a v2 test plate with a weaker, adjustable seam (see the log).

## Log

Entries before 2026-11-17 are in [docs/LOG.md](docs/LOG.md).

- 2026-11-19: Secret Santa tag pair test piece (`tools/tag-pair/coupon.py`; printdb model 155, version
  214, print 162; uploaded to Meltbot as `Tag-Pair-Coupon-v1.gcode`, not started). Two 50 × 28 mm tags
  are stacked with an air gap. "TO: SALLY" is raised on the hidden face and "FROM: <variant>" on top.
  Tapered pillars in the margins snap off at their tips. A seam wall, one line thick, seals the gap and
  tears open. Four pairs:
  - A: gap 0.6 mm, sealed
  - B: gap 0.8 mm, sealed
  - C: gap 1.0 mm, thinner 0.6 mm pillar tips, no seal
  - D: gap 0.8 mm, sealed, 2 mm tags, to test whether the name shows against a lamp

  Result (RJ, same day): the name didn't show through any tag against a lamp, even at 1.2 mm.
  A, B and D sealed solid and couldn't be pulled apart, even straight off the plate. C fell apart as it came
  off the plate, and printed messy. So the continuous seam is the bond, and 0.6 mm tips alone don't hold.
  v2 should keep 1.2 mm tags and a 0.8 mm gap, and vary the seam: dashed walls at different duty cycles, a
  seam that stops one layer short, and stronger pillars with no seam. Add a pry notch.
  The history sync only links prints whose `external_ref` is empty. Leave it blank when registering a print.

  Each top tag's first layer slices as a plain bridge, with no supports. The plate is 42 min 50 s and
  19.3 g in ELEGOO Matte White (spool 41) at 205/60 °C on Textured PEI, and the G-code validated.

- 2026-11-19: Secret Santa snowflake, a feasibility prototype (`tools/qr-ornament/`; test files in
  `.private/products/qr-snowflake/print-test/`). The message is plain text in a QR code turned 45°, with
  pixel arms, a hanging loop, and the giver's name and year debossed on the back of a tag. Two
  one-colour variants, both a single watertight body on Meltbot's profile:
  - **Stencil:** a white plate with holes, scanned lying on something dark. A 42-character message with
    2 mm modules came out as one piece: 68 corner discs and 4 bridges (the finder and alignment rings).
    It prints in 32 min and uses 8.6 g at 1.6 mm thick.
  - **Relief:** a 0.6 mm backing with raised modules and a 3 mm rim, scanned held up to a light. It
    prints in 41 min and uses 14.6 g.

  Simulated photos run through zbar and OpenCV, 27 conditions each (a perfect print as control: 25/27):
  - Stencil at 1.2–1.6 mm: 18–23/27. Deep holes fail at 40° tilt.
  - Relief: 20–23/27 if white PLA scatters little, 10–16 at moderate scatter, 0 at heavy scatter, and
    0 front-lit.
  - 1.5 mm modules (74 mm wide instead of 99 mm) score a little lower on both.

  How much light white PLA lets through is a guess until one print is measured. Messages over about
  42 characters step up a QR size: 60 characters is version 4, 82 is version 5.

- 2026-11-19: The round, dotted snowflake (`tools/qr-ornament/dotflake.py`; files in
  `.private/products/qr-snowflake/dot-print-test/`). Dark modules are dots and the finder squares
  ("eyes") have rounded corners. The code sits on a disc with six arms grown from the giver's name and
  year, so every ornament's arms differ. The name and year are debossed along the back rim.
  - **Corner rounding:** fully rounded eyes defeat OpenCV completely (0/27 even on a perfect print).
    Half-module corners keep every decoder working, so that's the default (`--eye-r`).
  - **Stencil:** dots need no bridges, just two ties per eye. But the dots shrink to 1.3 mm to keep a
    0.7 mm web, and then only zbar reads it: 15–20/27 at 2 mm modules, 22–24/27 at 2.5 mm.
  - **Relief:** better than the square relief (23–25/27 with little scatter, 21 with moderate). It
    still reads at 1.6 mm modules.
  - **Size is the catch:** a circle round a square is 1.4× wider. At 2 mm the ornament is 113 × 134 mm
    (stencil 55 min, 11.5 g). The relief at 1.6 mm is 98 × 116 mm (40 min, 8.5 g).
  - A message of 26 characters or fewer would drop one QR size.

- 2026-11-18: People as head ornaments, through the pet stencil brief (scratch folder `people-01/`). A
  three-person round bauble was too fine at 80 mm. Heads work: four family photos, three tries each, all
  one piece. The style was steady in 11 of 12 tries; likeness varies. Bridges over 3 mm are common, so the
  builder's bridge placement needs a look before people go on sale.

- 2026-11-17: Market research on the pet ornament, written while RJ was away:
  [products/cutout-ornament/market-research.md](products/cutout-ornament/market-research.md). Found no
  one selling a two-colour flat stencil pet ornament printed on demand. Nearest: Meshy's full-colour printed
  keychain ($39), Etsy 3D-printed pet items ($11.70–$35), laser-cut wood silhouettes ($15–$20), and
  $10–$30 printed-photo ornaments (the volume market). Suggests pricing in the $19–$29 band and offering a
  proof or remake promise; informs step 36. Open: Slant's shipping for one box decides the margin. Several
  competitor pages blocked fetches, so some prices are search snippets to re-check. Nothing charged, no
  code changed.

- 2026-11-17: The pet ornament became a two-part stencil, fulfilled by Slant (decisions 14 and 15). The
  mosaic had too many pieces. Built in the scratch folder: GPT Image stencil briefs; a builder that bridges
  loose details, adds pegs, pocket, a hanging ring with a filleted neck, and a name tag in five stencil fonts
  (Black Ops One dropped, its gaps print too thin); Slant quotes ($3.56–4.01 a pet, no supports); colour
  plates; a print queue; and the picker prototype, built in its own session. Tried and dropped: an
  embossed border round the tag, then a rule above the name. RJ preferred the plain tag once he saw all ten
  at actual size on paper. Timmy (turtle) dropped: weak drawing. Sticker print-on-demand researched
  (products/photo-cutout/). Docs passed for stale references: README, docs/ORDERS.md, docs/LOG.md, the
  product files, and `tools/cutout/` marked superseded.
