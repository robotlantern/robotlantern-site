# Framework proposal: Astro

Status: adopted 2026-09-23.

## What Astro is

A build tool for websites that are mostly content. You write page templates, and Astro turns
them and your content files into plain HTML and CSS at build time. The published site is static
files. No server runs, and there's nothing for Astro to do once the site is built.

By default, pages ship no JavaScript. When a page needs some, such as the sunset scroll, a 3D
model or a cart button, you mark that component as interactive. Only that component's script is
sent, and only on that page. Astro calls these "islands." The script can be plain JavaScript,
Three.js, React or anything else.

## What "content collections" means

A collection is a folder of files plus a schema that says what each file must contain. For
example:

- `essays/cogito-ergo-so-what/` holds the final text, the original draft and the generated
  attribution data. The schema requires a title, contributors and an attribution file.
- `conversations/<slug>/` holds a transcript excerpt as `conversation.md`, plus its images. The
  schema requires a title, a date and participants (see [CONVERSATIONS.md](CONVERSATIONS.md)).
- `products/<slug>.md` holds a product's story, images, price, Gelato product UID and Stripe
  Payment Link.

At build time, Astro loads the files, checks them against the schema, and stops with a clear
error if something is missing or malformed. Templates then get the data already typed and
validated.

**The content model is yours, not Astro's.** You decide what an essay is. The schema is just
where that definition is written down and enforced. The files themselves are ordinary Markdown
and JSON with no Astro-specific syntax, so if Astro were dropped later, the content would stay
and only the templates and schema declarations would need rewriting.

## How the pieces map

| Piece | In Astro | Outside Astro |
| --- | --- | --- |
| Essay page, with contribution highlighting | A template that reads the essay's files | The attribution tool, a script that runs before the build and writes JSON |
| Conversation page | A template plus CSS | The capture and selection of the transcript |
| Home sunset scroll | One page with its own script | — |
| Shop | Product pages from the products collection, each linking to Stripe checkout | Stripe (checkout), a Cloudflare Worker (paid order to Gelato) and Gelato (fulfillment) |
| Interactive projects | An island on that project's page | — |

The attribution logic, which matters most, doesn't depend on the framework at all. It's a
separate script, and Astro only displays its output.

## Costs and risks

- Templates use Astro's own `.astro` syntax: HTML with a small script block at the top. That's
  the only part tied to Astro.
- Astro releases a major version about once a year. Upgrades have usually been modest, but they
  are real work.
- Astro has no admin screen or CMS. You edit files, which is consistent with Git as the source of
  truth.

## Alternatives

- **Eleventy (11ty):** simpler and older, with no built-in schemas and weaker support for
  interactive islands.
- **Hand-rolled TypeScript build:** what Codex wrote. You get full control, but you maintain the
  page generation, dev server and asset handling yourself.
- **Next.js or SvelteKit:** application frameworks, heavier than a mostly static site needs.

## Recommendation

Astro. Schema-checked content and per-page islands fit this site closely, and the parts that
make Robot Lantern distinctive (attribution, transcript handling, products) stay in plain files
and ordinary scripts that don't depend on it.
