# Importing a conversation

Status: approved by RJ 2026-09-25, from the first import (`its-always-the-pleiades`).

## Two copies

- **Capture (private):** `.private/conversations/<slug>/` holds the export as retrieved, an asset
  manifest and the original files. It is never edited, so every public change can be checked
  against it. It keeps source IDs and the positions of citations.
- **Public copy:** `src/content/conversations/<slug>/` holds `conversation.md` and its images.
  It is generated from the capture by scripted replacements, and each change shows on the page
  as a bracketed marker or an editor's note.

## Format of `conversation.md`

- Frontmatter: `title`, `date`, `time` (a plain phrase such as "before dawn"), `source`,
  `participants` (`id`, `name` as the transcript's headings use it, `kind`, `author`, and `model`
  for an AI), `timezone`, `range`. `author` is an entry in `src/content/authors/`, which holds the
  display name, full name and bio. RJ is "RJ" everywhere except his bio. `model` is the name the
  app showed for the conversation, as RJ confirms it, or `unknown`. A chat app may route single turns to other models, and only the
  account export records that, so this is the model as the speaker saw it.
- `timezone` is RJ's local zone at the time. Message times, once a capture keeps them, show
  in that zone: a header at each new calendar day, and a message's time when it's tapped.
- Each message starts with `## <Speaker>`, followed by the message's Markdown. Images go inline
  where they were attached, with real alt text.
- Editor's notes are their own paragraph: `*[Editor’s note: …]*`.
- Citations are HTML so the page can style them: `<sup class="cite"><a href="…" title="…">1</a></sup>`
  where cited, then `<ol class="sources">` after the message, one `<li>` per source with the
  title linked and the site after a `·`. A withheld link keeps its number and is marked
  `[link removed]`.
- Reasoning goes in a fenced block with the app's "Worked for …" time, if shown:
  ```` ```reasoning worked="47s" ````. The page shows it collapsed.

## Rules

1. **Citations are kept.** They matter for checking a model's claims later. Each cited source
   becomes a numbered marker where it appeared, plus a source list at the end of the message
   with the URL and title. A source that hasn't been recovered yet is listed as not recovered.
   Until citations are recovered, one editor's note says they're missing, and the capture
   keeps their positions. Once they're recovered, the note goes. There's no preamble note: the
   brackets speak for themselves. ChatGPT's `:chatgpt-content-reference` tokens and the Claude app's
   search results both map to this. How to recover them: [CITATIONS.md](CITATIONS.md).
2. **Reasoning and tool use: only what the app showed.** Include the summarized reasoning,
   search queries and tool steps the app displayed to the user. Put each in a fenced block
   (```` ```reasoning ```` or ```` ```tool ````) before the message it led to. The page shows
   these collapsed. Never reconstruct them.
3. **Missing pieces get a note, never a guess.** If a message, an image or a reply's text is
   missing, add an editor's note where it belongs.
4. **Don't make it any worse.** Some of RJ's details are already public. Publish nothing that
   narrows his location or identity further, including in links, file names and image
   metadata. **Redact in the speaker's voice.** Replace private details with brackets that read naturally
   where they appear, for example "[your town]" in the model's reply and "[exact coordinates
   removed]". Crop an image rather than blurring it. Strip image metadata and keep the color
   profile.
5. **Links added by the editor are marked** (how they're chosen: [LINKS.md](LINKS.md)) with the link title `"Editor’s link"`, so they can be
   styled differently from links the speakers wrote.
6. **No cleanup of substance.** Typos, hedges and asides stay. Only the redactions above change
   the text.
