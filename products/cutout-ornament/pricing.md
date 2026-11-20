# Stencil ornament: pricing

_NOW.md step 19. Research done 2026-11-20. Prices are snapshots from that day, in the weeks when sellers run
holiday sales. Nothing here changes a `shop.json`: decision 20 does that once RJ says yes._

## Recommendation

One price list, shipping and the name tag included, by the number of ornaments in the order (decision 26:
designs share one Slant box, and the tier follows the order's total count):

| Ornaments in the order | Each | Order total | Margin (expected) | Margin (pessimistic) |
| --- | --- | --- | --- | --- |
| 1 | $22.00 | $22 | $8.94 (41%) | $8.04 (37%) |
| 2 | $17.00 | $34 | $16.24 (48%) | $13.60 (40%) |
| 3 | $15.00 | $45 | $22.56 (50%) | $18.18 (40%) |
| 6 | $13.00 | $78 | $41.10 (53%) | $31.50 (40%) |
| 12 | $11.00 | $132 | $66.89 (51%) | $46.85 (35%) |
| 25 | $9.50 | $237.50 | $115.19 (49%) | $95.15 (40%) |
| 50 | $8.50 | $425 | $192.20 (45%) | $172.16 (41%) |

Margin is what's left after Slant, Stripe, drawings and a remake reserve (the next section). "Expected" is the
base case, "pessimistic" the bad case. The ladder keeps about $7–9 an ornament up to six, then thins to $5.50 at a
dozen and $3.80 at 50. Slant's box is the cost that shrinks with count, and the price passes that on.

**The product file's `pricing`** (the shape in docs/ORDERS.md, which step 9's Worker prices as built):

```json
"pricing": {
  "tiers": [
    { "from": 1,  "each": 22 },
    { "from": 2,  "each": 17 },
    { "from": 3,  "each": 15 },
    { "from": 6,  "each": 13 },
    { "from": 12, "each": 11 },
    { "from": 25, "each": 9.5 },
    { "from": 50, "each": 8.5 }
  ],
  "maxPerOrder": 50,
  "maxDesigns": 12,
  "modifiers": []
}
```

- **Modifiers: none at launch.** A flat modifier applies at every tier, so a "ready-made design $X cheaper" modifier
  would drop under the cost floor at 25 and 50. The name tag costs a few cents of plastic in the same two
  parts, so a "no tag" discount isn't worth the page's complexity. Ready-made designs (decision 30) sell at the
  same price: they save us the drawing (about $0.84), and the buyer gets the same object. The inlay
  surcharge of decision 29 waits for its own quote.
- **Launch price: none separate.** The ladder is the low-margin price RJ asked for: it sits about $2 above the
  lowest price that clears a 30% pessimistic margin ($20 for one, $14.50 for two, $11 for six, $10.25 for a
  dozen, $7.25 for 50). Launch day has no traffic yet, and a lower price can't make visitors appear. The cushion
  covers what nobody has measured (the next section). Look at it again after the acceptance order and the first ten paid
  orders, when Slant's timing, the remake rate and the draw-to-buy rate are known.
- **Promotion code: one, small and capped.** `AGAIN`: $3 off any order, for an order placed after a first one.
  Stripe makes it: one coupon (`amount_off` 300 USD, `max_redemptions` 100, `redeem_by` 2026-12-10), one promotion
  code. A dollar amount, not a percentage: 20% off a 50-ornament order would be $85. The code goes on the thanks
  page and in the shipping email, so only people who've bought see it, and the code stays shareable at no
  cost. The margin on a single with the code is $5.13 (27%) pessimistic and about $6 expected, the thinnest
  case on the page, so the cap matters.
- **Beyond 50:** the page says to write for a quote. Slant's per-part price may drop at 100 and 1,000 units (below).

## Cost floor per ornament

Measured numbers are from docs/CHARGES.md (2026-11-19). Everything else is an assumption, stated here so it can
be changed.

