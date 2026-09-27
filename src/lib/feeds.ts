// The order pieces are read in: newest posted first. /chats/ and /thoughts/ open on the first,
// and each piece's page continues into the next one as the reader scrolls (Reader.astro).
import { getCollection } from 'astro:content';

export type FeedItem = { id: string; href: string; title: string; posted: Date; date: Date; search: string };

export async function chatFeed(): Promise<FeedItem[]> {
  return (await getCollection('conversations'))
    .map((c) => ({
      id: c.id,
      href: `/chats/${c.id}/`,
      title: c.data.title,
      posted: c.data.posted ?? c.data.date,
      date: c.data.date,
      search: [c.data.title, ...c.data.participants.map((p) => p.name)].join(' ').toLowerCase(),
    }))
    .sort((a, b) => +b.posted - +a.posted || +b.date - +a.date);
}

export async function thoughtFeed(): Promise<FeedItem[]> {
  return (await getCollection('essays'))
    .map((e) => ({ id: e.id, href: `/thoughts/${e.id}/`, title: e.data.title, posted: e.data.date, date: e.data.date, search: e.data.title.toLowerCase() }))
    .sort((a, b) => +b.posted - +a.posted);
}

// The piece after `id` in reading order, or none at the end.
export const nextAfter = (feed: FeedItem[], id: string) => feed[feed.findIndex((f) => f.id === id) + 1];
