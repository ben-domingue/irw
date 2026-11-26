"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent Y batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise.

Tables built (CONFIGS below): ten correlation tables from ten articles, from the
candidates agents P, U and X left "pending" or unvetted in held.csv (Europe PMC caption
scan of 2026-11-17). Two are item-level matrices (OHIP5-SRB, BIAJS); the others are
among scale scores and covariates. The N of each is from the caption, a table note or
the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_x.py, except that each table is first expanded into a
grid (a cell with rowspan/colspan fills every position it spans), so the `rows` and
`cols` indices of a config are grid positions. Cells are read as text. Significance
stars and daggers are stripped; nothing else is changed. Unicode minus (U+2212) and
an en dash used as a minus are read as "-", and spaces inside a cell are dropped
("− 0.13**" -> -0.13). For each pair of variables the script reads both cells (row
i/column j and row j/column i): exactly one must hold a number and the other must be
empty or a dash, or both must hold the same number (a full square). Diagonal cells
(1, 1.0, 1.00, 1.000, a dash or blank) are written as 1. Values are written in
shortest round-trip form of the published decimal (for example "0.40" -> "0.4"),
i.e. unchanged.

Mean, SD and reliability cells are read from the cell a config names (with a regular
expression when the cell holds more than the number), or from the article text with a
regular expression that must match exactly one value. They become mean/sd/rel rows,
values as printed. Variable names are the source's labels without running numbers or
dummy-coding tags ("(=1)"); where the source prints item content as the row label, the
items are written as item1, item2, ..., never with item wording.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_y.py <out dir>
(set IRW_PMC_XML_DIR=<dir of PMCxxxx.xml> to read saved copies instead of Europe PMC)
"""
import csv
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

NUM = r"(-?\d?\.\d+)"


def col_moments(stat, names, label, rows, col, rx=None):
    """One moment per variable, read from rows[i] of column col of table label."""
    return [dict(stat=stat, var=v, label=label, row=r, col=col, rx=rx)
            for v, r in zip(names, rows) if r is not None]


def row_moments(stat, names, label, row, cols, rx=None):
    """One moment per variable, read from row `row`, cells cols[i]."""
    return [dict(stat=stat, var=v, label=label, row=row, col=c, rx=rx)
            for v, c in zip(names, cols) if c is not None]


def text_moment(stat, var, rx):
    return dict(stat=stat, var=var, text=rx)


def items(k):
    return [f"item{i}" for i in range(1, k + 1)]


def seq(k):
    return list(range(1, k + 1))


# --- configs -----------------------------------------------------------------
EDT = ["CTM-3", "CAT-T", "STAI", "PROMIS", "Factor 2", "Factor 1", "Global"]
OHIP = items(5)
BIAJS = ["BIAJS_1", "BIAJS_2", "BIAJS_3", "BIAJS_4"]
ATH = ["Perceived stress at T1", "Stress mindset at T1", "Positive reframing at T2",
       "Behavioral disengagement at T2", "Depressive symptoms at T3"]
KOR = ["Depressive symptoms", "Life-service competence", "Communication-media competence",
       "Social activity participation", "Age", "Education", "Living alone"]
KOR_M = ["Depressive symptoms", "Life-service competence", "Communication-media competence",
         "Social activity participation", "Education"]
FV = ["HC", "FI", "PBC", "PCA", "ATT", "PI"]
ART = ["Visual art experience", "Presence of meaning", "Search for meaning", "Depression",
       "Anxiety", "Stress", "Psychological distress"]
TPR = ["IUS total", "APS-S", "BFNE", "IUI", "IUP"]
TPR_T3 = [1, 5, 4, 3, 2]          # rows of Table 3 (M, SD, alpha) for TPR, in TPR order
AIW = ["Continuous AI availability", "AI delegation dependence",
       "Boundary management preference", "AI process vigilance", "Work-related rumination",
       "Psychological detachment", "Recovery outcomes"]
PSY = ["Fear", "Grief", "Physical distress", "Insanity", "Isolation", "Death", "Paranoia",
       "Acceptance and reappraisal", "Sensory regulation and physical interaction",
       "Social support and disclosure", "EBI"]

DUMMY = r"\s*\([^()]*=\s*1\)$"     # "Age (old-old = 1)" -> "Age"
CA = "Cronbach['’]s α"

CONFIGS = [
    dict(pmcid="PMC12994314", label="TABLE 5", table="beachy_2026_edtransitions7", n=301,
         names=EDT, label_col=0,
         parts=[dict(names=EDT, rows=seq(7), cols=seq(7))]),
    dict(pmcid="PMC12653925", label="Table 3", table="popovac_2025_ohip5srb5", n=236,
         names=OHIP, parts=[dict(names=OHIP, rows=seq(5), cols=seq(5))],
         moments=col_moments("mean", OHIP, "Table 2", list(range(2, 7)), 1)
         + col_moments("sd", OHIP, "Table 2", list(range(2, 7)), 2)),
    dict(pmcid="PMC12564600", label="Table 1", table="silva_2025_biajs4", n=234,
         names=BIAJS, label_col=0,
         parts=[dict(names=BIAJS, rows=seq(4), cols=[6, 7, 8, None])],
         moments=col_moments("mean", BIAJS, "Table 1", seq(4), 1)
         + col_moments("sd", BIAJS, "Table 1", seq(4), 2), moment_label_col=0),
    dict(pmcid="PMC13593483", label="Table 2", table="huang_2026_athletestress5", n=769,
         names=ATH, label_col=0,
         parts=[dict(names=ATH, rows=seq(5), cols=seq(5))],
         moments=row_moments("mean", ATH, "Table 2", 6, seq(5))
         + row_moments("sd", ATH, "Table 2", 7, seq(5))
         + [text_moment("rel", ATH[0], CA + r" for perceived stress at T1 was " + NUM + r"\."),
            text_moment("rel", ATH[1], CA + r" for stress mindset at T1 was " + NUM + r"\."),
            text_moment("rel", ATH[2], CA + r" for positive reframing at T1 and T2 was \d?\.\d+ and " + NUM + r","),
            text_moment("rel", ATH[3], CA + r" for behavioral disengagement at T1 and T2 was \d?\.\d+ and " + NUM + r","),
            text_moment("rel", ATH[4], CA + r" of depressive symptoms at T1, T2, T3 was \d?\.\d+, \d?\.\d+, and " + NUM + r", respectively")]),
    dict(pmcid="PMC13702013", label="Table 3", table="jung_2026_digitalcompetence7", n=9951,
         names=KOR, label_col=0, label_strip=DUMMY,
         parts=[dict(names=KOR, rows=seq(7), cols=seq(6) + [None])],
         moments=row_moments("mean", KOR_M, "Table 3", 8, [1, 2, 3, 4, 6])
         + row_moments("sd", KOR_M, "Table 3", 9, [1, 2, 3, 4, 6])
         + [text_moment("rel", "Depressive symptoms", r"Internal consistency in the present sample was acceptable \(Cronbach’s α = " + NUM + r"\)"),
            text_moment("rel", "Life-service competence", r"4 items, range 0[–-]4, α = " + NUM + r"\)"),
            text_moment("rel", "Communication-media competence", r"6 items, range 0[–-]6, α = " + NUM + r"\)")]),
    dict(pmcid="PMC13610518", label="Table 3", table="contreraslopez_2026_fvpurchase6", n=458,
         names=FV, label_col=0,
         parts=[dict(names=FV, rows=seq(6), cols=seq(6))]),
    dict(pmcid="PMC13582478", label="Table 5", table="lv_2026_visualart7", n=423,
         names=ART, label_col=0,
         parts=[dict(names=ART, rows=seq(7), cols=list(range(3, 10)))],
         moments=col_moments("mean", ART, "Table 5", seq(7), 1)
         + col_moments("sd", ART, "Table 5", seq(7), 2)
         + [text_moment("rel", ART[0], r"Internal consistency in the analytic sample was high \(Cronbach’s alpha = " + NUM + r"\)"),
            text_moment("rel", ART[1], r"Cronbach’s alpha was " + NUM + r" for presence of meaning and"),
            text_moment("rel", ART[2], r"for presence of meaning and " + NUM + r" for search for meaning"),
            text_moment("rel", ART[3], r"Cronbach’s alpha was " + NUM + r" for the adapted depressive-symptom items"),
            text_moment("rel", ART[4], r"depressive-symptom items, " + NUM + r" for the anxiety-symptom items"),
            text_moment("rel", ART[5], r"anxiety-symptom items, " + NUM + r" for the stress-symptom items"),
            text_moment("rel", ART[6], r"stress-symptom items, and " + NUM + r" across all 21 psychological-distress items")]),
    dict(pmcid="PMC13550155", label="Table 4", table="dipetrillo_2026_teacherprocrast5", n=444,
         names=TPR, label_col=0,
         parts=[dict(names=TPR, rows=seq(5), cols=seq(5))],
         moments=col_moments("mean", TPR, "Table 3", TPR_T3, 1)
         + col_moments("sd", TPR, "Table 3", TPR_T3, 2)
         + col_moments("rel", TPR, "Table 3", TPR_T3, 4)),
    dict(pmcid="PMC13645697", label="Table 9", table="zhang_2026_aidelegation7", n=642,
         names=AIW, label_col=0,
         parts=[dict(names=AIW, rows=seq(7), cols=seq(7))],
         moments=col_moments("mean", AIW, "Table 8", seq(7), 2)
         + col_moments("sd", AIW, "Table 8", seq(7), 3)
         + col_moments("rel", AIW, "Table 3", seq(7), 3), moment_label_col=0),
    dict(pmcid="PMC11582610", label="Table 3", table="wood_2024_psychedelicchallenge11", n=529,
         names=PSY, label_col=1,
         parts=[dict(names=PSY, rows=seq(11), cols=list(range(2, 13)))],
         moments=[text_moment("rel", "EBI", r"also had high internal consistency \(α = " + NUM + r"\), justifying")]),
]

DIAG = {"1", "-", "–", "—", "", "1.00", "1.0", "1.000"}
EMPTY = {"", "-", "–", "—", "--"}


def txt(e):
    return re.sub(r"\s+", " ", "".join(e.itertext())).strip()


def get(pmcid):
    local = os.environ.get("IRW_PMC_XML_DIR")
    if local:
        return (Path(local) / f"{pmcid}.xml").read_bytes()
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def num(cell, where):
    s = cell.replace("−", "-").replace("–", "-").replace(" ", "")
    s = re.sub(r"[*†]+$", "", s)
    if not re.fullmatch(r"-?(\d+)?\.\d+|-?\d+", s):
        raise SystemExit(f"{where}: cannot read {cell!r}")
    return repr(float(s))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def varname(lab, strip=None):
    lab = re.sub(r"^(\(\d+\)|\[\d+\]|\d+\.)\s*", "", lab).strip()
    if strip:
        lab = re.sub(strip, "", lab)
    return lab


def check_licence(pmcid, root):
    lic = root.find(".//license")
    href = (lic.get("{http://www.w3.org/1999/xlink}href") or "") if lic is not None else ""
    links = " ".join(e.get("{http://www.w3.org/1999/xlink}href") or "" for e in lic.iter()) if lic is not None else ""
    ltxt = txt(lic) if lic is not None else ""
    if re.search(r"NonCommercial|NoDeriv|by-nc|by-nd|by-sa|ShareAlike", href + links + ltxt):
        raise SystemExit(f"{pmcid}: restricted licence {href} {ltxt[:120]}")
    if not (re.search(r"creativecommons\.org/(licenses/by/|publicdomain/zero)", href + links + ltxt)
            or re.search(r"Creative Commons Attribution( \(CC BY\))? (L|l)icen[cs]e", ltxt)):
        raise SystemExit(f"{pmcid}: licence not CC BY / CC0: {href} {ltxt[:120]}")


def table_rows(root, label):
    tws = [t for t in root.iter("table-wrap")
           if t.find("label") is not None and txt(t.find("label")) == label]
    if len(tws) != 1:
        raise SystemExit(f"{label}: found {len(tws)} tables")
    grid = {}
    for i, tr in enumerate(tws[0].iter("tr")):
        j = 0
        for c in (c for c in tr if c.tag in ("td", "th")):
            while (i, j) in grid:
                j += 1
            rs, cs = int(c.get("rowspan") or 1), int(c.get("colspan") or 1)
            for a in range(rs):
                for b in range(cs):
                    grid[(i + a, j + b)] = txt(c)
            j += cs
    nr = max(k[0] for k in grid) + 1
    return [[grid.get((i, j), "") for j in range(max([k[1] for k in grid if k[0] == i] + [-1]) + 1)]
            for i in range(nr)]


def read_part(cfg, part, rows, where):
    """{frozenset(pair): (value, raw)} for the pairs printed in one panel."""
    names, ridx, cidx = part["names"], part["rows"], part["cols"]
    k = len(names)
    if len(ridx) != k or len(cidx) != k:
        raise SystemExit(f"{where}: bad part config")
    if "label_col" in cfg:  # printed row labels must match the names used
        for nm, r in zip(names, ridx):
            if r is not None:
                lab = varname(rows[r][cfg["label_col"]], cfg.get("label_strip"))
                if norm(lab) != norm(nm):
                    raise SystemExit(f"{where}: row label {lab!r} is not {nm!r}")

    def cell(a, b):
        r, c = ridx[a], cidx[b]
        if r is None or c is None or c >= len(rows[r]):
            return None
        return rows[r][c]

    got = {}
    for i in range(k):
        d = cell(i, i)
        if d is not None and d.strip() not in DIAG:
            raise SystemExit(f"{where}: diagonal {names[i]} is {d!r}")
        for j in range(i):
            a, b = cell(i, j), cell(j, i)
            a = None if a is None or a in EMPTY else a
            b = None if b is None or b in EMPTY else b
            if a is None and b is None:
                raise SystemExit(f"{where}: missing cell ({names[i]}, {names[j]})")
            if a is not None and b is not None and num(a, where) != num(b, where):
                raise SystemExit(f"{where}: asymmetric ({names[i]}, {names[j]}): {a!r} / {b!r}")
            raw = a if a is not None else b
            v = num(raw, f"{where} ({names[i]},{names[j]})")
            if abs(float(v)) >= 1:
                raise SystemExit(f"{where}: |r| >= 1 at ({names[i]},{names[j]})")
            got[frozenset((names[i], names[j]))] = (v, raw)
    return got


def build(cfg, root):
    where = f"{cfg['pmcid']} {cfg['label']}"
    rows = table_rows(root, cfg["label"])
    names = cfg["names"]
    k = len(names)
    if len(set(names)) != k:
        raise SystemExit(f"{where}: duplicate names")
    cells = {}
    for part in cfg["parts"]:
        if not set(part["names"]) <= set(names):
            raise SystemExit(f"{where}: part names")
        for key, (v, raw) in read_part(cfg, part, rows, where).items():
            if key in cells and cells[key][0] != v:
                raise SystemExit(f"{where}: panels disagree on {sorted(key)}")
            cells[key] = (v, raw)
    blank = {frozenset(p) for p in cfg.get("blank", [])}

    out, check = [], []
    for i in range(k):
        for j in range(i):
            key = frozenset((names[i], names[j]))
            if key in cells:
                if key in blank:
                    raise SystemExit(f"{where}: {sorted(key)} is printed")
                v, raw = cells[key]
            elif key in blank:
                v, raw = "", ""
            else:
                raise SystemExit(f"{where}: pair {sorted(key)} not printed")
            out.append({"stat": "cor", "var1": names[i], "var2": names[j], "value": v,
                        "n": cfg["n"]})
            check.append((names[i], names[j], raw))
        out.append({"stat": "cor", "var1": names[i], "var2": names[i], "value": "1",
                    "n": cfg["n"]})

    for lab, (r1, c1), (r2, c2) in cfg.get("moment_checks", []):
        t = table_rows(root, lab)
        if t[r1][c1] != t[r2][c2]:
            raise SystemExit(f"{where}: {lab} cells ({r1},{c1}) and ({r2},{c2}) differ")

    body = None
    seen = set()
    for m in cfg.get("moments", []):
        if m["var"] not in names or (m["stat"], m["var"]) in seen:
            raise SystemExit(f"{where}: bad moment {m}")
        seen.add((m["stat"], m["var"]))
        if "text" in m:
            if body is None:
                body = txt(root.find(".//body"))
            hits = set(re.findall(m["text"], body))
            if len(hits) != 1:
                raise SystemExit(f"{where}: {m['stat']} for {m['var']!r} matched {hits}")
            raw = hits.pop()
        else:
            t = table_rows(root, m["label"])
            if "moment_label_col" in cfg:  # the row label must name the variable
                lab = varname(t[m["row"]][cfg["moment_label_col"]])
                if norm(lab) != norm(m["var"]):
                    raise SystemExit(f"{where}: {m['label']} row {m['row']} is {lab!r}, not {m['var']!r}")
            c = t[m["row"]][m["col"]]
            if m.get("rx"):
                hit = re.search(m["rx"], c)
                if not hit:
                    raise SystemExit(f"{where}: {m['stat']} cell {c!r} for {m['var']!r}")
                raw = hit.group(1)
            else:
                raw = c
        v = num(raw, f"{where} {m['stat']} {m['var']}")
        if m["stat"] == "rel" and not 0 < float(v) <= 1:
            raise SystemExit(f"{where}: reliability {v} for {m['var']}")
        if m["stat"] == "sd" and float(v) <= 0:
            raise SystemExit(f"{where}: sd {v} for {m['var']}")
        out.append({"stat": m["stat"], "var1": m["var"], "var2": "", "value": v, "n": cfg["n"]})
        check.append((m["stat"] + ":" + m["var"], "", raw))
    return out, check


def main(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cache = {}
    for cfg in CONFIGS:
        if cfg["pmcid"] not in cache:
            cache[cfg["pmcid"]] = ET.fromstring(get(cfg["pmcid"]))
            check_licence(cfg["pmcid"], cache[cfg["pmcid"]])
        rows, check = build(cfg, cache[cfg["pmcid"]])
        with open(outdir / f"{cfg['table']}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n"])
            w.writeheader()
            w.writerows(rows)
        with open(outdir / f"{cfg['table']}.check.tsv", "w", encoding="utf-8") as f:
            for a, b, raw in check:
                f.write(f"{a}\t{b}\t{raw}\n")
        print(f"{cfg['table']}: {len(cfg['names'])} variables, {len(rows)} rows")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 pmc_article_tables_y.py <out dir>")
    main(sys.argv[1])
