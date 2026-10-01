# What costs money

This doc lists every action on Stripe, Gelato, Cloudflare and the other print services that can
cost money. Before
doing anything not listed here, find out what it costs and add it.

Stripe was checked on 2026-09-28, Gelato on 2026-09-23 and 2026-09-28, Cloudflare on 2026-09-27
and Shopify on 2026-09-23 (see [Sources](#sources)).

## Current state

- **The shop is Stripe + Gelato, with no Shopify (RJ, 2026-09-28).** Stripe takes payment, a
  Cloudflare Worker passes each paid order to Gelato's API, and Gelato prints and ships. Nothing
  has a monthly fee. See NOW.md, task 7.
- **Shopify:** canceled by RJ on 2026-09-30, before the 2026-10-01 bill. RJ removed its links to
  Gelato and QPMN.
- **Gelato:** free plan, no Gelato+. API keys work (checked 2026-10-01 with read-only calls).
- **Stripe:** account open and **activated for live payments** (charges and payouts enabled,
  2026-10-01). The key on file is a **live** restricted key (Stripe's preset for AI agents). Build
  and test with a sandbox key instead (see "Testing without a real charge").
- **Cloudflare:** free account; its API token works (2026-10-01). The token can also reach
  billing and domain registration, so agents treat those as off limits (see below).
- **Slant 3D, QPMN:** accounts, no orders. Slant's key works; QPMN's API docs come from QPMN on
  request.

## Stripe: actions that cost money

Stripe has no setup or monthly fee. Every fee below is per transaction and comes out of the payout.

| Action | Cost |
| --- | --- |
| A real card payment (Checkout, Payment Links, Apple Pay, Link) | 2.9% + 30¢ for US cards. International cards add 1.5%, and currency conversion adds 1%. |
| Refunding a payment | No refund fee, but the original payment's fees aren't returned |
| A dispute (chargeback) | $15 per dispute, plus the disputed amount |
| Stripe Tax, automatic sales tax at checkout | 0.5% per transaction on Tax Basic. Tax Complete starts at $90/month on an annual contract. |
| Radar Standard, Plus or Pro (fraud screening) | A fee per screened transaction (from 5¢). Radar Lite has no fee. Check which plan a new account starts on before going live. |
| Any other paid product (Billing, Invoicing, Climate, Atlas, Identity) | Not needed. Don't turn one on. |

## Stripe: free

- The account itself, and everything in **test mode** (sandboxes). Test cards never move money.
- Payment Links and hosted Checkout pages, products, prices and fixed shipping rates.
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
| Pages, or Workers static assets, for the site | Free: 500 builds a month, 20,000 files and 25 MiB per file per deploy, no bandwidth limit for static files (checked 2026-09-27) |
| Moving the domain's nameservers to Cloudflare, DNS | Free |
| Workers requests that run code (the shop's order Worker, the counted short links in NOW.md task 17) | Free up to 100,000 a day; the paid plan is a monthly fee |
| R2 storage (large files, later) | Free up to 10 GB and 1M writes / 10M reads a month; downloads free. Needs a card on file, so going over bills automatically: add a spending check before turning it on |
| Web Analytics, Bot Fight Mode | Free, but they break the privacy page's claims (NOW.md, task 9) |
| Anything under Billing, a paid plan or add-on, or Registrar (buying or transferring a domain) | Costs money. The API token can do these: agents never call them. |

## Shopify (until the store closes)

| Action | Cost |
| --- | --- |
| Keeping the Basic plan | $39 per 30 days, plus 6% tax. The next bill is 2026-10-01. |
| Pausing ("Pause and Build") | About $9 per 30 days. Not needed now that the shop doesn't use Shopify. |
| Closing the store | Free. Any charges still outstanding are billed at closing. All apps are uninstalled, including Gelato. Reopening means choosing a paid plan again. |
| Anything else: paid apps, Gelato+ through the Shopify app, themes, domains, labels | Don't. |

## Other services

| Action | Cost |
| --- | --- |
| Northwest Registered Agent address as the shop's public address | Check the plan: mail handling or forwarding may be a paid add-on |
| An email service for shipping notices (for example Resend or Postmark) | Not chosen. Check its free tier before signing up. |
| Slant 3D: placing an order through the API or dashboard | Charged per order (part, filament and shipping). Reading files, filaments and quotes is free. Not yet checked in detail: read Slant's API docs on orders before writing anything there. |
| QPMN: placing an order | Product plus shipping, per order; no fee for API access (QPMN's API page, 2026-10-01). |
| Lulu (books, later) | Per order. API access is by request. |
| Shipping labels for things RJ ships himself (USPS through a label service such as Pirate Ship, or USPS Click-N-Ship) | Per label. The accounts are free. Not yet chosen or checked: check before the first label. |
| A PO box for the return address | A yearly or half-yearly fee, by box size. Not yet checked. |

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
