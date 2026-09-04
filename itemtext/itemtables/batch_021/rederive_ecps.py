#!/usr/bin/env python3
"""rederive_ecps.py -- batch_021, issue #1831

Rebuilds the shipped text for the eight ecps_sahm_2024_* tables from the
administered COVIDiSTRESS Round II instrument and writes rederived_ecps.json,
so verify_ecps_sahm_2024_*.R diffs against a rebuild of the source rather than
against a prose claim.

The instrument itself lives in ecps_source.py, which also documents why it is
written out rather than parsed. This script re-establishes three things rather
than asserting them:

1. Every stem, item and ladder label still occurs in one of the two sources --
   `Copy of survey.pdf` (the administered Qualtrics form) or the two
   registration workbooks -- and reports which.

2. The _0neutral decode. The cleaned data file carries each of these items
   twice, as *_0neutral and *_midneutral, and IRW uses the _0neutral copy.
   Cross-tabulating the pair recovers the scale exactly: the midpoint is pulled
   out to 0 and the six named anchors stay at 1-6. Re-run here per item, so a
   changed export cannot silently invalidate the labels.

3. The source tie. Every shipped item code is a column of
   Final_COVIDiSTRESS_Vol2_cleaned.csv, which is what connects these tables to
   this questionnaire at all -- their dictionary rows named the wrong study
   until 2026-09-04 (see provenance.csv).

Reads   .cache/ecps_sahm_2024/{survey.pdf or survey_pages.json, blocks.json,
                               covidistress_vol2.csv}
Writes  itemtables/batch_021/rederived_ecps.json
Run from itemtext/:  python3 itemtables/batch_021/rederive_ecps.py
"""
import csv, importlib.util, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ecps_source",
                                              os.path.join(HERE, "ecps_source.py"))
src = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src)

CACHE = src.CACHE
OUT = os.path.join(HERE, "rederived_ecps.json")


def _num(v):
    """Numeric value, or None for the file's NA / blank cells."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def neutral_decode(csv_path):
    """Cross-tabulate each *_0neutral item against its *_midneutral twin."""
    if not os.path.exists(csv_path):
        return {"note": "cleaned data file not cached; decode not re-run"}
    with open(csv_path, encoding="utf-8", errors="ignore") as f:
        rdr = csv.reader(f)
        hdr = next(rdr)
        idx = {h: i for i, h in enumerate(hdr)}
        pairs = [(h, h.replace("_0neutral", "_midneutral")) for h in hdr
                 if h.endswith("_0neutral")]
        pairs = [(a, b) for a, b in pairs if b in idx]
        seen = {a: defaultdict(set) for a, _ in pairs}
        for row in rdr:
            for a, b in pairs:
                x, y = row[idx[a]].strip(), row[idx[b]].strip()
                if _num(x) is not None and _num(y) is not None:
                    seen[a][x].add(y)
    sigs = defaultdict(list)
    for a, _ in pairs:
        sig = " ".join("%s->%s" % (k, "/".join(sorted(seen[a][k])))
                       for k in sorted(seen[a], key=_num))
        sigs[sig].append(a)
    return {"items_with_both_codings": len(pairs),
            "distinct_mappings": {k: sorted(v) for k, v in sigs.items()}}


def main():
    v = src.verify()
    if v is None:
        sys.exit("neither the survey PDF nor the workbooks are cached (%s);\n"
                 "the committed rederived_ecps.json stands. Refetch from osf.io/36tsd\n"
                 "-- see provenance.csv source_ref." % CACHE)
    if v["unverified"]:
        sys.exit("%d string(s) verify against neither source:\n%s"
                 % (len(v["unverified"]),
                    "\n".join("  %s / %s / %s / %s" % x for x in v["unverified"][:10])))

    tables = {}
    for short, secs in src.TABLES.items():
        tab = "ecps_sahm_2024_" + short
        entries = {}
        for si, s in enumerate(secs, start=1):
            for code, text in zip(s["codes"], s["items"]):
                entries[code] = {
                    "section_id": "%s_%d" % (tab, si),
                    "instrument": "%s: %s" % (src.STUDY, s["label"]),
                    "section_prompt": s["stem"],
                    "text": text,
                    "ladder": {str(k): val for k, val in s["ladder"].items()},
                }
        tables[tab] = entries

    csv_path = os.path.join(CACHE, "covidistress_vol2.csv")
    colcheck = {}
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8", errors="ignore") as f:
            cols = set(next(csv.reader(f)))
        for tab, entries in tables.items():
            colcheck[tab] = {"items": len(entries),
                             "not_a_column": [c for c in entries if c not in cols]}
    else:
        colcheck = {"note": "cleaned data file not cached; column check skipped"}

    payload = {"tables": tables,
               "string_verification": {"in_survey_pdf": v["pdf"],
                                       "in_workbooks": v["workbook"],
                                       "unverified": 0},
               "neutral_decode": neutral_decode(csv_path),
               "source_column_check": colcheck}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)

    nd = payload["neutral_decode"]
    print("wrote %s: %d tables, %d items" % (OUT, len(tables),
                                             sum(len(x) for x in tables.values())))
    print("  strings verified: %d in the survey PDF, %d in the workbooks, 0 in neither"
          % (v["pdf"], v["workbook"]))
    if "distinct_mappings" in nd:
        print("  _0neutral decode: %d items carry both codings, %d distinct mapping(s)"
              % (nd["items_with_both_codings"], len(nd["distinct_mappings"])))
        for sig, items in sorted(nd["distinct_mappings"].items(),
                                 key=lambda kv: -len(kv[1])):
            print("     n=%-3d %s" % (len(items), sig))


if __name__ == "__main__":
    main()
