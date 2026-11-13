---
name: Pet ornament (snap-together mosaic)
stage: feasibility
fulfillment: self
next: RJ chooses and labels better pet photos, then an agent compares the routes and builds one (NOW.md, steps 31-32)
waiting_on: rj
updated: 2026-11-13
---

A flat ornament of a customer's pet, made from their photo: the pet's head as a cartoon, in flat pieces of
coloured PLA that snap onto a black back, like a small stained-glass window or a mosaic puzzle. Each piece
prints flat in one colour, so the files can be made from the photo by a program, Meltbot (and later
Slant) prints them, and the customer only snaps the pieces into place. Putting it together is part of the
gift. On 2026-11-13 RJ made it the first product in place of the lithophane ornament, which prints slowly,
isn't distinctive enough, and hasn't been tried in matte PLA (NOW.md, decision 13).

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
- **Name and year** (RJ, 2026-11-13): the pet's name and a year. The year defaults to the current one, and
  the customer can enter any year, so a photo of a pet long gone works too. It isn't framed as a memorial:
  the buyer reads the year as they like. More text may be allowed, depending on how the tool turns out.
  Letters must be at least 1.2 mm wide in every stroke, which at 80 mm favours a bold font and a plate or
  banner as its own piece.
- **More fun than a head** (RJ, 2026-11-13): designs with a joke or a prop, such as a Santa hat, reindeer
  antlers, a "Good boy" medal, a stocking, tangled lights or a "Naughty list" banner. These suit the
  template route (below): each design is drawn once per breed and recoloured for the customer's pet.
- **A portrait version** for people, as in RJ's 2025 cutouts: black and white, or colour. GPT Image
  reproduced both from his photo (below).

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

## Approaches to compare (step 32)

The first test (above) used FLUX.2 klein on single photos. RJ's photos, chosen and labelled with names
(NOW.md, step 31), are for comparing these properly. Under discussion on 2026-11-13, not decided:

1. **Local image model, photo in** (what was tested): FLUX.2 klein on Sarcean, about 50 s an image, the
   photo stays on Sarcean.
2. **Describe, then draw:** a vision LLM writes a structured description (species, breed, coat colours and
   where the markings are, ear shape, eye colour), and the image model draws from that, with or without
   the photo as a reference.
3. **GPT Image through Codex:** likely better at following the markings and at flat, clean shapes. The
   customer's photo would go to OpenAI, so the privacy page and docs/ORDERS.md change first (RJ: change the
   policy if needed). Per-image cost goes in docs/CHARGES.md before it's used for orders.
4. **Breed templates:** a library of cartoon heads, generated once, by species, breed and colouring, each
   already split into clean pieces. An order picks the nearest template, then recolours and reshapes it to
   the customer's photo (coat colours, markings, ear and muzzle proportions). Quality is set once per
   template rather than per order, and each order needs less compute. The work is deciding how much a
   template can be changed (recolour only, or warp too) before it stops looking like the pet.

### GPT Image test (2026-11-13)

Run through `codex exec` with `-m gpt-6-luna` (RJ: same image quality as the default model, far fewer
tokens). Codex's built-in image tool saves to `~/.codex/generated_images/`; a sandboxed run can't copy the
file out, so collect it from there. Close stdin (`< /dev/null`), or `codex exec` waits on it. The images are
in `.private/products/cutout-ornament/feasibility-2026-11-13/gpt-image/`.

- **Portraits** (RJ's 2025 photo and his two artboards as the style reference): the black-and-white and
  colour versions came out very close to his hand-cut ones, in a few minutes, from one prompt.
- **Pet designs** (generic breeds, no customer photo): a Santa-hat retriever, a cat in a stocking, a "Good
  boy" beagle with antlers, a lab tangled in lights, and a "Naughty list" tabby, among others. They're
  shop-quality flat art with names and years drawn in. This is far better than the local model.
- **Black is the back.** `mosaic.py --void black` makes no piece where the drawing is black. The back
  shows there, so black lines can be any width (closed eyes, a mouth line). Only the coloured and white
  areas become pieces. `--palette` snaps each pixel to the filament colours the prompt allowed.
- **A 3 mm grid with 1.5 mm pins** (`--pitch 3 --pin 1.5`) keeps small regions, like a muzzle, that a
  4 mm grid loses. The fit coupon has to prove a 1.5 mm pin holds.
- **What fails, and the rules it gives the prompt:**
  - Black fur vanishes into the back (the lab, the tuxedo cat). Pure black is only for lines and eyes;
    black fur is charcoal, a filament to buy.
  - Busy designs lose their small parts at 80 mm. Every coloured region must be at least about 6% of the
    width across, with no catchlights or teeth, or the ornament gets bigger.
  - Lettering drawn by the model can't be printed: the gaps between letters are under a millimetre. **Our
    code draws the name plate**, from a bold font with printable spacing, so the customer's text never goes
    through the model and can't be misspelled.
- **Round 2 used those rules** (`round2/BRIEF.md`): the beagle with antlers, the retriever in a Santa hat
  and the pug in a sweater collar now come through almost whole: 9–11 pieces in 4–5 colours, smallest
  35–43 mm², and the pieces read as the drawing (`round2-pieces.jpg`). The pug sliced at 29 minutes of face
  plates plus 33 for its silhouette back, 16 g. Still failing: the cat, whose charcoal is too close to
  the black lines (use a lighter grey, or check the snapped colours), and the mouth inside a portrait's
  beard. Codex made extra portraits it wasn't asked for, so a brief should say "exactly N images".
- **Where this leaves the routes:** GPT Image wins on design quality. The template idea fits it well: draw
  each design once per breed and colouring under these rules, approve it, then fit the customer's pet to
  it. Whether a customer's photo goes to GPT Image for recolouring or fitting is the privacy question in
  decision 13.

## Prototype

1. **Fit coupon:** pins and sockets at three clearances (15 min, 3 g). RJ reports which one snaps and holds.
2. **One ornament:** the heeler (if its owner says yes) or a pet RJ picks, in the colours on hand, then
   in pet colours once they're bought. RJ assembles it and photographs it on the tree for the listing.

## Questions

- Silhouette or round, or both as options?
- Name plate as its own piece, or lettering on the back too?
- A proof by email before making it, or not?
- Which pet colours to buy, and how much?
- Should the black-and-white "stencil" version be offered too, cheaper ($29?) and from stock colours?
- People as well as pets later? Likeness matters more for people, so pets first.
