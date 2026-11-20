# What costs money

This doc lists every action on Stripe, Gelato, Cloudflare, OpenAI, Claude and the print services that can
cost money. Before
doing anything not listed here, find out what it costs and add it.

Stripe was checked on 2026-09-28, Gelato on 2026-09-23 and 2026-09-28, Cloudflare on 2026-09-27
and Shopify on 2026-09-23 (see [Sources](#sources)). Slant's orders were checked on 2026-10-02 in the
3d-modeling sessions, and Workers KV's free plan on 2026-11-10.

## Current state

- **The shop is Stripe + Gelato, with no Shopify (RJ, 2026-09-28).** Stripe takes payment, a
  Cloudflare Worker passes each paid order to Gelato's API, and Gelato prints and ships. Nothing
  has a monthly fee. See SHOP.md and ORDERS.md.
- **Shopify:** canceled by RJ on 2026-09-30, before the 2026-10-01 bill. RJ removed its links to
  Gelato and QPMN.
- **Gelato:** free plan, no Gelato+. API keys work (checked 2026-10-01 with read-only calls).
- **Stripe:** account open and **activated for live payments** (charges and payouts enabled,
  2026-10-01). The key on file is a **live** restricted key (Stripe's preset for AI agents). Build
  and test with a sandbox key instead (see "Testing without a real charge").
- **Cloudflare:** free account; its API token works (2026-10-01). The token can also reach
  billing and domain registration, so agents treat those as off limits (see below). Since
  2026-10-01 it runs the site's copy (`site`) and the order Worker (`shop`) on the free
  `robotlantern.workers.dev` subdomain (docs/HOSTING.md, docs/SHOP.md).
- **Slant 3D:** account and API key (v2), no orders. One platform exists ("Robot Lantern printdb",
  created 2026-10-02 with RJ's OK), and STLs have been uploaded for free quotes. Sixteen unpaid test drafts
  stay on the account for good: one from 2026-10-02, and fifteen from 2026-11-19 that RJ asked for, to measure
  shipping. Re-checked 2026-11-19: the October
  draft was still there after 47 days, and `DELETE` still answers "Can not cancel a draft order", so drafts
  neither expire nor delete.
- **QPMN:** account, no orders. Its API docs come from QPMN on request.
- **Photo products** (docs/ORDERS.md): uploads go to Workers KV on the free plan (NOW.md
  decision 5). The stencil ornament adds two costs: OpenAI drawings, which are capped, and the Slant order
  RJ processes for each sale (both below).
- **OpenAI API:** from NOW.md step 3, a project with prepaid credit and auto-recharge off (decision 21).
  RJ made a project key on 2026-11-19 (in `openai.env`), loaded $30 of credit with auto-recharge off, and set
  the key to expire after 30 days, so a new key is needed before 2026-12-19. That's mid-season. The key has
  full permissions: RJ didn't restrict it. It sees eleven GPT Image models (`GET /v1/models`, free).
  **Test allowance (RJ, 2026-11-19):** up to $5 of that credit for calls that check or confirm something for
  the pipeline, such as choosing the model. Drawings for anything else still go through Codex. Log each paid
  test run's count and estimated cost in NOW.md.

## The stencil ornament, per order (measured 2026-11-19)

| Cost | Amount | When |
| --- | --- | --- |
| Slant: both parts, with a name tag | $3.56–4.02 an ornament (quotes for ten pets and the test cat) | RJ processes the draft |
| Slant: shipping | $5.73–6.93 for one ornament in the lower 48, $8.41 to Alaska, $8.95 to Hawaii; more ornaments in a box add little (below) | the same |
| Stripe | 2.9% + 30¢ (about $1.14 on $29) | each payment |
| Stripe Tax | 0.5% of West Virginia orders only | each WV payment |
| OpenAI drawings | about $0.05–0.25 each, up to 3 per photo, including people who don't buy | each drawing |

**How it was measured.** Slant shows shipping only on a draft order, and drafts are permanent (below). At RJ's
request, 15 free drafts were made of the test order (`tools/ornament/fixtures/test-order`: white base, red
stencil, name tag; 39 g an ornament by Slant's weights). Single ornaments went to state capitols. The volume
drafts went to RJ's address in West Virginia, the dearest lower-48 zone we tried. Slant's farm is in Idaho.

**Parts don't get cheaper in volume.** Quotes at 1, 6, 12, 20, 50 and 100 all priced each part the same ($2.39
base, $1.63 stencil). Twelve different designs cost exactly what twelve copies of one design cost. So any discount
Slant offers isn't in the API's prices: NOW.md step 19's research brief asks about it.

**Shipping by place** (one ornament): ID $5.73 · CA $5.95 · TX $6.06 · IL $6.06 · FL $6.85 · ME $6.85 ·
WV $6.93 · AK $8.41 · HI $8.95.

**Shipping by count** (to WV; it rises in weight steps and levels off):

| Ornaments | Parts | Shipping | Slant total | Each |
| --- | --- | --- | --- | --- |
| 1 | $4.02 | $6.93 | $10.95 | $10.95 |
| 3 | $12.06 | $7.35 | $19.41 | $6.47 |
| 6 | $24.12 | $8.40 | $32.52 | $5.42 |
| 12 (same or all different) | $48.24 | $10.15 | $58.39 | $4.87 |
| 20 | $80.40 | $10.15 | $90.55 | $4.53 |
| 50 | $201.00 | $11.95 | $212.95 | $4.26 |

So the cheapest an ornament can be made is about $4.02 plus a share of one box, and a single ornament carries the
most shipping by far. Add Stripe's fee and the drawings (at most 3 per design). Other zones will run up to about
$1.20 less than WV in the lower 48. Alaska and Hawaii run about $1.50–2.00 more, probably more at volume.

## Stripe: actions that cost money

Stripe has no setup or monthly fee. Every fee below is per transaction and comes out of the payout.

| Action | Cost |
| --- | --- |
| A real card payment (Checkout, Payment Links, Apple Pay, Link) | 2.9% + 30¢ for US cards. International cards add 1.5%, and currency conversion adds 1%. |
| Refunding a payment | No refund fee, but the original payment's fees aren't returned |
| A dispute (chargeback) | $15 per dispute, plus the disputed amount |
| Stripe Tax, automatic sales tax at checkout (adopted 2026-10-01; docs/SALES-TAX.md) | 0.5% of each sale into a state where Robot Lantern is registered to collect, so only West Virginia orders. Tax Complete starts at $90/month on an annual contract: not needed. |
| Radar Standard, Plus or Pro (fraud screening) | A fee per screened transaction (from 5¢). Radar Lite has no fee. Check which plan a new account starts on before going live. |
| Any other paid product (Billing, Invoicing, Climate, Atlas, Identity) | Not needed. Don't turn one on. |

## Stripe: free

- The account itself, and everything in **test mode** (sandboxes), including Stripe Tax there.
  Test cards never move money.
- Payment Links and hosted Checkout pages, including Checkout Sessions created through the API (photo
  products, docs/ORDERS.md), products, prices and fixed shipping rates.
- Email receipts, webhooks and API keys.
- Fixed tax rates that you set yourself (as opposed to Stripe Tax).

## Gelato: actions that cost money

| Action | Cost |
| --- | --- |
| Creating an order through the API with `orderType: "order"` | Product cost plus shipping, charged to Gelato's card or wallet at once. **The API has no test mode:** a real order request is a real order. |
| Placing an order in the Gelato dashboard, including samples, or confirming a draft | Charged at placement. There are no free samples. Seasonal sample discounts cover the product only, not shipping. |
| Approving an order that was pending approval | Charged at approval |
| US sales tax on any order | Added in 44 states unless a resale certificate is on file |
| Canceling an order after it reaches "In Production" | Only the shipping is refunded. Cancellations refund to the Gelato Wallet, not the card. |
| Gelato+ | $29.99 per month or $239.88 per year, plus US tax. The 14-day trial asks for payment details. **"Activate now to apply discounts" skips the trial and charges immediately.** |
| Wallet auto top-up | Charges the card whenever it tops up |

## Gelato: free

- The account, the catalog, the design editor, templates, standard mockups and API keys.
- **Draft orders.** `orderType: "draft"` creates an order that isn't placed. Drafts can be deleted.
- **Quotes.** The Quote order endpoint returns product and shipping prices without ordering.
- Canceling before printing starts, while the status is "Digitizing", "Uploading" or "Passed". This
  refunds in full, to the wallet.
- Webhooks.

## Testing without a real charge

1. Use a Stripe **sandbox** (test mode) and its test cards for every checkout test. The live key
   in the secrets folder is for launch: never point a test at it, because a live Payment Link
   takes real cards.
2. Until RJ says otherwise, the Worker creates Gelato orders as **drafts**, whichever Stripe mode
   the payment came from. A test payment then leaves a draft to check and delete, and a real
   payment leaves a draft for RJ to confirm in the Gelato dashboard. Gelato's manual approval
   setting belongs to a connected store, so don't rely on it for API orders.
3. Never call Gelato's create-order endpoint with `orderType: "order"` from a test.

## Cloudflare (hosting from cutover)

Not re-checked for billing detail; confirm on Cloudflare's pricing pages before turning anything on.

| Action | Cost |
| --- | --- |
| The workers.dev subdomain, and Workers static assets for the site (how Cloudflare now builds new Pages projects) | Free: 500 builds a month, 20,000 files and 25 MiB per file per deploy, no bandwidth limit for static files (checked 2026-09-27) |
| Moving the domain's nameservers to Cloudflare, DNS | Free |
| Workers requests that run code (the shop's order Worker, the photo-order API, the counted short links in LOG.md task 17) | Free up to 100,000 a day; the paid plan is a monthly fee |
| Workers KV on the Free plan (photo uploads, docs/ORDERS.md) | Free: 1 GB stored, 100,000 reads and 1,000 writes a day, values up to 25 MiB (checked 2026-11-10). The Free plan has no bill to run up. Keep the account on it: Workers Paid is a monthly fee |
| Creating a KV namespace (`shop-orders-live`, 2026-11-20) and Cron Triggers (the order Worker's daily purge) | Free. Their reads, writes and runs fall within Workers Paid's included usage |
| Workers CPU on the Free plan | 10 ms per request, which is why uploads stream straight into KV (docs/ORDERS.md). More CPU means Workers Paid ($5 a month). **RJ approved Workers Paid on 2026-11-19 and switched it on.**  It also lifts the KV limit of 1,000 writes a day |
| R2 storage (large files, later) | Free up to 10 GB and 1M writes / 10M reads a month; downloads free. Needs a card on file, so going over bills automatically: add a spending check before turning it on |
| Web Analytics, Bot Fight Mode | Free, but they break the privacy page's claims (LOG.md, task 9) |
| Anything under Billing, a paid plan or add-on, or Registrar (buying or transferring a domain) | Costs money. The API token can do these: agents never call them. |

## Shopify (until the store closes)

| Action | Cost |
| --- | --- |
| Keeping the Basic plan | $39 per 30 days, plus 6% tax. The next bill is 2026-10-01. |
| Pausing ("Pause and Build") | About $9 per 30 days. Not needed now that the shop doesn't use Shopify. |
| Closing the store | Free. Any charges still outstanding are billed at closing. All apps are uninstalled, including Gelato. Reopening means choosing a paid plan again. |
| Anything else: paid apps, Gelato+ through the Shopify app, themes, domains, labels | Don't. |

## OpenAI API (customer drawings)

Drawings are made through our Worker only, under the caps in docs/PRODUCTION.md. Prices were read on
2026-11-19 from third-party summaries, which disagree about model names. Whoever makes the key (step 3) or
wires the Worker (step 9) checks [OpenAI's pricing page](https://openai.com/api/pricing/) and sets
`costPerDrawing` from it.

| Action | Cost |
| --- | --- |
| One drawing (GPT Image edit, 1024 × 1024) | Billed in tokens. Measured 2026-11-19 with `gpt-image-2.6-sunburst`: $0.053 at medium (production) and $0.063 at high, photo included. `costPerDrawing` is 0.06. `gpt-image-2` at high was $0.22 |
| Model tests | $2.79 of the $5 test allowance spent on 2026-11-19 (42 calls, `../ornaments-design-session/model-ab-01/`). Step 9 made one more on 2026-11-20 through the sandbox Worker (about $0.05, a drawn cat) |
| Prepaid credit | RJ buys it. With auto-recharge off, the balance is a hard cap |
| Auto-recharge, a raised limit, other models, fine-tuning, a ChatGPT plan | Not used. Agents never turn any of these on |

## Claude (cloud routines)

Routines and cloud sessions draw on RJ's Claude subscription usage like any other session, and nothing is
billed separately. Don't turn on paid extra usage for them. An idle `rl-orders` run stops after one command
(docs/PRODUCTION.md).

## Other services

| Action | Cost |
| --- | --- |
| Northwest Registered Agent address as the shop's public address | Check the plan: mail handling or forwarding may be a paid add-on |
| An email service for shipping notices (for example Resend or Postmark) | Not chosen. Check its free tier before signing up. |
| Slant 3D: processing an order (`POST /orders/{id}`, or in the dashboard) | Charged then: parts, components and shipping. Pricing seen so far is about $1.14 a part plus $0.0426 a gram, and shipping appears only on an order (measured by place and count in "The stencil ornament, per order" above). Only RJ processes orders |
| Slant 3D: drafting an order (`POST /orders`) | Free, but **permanent**: Slant can't cancel or delete a draft, and drafts don't expire (re-checked 2026-11-19). Draft only for a real, checked order, and never in a test unless RJ asks (docs/ORDERS.md) |
| Slant 3D: uploads, quotes (`POST /files/{id}/estimate`), filaments, components, platforms | Free. Quotes go through printdb's `slant.py`, which uploads each STL once |
| Supplies for prototypes and stock (white filament, frames, LEDs, puck lights, tealights, sticker paper, boxes) | RJ buys them. Agents list options with prices first |
| Cricut Design Space, for Print Then Cut | Not checked: confirm Print Then Cut needs no paid subscription before the first cut |
| QPMN: placing an order | Product plus shipping, per order; no fee for API access (QPMN's API page, 2026-10-01). |
| Lulu (books, later) | Per order. API access is by request. |
| Shipping labels for things RJ ships himself (USPS through a label service such as Pirate Ship, or USPS Click-N-Ship) | Per label. The accounts are free. Not yet chosen or checked: check before the first label. |

## Sources

Stripe, checked 2026-09-28:

- [Pricing](https://stripe.com/pricing)
- [Radar plans and fees](https://docs.stripe.com/radar/how-radar-works)
- [Website checklist](https://docs.stripe.com/get-started/checklist/website)

Gelato API documentation, checked 2026-09-28:

- [Overview and authentication](https://dashboard.gelato.com/docs/)
- [Get started (orders by product UID, with no store)](https://dashboard.gelato.com/docs/get-started/)
- [How orders work (statuses, split orders)](https://dashboard.gelato.com/docs/orders/order_details/)
- [Webhooks](https://dashboard.gelato.com/docs/webhooks/)
- [Create order](https://dashboard.gelato.com/docs/orders/v4/create/)

Gelato Help Center, checked 2026-09-23:

- [How much Gelato costs](https://support.gelato.com/en/articles/8996080-how-much-does-gelato-cost)
- [Payment process](https://support.gelato.com/en/articles/8996153-understanding-the-payment-process-for-your-orders)
- [Pending approval](https://support.gelato.com/en/articles/8996051-why-does-my-order-have-the-status-pending-approval)
- [Deleting drafts](https://support.gelato.com/en/articles/8996599-can-i-delete-an-order-with-the-status-draft-or-pending-approval)
- [Canceling](https://support.gelato.com/en/articles/8996601-how-do-i-cancel-an-order-via-the-gelato-dashboard)
- [Samples](https://support.gelato.com/en/articles/8996052-do-you-offer-free-samples)
- [Sample discounts](https://support.gelato.com/en/articles/8996054-do-you-have-any-discounts-for-sample-orders)
- [Gelato+ price](https://support.gelato.com/en/articles/8996313-how-much-does-gelato-subscription-cost)
- [Gelato+ trial](https://support.gelato.com/en/articles/8996311-do-you-offer-a-free-gelato-trial-period)
- [Wallet charges](https://support.gelato.com/en/articles/8996116-i-have-gelato-wallets-enabled-why-was-my-credit-card-charged)
- [US sales tax](https://support.gelato.com/en/articles/8996155-taxes-in-the-americas)

Shopify, checked 2026-09-23 (the full comparison of plans is in this file's Git history):

- [Pausing your store](https://help.shopify.com/en/manual/your-account/manage-orgs-and-stores/manage-pricing-plan/pause-store)
- [Billing when pausing or deactivating](https://help.shopify.com/en/manual/your-account/manage-billing/billing-considerations-pause-deactivate-store)
