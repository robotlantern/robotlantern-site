# Writing an article in Git

Attribution comes from commit history, so the history has to say who wrote what.

## Where drafts live

Drafts go in a private repo outside this one (this repo is public). Use one folder per article, so
`git log -- <folder>` shows only that article's history. When the article is published, the
attribution tool reads that history and writes the final text and the attribution JSON here.

## Conventions

1. **RJ's own draft is the first commit,** made before any model sees it.
2. **Each participant commits only their own changes.** A model's edits go in their own commit
   with the model as author, for example
   `git commit --author="GPT-5.6-sol <gpt-5.6-sol@models.invalid>"`. Never stage RJ's
   uncommitted work in a model's commit, or the other way around.
3. **Text pasted from a chat gets its own commit, authored by whoever wrote it.** If RJ copies a
   model's suggested sentence into the draft, that commit's author is the model.
4. **Mark copyedit passes.** A commit that only fixes case, punctuation, spelling or grammar gets
   the trailer `Contribution: copyedit`. Its changes keep the original author's credit, so the
   tool doesn't have to guess. A copyedit agent is scoped to form only (case, punctuation,
   spelling, grammar), commits under its own name, and marks every commit this way. Any change
   to wording goes in an ordinary commit and counts as authorship, even a single word. See
   "Decision" in [ATTRIBUTION.md](ATTRIBUTION.md).
5. **Never squash, rebase or amend.** The history is the evidence.
6. **Keep the conversation too.** Save the chat alongside the drafts, privately, for the "Inside
   this post" view. Git records who changed the text. The chat records how the changes came about.

## Publishing

Run `python3 tools/attribution/attribution.py git --repo <drafts repo> --file <folder>/article.md
-o attribution.json --preview check.html` and look over the preview before copying the article
and its JSON here. See [ATTRIBUTION.md](ATTRIBUTION.md).
