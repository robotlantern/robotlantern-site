"""Word-level attribution through an article's version chain.

Input is an ordered list of entries, each with an author. Drafts and copyedit passes form the
chain: each one is diffed against the one before it, and unchanged words keep their owner.
Messages are not in the chain; text a draft inserts that matches an earlier message (6+ words)
is credited to that message's author. Details and output format: docs/ATTRIBUTION.md.

  python3 tools/attribution/attribution.py git --repo DRAFTS --file essay/article.md -o out.json
  python3 tools/attribution/attribution.py chat MANIFEST.json -o out.json
  python3 tools/attribution/attribution.py versions VERSIONS.json -o out.json
"""
import argparse, hashlib, json, re, subprocess, sys
from difflib import SequenceMatcher

SCHEMA = 'robot-lantern/attribution@1'
MESSAGE_MIN_WORDS = 6

# ---------------------------------------------------------------- Markdown projection
# Each source character is TEXT (visible prose, counted), SEP (a newline: kept for
# tokenizing, never counted), or omitted (syntax, URLs, code, footnote navigation).
TEXT, SEP = 'text', 'sep'
BLOCK_PREFIX = re.compile(r'[ \t]*(?:>[ \t]?)*[ \t]*(?:#{1,6}[ \t]+|[-*+][ \t]+|\d+[.)][ \t]+)?')
FOOTNOTE_DEF = re.compile(r'\[\^[^\]]+\]:[ \t]*')
LINK_DEF = re.compile(r'[ \t]*\[[^\]^][^\]]*\]:[ \t]*\S')
RULE = re.compile(r'[ \t]*(?:[-*_][ \t]*){3,}$|[ \t]*=+[ \t]*$')
FENCE = re.compile(r'[ \t]*(`{3,}|~{3,})')
FOOTNOTE_HEADING = re.compile(r'[ \t]*#{1,6}[ \t]+(?:foot)?notes[ \t]*#*[ \t]*$', re.I)
TAG = re.compile(r'<!--.*?-->|</?[A-Za-z][^<>]*>|<(?:https?|mailto):[^<>\s]+>', re.S)


def _closing(s, i, end, open_, close):
    """Index of the bracket closing s[i], or -1."""
    depth = 0
    for k in range(i, end):
        if s[k] == '\\':
            continue
        if s[k] == open_ and (k == 0 or s[k - 1] != '\\'):
            depth += 1
        elif s[k] == close and (k == 0 or s[k - 1] != '\\'):
            depth -= 1
            if depth == 0:
                return k
    return -1


def _inline(s, i, end, kind):
    while i < end:
        c = s[i]
        if c == '\\' and i + 1 < end and not s[i + 1].isalnum() and not s[i + 1].isspace():
            kind[i + 1] = TEXT
            i += 2
        elif c == '`':
            run = len(s[i:end]) - len(s[i:end].lstrip('`'))
            close = s.find('`' * run, i + run, end)
            if close < 0:
                kind[i:i + run] = [TEXT] * run
                i += run
            else:
                i = close + run  # code: not prose
        elif c == '<' and (m := TAG.match(s, i, end)):
            if re.match(r'<sup\b', m.group(0), re.I):  # footnote reference number
                close = s.lower().find('</sup>', m.end(), end)
                i = end if close < 0 else close + len('</sup>')
            else:
                i = m.end()
        elif c == '!' and i + 1 < end and s[i + 1] == '[':
            j = _closing(s, i + 1, end, '[', ']')
            if j > 0 and j + 1 < end and s[j + 1] == '(' and (k := _closing(s, j + 1, end, '(', ')')) > 0:
                i = k + 1  # image: alt text is not prose
            else:
                kind[i] = TEXT
                i += 1
        elif c == '[':
            j = _closing(s, i, end, '[', ']')
            if s.startswith('[^', i) and j > 0:
                i = j + 1  # footnote reference
                continue
            k = -1
            if j > 0 and j + 1 < end and s[j + 1] == '(':
                k = _closing(s, j + 1, end, '(', ')')
            elif j > 0 and j + 1 < end and s[j + 1] == '[':
                k = _closing(s, j + 1, end, '[', ']')
            if k < 0:
                kind[i] = TEXT
                i += 1
                continue
            target = s[j + 2:k].strip().lstrip('<')
            if target.startswith('#'):
                i = k + 1  # in-page navigation such as a footnote back-link
            else:
                _inline(s, i + 1, j, kind)
                i = k + 1
        elif c == '*' or (c == '~' and s.startswith('~~', i)):
            i += 1 + (c == '~')
        elif c == '_' and not ((i > 0 and s[i - 1].isalnum()) and (i + 1 < end and s[i + 1].isalnum())):
            i += 1
        else:
            kind[i] = TEXT
            i += 1


