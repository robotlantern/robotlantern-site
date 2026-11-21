---
name: Pet ornament (two-part stencil)
stage: listing
fulfillment: slant
next: the launch, NOW.md steps 7-17 (the tools in the repo, the Worker, the page, then a live order)
waiting_on: agent
updated: 2026-11-19
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

1. **Drawing:** GPT Image redraws the photo as a two-colour stencil. For customers, our Worker calls OpenAI's API
   (decision 16). For design work it ran through `codex exec` on gpt-6-luna. The brief asks for
   the head and neck only, mostly solid colour with the features as white cut-outs, in one connected piece,
   with no line or gap under 2% of the width. There's one generic brief per subject (`briefs/`, NOW.md
   step 7).
2. **Builder:** reads the drawing as ink on white, drops specks, thickens thin strokes, fills thin gaps,
   bridges loose pieces, then makes the outline, pocket, pegs, ring and tag. Out come `base.stl`,
   `stencil.stl`, a preview and two SVGs for the picker (with and without the name cut). It checks the
   stencil is one piece and both meshes are watertight.
3. **Colours and plates:** a palette file gives each pet its Slant colours and the shelf spool that stands in
   for each colour on Meltbot. A packer lays parts onto 220 mm plates by colour.
4. **Quotes:** `~/work/3d-modeling/tools/estimate.py --slant`, free, through printdb's cache.

The builder and the picker move into the repo (`tools/ornament/`, the product page; NOW.md steps 7 and 10). The
family batch, its drawings and the print queue stay in the scratch folder next to this repo,
`../ornaments-design-session/`, because they come from family photos. **These designs don't go in printdb or
Git** (decision 15).

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

## At launch (2026-11-20; NOW.md decisions 16-25)

- **The one product at launch.** Pets, and people too if decision 25 says yes. Ordered on
  `/shop/cutout-ornament/`, drawn by GPT Image through OpenAI's API (capped), built and checked by the
  `rl-orders` routine, drafted at Slant by our Worker, and processed by RJ ([docs/ORDERS.md](../../docs/ORDERS.md),
  [docs/PRODUCTION.md](../../docs/PRODUCTION.md)).
- **Choices:** any two of Slant's PLA colours (clear hidden), name tag on or off, one line of text up to 16
  characters, five stencil fonts. One size, 84 mm wide.
- **Defaults** (decision 20): $29 with US shipping and the name tag included; 25 a week; order by Dec 10 for
  Christmas until the first order shows Slant's timing; a free remake or refund if it arrives broken or
  doesn't match the preview.
- **Fit:** Buster (v1) printed 2026-11-19 and fits. Thin necks are widened to 1.8 mm since then (build-v6).
- **Listing photos:** Buster, Tucker and the heads from MeltBot, marked as examples (decisions 10 and 14).
  Their slot: put the files in `public/images/shop/cutout-ornament/` and list them in `shop.json`'s `images`. The
  product page then shows them as "Printed examples" ("Our own prints, shown as examples"), and the shop card
  uses the first in place of the ready-made drawings.

## Next variants (after launch)

RJ, 2026-11-19, on seeing the prints: they're big, so other ways to show them would sell. Ones that need no
prototype go first. Their checks, Slant quotes and renders are enough for RJ to say yes.

- **Large,** about 150 mm, filling a plate. The builder takes `--width`. Pegs, rim and thicknesses stay in mm,
  so it's the same design with bigger features, which print more easily. The quote rises with grams.
- **Wall:** the ring left off and an adhesive strip from Slant's components in the box. The ring already
  hangs flush on a small nail, so the listing can say that from day one.
- **Needs a print first:** a kickstand (print-in-place, or a slot-in third part), standard shapes (star, bell,
  round) for subjects without a clean silhouette, and the bridge placement for people.

## Open

- **Shipping from Slant** for one small box. The acceptance order (NOW.md step 17) gives the number. The price
  may move after that.
- **Weak drawings:** the turtle failed, and some drawings come back with a part that can't print. The builder's
  one-piece check catches those, and the order goes to RJ instead of Slant.
- **Cheaper drawings:** test lower quality and cheaper models right after launch (decision 16).

## Related

- The printed-photo version of a pet ornament (a die-cut sticker on a plain backing) is in
  `products/photo-cutout/`.
