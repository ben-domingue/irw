"""Check every staged backfill CSV against the published table it replaces.

Fails on anything that would corrupt the response join or misrepresent the
administered wording:
  * item / resp sets must be identical to the published table
  * row count identical
  * a `_translated` column must be either fully populated or fully empty
  * `language` must be non-empty and identical on every row

**Two modes, because the backfill has two contracts.** Both were run on 2026-09-01,
in parallel, and only one of them was ever encoded here:

  add     (default) the published base fields ALREADY hold the administered wording,
          so the backfill only adds columns and every base field must stay
          byte-identical. This is tier A: 78 tables.
  recover the published base fields hold ENGLISH, and the administered wording has
          been recovered from the paper, so `item_text` (and sometimes
          `instructions`) legitimately CHANGES and the English moves to the
          `_translated` twin. This is what the three tier B/C tables in `staging/`
          did. A changed base field is reported rather than failed, and the check
          that matters instead is that the item/resp join keys did not move.

Set with ITBF_MODE, e.g. `ITBF_MODE=recover python3 verify_backfill.py staging`.
"""
import csv, io, os, sys

# The published copies this checks against live beside the script, so the check is
# re-runnable by anyone who clones the repo. It used to default into a /tmp scratch
# directory that stopped existing the moment the session ended (#1811).
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('ITBF_SRC') or os.path.join(HERE, 'published')
STAGED = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'staged')
if not os.path.isdir(SRC):
    sys.exit(f"no published copies at {SRC}\n"
             f"run fetch_published_itemtext.R first, or set ITBF_SRC")
if not os.path.isdir(STAGED):
    sys.exit(f"no staged directory at {STAGED}")
BASE = ('instructions', 'section_prompt', 'item_text', 'option_text')
MODE = os.environ.get('ITBF_MODE', 'add')

# A `_translated` column is normally all-or-nothing: a half-filled one means a
# translation was dropped. These tables are the documented exception, where the
# study itself published wording for only some of its items, so the gap is the
# truth about the source rather than a hole in the work. Reason required.
PARTIAL_OK = {
    ('arzamoncunill_2023_epq_clinical', 'item_text_translated'):
        'The study ran a 43-item pretest pool but published full wording, in Spanish, '
        'only for the items kept in its final questionnaire. The 12 that survived carry '
        'their administered Spanish; the other 10 keep the English category descriptor '
        'from Appendix S5 with an empty twin. See provenance.csv and irw#1777.',
}
if MODE not in ('add', 'recover'):
    sys.exit(f"ITBF_MODE must be 'add' or 'recover', not {MODE!r}")


def blank(v):
    """The two efforts wrote empties differently: '' from Python, 'NA' from R."""
    return (v or '').strip() in ('', 'NA')

ok = bad = 0
for fn in sorted(os.listdir(STAGED)):
    if not fn.endswith('.csv'):
        continue
    tb = fn[:-len('__items.csv')] if fn.endswith('__items.csv') else fn[:-4]
    new = list(csv.DictReader(io.open(os.path.join(STAGED, fn), encoding='utf-8')))
    # two naming conventions reached this directory from two parallel efforts:
    # <table>.csv (the tier A bulk) and <table>__published.csv (the recovered-wording three)
    for cand in (tb + '.csv', tb + '__published.csv'):
        src = os.path.join(SRC, cand)
        if os.path.exists(src):
            break
    else:
        print(f'FAIL {tb}: no published copy in {SRC}')
        bad += 1
        continue
    old = list(csv.DictReader(io.open(src, encoding='utf-8')))
    errs = []
    notes = []
    if len(new) != len(old):
        errs.append(f'row count {len(new)} != {len(old)}')
    if {r['item'] for r in new} != {r['item'] for r in old}:
        errs.append('item set changed')
    if {r['resp'] for r in new} != {r['resp'] for r in old}:
        errs.append('resp set changed')
    for c in BASE:
        if c in old[0] and [r.get(c) for r in new] != [r.get(c) for r in old]:
            if MODE == 'add':
                errs.append(f'base field {c} was modified')
            else:
                notes.append(f'base field {c} rewritten to the administered wording')
    langs = {r['language'] for r in new}
    if len(langs) != 1 or not langs.pop().strip():
        errs.append('language missing or inconsistent')
    for c in BASE:
        t = c + '_translated'
        filled = [i for i, r in enumerate(new) if not blank(r.get(t))]
        wants = [i for i, r in enumerate(new) if not blank(r.get(c))]
        if filled and set(filled) != set(wants):
            if (tb, t) in PARTIAL_OK:
                notes.append(f'{t} partial by design ({len(filled)}/{len(wants)})')
            else:
                errs.append(f'{t} partially filled ({len(filled)}/{len(wants)})')
    if errs:
        bad += 1
        print(f'FAIL {tb}: ' + '; '.join(errs))
    else:
        ok += 1
        tail = ('; ' + '; '.join(notes)) if notes else ''
        print(f'ok   {tb} ({len(new)} rows, {new[0]["language"]}){tail}')
print(f'\n{ok} passed, {bad} failed')
sys.exit(1 if bad else 0)
