"""python3 -m unittest discover tools/attribution"""
import os, subprocess, tempfile, unittest
from attribution import TEXT, build, from_git, project


def owners(result, md):
    """Text of each span, prefixed with its author initial; copyedits get a '*'."""
    return [(s['author'][0] + ('*' if 'copyedit' in s else ''), md[s['start']:s['end']]) for s in result['spans']]


def run(*versions, small_edits='authorship'):
    entries = [{'author': a, 'role': r, 'text': t} for a, r, t in versions]
    return build({'versions': entries}, small_edits)


class Projection(unittest.TestCase):
    def visible(self, md):
        kind, _ = project(md)
        return ''.join(c for c, k in zip(md, kind) if k == TEXT)

    def test_syntax_is_not_counted(self):
        md = '# Title\n\nSee [the *demon*](https://x.org/a_b) and `code`.<sup id="r">[1](#fn-1)</sup> [↩](#ref-1)'
        self.assertEqual(self.visible(md), 'TitleSee the demon and . ')

    def test_footnotes_section(self):
        md = 'Body.\n\n## Footnotes\n\n**[1]** Note.'
        kind, section = project(md)
        self.assertEqual(section[0], 'body')
        self.assertEqual(section[md.index('Note')], 'footnotes')
        md = 'Body.[^1]\n\n[^1]: Note.'
        self.assertEqual(self.visible(md), 'Body.Note.')
        self.assertEqual(project(md)[1][md.index('Note')], 'footnotes')

    def test_intraword_underscore_is_text(self):
        self.assertEqual(self.visible('snake_case and _emphasis_'), 'snake_case and emphasis')


class Chain(unittest.TestCase):
    def test_unchanged_text_keeps_first_author(self):
        r = run(('rj', 'draft', 'The cat sat on the mat.'),
                ('gpt', 'draft', 'The cat sat on the mat. It purred loudly all night.'))
        self.assertEqual(owners(r, 'The cat sat on the mat. It purred loudly all night.'),
                         [('r', 'The cat sat on the mat.'), ('g', ' It purred loudly all night.')])

    def test_mechanical_edits_are_copyedits(self):
        final = 'Descartes’s demon, it’s colour.'
        r = run(('rj', 'draft', "descartes' demon its color."), ('gpt', 'draft', final))
        self.assertEqual({a for a, _ in owners(r, final)}, {'r', 'r*'})
        self.assertEqual(r['totals']['body']['authors'], {'rj': {'chars': len(final), 'percent': 100}})
        self.assertIn('gpt', r['totals']['body']['copyedits'])

    def test_rewrite_is_authorship_without_confetti(self):
        final = 'I slew the demon with a better argument about equivalence.'
        r = run(('rj', 'draft', 'I slew the demon with another weapon: it just does not matter.'),
                ('gpt', 'draft', final))
        # the closing period survives from RJ's sentence
        self.assertEqual(owners(r, final), [('r', 'I slew the demon with '), ('g', 'a better argument about equivalence'), ('r', '.')])

    def test_small_edit_policy(self):
        final = 'The cat sat quietly on the mat.'
        self.assertIn(('g', ' quietly'), owners(run(('rj', 'draft', 'The cat sat on the mat.'), ('gpt', 'draft', final)), final))
        r = run(('rj', 'draft', 'The cat sat on the mat.'), ('gpt', 'draft', final), small_edits='copyedit')
        self.assertEqual(set(r['totals']['body']['authors']), {'rj'})

    def test_copyedit_role_keeps_everything(self):
        final = 'A dog stood beside the rug.'
        r = run(('rj', 'draft', 'The cat sat on the mat.'), ('gpt', 'copyedit', final))
        self.assertEqual(set(r['totals']['body']['authors']), {'rj'})

    def test_text_pasted_from_a_message(self):
        suggestion = 'maybe the demon is just a very patient landlord'
        final = f'I think {suggestion}. Anyway.'
        r = run(('rj', 'draft', 'I think. Anyway.'), ('gpt', 'message', f'How about: "{suggestion}"?'),
                ('rj', 'draft', final))
        self.assertIn(('g', suggestion), owners(r, final))

    def test_body_and_footnotes_reported_separately(self):
        final = 'Body text here.\n\n## Footnotes\n\n**[1]** A long note by the model.'
        r = run(('rj', 'draft', 'Body text here.'), ('gpt', 'draft', final))
        self.assertEqual(set(r['totals']['body']['authors']), {'rj'})
        self.assertEqual(set(r['totals']['footnotes']['authors']), {'gpt'})


class Git(unittest.TestCase):
    def test_history_with_copyedit_trailer(self):
        with tempfile.TemporaryDirectory() as repo:
            env = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}

            def commit(text, author, message):
                os.makedirs(f'{repo}/essay', exist_ok=True)
                with open(f'{repo}/essay/article.md', 'w') as f:
                    f.write(text)
                subprocess.run(['git', '-C', repo, 'add', '.'], check=True, env=env)
                subprocess.run(['git', '-C', repo, '-c', 'user.name=x', '-c', 'user.email=x@x', 'commit', '-q',
                                f'--author={author}', '-m', message], check=True, env=env)

            subprocess.run(['git', 'init', '-q', repo], check=True, env=env)
            commit('The cat sat on the mat.\n', 'RJ Carroll <rj@example.com>', 'First draft')
            commit('The cat sat on the mat. It purred all night long.\n',
                   'GPT-5.6-sol <gpt-5.6-sol@models.invalid>', 'Add a sentence')
            commit('The cat sat on the rug. It purred all night long.\n',
                   'GPT-5.6-sol <gpt-5.6-sol@models.invalid>', 'Fix wording\n\nContribution: copyedit')
            data = from_git(repo, 'essay/article.md')
            self.assertEqual([v['role'] for v in data['versions']], ['draft', 'draft', 'copyedit'])
            self.assertEqual(data['participants']['gpt-5.6-sol']['kind'], 'ai')
            r = build(data, source_kind='git')
            final = 'The cat sat on the rug. It purred all night long.\n'
            self.assertEqual(owners(r, final),
                             [('r', 'The cat sat on the '), ('r*', 'rug'), ('r', '.'), ('g', ' It purred all night long.')])


if __name__ == '__main__':
    unittest.main()
