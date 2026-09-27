# Robot Lantern

The website, publishing system and shop behind [robotlantern.com](https://robotlantern.com). It's
the base for Robot Lantern's creative and product work.

## What gets published

The sections are **Thoughts**, **Chats**, **Builds** and **Shop**. In code and docs they're
essays, conversations, interactives and products.

- **Thoughts (essays).** Each essay shows who wrote it: an attribution block with percentages under
  the title, and one toggle that highlights who wrote which words. The attribution count is part
  of the appeal, so it has to be right. The editing chat behind an essay isn't published with it.
  If a chat that led to an essay is interesting in its own right, it's published separately as a
  chat and the two are cross-linked.
- **Chats (conversations).** A selected section of a real transcript that's interesting in its
  own right (star talk, not copyediting). Each one stands alone and reads like a chat app. A chat
  may link to an essay but doesn't have to.
- **Builds (interactives).** Things you can use in the browser, each running full screen, such
  as The Sky, Unprojected.
- **Products.** Print-on-demand items made from Robot Lantern brand art. Gelato fulfills them and
  Shopify handles checkout.
- **Home.** A scroll from sunset into night. The top of the page uses the warm oranges of the
  reference sunset photo. As you scroll down, the sky darkens, stars appear, and the robot lantern
  grows brighter along with them.

Later: the webcomic and custom children's books.

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

GitHub Pages serves the old robotlantern.com until cutover. The new site moves to Cloudflare
(decided 2026-09-27): commerce is in the first launch, and GitHub Pages' terms don't cover sites
built mainly for commercial transactions. Cutover moves the domain's nameservers to Cloudflare
(NOW.md, task 9). The build output is static, so the host only changes the deploy step.

See [AGENTS.md](AGENTS.md) for how work happens here.
