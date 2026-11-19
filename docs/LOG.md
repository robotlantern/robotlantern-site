# History

What NOW.md recorded before its rewrites of 2026-11-10, 2026-11-17 and 2026-11-19, moved here unchanged so NOW.md can stay short.
It keeps the reasons behind earlier decisions. The current state, the road to launch and newer log
entries are in [NOW.md](../NOW.md).

## The 2026-11-10 plan, as NOW.md had it on 2026-11-19 (superseded by the launch plan)

NOW.md was rewritten on 2026-11-19 around launching the stencil ornament on 2026-11-20 (its decisions 16–25). What it said before is kept here unchanged. The other photo products' files cite this plan's step numbers ("the 2026-11-10 plan, step N").

**Pick up here (2026-11-17): more ornament design work with RJ, interactively** (step 35). He wants more
than one ornament prototyped for launch photos, even if the others say "coming soon". The fit test (step 33)
waits until RJ is ready to print: he doesn't want prints running while he works.
**2026-11-19:** RJ printed Buster (v1, no tag) as a first fit test: it fits and looks great, but a stencil
neck about 1.0 mm wide nearly let the left eye patch break off. The builder now widens such necks, and its
bridges, to 1.8 mm (`--neck`, `--bridge`). Tucker, Annabel, Cashew, Sam, Toby and Wiggles are rebuilt with it (build-v6); their white bases are on two
sliced trays, three each, uploaded to MeltBot after a heads tray (flower-crown, laughing-boy, beard-man) that
started printing 2026-11-19 (printdb jobs 173-175: generic records, no designs, by RJ's choice). Stencils built, not plated.

### The scratch folder as of 2026-11-19 (not in Git, not in printdb)

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

### Decisions 1–15 as worded on 2026-11-17

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

### The road to launch as it stood on 2026-11-19, before the rewrite

Steps in order. **RJ** steps are his; **Agent** steps are one session each. "After 6:" means the step
waits for step 6. Times are rough: agent time is wall-clock, RJ time is hands-on. Check a step off when
it's done.

The pet ornament's remaining path is steps 33–36, then 13 and 20. If the tax certificate is slow, the site can
go live with the shop showing "coming soon" until it arrives.

### Accounts, tax and the domain

1. [x] **RJ** · The decisions above: 1–12 taken as recommended (2026-11-10). *5 min*
2. [ ] **RJ** · Sales tax ([docs/SALES-TAX.md](SALES-TAX.md)): the LLC is registered with West Virginia
   (certificate 2025-12-16, monthly sales and use tax account), and the $0 returns for Dec 2025 through
   Oct 2026 were submitted by 2026-11-12. Left: check the December 2025 receipt is in your tax folder, and ask
   the Tax Department whether quarterly or annual filing is allowed. Until then, file a $0 return each month
   by the 20th. The EIN is not a launch blocker. *15 min*
3. [ ] **RJ** · Materials: say whether to buy PLA in tan, brown and bone white, so three of the ten
   pets can be printed for photos (a charge; the product file and the print queue list them). Also which sticker paper and
   Cricut you have, and which lights are on your tree (mini LED, C7 or C9). *10 min*
4. [ ] **RJ** · Cloudflare: look at https://site.robotlantern.workers.dev; say yes or no to SPF and DMARC
   for mail ([docs/HOSTING.md](HOSTING.md)); add robotlantern.com to Cloudflare (dashboard, free
   plan), or give the API token Zone and DNS edit for the change window. *15 min*
5. [ ] **Agent** · After 4: Enter the DNS records in Cloudflare and compare them with the old ones
   (docs/HOSTING.md, "Cutover"). *15 min*
6. [ ] **RJ** · After 5: Switch the nameservers at DomainRegistry.com to Cloudflare's. Changes can take up
   to a day to spread. *10 min*
7. [ ] **RJ** · After 2: Stripe: create the order Worker's restricted live key ([docs/ORDERS.md](ORDERS.md),
   "Stripe"). Changing the business details to Robot Lantern LLC needs an EIN and is optional. *20 min*
8. [ ] **RJ** · After 2 and 7: Turn on West Virginia in Stripe Tax (live) in the Dashboard, choosing "Start
   collecting immediately" with the Combined Sales and Use account number (docs/SALES-TAX.md, step 5). An
   agent then reads the registration back. *10 min*

### The order flow ([docs/ORDERS.md](ORDERS.md))

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
    ([docs/SHOP.md](SHOP.md), "Launch"; docs/LOG.md, task 9), merge `rebuild` into `main`, push, and
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

### The pet ornament ([products/cutout-ornament/product.md](../products/cutout-ornament/product.md))

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

## NOW.md log, 2026-11-17 to 2026-11-19

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
  RJ's read: C was the best. Its mess and its separation came from the gaps being too tall and from the big
  empty areas above and below the name, which had nothing in them. One layer of difference is enough to read
  the name. No dashed seams, and one coupon at a time.
- 2026-11-19: tag pair test v2, variant E (printdb version 215, print 172; 10 min 25 s, 4.15 g). This is C
  with the hidden name raised one layer (0.2 mm) and one layer of air above it, so the pillars are 0.4 mm
  tall. It has 16 pillars, including new ones near the left and right edges. Uploaded and not started.
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
  [products/cutout-ornament/market-research.md](../products/cutout-ornament/market-research.md). Found no
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