def project(md):
    """Return (kind, section) per source character. section is 'body' or 'footnotes'."""
    kind = [None] * len(md)
    section = ['body'] * len(md)
    in_footnotes, fence = False, None
    pos = 0
    for line in md.split('\n'):
        start, end = pos, pos + len(line)
        pos = end + 1
        if end < len(md):
            kind[end] = SEP
        if fence:
            if line.strip().startswith(fence):
                fence = None
            continue
        if m := FENCE.match(line):
            fence = m.group(1)
            continue
        if FOOTNOTE_HEADING.match(line) or FOOTNOTE_DEF.match(line):
            in_footnotes = True
        if in_footnotes:
            section[start:pos] = ['footnotes'] * (min(pos, len(md)) - start)
        if not line.strip() or RULE.match(line) or LINK_DEF.match(line):
            continue
        i = start + BLOCK_PREFIX.match(line).end()
        if m := FOOTNOTE_DEF.match(md, i, end):
            i = m.end()
        if line.lstrip().startswith('|'):
            if re.fullmatch(r'[\s|:-]+', line):
                continue
            for cell in re.finditer(r'[^|]+', line):
                _inline(md, start + cell.start(), start + cell.end(), kind)
            continue
        line_end = end
        if re.search(r'[ \t]+#+[ \t]*$', line) and line.lstrip().startswith('#'):
            line_end = start + len(re.sub(r'[ \t]+#+[ \t]*$', '', line))
        _inline(md, i, line_end, kind)
    return kind, section


# ---------------------------------------------------------------- tokens
TOKEN = re.compile(r'\w+|[^\w\s]|\s+')


class Doc:
    """A version's projected text as tokens, with each token's source character indices."""

    def __init__(self, md):
        self.md = md
        self.kind, self.section = project(md)
        chars = [(i, md[i]) for i in range(len(md)) if self.kind[i] in (TEXT, SEP)]
        text = ''.join(c for _, c in chars)
        self.tokens, self.index = [], []
        for m in TOKEN.finditer(text):
            self.tokens.append(m.group(0))
            self.index.append([chars[k][0] for k in range(m.start(), m.end())])


def is_word(t):
    return bool(re.search(r'\w', t))


def words(tokens):
    return sum(map(is_word, tokens))


def mechanical(a, b):
    """Case, punctuation or spelling-level change between two whitespace-delimited words."""
    if a.lower() == b.lower() or re.sub(r'\W', '', a).lower() == re.sub(r'\W', '', b).lower():
        return True
    return len(a) >= 4 and SequenceMatcher(None, a.lower(), b.lower()).ratio() >= 0.8


def whole_words(tokens, i, j):
    """The whitespace-delimited words touched by tokens[i:j]."""
    while i > 0 and not tokens[i - 1].isspace():
        i -= 1
    while j < len(tokens) and not tokens[j].isspace():
        j += 1
    return ''.join(tokens[i:j]).split()


def spoken(tokens):
    """Whitespace-delimited words, so that "I’m" counts once."""
    return len([w for w in ''.join(tokens).split() if re.search(r'\w', w)])


