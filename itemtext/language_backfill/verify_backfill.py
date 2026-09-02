"""Check every staged backfill CSV against the published table it replaces.

Fails on anything that would corrupt the response join or misrepresent the
administered wording:
  * item / resp sets must be identical to the published table
  * row count identical
  * every base text field byte-identical (the backfill ADDS, never edits)
  * a `_translated` column must be either fully populated or fully empty
  * `language` must be non-empty and identical on every row
"""
import csv, io, os, sys

SRC = os.environ.get('ITBF_SRC', '/tmp/claude-1000/itbf/text')
STAGED = sys.argv[1] if len(sys.argv) > 1 else 'itemtext/language_backfill/staged'
BASE = ('instructions', 'section_prompt', 'item_text', 'option_text')
ok = bad = 0
for fn in sorted(os.listdir(STAGED)):
    if not fn.endswith('.csv'):
        continue
    tb = fn[:-len('__items.csv')] if fn.endswith('__items.csv') else fn[:-4]
    new = list(csv.DictReader(io.open(os.path.join(STAGED, fn), encoding='utf-8')))
    old = list(csv.DictReader(io.open(os.path.join(SRC, tb + '.csv'), encoding='utf-8')))
    errs = []
    if len(new) != len(old):
        errs.append(f'row count {len(new)} != {len(old)}')
    if {r['item'] for r in new} != {r['item'] for r in old}:
        errs.append('item set changed')
    if {r['resp'] for r in new} != {r['resp'] for r in old}:
        errs.append('resp set changed')
    for c in BASE:
        if c in old[0] and [r.get(c) for r in new] != [r.get(c) for r in old]:
            errs.append(f'base field {c} was modified')
    langs = {r['language'] for r in new}
    if len(langs) != 1 or not langs.pop().strip():
        errs.append('language missing or inconsistent')
    for c in BASE:
        t = c + '_translated'
        vals = [(r.get(t) or '').strip() for r in new]
        base = [(r.get(c) or '').strip() for r in new]
        filled = [i for i, v in enumerate(vals) if v]
        wants = [i for i, v in enumerate(base) if v and v != 'NA']
        if filled and set(filled) != set(wants):
            errs.append(f'{t} partially filled ({len(filled)}/{len(wants)})')
    if errs:
        bad += 1
        print(f'FAIL {tb}: ' + '; '.join(errs))
    else:
        ok += 1
        print(f'ok   {tb} ({len(new)} rows, {langs if False else new[0]["language"]})')
print(f'\n{ok} passed, {bad} failed')
sys.exit(1 if bad else 0)
