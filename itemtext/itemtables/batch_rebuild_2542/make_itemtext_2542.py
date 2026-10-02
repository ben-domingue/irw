"""Item text for the two c19prc tables rebuilt under irw#2542 (PR #2756).

Reads the SPSS variable/value labels of the C19PRC-UK deposit (OSF v2zur, CC BY 4.0;
cached at ~/.cache/c19prc_uk_mcbride_2021/) and writes one __items.csv per table, keyed
to the item codes of the rebuilt response tables (item_response_warehouse_4 v12.2):

socialdistance (22 codes)
  SocialDistance1-14        W1 + W2 (+ W5 for all but 4); W5 item i+1 -> code i for i=8..14
  SocialDistance4_W5        W5 item 4 ("...time and facilities...")
  SocialDistance15_W1-17_W1 W1 items 15-17
  SocialDistance15_W2-17_W2 W2 items 15-17 + W5 items 16-18
  SocialDistance18          W2 item 18 + W5 item 8
lockdown_contact_behaviours (9 codes, W5 numbering)
  Risk_Behaviours_1-4       W5 + W6 items 1-4
  Risk_Behaviours_5, _6     W5 only
  Risk_Behaviours_7-9       W5 items 7-9 + W6 items 5-7

The script asserts that every pooled code carries the same statement in every wave
(after stripping the leading number and straightening apostrophes) and the same value
labels, and that the live table reproduces the .sav cell for cell under this mapping
(wave x item x resp counts) when live CSVs are given.

Usage: python3 make_itemtext_2542.py <out_dir> [<live_socialdistance.csv> <live_lockdown.csv>]
Nulls are written as empty unquoted cells, never the literal NA.
"""
import collections
import csv
import os
import re
import sys

import pyreadstat

SRC = os.path.expanduser("~/.cache/c19prc_uk_mcbride_2021/")
SAV = {1: "C19PRC_UKW1W2_archive_final.sav", 2: "C19PRC_UKW1W2_archive_final.sav",
       5: "C19PRC_UKW5_archive_final.sav", 6: "C19PRC_UK_W6_archive_final.sav"}
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]

_meta = {}


def meta(w):
    f = SAV[w]
    if f not in _meta:
        _meta[f] = pyreadstat.read_sav(SRC + f, metadataonly=True)[1]
    return _meta[f]


def label(w, col):
    """(stem, statement, value_labels) from the .sav label '<stem> - <N.> <statement>'."""
    m = meta(w)
    lab = m.column_names_to_labels[col]
    stem, stmt = lab.split(" - ", 1)
    stmt = re.sub(r"^\d+\.\s*", "", stmt).strip()
    stem = re.sub(r"\s+", " ", stem).strip()
    vl = {int(k): v for k, v in m.variable_value_labels[col].items()}
    return stem, stmt, vl


def norm(s):
    return s.replace("’", "'").strip()


def sd_col(w, i):
    return f"W{w}_SocialDistance{i}" if w in (1, 2) else f"W5_SocialDistance_{i}"


# code -> [(wave, sav column)], first entry is the wording that ships
SD = collections.OrderedDict()
for i in range(1, 15):
    SD[f"SocialDistance{i}"] = [(1, sd_col(1, i)), (2, sd_col(2, i))]
    if i != 4:
        SD[f"SocialDistance{i}"].append((5, sd_col(5, i if i < 8 else i + 1)))
for i in (15, 16, 17):
    SD[f"SocialDistance{i}_W1"] = [(1, sd_col(1, i))]
for i in (15, 16, 17):
    SD[f"SocialDistance{i}_W2"] = [(2, sd_col(2, i)), (5, sd_col(5, i + 1))]
SD["SocialDistance18"] = [(2, sd_col(2, 18)), (5, sd_col(5, 8))]
SD["SocialDistance4_W5"] = [(5, sd_col(5, 4))]

LC = collections.OrderedDict()
for i in range(1, 10):
    LC[f"Risk_Behaviours_{i}"] = [(5, f"W5_Risk_Behaviours_{i}")]
