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
  sky map, and the monogram's dot. It can't stand alone as a logo; it's always with the letters
  or in a group.
- **The monogram** (`monogram-logo-bw.svg`): the two halves of the wordmark's "t" (reading as a
  lowercase r over an l) with the ovaloid beside it. A stylized lantern, or the side of a
  robot's head. It's the favicon, and the site's menu button: the wordmark collapses into it,
  because its three parts are the wordmark's own "t" and period.

## Icons and the social image

`tools/brand/make_icons.py` makes `public/favicon.svg`, `favicon.ico`, `apple-touch-icon.png`
and `og.png` (the wordmark on the night photo, for link previews) from the monogram, in one of
the four tile colorings in `design/brand/favicon-options/`. The choice is `FAVICON` at the top
of the script. `src/components/HeadMeta.astro` puts them on every page.

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
