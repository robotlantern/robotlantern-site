# Production

How orders run once the site is live (NOW.md, decisions 16–24). Production runs in Claude cloud environments,
so Sarcean can sleep. This page covers what runs where, what each part may touch, and how RJ stays in the
loop. The order flow and its contracts are in [ORDERS.md](ORDERS.md).

Written 2026-11-19, before any of it was built. Steps 7–16 build it, and step 15 corrects anything here that the
cloud turns out to do differently. Claude's scheduled routines are a research preview, so their limits can
change.

## What runs where

| Part | Where | Does | Keeps |
| --- | --- | --- | --- |
| The page | the customer's browser | photo, crop, preview, choices | nothing, and loads nothing from other sites |
| Order Worker `shop` | Cloudflare, free plan | drawings (OpenAI), orders, checkout (Stripe), webhook, queue, Slant drafts | KV: photos, drawings, orders; its secrets |
| OpenAI | API project "Robot Lantern shop" | draws the stencil | inputs and outputs up to 30 days, per its policy |
| Stripe | live account | payment, tax, receipts | name, email, address, card |
| `rl-orders` | Claude cloud, `rl-production`, hourly 7:00–23:00 | builds, checks, uploads to Slant, asks for the draft, emails RJ | nothing after the run |
| `rl-daily` | Claude cloud, `rl-production`, 8:00 daily | shipping status, purges, summary | nothing after the run |
| Slant 3D | its API and dashboard | prints and ships | the STLs, name and address |
| RJ | email, Slant, Stripe | processes each draft, answers "Needs you", refunds | — |
| Sarcean | | building and testing; the manual fallback | the secrets folder, the master copy of every key |

## Secrets

The master copies are in `~/.codex/secrets/robot-lantern/` on Sarcean. They never go in Git, chat, or an
environment variable that other people can read.

| Secret | File | Worker secret | `rl-production` |
| --- | --- | --- | --- |
| OpenAI key | `openai.env` `OPENAI_API_KEY` | `OPENAI_API_KEY` | — |
| Stripe, the Worker's live key | `stripe.env` `STRIPE_SECRET_KEY_LIVE_WORKER` | `STRIPE_SECRET_KEY_LIVE` | — |
| Stripe live webhook secret | `stripe.env` `STRIPE_WEBHOOK_SECRET_LIVE` | `STRIPE_WEBHOOK_SECRET_LIVE` | — |
| Slant key | `slant.env` `SLANT_API_KEY` | `SLANT_API_KEY` (drafts) | network secret for `slant3dapi.com` |
| Queue tokens | `orders.env` `ORDERS_QUEUE_TOKEN_LIVE` / `_TEST` | `QUEUE_TOKEN_LIVE` / `_TEST` | network secrets for `robotlantern.com` / `shop.robotlantern.workers.dev` |
| Proof-link key | `orders.env` `PROOF_LINK_SECRET` (made 2026-11-20) | `PROOF_LINK_SECRET` | — |

Agents load Worker secrets from these files with `wrangler secret put`, never by pasting them anywhere. RJ
pastes the cloud's network secrets himself (NOW.md step 5). A network secret is added by the cloud's proxy to
requests for its host, so the key never enters the machine the routine runs on. That's why the tools
send no `Authorization` header when no key is set in their environment.

## Cloud environments

Created by RJ at claude.ai/code (NOW.md step 5). Both use the repository `robotlantern/robotlantern-site`.

### `rl-production`, for the order routines only

- **Network:** Limited, with "Allow package managers" on, plus these hosts:
  - `slant3dapi.com`
  - `slant-gatekeeper.s3.us-west-2.amazonaws.com`, the host in Slant's presigned upload links (seen 2026-11-19).
    The upload's PUT carries its own signature, so it gets no network secret.
  - `robotlantern.com`
  - `shop.robotlantern.workers.dev`
