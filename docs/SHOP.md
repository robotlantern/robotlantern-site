# The shop

Built in Stripe's sandbox 2026-10-01 ([LOG.md](LOG.md), task 7). Stripe takes the money, a
Cloudflare Worker passes printed items to Gelato as **draft** orders, and RJ ships what he makes.
No monthly fees. What costs money is in [CHARGES.md](CHARGES.md).

This page covers fixed products, which sell through Payment Links. Products made from a customer's
photo, which are the launch's focus, order through their own flow built on this one:
[ORDERS.md](ORDERS.md).

## A product's shop file

`products/<slug>/shop.json`, beside the pipeline's `product.md` (docs/PRODUCTS.md). Prices are
in dollars; prices exclude sales tax, which Stripe Tax adds at checkout.

```json
{
  "name": "Wordmark tee",
  "description": "One or two sentences for the shop and the checkout page.",
  "price": 28,
  "shipping": 5,
  "taxCode": "txcd_99999999",
  "fulfillment": "gelato",
  "gelato": { "files": { "default": "/shop/files/wordmark-tee.png" } },
  "options": {
    "label": "Size",
    "choices": [
      { "label": "S", "productUid": "apparel_product_gca_t-shirt_…_gsi_s_…" },
      { "label": "M", "productUid": "apparel_product_gca_t-shirt_…_gsi_m_…" }
    ]
  },
  "images": ["/images/shop/wordmark-tee.jpg"],
  "listed": false
}
```

- **`fulfillment`:** `gelato` (Gelato prints and ships) or `self` (RJ makes and ships it, with
  `stock`: how many the Payment Link may sell in all; it switches itself off after that many,
  showing "Sold out". To sell more, raise the number and sync). Photo products add `slant` later
  ([ORDERS.md](ORDERS.md), "Fulfillment").
- **`gelato`:** `productUid` (or one per choice under `options`), and `files`: print area →
  file. A path starting with `/` is on the site; any `https://` URL works too. Gelato fetches
  the file when the order is created.
- **`options`:** at most one choice, shown at checkout as a required dropdown. Each choice
  needs its own Gelato `productUid`.
- **`taxCode`:** Stripe's product tax code. Leave it out for general goods (`txcd_99999999`).
- **`images`:** shown on the shop page and Stripe's checkout page.
- **`listed`:** whether the shop page shows it.
- **`stripe`:** written by the sync script; don't edit by hand.

## Making it real in Stripe

    python3 tools/shop/sync.py            # every products/*/shop.json, in the sandbox

creates or updates each product's Stripe product, price, flat shipping rate and Payment Link,
and writes their IDs and the link into the file. Run it again after any change. A new price,
shipping amount or set of choices makes a new Payment Link (the old one is switched off), so
rebuild and deploy the site afterwards. The shop page links to the `test` links until
`SHOP_MODE` in `src/lib/shop.ts` becomes `live` at launch.

Every Payment Link: US shipping addresses only, one flat shipping rate, Stripe Tax on, quantity
one, and a thank-you message on Stripe's page.

## The order Worker

`shop-worker/index.js`, deployed as `shop` at https://shop.robotlantern.workers.dev/stripe with
`tools/shop/worker-deploy.sh` (`--secrets` also loads the sandbox keys). Stripe's sandbox sends
it `checkout.session.completed` and `checkout.session.async_payment_succeeded` (webhook endpoint
created 2026-10-01; its signing secret is `STRIPE_WEBHOOK_SECRET_TEST` in the secrets folder).

For each paid session it checks Stripe's signature, reads the line items, and, for printed
items, searches Gelato for an order whose `orderReferenceId` is the Checkout Session ID before
creating one. So Stripe's retries never make a second order. It always creates a **draft**:
nothing is printed or charged until RJ confirms it in Gelato's dashboard. Self-shipped orders
need nothing from it; Stripe's payment email tells RJ.

If Gelato refuses an order (a bad address or file, say), the Worker answers 500. Stripe then
retries for three days and shows the failure under Workbench → Webhooks. Its logs are in
Cloudflare (Workers → `shop` → Logs), with session IDs and no customer details.

Photo orders at `/api/orders` are built and tested in the sandbox ([ORDERS.md](ORDERS.md)). From launch the Worker also makes customers' drawings and drafts Slant orders ([PRODUCTION.md](PRODUCTION.md)). Not built
yet: Gelato's status webhooks
(they arrive with shipping emails, later), and email from the Worker itself (waits for Cloudflare
Email Routing after cutover).

## Testing

- `python3 tools/shop/test_order.py tools/shop/fixtures/test-mug/shop.json` buys a product in
  the sandbox without a browser: it ships to the West Virginia State Capitol, so tax shows, and
  pays with Stripe's test card token. Stripe then calls the Worker. Products with a size choice
  can't be tested this way; use their Payment Link.
- The fixtures in `tools/shop/fixtures/` (a mug, a tee with sizes, a self-shipped piece) are
  sandbox-only products, never on the shop page. Sync them by path:
  `python3 tools/shop/sync.py tools/shop/fixtures/*/shop.json`.
- Each printed test leaves a Gelato draft. Gelato has no sandbox: its "sandbox" key reaches the
  same account as the live one, so test drafts sit among real ones (their metadata says
  `stripeMode: test`). Delete them in Gelato's dashboard (Orders → Drafts).
- The Payment Links themselves (`stripe.test.url` in each file) take Stripe's test cards in a
  browser. That's RJ's end-to-end check (NOW.md).

Tested 2026-10-01: a mug order created the right Gelato draft (product, file and West Virginia
address); a resent event found it and created nothing; a tee with size M became the M product;
the self-shipped piece left Gelato alone; a bad signature got a 400; Charleston, WV orders
got 7% tax.

## Stripe Tax

Sandbox: head office Fairmont, WV; prices and shipping exclude tax; a West Virginia registration
active from 2026-10-01. Live: the same settings, with the registration's real start date, once
the state certificate exists (docs/SALES-TAX.md; NOW.md).

## Launch

1. Live webhook endpoint: Stripe dashboard (live) → Workbench → Webhooks → add
   `https://shop.robotlantern.workers.dev/stripe` for the two events above, API version
   `2026-08-26.dahlia`.
2. Worker secrets, loaded from the secrets folder with `npx wrangler secret put <NAME>` in `shop-worker/`
   ([PRODUCTION.md](PRODUCTION.md), "Secrets"): `STRIPE_WEBHOOK_SECRET_LIVE`, `STRIPE_SECRET_KEY_LIVE` (the
   restricted key RJ creates in NOW.md step 4, not the agents' key), `OPENAI_API_KEY`, `SLANT_API_KEY`,
   `QUEUE_TOKEN_LIVE` and `PROOF_LINK_SECRET`. `GELATO_API_KEY_LIVE` is needed only once a Gelato product is
   listed.
3. `python3 tools/shop/sync.py --live`, set `SHOP_MODE` to `live`, deploy the site.
4. Stripe's email for successful payments on (it's how self-shipped orders reach RJ), and its email
   receipts to customers.
5. Photo products: the live KV namespace bound to the Worker, and `robotlantern.com/api/*` routed to it
   ([ORDERS.md](ORDERS.md)).
