# Recovering citations from a chat

Status: proposed 2026-09-25, from the Pleiades conversation. Exports and shared-chat links drop
the sources behind a reply's citations. Instead, at the end of the conversation, we ask the model
for them in the same app, then check every link ourselves.

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

### v2: proposed, not yet run

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

## Not yet tried

The Claude app, other ChatGPT models, and conversations long enough to have been compacted.
