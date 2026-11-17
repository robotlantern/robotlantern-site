---
name: Pet ornament (two-part stencil)
stage: design
fulfillment: slant
next: RJ prints the fit test (Tucker) on Meltbot when he's ready, then an agent turns the picker into the product page (NOW.md, steps 33–34)
waiting_on: rj
updated: 2026-11-17
---

A flat ornament of a customer's pet in two colours of PLA: a **base** in one colour and a **stencil** sheet
in another that presses onto it, with the pet drawn as cut-outs in the stencil. An optional **name tag**
hangs below the head with the name cut through the same sheet. Two parts, no glue, any two of Slant 3D's
20 PLA colours. Slant prints and ships it. Our own prints are used for the listing photos, labelled as
examples (decision 10).

It replaced the mosaic design of 2026-11-13 on 2026-11-17. That design needed many pieces per ornament,
too fiddly to assemble, and Slant charges per part. The mosaic design and its batch are recorded in
[docs/LOG.md](../../docs/LOG.md). Its code, `tools/cutout/`, is kept for reference only.

## The design (approved 2026-11-17, "build-v3")

RJ saw the first ten printed on paper at actual size and approved them as they are.

- **Stencil:** 1.2 mm thick, one connected piece, printed face down. Every coloured shape must touch the
  rest. Where the drawing has floating details, the builder joins them to the sheet with short bridges, the
  way real stencils do, and warns if a bridge is over 3 mm. Nothing in it is under 1 mm, red or gap.
- **Base:** 3.2 mm thick, the pet's outline plus a 2 mm rim, with a 1 mm pocket the stencil drops into
  (0.10 mm clearance a side, so it sits 0.2 mm proud).
- **Joint:** six diamond pegs (2.2 mm square turned 45°, 1.4 mm tall) on the stencil's back press into round
  3.0 mm blind holes in the pocket floor. The peg's diagonal is wider than the hole, so the corners give.
  Untested in print: the fit test decides.
- **Hanging ring:** 10 mm across with a 4 mm hole, on the outline's centre line so it hangs level. A filleted
  neck joins it to the head.
- **Name tag** (optional): 17 mm of base below the head, 50–72 mm wide. The stencil covers it as a plate
  with the text cut through, so the letters show the base colour. Any text of one line, sized to fill the
  tag (capital height 5–11 mm), in one of five Google stencil fonts: Allerta Stencil, Saira Stencil One,
  Big Shoulders Stencil, Emblema One, Wallpoet. No border or rule: RJ tried both and preferred it plain.
- **Size:** 84 mm wide, 100–123 mm tall with the tag.
- **For Slant's slicer:** every wall is vertical and every hole opens upward, so neither part has an
  overhang or a bridged roof. Slant flagged no supports on any of the 20 parts. (Orca reports 2–4
  internal bridge moves per base, over infill.)

## How a design is made

1. **Drawing:** GPT Image (through `codex exec` on gpt-6-luna) redraws the photo as a two-colour stencil:
   head and neck only, mostly solid colour with the features as white cut-outs, one connected piece, no
   line or gap under 2% of the width. One brief per pet.
2. **Builder:** reads the drawing as ink on white, drops specks, thickens thin strokes, fills thin gaps,
   bridges loose pieces, then makes the outline, pocket, pegs, ring and tag. Out come `base.stl`,
   `stencil.stl`, a preview and two SVGs for the picker (with and without the name cut). It checks the
   stencil is one piece and both meshes are watertight.
3. **Colours and plates:** a palette file gives each pet its Slant colours and the shelf spool that stands in
   for each colour on Meltbot. A packer lays parts onto 220 mm plates by colour.
4. **Quotes:** `~/work/3d-modeling/tools/estimate.py --slant`, free, through printdb's cache.

The builder, the batch, the picker and the print queue live in a scratch folder next to this repo,
`../ornaments-design-session/`. It stays out of Git because the designs come from family photos. **These
designs don't go in printdb** (RJ, 2026-11-17).

## Numbers (first batch, ten family pets)

- **Slant:** $3.56–4.01 an ornament with a name tag, both parts, before shipping. That's $1.14 a part plus
  plastic; white costs more per gram. Ten came to $38.05. Shipping for a single small box is still unknown
  (the only data point is $10.15 for 684 g).
- **Meltbot:** about 48–61 minutes and 20–26 g an ornament. The batch packs onto nine colour plates,
  6 h 38 min and 176 g in all.
- **Shelf colours for photos:** white, black, red, orange, green (olive, darker than Slant's) and blue. There's
  no PLA on the shelf for Slant's tan, brown or bone white (step 3).

## The customer's choices

A front-end prototype of the picker exists in the scratch folder: pick a design, base and stencil colours
from Slant's 20 PLAs (clear hidden), suggested pairs, a swap button, a warning when the two colours are too
close, and the name tag with live fitting and the five fonts. It sends nothing. Its output is the JSON the
builder needs (colours with Slant ids, text, font). Photo swatches of each colour are being gathered so it
doesn't rely on reported hex values.

## Open

- **Fit:** do the pegs hold, and is the pocket right? (step 33)
- **Price** and whether Slant ships it from the first order (decision 14).
- **Customer photos and GPT Image:** a customer's photo would go to OpenAI. The privacy page changes
  first if so (decision 13 left this open).
- **A proof by email** before it's made (decision 13).
- **Weak drawings:** the turtle failed; some images come back with a part that can't print (a lost bridge),
  which the one-piece check catches. Regenerate or pick another image. A person looks at every preview.

## Related

- The printed-photo version of a pet ornament (a die-cut sticker on a plain backing) is in
  `products/photo-cutout/`.
