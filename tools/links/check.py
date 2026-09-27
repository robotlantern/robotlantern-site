"""Check a post's links.json (docs/LINKS.md, step 2).

Each Wikipedia URL must resolve to an article, not a disambiguation page. A redirect is
reported so an agent can confirm it lands on the same topic. The canonical title and the
article's short description are written back into links.json. Other URLs must answer 200.

    python3 tools/links/check.py src/content/conversations/<slug>/links.json
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = 'RobotLanternLinkCheck/1.0 (https://robotlantern.com)'


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.geturl(), r.read()


def check_wiki(link):
    title = urllib.parse.unquote(link['url'].split('/wiki/', 1)[1])
    api = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(title, safe='')
    _, _, body = fetch(api)
    page = json.loads(body)
    problems = []
    if page.get('type') == 'disambiguation':
        problems.append('disambiguation page')
    canonical = page['titles']['canonical']
    if canonical.replace('_', ' ') != title.replace('_', ' '):
        problems.append(f'redirects to "{page["titles"]["normalized"]}"')
    link['url'] = 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(canonical, safe='()_,\'–-')
    link['title'] = page['titles']['normalized']
    link['description'] = page.get('description', '')
    return problems


def main(path):
    links = json.load(open(path))
    failed = 0
    for link in links:
        try:
            if '://en.wikipedia.org/wiki/' in link['url']:
                problems = check_wiki(link)
            else:
                status, _, _ = fetch(link['url'])
                problems = [] if status == 200 else [f'HTTP {status}']
                link['title'] = link.get('title', link['url'])
        except urllib.error.HTTPError as e:
            problems = [f'HTTP {e.code}']
        except Exception as e:  # network trouble is a failure, not a pass
            problems = [f'{type(e).__name__}: {e}']
        fatal = [p for p in problems if not p.startswith('redirects')]
        failed += bool(fatal)
        mark = 'FAIL' if fatal else ('note' if problems else 'ok  ')
        print(f'{mark} {link["text"]!r} -> {link.get("title", link["url"])}' + (f'  [{"; ".join(problems)}]' if problems else ''))
    with open(path, 'w') as f:
        json.dump(links, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'{len(links)} links, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
