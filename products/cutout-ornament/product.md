---
name: Pet ornament (snap-together mosaic)
stage: feasibility
fulfillment: self
next: RJ decides whether it's the first product, which shape, and the pet filament colours (NOW.md, step 30)
waiting_on: rj
updated: 2026-11-13
---

A flat ornament of a customer's pet, made from their photo: the pet's head as a cartoon, in flat pieces of
coloured PLA that snap onto a black back, like a small stained-glass window or a mosaic puzzle. Each piece
prints flat in one colour, so the files can be made from the photo by a program, Meltbot (and later
Slant) prints them, and the customer only snaps the pieces into place. Putting it together is part of the
gift. RJ proposed it on 2026-11-13 as the first product in place of the lithophane ornament, which prints
slowly, isn't distinctive enough, and hasn't been tried in matte PLA.

It comes from RJ's 2025 paper portraits: photos traced by hand in Illustrator into colour layers, cut on
the Cricut and stacked. The tracing was the work that made them impractical to sell, and it's the part
this replaces. RJ's original artwork (the Illustrator file and its preview) is in
`.private/products/cutout-ornament/`, kept private because it's a portrait of a real person.

## Sketch

RJ's sketch (`cutout-ornament-sketch.jpeg`): a common back with a grid of snap connectors, and a picture
layer that snaps on.

- **Pieces:** every part of the face belongs to exactly one piece, in one filament colour. Pieces are
  1.6 mm thick and print face-down. Neighbouring pieces are inset 0.3 mm each, so a 0.6 mm black line of the
  back shows between them. That line is the cartoon's outline, and it hides fit tolerance.
- **Snap grid:** the back has a square socket every 4 mm. Each piece carries a 2 mm square pin wherever its
  interior covers a socket, so it can't fall off and a single pin stops it turning. A two-colour version
  is the black-and-white "stencil" (RJ's 2025 portrait, second version); several colours make the mosaic.
- **Shape:** either the pet's own silhouette, with a 2 mm black border and a hanging tab (the "pet head",
  recommended), or a round 80 mm ornament with a festive field colour around the pet. A round back is the
  same for every order, so it could be printed in stock. A silhouette back is made per order.
- **Size:** 80 mm across. Bigger is easier to print and keeps more detail.

## Feasibility (2026-11-13)

The question was whether the vectorising step can be automated well enough. It can, but only with an AI
image step in the middle, and it runs on Sarcean.

**How it works.** `tools/cutout/mosaic.py` (prototype) does:

1. **Photo to cartoon.** FLUX.2 klein 4B, the local image model in `~/work/lab/flux-lab` (Apache 2.0; no
   third party sees the photo), redraws the cropped photo as a flat cartoon head: a few solid colours, bold
   eyes and nose, white background. It takes about 50 seconds a picture on Sarcean, so three or four
   versions per order cost a few minutes and RJ picks the best.
2. **Cartoon to pieces.** Background removal (the isnet model lithophane-maker already uses), colour
   clustering, a match to the filament list, then rules that make it printable by construction: no part
   narrower than 1.2 mm; every piece holds a pin; a small region that stands out (an eye, a nose) grows until
   it holds one, the way a cartoonist exaggerates features; a small one that doesn't stand out merges into
   its neighbour. It takes about 10 seconds.
3. **Pieces to files.** SVG layers per colour, an STL per colour plate (pins up) and the back's STL.
   They're deterministic, checked watertight, and ready for Meltbot or Slant. `tools/cutout/slice.py`
   slices them with the OrcaSlicer CLI on Meltbot's presets.

**What the test showed** (five pets from RJ's photo export of 2026-11-12; the comparison sheet and files
are in `.private/products/cutout-ornament/feasibility-2026-11-13/`):

- **Without AI**, clustering a real photo gives camouflage blobs: fur texture and lighting turn into
  patches, and the eyes get lost. Only a high-contrast dog in black and white read as itself. This is the
  problem RJ hit in December 2025, and better filtering doesn't solve it.
- **With the AI step**, the heeler and the puggle came out recognisable and printable in 10 pieces each, and
  the heeler kept its blaze, two-tone ears and grey patches. The prompt matters: asking it to keep the coat's
  colours and markings fixed the heeler, which the first prompt had turned tan.
