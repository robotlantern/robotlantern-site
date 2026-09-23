# Robot Lantern

The website, publishing system and shop behind [robotlantern.com](https://robotlantern.com). It's
the base for Robot Lantern's creative and product work.

## What gets published

- **Essays.** Each essay is a product in its own right: the finished piece plus the record of how
  it was written. Readers can switch on contribution highlighting to see who wrote which words,
  open "Inside this post" to read the full editing conversation and drafts, or read the exact
  Markdown. The attribution count is part of the appeal, so it has to be right.
- **Conversations.** A selected section of a real transcript, styled as a conversation. Each one
  stands alone and has its own reading design. A conversation may link to an essay but doesn't
  have to.
- **Products.** Print-on-demand items made from Robot Lantern brand art. Gelato fulfills them and
  Shopify handles checkout.
- **Home.** A scroll from sunset into night. The top of the page uses the warm oranges of the
  reference sunset photo. As you scroll down, the sky darkens, stars appear, and the robot lantern
  grows brighter along with them.

Later: interactive project pages (such as the Celebration Clock), the webcomic, and custom
children's books.

## Look

The night sky, across the whole site: deep blues and near-black, starlight, and the warm orange
of the lantern and the sunset used as accent. The home page is the one place that starts at
sunset and scrolls into night. Every other page lives in the night.

## Shape

- **Git is the source of truth.** Content, code, assets and schemas live here. To publish, build
  and push.
- **Content lives in plain files.** Markdown and JSON in this repo, in a structure Robot Lantern
  defines. The site framework reads them. See [docs/FRAMEWORK.md](docs/FRAMEWORK.md).
- **Static first.** Pages build to plain HTML. A page that needs interactivity loads its own
  script, and other pages don't load it.
- **Commerce is a subsystem.** Shopify handles products, cart, checkout and orders, and Gelato
  fulfills them. The site shows products in its own design and hands off to Shopify's checkout.
  Shopify doesn't shape the site.
- **Backends only where reality requires them.** The first launch needs none.

The previous attempt made Shopify the platform. Conversations and provenance had to squeeze into
Shopify's blog and metafield model, and most of the engineering went into working around that.
Its designs for the essay and conversation pages are close to final and are being carried over.
Its Shopify plumbing is not.

## First launch

A home page, one essay, one conversation, and a shop with a few products. The work is broken into
tasks in [NOW.md](NOW.md). Each task says where to start and when it's done.

## Hosting

GitHub Pages currently serves robotlantern.com. Decide at cutover whether to stay there or move
to Cloudflare Pages: commerce is in the first launch, and GitHub Pages' terms don't cover sites
built mainly for commercial transactions. The build output is static either way, so switching
hosts means changing the deploy step, not the site.

See [AGENTS.md](AGENTS.md) for how work happens here.
