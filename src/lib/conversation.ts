// Splits a conversation.md body into messages (docs/CONVERSATIONS.md): each message starts
// with "## <Speaker>". Anything before the first message is the editor's preamble.
export type Participant = { id: string; name: string; kind: 'human' | 'ai'; model?: string };
export type RawMessage = { speaker: Participant; markdown: string };

export function splitMessages(body: string, participants: Participant[]) {
  const preamble: string[] = [];
  const messages: { speaker: Participant; lines: string[] }[] = [];
  let fenced = false;
  for (const line of body.split('\n')) {
    if (/^```/.test(line)) fenced = !fenced;
    const heading = !fenced && /^## (.+?)\s*$/.exec(line);
    if (heading) messages.push({ speaker: findSpeaker(heading[1], participants), lines: [] });
    else (messages.at(-1)?.lines ?? preamble).push(line);
  }
  return {
    preamble: preamble.join('\n').trim(),
    messages: messages.map((m): RawMessage => ({ speaker: m.speaker, markdown: m.lines.join('\n').trim() })),
  };
}

function findSpeaker(label: string, participants: Participant[]) {
  const l = label.toLowerCase();
  const match =
    participants.find((p) => p.name.toLowerCase() === l || p.id === l) ??
    participants.find((p) => p.name.toLowerCase().startsWith(l + ' '));
  if (!match) throw new Error(`Conversation speaker "${label}" isn't in the frontmatter's participants.`);
  return match;
}