def opcodes(prev, cur):
    """difflib opcodes, with stray one-word matches inside a rewrite folded into the rewrite."""
    ops = [list(o) for o in SequenceMatcher(None, prev, cur, autojunk=False).get_opcodes()]
    out = []
    for k, op in enumerate(ops):
        tag, a, b, c, d = op
        between = tag == 'equal' and out and out[-1][0] != 'equal' and k + 1 < len(ops) and ops[k + 1][0] != 'equal'
        if between and (words(cur[c:d]) == 0 or (
                spoken(cur[c:d]) == 1 and spoken(cur[out[-1][3]:out[-1][4]]) + spoken(cur[ops[k + 1][3]:ops[k + 1][4]]) >= 3)):
            out[-1] = ['replace', out[-1][1], b, out[-1][3], d]
            continue
        if tag != 'equal' and out and out[-1][0] != 'equal':
            out[-1] = ['replace', out[-1][1], b, out[-1][3], d]
            continue
        out.append(op)
    return out


# ---------------------------------------------------------------- chain blame
def attribute(entries, small_edits='authorship'):
    """entries: [{author, role: draft|copyedit|message, text, label}]. Returns (final Doc, owners).

    An owner is {author, from, copyedit?: {by, version, op}} per final token."""
    docs = [Doc(e['text']) for e in entries]
    messages = []
    prev = prev_own = None
    op_id = 0
    for n, (e, doc) in enumerate(zip(entries, docs)):
        if e['role'] == 'message':
            messages.append(n)
            continue
        t = doc.tokens
        if prev is None:
            prev, prev_own = doc, [{'author': e['author'], 'from': n} for _ in t]
            continue
        own = [None] * len(t)
        pt = prev.tokens
        for tag, a, b, c, d in opcodes(pt, t):
            if tag == 'equal':
                own[c:d] = prev_own[a:b]
                continue
            if tag == 'delete':
                continue
            op_id += 1
            old, new = pt[a:b], t[c:d]
            ow, nw = whole_words(pt, a, b), whole_words(t, c, d)
            copy = (e['role'] == 'copyedit' or words(new) == 0
                    or (len(ow) == len(nw) and all(map(mechanical, ow, nw)))
                    or (small_edits == 'copyedit' and words(old) <= 2 and words(new) <= 2))
            if copy:
                for k in range(c, d):
                    j = a + (k - c)
                    base = (prev_own[j] if tag == 'replace' and len(old) == len(new)
                            else own[c - 1] if c > 0 and own[c - 1] else prev_own[min(a, len(prev_own) - 1)])
                    own[k] = {'author': base['author'], 'from': base['from'],
                              'copyedit': {'by': e['author'], 'version': n, 'op': op_id}}
                continue
            own[c:d] = [{'author': e['author'], 'from': n}] * (d - c)
            for m in messages:  # text pasted from an earlier message keeps that message's author
                mt = docs[m].tokens
                for blk in SequenceMatcher(None, new, mt, autojunk=False).get_matching_blocks():
                    if blk.size and words(new[blk.a:blk.a + blk.size]) >= MESSAGE_MIN_WORDS:
                        for k in range(c + blk.a, c + blk.a + blk.size):
                            if own[k]['from'] == n:
                                own[k] = {'author': entries[m]['author'], 'from': m}
        prev, prev_own = doc, own
    # Remove specks. A space or punctuation mark between two words by the same author, and the
    # tail of a word whose start is someone else's, belong to that author; whoever put the speck
    # there is recorded as having made a copyedit.
    t = prev.tokens

    def absorb(k, owner):
        nonlocal op_id
        if prev_own[k]['author'] != owner['author']:
            op_id += 1
            prev_own[k] = {'author': owner['author'], 'from': owner['from'],
                           'copyedit': {'by': prev_own[k]['author'], 'version': prev_own[k]['from'], 'op': op_id}}

    word_at = [k for k, tok in enumerate(t) if is_word(tok)]
    for x, y in zip(word_at, word_at[1:]):
        if prev_own[x]['author'] == prev_own[y]['author']:
            for k in range(x + 1, y):
                absorb(k, prev_own[x])
    k = 0
    while k < len(t):
        j = k
        while j + 1 < len(t) and not t[j + 1].isspace() and not t[k].isspace():
            j += 1
        inner = [m for m in range(k, j + 1) if is_word(t[m])]  # quotes and trailing commas stay out
        for m in range(inner[0] + 1, inner[-1] + 1) if inner else ():
            absorb(m, prev_own[inner[0]])
        k = j + 1
    return prev, prev_own


