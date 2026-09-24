# Attribution

`tools/attribution/attribution.py` works out who wrote which words of an essay. It uses Python 3
and nothing else. Tests: `python3 -m unittest discover tools/attribution`.

## Input

An ordered list of entries, each with an author and a role:

- **draft**: a full version of the article. Drafts form the chain.
- **copyedit**: a full version whose changes all keep their original author (the Git trailer
  `Contribution: copyedit`).
- **message**: chat text that isn't part of the chain but may have been pasted into a draft.

There are two sources:

- **Git** (the main path, conventions in [WRITING.md](WRITING.md)):
  `attribution.py git --repo DRAFTS --file essay/article.md -o attribution.json`. Each commit
  that touches the file is a version, and its Git author is the author. An email ending in
  `@models.invalid` marks a model.
- **A captured chat** (the first essay): `attribution.py chat MANIFEST.json -o attribution.json`.
  Every captured message becomes a message entry. The private manifest lists which items are
  drafts, how to cut each draft out of its message, any author corrections, and attached files.
  The first essay's manifest is in `.private/first-essay/`.

`--preview page.html` also writes a spot-check page.

## Rules

1. Each draft is diffed word by word against the one before it. Words it keeps keep their owner,
   and words it adds or rewrites belong to its author.
2. A change is a **copyedit** when the words on both sides match apart from case, punctuation
   or spelling (80% similar), or when it only adds or changes spaces and punctuation. The text
   keeps its original author and gets a copyedit mark naming the editor.
3. Words a draft adds that match an earlier message (6+ words in a row) belong to that message's
   author.
4. No specks. A lone matched word inside a rewrite goes with the rewrite. A space or punctuation
   mark between two words by the same author, and the tail of a word, go with the author;
   whoever actually wrote them gets a copyedit mark instead.
5. Only visible prose counts: Markdown syntax, URLs, code, images and footnote navigation don't.
   Everything from a `Footnotes`/`Notes` heading or the first `[^n]:` definition on is the
   footnotes section.

## Decision: copyedits are judged by form, not size

Adopted 2026-09-24. A change counts as a copyedit only when rule 2 says so, or when it comes from a
commit declared as a copyedit. A one- or two-word change that alters wording (adding "now",
changing "You" to "We") is authorship, whoever made it. Reasons:

- Word count doesn't measure meaning. One word can qualify an argument or change its voice.
  A form test can be checked from the diff, and a size threshold can't.
- RJ publishes his own essays, so a looser rule would credit the publisher. The strict rule makes
  a claim any reader can verify against the drafts.
- In Git, a copyedit pass is declared with a trailer by whoever made it, so the tool doesn't have
  to guess. A copyediting agent works under its own identity, and its edits show in its own
  copyedit count, not as authorship.

On the first essay, the looser rule would have given 92% instead of 91% RJ in the body.

## Output

```jsonc
{
  "schema": "robot-lantern/attribution@1",
  "article_sha256": "…",               // the Markdown this applies to
  "offset_unit": "Unicode code points in the article Markdown",
  "participants": [{"id": "rj-carroll", "name": "RJ Carroll", "kind": "human"}],
  "versions": [{"n": 0, "author": "rj-carroll", "role": "draft", "label": "…"}],
  "totals": {
    "body":      {"chars": 4116, "authors": {"rj-carroll": {"chars": 3757, "percent": 91}},
                  "copyedits": {"gpt-5.6-sol": {"edits": 22, "chars": 55}}},
    "footnotes": {"…": "…"}
  },
  "spans": [{"start": 2, "end": 14, "section": "body", "author": "rj-carroll", "from": 0,
             "copyedit": {"by": "gpt-5.6-sol", "version": 44}}]
}
```

Spans cover only counted characters and index into the article's Markdown source. The renderer
highlights a text node by intersecting its source position with the spans. `from` and
`copyedit.version` index into `versions`. Percentages use largest remainders, so they sum to 100.
