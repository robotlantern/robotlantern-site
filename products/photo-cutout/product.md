---
name: Custom cutouts (standees and ornaments)
stage: feasibility
fulfillment: self
next: Agent builds the cutout recipe and the sticker files, after the subject picker (NOW.md, step 16)
waiting_on: agent
updated: 2026-11-17
---

The subject of a photo (a person, a pet, a car) cut out as a 3D-printed shape in any colour of PLA, with
the photo printed and cut to the same outline and stuck on its face. A separate base, a wedge or a fin,
prints with it so it stands on a shelf. A smaller version has a loop instead and hangs as an ornament
(RJ's memo, 2026-11-10).

## Sketch

- **Outline:** from the subject picker, smoothed, with a thin rim of the backing colour showing around
  the photo.
- **Backing:** a few millimetres of PLA in the customer's choice of colour.
- **Base:** a wedge or a fin that slots into the backing, chosen from the photo's bottom edge or by the
  customer (question).
- **Ornament:** smaller, with a loop at the top (Slant sells green ornament hooks, SL046, $0.25).
- **Photo:** printed on sticker paper and cut on the Cricut with Print Then Cut, then applied by RJ, or
  shipped as a sticker for the customer to apply.
- **Sizes:** the standee heights and the ornament's size are set in feasibility.

## What exists

- lithophane-maker: IS-Net subject masks, outlines from a mask, extrusion and booleans. Its pop-art
  silhouette lamp is the nearest recipe. Nothing printed.

This is the second product to open, after the ornament. It's the simplest use of the subject picker,
which pop-outs and the projector reuse.

## Sticker print-on-demand (RJ, 2026-11-17)

RJ's idea for the ornament version: the pet ornament's outline (`products/cutout-ornament/`) as a plain backing
printed by Slant, and the photo printed and cut to the same outline by a sticker print-on-demand service and
mailed to the customer separately. The customer sticks it on. Upload a PNG with transparency and the service
cuts along its edge. Make the backing's outline the cut line plus 2–3 mm, so a slightly misplaced sticker
still looks right. The Cricut version (Inkbot Alpha plus Print Then Cut) stays the prototype route.

A web search on 2026-11-17 found these. Prices are catalogue base costs, unconfirmed, and nothing has been ordered:

- **Printful die-cut stickers** (catalogue product 957): public order API, matte vinyl, 2–6 in, about $4.36 at
  3×3 in, no minimums, branded packing slip. The first pick to test. The kiss-cut version (358) is about $2.34 but
  comes on a square backing sheet.
- **Printify die-cut** (blueprint 600): any shape, but prices and shipping need an API token.
- **Sticker it (stickerit.co):** a print API where we supply the cut line ourselves; keys by email.
- No die-cut sticker, or no usable API: Gelato, Prodigi (kiss-cut squares, sales contact), Gooten, Sticker
  Mule (its API only reorders), StickerYou.
- Unknown everywhere: whether the cut follows the alpha edge exactly or sits off it, the white rim, how well
  vinyl sticks to PLA, single-sticker shipping, and content rules for customer photos. A Printful 3×3 sample
  answers most of it. It's a charge, so add it to docs/CHARGES.md and get RJ's go first.
- Printify cuts small gaps in the art as one shape, so fill gaps between legs and in fur before upload.

## Questions

- Which inkjet printer, sticker paper and Cricut? Print Then Cut's size limit sets the biggest standee.
  (NOW.md, step 3)
- Seal the sticker with a laminate or clear coat so it survives handling?
- Base style: the customer's choice, or automatic?
