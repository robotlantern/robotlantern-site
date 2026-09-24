# What to take from earlier attempts

The earlier attempts live in sibling folders on RJ's machine and aren't published. Treat them as
read-only sources. Copy each item listed here when its task arrives, and don't import anything
wholesale.

## Shopify prototype (`../robot-lantern-shopify`, September 15–18, 2026)

To view it, run `scripts/rl run build` there, then `scripts/rl run preview` and open
http://127.0.0.1:4173/.

**Take:**

- **Essay page design:** the journal page, which has a regular view, contribution highlighting,
  "Inside this post" (the editing conversation as JSON) and the Exact Markdown link, plus the
  contributor footer. Its layout and behavior are close to final. Restyle it from light cream
  to the night-sky palette (README, "Look"). The attribution tool is being rebuilt (NOW.md task 3).
- **Conversation page design:** the reader's template and CSS. Leave out the parts that split a
  conversation across several Shopify articles; those were workarounds for Shopify's limits.
  Its sample conversation (a voice chat) is replaced by `its-always-the-pleiades`, a text chat
  with inline photos, in `src/content/conversations/`.
- **Attribution tool:** `tools/wording.py` and `tools/wording.ts`. It's the starting point for the
  fix. The rules are described in the "exact_wording_v1" section of `docs/CONTENT-CONTRACT.md`.
- **Content principles:** "Invariants" 1–7 in `docs/CONTENT-CONTRACT.md`.
- **Essay source material:** `.private/inbox/first-post/` holds the final essay (`article.md`),
  the initial and final drafts (the initial draft is RJ's original), and the writing chat
  (`source-chat.retrieval.json`, 24 turns, GPT-5.6-sol).
- **Brand:** the images in `site-design-inspo/` (`sunset.jpg`, `stars.jpeg`, and `IMG_9356.jpeg`
  as the basis for the wordmark) and the wordmark traces in `.private/review/`.
- **Products:** the catalog candidates, the placement previews in `.private/review/`, and the
  Gelato unit-economics work.

**Leave:** the Dawn-based theme, transport and chunking, the manifest-part compiler, Shopify reader
delivery, reconciliation, theme-editor QA, and the stage reports.

## Older workspace (`../robot-lantern-OLD`)

The business operations material (finances, catalog, social, brand assets) stays where it is.
`webcomic/brainstorm-001.md` is a future project.

## Old landing page (this repo's `main`)

Nothing carries over.
