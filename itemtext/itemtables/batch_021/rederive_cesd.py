#!/usr/bin/env python3
"""rederive_cesd.py -- batch_021, issue #1831

Re-parses the CES-D block of the PROMIS Wave 1 study codebook and writes
rederived_cesd.json, so verify_promis1wave1_cesd.R diffs the shipped text
against a rebuild of the source.

CES-D sits in the codebook's legacy-items tables, whose layout differs from
the PROMIS bank sections handled by rederive_promis.py: each row repeats an
instruction sentence before the stem, and trailing Domain / Sub-Domain columns
run into the option text. Two traps this handles explicitly:

  - "CESD16" also appears in the scoring appendix ("CESD16 need to be
    recoded"), so rows are anchored on the code followed by the instruction
    sentence, not on the code alone.
  - The block's last row (CESD20) is not followed by another CESD code, so its
    option run continues into the next scale. Options are therefore read only
    while the keys ascend by one, which stops at the boundary.

Reads   .cache/promis1wave1/codebook.txt
Writes  itemtables/batch_021/rederived_cesd.json
Run from itemtext/:  python3 itemtables/batch_021/rederive_cesd.py
"""
import json, os, re, sys

SRC   = ".cache/promis1wave1/codebook.txt"
OUT   = "itemtables/batch_021/rederived_cesd.json"
INSTR = ("Select the statement which best describes how often you felt or behaved this way "
         "during the past week.")


# The legacy tables carry Domain / Sub-Domain columns after Responses, so the
# last option label on a row absorbs them (and sometimes the next form's
# header). None of these phrases occur inside a CES-D response label.
META = re.compile(r'\s+(?:Emotional Distress|Physical Function|Social Role|Fatigue|Pain|Sleep'
                  r'|Global|Legacy Items|APPENDIX)\b.*$')
def strip_trailing_meta(s):
    return META.sub('', s).strip()

def main():
    if not os.path.exists(SRC):
        sys.exit("cached codebook absent (%s); the committed rederived_cesd.json stands.\n"
                 "The deposit's download is guestbook-gated -- see provenance.csv source_ref." % SRC)
    t = re.sub(r'\s+', ' ', open(SRC, encoding="utf-8").read())
    anchors = [(m.start(), int(m.group(1)))
               for m in re.finditer(r'\bCESD(\d{1,2})\s+' + re.escape(INSTR), t)]
    if not anchors:
        sys.exit("no CES-D item rows found in the codebook")
    ends = [a[0] for a in anchors[1:]] + [None]
    out = {}
    for (pos, num), end in zip(anchors, ends):
        seg = (t[pos:end] if end else t[pos:pos + 1500])
        seg = re.sub(r'^\bCESD\d{1,2}\s+' + re.escape(INSTR), '', seg).strip()
        om = re.search(r'\d{1,2} ?= ?', seg)
        if not om:
            continue
        stem, blob = seg[:om.start()].strip(), seg[om.start():]
        opts, expect = {}, None
        for chunk in re.split(r'(?=\d{1,2} ?= ?)', blob):
            mm = re.match(r'^(\d{1,2}) ?= ?(.+)$', chunk.strip())
            if not mm or not mm.group(2).strip():
                continue
            k = int(mm.group(1))
            if expect is not None and k != expect:
                break                      # key run broke: past this row's options
            opts[str(k)] = strip_trailing_meta(mm.group(2).strip())
            expect = k + 1
        out["CESD%d" % num] = {"instructions": INSTR, "stem": stem, "opts": opts}

    # The CES-D uses one response set for all its items; require that, so a row
    # whose options bled in from a neighbouring scale cannot pass silently.
    sets = {}
    for v in out.values():
        sets.setdefault(json.dumps(v["opts"], sort_keys=True), 0)
        sets[json.dumps(v["opts"], sort_keys=True)] += 1
    canon, n = max(sets.items(), key=lambda kv: kv[1])
    odd = [c for c, v in out.items() if json.dumps(v["opts"], sort_keys=True) != canon]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"items": out, "shared_option_set": json.loads(canon),
                   "items_sharing_it": n, "items_not_sharing_it": odd},
                  f, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote %s: %d CES-D items; %d share the one option set; deviating: %s"
          % (OUT, len(out), n, odd or "none"))

if __name__ == "__main__":
    main()