## NOW.md log, 2026-11-10 to 2026-11-13

Moved here unchanged when NOW.md was rewritten on 2026-11-17 for the two-part stencil ornament.

- 2026-11-13 (evening): Pet ornament, continued. GPT Image through `codex exec` (gpt-6-luna; images land in
  `~/.codex/generated_images/`, collected from there) beat the local model by far. `mosaic.py` gained a
  palette snap, black-as-back, three layers (a black line layer over the colour pieces, so detail lines never
  cut colours into slivers) and the name plate; `run_batch.py` runs a manifest. House palette set from the
  shelf against Slant's catalogue in printdb: black, white, tan, brown, gray, red, green, gold, orange,
  yellow. RJ chose and labelled photos (moved to `.private/`); 14 ornaments made, years from EXIF or
  estimated (product file). Family-photo and portrait tests are in `.private/` too; RJ prefers the
  black-and-white portraits. RJ to decide: buying tan, brown, gray, green and yellow for local prototypes.
- 2026-11-13: Picked up after the 2026-11-10 sessions hit the usage limit. Step 9 finished: its test now
  passes end to end in Stripe's sandbox (upload, the price from the product file, two-day expiry, test-card
  payment, webhook and resend, bad signatures, pull, list, purge); docs/ORDERS.md and SHOP.md updated. Stale
  items fixed: tax step 2 narrowed to the Dec 2025 receipt and the filing-frequency question; step 8 is RJ's
  in the Dashboard ("Start collecting immediately", per the Stripe Tax session of 2026-11-12); the matte
  spools have been in printdb since 2026-11-10. RJ paused the lithophane ornament (step 14) and proposed a
  snap-together pet ornament. A feasibility prototype (`tools/cutout/`) found it works with a local
  AI cartoon step and doesn't without one (product file; decision 13 and steps 30–34 added). RJ said go,
  with names and years on the ornament, and wants to pick and label better photos before the routes are
  compared again (an LLM description fed to the image model; GPT Image through Codex; a library of breed
  templates recoloured from the customer's photo). RJ's
  Illustrator file and its preview moved to `.private/products/cutout-ornament/`. The pet photos used
  came from RJ's Immich export of 2026-11-12, which is mostly people: only five pets were in it.
- 2026-11-12: Submitted the May–October 2026 $0 WV sales and use tax returns; MyTaxes issued
  confirmations and showed each request as pending. The receipts are in the tax filings folder. The
  action center showed no outstanding actions. Verify the December 2025 receipt and ask about a
  quarterly or annual filing frequency before closing step 2.
- 2026-11-10: RJ is back after five weeks away, and the launch now centres on four products made from a
  customer's photo (his memo in the 3d-modeling repo, `ideas/ideas-products-nov-2026.md`). Re-planned:
  one order flow built as modules (docs/ORDERS.md), a folder per product, a marketing kit per product
  (docs/MARKETING.md), and a new road to launch with twelve proposed decisions. Merch parked. Old road,
  task notes and log moved to docs/LOG.md. Checked on the way: the preview and the Cloudflare copy work
  after the LAN move (Git primary now on Bilbo); lithophane-maker, the jack-o'-lantern engine and printdb
  have nothing printed; the projector files are CC BY-SA; Slant has no light small enough for a
  projector; Workers KV's free plan and the 10 ms CPU limit set how uploads work.
- 2026-11-12 (end of day): RJ phoned the WV Tax Department, which got him a MyTaxes login (his SSN entered
  with ID type FEIN) and confirmed there is no charge for unfiled $0 returns. He is filing Dec 2025 through
  Oct 2026 and saving the confirmations (Jan and Feb were in his tax folder when checked). The Business4WV
  summary shows the LLC was registered with the state on 2025-12-11 using his SSN, so no EIN came from
  formation. That weakens the earlier guess that an EIN already exists: the IRS online tool's reference
  number 101 (a name match, per third-party guides) may be some other entity's similar name. IRS phone
  calls end in "high call volume". Fallbacks: fax the SS-4 (draft in `.private/tax/`) and the Taxpayer
  Advocate Service. The EIN is optional for launch. docs/SALES-TAX.md "Before the first sale" is rewritten
  to match; the three entries below are superseded where they differ.
- 2026-11-12 (latest, superseded): the IRS online tool failed again at Review & Submit with reference number
  101 (a name match with an existing record, per third-party guides), which fits an EIN already existing
  for the LLC. Next: RJ calls the IRS (800-829-4933) and the WV Tax Department (see `.private/tax/`).
- 2026-11-12 (later): RJ downloaded the 14 PDFs from Northwest's portal. They show the LLC already has a
  WV Business Registration Certificate (issued 2025-12-16) and a monthly sales and use tax account, and
  that the "monthly tax forms" are blank WV sales and use tax returns for Dec 2025 to Oct 2026: none
  filed, no delinquency letters among them. The annual report was filed 2026-04-10 and Northwest's
  letter says the LLC is in good standing. So the EIN is no longer on the launch path, and step 2 becomes
  "bring the account current". Open: which federal ID WV has on file; whether an EIN already exists
  (a year of failed IRS attempts fits); the penalties, if any, for the late $0 returns.
- 2026-11-12: Step 2 rechecked against the IRS, Stripe and the state's own pages (docs/SALES-TAX.md). No
  EIN yet: the IRS site has not worked for RJ. Findings (the first two now superseded, see above): the EIN
  is the dependency for West Virginia's
  registration (an LLC registers with it), not for Stripe, which already takes live payments on RJ's SSN;
  the IRS no longer issues EINs by phone; fax gives the EIN in about 4 business days and mail in about 4
  weeks, so mail would miss the Dec 9 order-by date. Not found: the state's processing time for the
  certificate. Open question for RJ: whether "haven't filed taxes" means 2026 (not due until
  2027-04-15) or an earlier year.
- 2026-11-10: RJ took the twelve decisions as recommended (step 1), and the docs no longer mark them
  as proposed. The ornament recipe (step 14) started in its own session.
- 2026-11-10: Shop policies (step 12): new Shipping, Returns and Contact pages in the footer; privacy and
  terms rewritten for Stripe and photo orders, with nothing left that says Shopify. Not legal advice: RJ's
  reading list and the points for a lawyer are in `.private/legal/policies-2026-11-10.md`, and
  docs/ORDERS.md lists the privacy promises the order code must keep.
- 2026-11-10 (paused 2026-11-13): Step 14 in progress (not checked off): lithophane-maker has the ornament recipe (`products/ornament.py`, fit checks pass; bulb 2 h 08 min / 42 g, cap 19 min / 2 g on Meltbot), the white wedge sliced and validated (7 min, 3 g; not uploaded until the matte white is in printdb), and the browser preview `src/scripts/shop/lithophane-bulb.js` (matches the recipe to 0.02 mm) with a test page at /shop/test/ornament/. Left: Blender renders reviewed, the feasibility section with price, cap and order-by date (USPS Ground Advantage send-by Dec 17), printdb registration.

## The mosaic pet ornament (2026-11-13, superseded 2026-11-17)

The first pet-ornament design: flat colour pieces on pins over a black back, with a black line layer on top
(`tools/cutout/mosaic.py`, `run_batch.py`; `products/cutout-ornament/product.md` in Git history before
2026-11-17). RJ dropped it on 2026-11-17: too many separate pieces to assemble, and Slant charges per part.
Step 32 as it stood then:

32. [ ] **Agent** · After 31: Get the first batch print-ready. Done 2026-11-13: GPT Image chosen over the local
    model; the house palette (shelf vs. Slant); three layers (back, colour pieces, black line layer); the shape and
    name plate generator; `run_batch.py`; 14 named pets drawn and turned into STLs. Left: fix Tucker's coat, the
    stencil bridges on B, R and 6, long names, and the plate overlapping the subject (product file, "To fix");
    a fit coupon for 1.5 mm pins at three clearances plus a strip of line layer, sliced and uploaded to Meltbot;
    colour-batched plates (one plate per colour across the ornaments being printed, each piece with a small
    ID on its pin side, and an assembly map per ornament), sliced for time and grams; one ornament's parts
    quoted through printdb's Slant client (quotes are free; never draft); `queue.py make` and `shop.json` for
    the product. *3–4 h*

## The road to launch as it stood on 2026-10-01

One list: the site and the shop launch together (RJ, 2026-10-01). Print-on-demand products list
from their mockups; each one's sample is ordered as soon as its mockup is approved, and is a
quality check rather than a gate. Things RJ makes himself can sell in limited numbers and ship
from him.

**RJ** steps are his; **Agent** steps an agent does in a session. "After 6:" means it waits for
step 6. Times are rough: agent time is wall-clock, RJ time is his hands-on time. Check a step
off when it's done.

1. [x] **RJ** · Phone check: fine for now (2026-10-01). Style changes come as a document (step 5).
2. [x] **RJ** · Ship to the US only (2026-10-01).
3. [x] **RJ** · Stripe sign-in and public details: passkey through Google; support email
   help@robotlantern.com, the Google Voice number, and the privacy page URL (2026-10-01).
4. [x] **RJ** · Self-shipped items: shipped from home (the return address on labels is fine, but
   it never goes on the site), up to about six products at launch (2026-10-01).
5. [ ] **RJ** · The document of site style changes, dropped in `inbox/`. *your pace*
6. [ ] **RJ** · Sales tax registration (docs/SALES-TAX.md): check whether the LLC already has a
   West Virginia Business Registration Certificate (MyTaxes). If it doesn't: get the EIN, then
   the certificate. *10 min to check; an hour or two if both are needed*
7. [ ] **RJ** · For each self-shipped product: a name, a few photos, the price, how many, and
   its packed weight or what you'll charge to ship it. Drop them in `inbox/`. *10 min each*
8. [ ] **Agent** · About's prose into Markdown RJ can edit (task 14). *15 min*
9. [x] **Agent** · Shop build in test mode (task 7): product files, Payment Links, the order
   Worker (Gelato drafts; self-shipped orders show in Stripe), Stripe Tax set up in the sandbox.
   Done 2026-10-01 ([docs/SHOP.md](SHOP.md)).
10. [ ] **Agent** · Mockups for the tee, mug and tote. *30 min*
11. [x] **Agent** · Cloudflare project, deployed to a Cloudflare address (kept out of search
    engines) for RJ to check; record every current DNS record for robotlantern.com, above all
    Google Workspace mail. Done 2026-10-01: https://site.robotlantern.workers.dev
    ([docs/HOSTING.md](HOSTING.md)).
12. [ ] **Agent** · Shop policy pages (shipping, returns, refunds, with handmade items final sale
    except for shipping damage) and the Stripe sections of privacy and terms. *30 min*
13. [ ] **RJ** · After 8: Rewrite the About page in its Markdown file. *your pace*
14. [ ] **Agent** · After 7: A product folder and listing draft for each self-shipped item. *30 min*
15. [ ] **RJ** · After 10 and 14: Pick the launch products and approve their mockups and
    listings. *20 min*
16. [ ] **Agent** · After 9, 12 and 15: Listings live in test mode: copy, prices, Payment Links.
    Quote a sample of each printed product. *45 min*
17. [ ] **RJ** · After 16: Order one sample of each printed launch product. **Costs money**: the
    quotes come from step 16. A quality check, not a gate. *15 min*
18. [ ] **RJ** · After 16: Run a test-mode purchase of a printed product and a self-shipped one
    through their Payment Links (test card 4242 4242 4242 4242); check the Gelato draft and the
    Stripe notice; delete the drafts, including the two the shop build's tests left. Create the
    Worker's restricted live Stripe key (docs/SHOP.md, "Launch"). *20 min*
19. [ ] **RJ** · After 6: Once the EIN arrives, change Stripe's business details to Robot Lantern
    LLC. *15 min*
20. [ ] **Agent** · After 6 and 19: Turn on West Virginia in Stripe Tax (live), with the
    registration's start date. *10 min*
21. [ ] **Agent** · After 5: The style changes. *depends on the list*
22. [ ] **RJ** · After 11: Check the Cloudflare copy (https://site.robotlantern.workers.dev).
    Say whether to add SPF and DMARC for mail (there are none; docs/HOSTING.md). Add
    robotlantern.com to Cloudflare (dashboard, free plan), or give the API token Zone and DNS
    edit for the change window. *15 min*
23. [ ] **Agent** · After 22: Enter the DNS records in Cloudflare and compare them with the old
    ones (docs/HOSTING.md, "Cutover"). *15 min*
24. [ ] **RJ** · After 23: Switch the nameservers at DomainRegistry.com to Cloudflare's. Changes
    can take up to a day to spread. *10 min*
25. [ ] **Agent** · After 13, 18, 20, 21 and 24: Launch, once RJ says go: set the launch dates,
    rerun the privacy pass, remove the frozen prototype and the `CNAME` file, switch the shop to
    live (docs/SHOP.md, "Launch"), merge `rebuild` into `main`, push, and deploy to Cloudflare. Check the site,
    a test email and one live checkout page. Printed orders still arrive as Gelato drafts RJ
    confirms. *45 min*
26. [ ] **RJ** · After 17: When the samples arrive, keep each listing, or pause it and send the
    product back to design. *20 min*

### Not needed for launch (2026-10-01)

Any time, in any order:

- **RJ** · Sign the assignment to the LLC (`.private/legal/assignment-to-llc.md`; full legal
  name), scan it, keep it with the LLC's papers.
- **RJ** · Trim the Cloudflare token's Billing and Registrar access, or leave it (agents won't
  call them; docs/CHARGES.md).
- **RJ** · Delete `shopify.env` from the secrets folder.
- **RJ** · Ask QPMN for its API docs (Developer Center, Integration with API); ask Lulu for API
  access when books come up.
- **RJ** · The blanket's three open questions (`products/stargazing-blankets/product.md`).
- **Agent** · Counted short links before the first social or YouTube link (task 17).
- **Optional** · `design/brand/mark-blob.*` can go when RJ's done with it.

## Task notes (through 2026-10-01)

The detail behind that road, and the record of what was done. NOW.md refers to these by task number.

1. **Close Shopify (RJ).** Done 2026-09-30, before the 2026-10-01 bill; RJ removed its links to
   Gelato and QPMN. `shopify.env` in the secrets folder is now dead and can be deleted.
2. **Framework sign-off.** Done 2026-09-23: Astro.
3. **Attribution tool.** Done 2026-09-24 (`tools/attribution/`, [docs/ATTRIBUTION.md](ATTRIBUTION.md)).
4. **Sunset scroll prototype.** Done 2026-09-25. It became the home page; the frozen prototype is
   at `public/prototypes/sunset-scroll/` (tag `sunset-scroll-v1`).
5. **Thought and chat pages.** Done 2026-09-27; RJ approved them on his phone. List and detail
   (`src/components/Reader.astro`): `/thoughts/` and `/chats/` open on the newest piece, the
   list is beside it on desktop and in the site menu on phones, and the column is endless.
   Chats sort by posted or chat date and search. Posted dates live in each chat's `post.json`.
6. **Launch conversation: "It's Always the Pleiades".** Done 2026-09-27: RJ approved the public
   text. The public copy is `src/content/conversations/its-always-the-pleiades/`, generated by
   `.private/conversations/pleiades/make_public.py`; 40 editor's links in `links.json`
   ([docs/LINKS.md](LINKS.md)). Deferred, not for launch: whether other replies showed
   reasoning or search steps worth including; per-message times (the next capture should keep
   them).
7. **First products, on Stripe and Gelato** (RJ, 2026-09-28: no Shopify; nothing with a
   monthly fee). Accounts open and keys checked 2026-10-01 (read-only calls): Stripe (live,
   activated), Gelato, Cloudflare, Slant 3D. The sandbox key (`STRIPE_SECRET_KEY_TEST`) is in
   and works. The products come from the pipeline (task 19): whichever two to four reach
   `listing` first. Shop art is made with AI (RJ, 2026-09-27).
   - **Built in the sandbox 2026-10-01** ([docs/SHOP.md](SHOP.md)):
     `products/<slug>/shop.json`, `tools/shop/sync.py`, the `shop` Worker, Stripe Tax with a West
     Virginia registration, and three sandbox fixtures. Left: real products' files (step 16), the
     live switch at launch, Gelato's status webhooks (with shipping emails, later).
   - How it works: each product is a JSON file in the repo with its price and its fulfillment:
     `gelato` (product UID and print file) or `self` (RJ makes and ships it). The shop page
     links to a Stripe Payment Link per product, which collects the shipping address and charges
     a flat shipping rate. A self-shipped item's link stops after its stock is sold (Payment
     Links' completed-sessions limit). When a payment completes, Stripe calls a Cloudflare
     Worker, which verifies Stripe's signature. For `gelato` it creates the Gelato order; the
     Stripe Checkout Session ID is the Gelato `orderReferenceId`, and the Worker searches for it
     before creating, so Stripe's retries can't place an order twice. Gelato's webhooks carry no
     signature, so the Worker treats them as a hint and re-reads the order from Gelato's API. For
     `self` it leaves the order to RJ (see "Order notices").
   - Products list from their mockups (RJ, 2026-10-01); samples follow as a quality check.
   - Order notices: at launch, RJ turns on Stripe's own emails for successful payments, which is
     how self-shipped orders reach him; the address is in the Stripe dashboard. The Worker's own
     email waits for cutover, when Cloudflare Email Routing can send it for free.
   - Sales tax: Stripe Tax, West Virginia only, live once the state registration exists
     ([docs/SALES-TAX.md](SALES-TAX.md)).
   - Safety: the Worker creates Gelato **drafts** until RJ says otherwise, and RJ confirms each
     one in the Gelato dashboard. Each order also emails RJ. See "Testing without a real charge"
     in docs/CHARGES.md.
   - Site pages that Shopify would have supplied: refund, returns and shipping policies, and
     contact details. Stripe's website checklist wants these before launch (the account is
     already activated). The public contact is an email address (help@robotlantern.com); no
     street address or phone number goes on the site. Stripe's public support address is
     already the registered agent's in Beckley; add help@ as its support email. Rewrite the
     Shopify parts of the privacy, terms and credits pages for Stripe.
   - Later, not for launch: automatic order placement, shipping emails with tracking (needs an
     email service), Stripe Checkout Sessions built by the Worker for carts of several items.
   - Done when a Stripe test-mode payment leaves the right Gelato draft, with the right product,
     file and address, a self-shipped test order shows in Stripe, and RJ has deleted the draft.
