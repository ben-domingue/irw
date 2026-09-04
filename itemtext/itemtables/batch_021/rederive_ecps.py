#!/usr/bin/env python3
"""rederive_ecps.py -- batch_021, issue #1831

Re-reads the COVIDiSTRESS Global Survey Round II questionnaire from the two
OSF workbooks and rebuilds the item text for the five shipped
ecps_sahm_2024_* tables, so verify_ecps_common.R diffs the shipped text
against a rebuild of the source rather than against a prose claim.

Two things it re-establishes rather than asserts:

1. The wording cross-check. `Measured Variables.xlsx` (registration files of
   osf.io/36tsd) and `MainStudy_CriticalMeasures.xlsx` (osf.io/vxuf4) are two
   separate documents. Where a scale appears in both, their item wording is
   compared line by line, which is a second route on the wording for the
   scales that have one.
2. The source. These tables' IRW dictionary rows attribute them to the Sahm
   ERQ-S study, which is wrong -- see provenance.csv. The data file is
   COVIDiSTRESS Vol 2, and the check that ties the tables to this
   questionnaire is that every shipped item code is a column of
   Final_COVIDiSTRESS_Vol2_cleaned.csv. That is re-run here when the cached
   CSV is present.

Reads   .cache/ecps_sahm_2024/{measured_variables.xlsx,
                               main_critical_measures.xlsx,
                               covidistress_vol2.csv}
Writes  itemtables/batch_021/rederived_ecps.json
Run from itemtext/:  python3 itemtables/batch_021/rederive_ecps.py
"""
import csv, json, os, re, sys, warnings
warnings.filterwarnings("ignore")

CACHE = ".cache/ecps_sahm_2024"
OUT   = "itemtables/batch_021/rederived_ecps.json"
STUDY = "COVIDiSTRESS Global Survey Round II"

def blocks_of(path):
    import openpyxl
    ws   = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr  = [str(c).strip() if c else "" for c in rows[0]]
    i_id, i_q = hdr.index("ID"), hdr.index("Question")
    idr = [(n, str(rows[n][i_id]).strip()) for n in range(1, len(rows))
           if rows[n][i_id] and str(rows[n][i_id]).strip()]
    out = {}
    for k, (n, name) in enumerate(idr):
        end = idr[k+1][0] if k+1 < len(idr) else len(rows)
        lines = []
        for m in range(n, end):
            q = rows[m][i_q]
            if q:
                for p in str(q).split("\n"):
                    if p.strip():
                        lines.append(p.strip())
        out[name] = lines
    return out

def clean(s):
    s = s.replace("\xa0", " ")
    s = re.sub(r'^\s*(?:-\s*|B\.\d+\.\d+\s+)', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def norm(s):
    s = clean(s).replace("’", "'")
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', s.lower())).strip()

# (section label, block, leading stem lines to skip, stem line index, code builder)
SPEC = {
 "ia": [("Information acquisition", "[information_acquisition]", 2, 1,
         lambda k: "information_acquisit_%d" % (k+1))],
 "distrust": [
   ("COVID-19 misperceptions", "[misperception]", 1, 0,
    lambda k: "misperception%d_%d" % (k // 2 + 1, k % 2 + 1)),
   ("Conspiratorial thinking", "[conspirational_thinking]", 0, None,
    lambda k: "conspirational_think_%d" % (k+1)),
   ("Anti-expert sentiment", "[antiexpert]", 0, None,
    lambda k: "antiexpert_%d" % (k+1))],
 "identity": [("Group identification", "[identity]", 1, 0,
               lambda k: "identity_%d_0neutral" % (k+1))],
 "moral": [("Moral values", "[moral values]", 2, 1,
            lambda k: "moral.values_%d_0neutral" % (k+1))],
 "sscd": [
   ("Compliance with COVID-19 guidelines", "compliance", 1, 0,
    lambda k: "compliance_%d" % (k+1)),
   ("Social influence: injunctive norms", "socialinfluence_norms", 1, 0,
    lambda k: "socialinfluence_nor1_%d" % (k+1)),
   ("Social influence: descriptive norms", "socialinfluence_norms", 1, 0,
    lambda k: "socialinfluence_nor2_%d" % (k+1))],
}

def main():
    reg_p = os.path.join(CACHE, "measured_variables.xlsx")
    if not os.path.exists(reg_p):
        sys.exit("cached questionnaire absent (%s); the committed rederived_ecps.json stands.\n"
                 "Refetch from osf.io/36tsd -- see provenance.csv source_ref." % reg_p)
    reg = blocks_of(reg_p)
    fin_p = os.path.join(CACHE, "main_critical_measures.xlsx")
    fin = blocks_of(fin_p) if os.path.exists(fin_p) else {}

    tables = {}
    for short, sections in SPEC.items():
        tab, si, entries = "ecps_sahm_2024_" + short, 0, {}
        for label, key, skip, stem_ix, code in sections:
            si += 1
            its = [clean(l) for l in reg[key][skip:]]
            if key == "socialinfluence_norms":
                if "injunctive" in label:
                    its, stem = its[:8], clean(reg[key][0])
                else:
                    its, stem = its[9:17], clean(reg[key][9])
            else:
                stem = clean(reg[key][stem_ix]) if stem_ix is not None else ""
            for k, txt in enumerate(its):
                entries[code(k)] = {"section_id": "%s_%d" % (tab, si),
                                    "instrument": "%s: %s" % (STUDY, label),
                                    "section_prompt": stem, "text": txt}
        tables[tab] = entries

    # cross-document wording agreement, per block
    cross = {}
    for key in sorted({s[1] for v in SPEC.values() for s in v}):
        a = [norm(x) for x in reg.get(key, [])]
        b = [norm(x) for x in fin.get(key, [])]
        cross[key] = ("absent_from_final" if not b else
                      "identical" if a == b else
                      "differs (%d vs %d lines)" % (len(a), len(b)))

    # every shipped code must be a column of the COVIDiSTRESS Vol 2 data file
    csv_p, colcheck = os.path.join(CACHE, "covidistress_vol2.csv"), {}
    if os.path.exists(csv_p):
        with open(csv_p, encoding="utf-8", errors="ignore") as f:
            cols = set(next(csv.reader(f)))
        for tab, entries in tables.items():
            missing = [c for c in entries if c not in cols]
            colcheck[tab] = {"items": len(entries), "not_a_column": missing}
    else:
        colcheck = {"note": "covidistress_vol2.csv not cached; column check skipped"}

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"tables": tables, "cross_document_wording": cross,
                   "source_column_check": colcheck}, f, ensure_ascii=False,
                  indent=1, sort_keys=True)
    print("wrote %s: %d tables, %d items; cross-document: %s" % (
        OUT, len(tables), sum(len(v) for v in tables.values()),
        ", ".join("%s=%s" % (k.strip("[]"), v) for k, v in cross.items())))

if __name__ == "__main__":
    main()