- **Network secrets** (the settings dialog names each by its host and header only; there's no variable name):
  - `SLANT_API_KEY` → `slant3dapi.com`, as `Authorization: Bearer`.
  - `ORDERS_QUEUE_TOKEN_LIVE` → `robotlantern.com`, as `Authorization: Bearer`.
  - `ORDERS_QUEUE_TOKEN_TEST` → `shop.robotlantern.workers.dev`, as `Authorization: Bearer`.
- **Environment variables:** `SLANT_PLATFORM_ID` (from `slant.env`). Nothing else.
- **Connectors:** none on the environment. Each routine is created with an empty connector list, and RJ adds
  Gmail to it at claude.ai/code/routines (the agent's session can't see the account's connector IDs).
- **Setup script:**

  ```bash
  #!/bin/bash
  set -e
  UV=$(command -v uv || echo /root/.local/bin/uv)
  "$UV" python install 3.13
  "$UV" venv --python 3.13 /opt/rl
  "$UV" pip install --python /opt/rl/bin/python numpy==2.5.3 opencv-python-headless==5.0.0.93 pillow==12.3.0 \
    scipy==1.18.1 shapely==2.1.2 manifold3d==3.5.4 trimesh==5.1.1 fonttools==4.66.1
  ```

  These are the versions the builder runs on Sarcean. The cloud image's default `python3` is 3.11, too old for
  numpy 2.5, so the script uses `uv` (preinstalled) with Python 3.13. A probe in `rl-dev` (2026-11-22) installed
  all eight at these versions in about 5 seconds.

### `rl-dev`, for agents building things while RJ does something else

- **Network:** Limited, with "Allow package managers" on. No other hosts.
- **Secrets, variables, connectors:** none.
- Work goes on `claude/*` branches, and a session on Sarcean merges what RJ wants.

## Routines

Created in step 15 (2026-11-22) with the `RemoteTrigger` API, and managed at claude.ai/code/routines. Each is a
fresh cloud session in `rl-production` with a checkout of `robotlantern/robotlantern-site` (`main`, the default
branch), on Sonnet 5.5. Their prompts stay short and point here, so changing a run is a commit, not a routine
edit.

- **Schedules are cron in UTC**, at most hourly. `rl-orders` is `0 0-4,12-23 * * *` and `rl-daily` is
  `0 13 * * *`: 7:00–23:00 and 8:00 Eastern in winter, an hour later in summer. Not worth adjusting twice a year.
- **Email goes through the Gmail connector to `orders@robotlantern.com`**, and to no one else. It's an alias of
  RJ's mailbox ([EMAIL.md](EMAIL.md)), named in both routine prompts.
- **Debugging:** each routine's runs and condensed logs are readable through `RemoteTrigger` (`list_runs`,
  `get_run_log`). Only RJ can delete a routine, at claude.ai/code/routines.

### `rl-orders`: hourly, 7:00–23:00 Eastern

> In robotlantern-site, check out `main`, read docs/PRODUCTION.md, and do "The orders run" for live orders.
> Keep to its limits exactly.

**The orders run:**

1. Run `/opt/rl/bin/python tools/orders/run.py status --live`. If it says there's nothing to do, stop. Most
   runs end here.
2. For each `paid` order: `run.py build <id>`. This downloads the order to a temporary folder, runs
   `tools/ornament/make.py` on each design's folder, stores each `out/` with the order, and moves it to `built`, or to `needs-rj` with the
   failed check.
3. For each design, look at `proof.png` next to its `preview.jpg`. Check that it's the same subject and the same colours, the tag
   text is right, and nothing is missing, broken or new. If not, run `run.py flag <id> "<what's wrong>"` and
   go on to the next order.
4. `run.py slant <id>`: uploads every design's two STLs, quotes them, and asks the Worker for the draft. The order moves to
   `drafted`.
5. Email RJ, one email per order (below). `run.py email <id>` prints it, with the signed proof links.

`run.py` has `status`, `build`, `flag`, `slant` and `email` (step 14), and `track` and `purge` for the daily run
(step 15). `track` reads Slant's order (`DRAFT`, `SUBMITTED`, `PRINTING`, `SHIPPED`, `CANCELLED`) and only moves
our record; it prints the newly shipped order IDs for step 2 of the daily run.

**Never:** process, cancel or edit a Slant order; refund; email a customer; change a cap or a switch;
make a new drawing; or put anything from an order into Git, a log or an email body. Order IDs and the signed
proof link are fine.

### `rl-daily`: 8:00 Eastern

> In robotlantern-site, check out `main`, read docs/PRODUCTION.md, and do "The daily run". Keep to its limits
> exactly.

**The daily run:**

1. `run.py track --live`: reads Slant's status for `drafted` and `processed` orders, and records `processed`,
   `shipped` and the tracking number.
2. For each newly shipped order: get the name and email from `/api/orders/<id>/contact`, and create a Gmail
   draft (not a sent email) to the customer with the tracking link. Use the template in
   `tools/orders/templates/shipped.md`, which step 11 writes.
3. `run.py purge --due --live`: deletes the photos 60 days after shipping (`POST /api/purge`). The Worker's
   daily cron does the same, so this is a second chance, not the only one.
4. Read `GET /api/stats`. If anything is stuck, flagged, near a cap, or the OpenAI balance looks low, email RJ
   a summary. Otherwise send nothing.

## Keeping RJ in the loop

All mail goes to RJ only, at `orders@`, and never to customers. RJ sends the customer drafts himself until he says
otherwise.

| When | From | Subject |
| --- | --- | --- |
| Someone pays | Stripe | Stripe's own payment email |
| An order is drafted at Slant | `rl-orders` | `Ready for Slant: order <id> ($<printing> + $<shipping>)`, with the signed proof link and Slant's dashboard link |
| An order needs RJ | `rl-orders`, `rl-daily` | `Needs you: order <id>`, with what's wrong and what the agent suggests |
| Something changed overnight | `rl-daily` | `Robot Lantern daily: …`, only when there's something to say |

RJ's part:
- **Process each "Ready for Slant" draft in Slant's dashboard.** A glance at the proof is optional.
- **Answer "Needs you".** Usually it means emailing the customer from help@ to offer a fresh drawing or a full
  refund (decision 4).
- **Refund in Stripe** when one is due.

## Caps and switches

| Guard | Where | Setting |
| --- | --- | --- |
| The OpenAI balance | OpenAI billing | prepaid, auto-recharge off (decision 21): the hard cap |
| Tries per photo | `shop.json` `drawing.triesPerPhoto` | 3 |
| Drawings per visitor per day | `shop-worker/limits.json` | 24 (enough for `maxDesigns` 12 with one retry each) |
| Estimated spend per day | `shop-worker/limits.json` | $10 |
| Orders per week | `shop.json` `weeklyCap` | 25 |
| Drawings or orders off | KV `switch:drawings`, `switch:orders` | `python3 tools/orders/switch.py drawings off --live` (on Sarcean: it needs the Cloudflare token) |
| Slant | Slant's dashboard | nothing is charged until RJ processes a draft |

Raising a cap, buying credit or turning auto-recharge on is RJ's call. Agents switch drawings off on their own
only if spending looks wrong, and they tell RJ straight away.

## When something goes wrong

- **The build fails, or the proof doesn't match the preview:** the order goes to `needs-rj`. RJ emails the
  customer to offer a fresh drawing from the same photo or a full refund. An agent makes the fresh drawing
  only when RJ asks.
- **OpenAI errors, or a cap is hit:** the page asks the customer to try later. Nothing is charged, and no try
  is used up.
- **Slant's API is down:** the next run tries again. After a day, the order goes to `needs-rj`.
- **A Slant colour is gone:** `run.py slant` refuses and flags the order. The product file's colours are
  updated, and RJ asks the customer to choose again or refunds.
- **Lost or broken in the post:** RJ chooses a remake (a new draft from the same files, which agents can make
  on his say) or a refund.
- **A routine is broken or the cloud is down:** do the same runs by hand (below).

## By hand, from Sarcean

The same scripts run in a session here, with the keys from the secrets folder. Open a session in this repo and
say: "Read docs/PRODUCTION.md and do the orders run, live." That's the fallback whenever the cloud can't do it,
and it's how step 14 tests the run before the routines exist.
