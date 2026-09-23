# Now

_Last updated 2026-09-23._

## Tasks

Each task fits in one sitting or can stop cleanly partway. Pick any task that isn't blocked.

1. **Pause Shopify (RJ), by 2026-09-30.** Do it in Settings > Plan unless the shop is built by
   then. The next bill is 2026-10-01. See [docs/CHARGES.md](docs/CHARGES.md).
2. **Framework sign-off (RJ).** Done 2026-09-23: Astro.
3. **Attribution tool.**
   - Start: `.private/analysis/README.md` (findings and a working revision-chain counterfactual),
     then the prototype's `tools/wording.py`.
   - Do: build one tool whose input is an ordered list of versions, each with an author. It has
     two sources:
     - An article's Git history, following [docs/WRITING.md](docs/WRITING.md). This is the main
       path.
     - The first essay's drafts, taken from its writing chat.
   - Attribute through the version chain (word-level blame). Copyedits keep the original author's
     color and get their own subtle mark and count. The footer reports the body and the footnotes
     separately.
   - Done when both sources produce attribution JSON, the top of the first essay has no copyedit
     confetti, and RJ has spot-checked the numbers.
4. **Sunset scroll prototype.**
   - Start: `sunset.jpg`, `stars.jpeg` and `IMG_9356.jpeg` (the wordmark) in the prototype's
     `site-design-inspo/`.
   - Do: build a standalone page. Scrolling moves from sunset to night, stars appear, and the
     lantern brightens with them.
   - Approach: paint the sky and stars as one tall CSS background, which works in every browser.
     A script of under 1 KB sets a single `--progress` value (0 at the top, 1 at the bottom), and
     CSS drives the lantern glow, star twinkle and color depth from it. Turn off the twinkle when
     the visitor's device is set to reduce motion.
   - Done when RJ says it matches the vision. It doesn't depend on the framework, so it can start
     now.
5. **Scaffold and port** (after task 2).
   - Do: set up Astro on `rebuild`. Port the layout and behavior of the prototype's essay and
     conversation pages, restyled with the night-sky palette (see README, "Look"). Leave a home
     page slot for task 4.
   - Done when an essay and a conversation render locally from files in this repo.
6. **Launch conversation.**
   - RJ picks a text chat; voice transcripts read poorly.
   - Do: capture it privately, then select the published range with RJ.
   - Done when RJ has approved the public text.
7. **First products** (after task 1).
   - Start: the prototype's catalog candidates and placement previews.
   - Do: RJ picks 2 to 4 designs. Create the Gelato products and linked Shopify drafts, and build a
     shop page that hands off to Shopify checkout.
   - Done when a test checkout completes without a real charge. Follow "Test checkout without a
     real charge" in docs/CHARGES.md. Gelato imports paid test orders by default.
8. **Cutover.** Choose the host, switch Pages to deploy through Actions, and merge to `main`. RJ
   changes DNS if needed.

## Open decisions (RJ)

- Copyedit rule (task 3): do edits of one or two words inside a sentence count as editing or as
  authorship? On the essay body, that decides between 92% and 96% RJ.
- Hosting at cutover: GitHub Pages or Cloudflare Pages.

## Parked

- Nothing yet.

## Log

- 2026-09-23: Fresh start. Cloned the live site repo and created the `rebuild` branch.
- 2026-09-23: Enforced HTTPS on robotlantern.com. Its DNS is at `hosting.businessidentity.llc`
  (registrar DomainRegistry.com), not Porkbun.
- 2026-09-23: Reviewed the Codex prototype. The essay design is close to final. Attribution looks
  GPT-heavy for three reasons:
  - The footer blends the essay body (92% RJ) with the footnotes (88% GPT), which are half the
    post's characters, so the whole post reads 52% / 48%.
  - Copyedits are painted as authorship across RJ's sentences.
  - The matcher lets GPT's first draft claim spaces and common words in text RJ wrote later.
- 2026-09-23: Wrote docs/CHARGES.md (task 1). Shopify no longer offers Starter to new stores, so
  the real choice is keeping Basic or pausing. Gelato's default instant approval means a Shopify
  test order for a Gelato product can be produced and charged.
- 2026-09-23: RJ decided to pause Shopify before the next bill unless the shop is built. The billing
  history shows bills every 30 days (last one 2026-09-01), so the next is 2026-10-01, not 10-02.
- 2026-09-23: RJ signed off on Astro (task 2). The site's overall look is the night sky, replacing
  the prototype's light cream. Task 3 was reframed: attribution comes from Git history for new
  articles, and the first essay's chat drafts are a second input to the same tool.
