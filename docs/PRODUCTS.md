# Product pipeline

Adopted by RJ on 2026-10-01. Every product idea gets a folder, `products/<slug>/`, with a
`product.md` that says what stage it's at and what happens next. Ideas can sit at any stage for
as long as they need: the file holds the state, so nothing depends on anyone remembering.

    python3 tools/products/board.py

prints every product by stage, with its next step and who it's waiting on.

## Stages

Each stage ends with a decision. RJ makes the ones marked **RJ**; an agent does the work between
them.

| Stage | The work | Done when |
| --- | --- | --- |
| `idea` | A name and a few lines: what it is and why someone would want it. No research. | It has a slug and a pitch. |
| `sketch` | What it is concretely: product type, size, what's printed where, who it's for, open questions. | **RJ:** "worth checking." |
| `feasibility` | Which printer and product, the printer's own price quote (free), shipping, the price and margin, file specs, and the rights to every piece of art and data. | **RJ:** go or no-go, on the numbers. |
| `design` | Print-ready files to the printer's spec, and mockups. | **RJ** approves the mockups. |
| `sample` | Only for a new product type or a new printer (the blanket, say): one sample, ordered and photographed before it lists. **Costs money**: RJ approves each order (docs/CHARGES.md). | **RJ** approves the sample, or it goes back to `design`. |
| `listing` | The shop entry: product file, mockups or photos, copy, the Stripe price and Payment Link (NOW.md, task 7). A known printer and product (a Gelato poster or tee) lists from its mockups, and its sample is ordered the same day as a quality check. | **RJ:** it goes live. |
| `live` | On sale. If a quality-check sample disappoints, the listing pauses and the product goes back to `design`. | Retired, or a new version starts at `design`. |

Ideas that wait go to `parked`, with a line saying why; dropped ones go to `dropped` and stay as
a record.

## Things RJ makes

A product RJ makes and ships himself (a 3D print, a hand-pulled print, a cut piece) goes through
the same stages, minus the printer. Its file says `fulfillment: self` and how many there are.

- **Limited runs.** The Payment Link stops after that many sales, so the shop never owes more
  than RJ can make.
- **Handling time.** The listing promises one RJ can keep while working in fits and starts,
  such as "ships within 5 business days".
- **Return address.** Labels need one, and it isn't his home: a PO box, or the registered agent
  if its plan forwards mail.
- **Labels cost money** per package (docs/CHARGES.md).
- **No children's products** without the testing US law requires for them; aim things at adults.
- **Returns.** Handmade items are final sale except for damage in shipping.

## Intake

RJ says "product idea: …" in any session, or drops a line in `inbox/`. The agent makes the folder
at `idea`, writes down what RJ said, and does nothing else unless asked. Ideas don't cost a
session.

## The file

```markdown
---
name: Stargazing blanket
stage: sketch
fulfillment: gelato   # or self, with a quantity; or a printer's name
next: RJ says whether it's worth checking
waiting_on: rj        # rj or agent
updated: 2026-10-01
---

A paragraph: what it is and why.

## Sketch
## Feasibility
## Design
## Sample
## Listing
```

Each stage adds its section as it's reached. Small design sources (SVG, notes) go in the folder.
Large print files don't go in Git: keep them in `.private/products/<slug>/` until listing, when
they need a public URL the printer can fetch.

## Rules

- **Margin.** Proposed floor, until RJ sets his own: what's left after the product, the printer's
  shipping, Stripe's fee (2.9% + 30¢) and any sales tax the printer adds is at least 30% of the
  price. Feasibility shows the arithmetic.
- **Rights.** Every element needs a clear right to sell: RJ's photos and art, AI art made for
  the shop, and data. ESA's Hipparcos and Gaia data is non-commercial, so it can't go on a
  product (NOW.md, task 15).
- **One product, one stage per session**, unless it's trivial. Move the stage, update `next`,
  commit.
- **Launch doesn't wait on the pipeline.** The shop opens with whatever two to four products
  reach `listing` first.