- **Failures to fix before selling:**
  - Small eyes on a busy face (the spaniel) still merge away. Fix: handle eyes on purpose (find them,
    enlarge them, always keep them).
  - The cat's photo showed only the top of its head, so the model invented a face that reads half dog. Fix:
    ask for a face-on photo and the species, and put the species in the prompt.
  - Likeness drifts. A cartoon of "your" pet has to be checked by someone who knows it, so this product
    needs a proof (below).

**Print time and material (OrcaSlicer, Meltbot presets, 0.20 mm, matte PLA):**

| Ornament | Face plates | Back | Filament |
| --- | --- | --- | --- |
| Heeler, silhouette, 10 pieces, 5 colours | 33 min (4–8 min a colour) | 34 min | 19 g |
| Spaniel, round, 5 colours | 45 min | 41 min | 23 g |

Each colour is its own plate, because Meltbot has one extruder. Batching orders puts the same colour from
several ornaments on one plate, which spreads the warm-up and the swap. A round back can be printed ahead
in stock, and a thinner back (1.8 mm) would cut its time by about a quarter. Expect about an hour of machine
time and 20–25 minutes of RJ's hands per ornament once orders are batched in fours: picking the cartoon,
swapping plates and filament, checking the pieces, packing.

**Materials.** On the shelf: matte white, black, navy, ruby red; orange, olive, gold and silver silk in part
spools. Pets need **brown, tan, cream and grey**, and pink is nice for noses and tongues. None are in
printdb. An ornament uses only 1–3 g of each colour, so small spools last a long time. Buying them is a
charge, so it waits for RJ (docs/CHARGES.md).

**Price (*proposed*): $36 + $5 shipping.** Comparables found on 2026-11-13: 3D-printed pet figures and
layered sculptures from about $13 to $45; painted pet ornaments $40 (Etsy glass) to $78–90 (Minted). This is
custom art of the customer's own pet, made to order, with a proof. It nets about $32 after Stripe's fees
(about $1.50), filament (about 50¢) and a box (about $1, *estimate*). Check the label price in Pirate Ship
before the first one, as for the lithophane.

**Weekly cap (*proposed*): 8 at first**, then 15 once a batch has been made. The limit is RJ's time for
proofs and plate swaps, not the printer.

**Order-by date for Christmas: Wednesday 2026-12-09**, as for the lithophane (USPS Ground Advantage send-by
2026-12-17), with the proof round inside the 5 business days to ship.

**What this changes in the order flow** (docs/ORDERS.md):

- **A proof.** The cartoon can't be made in the customer's browser, so the configurator shows an example and
  the photo crop, the customer pays, and RJ emails the chosen cartoon from help@ for a yes or one redo.
  A no is a full refund. This changes decision 4 ("no proof round by default") for this product only.
- **Inputs:** a face-on photo, the species, the pet's name (for the box, optional), and the shape.
- **Privacy:** the AI step runs on Sarcean, so the photo goes nowhere new. The privacy page's existing
  promises cover it.
- **Slant later:** the pieces are loose flat parts the customer assembles, which is the kind of product
  Slant can ship (decision 3). Slant would need one order per colour, or a multicolour service; check
  before relying on it.

**Rights:** the FLUX.2 klein 4B weights are Apache 2.0 (flux-lab README). No style LoRA is used. The
cartoon is a new drawing of the customer's photo, which they confirm they may use (the terms already say
so).

## Prototype

1. **Fit coupon:** pins and sockets at three clearances (15 min, 3 g). RJ reports which one snaps and holds.
2. **One ornament:** the heeler (if its owner says yes) or a pet RJ picks, in the colours on hand, then
   in pet colours once they're bought. RJ assembles it and photographs it on the tree for the listing.

## Questions

- Is this the first product (NOW.md, step 30)? Silhouette or round, or both as options?
- Which pet colours to buy, and how much?
- Should the black-and-white "stencil" version be offered too, cheaper ($29?) and from stock colours?
- People as well as pets later? Likeness matters more for people, so pets first.