8. **Privacy pass.** First run done 2026-09-27 (findings in `.private/privacy/`); nothing flagged
   is a concern (Fairmont, Bogotá and the machines' names can be public). Rerun before cutover.
9. **Cutover.** The host is Cloudflare (RJ, 2026-09-27). Steps:
   - Done 2026-10-01: the site is a static-assets Worker, `site`, at
     https://site.robotlantern.workers.dev (noindex), deployed with `tools/site-deploy.sh`.
     The current DNS records and the cutover steps are in [docs/HOSTING.md](HOSTING.md).
   - Move robotlantern.com's nameservers from DomainRegistry.com to Cloudflare (RJ, by hand): the
     bare domain can't be served by Cloudflare otherwise. First copy every existing record into
     Cloudflare, above all Google Workspace mail (MX, SPF, DKIM, DMARC), or mail breaks. Remove
     the `CNAME` file (a GitHub Pages leftover). The DNS host refuses zone transfers, so check its
     own record list too.
   - The API token can't add a zone or write DNS (zone access is read-only), so either RJ adds
     the zone in the dashboard or adds Zone and DNS edit to the token for the change window.
   - Keep Cloudflare's Bot Fight Mode, challenges, rate limiting and Web Analytics off; the
     privacy page says the site sets no cookies and loads nothing from other sites.
   - Set every essay date marked `datePlaceholder` and every chat's `postedPlaceholder` to the
     launch date (the build warns about each), rerun the privacy pass (task 8), and merge
     `rebuild` into `main`.
   - Done already: 404 page, `robots.txt`, `/sitemap.xml`, favicon set and social image, the old
     landing page's files removed from the root.
   - Remove `public/prototypes/sunset-scroll/`, the frozen copy of the prototype (the tag
     `sunset-scroll-v1` keeps it).
10. **Samwise previews.** Done 2026-09-27; RJ has used them on his phone ([docs/PREVIEW.md](PREVIEW.md)).
11. **Home page, first slice.** Done 2026-09-27; RJ approved it on his phone. The sunset scroll;
    the wordmark docks and its period (the ovaloid) flies in spinning, with a tail along its path;
    cards draw from their stars; the nav sits on the tree silhouette; after landing, the wordmark
    collapses into the monogram menu. Next slices are in docs/HOME.md ("Map", "Open").
12. **Section marks in the nav.** Done 2026-09-27: RJ's marks (one to four stars on dashed
    shapes), with the brand's ovaloids as the stars (`src/components/SectionMark.astro`).