for i in (1, 2, 3, 4):
    LC[f"Risk_Behaviours_{i}"].append((6, f"W6_Risk_Behaviours_{i}"))
for w5, w6 in ((7, 5), (8, 6), (9, 7)):
    LC[f"Risk_Behaviours_{w5}"].append((6, f"W6_Risk_Behaviours_{w6}"))


def check_pooled(spec):
    for code, srcs in spec.items():
        _, s0, v0 = label(*srcs[0])
        for w, c in srcs[1:]:
            _, s, v = label(w, c)
            assert norm(s) == norm(s0), (code, w, c, s, s0)
            assert v == v0, (code, w, c)


def section_of_sd(code):
    if code == "SocialDistance4_W5":
        return 4
    if code.endswith("_W1"):
        return 2
    if code.endswith("_W2") or code == "SocialDistance18":
        return 3
    return 1


def build(table, spec, instrument, section_fn, stem_in_instructions):
    rows = []
    stems = {}
    for code, srcs in spec.items():
        w, c = srcs[0]
        stem, stmt, vl = label(w, c)
        sec = section_fn(code)
        stems.setdefault(sec, stem)
        assert stems[sec] == stem, (code, sec)
        for r in sorted(vl):
            rows.append({"table": table, "section_id": f"{table}_{sec}", "item": code,
                         "instrument": instrument,
                         "instructions": stem if stem_in_instructions else "",
                         "section_prompt": "" if stem_in_instructions else stem,
                         "item_text": stmt, "correct_response": "",
                         "option_text": vl[r], "resp": r})
    if stem_in_instructions:
        assert len(set(stems.values())) == 1
    rows.sort(key=lambda d: (d["section_id"], list(spec).index(d["item"]), d["resp"]))
    return rows


def write(rows, path):
    def cell(k, v):
        if k == "resp":
            return str(v)
        if v == "":
            return ""
        return '"' + v.replace('"', '""') + '"'
    with open(path, "w", newline="") as f:
        f.write(",".join(f'"{c}"' for c in COLS) + "\n")
        for d in rows:
            f.write(",".join(cell(c, d[c]) for c in COLS) + "\n")


def crosscheck(live_csv, spec):
    """live wave x item x resp counts == .sav counts under the mapping."""
    live = collections.Counter()
    with open(live_csv, newline="") as f:
        for d in csv.DictReader(f):
            live[(int(float(d["wave"])), d["item"], int(float(d["resp"])))] += 1
    sav = collections.Counter()
    data = {}
    for code, srcs in spec.items():
        for w, c in srcs:
            if SAV[w] not in data:
                data[SAV[w]] = pyreadstat.read_sav(SRC + SAV[w])[0]
            col = data[SAV[w]][c]
            for v, n in col.value_counts().items():
                sav[(w, code, int(v))] += int(n)
    diff = {k for k in set(live) | set(sav) if live[k] != sav[k]}
    return len(set(live) | set(sav)), diff


if __name__ == "__main__":
    out = sys.argv[1]
    check_pooled(SD)
    check_pooled(LC)
    t1 = "c19prc_uk_mcbride_2021_socialdistance"
    t2 = "c19prc_uk_mcbride_2021_lockdown_contact_behaviours"
    r1 = build(t1, SD, "COM-B (Capability, Opportunity, Motivation - Behaviour) questions: social distancing",
               section_of_sd, stem_in_instructions=False)
    r2 = build(t2, LC, "Weekly social-contact and protective behaviours (C19PRC-UK Waves 5-6)",
               lambda code: 1, stem_in_instructions=True)
    write(r1, os.path.join(out, t1 + "__items.csv"))
    write(r2, os.path.join(out, t2 + "__items.csv"))
    print(t1, len(r1), "rows,", len(SD), "items")
    print(t2, len(r2), "rows,", len(LC), "items")
    if len(sys.argv) == 4:
        for t, spec, live in ((t1, SD, sys.argv[2]), (t2, LC, sys.argv[3])):
            n, diff = crosscheck(live, spec)
            print(t, "wave x item x resp cells:", n, "mismatches:", len(diff), sorted(diff)[:10])
