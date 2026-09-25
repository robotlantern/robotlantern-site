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

## First run

The Pleiades conversation. RJ picked every "likely" and "maybe" candidate in its private
`NOTES.md`, so that list is the answer key for judging how well the proposing model does.
