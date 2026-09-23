# Now

_Last updated 2026-09-23._

## Tasks

Each task fits in one sitting or can stop cleanly partway. Pick any task that isn't blocked.

1. **Charges reference.** Needed before Shopify rebills on 2026-10-02.
   - Start: Shopify's and Gelato's own help docs.
     `../robot-lantern-shopify/docs/INTEGRATIONS.md` has partial notes.
   - Do: write `docs/CHARGES.md`, listing every action that costs money on Shopify and Gelato,
     with sources. Include what still works if Shopify is paused or downgraded: Storefront API,
     test checkout, draft products, the Gelato app.
   - Done when RJ can decide from that doc alone whether to keep, pause or downgrade Shopify.
2. **Framework sign-off (RJ).** Read `docs/FRAMEWORK.md` and decide. Done when the "Stack"
   section in AGENTS.md names the framework.
3. **Attribution fix.**
   - Start: `.private/analysis/README.md`, then the prototype's `tools/wording.py`.
   - Do:
     - Attribute through the revision chain instead of matching every draft independently.
     - Keep the original author's color on copyedits (case, punctuation, possessives, spelling),
       marking them with their own subtle style and count.
     - Report the essay body and the footnotes separately in the footer.
   - Done when the top of the essay has no copyedit confetti and RJ has spot-checked the numbers.
4. **Sunset scroll prototype.**
   - Start: `sunset.jpg`, `stars.jpeg` and `IMG_9356.jpeg` (the wordmark) in the prototype's
     `site-design-inspo/`.
   - Do: build a standalone page. Scrolling moves from sunset to night, stars appear, and the
     lantern brightens with them.
   - Done when RJ says it matches the vision. It doesn't depend on the framework, so it can start
     now.
5. **Scaffold and port** (after task 2).
   - Do: set up the site on `rebuild`. Port the prototype's essay and conversation designs as they
     are, and leave a home page slot for task 4.
   - Done when an essay and a conversation render locally from files in this repo.
6. **Launch conversation.**
   - RJ picks a text chat; voice transcripts read poorly.
   - Do: capture it privately, then select the published range with RJ.
   - Done when RJ has approved the public text.
7. **First products** (after task 1).
   - Start: the prototype's catalog candidates and placement previews.
   - Do: RJ picks 2 to 4 designs. Create the Gelato products and linked Shopify drafts, and build a
     shop page that hands off to Shopify checkout.
   - Done when a test checkout completes without a real charge.
8. **Cutover.** Choose the host, switch Pages to deploy through Actions, and merge to `main`. RJ
   changes DNS if needed.

## Open decisions (RJ)

- Framework (task 2).
- Copyedit rule (task 3): do edits of one or two words inside a sentence count as editing or as
  authorship? On the essay body, that decides between 92% and 96% RJ.
- Shopify on 2026-10-02: keep, pause or downgrade. Task 1 informs this.
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
