# Now

_Last updated 2026-11-19._

## Start here

**Goal (RJ, 2026-11-19): launch on 2026-11-20, in the afternoon, with one product working end to end.** Someone
orders on robotlantern.com, Stripe takes the payment, Slant 3D prints and ships, and our backend handles
everything in between. The product is the two-part stencil ornament made from a photo
([products/cutout-ornament/product.md](products/cutout-ornament/product.md)). Everything else waits until
after launch.

How it works at launch ([docs/ORDERS.md](docs/ORDERS.md) has the contracts and
[docs/PRODUCTION.md](docs/PRODUCTION.md) the running of it):

1. On the product page, the customer adds a photo and crops it to the head. Our Worker sends it to OpenAI's
   GPT Image API, which redraws it as a two-colour stencil. The customer gets at most three tries per photo,
   and spending is capped (decision 21).
2. The browser draws the ornament from that drawing in the colours the customer picks, with an optional
   name tag. The customer orders and pays on Stripe's page.
3. Every hour, a Claude routine in the cloud builds both STLs from the drawing and checks them against the
   preview the customer approved. It uploads them to Slant and asks our Worker to draft the Slant order.
   Then it emails RJ.
4. **RJ processes the draft in Slant's dashboard.** That's when Slant charges, and it's RJ's only routine step
   per order. Slant prints and ships the ornament.

**What RJ does and decides is in "Road to launch", steps 1–6, 13 and 17.** Everything else is an agent step.
`python3 tools/next.py` prints what's ready. Agent steps start with: "Read AGENTS.md and NOW.md, then do step
N." Start build sessions at medium effort (high for steps 9 and 10), each in its own worktree. Step 14 merges
them.

The ornament design work so far lives in the scratch folder `../ornaments-design-session/`, which isn't in Git
(decision 15). Step 7 moves its code into the repo, but no family designs. Its `PRINT-QUEUE.md` lists what's on
MeltBot.

## Decisions

1–15 are from 2026-11-10 to 11-17. Where 16 onwards differs, 16 onwards wins.

1. **Launch cut** (superseded by 18). The site launches once the first product can be ordered. The other
   lines open as their prototypes pass.