13. **Footer pages: privacy, terms, credits.** Approved, with the licence applied 2026-10-01
    (CC BY-NC 4.0 for essays and chats; RJ's photos all rights reserved). Left: rewrite the
    Shopify parts for Stripe and link the site's own shop policies (with task 7). Gelato's terms
    checked 2026-10-01: it processes order data for Robot Lantern, its printers are
    sub-processors, and **carriers are separate controllers**, so the privacy page should say the
    carrier handles your address under its own policy. OpenAI's terms assign output to the
    user and bar presenting output as human-written; the site's attribution already does the
    opposite. Research notes: `.private/legal/`.
14. **About page and the cast.** At `/about/`, with the intro drafted in RJ's review session.
    RJ rewrites it himself before launch, once its prose is in a Markdown file
    (`src/content/about.md`), leaving the cast's layout in `about.astro`. InkBot Delta is the
    third printer, named at 2 a.m. without the Greek alphabet; there's no Gamma (RJ, 2026-10-01).
15. **Builds.** Done 2026-09-27; RJ checked it on his phone. Each build runs full screen
    (`src/layouts/BuildLayout.astro`) with the monogram as the way home; the Builds page has one
    card per build (`src/content/builds/*.json`). The Sky, Unprojected is copied into
    `public/sky/` from `unprojection-opus` (commit `1b19308`; to update, rebuild there and copy
    `assets/`, `data/` and `photo/`). ESA's Hipparcos and Gaia data is used non-commercially:
    no shop links or promotions on build pages, and no ESA-derived renders on products. Ask ESA
    before any potentially monetized video made from it.
16. **Brand.** Done 2026-09-27 ([docs/BRAND.md](BRAND.md)): RJ's ovaloid period, the
    left-aligned two-line wordmark and a one-line version. On 2026-10-01 RJ's tile (E) became the
    logo: favicon, menu button and the way home from builds, with a new four-frame collapse.
    Open: RJ's phone check.
17. **Analytics** (RJ, 2026-09-30: before the first social link). As recommended in RJ's review
    session: at cutover, use Cloudflare's own traffic totals (no script, nothing to change on the
    privacy page); before the first YouTube link, add counted short links
    (`robotlantern.com/y/<slug>`, a small redirect that counts, one sentence on the privacy page);
    hold Cloudflare's analytics script until RJ wants to know what people read, and update the
    privacy page the same day.

