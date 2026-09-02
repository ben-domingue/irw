"""Build a backfilled item text CSV: administered wording kept in the base
fields, English added in the parallel `_translated` fields, `language` named.

Usage:  build_backfill.py <table> <language> <translations.json> [--out DIR]

`translations.json` maps the EXACT administered string to its English
rendering, per field:

    {"item_text": {"<German>": "<English>", ...},
     "option_text": {...}, "instructions": {...}, "section_prompt": {...}}

Rules enforced here rather than left to the caller:

* `item` and `resp` are join keys and are never translated.
* A field whose administered wording was NOT recovered (it already holds
  English) gets an EMPTY `_translated` column, not a copy of itself. Copying
  English into the translated column would assert that the base field is the
  administered wording, which is the thing that is false about those tables.
* Every administered string must be present in the mapping. A missing key is
  an error, not a silently untranslated cell -- a half-translated column is
  worse than an absent one because nothing downstream can tell which is which.
* `NA` is treated as empty, matching how these CSVs were written.
"""
import csv, io, json, os, sys, unicodedata

FIELDS = ('instructions', 'section_prompt', 'item_text', 'option_text')
ORDER = ['table', 'section_id', 'item', 'instrument', 'language',
         'instructions', 'section_prompt', 'item_text', 'correct_response',
         'option_text', 'resp',
         'instructions_translated', 'section_prompt_translated',
         'item_text_translated', 'option_text_translated']


def blank(v):
    return (v or '').strip() in ('', 'NA')


def key(v):
    """Lookup key for a source string.

    Published tables are NOT consistently normalised: the sv-maia2_* Serbian
    tables store decomposed (NFD) Unicode -- "c" plus a combining caron
    U+030C -- where a hand-written mapping naturally uses precomposed NFC
    U+010D. The two render identically and compare unequal, so matching is done
    on NFC-normalised text.

    Only the LOOKUP is normalised. The base field is written back byte for byte
    as published, because the whole claim of the base column is that it is what
    the table already serves.
    """
    return unicodedata.normalize('NFC', (v or '').strip())


def build(table, language, tmap, src_dir, out_dir):
    src = os.path.join(src_dir, table + '.csv')
    rows = list(csv.DictReader(io.open(src, encoding='utf-8')))
    if not rows:
        raise SystemExit(f'{table}: source is empty')

    missing = {}
    for f in FIELDS:
        if f not in rows[0]:
            continue
        m = {key(k): val for k, val in tmap.get(f, {}).items()}
        for r in rows:
            v = (r.get(f) or '').strip()
            if blank(v) or not m:
                continue
            if key(v) not in m:
                missing.setdefault(f, set()).add(v)
    if missing:
        for f, vs in missing.items():
            print(f'{table}: {len(vs)} untranslated in {f}:', file=sys.stderr)
            for v in sorted(vs)[:10]:
                print('   ', v[:100], file=sys.stderr)
        raise SystemExit(f'{table}: refusing to write a half-translated table')

    out = []
    for r in rows:
        o = {k: r.get(k, '') for k in ORDER if k in r}
        o['language'] = language
        for f in FIELDS:
            tcol = f + '_translated'
            m = {key(k): val for k, val in tmap.get(f, {}).items()}
            v = (r.get(f) or '').strip()
            o[tcol] = '' if (blank(v) or not m) else m[key(v)]
        out.append({k: o.get(k, '') for k in ORDER})

    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, table + '.csv')
    w = csv.DictWriter(io.open(dst, 'w', encoding='utf-8', newline=''),
                       fieldnames=ORDER, quoting=csv.QUOTE_ALL)
    w.writeheader()
    w.writerows(out)
    filled = [f for f in FIELDS if tmap.get(f)]
    print(f'{table}: {len(out)} rows, language={language}, translated: {", ".join(filled)}')
    return dst


if __name__ == '__main__':
    a = sys.argv[1:]
    out_dir = 'itemtext/language_backfill/staged'
    if '--out' in a:
        i = a.index('--out'); out_dir = a[i + 1]; a = a[:i] + a[i + 2:]
    table, language, tfile = a[0], a[1], a[2]
    build(table, language, json.load(io.open(tfile, encoding='utf-8')),
          os.environ.get('ITBF_SRC', '/tmp/claude-1000/itbf/text'), out_dir)