| Ornaments in the order | Slant parts | Slant shipping | Slant total | Slant each |
| --- | --- | --- | --- | --- |
| 1 | $4.02 | $6.93 | $10.95 | $10.95 |
| 2 | $8.04 | $7.14 (interpolated) | $15.18 | $7.59 |
| 3 | $12.06 | $7.35 | $19.41 | $6.47 |
| 6 | $24.12 | $8.40 | $32.52 | $5.42 |
| 12 | $48.24 | $10.15 | $58.39 | $4.87 |
| 25 | $100.50 | $10.45 (interpolated) | $110.95 | $4.44 |
| 50 | $201.00 | $11.95 | $212.95 | $4.26 |

Shipping is to West Virginia, the dearest lower-48 zone measured. Other lower-48 zones run up to $1.20 less for
one ornament. Alaska and Hawaii cost about $1.50–2.00 more, so a single there still clears about $6.90 at $22.

- **Stripe:** 2.9% + 30¢ per payment (re-read at stripe.com/pricing on 2026-11-20). West Virginia orders add 0.5% for
  Stripe Tax and a fee on the tax collected, about 0.7% of the price in all. That's in the WV column below. The
  pricing page lists Stripe Tax at 0.5% for no-code integrations (Payment Links, Checkout) and $0.50 a transaction
  for API integrations. Our Worker creates Checkout Sessions, which I take to be the first, but I couldn't
  confirm it. If it's the second, a West Virginia order costs $0.50, about 2% of a single.
- **Drawings:** $0.06 each (docs/CHARGES.md: $0.053 measured, budgeted at $0.06). A buyer's design takes 2 tries
  on average (the cap is 3). Non-buyers burn 3 tries each. Nobody has measured the share of people who draw and
  go on to buy, so it's an assumption: **20%** for the expected case, **10%** for the pessimistic case. That makes
  $0.84 a design (20%), $1.74 (10%) or $0.49 (33%). It's charged per design, not per ornament, so a dozen of one
  design carries $0.84, and a dozen different designs carry $0.84 each. The pessimistic case assumes every
  ornament is a different design, up to `maxDesigns` of 12. Ready-made designs and bring-your-own drawings cost
  nothing here.