18. **RJ's review fixes, 2026-09-30.** Done 2026-10-01 (screenshots in `inbox/`, which is
    gitignored): the logo is RJ's tile, the right way up; the collapse is four timed frames,
    each one a whole cream tile; the one-line wordmark heads the menu; the logo has room in the
    reading bar and keeps its tile everywhere; the section nav sits at the bottom of every page
    on a dark bar; Thoughts' mark is a star with a short dashed tail in the nav and the menu alike; the status bar takes the
    page's color (tested in the iOS 26 simulator). Left: RJ's phone check.
19. **Product pipeline.** Done 2026-10-01 ([docs/PRODUCTS.md](PRODUCTS.md)): one folder
    per product in `products/`, staged idea → sketch → feasibility → design → sample → listing →
    live, with RJ deciding at each gate. `python3 tools/products/board.py` shows where everything
    is and who it's waiting on. Seeded with the stargazing blankets, night sky photo prints and
    the wordmark tee, mug and tote.

20. **Second chat: "The Hard Problem of Alignment"** (RJ with Claude Opus 5.5, 2026-09-29).
    Captured from RJ's claude.ai export into `.private/conversations/capability-separation/`
    (NOTES.md there). RJ's answers, 2026-10-01: that title, Opus 5.5, all 18 messages, keep the
    course detail. The public copy is generated by that folder's `make_public.py` into
    `src/content/conversations/the-hard-problem-of-alignment/`, with the three citations where
    the export marks them, the fetch and reasoning summaries collapsed, and 40 editor's links
    (`links.json`, checked). RJ approved the text 2026-10-01; it's published. Later: show
    per-message times, which this capture keeps and the page doesn't display yet. It may also
    seed an essay.

