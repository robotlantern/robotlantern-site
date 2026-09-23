# What costs money

This doc lists every action on Shopify and Gelato that can cost money. Before doing anything not
listed here, find out what it costs and add it.

Prices were checked against Shopify's and Gelato's own pages on 2026-09-23 (see [Sources](#sources)).
The account state was last observed in the Shopify admin on 2026-09-16.

## Current state

- **Shopify:** Basic plan, billed monthly at $39 per 30 days. No paid apps and no other Shopify
  subscriptions. Bills arrive every 30 days: the last one was 2026-09-01, so the next is
  **2026-10-01**. Each bill adds 6% tax, so Basic actually costs $41.34, and the pause would cost
  about $9.54.
- **Gelato:** free plan. The dashboard was still offering the Gelato+ trial, so there is no
  subscription. The Gelato app is installed in Shopify, and the app is free.
- **Starter is gone.** Shopify stopped offering the $5 Starter plan to new stores. Merchants who
  leave Starter can't return to it, and this store was never on it. That leaves only two ways to
  cut the Shopify bill: pause the store or close it.

## The October 1 decision

| Option | Cost | What you get |
| --- | --- | --- |
| **Keep Basic, monthly** | $39 per 30 days | Everything, including test checkout and real sales. |
| **Basic, yearly** | $348 up front ($29/month) | Same features. You can't go back to monthly until the year ends, and even then only by contacting Support. It pays off after about 9 months, so it only makes sense after launch. |
| **Pause and Build** | $9 per 30 days¹ | The admin, draft products and apps keep working. Checkout is off on every channel, so there's no test checkout and no sales. |
| **Agentic plan** | $0 | Built for merchants who *don't* use Shopify as their store. It can't sell through the online store checkout, which is the checkout our site hands off to. It doesn't fit, and it's unclear whether this store can even switch to it. |
| **Close the store** | $0 | All apps are uninstalled, including Gelato and the publisher app. Reopening means choosing a plan again. Not worth it to save $9. |

¹ Shopify's current help page only says "reduced cost." The $9 figure comes from Shopify
Community answers and 2026 third-party guides. The admin shows the exact price before you
confirm.

**Decided (RJ, 2026-09-23): pause by 2026-09-30 unless the shop is built.** Nothing planned for the next 30 days needs a live
checkout. The framework decision, the scaffold and the Gelato/Shopify product setup for task 7
all work while paused. Only the test checkout at the end of task 7 needs a paid plan. When the
shop page is ready for it, unpause and pick Basic monthly. Upgrades are billed right away, prorated
from the upgrade date, with the unused part of the old plan credited back. So unpausing early costs
about the same as staying on Basic for those days. Shopify documents this proration for upgrades
generally, not for unpausing specifically.

How pausing works:

- The pause starts at the end of the current billing cycle. Choose it by 2026-09-30, and until
  then the store runs normally.
- To unpause, you choose a plan again, because the old one lapses. Basic's list price is the same
  $39 you pay now, so nothing is lost.
- Apps stay installed. Paid apps would keep billing, but there are none.

## What works on each plan

| | Basic | Paused | Closed |
| --- | --- | --- | --- |
| Admin, editing products, draft products | Yes | Yes | No |
| Apps, including Gelato and the publisher app (Admin API) | Yes | Yes (apps stay active) | Uninstalled |
| Gelato creating products in Shopify | Yes | Expected: apps and product editing still work. Not tested. | No |
| Storefront API (product data for our site) | Yes | Not documented. The storefront stays viewable, so reads will probably work. | No |
| Test checkout | Yes | **No.** Test gateways need a paid plan, and checkout is off. | No |
| Real sales | Yes | No | No |
| Draft order invoices | Yes | Can be sent, but can't be paid | No |

The Storefront API has no fee. The Headless sales channel app, which issues Storefront API
tokens, is free.

## Shopify: actions that cost money

| Action | Cost |
| --- | --- |
| Staying on a paid plan | Basic: $39 per 30 days, or $29/month billed yearly. Grow: $105 or $79. Advanced: $399 or $299. |
| Choosing a plan: unpausing, upgrading, or switching to yearly | Billed immediately, prorated |
| Pausing | $9 per 30 days¹ |
| Installing a paid app, or approving an app's recurring or usage charge | Added to the next Shopify bill. It keeps billing while paused. |
| Starting Gelato+ from inside the Shopify app | $29.99 per month or $239.88 per year, billed through Shopify every 30 days |
| Buying a domain through Shopify | Annual fee. Renewals continue even if the store closes. Not needed: DNS for robotlantern.com is elsewhere. |
| Buying a paid theme | One-time price shown in the Theme Store. Not needed: the site isn't a Shopify theme. |
| Buying shipping labels in Shopify | Per label. Not needed: Gelato ships. |
| A real sale through Shopify Payments | 2.9% + 30¢ per online card payment on Basic (3.5% + 30¢ for premium cards) |
| A real sale through a third-party payment provider | That provider's fee plus 2% to Shopify on Basic |
| Paying for a real order with a real card and refunding it as a "test" | The processor may keep its fees. Use test mode instead (see below). |
| Shopify Tax | Free on the first $100,000 of sales each year, then a small per-order fee |
| Shopify email | Free up to 10,000 emails a month, then charged |
| Chargebacks | The disputed amount plus a dispute fee, taken from payouts |

Anything added to the bill between cycles is billed early once it passes the account's billing
threshold.

## Shopify: free

- Draft products, unlimited products, and collections.
- The Admin API through the Robot Lantern Local Publisher custom app, and Theme CLI. The app
  doesn't appear among paid app subscriptions.
- The Storefront API, and the Headless channel app.
- Test orders through Shopify Payments test mode or the test ("Bogus") gateway. Shopify says:
  "You aren't charged for test orders placed through these gateways." These need a paid plan, and
  while payments are in test mode real customers can't order, so switch it off before launch.
- Cart permalinks (`/cart/VARIANT_ID:QTY`), which hand a static site off to Shopify checkout.
- Installing the Gelato app.

## Gelato: actions that cost money

| Action | Cost |
| --- | --- |
| A Shopify order with a Gelato-connected product that has been paid | Product cost plus shipping, charged to Gelato's card or wallet when Gelato receives the order. Approval is **instant by default**, so the charge is immediate. Gelato syncs orders every 15 minutes. |
| Placing an order in the Gelato dashboard, including samples | Charged at placement. There are no free samples. Seasonal sample discounts cover the product only, not shipping. |
| Approving an order that was pending approval | Charged at approval |
| US sales tax on any order | Added in 44 states unless a resale certificate is on file |
| Canceling an order after it reaches "In Production" | Only the shipping is refunded. Cancellations refund to the Gelato Wallet, not the card. |
| Gelato+ | $29.99 per month or $239.88 per year, plus US tax. The 14-day trial asks for payment details. **"Activate now to apply discounts" skips the trial and charges immediately.** |
| Features that need Gelato+ | These include live shipping rates on Basic Shopify, automatic print-file processing from checkout attributes, product discounts, and Personalization Studio. Using one means subscribing. |
| Wallet auto top-up | Charges the card whenever it tops up |

## Gelato: free

- The account, connecting the store, the catalog, the design editor, templates, standard mockups,
  and creating or publishing products to Shopify.
- The **Custom store**, a private store for testing designs and products. Customers can't reach it.
- **Draft orders.** Gelato recommends them for checking regional prices and tax before a real
  order. The API's `orderType: "draft"` creates one without placing it.
- **Orders pending approval.** Gelato says: "you are not yet charged for the order." Draft and
  pending-approval orders can be deleted.
- Canceling before printing starts, while the status is "Digitizing", "Uploading" or "Passed". This
  refunds in full, to the wallet.

## Test checkout without a real charge

Gelato imports every paid Shopify order that includes a connected product, and a Shopify test order
counts as paid. Gelato's docs never say it skips test orders, and at least one merchant on the
Shopify Community received real products from a test-card order. **Treat a test checkout of a
Gelato product as a real Gelato order** unless one of these is in place first:

1. **Test with a Shopify-only product.** Create a draft test product that isn't connected to
   Gelato. Gelato won't import it ("No mapped line items") as long as its "import not connected"
   option is off. This tests the site-to-checkout handoff with nothing for Gelato to import.
2. **To test a real Gelato product,** first switch Gelato's Order Approval to **Manual** under
   Stores > Edit store details. The test order stops at Pending Approval, uncharged. Delete it
   there, then set approval back to Automatic before launch.

In both cases, use Shopify Payments test mode or the test gateway, never a real card.

## Sources

Shopify, checked 2026-09-23:

- [Pricing](https://www.shopify.com/pricing)
- [Pausing your store](https://help.shopify.com/en/manual/your-account/manage-orgs-and-stores/manage-pricing-plan/pause-store)
- [Billing when pausing or deactivating](https://help.shopify.com/en/manual/your-account/manage-billing/billing-considerations-pause-deactivate-store)
- [Plan changes and proration](https://help.shopify.com/en/manual/your-account/manage-billing/managing-your-bills/billing-plan-changes)
- [Billing cycles and thresholds](https://help.shopify.com/en/manual/your-account/manage-billing/managing-your-bills/viewing-your-bills/billing-cycles-thresholds)
- [Charges on your bill](https://help.shopify.com/en/manual/your-account/manage-billing/billing-charges/types-of-charges/shopify-charges)
- [App charges](https://help.shopify.com/en/manual/your-account/manage-billing/billing-charges/types-of-charges/third-party-charges/app-charges)
- [Starter plan](https://help.shopify.com/en/manual/intro-to-shopify/pricing-plans/plans-features/shopify-starter-plan)
- [Agentic plan](https://help.shopify.com/en/manual/intro-to-shopify/pricing-plans/plans-features/shopify-agentic-plan)
- [Test orders](https://help.shopify.com/en/manual/checkout-settings/test-orders)
- [Shopify Tax pricing](https://help.shopify.com/en/manual/taxes/shopify-tax/pricing)
- [Chargebacks](https://help.shopify.com/en/manual/payments/chargebacks)
- [Headless app](https://apps.shopify.com/headless)
- [Gelato app listing](https://apps.shopify.com/gelato-print-on-demand)
- The $9 pause price: [Shopify Community](https://community.shopify.com/c/shopify-discussions/9-mo-paused-account-for-building/m-p/1546455)
- Starter's withdrawal: [Ecommercetrix, 2026-08-15](https://www.ecommercetrix.com/ecommerce-news/shopify-starter-plan-ends/)
- The test order that shipped: [Shopify Community](https://community.shopify.com/t/test-order-that-came/398462)

Gelato Help Center, checked 2026-09-23:

- [How much Gelato costs](https://support.gelato.com/en/articles/8996080-how-much-does-gelato-cost)
- [Payment process](https://support.gelato.com/en/articles/8996153-understanding-the-payment-process-for-your-orders)
- [Default approval](https://support.gelato.com/en/articles/8996131-what-is-our-default-order-approval-workflow)
- [Manual approval](https://support.gelato.com/en/articles/8996084-what-is-the-manual-order-approval-workflow)
- [Pending approval](https://support.gelato.com/en/articles/8996051-why-does-my-order-have-the-status-pending-approval)
- [Deleting drafts](https://support.gelato.com/en/articles/8996599-can-i-delete-an-order-with-the-status-draft-or-pending-approval)
- [Canceling](https://support.gelato.com/en/articles/8996601-how-do-i-cancel-an-order-via-the-gelato-dashboard)
- [Order import](https://support.gelato.com/en/articles/9895762-why-was-my-order-not-imported-to-gelato)
- [Samples](https://support.gelato.com/en/articles/8996052-do-you-offer-free-samples)
- [Sample discounts](https://support.gelato.com/en/articles/8996054-do-you-have-any-discounts-for-sample-orders)
- [Gelato+ price](https://support.gelato.com/en/articles/8996313-how-much-does-gelato-subscription-cost)
- [Gelato+ trial](https://support.gelato.com/en/articles/8996311-do-you-offer-a-free-gelato-trial-period)
- [Wallet charges](https://support.gelato.com/en/articles/8996116-i-have-gelato-wallets-enabled-why-was-my-credit-card-charged)
- [US sales tax](https://support.gelato.com/en/articles/8996155-taxes-in-the-americas)
- [Custom store](https://support.gelato.com/en/articles/8996391-what-is-your-custom-store-can-i-use-it-for-testing-gelato)
- [Shopify checkout on a custom site](https://support.gelato.com/en/articles/8996410-can-i-use-shopify-checkout-on-a-custom-website)
- [Gelato+ and Shopify plans](https://support.gelato.com/en/articles/8996408-how-much-does-it-cost-to-use-shopify)
- [API draft orders](https://dashboard.gelato.com/docs/orders/v3/create/)