- **Remake reserve:** 3% of the Slant total, for a broken or mismatched ornament (decision 20's remake promise). It's
  generous for big orders, where a remake is one or two ornaments, not the whole order.
- **Not counted:** RJ's time, the $5 a month Workers Paid plan, a dispute ($15 each), refunds for drawings that fail
  and orders RJ rejects. Stripe's fee isn't returned on a refund.

| Ornaments | Slant | Stripe at the tier price | Drawings: expected / pessimistic | Reserve | Cost each, expected | Cost each, pessimistic |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | $10.95 | $0.94 | $0.84 / $1.74 | $0.33 | $13.06 | $13.96 |
| 2 | $15.18 | $1.29 | $0.84 / $3.48 | $0.46 | $8.88 | $10.20 |
| 3 | $19.41 | $1.61 | $0.84 / $5.22 | $0.58 | $7.48 | $8.94 |
| 6 | $32.52 | $2.56 | $0.84 / $10.44 | $0.98 | $6.15 | $7.75 |
| 12 | $58.39 | $4.13 | $0.84 / $20.88 | $1.75 | $5.43 | $7.10 |
| 25 | $110.95 | $7.19 | $0.84 / $20.88 | $3.33 | $4.89 | $5.69 |
| 50 | $212.95 | $12.63 | $0.84 / $20.88 | $6.39 | $4.66 | $5.06 |

Stripe, drawings and reserve are per order. The pessimistic margin on a West Virginia order (tax and Stripe Tax in) is $7.90
at 1, $13.37 at 2, $17.88 at 3, $30.98 at 6, $45.96 at 12, $93.55 at 25 and $169.29 at 50. Prices where the pessimistic
margin hits zero (break-even): $13.75 for one, $10 for two, $9 for three, $7.75 for six, $7 for a dozen, $5.75 for
25 and $5 for 50.

**How sensitive is it?** A single at $22 makes $8.04, $8.94 or $9.30 for draw-to-buy rates of 10%, 20% and 33%. The
price barely depends on the rate. It depends on Slant's box: a single's $10.95 is half the price, so one remake
costs a single's whole margin.

## Competitors (seen 2026-11-20)

"Page" means I read the page itself. "Snippet" means only a search engine's summary of it. **Etsy returned 403 to
every fetch I made, in the built-in browser as well, so no Etsy figure was read from a listing**, and I didn't try
to get past the block. The rest of the Etsy rows are snippets from Etsy's search pages. Shipping is blank where the
page doesn't show it before checkout.

### 3D-printed and made-from-photo

| Seller and product | Price | Shipping | Read | URL |
| --- | --- | --- | --- | --- |
| Baker Street Cutters, pet portrait ornament, 3D-printed cameo relief, white plastic, 4 in | $45.00 | not shown; USPS Ground Advantage from Idaho, 3–7 business days to make | page | [product](https://www.portraitcutters.com/product-page/custom-pet-portrait-ornament-from-photo-3d-printed-cameo-style-decor), [shipping](https://www.portraitcutters.com/shipping-returns) |
| Meshy, pet photo keychain, full-colour raised portrait, leather frame (not an ornament) | $39 | at checkout; 7–10 days; free remake | page | [shop](https://www.meshy.ai/shop/keychain) |
| Figuro, custom pet figurines (not flat ornaments) | $49–$89 (catalog to $499) | at checkout, DHL Express; 2–4 weeks | page | [FAQ](https://getfiguro.com/pages/faq) |
| Etsy, 3D-printed dog ornament, personalized | $20.75 | not seen | snippet | [search](https://www.etsy.com/market/custom_pet_ornament_3d) |
| Etsy, 3D dog ornament with Santa hat and lights, from a photo | $14.99 sale | not seen | snippet | [search](https://www.etsy.com/market/dog_photo_ornament) |
| Etsy, 3D-printed hand-painted dog or cat ornament from a photo | $12.55 (was $27.90) | not seen | snippet | [search](https://www.etsy.com/market/3d_ornament_from_photo) |
| Etsy, 3D-printed resin family-photo ornament | $35.46 | not seen | snippet | [search](https://www.etsy.com/market/3d_photo_christmas_ornament) |
| Etsy, lithophane photo ornament | $29.95, free shipping (another at $10.20, was $12.00) | free (the $29.95 one) | snippet | [search](https://www.etsy.com/market/3d_photo_ornaments) |
| Etsy, 3D-printed pet name bone ornament | $11.70 + $8.62 shipping (from 2026-11-17, not seen again) | $8.62 | snippet | [listing](https://braille3dprint.patternbyetsy.com/listing/1112887942/custom-pet-name-christmas-tree) |
| Love and Kin, raised 3D ceramic and acrylic pet photo ornaments (the article doesn't say how they're made) | $17.99–$19.99 (was $24.99–$39.99) | at checkout | page | [article, 2026-10-12](https://loveandkin.com/en-us/blog/custom-dog-ornaments) |

### Printed photo

| Seller and product | Price | Shipping | Read | URL |
| --- | --- | --- | --- | --- |
| Shutterfly pet metal ornament | $12.49 (was $24.99); buy-one-get-one code listed as ending Nov 19 | free at $99 | page | [product](https://www.shutterfly.com/p/photo-gifts/ornaments/photo-gallery-pet-metal-ornament) |
| Personalization Mall, two-sided pet memorial metal ornament | $14.99 (was $29.99) | at checkout; ships in 1–2 days | page | [product](https://www.personalizationmall.com/Pet-Memorial-Personalized-Photo-2-Sided-Ornament-p45421.prod) |
| YouCustomizeIt, pet photo snowflake ornament, aluminum | $15.88 each for 1–5 | at checkout; overnight option arrives Nov 27 | page | [product](https://www.youcustomizeit.com/p/Pet-Photo-Vintage-Snowflake-Ornament/462803) |
| Vistaprint, photo ornaments, metal or ceramic | not shown; 100 maximum, quote over 50 | at checkout | page | [category](https://www.vistaprint.com/photo-gifts/christmas-ornaments) |

### Laser-cut and engraved wood

| Seller and product | Price | Shipping | Read | URL |
| --- | --- | --- | --- | --- |
| Uncommon Goods, laser-engraved pet portrait wood slice, 3 in | $35.00 | not shown; free with a paid membership; ships by Nov 25 | page | [product](https://www.uncommongoods.com/product/personalized-pet-portrait-wood-slice-ornament) |
| My Heart Gift, basswood dog silhouette with a name, 9 cm | $25.99 (was $51.98) | free standard (5–9 days); $7.95 expedited | page | [product](https://www.myheartgift.com/custom-dog-christmas-decoration) |
| Personal Creations, laser-cut wood bone or paw with a name | $14.99 (25% off applies) | not shown | page | [product](https://www.personalcreations.com/product/Pet-Laser-Cut-Wood-Ornament-Bone-30448337) |
| Foxwood Engraving, line-art breed silhouette | $22.95 | at checkout | snippet | [product](https://foxwoodengraving.com/products/personalized-dog-breed-ornament) |
| All Custom Gifts, birch dog or cat silhouette, 3.5 in, name and year | $13.00 | $5.95 flat | snippet | [product](https://www.allcustomgifts.com/products/personalized-christmas-pet-silhouette-ornament) |
| McIntosh Woodworking, 3 in laser-cut dog with a bone tag | $15.95 | free | snippet | [product](https://www.mcintoshwoodworking.com/Personalized-Dog-Christmas-Ornament--Custom-Pet-Name-Wood-Ornament--Laser-Cut-3-Dog-Lover-Gift--Handmade-in-USA--Its-Treat-OClock-Somewhere-Holiday-Decoration_p_3686.html) |
| Forest Decor, wooden dog silhouette with a name | $79.99 (an outlier) | free over $49 | snippet | [product](https://forest-decor.com/product/custom-wooden-dog-ornament-with-pet-name-or-phrase/) |

### Where we land

- **One ornament, delivered:** printed-photo ornaments list at $12.49–$15.88 on sale, shipping extra, and wood
  silhouettes cost $13–$26 before shipping. Where shipping is shown, the landed price runs from $15.95 (McIntosh, free
  shipping) through $18.95 (All Custom Gifts, $13 + $5.95) to $25.99 (My Heart Gift). The 3D-printed pages
  I could read start at $39. At $22 with shipping and the tag
  included we sit in the middle of the wood and photo group and below the 3D-printed pages (Baker Street $45,
  Meshy $39). Only Etsy snippets are cheaper ($12.55–$20.75).
- **What a lower price would buy:** $19 (the wood silhouette's $13 + $5.95 landed price) leaves $6.03 expected and
  $5.13 pessimistic (27%) on a single, below the 30% line, and one remake ($10.95 at Slant) takes nearly two sales' margin. Shutterfly and Personalization Mall are showing half off ($12.49 and $14.99
  against list prices of $24.99 and $29.99), so the photo ornaments are the hardest to compete with this month and
  may not stay that cheap. We don't beat the photo ornaments on price at one ornament, and we don't need to.
- **Several ornaments:** the field's multi-buy is thin. Shutterfly had a BOGO code (ended Nov 19), YouCustomizeIt
  has "bulk" at 12+ without showing it, and Personalization Mall quotes bulk. Etsy shipping isn't known.
  Three at $15 each is $45 shipped, with no extra fee per ornament.

## Church, school, club: a dozen or more of one design

Decision 26 makes this the same path as a pet. At launch the pages offer pets, people and the ten ready-made
designs, so a buyer of a dozen would pick a ready-made design (or send one drawing). A church or school drawn
from a photo ("place") comes after launch (decision 27).

| Seller and product | 12 | 24 | 25 | 50 | Minimum, shipping | Read | URL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Lazer Designs, laser-engraved alder, 3 × 2 in, text only, one design | $8.78 | $7.73 | — | $6.94 | none; free shipping | page | [product](https://www.lazerdesigns.com/prince-of-peace-ornament) |
| White House Historical Association, official ornament, fundraising price | — | — | $23.50 (25–99) | $23.50 | 25; free on 1–5 only | page | [fundraising](https://shop.whitehousehistory.org/pages/fundraising) |
| YouCustomizeIt, school mascot ceramic ball | "bulk" at 12+, not shown | | | | none | page | [product](https://www.youcustomizeit.com/p/School-Mascot-Ceramic-Ball-Ornament-Christmas-Tree-Personalized/155429) |
| Vistaprint photo ornaments | quote over 50 | | | | 100 maximum | page | [category](https://www.vistaprint.com/photo-gifts/christmas-ornaments) |
| Promotional-product vendors, for example Rush Order Tees and Beacon Design | | | | | minimums of 50–250 | snippet | [Rush Order Tees](https://www.rushordertees.com/ornaments/) |
| **Us, per the ladder** | **$11.00** | **$11.00** | **$9.50** | **$8.50** | **none; shipping and tag included** | | |

- Lazer Designs shows where a bulk curve goes: $30.99 each for one or two, $8.78 at twelve, $5.10 at 500. Its
  ornament is a text-only blank in one colour. Ours is a drawn, two-colour portrait that can be a custom
  subject, at the same price. The fundraising price of $23.50 (25+) is the White House's, for an official ornament
  with a licence behind it. Neither is a like-for-like comparison, but both bracket us.
- A club buying 25 at $9.50 pays $237.50 and ships in one box. The White House's own fundraising page says a
  group could earn up to $10 an ornament reselling at its price. At $9.50 a group reselling at $18–$20 earns
  $8.50–$10.50 on each. I'm not claiming that's what groups charge, only that the margin exists. Selling the
  group on this is a copy line for step 11.
- Our margin at a dozen is $5.57 an ornament expected ($3.90 pessimistic), $4.61 at 25 and $3.84 at 50. A thin
  margin on large orders puts more money at risk in a bad batch: a failed 50-ornament run costs $213 at Slant.
  The 3% reserve isn't enough for that. For orders over 24, RJ may want to look at each design's preview before the
  order goes to Slant, not only at mismatches (decision 19).
- **Cliffs:** a tier's total can be lower than the one before. Twelve at $11 is $132, but eleven at $13 is $143.
  So buyers just under a break are better off adding ornaments, and step 9's page already tells them how much
  the next tier saves. The same holds at 25 and 50. I left it, because the alternative is more tiers on the page.
- **Families with several designs:** three pets, or five grandchildren, are an order of 3 or 5 at $15 each. The tier
  follows the order's total count whether the designs match or not (docs/ORDERS.md, decision 26).

## Does Slant discount volume any other way?

Short answer: nothing public says so, and one public page suggests our API quotes might hide a drop.

- **Public pages (read 2026-11-20):** the FAQ says each upload "shows prices at 1, 100 and 1000 units for every
  upload, and the unit price drops as quantity goes up", at [slant3d.com/faq](https://www.slant3d.com/faq).
  The [service page](https://www.slant3d.com/3d-printing-service) says "Prices update for 1, 100 and 1000+ units",
  and [Teleport](https://www.slant3d.com/teleport) says "Order 100 or 1,000,000. No minimums". None gives a rate card,
  a business or bulk program, a reseller tier or a contact for large orders. The
  [quoter](https://www.slant3d.com/megaquoter) asks about "regular restocking" and "one large one-time order", but shows
  no prices without an upload.
- **Our API quotes show no drop from 1 to 100 units** (docs/CHARGES.md: each part priced the same at 1, 6, 12, 20,
  50 and 100). Either the drop begins above 100, or the web quoter's prices aren't the API's. We don't know which.
 
- **The other programs don't apply.** The Shopify app has a $9 a month base plan and "a custom price based on
  fulfillment request's cost to print" ([app page](https://apps.shopify.com/slant)). Portals deducts production cost
  from each sale. Tangled is filament at $10/kg for members. SlantBox is a subscription that builds refills into the part
  price. A Slant blog post titled "Does Slant 3D do White-Label Services? Yes!" (2026-11-09) is listed on its blog index. Its page
  gave me an error, so I only have the title.
- **Not contacted.** Only Slant can answer, so here is the question for RJ to send (it names no one and no account;
  add the account email when sending):

> Hello. We order two-part PLA ornaments through your API (two STLs of about 39 g each per ornament, one box per
> order, orders of 1 to 50 ornaments, shipping to the lower 48, Alaska and Hawaii). Four questions:
>
> 1. Your FAQ says the quoter shows prices at 1, 100 and 1000 units and that the unit price drops as quantity goes
>    up. Our API quotes for the same parts show one price per part from 1 to 100 units. Does the API return the same
>    prices as the web quoter? At what quantity does a part's price drop, and by how much?
> 2. Is there a business, volume or reseller rate for an account that sends a steady flow of API orders? If so,
>    what are the thresholds, and how do we apply?
> 3. Shipping to one address rose from $6.93 for one ornament to $10.15 for twelve and $11.95 for fifty in our
>    quotes. Is that the rate card for everyone, or is there a lower business rate?
> 4. What is the lead time for an order of 25 to 50 ornaments (50 to 100 parts) placed between December 1 and
>    December 10? Your FAQ says 99.5% of orders ship in under two business days. Does that hold for orders this size?

Question 4 matters most this week: the order-by date of Dec 10 assumes Slant's timing, which the acceptance order
(step 17) will show for one ornament but not for 50.

## Volume promotions: what launch carries without build work

Checked against step 9's Worker (`shop-worker/designs.js` and `index.js` on step 9's branch, 2026-11-20).

| Promotion | Build work? | Detail |
| --- | --- | --- |
| Several ornaments in one order, sharing one Slant box | **None.** | `priceOrder` takes the tier from the order's total count and prices every design at it. The page shows the next tier's saving (docs/ORDERS.md). Only `shop.json`'s `pricing.tiers` change. |
| Launch price | **None**, and not recommended (above). | It's the `each` values in the same file. A time-limited price needs a date check someone must remember to remove. |
| Promotion code for a second order | **One line, and a test.** | The Checkout Session is created without `allow_promotion_codes`, so Checkout shows no code box. Adding `allow_promotion_codes: true` to the `checkout/sessions` call in `shop-worker/index.js` turns it on. It can't be combined with the `discounts` parameter, and we don't use that one. Then the sandbox test: one order with a code, to see that automatic tax and the webhook cope. The webhook stores Stripe's `amount_total`, which already includes a discount, and nothing compares it with the order's price, so it needs no change. |
| The coupon and the promotion code themselves | None in the repo. A Stripe step. | Free. Made in the Dashboard or with the API, in sandbox first. The restricted key on file may not be allowed to create coupons, so RJ or an agent with the right key does it. Each redemption costs us $3, so RJ's yes to this plan covers `AGAIN` only. |
| Showing the code | None in the Worker. Copy. | The thanks page and the shipping email draft's text (steps 11 and 16). Stripe promotion codes can't restrict a code to "second order" (`first_time_transaction` only restricts to a first one), so the code is shared by showing it only after purchase. |

Stripe limits for reference (docs.stripe.com, "Add discounts"): a Checkout Session takes one coupon or promotion
code; a promotion code can set `max_redemptions`, `expires_at` and a minimum order amount; promotion codes cost
nothing to use.

## Not verified

- **No Etsy listing was read**; every Etsy figure is a search-engine summary, and Etsy's shipping isn't known.
- **Slant's volume pricing, shipping for 4–5, 25 and 100 ornaments, and lead time for large orders.** The 25
  row's shipping is interpolated; 2 is interpolated between the measured 1 and 3.
- **The draw-to-buy rate (assumed 20%, bad case 10%)** and the remake rate (3%). Both come from the first ten paid
  orders.
- **Whether Stripe Tax charges 0.5% or $0.50 on our Checkout Sessions.**
- Competitor prices are mid-sale: Shutterfly's and Personalization Mall's halved prices may return to list price
  in December, and the pages I read give no delivery promise past Dec 10.
- Pages not re-read (blocked or rate-limited): eBay, MyPetPrints, Etsy, mb3d.uk, Amazon, PurEvents on Etsy.
