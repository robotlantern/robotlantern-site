#!/bin/sh
# Build the committed tip of a branch and deploy it to Cloudflare (docs/HOSTING.md).
#
#   tools/site-deploy.sh            # rebuild, until cutover
#   tools/site-deploy.sh <branch>
#
# Builds from `git archive`, so uncommitted files and .DS_Store never ship.
set -eu

ref=${1:-rebuild}
secrets=${RL_SECRETS:-$HOME/.codex/secrets/robot-lantern}
root=$(git rev-parse --show-toplevel)

# Read the token as data, not shell code.
val() { sed -n "s/^$1=//p" "$secrets/cloudflare.env" | head -1; }
CLOUDFLARE_API_TOKEN=$(val CF_API_TOKEN)
CLOUDFLARE_ACCOUNT_ID=$(val CF_ACCT_ID)
export CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
git -C "$root" archive "$ref" | tar -x -C "$work"
ln -s "$root/node_modules" "$work/node_modules"
cd "$work"
npm run build --silent
npx --yes wrangler@4 deploy --message "$ref $(git -C "$root" rev-parse --short "$ref")"
