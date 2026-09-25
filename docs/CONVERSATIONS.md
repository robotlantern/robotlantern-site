# Importing a conversation

Status: proposed 2026-09-24, from the first import (`its-always-the-pleiades`). RJ to confirm.

## Two copies

- **Capture (private):** `.private/conversations/<slug>/` holds the export as retrieved, an asset
  manifest and the original files. It is never edited, so every public change can be checked
  against it. It keeps source IDs and the positions of citations.
- **Public copy:** `src/content/conversations/<slug>/` holds `conversation.md` and its images.
  It is generated from the capture by scripted replacements, and each change shows on the page
  as a bracketed marker or an editor's note.

## Format of `conversation.md`

- Frontmatter: `title`, `date`, `source`, `participants` (`id`, `name`, `kind`, and `model` for
  an AI, `unknown` unless the model is confirmed), `range`.
- Each message starts with `## <Speaker>`, followed by the message's Markdown. Images go inline
  where they were attached, with real alt text.
- Editor's notes are their own paragraph: `*[Editor’s note: …]*`.

## Rules

1. **Citations are kept.** They matter for checking a model's claims later. Each cited source
   becomes a numbered marker where it appeared, plus a source list at the end of the message
   with the URL and title. A source that hasn't been recovered yet is listed as not recovered.
   Until citations are recovered, one editor's note says they're missing, and the capture
   keeps their positions. ChatGPT's `:chatgpt-content-reference` tokens and the Claude app's
   search results both map to this. How to recover them: [CITATIONS.md](CITATIONS.md).
2. **Reasoning and tool use: only what the app showed.** Include the summarized reasoning,
   search queries and tool steps the app displayed to the user. Put each in a fenced block
   (```` ```reasoning ```` or ```` ```tool ````) before the message it led to. The page shows
   these collapsed. Never reconstruct them.
3. **Missing pieces get a note, never a guess.** If a message, an image or a reply's text is
   missing, add an editor's note where it belongs.
4. **Redact in the speaker's voice.** Replace private details with brackets that read naturally
   where they appear, for example "[your town]" in the model's reply and "[exact coordinates
   removed]". Crop an image rather than blurring it. Strip image metadata and keep the color
   profile.
5. **Links added by the editor are marked** with the link title `"Editor’s link"`, so they can be
   styled differently from links the speakers wrote.
6. **No cleanup of substance.** Typos, hedges and asides stay. Only the redactions above change
   the text.
