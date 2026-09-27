# Home page

Status: design agreed with RJ on 2026-09-25. The first slice (task 11) is built in
`src/pages/index.astro`: docking, the shooting-star period, and two cards (the Pleiades chat,
then the essay). It extends the sunset scroll in
`public/prototypes/sunset-scroll/` (tag `sunset-scroll-v1`, previewed at
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
products but are their own category. RJ named the sections on 2026-09-27: **Thoughts** (essays),
**Chats** (conversations), **Builds** (interactives) and **Shop** (products). Each has its own
small icon, shown with its name in the navigation.

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

## Built choices to review (task 11)

- The period leaves at progress .1 and lands at .36, after the letters (.06 to .3). The letters
  now finish lighting by .28; the period's lamp lights after it lands.
- The first card draws once the mark has landed and the card's top is on screen.
- The Pleiades on the first card are drawn from catalog positions (the seven brightest), not
  matched to the photo, which stays fixed while cards scroll. The essay's star is a plain
  four-point star until stars are assigned from the map.
- Each card shows the opening (RJ's first message and two paragraphs of the reply; the essay's
  first two paragraphs), then a "Keep reading" link. The title links too.
- On a page shorter than the sky's run, the sky finishes at the bottom of the page instead, so
  the page always ends at night.
- The nav appears as the mark lands, in the same place as on every other page.

## Open

- **Section marks (decided 2026-09-27; NOW.md task 12).** RJ drew them in Affinity
  (`design/asterisms/section-marks-scratch-rj.svg`). The stars count up: THOUGHTS has one large
  asterisk with a dashed trail rising from under the word; CHATS a binary pair on a dashed ring;
  BUILDS three stars in three sizes on a left-pointing pentagon; SHOP four on a tilted diamond
  around the word. Lines are faint (10% white), stars bright and twinkling. Every asterisk is
  three strokes at 0°, 60° and 120°, with the stroke 1/7.7 of its width.
  `src/components/SectionMark.astro` holds the geometry in em from the end of each word, so it
  scales with the label. The conversion snapped stars onto their vertices and regularized the
  pentagon (it was within 2px). This replaced the one-star shapes, which replaced star-fitted
  asterisms that RJ judged overfitted.

- Where the navigation sits before the full map exists: beside the docked wordmark?
- The order of cards after the first. For launch: the essay, then products.
- Whether the wordmark is readable at header size. Check on a phone.
- Whether tapping the lantern opens the map.
- The first card uses the conversation page's style (task 5, done).
