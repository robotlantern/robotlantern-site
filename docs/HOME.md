# Home page

Status: the first slice (task 11) is built in `src/pages/index.astro` and RJ approved it on his
phone on 2026-09-27: docking, the flying period, the collapse into the menu, and two cards (the
Pleiades chat, then the essay). It extends the sunset scroll prototype
(`public/prototypes/sunset-scroll/`, tag `sunset-scroll-v1`); timings below are measured against
that version. The sky map ("Map") is the next big piece.

## Sequence

1. **Arrival.** The sunset scroll as built: sunset, afterglow, stars fading in, lantern lighting.
2. **The wordmark docks.** After about 6% of the v1 scroll (roughly a quarter of a screen), the
   wordmark shrinks and flies to the upper left. It lands by about progress 0.3 of v1, when the
   afterglow is fading and the stars are coming in. The letters finish lighting before they
   land. The period (the brand's ovaloid, docs/BRAND.md) breaks away and flies on a curve,
   spinning, with a tail drawn along the path it has just travelled (behind it in either
   direction, as long as its speed makes it). It lands last, settling at its own angle, then
   glows. Its motion eases toward the scroll position rather than jumping with each scroll step.
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
- The section nav is anchored at the bottom, on the tree silhouette, with a haze rising behind it;
  the top stays clear for the sky and the wordmark (RJ, 2026-09-27). Every other page now has
  the same nav at the bottom, on a dark bar (2026-09-30).
- Once the period has landed, the wordmark collapses into the logo in the corner (the menu
  button), as on every other page, and opens out again on the way back up. (A pinned header with a dark fade was
  tried and dropped on 2026-09-27: iOS Safari showed content behind the status bar, and the dark
  bar broke the sunset.)
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

## Approved choices (task 11, 2026-09-27)

- The letters fly from progress .06 to .3 and finish lighting by .28; the period leaves at .1 and
  lands at .36; its lamp lights after it lands. Then, 24px of scroll later, the wordmark collapses
  into the logo, the menu button (four frames, timed; docs/BRAND.md).
- The first card draws once the mark has landed and the card's top is on screen.
- The Pleiades on the first card are seven ovaloids at catalog positions, not matched to the photo
  (which stays fixed while cards scroll). The essay's star is one ovaloid until stars are
  assigned from the map.
- Each card shows the opening (RJ's first message and two paragraphs of the reply; the essay's
  first two paragraphs), then "Keep reading". The title links too.
- On a page shorter than the sky's run, the sky finishes at the bottom, so the page always ends
  at night.
- The nav sits on the tree silhouette at the bottom and appears as the mark lands.

## Section marks

RJ drew them in Affinity (`design/section-marks/section-marks-rj.svg`). The stars count up:
THOUGHTS has one large star with a short dashed tail, the same in the nav and the menu (RJ, 2026-10-01; it first ran as a dashed underline from the start of the word); CHATS a binary pair on
a dashed ring; BUILDS three stars in three sizes on a left-pointing pentagon; SHOP four on a
tilted diamond around the word. The stars are the brand's ovaloid, each turned its own way. Lines
are faint (30% white), stars bright and twinkling. `src/lib/section-marks.ts` holds the geometry
in em from the end of each word, so it scales with the label, and each nav item leaves room for
how far its mark reaches. `src/components/SectionIcon.astro` draws the same marks as standalone
icons. This replaced dashed one-star shapes, which replaced star-fitted asterisms that RJ judged
overfitted.

## Open

- The order of cards after the first two. For launch: the essay, then products.
- The full map view (see "Map"): when there's enough content to form shapes. It could become an
  item in the site menu.
