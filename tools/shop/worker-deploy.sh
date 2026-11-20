#!/bin/sh
# Deploy the shop's order Worker and give it its keys (docs/SHOP.md, docs/PRODUCTION.md "Secrets").
#
#   tools/shop/worker-deploy.sh            # code only
#   tools/shop/worker-deploy.sh --secrets  # code, then the sandbox keys, the OpenAI key and the proof-link key
#
# Live keys are added at launch, by hand, with `wrangler secret put` (docs/SHOP.md, "Launch").
# SLANT_API_KEY is one of them: without it the Worker can't draft at Slant, even by mistake.
set -eu

secrets=${RL_SECRETS:-$HOME/.codex/secrets/robot-lantern}
root=$(git rev-parse --show-toplevel)

# Read keys as data, not shell code.
val() { sed -n "s/^$2=//p" "$secrets/$1" | head -1; }
CLOUDFLARE_API_TOKEN=$(val cloudflare.env CF_API_TOKEN)
CLOUDFLARE_ACCOUNT_ID=$(val cloudflare.env CF_ACCT_ID)
export CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID

cd "$root/shop-worker"
npx --yes wrangler@4 deploy

if [ "${1:-}" = --secrets ]; then
  put() { [ -n "$2" ] && printf %s "$2" | npx --yes wrangler@4 secret put "$1" >/dev/null && echo "set $1"; }
  put STRIPE_SECRET_KEY_TEST "$(val stripe.env STRIPE_SECRET_KEY_TEST)"
  put STRIPE_WEBHOOK_SECRET_TEST "$(val stripe.env STRIPE_WEBHOOK_SECRET_TEST)"
  put GELATO_API_KEY_TEST "$(val gelato.env GELATO_API_KEY_SANDBOX)"
  put QUEUE_TOKEN_TEST "$(val orders.env ORDERS_QUEUE_TOKEN_TEST)"
  put PROOF_LINK_SECRET "$(val orders.env PROOF_LINK_SECRET)"
  put OPENAI_API_KEY "$(val openai.env OPENAI_API_KEY)"
fi
