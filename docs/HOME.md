# Home page

Status: design agreed with RJ on 2026-09-25, not built yet. It extends the sunset scroll in
`prototypes/sunset-scroll/` (tag `sunset-scroll-v1`, previewed at
https://rl.rblt.io/prototypes/sunset-scroll/). Timings below are measured against that version.

## Sequence

1. **Arrival.** The sunset scroll as built: sunset, afterglow, stars fading in, lantern lighting.
2. **The wordmark docks.** After about 6% of the v1 scroll (roughly a quarter of a screen), the
   wordmark shrinks and flies to the upper left. It lands by about progress 0.3 of v1, when the
   afterglow is fading and the stars are coming in. The letters finish lighting before they
   land. The period breaks away and travels as a shooting star with a short trail. It lands last,
   then glows.
3. **The first card draws.** At the same point, the Pleiades appear. A white outline starts at
   the Pleiades, which sit on the card's top edge, and runs right, down, left, up, and right
   again to close. Then the content appears quickly, with a slightly see-through fill so the sky
   still shows. The first card is the opening lines of "It's Always the Pleiades", styled as the
   conversation page.
4. **Later cards.** When a card's bottom reaches the middle of the screen, the next card's
   outline starts drawing, each from its own star (see "Map"). Drawn cards stay drawn. Scrolling
   back up un-draws them in reverse order.

## Motion rules

- **Driven by scroll position:** the sky, the lantern and the wordmark's flight.
- **Triggered:** each card's outline and content. They run a fast animation (about 0.8s) when
  their point is crossed, and reverse when it's crossed going back up.
- The sky runs over a fixed scroll distance, at the pace RJ approved, then holds at full night.
  It doesn't stretch over the whole page.
- A quick flick past several cards draws them one after another. After a reload, cards already
  above the screen are simply there.
- The docked header gets a soft dark fade, so cards passing under it don't collide with it.
- Reduced motion: a simple fade replaces the flight and the line drawing.
- All content is in the page. Without the script or the animation, everything still reads.
- Card fill: about 75% night color with a light blur behind it.

## Content types

There are four: conversations, essays, products and interactives. Interactives accompany
products but are their own category. The sections won't be named with those words. Each gets a
sky name plus a plain line underneath, so a newcomer can tell them apart. RJ picks the names.

## Map

The content is a network, and the navigation uses a constellation metaphor.

- **The sky is the map.** Each item gets a real star in the night photo, and each content type
  gets its own region of the sky. Conversations could take the Pleiades. A card's outline starts
  at its own star.
- **Lines only stand for real links.** Examples: a conversation and the essay it led to, a
  product and its interactive, or an essay and a print made from it.
- **Keep it calm:**
  - Nothing pans or zooms unless the reader asks, and the whole sky is always in view.
  - Lines are faint by default and brighten when their star is in focus.
  - Reading always happens in the center column. Choosing a star opens the normal page.
  - Every star is also in a plain list, for keyboards and screen readers.
- **Desktop:** content stays in a center column. The sky on either side shows the current
  card's star and its links.
- **Phone:** the map is its own view. Tapping the lantern might open it (undecided).
- **At launch:** the center column, the docked header and the desktop margin glow. The full map
  view waits until there's enough content to form shapes. Stars are assigned from the start.

## Open

- Section names (RJ).
- Where the navigation sits before the full map exists: beside the docked wordmark?
- The order of cards after the first. For launch: the essay, then products.
- Whether the wordmark is readable at header size. Check on a phone.
- Whether tapping the lantern opens the map.
- The first card needs the conversation style, which task 5 restyles for the night. Until then,
  use a provisional night version of the old prototype's style.
