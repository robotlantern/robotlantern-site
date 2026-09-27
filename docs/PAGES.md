# Page design

Status: RJ's direction from reviewing the first preview, 2026-09-27.

## Everywhere

- Sections: Thoughts, Chats, Builds, Shop, each with its own small icon. Routes are `/thoughts/`,
  `/chats/`, `/builds/`, `/shop/`. An authors page (`/authors/`) is linked from every page's
  footer, not from the main navigation.
- People are shown by first name with a person icon, and models by name with a robot icon. RJ
  is "RJ"; his full name appears only in his bio card.
- No labels that state the obvious: no "Essay" or "Conversation" kicker above a title, no names
  or numbers on chat messages, no note saying a transcript was edited when the brackets show it.
- The wordmark's top margin equals its left margin.

## Thoughts (essays)

- Under the title, in place of a byline: the attribution block. It shows each author with
  their icon, linked to their entry on the authors page, the essay and footnote percentages, a
  ring showing the essay body's split, and one toggle that highlights who wrote which words.
- Desktop: author cards (a sentence or two each) in the left margin. Phones hide them.
- No "Inside this post" and no Markdown download. If the chat behind an essay is worth reading,
  it's published as a chat and cross-linked.

## Chats (conversations)

- It should feel like a chat app. RJ's messages are orange speech bubbles with a tail, in a sans
  serif. The model's replies are full-column serif text (RJ's pick, 2026-09-27). A blue-bubble
  version was tried; it's in Git history at commit `d91c93f`.
- Under the title, one line: the speakers with their icons, the date as M.D.YYYY, and the
  `time` phrase. Nothing else before the first message. When scrolling, a small copy of the
  title stays at the top.
- List and detail: on desktop, a sidebar lists the chats, like the ChatGPT and Claude apps. On a
  phone, the list opens as a drawer from a menu button.
- Position: a column of dashes along the left edge, colored by speaker and sized by message
  length. Dashes near the reader's position grow taller and wider, and tapping or dragging on
  the column jumps there. They're dim, and appear only once the title has scrolled under the bar. No summaries or section headings.