def largest_remainder(counts):
    total = sum(counts.values())
    if not total:
        return {k: 0 for k in counts}
    raw = {k: 100 * v / total for k, v in counts.items()}
    out = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: (-(raw[k] - out[k]), k))[:100 - sum(out.values())]:
        out[k] += 1
    return out


def build(data, small_edits='authorship', source_kind='versions'):
    entries = data['versions']
    assert entries and entries[0]['role'] != 'message', 'the first entry must be a draft'
    final, owners = attribute(entries, small_edits)
    md = final.md
    # per character owner, counted characters only
    char_owner = {}
    for tok_idx, own in zip(final.index, owners):
        for i in tok_idx:
            if final.kind[i] == TEXT:
                char_owner[i] = own
    spans = []
    for i in sorted(char_owner):
        own, sec = char_owner[i], final.section[i]
        key = (own['author'], own['from'], json.dumps(own.get('copyedit'), sort_keys=True), sec)
        if spans and spans[-1]['end'] == i and spans[-1]['_key'] == key:
            spans[-1]['end'] = i + 1
            continue
        span = {'start': i, 'end': i + 1, 'section': sec, 'author': own['author'], 'from': own['from']}
        if own.get('copyedit'):
            span['copyedit'] = {'by': own['copyedit']['by'], 'version': own['copyedit']['version']}
        span['_key'] = key
        spans.append(span)
    totals = {}
    for sec in ('body', 'footnotes'):
        counts, edits, edit_chars = {}, {}, {}
        for i, own in char_owner.items():
            if final.section[i] != sec:
                continue
            counts[own['author']] = counts.get(own['author'], 0) + 1
            if ce := own.get('copyedit'):
                edits.setdefault(ce['by'], set()).add(ce['op'])
                edit_chars[ce['by']] = edit_chars.get(ce['by'], 0) + 1
        pct = largest_remainder(counts)
        totals[sec] = {'chars': sum(counts.values()),
                       'authors': {a: {'chars': counts[a], 'percent': pct[a]} for a in sorted(counts)},
                       'copyedits': {a: {'edits': len(edits[a]), 'chars': edit_chars[a]} for a in sorted(edits)}}
    for s in spans:
        del s['_key']
    participants = data.get('participants', {})
    for e in entries:
        participants.setdefault(e['author'], {'name': e['author'], 'kind': 'unknown'})
    return {
        'schema': SCHEMA,
        'method': 'revision-chain word blame',
        'source': source_kind,
        'policy': {'small_edits': small_edits, 'message_match_min_words': MESSAGE_MIN_WORDS},
        'article_sha256': hashlib.sha256(md.encode()).hexdigest(),
        'offset_unit': 'Unicode code points in the article Markdown',
        'participants': [{'id': k, **v} for k, v in participants.items()],
        'versions': [{'n': n, 'author': e['author'], 'role': e['role'], 'label': e.get('label', '')}
                     for n, e in enumerate(entries)],
        'totals': totals,
        'spans': spans,
    }


# ---------------------------------------------------------------- inputs
def slug(s):
    return re.sub(r'[^a-z0-9.]+', '-', s.lower()).strip('-')


def from_git(repo, file):
    """Versions from the history of one file, oldest first (conventions: docs/WRITING.md)."""
    fmt = '%x1e%H%x1f%an%x1f%ae%x1f%s%x1f%(trailers:key=Contribution,valueonly,separator=%x2c)%x1f'
    log = subprocess.run(['git', '-C', repo, 'log', '--reverse', '--follow', '--name-only', '--format=' + fmt, '--', file],
                         check=True, capture_output=True, text=True).stdout
    versions, participants = [], {}
    for rec in log.split('\x1e')[1:]:
        sha, name, email, subject, trailer, names = rec.split('\x1f')
        path = [p for p in names.split('\n') if p.strip()][-1]
        show = subprocess.run(['git', '-C', repo, 'show', f'{sha}:{path}'], capture_output=True, text=True)
        if show.returncode:
            continue  # file deleted in this commit
        author = slug(name)
        participants[author] = {'name': name, 'kind': 'ai' if email.endswith('@models.invalid') else 'human'}
        role = 'copyedit' if 'copyedit' in trailer.lower() else 'draft'
        versions.append({'author': author, 'role': role, 'text': show.stdout, 'label': subject, 'commit': sha})
    return {'participants': participants, 'versions': versions}


