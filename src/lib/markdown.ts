// Markdown to HTML for essays and conversations. One unified pipeline with a few small
// tree passes of our own, so the content files stay plain Markdown.
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import rehypeKatex from 'rehype-katex';
import { toHtml } from 'hast-util-to-html';

type Node = { type: string; children?: Node[]; [key: string]: any };
type Pass = (tree: Node) => void;

// ChatGPT writes math as \[ … \] and \( … \); remark-math reads $$ … $$ and $ … $.
// Fenced code is left alone.
export function convertMathDelimiters(md: string): string {
  return md
    .split(/(^```[\s\S]*?^```$)/m)
    .map((part, i) =>
      i % 2
        ? part
        : part
            .replace(/^([ \t]*)\\\[([\s\S]+?)\\\][ \t]*$/gm, (_, indent, body) => `${indent}$$${body}$$`)
            .replace(/\\\(([^\n]+?)\\\)/g, (_, body) => `$${body.trim()}$`),
    )
    .join('');
}

const blockParser = unified().use(remarkParse).use(remarkGfm).use(remarkMath);

// ```reasoning worked="47s"``` and ```tool``` blocks become collapsed <details>, with the
// block's own Markdown rendered inside (docs/CONVERSATIONS.md, rule 2).
const collapsedBlocks: Pass = (tree) => {
  const walk = (node: Node) => {
    node.children?.forEach((child, i) => {
      if (child.type === 'code' && (child.lang === 'reasoning' || child.lang === 'tool')) {
        const worked = /worked="([^"]+)"/.exec(child.meta ?? '')?.[1];
        const label = child.lang === 'reasoning' ? 'Reasoning' : 'Tool use';
        node.children![i] = {
          type: 'collapsed',
          data: { hName: 'details', hProperties: { className: ['collapsed', child.lang] } },
          children: [
            {
              type: 'collapsedSummary',
              data: { hName: 'summary' },
              children: [{ type: 'text', value: worked ? `${label} · Worked for ${worked}` : label }],
            },
            ...(blockParser.parse(child.value) as Node).children!,
          ],
        };
      } else walk(child);
    });
  };
  walk(tree);
};

function textOf(node: Node): string {
  if (node.type === 'text') return node.value;
  return (node.children ?? []).map(textOf).join('');
}

function hasClass(node: Node, name: string) {
  const c = node.properties?.className;
  return Array.isArray(c) ? c.includes(name) : c === name;
}

// *[Editor’s note: …]* paragraphs get their own style.
const editorNotes: Pass = (tree) => {
  const walk = (node: Node) =>
    node.children?.forEach((child) => {
      if (child.type === 'element' && child.tagName === 'p') {
        const first = child.children?.find((c) => !(c.type === 'text' && !c.value.trim()));
        if (first?.tagName === 'em' && textOf(first).startsWith('[Editor’s note:')) {
          child.properties = { ...child.properties, className: ['editor-note'] };
        }
      } else walk(child);
    });
  walk(tree);
};

// Tables scroll sideways on a phone instead of widening the page.
const scrollTables: Pass = (tree) => {
  const walk = (node: Node) =>
    node.children?.forEach((child, i) => {
      if (child.type === 'element' && child.tagName === 'table') {
        node.children![i] = {
          type: 'element',
          tagName: 'div',
          properties: { className: ['table-scroll'], tabIndex: 0 },
          children: [child],
        };
      } else walk(child);
    });
  walk(tree);
};