## Log (2026-09-23 to 2026-10-01)

- 2026-09-23: Fresh start. Cloned the live site repo and created the `rebuild` branch.
- 2026-09-23: Enforced HTTPS on robotlantern.com. Its DNS is at `hosting.businessidentity.llc`
  (registrar DomainRegistry.com), not Porkbun.
- 2026-09-23: Reviewed the Codex prototype. The essay design is close to final. Attribution looks
  GPT-heavy for three reasons:
  - The footer blends the essay body (92% RJ) with the footnotes (88% GPT), which are half the
    post's characters, so the whole post reads 52% / 48%.
  - Copyedits are painted as authorship across RJ's sentences.
  - The matcher lets GPT's first draft claim spaces and common words in text RJ wrote later.
- 2026-09-23: Wrote docs/CHARGES.md (task 1). Shopify no longer offers Starter to new stores, so
  the real choice is keeping Basic or pausing. Gelato's default instant approval means a Shopify
  test order for a Gelato product can be produced and charged.
- 2026-09-23: RJ decided to pause Shopify before the next bill unless the shop is built. The billing
  history shows bills every 30 days (last one 2026-09-01), so the next is 2026-10-01, not 10-02.
- 2026-09-23: RJ signed off on Astro (task 2). The site's overall look is the night sky, replacing
  the prototype's light cream. Task 3 was reframed: attribution comes from Git history for new
  articles, and the first essay's chat drafts are a second input to the same tool.
