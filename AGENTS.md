# Working in this repo

Read [README.md](README.md) for direction and [NOW.md](NOW.md) for current state before starting.

## Rules

1. **One bounded task per session.** The task comes from NOW.md or from RJ directly, and it has a
   done-condition. When it's done or blocked, stop and report. Don't go looking for adjacent work.
2. **The repo is the handoff.** Before a session ends, update NOW.md with what changed, what's
   next and what's blocked. Commit small and often. Anything that must outlive the session
   belongs in the repo, not in the chat thread.
3. **Stay inside the current task.** Ideas outside it go under "Parked" in NOW.md, not into code.
4. **Boundaries:**
   - **Never incur a charge without RJ's go-ahead.** That includes orders, samples, paid apps,
     plan changes and paid API tiers. Working in Shopify, Gelato and other services is expected.
     [docs/CHARGES.md](docs/CHARGES.md) lists which actions cost money. If an action isn't listed
     there, find out and add it before doing it.
   - **Don't route around a block.** If RJ has declined a permission or a command, or a
     credential is missing, stop and ask. Don't use browser automation, computer use or
     screenshots as a workaround. Those tools are fine when they're the right tool for the job.
   - **robotlantern.com DNS isn't on Porkbun.** RJ changes it by hand at the registrar's DNS host.
     Prepare the exact records and hand them over.
   - **Pushing `main` deploys the live site.** Ask first. Pushing to the `samwise` remote is
     free: that's the preview ([docs/PREVIEW.md](docs/PREVIEW.md)).
5. **Keep it plain.** Content lives in Markdown and JSON files. Don't add compilers, adapters,
   transport layers or portability abstractions until there's a concrete second use for one.
6. **Keep docs short.** README, AGENTS and NOW, plus `docs/` for anything that must outlive a
   task. No stage reports or resume checkpoints.
7. **Nothing private in Git.** No credentials, account IDs, local absolute paths, private source
   captures or unreviewed conversation text. Private working material goes in `.private/`, which
   is gitignored. This repo is public.
   Before launch, a privacy pass covers everything public. The aim is "don't make it any worse":
   nothing that narrows RJ's location or identity beyond what's already public. RJ has cleared
   Fairmont, WV, Bogotá and the machines' names for publication (2026-09-27).

## Branches

- `main` is what's live at robotlantern.com. Until cutover, it's the old static landing page,
  served by GitHub Pages from the branch root.
- `rebuild` holds the new site until the first launch. Nothing from the old landing page carries
  over. It lives on Sarcean and Samwise, not GitHub, and pushing it to `samwise` updates the
  preview.

## Stack

- Astro with static output, adopted 2026-09-23 (see [docs/FRAMEWORK.md](docs/FRAMEWORK.md)).
  Content goes under `src/content/`, with schemas in the content config.
- Plain `<script>` tags for interactivity. No UI framework until a page actually needs one.
- Node version pinned in `.node-version`.
