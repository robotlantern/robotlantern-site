# Previews on Samwise

Status: adopted and set up 2026-09-25.

| Repo | Preview branch | URL |
|---|---|---|
| this repo | `rebuild` | https://rl.rblt.io/ |
| `unprojection-astra` | `main` | https://sky-astra.rblt.io/ |
| `unprojection-opus` | `main` | https://sky-opus.rblt.io/ |

The infrastructure is the `static-preview` stack in `~/work/services`, whose README covers
adding a site.

## Policy

Work is built on Sarcean and previewed on Samwise, where RJ can test it on his phone over
trusted HTTPS. GitHub carries only what's public: `main` of this repo, which is the live site.
The sibling visualization repos (`unprojection-astra`, `unprojection-opus`) stay off GitHub
until RJ decides to publish them.

- Pushing to the `samwise` remote needs no permission. Pushing to GitHub does.
- Samwise holds each repo as a bare repo at `/srv/git/<repo>.git`, like the other Samwise
  projects.

## How a preview works

1. Push the preview branch to `samwise`. Here that's `rebuild`; in the siblings it's `main`.
2. Samwise builds that commit. If `package.json` has a `build` script, the build runs in a
   Node container and `dist/` is served. Otherwise the committed files are served as they are.
3. The push output shows the build log and the preview URL. A failed build leaves the last
   good preview up.
4. Previews are served with `Cache-Control: no-cache`, so a reload on the phone always shows
   the latest push.

Preview names are reachable only on the LAN or over the VPN. Split-horizon DNS points them at
Samwise, and public DNS for them fails closed at `192.0.2.1`. The first build of a new Node
version pulls its image, so it's slower.

## Live reload

A dev server isn't part of the preview. For a tight loop, such as tuning an animation, run
the dev server on Sarcean with `--host` and open it from the phone at Sarcean's LAN address.
Push to `samwise` to check the real build.
