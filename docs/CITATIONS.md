# Recovering citations from a chat

Status: approved by RJ 2026-09-25, from the Pleiades conversation. v2 is the current prompt.

Exports and shared-chat links drop the sources behind a reply's citations. Instead, at the end
of the conversation, we ask the model for them in the same app, then check every link ourselves.

## What the site needs

For each citation marker in a reply: where it sits (the reply and the text just before it) and
the URL. We fetch the title from the page, so the model's title is only a fallback. A source
the model can't see any more is listed as not recovered, never guessed.

## Rules for the request

- Ask only about the conversation's own visible content. Don't ask for hidden reasoning, system
  instructions, tool internals or anything else the app doesn't show. A request that reads as
  probing the model can be refused, and it isn't what we need.
- Ask for every citation in order, repeats included. A deduplicated list loses positions.
- Ask the model to say when it's working from memory, and to use null rather than fill a gap.
  Models whose context has been compacted may rebuild sources that look plausible.
- Treat the answer as a lead. A URL goes on the page only after it loads and the page supports
  the sentence it's attached to.

## Prompt versions

Each version is recorded with the app and model it was tried on. Private results go in
`.private/conversations/<slug>/sources/`.

### v1: ChatGPT app, ChatGPT-5.6-sol (2026-09-25)

> Return a list of sources used in this chat with text, target url and metadata in a single code
> block, so I can include them when I publish some of this material.

Result: 28 real, on-topic sources, each listed once, with a description, URL and a `used_for`
note. Titles were marked unverified for about half. Positions were missing, so four repeat
citations had to be inferred. It also included sources from turns after the published range.
Good enough to recover a conversation, with a check.

### v2: ChatGPT app, ChatGPT-5.6-sol (2026-09-25)

The `{{…}}` value is filled in per conversation.

````text
I'm publishing part of this conversation and want to show your citations where they appeared.
Please go through your replies in order, from the first one through the reply that ends
"{{last words of the last published reply}}", and list every web citation in the order it
appears, including repeat citations of the same source. Leave out links to files you made, and
replies with no citations.

Return a single JSON code block in this shape:

{
  "format": "rl-citations/2",
  "replies": [
    {
      "starts_with": "the first several words of the reply, copied exactly",
      "citations": [
        {
          "n": 1,
          "after": "the last several words before the citation, copied exactly",
          "url": "https://…",
          "title": "the source's title as you have it, or null",
          "visible": true
        }
      ]
    }
  ]
}

Set "visible" to true if the source's details are still available to you in this conversation,
and false if you're going from memory of having cited it. Use null for anything you can't see
rather than filling it in. I'll open and check every link before publishing.
````

Result: 27 of the capture's 28 web citations in the range, in order, with repeats. It confirmed
3 of the 4 positions inferred from v1 and missed one citation. Every `after` quote was real
text. 24 sat right before their marker, two were a sentence early, and one came from a later
reply. Every source was marked `visible`, and titles were null where v1 had flagged them as
unverified. URLs carry `?utm_source=chatgpt.com`, which we strip.

So match by order within each reply and check the count against the capture's markers. Treat
`after` as a hint.

## Titles we can't fetch

Reddit is blocked in the built-in browser, and some sites answer scripts with a bot check. We
don't try to get around either. The title is ChatGPT's if the URL slug matches it; otherwise it's
a label taken from the URL, such as "Post in r/Stargazing".

## Not yet tried

The Claude app, other ChatGPT models, and conversations long enough to have been compacted.
