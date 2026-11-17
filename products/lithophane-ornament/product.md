---
name: Lithophane ornament
stage: parked
fulfillment: self
next: Paused by RJ on 2026-11-13 in favour of the pet ornament (products/cutout-ornament/, a two-part stencil since 2026-11-17); resume after launch
waiting_on: rj
updated: 2026-11-13
---

A round Christmas ornament with the customer's photo in its wall as a lithophane. It looks like plain
white plastic until the tree lights come on, and then the picture appears. It slips over one bulb of a
light string. A separate cap, printed in gold silk PLA like the metal cap of a glass ornament, clips on top
and holds it on the strand (RJ's memo, 2026-11-10). It's a Christmas gift, so its page carries an order-by
date.

## Sketch

- **Bulb:** one piece, printed upright for continuous tone (the engine's `sphere` form with `projection:
  front`). White at launch (NOW.md decision 7). A coloured wall tints and dims the picture,
  so a colour is offered only after its wedge is printed.
- **Cap:** gold silk PLA (printdb spool 34, about 200 g); silver (spool 22) could be an option. It clips
  onto the bulb's neck and grips the light's socket or wire.
- **Light:** the customer's own string lights, **LED only**. PLA softens at about 60 °C, and older
  incandescent bulbs can run hotter. The page says which bulbs it fits, from what's on RJ's tree.
- **Size:** set by the bulb it slips over and by Meltbot's print time. Glass ornaments run about
  60–80 mm across, which is the range to try.
- **Photo:** cropped to a circle on the front; the rest of the ball is plain. Faces need contrast, so the
  configurator warns about dark or flat photos.

## What exists

- lithophane-maker (2026-10-04): the `sphere` form, the optical tone curve, the calibration wedge, and the
  heart keepsake recipe, the nearest relative (a gold frame with a ribbon ring). Nothing printed.
- printdb lists 25 g of white PLA. The four matte spools need adding first (NOW.md, step 3).

## Feasibility (2026-11-10, step 14)

**Paused (RJ, 2026-11-13):** an ornament takes about 2½ hours to print, it isn't distinctive enough to lead
the shop, and matte PLA's translucency is untested. Left when it paused: look at the Blender renders
(lithophane-maker `fixtures/orders/ornament-couple/out/render_*.png`) and register it in printdb. The recipe,
preview and numbers below stand.

The recipe is `products/ornament.py` in lithophane-maker (its docs/PRODUCTS.md, section 4). The preview is
`src/scripts/shop/lithophane-bulb.js`, with a test page at `/shop/test/ornament/`. The light is an option:
mini LED (72 mm ball), C7 (76 mm) or C9 (84 mm). The bulb and socket sizes are catalogue values until RJ's
lights are measured.

- **Print time on Meltbot (OrcaSlicer):** bulb 2 h 08 min, 42 g white at 0.16 mm layers, neck down with a
  brim; cap 19 min, 2 g gold silk. About 2 h 30 min an ornament.
- **Cost per ornament:** about $1 of filament (white at an assumed ~$20/kg; gold from printdb's price),
  about $1 for a box and tissue (*estimate*), and Stripe's 2.9% + 30¢. The label is covered by the flat shipping
  charge. USPS Ground Advantage under 1 lb is now one price per zone, with a holiday surcharge through
  2027-01-17, so check the real label price in Pirate Ship before the first label (docs/CHARGES.md).
- **Weekly cap (*proposed*): 10.** That's about 25 h of printing and 2–3 h of RJ's hands (start, trim the brim,
  assemble, test, pack).
- **Comparables:** Etsy lithophane ornaments are about $12–30, mostly flat. MAD Made Creations sells one for
  $9.99. Shutterfly glass photo ornaments are $26–30, and Personalization Mall's lightable glass ones $14–28,
  with the bulb sold separately.
- **Proposed price: $34 + $5 shipping.** It's a lit ball rather than a flat disc, made to order by one person,
  with limited weekly capacity. It nets about $30 after fees, materials and box.
- **Order-by date for Christmas: Wednesday 2026-12-09.** USPS's recommended Ground Advantage send-by date is
  2026-12-17 (lower 48). The listing promises shipping within 5 business days.
- **Calibration wedge:** sliced and checked for Meltbot (lithophane-maker `tools/slice_wedge.py`: 7 min, 3 g,
  Textured PEI, 220/55 °C). It isn't uploaded yet, because uploading needs the matte white spool in printdb
  (step 3). Matte PLA is often more opaque than plain white, and the wedge shows whether it's translucent enough.

## Prototype

A matte white wedge (about 15 minutes and 3 g), then a bulb and a cap. RJ photographs the wedge on a
light for calibration (lithophane-maker `docs/ENGINE.md`, "Filament optics and calibration"), and the
ornament lit on the tree for the listing.

## Questions

- Which lights are on RJ's tree: mini LED, C7 or C9? (NOW.md, step 3)
- The picture on the front only, or wrapped around the ball?
- A ribbon loop on the cap too, so it can hang where there's no light?