// Relative image paths point at the files next to the content.
const imageBase =
  (base: string): Pass =>
  (tree) => {
    const walk = (node: Node) =>
      node.children?.forEach((child) => {
        if (child.type === 'element' && child.tagName === 'img') {
          const src = String(child.properties?.src ?? '');
          if (src && !/^([a-z]+:|\/|#)/i.test(src)) child.properties!.src = base + src;
          child.properties!.loading = 'lazy';
          child.properties!.decoding = 'async';
        }
        walk(child);
      });
    walk(tree);
  };

// Editor's links (docs/LINKS.md): the first mention of each term in the post links to its
// article. Runs before raw HTML is parsed, so citations and speakers' own links are skipped.
export type EditorLink = { text: string; url: string; sense?: string; title?: string };
export type LinkState = { links: EditorLink[]; done: Set<string> };

const noLinkTags = new Set(['a', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'sup', 'summary']);
const wordChar = /[\p{L}\p{N}]/u;

const editorLinks =
  (state: LinkState): Pass =>
  (tree) => {
    for (const link of state.links) {
      if (state.done.has(link.text)) continue;
      const found = (node: Node): boolean => {
        const kids = node.children ?? [];
        for (let i = 0; i < kids.length; i++) {
          const child = kids[i];
          if (child.type === 'element') {
            if (noLinkTags.has(child.tagName) || hasClass(child, 'math-inline') || hasClass(child, 'math-display')) continue;
            if (found(child)) return true;
          } else if (child.type === 'text') {
            const at = findWord(child.value, link.text);
            if (at < 0) continue;
            const before = child.value.slice(0, at);
            const after = child.value.slice(at + link.text.length);
            kids.splice(
              i,
              1,
              ...(before ? [{ type: 'text', value: before }] : []),
              {
                type: 'element',
                tagName: 'a',
                properties: { href: link.url, title: 'Editor’s link', className: ['editor-link'] },
                children: [{ type: 'text', value: link.text }],
              },
              ...(after ? [{ type: 'text', value: after }] : []),
            );
            return true;
          }
        }
        return false;
      };
      if (found(tree)) state.done.add(link.text);
    }
  };

function findWord(haystack: string, needle: string) {
  for (let at = haystack.indexOf(needle); at >= 0; at = haystack.indexOf(needle, at + 1)) {
    const prev = haystack[at - 1];
    const next = haystack[at + needle.length];
    if ((!prev || !wordChar.test(prev)) && (!next || !wordChar.test(next))) return at;
  }
  return -1;
}

// Attribution (docs/ATTRIBUTION.md): spans index into the Markdown source in code points.
// Each text node is split where its source characters change owner.
export type Span = { start: number; end: number; author: string; copyedit?: { by: string } };
export type Attribution = {
  participants: { id: string; name: string; kind: string }[];
  spans: Span[];
};

const attributionSpans =
  (source: string, attribution: Attribution): Pass =>
  (tree) => {
    const codePoint: number[] = [];
    let cp = 0;
    for (let i = 0; i < source.length; i++) {
      codePoint[i] = cp;
      const c = source.charCodeAt(i);
      if (c < 0xd800 || c > 0xdbff) cp++;
    }
    codePoint[source.length] = cp;
    const kind = Object.fromEntries(attribution.participants.map((p) => [p.id, p.kind]));
    const spans = attribution.spans;
    const spanAt = (point: number) => {
      let lo = 0;
      let hi = spans.length - 1;
      while (lo <= hi) {
        const mid = (lo + hi) >> 1;
        if (spans[mid].end <= point) lo = mid + 1;
        else if (spans[mid].start > point) hi = mid - 1;
        else return spans[mid];
      }
      return undefined;
    };
    // Maps each character of a text node's value back to its source offset. Gives up
    // (no highlight) if the value isn't a plain copy of the source apart from escapes.
    const offsets = (value: string, start: number, end: number) => {
      const out: number[] = [];
      let j = start;
      for (let i = 0; i < value.length; i++) {
        while (j < end && source[j] !== value[i] && (source[j] === '\\' || source[j] === ' ' || source[j] === '\t')) j++;
        if (source[j] !== value[i]) return null;
        out.push(j++);
      }
      return out;
    };
    const walk = (node: Node) => {
      const kids = node.children ?? [];
      for (let i = 0; i < kids.length; i++) {
        const child = kids[i];
        if (child.type === 'element') {
          if (child.tagName !== 'code' && child.tagName !== 'pre') walk(child);
          continue;
        }
        if (child.type !== 'text' || !child.position) continue;
        const map = offsets(child.value, child.position.start.offset, child.position.end.offset);
        if (!map) continue;
        const pieces: Node[] = [];
        let run = '';
        let runSpan: Span | undefined;
        const key = (s?: Span) => (s ? `${s.author}|${s.copyedit?.by ?? ''}` : '');
        const flush = () => {
          if (!run) return;
          if (!runSpan) pieces.push({ type: 'text', value: run });
          else {
            const k = kind[runSpan.author] ?? 'unknown';
            pieces.push({
              type: 'element',
              tagName: 'span',
              properties: {
                className: ['w', `w-${k}`, ...(runSpan.copyedit ? ['w-ce'] : [])],
                dataBy: runSpan.author,
                ...(runSpan.copyedit ? { dataCe: runSpan.copyedit.by } : {}),
              },
              children: [{ type: 'text', value: run }],
            });
          }
          run = '';
        };
        for (let k = 0; k < child.value.length; k++) {
          const s = spanAt(codePoint[map[k]]);
          if (key(s) !== key(runSpan)) {
            flush();
            runSpan = s;
          }
          run += child.value[k];
        }
        flush();
        kids.splice(i, 1, ...pieces);
        i += pieces.length - 1;
      }
    };
    walk(tree);
  };

export type RenderOptions = {
  imageBase?: string;
  links?: LinkState;
  attribution?: Attribution;
};

// Renders Markdown to a hast tree. Exposed as a tree so pages can lift parts out (the
// essay's title) before serializing.
export async function renderTree(md: string, options: RenderOptions = {}) {
  const passes: Pass[] = [];
  if (options.attribution) passes.push(attributionSpans(md, options.attribution));
  if (options.links) passes.push(editorLinks(options.links));
  passes.push(editorNotes, scrollTables);
  if (options.imageBase) passes.push(imageBase(options.imageBase));

  const processor = unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkMath)
    .use(() => collapsedBlocks)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(() => (tree: Node) => passes.forEach((pass) => pass(tree)))
    .use(rehypeRaw)
    .use(rehypeKatex, { output: 'htmlAndMathml' });
  return (await processor.run(processor.parse(md))) as Node;
}

export function toHTML(tree: Node | Node[]) {
  return toHtml(Array.isArray(tree) ? { type: 'root', children: tree } : (tree as any), {
    allowDangerousHtml: true,
  });
}

export async function renderMarkdown(md: string, options: RenderOptions = {}) {
  return toHTML(await renderTree(md, options));
}