def cut(text, rule):
    """Keep lines from the first matching `from` line up to (not including) the next `to` line."""
    if not rule:
        return text
    lines = text.split('\n')
    start = next(k for k, l in enumerate(lines) if re.search(rule['from'], l)) if rule.get('from') else 0
    stop = next((k for k in range(start + 1, len(lines)) if re.search(rule['to'], lines[k])), len(lines)) if rule.get('to') else len(lines)
    return '\n'.join(lines[start:stop]).strip('\n') + '\n'


def from_chat(manifest_path):
    """Versions from a captured chat (Codex retrieval JSON) plus a private manifest.

    Every captured message up to the last draft becomes a message entry, in order. The manifest
    marks which items are drafts (with an optional `cut` and author override) and inserts
    attached files as drafts before a given item."""
    man = json.load(open(manifest_path))
    cap = json.load(open(man['capture']))
    assert cap['pages'][-1]['page']['hasMore'] is False, 'capture is incomplete'
    items = [it for t in [t for p in cap['pages'] for t in p['turns']][::-1] for it in t['items']]
    speakers = man['speakers']  # capture item type -> participant id
    drafts = {d['item']: d for d in man['drafts'] if 'item' in d}
    files = {}
    for d in man['drafts']:
        if 'file' in d:
            files.setdefault(d['before_item'], []).append(d)
    last = max(k for k, it in enumerate(items) if it['id'] in drafts)
    versions = []
    for k, it in enumerate(items[:last + 1]):
        for f in files.get(it['id'], []):
            versions.append({'author': f['author'], 'role': 'draft', 'text': open(f['file']).read(), 'label': f.get('label', 'attached draft')})
        text = it.get('text') or '\n'.join(c['text'] for c in it.get('content', []))
        if it['id'] in drafts:
            d = drafts[it['id']]
            versions.append({'author': d.get('author', speakers[it['type']]), 'role': 'draft',
                             'text': cut(text, d.get('cut')), 'label': d.get('label', f'chat item {k}')})
        else:
            versions.append({'author': speakers[it['type']], 'role': 'message', 'text': text, 'label': f'chat item {k}'})
    if man.get('article'):
        article = open(man['article']).read()
        assert versions[-1]['text'].strip() == article.strip(), 'last draft differs from the article'
        versions[-1]['text'] = article
    return {'participants': man['participants'], 'versions': versions}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='source', required=True)
    g = sub.add_parser('git', help='history of one article file in a drafts repo')
    g.add_argument('--repo', required=True)
    g.add_argument('--file', required=True)
    c = sub.add_parser('chat', help='a captured writing chat, via a manifest')
    c.add_argument('manifest')
    v = sub.add_parser('versions', help='a versions JSON file')
    v.add_argument('path')
    for s in (g, c, v):
        s.add_argument('-o', '--out', help='write JSON here (default: stdout)')
        s.add_argument('--small-edits', choices=['authorship', 'copyedit'], default='authorship',
                       help='whether 1-2 word edits count as authorship or as copyedits')
        s.add_argument('--preview', help='also write an HTML page for spot-checking')
    a = p.parse_args(argv)
    data = (from_git(a.repo, a.file) if a.source == 'git' else from_chat(a.manifest) if a.source == 'chat'
            else json.load(open(a.path)))
    result = build(data, a.small_edits, a.source)
    out = json.dumps(result, ensure_ascii=False, indent=1) + '\n'
    if a.out:
        open(a.out, 'w').write(out)
    else:
        sys.stdout.write(out)
    if a.preview:
        from preview import write_preview
        write_preview(data['versions'][-1]['text'], result, a.preview)
    for sec, t in result['totals'].items():
        shares = ', '.join(f"{k} {v['percent']}% ({v['chars']})" for k, v in t['authors'].items())
        edits = ', '.join(f"{k} {v['edits']} edits ({v['chars']} chars)" for k, v in t['copyedits'].items()) or 'none'
        print(f'{sec}: {shares}; copyedits: {edits}', file=sys.stderr)


if __name__ == '__main__':
    main()
