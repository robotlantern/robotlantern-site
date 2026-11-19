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
- **Products.** First, things made from a customer's photo. The launch product is a two-part stencil ornament
  of a pet, drawn from the customer's photo and printed and shipped by Slant 3D. A lithophane ornament and
  lamp, custom cutouts, pop-out photos and a stereographic projector come later. The customer shapes theirs
  on the product's page and pays through Stripe. A Claude routine in the cloud builds and checks the print
  files, and RJ approves each order at Slant ([docs/ORDERS.md](docs/ORDERS.md),
  [docs/PRODUCTION.md](docs/PRODUCTION.md)).
  Print-on-demand items from Robot Lantern's own art come later, with Stripe taking payment and Gelato
  printing and shipping ([docs/SHOP.md](docs/SHOP.md)). Ideas move through the pipeline in
  [docs/PRODUCTS.md](docs/PRODUCTS.md).
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
- **Commerce is a subsystem.** Products are files in this repo. The site shows them in its own
  design and hands off to Stripe's hosted checkout. A small Cloudflare Worker keeps each photo
  order's files, asks OpenAI's image API for the customer's drawing (capped), drafts Slant orders, and
  passes printed merch to Gelato. The preview runs in the browser. Print files are made by scheduled
  Claude routines in the cloud, so nothing waits on RJ's machines. There's no monthly platform fee.
- **Backends only where reality requires them.** The first launch needs two: the order Worker and the
  cloud routines ([docs/PRODUCTION.md](docs/PRODUCTION.md)).

The previous attempt made Shopify the platform. Conversations and provenance had to squeeze into
Shopify's blog and metafield model, and most of the engineering went into working around that.
Its designs for the essay and conversation pages are close to final and are being carried over.
Its Shopify plumbing is not.

## First launch

A home page, an essay, two chats, a build, and a shop with one product, the stencil ornament, working end to
end. The other photo product lines open as their prototypes pass. The work is broken into steps in [NOW.md](NOW.md). Each step
says what it waits for, and NOW.md says how to start one.

## Hosting

GitHub Pages serves the old robotlantern.com until cutover. The new site moves to Cloudflare
(decided 2026-09-27): commerce is in the first launch, and GitHub Pages' terms don't cover sites
built mainly for commercial transactions. Cutover moves the domain's nameservers to Cloudflare
(NOW.md, steps 2, 12 and 13). The build output is static, so the host only changes the deploy step.

See [AGENTS.md](AGENTS.md) for how work happens here.
