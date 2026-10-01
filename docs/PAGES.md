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
- Thoughts and Chats are list and detail, like a chat app (`src/components/Reader.astro`).
  `/thoughts/` and `/chats/` open on the newest piece, with the list beside it on desktop and
  in the site menu on phones. There are no separate list pages. The column is endless: near the end
  of a piece, the next one (newest posted first) is appended, and the address, page title and
  list follow whichever piece is in view.
- The site menu is the same everywhere: Home (the ovaloid under a roof), the four sections, the
  footer pages, and on Thoughts and Chats that section's list with search. Its head carries the
  one-line wordmark. It opens from the logo: as the reader scrolls, the wordmark stays in the
  corner and collapses into it (docs/BRAND.md, "The collapse"). At the top of a page the full
  wordmark links home (`src/components/SiteMenu.astro`).
- The section nav is anchored at the bottom of every page, a translucent dark bar floating over
  the content (`src/components/BottomNav.astro`; RJ, 2026-09-30). On the home page it sits on
  the tree silhouette instead and appears once the wordmark lands.
- The logo sits in the top-left corner, centered in the bar that reading pages pin to the top
  (`--bar-h`, `--logo` in `src/styles/global.css`), with room around it.
- Builds run full screen with no site chrome, except a quiet way home in the same corner: the
  logo (`src/layouts/BuildLayout.astro`).
- iOS Safari (26) tints its status bar from the page: from the topmost opaque fixed layer touching
  the top edge, or else the page's background color, and it ignores a layer that's transparent.
  So every page's root background is the color at its top (`--deep`), and the home page moves it,
  and a 24px strip blended with "lighten", with the sky as you scroll. Tested in the iOS 26
  simulator, 2026-10-01.

## Thoughts (essays)

- Under the title, in place of a byline: the attribution block. It shows each author with
  their icon, linked to their entry on the authors page, the essay and footnote percentages, a
  ring showing the essay body's split, and one toggle that highlights who wrote which words.
- Wide screens: author cards (a sentence or two each) in the right margin; the list takes the
  left. Narrower screens hide them.
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
  phone, the list is in the site menu. The list sorts by when a chat was posted
  here (the default) or when it happened, and has a search box. The posted date lives in
  `post.json` beside the transcript.
- A chat that led to a build ends with a link to it.
- Position: a column of faint dashes along the right edge, colored by speaker and sized by message
  length. Dashes near the reader's position grow taller and wider, and tapping or dragging on
  the column jumps there. They're dim, and appear only once the title has scrolled under the bar. No summaries or section headings.

## Builds

- The Builds page shows one card per build (`src/content/builds/*.json`): a screenshot from
  inside it behind a headline, a line saying what it is, a Launch button, and the chat it came
  from.
