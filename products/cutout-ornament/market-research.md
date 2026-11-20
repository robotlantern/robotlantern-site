# Pet ornament: market research

_2026-11-17. Desk research from web searches and page fetches that day. Prices are snapshots and change often._

_Corrected 2026-11-20 by NOW.md step 19: the figures that were wrong are marked "(2026-11-20)" below.
The prices, shipping, cost floor and recommendation are in [pricing.md](pricing.md)._

**Question:** does anything like our product exist (upload a pet photo, get a custom two-colour 3D-printed
ornament that looks like the pet), and how does it compare on what it is and what it costs?

## Short answer

1. **Nobody I found sells our exact product.** That is two flat PLA parts (a base and a stencil), two
   colours, drawn from the customer's photo as a stencil portrait, printed and shipped on demand. Nothing
   found does the whole thing.
2. **The three nearest neighbours each differ on a key point.** Full-colour 3D-printed keychains (Meshy)
   cost about twice our likely price. Photo-to-3D file generators sell a file, not an ornament. Laser-cut
   wood "silhouette" ornaments are the right look and price but are one colour and cut by hand-made
   designs.
3. **Our unit cost is small; shipping decides the price.** Slant quotes $3.56–4.02 an ornament before
   shipping (docs/CHARGES.md, [product.md](product.md)). Shipping was measured on 2026-11-19: $6.93 for one
   ornament to West Virginia, so a single costs $10.95 at Slant, falling to $4.87 each for a dozen (2026-11-20).
   Custom pet ornaments sell for roughly $8–$50, most at $12–$35. [pricing.md](pricing.md) works out the margins.
4. **The market is crowded and mostly 2D (printed photo on ceramic, glass or metal).** Our differences are the
   look (a bold, graphic stencil portrait, not a photo) and the honest "your pet in two colours of plastic"
   pitch. The risk is not that the idea is taken. The risk is that buyers who want a recognisable photo
   likeness will prefer a printed photo at $10–$25.

## What we are building (for the comparison)

Two parts of PLA, 84 mm wide, 100–123 mm tall with the name tag: a 3.2 mm base and a 1.2 mm stencil sheet
with the pet cut out as shapes, pressed together with pegs, plus an optional stencil-font name tag. Any two
of Slant's 20 PLA colours. A GPT Image redraw turns the photo into a two-colour stencil, a script builds the
STLs, a person checks the preview, Slant prints and ships. Ten family pets (dogs, cats, a parrot) were
designed and printed on paper at actual size; the sheet of ten reads as bold, graphic portraits with
recognisable breeds and markings. Slant quotes: $3.56–4.02 each with a tag, no supports flagged.

## What exists

### 1. Photo-to-3D file generators (you print it yourself)

