#!/usr/bin/env python3
"""rederive_haq.py -- batch_021, issue #1831

Re-parses the HAQ block of the PROMIS Wave 1 study codebook and writes
rederived_haq.json, so verify_promis1wave1_haq.R diffs the shipped text
against a rebuild of the source.

HAQ needs its own re-derivation for three reasons:

  - Its codes end in a letter (HAQ1a, HAQ3c), so the all-caps code pattern
    rederive_promis.py uses for the PROMIS banks -- which requires a trailing
    digit -- never matched them.
  - Like CES-D it sits in the legacy-items tables, whose trailing Domain /
    Sub-Domain columns run into the last option label.
  - HAQ9-HAQ12 print their two options in descending key order ("1 = Yes0 =
    No"), unlike the 0-3 difficulty items, so the option run is read as a
    monotone run in either direction rather than an ascending one.

Reads   .cache/promis1wave1/codebook.txt
Writes  itemtables/batch_021/rederived_haq.json
Run from itemtext/:  python3 itemtables/batch_021/rederive_haq.py
"""
import json, os, re, sys

SRC = ".cache/promis1wave1/codebook.txt"
OUT = "itemtables/batch_021/rederived_haq.json"
CODES = ["HAQ%d%s" % (n, s) for n in range(1, 9) for s in ("a", "b", "c")] \
        + ["HAQ%d" % n for n in (9, 10, 11, 12)]
META = re.compile(r'\s+(?:Physical Function|Emotional Distress|Social Role|Fatigue|Pain|Sleep'
                  r'|Global|Legacy Items|APPENDIX)\b.*$')
CODE_ANY = r'HAQ\d{1,2}[a-c]?|[A-Z][A-Z0-9]{2,10}\d'
STEM_START = r'(?=Over the past week|Are you able|To |How )'

def parse_opts(blob):
    """Options as a monotone key run; stops where the run breaks (next scale)."""
    pairs = []
    for chunk in re.split(r'(?=\d{1,2} ?= ?)', blob):
        m = re.match(r'^(\d{1,2}) ?= ?(.+)$', chunk.strip())
        if m and m.group(2).strip():
            pairs.append((int(m.group(1)), META.sub('', m.group(2).strip()).strip()))
    if not pairs:
        return {}
    step, out = None, {str(pairs[0][0]): pairs[0][1]}
    for i in range(1, len(pairs)):
        d = pairs[i][0] - pairs[i-1][0]
        if step is None:
            if d not in (1, -1):
                break
            step = d
        elif d != step:
            break
        out[str(pairs[i][0])] = pairs[i][1]
    return out

def main():
    if not os.path.exists(SRC):
        sys.exit("cached codebook absent (%s); the committed rederived_haq.json stands.\n"
                 "The deposit's download is guestbook-gated -- see provenance.csv source_ref." % SRC)
    t = re.sub(r'\s+', ' ', open(SRC, encoding="utf-8").read())
    out = {}
    for code in CODES:
        m = re.search(r'\b' + code + r'\s+' + STEM_START, t)
        if not m:
            continue
        seg = t[m.end(): m.end() + 700]
        seg = re.split(r'\s+(?:' + CODE_ANY + r')\s+' + STEM_START, seg)[0]
        om = re.search(r'\d{1,2} ?= ?', seg)
        if not om:
            continue
        mid, blob = seg[:om.start()].strip(), seg[om.start():]
        ctx = ""
        cm = re.match(r'^(Over the past week)\s+(.*)$', mid)
        if cm:
            ctx, mid = cm.group(1), cm.group(2).strip()
        out[code] = {"context": ctx, "stem": mid, "opts": parse_opts(blob)}
    thin = {c: sorted(v["opts"]) for c, v in out.items() if len(v["opts"]) < 2}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"items": out}, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote %s: %d HAQ items; option-set sizes %s; items with <2 options: %s"
          % (OUT, len(out), sorted({len(v["opts"]) for v in out.values()}), thin or "none"))

if __name__ == "__main__":
    main()
