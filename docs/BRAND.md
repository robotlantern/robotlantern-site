# Brand mark

Status: exploring (NOW.md task 16). The wordmark stays. What's missing is a single mark that
works as the logo, the favicon and the motif: the stars in the nav and the star each card is
drawn from.

## What RJ wants

- The wordmark ends in an asterisk instead of a period: spark-like, asymmetrical, slightly
  skewed.
- That same shape becomes the nav's asterisks and the star each home-page card starts from.
- One line and stacked versions of the wordmark, left and right aligned.

## The risk: sparks are crowded

Asterisks and sparkles are now the shorthand for AI. A four-point sparkle reads as "AI feature"
in most apps, and Anthropic's Claude mark is an orange, irregular, radiating spark. A warm,
asymmetric spark next to a site that credits Claude could be read as borrowing it. The mark has
to be recognisably Robot Lantern's, not a spark in general.

Ways to make it ownable:

- **Build it from the wordmark.** The letters are chunky, with rounded ends and stencil-like
  cuts (the t's crossbar is split from its stem). A spark made from those same strokes belongs
  to the wordmark and to no one else. "Robot five" in `design/brand/sparks.svg` starts in this
  direction.
- **Keep the lantern.** The period is the lantern, and it already has a story on the home page:
  it breaks away as a shooting star and lands, glowing. A spark that is the lit period
  ("Lit period") keeps that story.
- **Use motion, not just shape.** The comet flight, the twinkle and the line-drawing are
  already distinctive. A plain shape moved in those ways can carry more identity than a complex
  shape standing still.
- **Avoid:** the four-point sparkle (reads as AI), and orange radiating bursts (reads as Claude).

## Tests for any candidate

- Reads at 16 px as a favicon, in one colour, on light and dark.
- Still reads as an asterisk in the nav at label size.
- Distinct from the Claude spark, the generic AI sparkle and a plain typographic asterisk,
  side by side.
- Sits with the wordmark's weight: arms about as thick as the letters' strokes.

## Materials (`design/brand/`)

- `sparks.svg`: six concepts, large and at 64, 32 and 16 px on light and dark.
- `wordmark-lockups.svg`: one line, stacked left, centered (current) and right, each with the
  period and with a weight-matched skewed six.
- `asterisks-distinct.svg`: 512 distinct asterisks from 1,935 Google Fonts families, the most
  common shape first, labelled with the family and how many look-alikes it stands for.
  `asterisks-all.svg` has every family. Both are local only (large; see `.gitignore`);
  `tools/brand/` rebuilds them in about a minute.
- `make_brand_sheets.py` regenerates the first two.

Google Fonts are under the SIL Open Font License or Apache 2.0, so a glyph can be used as the
start of a logo. Credit the font on the Credits page if the final mark keeps its outline.
