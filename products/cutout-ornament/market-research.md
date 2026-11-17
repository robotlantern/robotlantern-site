# Pet ornament: market research

_2026-11-17. Desk research from web searches and page fetches that day. Prices are snapshots and change often._

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
3. **Our unit cost is tiny; shipping decides the price.** Slant quotes $3.56–4.01 an ornament before
   shipping (NOW.md, [product.md](product.md)). Custom pet ornaments sell for roughly $8–$50, most at
   $12–$35. A price of about $15–$25 looks defensible, but shipping from Slant for one small box is still
   unknown, so no margin can be stated yet.
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
recognisable breeds and markings. Slant quotes: $3.56–4.01 each with a tag, no supports flagged.

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
  figures from search results: the shop page itself returned 403 to my fetch).
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
| Pewter pet photo ornament | $15.88 | [YouCustomizeIt](https://www.youcustomizeit.com/p/Pet-Photo-Vintage-Snowflake-Ornament/462803) |
| Shutterfly pet metal ornament | from $24.99 | [Shutterfly](https://www.shutterfly.com/p/photo-gifts/ornaments/photo-gallery-pet-metal-ornament) |
| Two-sided pet memorial photo ornament | $29.99 | [Personalization Mall](https://www.personalizationmall.com/Pet-Memorial-Personalized-Photo-2-Sided-Ornament-p45421.prod) |
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
| Price (our cost to make) | $3.56–4.01 + shipping (unknown) + payment fees | Meshy $39; Etsy 3D-printed $11.70–$35; wood $15–$20; photo ornaments $10–$30 | **Low cost base** |
| Likely retail | roughly $15–$25 (RJ's call, step 36) | Middle of the market, well under 3D-printed full-colour pieces | **Room to price on value** |
| Personalisation | Photo, two colours, name in five fonts | Usually name or photo only | **Richer than most** |
| Turnaround | Slant production time not yet measured | Meshy 7–10 days; Etsy varies | **Unknown, must check against the order-by date** |
| Proof | Not decided (decision 13) | Meshy remakes if it differs from the approved design; MyPetPrints proofs first | **Gap if we skip it** |
| Quality risk | Fit untested (step 33); AI drawing sometimes fails | Established print shops | **Must test** |
| Who prints | Slant 3D, on demand | Etsy sellers print themselves; Meshy prints in-house | **Comparable** |

### Price floor, with the numbers we have

- Cost per ornament at Slant: $3.56–4.01 (parts and plastic, no shipping).
- Payment fees at Stripe's published US rate of 2.9% + 30¢ would be about $0.85 on a $20 sale (check the
  current rate before relying on it; not fetched today).
- Shipping: unknown for one small box. The only Slant data point is $10.15 for 684 g (docs/CHARGES.md). If a
  single ornament ships for several dollars, a $15 price leaves little. Etsy's bone ornament shows the
  market tolerates shipping near the item price ($8.62 on $11.70).
- So the price depends on one number we can't get without a real draft order: Slant's shipping for one box.
  Free-with-price or shipping-at-checkout is a decision for step 36.

## What this suggests (for RJ's step 36, not decisions)

1. **Price in the $19–$29 band**, not the cheapest. Our product costs more than a printed disc to make and
   needs a person to check each preview. Under $15 invites comparison with a photo ornament, which we lose.
2. **Sell the look, not "a photo of your pet".** Copy and pictures should say it is a stencil portrait in
   two colours you choose, with real prints shown (decision 10). Showing a customer's photo beside the
   ornament makes the likeness comparison honest and favourable.
3. **Offer a proof, or a clear remake promise.** Meshy and MyPetPrints both do. A preview image before
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
- I did not test Slant's lead time or shipping.
- A small number of the search-result summaries were model-written, not the pages' words. Anything the
  report relies on is cited to a URL so it can be checked.
