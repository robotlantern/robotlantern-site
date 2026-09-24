"""Spot-check page: the article's Markdown source with attributed characters colored.

Syntax and uncounted characters are dimmed. Copyedited characters keep their author's color and
get a dotted underline. Hover shows the version a span came from."""
import html

COLORS = {'human': '#f0a040', 'ai': '#5aa0f0', 'unknown': '#bbbbbb'}


def write_preview(md, result, path):
    kinds = {p['id']: p.get('kind', 'unknown') for p in result['participants']}
    labels = {v['n']: v['label'] for v in result['versions']}
    parts, pos = [], 0
    for s in result['spans']:
        if s['start'] > pos:
            parts.append(f'<span class="x">{html.escape(md[pos:s["start"]])}</span>')
        ce = s.get('copyedit')
        title = f"{s['author']} · from {s['from']}: {labels[s['from']]}"
        if ce:
            title += f" · copyedit by {ce['by']} in {ce['version']}: {labels[ce['version']]}"
        parts.append(f'<span class="{kinds[s["author"]]}{" ce" if ce else ""}" title="{html.escape(title)}">'
                     f'{html.escape(md[s["start"]:s["end"]])}</span>')
        pos = s['end']
    parts.append(f'<span class="x">{html.escape(md[pos:])}</span>')
    rows = ''
    for sec, t in result['totals'].items():
        shares = ', '.join(f"{k} {v['percent']}% ({v['chars']} chars)" for k, v in t['authors'].items())
        edits = ', '.join(f"{k}: {v['edits']} edits, {v['chars']} chars" for k, v in t['copyedits'].items()) or 'none'
        rows += f'<p><b>{sec}</b>: {html.escape(shares)} · copyedits: {html.escape(edits)}</p>'
    page = f'''<!doctype html><meta charset="utf-8"><title>Attribution check</title>
<style>body{{background:#0b1020;color:#ddd;font:16px/1.6 Georgia,serif;max-width:48rem;margin:2rem auto;padding:0 1rem}}
pre{{white-space:pre-wrap;font:inherit}} .x{{color:#556}} .human{{background:{COLORS['human']}33}}
.ai{{background:{COLORS['ai']}33}} .unknown{{background:#8883}} .ce{{text-decoration:underline dotted #fff9}}</style>
{rows}<pre>{''.join(parts)}</pre>'''
    open(path, 'w').write(page)
