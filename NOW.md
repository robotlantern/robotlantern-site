# Now

_Last updated 2026-10-01._

## Start here

The new site is built on the `rebuild` branch and previewed at https://rl.rblt.io/ (push to
`samwise`; [docs/PREVIEW.md](docs/PREVIEW.md)). Design rules are in [docs/PAGES.md](docs/PAGES.md),
the home page in [docs/HOME.md](docs/HOME.md) and the brand in [docs/BRAND.md](docs/BRAND.md).
**What's left is the list below, in order: the site and the shop launch together.** `python3 tools/next.py` prints RJ's next steps
from it. Task notes further down hold the detail.

## Road to launch

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
   Done 2026-10-01 ([docs/SHOP.md](docs/SHOP.md)).
10. [ ] **Agent** · Mockups for the tee, mug and tote. *30 min*
11. [x] **Agent** · Cloudflare project, deployed to a Cloudflare address (kept out of search
    engines) for RJ to check; record every current DNS record for robotlantern.com, above all
    Google Workspace mail. Done 2026-10-01: https://site.robotlantern.workers.dev
    ([docs/HOSTING.md](docs/HOSTING.md)).
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

### Not needed for launch

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

## Task notes

The detail behind the road to launch, and the record of what's done.

1. **Close Shopify (RJ).** Done 2026-09-30, before the 2026-10-01 bill; RJ removed its links to
   Gelato and QPMN. `shopify.env` in the secrets folder is now dead and can be deleted.
2. **Framework sign-off.** Done 2026-09-23: Astro.
3. **Attribution tool.** Done 2026-09-24 (`tools/attribution/`, [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md)).
4. **Sunset scroll prototype.** Done 2026-09-25. It became the home page; the frozen prototype is
   at `public/prototypes/sunset-scroll/` (tag `sunset-scroll-v1`).
5. **Thought and chat pages.** Done 2026-09-27; RJ approved them on his phone. List and detail
   (`src/components/Reader.astro`): `/thoughts/` and `/chats/` open on the newest piece, the
   list is beside it on desktop and in the site menu on phones, and the column is endless.
   Chats sort by posted or chat date and search. Posted dates live in each chat's `post.json`.
6. **Launch conversation: "It's Always the Pleiades".** Done 2026-09-27: RJ approved the public
   text. The public copy is `src/content/conversations/its-always-the-pleiades/`, generated by
   `.private/conversations/pleiades/make_public.py`; 40 editor's links in `links.json`
   ([docs/LINKS.md](docs/LINKS.md)). Deferred, not for launch: whether other replies showed
   reasoning or search steps worth including; per-message times (the next capture should keep
   them).
7. **First products, on Stripe and Gelato** (RJ, 2026-09-28: no Shopify; nothing with a
   monthly fee). Accounts open and keys checked 2026-10-01 (read-only calls): Stripe (live,
   activated), Gelato, Cloudflare, Slant 3D. The sandbox key (`STRIPE_SECRET_KEY_TEST`) is in
   and works. The products come from the pipeline (task 19): whichever two to four reach
   `listing` first. Shop art is made with AI (RJ, 2026-09-27).
   - **Built in the sandbox 2026-10-01** ([docs/SHOP.md](docs/SHOP.md)):
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
     ([docs/SALES-TAX.md](docs/SALES-TAX.md)).
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
     The current DNS records and the cutover steps are in [docs/HOSTING.md](docs/HOSTING.md).
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
10. **Samwise previews.** Done 2026-09-27; RJ has used them on his phone ([docs/PREVIEW.md](docs/PREVIEW.md)).
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
16. **Brand.** Done 2026-09-27 ([docs/BRAND.md](docs/BRAND.md)): RJ's ovaloid period, the
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
19. **Product pipeline.** Done 2026-10-01 ([docs/PRODUCTS.md](docs/PRODUCTS.md)): one folder
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

## Parked

- Essay: why the machines have names (RJ says there's a practical reason; the About page promises
  it).
- Post: what "the model" means in a chat app. Per-turn routing, personalization and the in-app
  context all shape a reply, and only the account export records which model answered.
- `unprojection-astra`, the other build of the sky visualization (GPT-6-Astra, open brief), is
  previewed on Samwise and stays off the site for now. The Opus build is live as a build.
- Large files as the site grows: video on YouTube; big downloads or self-hosted video on
  Cloudflare R2 behind a subdomain (free tier 10 GB; it needs a card on file, so add it to
  docs/CHARGES.md before turning it on).

## Log

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