| Service | What you get | Price | Note |
|---|---|---|---|
| 3D AI Studio, Holiday Ornament | A chunky figure with a Santa hat and a hanging loop, STL or 3MF, in 2–3 minutes | free to try, download is on paid plans (price not listed) | Does not print or ship. No multi-colour output; fine details "don't hold up" at ornament size ([source](https://www.3daistudio.com/blog/3d-printed-christmas-ornaments-from-a-photo)) |
| SupaVoxel | Pet figurine model, STL or 3MF, up to a 4-colour file | 3 free credits, STL/3MF export from $25 a year | "SupaVoxel makes the 3D file. It does not print or ship figures." Long fur and whiskers lost ([source](https://supavoxel.com/use-cases/pet-figurine)) |
| PrintPal | Pet photo to printable figurine | free generator listed | Not fetched; seen only in search results ([source](https://printpal.io/tools/pet-3d-generator)) |
| Meshy (model tool) | Photo to textured 3D model, multi-colour 3MF | not checked | Seen in search results ([source](https://www.meshy.ai/use-cases/3d-printed-gifts/pet-figurines)) |

**Reading:** these are tools for people who own a printer. They are not competitors for a gift buyer who
wants a finished ornament, but they show that "pet photo to 3D print" is a well-known idea, and that the
common failure is lost fine detail at ornament size. Our stencil approach is built around exactly that
failure (bridged details, nothing under 1 mm).

### 2. Made-to-order 3D-printed pet pieces

- **Meshy pet keychain:** printed in full colour on industrial CJP printers from the customer's photo, **US$39**
  on the shop page, 7–10 days, shipping extra, remade free if it doesn't match the approved design. Another
  Meshy page says the keychains are a fixed 2 in (50 mm) during the beta and that the final price depends on
  colour coverage and complexity, so "$39" may be a starting price
  ([shop](https://www.meshy.ai/shop/keychain), [creative lab](https://www.meshy.ai/creative-lab/keychain);
  shop page read 2026-11-20: $39 confirmed; a keychain with a leather frame, 7–10 days, shipping at checkout; the size figure is from the creative-lab page and wasn't re-checked).
- **Etsy 3D-printed pet items** (search snippets, not fetched; Etsy pages block my fetches): a 3D-printed
  pet-name bone ornament, any colour combination, $11.70 plus $8.62 shipping to the US
  ([listing](https://braille3dprint.patternbyetsy.com/listing/1112887942/custom-pet-name-christmas-tree));
  a "Custom Dog Ornament from Photo, 3D Printed Pet Christmas Keepsake with Name" at $35.00; custom 3D
  pet figurines from $15 to $119, one at $43 ("3D Shadowtone Layered Color" sculpture,
  [listing](https://my.stlflix.com/?p=624045)); a UK seller's small pet print from a photo at £16.99
  ([mb3d](https://mb3d.uk.com/products/custom-pet-print-3d-print-from-any-photo)). Etsy search pages:
  [3D ornament from photo](https://www.etsy.com/market/3d_ornament_from_photo),
  [custom pet ornament 3D](https://www.etsy.com/market/custom_pet_ornament_3d).
- **Figuro** (custom pet figurines and memorial ornaments from photos): $49–$89 per its FAQ, with an optional
  hand-painted finish ([FAQ](https://getfiguro.com/pages/faq)). A sculpture, not a flat ornament.

**Reading:** the made-to-order 3D-printed segment is figurines and full-colour pieces at **$35–$90**, mostly
one-person Etsy shops doing hand-modelling. None is an automated, two-colour, flat design at a few dollars of
cost. The flat two-colour stencil look is, as far as I could find, **unoccupied in 3D print** (a negative
finding from a few searches, not a proof).

### 3. Laser-cut and engraved wood: the closest look and price

- A wood ornament in the shape of a breed outline, cut through as a silhouette, or with a back for a "3D
  effect": **$15.07–$19.87** (PurEvents, listed in Cuteness's roundup of Etsy pet-ornament shops). The same
  roundup has a wood slice with an engraved pet photo at $17, a burned-in portrait with name banner at
  $45–$51, and a laser-cut paw with a name at $6.50 ([Cuteness](https://cuteness.com/13774929/best-etsy-shops-personalized-pet-ornaments)).
- Other search snippets: photo-engraved wood ornaments about $5–$20; 3D-carved wood pet portraits $130–$180
  ([search page](https://www.etsy.com/market/personalized_pet_ornaments_with_photo)).

**Reading:** the silhouette is a known and liked form, but one colour and a generic breed shape, not the
individual pet. Our stencil carries the pet's own markings (a tuxedo cat's bib, a boxer's mask), which a
breed outline cannot.

### 4. Printed-photo ornaments (the volume market)

| Product | Price | Source |
|---|---|---|
| Ceramic photo ornament, Etsy/eBay | about $9.99–$14.99 | [eBay](https://www.ebay.com/itm/197277135497) |
| Pewter pet photo ornament | $15.88 for 1–5 (page read 2026-11-20; it says pewter in one place and aluminum in another) | [YouCustomizeIt](https://www.youcustomizeit.com/p/Pet-Photo-Vintage-Snowflake-Ornament/462803) |
| Shutterfly pet metal ornament | $12.49, was $24.99 (page read 2026-11-20; a buy-one-get-one code ran to Nov 19) | [Shutterfly](https://www.shutterfly.com/p/photo-gifts/ornaments/photo-gallery-pet-metal-ornament) |
| Two-sided pet memorial photo ornament | $14.99, was $29.99 (page read 2026-11-20) | [Personalization Mall](https://www.personalizationmall.com/Pet-Memorial-Personalized-Photo-2-Sided-Ornament-p45421.prod) |
| Zazzle ceramic ball photo ornament | CA$34 | [Zazzle](https://www.zazzle.ca/custom_pet_photo_ball_ornament-256474610204640544) |
| Hand-painted glass pet ornament (artist draws from photo, proof first) | $39.95 | [MyPetPrints](https://www.mypetprints.co/products/custom-pet-printed-glass-ornament) (search snippet) |
| Lightweight aluminium memorial ornament with photo | $7.80–$12.75 | Cuteness roundup above |
| Crown & Paw custom pet ornaments (metal) | not found | [Trend Hunter](https://www.trendhunter.com/trends/petinspired-ornament) |

**Reading:** this is where most buyers go. $10–$30 for the pet's actual photo, on a recognised
material, delivered fast by large print shops. We cannot win on likeness or price here. We can win only on
being a different kind of object: a designed, graphic, tactile portrait rather than a photo on a disc.

## How we compare

| Axis | Our ornament | Nearest existing | Verdict |
|---|---|---|---|
| Likeness to the pet | Stencil portrait: markings and expression, not skin tone or fur texture | Printed photo is exact; AI-figure tools are generic | **Behind photos, ahead of silhouettes** |
| Look | Bold two-colour graphic, any two of 20 colours, optional stencil name | Wood silhouette (one colour); figurines (sculpted) | **Distinct** |
| Price (our cost to make) | $3.56–4.02 + shipping ($6.93 for one to WV, $4.87 each at a dozen; 2026-11-20) + payment fees | Meshy $39; Etsy 3D-printed $11.70–$35; wood $15–$20; photo ornaments $10–$30 | **Low cost base** |
| Likely retail | $22 for one, less with more in the order ([pricing.md](pricing.md)) | Middle of the market, well under 3D-printed full-colour pieces | **Room to price on value** |
| Personalisation | Photo, two colours, name in five fonts | Usually name or photo only | **Richer than most** |
| Turnaround | Slant says 99.5% of orders ship in under 2 business days plus transit (its FAQ, 2026-11-20); not measured on our order | Meshy 7–10 days; Baker Street Cutters 3–7 business days to make; Etsy varies | **Check against the order-by date with the acceptance order** |
| Proof | The preview the customer approves, and a remake promise (decisions 19 and 20) | Meshy remakes if it differs from the approved design; MyPetPrints proofs first | **Covered** |
| Quality risk | Fit proven on a printed Buster (product.md); AI drawing sometimes fails | Established print shops | **Must test** |
| Who prints | Slant 3D, on demand | Etsy sellers print themselves; Meshy prints in-house | **Comparable** |

### Price floor, with the numbers we have

- Cost per ornament at Slant: $3.56–4.02 (parts and plastic, no shipping).
- Payment fees: 2.9% + 30¢, confirmed at stripe.com/pricing on 2026-11-20 (about $0.88 on a $20 sale).
- Shipping (corrected 2026-11-20): measured 2026-11-19 with free drafts, $6.93 for one ornament to West Virginia
  and $5.73–$8.95 across states, so a single costs $10.95 at Slant. Twelve cost $4.87 each. Etsy's bone ornament
  shows the market tolerates shipping near the item price ($8.62 on $11.70; snippet, not re-read).
- The price list, with shipping included, is in [pricing.md](pricing.md). The open question here is closed.

## What this suggests (written 2026-11-17; pricing.md sets the price)

1. **Price in the $19–$29 band**, not the cheapest. (2026-11-20: pricing.md recommends $22 for one ornament, now that shipping is measured. The 3D-printed pages I could read start at $39.) Our product costs more than a printed disc to make and
   needs a person to check each preview. Under $15 invites comparison with a photo ornament, which we lose.
2. **Sell the look, not "a photo of your pet".** Copy and pictures should say it is a stencil portrait in
   two colours you choose, with real prints shown (decision 10). Showing a customer's photo beside the
   ornament makes the likeness comparison honest and favourable.
3. **Offer a proof, or a clear remake promise.** (Decided: the preview is the proof, and the remake promise is decision 20.) Meshy and MyPetPrints both do. A preview image before
   production is also our own quality check for failed drawings.
4. **Lead with animals that suit the style.** My own reading of the ten-design sheet (a judgement, not
   data): strongly marked faces, like a tuxedo cat or a boxer, look best. Competitors all admit that fine
   fur and whiskers get lost at ornament size, so the listing should say so too.
5. **Memorial buyers are a large part of this market** (Figuro, MyPetPrints and many Etsy listings are built
   around it). It is a natural audience but also an emotional one: the proof step and remake promise matter
   more there.

## Limits of this research

- Searches were done on 2026-11-17. Several pages blocked my fetches (Etsy, Meshy shop, bigshinyballs, Crown
  & Paw, MyPetPrints returned 403, 429 or errors), so prices from them are from search-result snippets and
  may be stale or sale prices. Rows marked "search snippet" and the Etsy figures should be re-checked by
  hand before they go in a listing or a pitch.
- I did not find sales volumes, reviews or turnaround for any competitor, so the demand claims above are
  qualitative.
- "Nobody sells this" is based on a handful of searches. A niche Etsy shop or a new startup could exist.
- I did not test Slant's lead time or shipping. (2026-11-20: shipping is measured, in docs/CHARGES.md; lead time isn't.)
- A small number of the search-result summaries were model-written, not the pages' words. Anything the
  report relies on is cited to a URL so it can be checked.
