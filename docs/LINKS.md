# Reference links

Status: proposed 2026-09-25.

Before a post is published, it gets editor's links for terms a reader may want to look up. A
small model (Haiku class) proposes them and a script checks them. RJ skims the list.

## Rule

Link the first mention in the post of each term a curious general reader might look up, when
one Wikipedia article covers that exact sense:

- named things: objects, places, people, works, organizations, software, events
- technical terms the text uses without explaining them

Skip everyday words, terms the text explains where they appear, anything already linked or
cited, and the speakers themselves. Never link inside headings, code, math or image alt text.
Prefer the specific article ("Taurus (constellation)", not "Taurus"). Link each term once per
post, and put at most one link in a sentence. A non-Wikipedia page is allowed only when it's
the obvious home for the term and no article fits, such as a subreddit, and RJ approves it.

## Steps

1. **Propose (agent).** Write `links.json` next to the post. For each term, record the exact
   text of its first mention, the article URL and a few words saying which sense is meant.
2. **Check (script).** Each URL must resolve to an article, not to a disambiguation page or a
   redirect to a different topic. Record the canonical title.
3. **Match (agent).** Compare each article's summary with the sentence it's attached to, and
   drop any that don't fit.
4. **Review (RJ).** Strike anything unwanted.
5. **Apply (build).** The site links the first mention at build time, marked as the editor's
   (docs/CONVERSATIONS.md, rule 5). The source text isn't changed, so attribution isn't
   affected.

Step 2 is `tools/links/check.py <links.json>`. It fails on a disambiguation page or a dead URL,
notes redirects, and writes each article's canonical title and description back into the file.

## First run (2026-09-27)

The Pleiades chat. RJ's picks from its private `NOTES.md` are the answer key and the published
list: 37 links. Dropped: September ε-Perseids (no article) and Proxima Centauri (already cited
to its article in the same sentence). Two sentences carry two links (Algol and Mirfak, Bellatrix
and Rigel) because RJ picked all four.

Haiku, proposing blind, returned 58 terms and found 29 of the 37 (78%). It missed the
subreddit, the "Howl" allusion, Bortle, stereopsis, GRB 080319B, the inverse-square law, the
Perseids, and core-collapse supernova (it chose Type II supernova instead). Its mistakes:
a disambiguation page (the check caught it), "red supergiant" linked to Red giant (the check
can't catch that; the match step must), a term that isn't in the text, and two already-cited
terms, against the rule. Its extras were mostly reasonable (Aldebaran, Perseus, Orion, the
planets, the Milky Way).

Verdict: a Haiku-class proposer is usable only with the check and a real match step, and RJ's
skim stays necessary. It finds common terms well and misses allusions and community names.