- 2026-09-24: Built the attribution tool (task 3). First essay: body 91% RJ / 9% GPT, footnotes 13%
  RJ / 87% GPT, with GPT's 22 surviving copyedits kept in RJ's color. The new rules fold stray
  matched words into rewrites and stop spaces and word fragments from switching owner, which
  also narrows the copyedit decision from 92/96 to 91/92.
- 2026-09-24: RJ spot-checked the first essay's preview and approved it. He adopted the strict copyedit
  rule (copyedits are judged by form, never by size), and a copyedit agent commits under its own
  name with the trailer. Task 3 is done.
- 2026-09-24: Replaced the launch conversation with "It's Always the Pleiades" (task 6). Location
  redacted: coordinates removed, "[your town]" for the city, compass screenshot cropped. Image
  metadata stripped. Citations and one reply's text still need recovering.
- 2026-09-25: Recovered the Pleiades citations by asking ChatGPT in the app for its sources (v1).
  It returned 28, all real and on-topic: 24 in the published range and 4 from later turns. The
  29 markers are 28 web citations, four of them repeats, plus a link to the annotated image.
  Drafted a versioned citation request (docs/CITATIONS.md) and a v2 prompt that keeps positions.
- 2026-09-25: Ran citation prompt v2. It confirmed the order and three of the four inferred
  repeats, and missed one citation. Put all 28 citations into the public copy with checked
  titles, and withheld the timeanddate link because it names the town. The image reply was the
  image alone; its reasoning summary came from the iPhone app. RJ approved the import and
  citation rules and adopted "don't make it any worse" for privacy, with a pass before cutover.
- 2026-09-25: Built the sunset scroll prototype (task 4). The sky is one tall gradient taken from
  the sunset photo's colors, with the star photo fading in below it. The Pleiades appear once, in
  the last screen. A fixed horizon glow, afterglow and treeline (cut from the sunset photo)
  give each screen a real-sky shape. The wordmark starts as a silhouette, and its period lights
  up as the lantern and warms the letters. The script is 566 bytes. Photo metadata, including the
  sunset photo's GPS, is stripped.
- 2026-09-25: Adopted Samwise previews: build on Sarcean, push to Samwise, test on the phone over
  trusted HTTPS on the LAN. GitHub keeps only the live site until something is published
  (docs/PREVIEW.md). The site repo's remote now uses the `github.com-robotlantern` SSH alias.
- 2026-09-25: Set up the Samwise previews: a `static-preview` stack behind `web-gateway`, bare
  repos with a build-on-push hook, LAN DNS for rl, sky-astra and sky-opus under rblt.io, and
  public records failing closed at 192.0.2.1 (Porkbun API, snapshots in ~/work/admin/domains).
- 2026-09-25: Sunset scroll round two (task 4). The stars are now RJ's Pleiades photo on a fixed
  layer that fades in and drifts 6vh over the whole scroll, replacing the tall tiled field. There
  are two versions of the photo, as taken and contrast-enhanced. The tree in the photo's corner is
  cropped out and its GPS is stripped.
- 2026-09-25: iOS 26 Safari colors its bottom toolbar from the fixed layer it finds a little way
  above the bottom edge, ignoring that layer's opacity. A 4px dark strip wasn't enough, and a
  24px one works. Checked on RJ's iPhone through iPhone Mirroring. The simulator's Safari
  settings page was blank, so the simulator couldn't switch to the Bottom tab layout.
- 2026-09-25: RJ signed off on the sunset scroll (task 4). He and Claude designed how content
  enters the home page and how a constellation map could work as navigation. Recorded in
  docs/HOME.md, with the first slice as task 11.
- 2026-09-26: Scaffolded Astro and ported the essay and conversation pages (task 5), restyled for
  the night. The essay's highlighting covers all 8,191 counted characters. Checked at phone and
  desktop widths. Chose task 5 before 11 because the first home card uses the conversation style.