2. **Merch waits.** The tee, mug, tote and blankets are parked until after launch.
3. **You make everything at first**, with a weekly cap per product, and a product moves to Slant after one
   paid test order (the pet ornament's is step 17).
4. **Pay, then check, then make.** Customers pay at checkout. Every order is checked before it's made, and a
   photo that won't work gets an email from help@ (swap it or a full refund).
5. **Uploads go to Cloudflare Workers KV on the free plan.** Unpaid uploads delete themselves after two days.
6. **Photos are deleted 60 days after the order ships**, with everything made from them. Order records
   without photos are kept seven years. Customer photos never go into marketing without written OK.
7. **Lithophane ornaments are white at launch and for LED lights only** (when that line opens).
8. **The projector gets our own generator**, with credit to threonin's projector on the Credits page.
9. **Lines that aren't ready show "coming soon"**, with an email link to signup@. Nothing is stored.
10. **Pictures are honest.** Real prototypes, or renders marked as renders. Example photos are yours,
    family's with their OK, or AI-made stand-ins marked as such.
11. **The About rewrite and the style changes don't hold launch.**
12. **Platforms:** Instagram, Facebook and Pinterest first.
13. **First product: the pet ornament** (RJ, 2026-11-13). Its open questions are settled by 16 and 19.
14. **Slant fulfils the pet ornament from launch** (RJ, 2026-11-17), in any two of Slant's PLA colours.
    Listing photos are our own Meltbot prints, marked as examples.
15. **The ornament designs stay out of printdb and Git** (RJ, 2026-11-17). They come from family photos. Code
    and generic briefs may go in the repo; family drawings, photos and names may not.
16. **Customer drawings come from GPT Image through OpenAI's API** (RJ, 2026-11-19), not RJ's subscription.
    So a customer's photo goes to OpenAI before they order, and the privacy page says so first (step 11).
    Right after launch, cheaper models and settings are tested.
17. **Production runs in Claude cloud environments** (RJ, 2026-11-19), with scheduled routines that have
    only the access their job needs. Sarcean is for building and is the manual fallback.
18. **Launch scope** (RJ, 2026-11-19): the stencil ornament only, end to end, on 2026-11-20. The interactive
    explainer, the video and new variants are welcome if agents finish them alongside, but don't hold launch.
19. **No proof by email** (agent's default under RJ's direction, 2026-11-19). The preview the customer
    approves is the proof. The routine checks the build against it, and anything that doesn't match goes to
    RJ ("Needs you") rather than to Slant.
20. **Defaults the agents have taken** (2026-11-19; RJ changes any of them by saying so):
    - **Price: open, pending step 19's research** (RJ, 2026-11-19). RJ wants margins as low as is sustainable,
      to sell volume in a crowded space. $29 with US shipping and the name tag included is a placeholder for
      building and testing until step 19 sets the price and any volume promotion.
    - **Orders:** a weekly cap of 25, and "order by Dec 10 for Christmas" until the acceptance order
      shows Slant's real timing.
    - **Remake promise:** a free remake or a refund if it arrives broken or doesn't match the preview.
    - **Who's in it:** pets at launch. People are added once decision 25 says so.
21. **Image spending** (confirmed by RJ, 2026-11-19). $25 of prepaid credit at OpenAI, with auto-recharge off, so the balance
    is a hard cap. Our Worker also stops drawings at an estimated $10 a day, 3 tries per photo and 6
    drawings per visitor a day.
22. **Put `rebuild` on GitHub** (confirmed by RJ, 2026-11-19). After the privacy pass (step 8), push `rebuild` to the public
    GitHub repo, because cloud routines can only run code from GitHub. Until now only `main` went there
    (docs/PREVIEW.md).
23. **Two cloud routines that email RJ** (confirmed by RJ, 2026-11-19). `rl-orders` runs hourly from 7:00 to 23:00 and
    `rl-daily` once a day (docs/PRODUCTION.md). They email RJ and no one else. Customer shipping emails are
    Gmail drafts that RJ sends himself until he says otherwise.
24. **Soft launch without asking again** (confirmed by RJ, 2026-11-19). Once steps 14 and 16's checks pass, an agent switches
    robotlantern.com to the new site. Nothing is announced until RJ's own order (step 17) works.
25. **People at launch: yes** (RJ, 2026-11-19: the heads are proven). The page offers "pet or person". Photos of
    the three test people go in marketing only with their OK.

26. **The tooling is for any subject, and an order can hold several ornaments** (RJ, 2026-11-19). The builder
    doesn't care what the drawing shows, so a church or school for its minister or principal, or a family's
    childhood home, uses the same path as a pet. Launch can still offer pets only, but nothing in the Worker,
    the page or the routine may assume pets or one ornament per order:
    - Subjects are data. The product file lists them, each with its brief (`briefs/<subject>.md`), its
      crop hint and its label, so adding "place" is a brief and a line, not a code change.
    - An order is a list of designs, each with a quantity, shipped in one Slant box. Slant's shipping barely
      grows with count (docs/CHARGES.md: one ornament costs $10.95 at Slant, a dozen $4.87 each), so volume
      pricing comes from this. Step 19 sets the prices.
27. **Places come after launch, but the launch code is ready for them** (orchestrator's call under RJ's direction,
    2026-11-19, from the buildings test). All 12 test buildings drew and built cleanly with a "place" brief and
    the unchanged builder. But the head crop, the fixed name tag, the ring's position and the lack of a height
    limit look wrong on some buildings, and fixing them the day before launch risks pets and people. So:
    - Before launch, the three fixes that protect every subject: a size limit, a detail-loss check and a shared
      name-tag fit test (step 7's follow-up, and step 10).
    - The page takes its crop mode (fill or fit) from the subject, so places need no page change later.
    - "Place" is the first addition after launch ("Not needed for launch").
    - Until then, RJ can take church, school and company orders by hand, building them with `make.py` and
      checking the proof himself.

RJ processes every Slant order himself (decision 14 stands). That's the one recurring cost.

## Road to launch

Steps run in dependency order, not number order: a step can start once its "After" steps are done. Check a
step off (`[x]`) when it's done.

### Tonight: RJ's setup (each one unblocks agents; any order)

1. [x] **RJ** · Answer decisions 21–24 in one reply: all four confirmed (2026-11-19).
2. [ ] **RJ** · Cloudflare ([docs/HOSTING.md](docs/HOSTING.md), "Cutover"):
   - In the dashboard, add robotlantern.com on the Free plan. Stop when it shows two nameservers, and don't
     change anything at the registrar yet.
   - Under My Profile → API Tokens, edit the agents' token to add Zone · DNS · Edit and Zone · Workers
     Routes · Edit for robotlantern.com.
   - Say yes or no to SPF and DMARC for mail (yes recommended).
3. [ ] **RJ** · OpenAI API (decision 21; [docs/CHARGES.md](docs/CHARGES.md)), at platform.openai.com:
   - Create a project called "Robot Lantern shop".
   - Under Billing, buy the prepaid credit with auto-recharge off.
   - In the project's limits, allow only the image models.
   - Create a project API key and save it as `OPENAI_API_KEY=` in `~/.codex/secrets/robot-lantern/openai.env`.
   - If the API asks for organization verification, do it under Settings → Organization (it wants ID).
4. [ ] **RJ** · Stripe, live mode ([docs/SALES-TAX.md](docs/SALES-TAX.md), step 5):
   - Under Developers → API keys, create a restricted key `shop-worker-live` with Checkout Sessions: Write,
     and Products and Shipping rates: Read. Save it as `STRIPE_SECRET_KEY_LIVE_WORKER=` in `stripe.env`.
     Step 16 says if the first live call needs anything more.
   - Under Tax → Registrations, add West Virginia, choosing "Start collecting immediately", with the
     Combined Sales and Use account number.
   - Turn on email receipts for successful payments, and your own email for successful payments.
5. [ ] **RJ** · Claude cloud ([docs/PRODUCTION.md](docs/PRODUCTION.md), "Cloud environments"), at
   claude.ai/code:
   - Connect GitHub, and give the Claude app access to `robotlantern/robotlantern-site`.
   - Create the environments `rl-production` and `rl-dev` exactly as listed, pasting each network secret
     from the file named there.
   - Leave only Gmail connected for routines (connect it if it isn't).
6. [ ] **RJ** · Prints and photos:
   - On MeltBot, print `Orn-Stencils-Tray-1` (the heads) and then `Orn-Stencils-Tray-2` (Tucker), in ELEGOO
     Matte Ruby Red.
   - Put Tucker and the three heads together. Photograph them with Buster, front-on against a plain
     background and hanging on the tree.
   - Put the photos in `.private/products/cutout-ornament/listing-photos/`.
   - Answer decision 25.

### Build: agents, in parallel, each in its own worktree (step 14 merges them)

7. [ ] **Agent** · Ornament tools into the repo, in `tools/ornament/` (docs/ORDERS.md, "Recipe"):
   - The builder and name-tag code from the scratch folder, with today's defaults (1.8 mm necks and bridges).
   - The five stencil fonts and their OFL licences in `public/shop/fonts/`, used by both the builder and the
     page.
   - Generic GPT Image briefs for a pet and a person in `products/cutout-ornament/briefs/`, with no names or
     family details.
   - `make.py` (order folder → `out/`) and a stdlib Slant client that uploads and quotes but never drafts.
   - `requirements.txt` pinned to docs/PRODUCTION.md's versions.

   Done when `make.py` reproduces build-v6 for two pets locally (their art stays out of Git) and passes on a
   drawing made for the test.

   Follow-up on the same branch, before step 14 (decision 27; the buildings test found these, and they apply to
   every subject):
   - A size limit: the art fits a box (80 mm wide, at most 110 mm tall), and a check fails a base outside it.
     Without it, a tall drawing printed 84 × 270 mm with every check passing.
   - A "white kept" check: the cut-out area in the proof divided by the cut-out area in the drawing. Below 0.8
     it fails, because the gap-fill has silently removed features the customer saw (outline-drawn windows,
     for example). Good builds score 0.9–1.1.
   - The name-tag fit test as a function the page can mirror, so the page refuses text that won't fit before
     checkout. Counting 16 characters isn't enough: "Fairmont General" fails.
8. [ ] **Agent** · After 1: Privacy pass over everything `rebuild` would publish, files and history (AGENTS.md
   rule 7). Then push `rebuild` to GitHub (decision 22) and make the desktop app see the GitHub remote, so
   cloud sessions can start. Report anything that had to change.
9. [ ] **Agent** · The order Worker for the ornament (docs/ORDERS.md, "Contracts"):
   - The drawings API to OpenAI, with decision 21's caps and an off switch.
   - Ornament orders that point to a drawing.
   - The queue endpoints, signed proof links, and purge of the new files.
   - The Slant draft endpoint, which only ever dry-runs in the sandbox.
   - The live KV namespace, and the fix for `fulfil()` demanding a Gelato key on photo orders.
   - Decision 26: subjects come from the product file, an order holds several designs with quantities, and
     the price comes from the product file's tiers.

   Extend `tools/orders/test_order.py` with OpenAI stubbed, and make one real drawing call after step 3.
   Deploy to the sandbox Worker.
10. [ ] **Agent** · The product page, `/shop/cutout-ornament/` (docs/ORDERS.md, "The page"):
    - Photo, square crop on the head, and the drawing request (stubbed until step 9 lands).
    - The preview drawn in the browser from the drawing.
    - The scratch folder's picker (colours, pairs, swap, name tag, self-hosted fonts).
    - The order button, the thank-you page, and the shop page linking here.
    - Decision 27: the subject also sets the crop mode, "fill" (crop to the square) or "fit" (letterbox in
      white). The name tag uses the builder's fit test, not a character count.
    - Decision 26: wording and crop hints come from the subject, so no "pet" is hard-coded; a quantity for
      each design; "add another design" to the same order; the price shown from the product file's tiers.

    Check it at 375 px on the preview host, with a drawing made for the test.
11. [ ] **Agent** · After 1 and 19: Words and pages:
    - Privacy, terms, shipping and returns for this product: OpenAI makes the drawing, Slant prints and
      ships, the remake promise, and how long things take.
    - The product's copy and FAQ, and `shop.json` with decision 20's price and options.
    - The home page leading with the product: one plain section and a link, with the sunset scroll kept.

    docs/PAGES.md's rules apply.
12. [ ] **Agent** · After 2: DNS (docs/HOSTING.md, "Cutover"):
    - Enter every record in Cloudflare and compare them with the old host's.
    - Keep the GitHub Pages records, DNS-only, until step 16.
    - Add SPF and DMARC if RJ said yes.
    - Give RJ the two nameservers.
13. [ ] **RJ** · After 12: At DomainRegistry.com, replace the nameservers with Cloudflare's two. Mail and the
    old site keep working while the change spreads. Cloudflare emails you when the site is active, so tell an
    agent then.

19. [ ] **Agent** · Price research (RJ, 2026-11-19). RJ's instinct is margins as low as sustainable, to sell volume
    in a crowded space where the idea alone doesn't show how competitive we are.
    - Start from `products/cutout-ornament/market-research.md`. Re-check the prices it took from search snippets, and
      add current Christmas 2026 prices for custom pet ornaments that compete for the same buyer: printed-photo,
      3D-printed, laser-cut and wood, on Etsy and elsewhere, including their shipping.
    - Our cost floor per ornament (docs/CHARGES.md): Slant parts and shipping, measured 2026-11-19 by place and by
      count ($10.95 for one ornament to WV, $4.87 each for a dozen, $4.26 each for 50), Stripe, and drawings,
      including those for people who don't buy. Slant's API quotes give no volume discount; research whether
      Slant offers one any other way (its business or bulk program).
    - Buyers beyond pet owners (decision 26): a church, school or club ordering a dozen or more of one design,
      and families with several designs. Price the tiers for them too, even though launch offers pets only. Also, where a low-margin price lands
      against the field.
    - Volume promotions:
      - several ornaments in one order sharing one Slant shipment (decision 26 builds this in; step 19 sets
        the tiers);
      - a code for a second order (Stripe promotion codes are free);
      - a launch price.
      Note which of these launch can carry without new build work.
    - Ends with a recommended price and promotion written into decision 20 and `products/cutout-ornament/`, for
      RJ's one-line yes. Steps 11 and 16 use it.

### Integrate, launch, accept

14. [ ] **Agent** · After 7, 9 and 10: Integration:
    - Merge the branches into `rebuild`.
    - Place one sandbox order through the real page with a stand-in photo: a real drawing, which counts
      against the cap, and Stripe's test card.
    - Do the order run by hand from this checkout, as docs/PRODUCTION.md describes it: build, checks, proof,
      Slant upload and quote, the Worker's draft dry run, and the email to RJ.
    - Push to `samwise` for RJ's phone. Fix what breaks.
15. [ ] **Agent** · After 5, 8 and 14: Production routines (docs/PRODUCTION.md, decision 23):
    - Create `rl-orders` and `rl-daily` in `rl-production`.
    - Run each once against the sandbox, and check the email that reaches RJ.
    - Write down anything the cloud did differently.
16. [ ] **Agent** · After 1, 3, 4, 11, 13 and 14: Soft launch (decision 24; docs/SHOP.md, "Launch"; docs/HOSTING.md,
    "Cutover"):
    - The live Stripe objects (`sync.py --live`) and the live webhook.
    - The Worker's live secrets, loaded from the secrets folder.
    - `robotlantern.com/api/*` routed to the Worker, and `SHOP_MODE` set to live.
    - Merge `rebuild` into `main` and push. Remove `CNAME` and the frozen prototype, then deploy.
    - Attach the custom domains (this is when the new site goes live) and drop the GitHub Pages records.
    - Check the site, a drawing, and one live checkout page without paying.
17. [ ] **RJ** · After 15 and 16: The acceptance order:
    - On your phone, order one ornament on robotlantern.com with your own card. This is a real charge.
    - When the routine's email says it's ready, process the draft in Slant (Slant charges you).
    - Tell an agent what Slant charged for shipping, and when the ornament arrives.
    - If it all worked, say "announce". You can refund yourself in Stripe; Stripe keeps its fee.
18. [ ] **Agent** · After 17: Announcement kit (docs/MARKETING.md; decision 12): first posts for Instagram,
    Facebook and Pinterest, made from the listing photos and with the order-by date. RJ posts them. Set the
    order-by date from the acceptance order's timing.

### Not needed for launch

These can run in parallel, at any time. ☁ marks tasks that can run in the `rl-dev` cloud environment while RJ
does other things.

- ☁ **Agent** · "How it's made", an interactive: photo → drawing → stencil → ornament, for the home and
  product pages. It's built from a stand-in example, marked as one (decision 10).
- ☁ **Agent** · An explainer video, about 20 seconds and vertical, for the product page and social. It's
  self-hosted: no YouTube embed, because the privacy page promises no requests to other sites.
- **Agent** (on Sarcean, with the OpenAI key) · Cheaper drawings, right after launch (decision 16):
  - Run the same ten test photos through GPT Image at lower quality settings and through cheaper models.
  - Make a table of the cost and the pass rate.
  - Switch `shop.json`'s model if a cheaper one passes RJ's look.
- **Agent** · Variants that need no prototype, with builder flags, Slant quotes, preview support and renders.
  RJ says yes on the renders.
  - Large: about 150 mm, filling a plate.
  - Wall: the ring left off, with an adhesive strip from Slant's components in the box. The ring already
    hangs flush on a nail.
- **Agent + RJ** · Variants that need a print:
  - A kickstand, print-in-place or slot-in.
  - Standard shapes (star, bell, round).
  - The bridge placement for people.
- **Agent** · Places, the first addition after launch (decision 27). The buildings test's folder
  (`../ornaments-design-session/buildings-01/`) has the brief, the photos and their licences.
  - Ring placement that can't land in a notch beside a tower.
  - A shorter name tag for wide art, or the name set into the ground band.
  - Add `briefs/place.md` and the subject to the product file, then re-tune on the API model with 3 tries per
    photo.
  - Marketing: the courthouse, the covered bridge, the country church and the lighthouse (public domain).
    Never use institutions' names or logos in our copy.
- **Agent** · Later automation:
  - Shipping emails sent automatically, once RJ has seen a few drafts.
  - Slant's webhook.
  - `rl-orders` fired by the Worker when an order is paid, instead of hourly.
  - A monthly export of the order records.
- **Agent** · The other photo products from the 2026-11-10 plan: the lithophane ornament and lamp, cutouts,
  pop-outs and the projector. Their steps are in [docs/LOG.md](docs/LOG.md).
- **RJ** · Sales tax: from launch, the monthly WV return includes sales (Stripe Tax's report). Still ask the
  Tax Department whether quarterly filing is allowed (docs/SALES-TAX.md).
- **RJ** · Materials: tan, brown and bone-white PLA for photos of Lily, Toby and Wiggles. It's a charge, so
  list options with prices first.
- **RJ** · From the earlier list:
  - The style changes document in `inbox/`, and the About rewrite (an agent first moves the text into
    `src/content/about.md`).
  - Delete Gelato's two test drafts.
  - Sign the LLC assignment (`.private/legal/`).
  - Trim the Cloudflare token's Billing and Registrar access.
  - Delete `shopify.env`.
  - Sort the untracked files from 2026-09-30 (`design/brand/…`, `prompts/`).
  - Ask QPMN for its API docs and Lulu for API access.
  - The sticker sample (a charge).

## Parked

- Brand merch and the stargazing blankets, until after launch (decision 2).
- The photo jack-o'-lantern (3d-modeling `jack-o-lantern/`), for Halloween 2027.
- Essay: why the machines have names. Post: what "the model" means in a chat app.
- `unprojection-astra` stays off the site for now.
- Large files later: video on YouTube, big downloads on Cloudflare R2 (a card on file; CHARGES.md first).
- The mosaic ornament engine, `tools/cutout/`, superseded and kept for reference.
- Secret Santa QR snowflakes (`tools/qr-ornament/`), parked 2026-11-19 in favour of the tag pair.
- Secret Santa tag pair (`tools/tag-pair/`): test v2 is uploaded to MeltBot as `Tag-Pair-Coupon-v2.gcode`
  (printdb print 172). RJ picks it up in another session if it works mechanically.

## Log

Entries before 2026-11-19 are in [docs/LOG.md](docs/LOG.md).

- 2026-11-19 (evening): RJ reports the pet and person heads are proven. Decision 25 is settled: people are
  a launch subject, and photos of the three people still need their OK before they appear in marketing. RJ
  asked for four test sessions, run one at a time by the orchestrating session, which logs its decisions here:
  1. **Buildings** (a church, a school, a hospital, then 12 photos in all). It reports first.
  2. **Agent-friendly ordering**: instructions for LLM agents, and agentic checkout. It runs second, not
     fourth, because RJ called it the #1 thing to settle today and it shapes the Worker's contracts before
     steps 9 and 10 build them.
  3. **Logos**: the Davisson Brothers Band cap logo, traced from vectors with no inference, and the inlay
     option. Local tests only; not in the launch.
  4. **Objects and gag gifts**: a list, and tests of the best ideas, as possible pre-made ornaments.

  No session merges into `rebuild` or changes the launch steps on its own. Each reports, and the orchestrator
  folds the results into decisions and steps 9–11.

  RJ, later the same evening: if starting a session is refused or waits on his approval in the app, the
  test runs as a background subagent of the orchestrating session instead, with the same brief and its
  findings on disk. Each test below says which way it ran. A subagent can't be opened as a session; read
  its findings file.
  - Test 1 (buildings) ran as a session: findings in `../ornaments-design-session/buildings-01/FINDINGS.md`. It recommended places
    after launch, with three builder checks before it; decision 27 takes that.

- 2026-11-19: Slant costs measured, at RJ's request, with 15 drafts of the test order (docs/CHARGES.md).
  Shipping depends a little on zone ($5.73 to Idaho, $6.93 to WV, $8.95 to Hawaii), and it barely grows with
  count: one ornament costs $10.95 to WV, and a dozen cost $4.87 each. Parts have no volume discount. Drafts
  still can't be deleted, and they don't expire. RJ will run a Codex research brief on what Slant keeps
  (`.private/research/slant-api-brief.md`). New decision 26: any subject, several ornaments to an order.

- 2026-11-19: RJ confirmed decisions 21–24 and asked for price research before the price is set (step 19,
  decision 20). Step 7 started in its own session at medium effort. Steps 9 and 10 wait for RJ's
  orchestration rules.

- 2026-11-19: **The launch plan.** RJ set the target: launch on 11-20 with the ornament, working end to
  end. Customer drawings come from GPT Image's API with capped spending. Production runs in Claude cloud
  routines, and Sarcean stops being the bottleneck. This file was rewritten around that, along with new docs:
  [docs/PRODUCTION.md](docs/PRODUCTION.md), and contracts in [docs/ORDERS.md](docs/ORDERS.md) so steps
  7, 9 and 10 can be built in parallel. The 2026-11-10 road to launch is kept in docs/LOG.md.
- 2026-11-19: Red stencils staged on MeltBot, all in ELEGOO Matte Ruby Red (spool 42), validated (220/65 °C,
  Textured PEI, no supports):
  - `Orn-Stencils-Tray-1.gcode`, printdb 176: the three heads' stencils, 58 min 40 s and 14.7 g.
  - `Orn-Stencils-Tray-2.gcode`, printdb 177: Tucker's v6 stencil, 25 min 32 s and 6.3 g.

  Base trays 1 and 2 are recorded as completed (printdb 173–174), and tray 3 was printing (175). The history
  sync can't link these generic jobs, so they were recorded by hand. Don't run the sync while a print is
  running, because it logs the running job as canceled.
- 2026-11-19: Buster (v1, no tag) printed as the first fit test. It fits and looks great. A 1 mm stencil neck
  nearly broke, so the builder now widens necks and bridges to 1.8 mm. The six white-base pets were rebuilt
  as build-v6, and their bases were printed on three trays.
- 2026-11-19: Secret Santa tag pair and QR snowflakes. Test v1 and its results, the v2 coupon, and the
  snowflake prototypes are in docs/LOG.md.
