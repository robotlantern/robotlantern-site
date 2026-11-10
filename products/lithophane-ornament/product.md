---
name: Lithophane ornament
stage: feasibility
fulfillment: self
next: Agent builds the bulb-and-cap recipe, the configurator's preview and the feasibility numbers (NOW.md, step 14)
waiting_on: agent
updated: 2026-11-10
---

A round Christmas ornament with the customer's photo in its wall as a lithophane. It looks like plain
white plastic until the tree lights come on, and then the picture appears. It slips over one bulb of a
light string. A separate cap, printed in gold silk PLA like the metal cap of a glass ornament, clips on top
and holds it on the strand (RJ's memo, 2026-11-10). It's a Christmas gift, so its page carries an order-by
date.

## Sketch

- **Bulb:** one piece, printed upright for continuous tone (the engine's `sphere` form with `projection:
  front`). White at launch (*proposed*, NOW.md decision 7). A coloured wall tints and dims the picture,
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

## Feasibility (next)

- The `ornament` recipe: bulb and cap from an order folder, with Meltbot estimates (time, grams), and a
  Slant quote for later.
- The configurator's tone preview, drawn on the bulb.
- Cost per ornament (filament, cap, box, label), the time per ornament, a weekly cap, prices of
  comparable ornaments, and a proposed price.
- The order-by date for Christmas, from the handling time and USPS's holiday dates.

## Prototype

A matte white wedge (about 15 minutes and 3 g), then a bulb and a cap. RJ photographs the wedge on a
light for calibration (lithophane-maker `docs/ENGINE.md`, "Filament optics and calibration"), and the
ornament lit on the tree for the listing.

## Questions

- Which lights are on RJ's tree: mini LED, C7 or C9? (NOW.md, step 3)
- The picture on the front only, or wrapped around the ball?
- A ribbon loop on the cap too, so it can hang where there's no light?
