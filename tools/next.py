"""What's next on the road to launch (NOW.md): RJ's open steps, in order, and what the agents
are on. Check a step off in NOW.md by changing its [ ] to [x].

    python3 tools/next.py          # RJ's next steps
    python3 tools/next.py --all    # every open step
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = ROOT.joinpath('NOW.md').read_text()
road = text.split('## Road to launch', 1)[1].split('### Not needed for launch', 1)[0]
steps = re.findall(r'^(\d+)\. \[( |x)\] \*\*(RJ|Agent)\*\* · (.+?)(?=^\d+\. \[|^###|\Z)', road, re.M | re.S)
finished = {n for n, done, _, _ in steps if done == 'x'}
open_ = []
for n, done, who, body in steps:
    if done == 'x':
        continue
    body = ' '.join(body.split())
    m = re.match(r'After ([\d, and]+): ', body)
    waits = [d for d in re.findall(r'\d+', m.group(1))] if m else []
    if m:
        body = body[m.end():]
    open_.append((n, who, body, [d for d in waits if d not in finished]))
show_all = '--all' in sys.argv

print(f'Road to launch: {len(finished)} of {len(steps)} steps done.')
ready = [s for s in open_ if not s[3] and (show_all or s[1] == 'RJ')]
later = [s for s in open_ if s[3] and (show_all or s[1] == 'RJ')]
print('\nReady now:' if ready else '\nNothing ready for RJ right now.')
for n, who, body, _ in ready:
    print(f'{n:>4}. {who + " · " if show_all else ""}{body}')
if later:
    print('\nLater:')
    for n, who, body, waits in later:
        print(f'{n:>4}. {who + " · " if show_all else ""}{body.split(". ")[0].rstrip(".")}  (waits for {", ".join(waits)})')
if not show_all:
    agent = [n for n, who, _, w in open_ if who == 'Agent' and not w]
    print(f'\nAgent steps ready: {", ".join(agent) or "none"}  (python3 tools/next.py --all)')
