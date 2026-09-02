"""Classify each text field of a published IRW item text table as administered
wording or English.

Positive evidence only. Two rules can PROVE a field is not English:

  1. a non-Latin script (CJK, Kana, Hangul, Cyrillic, Arabic, Devanagari,
     Hebrew, Greek, Thai);
  2. Latin script carrying more than three non-ASCII letters (diacritics).

Everything else is NEEDS_REVIEW. Nothing is ever called non-English on the
absence of English.

Two rejected heuristics, both of which produced confident wrong answers:

  * "few English function words => non-English" fires on word-list
    instruments. `amarilla_2020_barthel` ("Bathing", "Bladder", "Grooming"),
    `geography` ("Lusaka (city)"), `gilbert_meta_40` ("Add: 4 + 1") are all
    English and all score zero. It invented 21 non-English tables.
  * The same rule on short option labels ("Never", "A little") invented 45
    false mixed-language tables before that.

Both failures share a cause: English prose is only one of the shapes English
item text takes, so a test tuned to prose reads every other shape as foreign.
"""
import csv, io, os, re, sys, collections, unicodedata

TXT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-1000/itbf/text'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/claude-1000/itbf/verdict_strict.csv'
SCRIPTS = [('CJK', r'[一-鿿]'), ('Hangul', r'[가-힯]'),
           ('Kana', r'[぀-ヿ]'), ('Cyrillic', r'[Ѐ-ӿ]'),
           ('Arabic', r'[؀-ۿ]'), ('Devanagari', r'[ऀ-ॿ]'),
           ('Hebrew', r'[֐-׿]'), ('Greek', r'[Ͱ-Ͽ]'),
           ('Thai', r'[฀-๿]')]
FIELDS = ('item_text', 'option_text', 'instructions', 'section_prompt')


def judge(t):
    """(verdict, script) for one field's concatenated text."""
    t = re.sub(r'\bNA\b', '', t or '').strip()
    if not t:
        return 'blank', ''
    sc = [n for n, p in SCRIPTS if len(re.findall(p, t)) > 2]
    if sc:
        return 'ADMIN', ';'.join(sc)
    dia = len([c for c in t if ord(c) > 127 and unicodedata.category(c).startswith('L')])
    if dia > 3:
        return 'ADMIN', 'latin-diacritic'
    return 'NEEDS_REVIEW', ''


def main():
    rows = []
    for fn in sorted(os.listdir(TXT)):
        if not fn.endswith('.csv'):
            continue
        tb = fn[:-4]
        d = list(csv.DictReader(io.open(os.path.join(TXT, fn), encoding='utf-8')))
        if not d:
            rows.append([tb, 'EMPTY'] + ['-'] * 4 + ['']); continue
        per, scr = {}, set()
        for c in FIELDS:
            if c not in d[0]:
                per[c] = 'missing'; continue
            v, s = judge(' '.join((r.get(c) or '') for r in d))
            per[c] = v
            if s and s != 'latin-diacritic':
                scr.add(s)
        verdict = 'HAS_ADMIN_TEXT' if 'ADMIN' in per.values() else 'NEEDS_REVIEW'
        rows.append([tb, verdict] + [per[c] for c in FIELDS] + [';'.join(sorted(scr))])
    w = csv.writer(io.open(OUT, 'w', encoding='utf-8', newline=''))
    w.writerow(['table', 'verdict'] + list(FIELDS) + ['scripts'])
    w.writerows(rows)
    for k, v in collections.Counter(r[1] for r in rows).most_common():
        print('  %-16s %d' % (k, v))
    print('total', len(rows))


if __name__ == '__main__':
    main()