- 2026-09-27: RJ reviewed the preview. Dropped "Inside this post" and Exact Markdown; an
  essay's editing chat is published only if it's interesting as a chat. Named the sections
  Thoughts, Chats, Builds and Shop. RJ is "RJ" except in his bio. Chats now read like a chat
  app. Design rules are in docs/PAGES.md.
- 2026-09-27: RJ picked full-column chat replies and set his bio. Added the Pleiades chat's 37
  editor's links (task 6) and a link checker. Haiku, proposing blind, found 78% of RJ's picks.
- 2026-09-27: The sunset scroll is now the live home page (`/`). Chat dashes moved to the right
  edge, fainter. Task 12: the nav's section icons are asterisms fitted to real stars in RJ's
  photo.
- 2026-09-27: The asterism nav was retired for section marks: an asterisk, a circle, a pentagon
  and a diamond after each name, each with one star.
- 2026-09-27: Home page first slice (task 11): the wordmark docks, its period flies in as a
  shooting star, and the Pleiades chat and the essay draw as cards.
- 2026-09-27: First privacy pass (task 8): media and history are clean; decisions for RJ are in
  `.private/privacy/`.
- 2026-09-27: Added the footer pages (About with the cast; privacy, terms and credits being
  drafted), and embedded The Sky, Unprojected as the first build.
- 2026-09-27: RJ's section marks in the nav; the comet glides. Brand exploration started (task 16):
  spark concepts, wordmark lockups, and a sheet of every Google Fonts asterisk.
- 2026-09-27: Builds run full screen and the Builds page has screenshot cards. Thoughts and
  Chats open on the newest piece, list and detail, endless. The chat links to its build.
- 2026-09-27: The brand rolled out site-wide: ovaloid period and stars, new wordmark, favicon
  set, and the wordmark collapsing into the monogram menu on every page.
- 2026-09-27: RJ's review session (read-only, with another agent) answered most open decisions:
  Cloudflare hosting, the LLC holds everything, West Virginia, 7-year order records, Google
  Workspace mail, AI shop art, no ESA email for now, a minimal Uploader privacy section, the
  Pleiades text approved, and tasks 5, 10, 11, 12 and 15 approved on his phone. Applied to the
  pages and docs.
- 2026-09-28: RJ dropped Shopify. The shop becomes Stripe Payment Links, a Cloudflare Worker and
  Gelato's order API, with no monthly fee, and Shopify closes before its 2026-10-01 bill. Gelato's
  API takes orders by product UID with no connected store, has no test mode, and sends unsigned
  webhooks, so the Worker creates drafts at first and re-reads webhooks from the API.
  docs/CHARGES.md now covers Stripe.
- 2026-09-30: RJ canceled Shopify before the 2026-10-01 bill. Nothing had been created in the
  store. Licensing decisions taken as recommended: CC BY-NC 4.0 for essays and chats, photos all
  rights reserved (not yet applied to the site or the footer pages). Accounts (Stripe, Gelato,
  Cloudflare) come next; the design feedback waits.
- 2026-10-01: RJ's review applied (task 18): his E tile is the logo, the collapse is four timed
  frames, the nav is at the bottom of every page, and the status bar takes the page's color.
  iOS 26 Safari tints the status bar from the topmost opaque fixed layer at the top edge (it
  ignores transparent ones), else from the page's background color. Keys checked for Stripe
  (a live restricted key; the account is activated), Gelato, Cloudflare (account token, zone
  access read-only) and Slant 3D; QPMN's API docs come on request. Licence applied to Terms and
  Credits. The asterism crops are retired; `inbox/` is gitignored.
- 2026-10-01: Captured the second chat from RJ's claude.ai export (task 20). The export keeps
  per-message times and the app's reasoning summaries, not the reasoning itself. Its first
  message carries injected context, including RJ's memory snapshot, which is never published.
- 2026-10-01: Product pipeline adopted (task 19): `products/` and docs/PRODUCTS.md, with a board
  script. The Stripe sandbox key works, so the shop build (task 7) is unblocked.
- 2026-10-01: NOW.md reorganized around one ordered road to launch, in two tracks (site, then
  shop), with `tools/next.py` printing RJ's next steps.
- 2026-10-01: The site and the shop launch together (RJ). Products list from mockups, with samples
  as a quality check instead of a gate, and RJ can sell limited runs of things he makes and ships
  himself. The road to launch is one list again.
- 2026-10-01: RJ's answers: phone check fine (style changes to come), US only, Stripe sign-in by
  passkey with its public details set, about six self-shipped products from home, no photo prints.
  Sales tax worked out (docs/SALES-TAX.md): Stripe Tax for West Virginia only, which needs the
  state's Business Registration Certificate, which likely needs the EIN first. The road to launch
  is now 26 steps, 4 done.
- 2026-10-01: Steps 9 and 11. Cloudflare: Wrangler now turns a new Pages project into a Worker,
  so the site is a static-assets Worker on a new free `robotlantern.workers.dev` subdomain, not
  `pages.dev` (its auto-setup also rewrote the Astro config; reverted). DNS records recorded:
  Google Workspace MX and DKIM, no SPF or DMARC. Shop: product files, a sync script, Payment
  Links and the order Worker, tested in the sandbox without a browser. Gelato has no sandbox:
  both keys reach one account, so two test drafts are in RJ's dashboard.
