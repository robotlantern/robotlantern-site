# Hosting on Cloudflare

Set up 2026-10-01 ([LOG.md](LOG.md), task 9). Until cutover, robotlantern.com is still the old landing
page on GitHub Pages; the new site runs on Cloudflare at a workers.dev address for checking.

## The site

- **What it is:** a Cloudflare Worker named `site` with static assets only (`wrangler.jsonc` at the
  repo root). No code runs on a page view, so the privacy page's claims hold. Cloudflare now
  creates new "Pages" projects as Workers like this one, so it's the same free product.
- **Where:** https://site.robotlantern.workers.dev (the account's workers.dev subdomain is
  `robotlantern`). It sends `X-Robots-Tag: noindex` (`public/_headers`), so search engines skip
  it. The header names only that host, so robotlantern.com won't get it.
- **Deploy:** `tools/site-deploy.sh` builds the committed tip of `rebuild` from `git archive`
  (uncommitted files and `.DS_Store` never ship) and deploys it. Free (docs/CHARGES.md).
- **Not found** pages use `404.html`; `/about` redirects to `/about/`.
- **Don't run `wrangler` from the repo root without a config.** Its auto-setup rewrote
  `package.json`, `astro.config.mjs` and `tsconfig.json` for an Astro adapter on 2026-10-01
  (reverted). With `wrangler.jsonc` in place it no longer does.

## Cutover

1. RJ adds robotlantern.com to Cloudflare (free plan). The dashboard scans the old DNS host
   and suggests records. Check them against the list below before anything else.
2. Enter or correct every record below, then add the site: in the `site` Worker, Settings →
   Domains & Routes → add custom domains `robotlantern.com` and `www.robotlantern.com`. That
   replaces the GitHub Pages records (the four `A` records and the `www` CNAME), which are
   removed. Equivalent in `wrangler.jsonc`: `"routes": [{ "pattern": "robotlantern.com",
   "custom_domain": true }, …]`. Then route `robotlantern.com/api/*` to the `shop` Worker, for photo
   orders ([ORDERS.md](ORDERS.md)).
3. RJ switches the nameservers at DomainRegistry.com. Mail must keep working throughout: the
   MX and DKIM records are copied first.
4. Afterwards: remove the `CNAME` file, and the GitHub Pages site in the repo's settings.

## DNS records for robotlantern.com

Read from the current DNS host (`ns1.hosting.businessidentity.llc`) on 2026-10-01. It refuses
zone transfers, so these come from asking for each common name one by one. A record under an
unusual name would be missed: compare with the DNS host's own list when RJ is signed in there.

| Name | Type | Value | TTL | Purpose |
| --- | --- | --- | --- | --- |
| `@` | A | 185.199.108.153 | 60 | GitHub Pages (old site). **Drop at cutover** |
| `@` | A | 185.199.109.153 | 60 | GitHub Pages. **Drop** |
| `@` | A | 185.199.110.153 | 60 | GitHub Pages. **Drop** |
| `@` | A | 185.199.111.153 | 60 | GitHub Pages. **Drop** |
| `www` | CNAME | robotlantern.github.io | 60 | GitHub Pages. **Drop** (the Worker's custom domain replaces it) |
| `@` | MX | 1 ASPMX.L.GOOGLE.COM | 60 | Google Workspace mail. **Keep** |
| `@` | MX | 5 ALT1.ASPMX.L.GOOGLE.COM | 60 | Google Workspace mail. **Keep** |
| `@` | MX | 5 ALT2.ASPMX.L.GOOGLE.COM | 60 | Google Workspace mail. **Keep** |
| `@` | MX | 10 ALT3.ASPMX.L.GOOGLE.COM | 60 | Google Workspace mail. **Keep** |
| `@` | MX | 10 ALT4.ASPMX.L.GOOGLE.COM | 60 | Google Workspace mail. **Keep** |
| `google._domainkey` | TXT | `v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAifQrXTggiJLfON+r4537EfE3qZ35dNm5pbxwUJMJMeEiQ6hsxJtcwdmqTA+6dwXhNvt9o/8PT6u89/ZJMq74a0ajJvJI6FbARLbQAoMq3nN2dOW5AErs9a5OlJA5LMDjFe9nCWrZ4HsS9V3EwxQag2XNufVWLJma8h4mrQkTLthiOlPNL0ADQBoEtKE5jnYRdcY5Uf+zAjYt4iD2yJwkI40s6vPA12XmO3f/qfrNmKH3pa9jakL9Sf5+qFWNCv/Qa1IDmLzYUxQyXPUrsDsyFt3B8vrEs+Ds0K52WkwqN+AorAUtfUV06QvYwbc08HkraKKu/Q9VLmu3vzhjjC3vjQIDAQAB` | 300 | Google Workspace DKIM (stored as two strings; enter as one value). **Keep** |
| `@` | TXT | `google-site-verification=qI_g9umE9VXvVKgKObu3d-Km8fvB3tEKndx-h63a9XM` | 60 | Google domain verification. **Keep** |
| `_github-pages-challenge-robotlantern` | TXT | `c780f8c05458d53ec3835cc0ca59cb` | 60 | GitHub Pages domain verification. Drop once GitHub Pages is off |

Checked and absent: AAAA and CAA on `@`, **SPF** (no `v=spf1` TXT on `@`), **DMARC**
(`_dmarc`), MTA-STS, and `mail`, `calendar`, `shop`, `blog` and other common subdomains. No
wildcard.

**Mail has no SPF or DMARC record today.** Google Workspace mail works without them, but more
of it lands in spam, and the shop will send receipts and order mail as robotlantern.com. Proposed
for the cutover, if RJ agrees (Google's recommended values):

| Name | Type | Value |
| --- | --- | --- |
| `@` | TXT | `v=spf1 include:_spf.google.com ~all` |
| `_dmarc` | TXT | `v=DMARC1; p=none; rua=mailto:<an address RJ reads>` |

`p=none` only reports; it changes no delivery. Cloudflare Email Routing (the order Worker's
email, LOG.md task 7) adds its own SPF include when it's turned on.
