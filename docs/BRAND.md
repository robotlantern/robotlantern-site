# Brand

Decided by RJ on 2026-09-27. The sources are his SVGs in `design/brand/`; the site draws from
`src/data/brand.json`, which `tools/brand/extract.py` makes from them (rerun it after editing).

## The pieces

- **The wordmark**, two ways: two lines, left-aligned (`wordmark-two-lines.svg`, the site's
  header), and one line (`wordmark-landscape.svg`). The letters take the lantern's light
  (`src/components/Wordmark.astro`).
- **The ovaloid** (`skewed-ovaloid.svg`): the wordmark's "o", rotated. It is the period, and the
  brand's one recurring shape: the lantern that flies across the home page and spins as it
  goes, the stars that cards are drawn from, the stars in the section marks and on the future
  sky map, and the logo's dot. It can't stand alone as a logo; it's always with the letters
  or in a group.
- **The logo** (`favicon-options/e-night-on-cream.svg`, RJ, 2026-09-30): the two halves of the
  wordmark's "t" as a lowercase r over an L, in night on a cream tile, with the orange ovaloid
  beside them. It's deliberately asymmetrical: half a robot's head, rounded on top (friendly)
  and square below. The t's lower half turns 90 degrees clockwise to become the r; its upper half
  drops to become the L. It's the favicon, the touch icon, the menu button and the way home from
  a build (`src/components/Logo.astro`). The older `monogram-logo-bw.svg` is the same glyphs
  without the tile.

## The collapse

Once the reader scrolls a little (on the home page, once the wordmark has landed), the wordmark
collapses into the logo in four quick frames, timed rather than tied to the scroll, so it never
rests half done. In the first frame all of "Robot Lantern" turns into one cream block where the
letters were; each frame it shrinks toward the logo's place while the t's halves and the period
ride on it into position, the lower half turning. Every frame is a whole tile. Scrolling back up
reverses it (`src/components/SiteMenu.astro`; RJ, 2026-09-30).

## Icons and the social image

`tools/brand/make_icons.py` makes `public/favicon.svg`, `favicon.ico`, `apple-touch-icon.png`
and `og.png` (the wordmark on the night photo, for link previews) from the logo. RJ chose E, his
resized version of D, on 2026-09-30; A to D in `design/brand/favicon-options/` are the options
he weighed. `src/components/HeadMeta.astro` puts them on every page.

## Rules

- **Never two ovaloids at the same angle.** Each takes an angle from its name (`turnFor` in
  `src/lib/brand.ts`), so a group looks scattered, or arranged as if orbiting, and stays the same
  between visits.
- **The light behind the period pulses** once it has landed in the wordmark.
- **Not a stellar theme everywhere.** The corona and eclipse idea was tried (it didn't hold up at
  every size and on every background) and set aside. The night sky belongs to the home page and
  the sky map, not to the mark.

## History

Explored on 2026-09-27 and set aside, all in Git history: star-fitted asterisms, the dashed
section shapes, six spark concepts, every Google Fonts asterisk (512 distinct shapes, harvested
by a script), and an eclipse prototype. The lesson worth keeping: sparks and asterisks now read
as "AI", and an orange radiating burst reads as Claude's mark. Ownable meant building from the
wordmark itself.
