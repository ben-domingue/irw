"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent X batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise.

Tables built (CONFIGS below): ten correlation tables from ten articles, chosen
from the Europe PMC caption scan of 2026-11-17 (scratchpad scripts_n/cands.tsv),
from the candidates agents P and U left unvetted. Seven are item-level matrices
(inter-item correlations; three polychoric, one tetrachoric); the others are
among scale scores and covariates. The N of each is from the caption, a table
note or the article text, as noted in matrices.csv.

Parsing: cells are read as text. Significance stars and daggers are stripped;
nothing else is changed. Unicode minus (U+2212) and an en dash used as a minus are
read as "-", and spaces inside a cell are dropped ("0.070 *" -> 0.070). Each config
names the <tr> holding each variable's row (`rows`) and the cell holding its column
(`cols`, counting <td>/<th> elements; None when the table prints no row or column
for it). A config may have several `parts` (one per panel of the printed table),
each naming a subset of the variables with its own rows and cols. For each pair of
variables the script reads both cells (row i/column j and row j/column i): exactly
one must hold a number and the other must be empty or a dash, or both must hold the
same number (a full square). A pair printed in more than one panel must have the
same value in each. A pair printed nowhere is written with an empty value only when
the config lists it in `blank` (V4: measured but not reported). Diagonal cells (1,
1.00, a dash or blank) are written as 1. Values are written in shortest round-trip
form of the published decimal (for example "0.40" -> "0.4"), i.e. unchanged.

Mean, SD and reliability cells are read from the cell a config names, with a
regular expression when the cell holds more than the number ("0.4(0.9)",
"Functional coping (α = 0.680; ω = 0.689)"), or from the article text with a
regular expression that must match exactly one value. They become mean/sd/rel rows,
values as printed. Variable names are the source's labels without running numbers
or model-role tags ("(X)"); where the source numbers its items they are written as
item1, item2, ..., never with item wording.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_x.py <out dir>
(set IRW_PMC_XML_DIR=<dir of PMCxxxx.xml> to read saved copies instead of Europe PMC)
"""
import csv
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

MSD_M = r"^(\S+?) ?\("        # "3.38 (1.00)" or "0.4(0.9)" -> mean
MSD_S = r"\((\S+)\)$"         # "3.38 (1.00)" -> sd


def col_moments(stat, names, label, rows, col, rx=None):
    """One moment per variable, read from rows[i] of column col of table label."""
    return [dict(stat=stat, var=v, label=label, row=r, col=col, rx=rx)
            for v, r in zip(names, rows) if r is not None]


def row_moments(stat, names, label, row, cols, rx=None):
    """One moment per variable, read from row `row`, cells cols[i]."""
    return [dict(stat=stat, var=v, label=label, row=row, col=c, rx=rx)
            for v, c in zip(names, cols)]


def text_moment(stat, var, rx):
    return dict(stat=stat, var=var, text=rx)


def items(k):
    return [f"item{i}" for i in range(1, k + 1)]


# --- configs -----------------------------------------------------------------
EWAQ = items(8)
CSSRS = items(6)
PQM = ["Before FC", "Before SoMPA", "Before SE", "During FC", "During SoMPA", "During SE",
       "After FC", "After SoMPA", "After SE", "Performance quality"]
FIVEC = ["Teacher Care", "Teacher Clarity", "Teacher-Student Closeness",
         "Teacher Confirmation", "Teacher Credibility", "Perceived Course Impact",
         "Perceived Course Meaningfulness", "Perceived Course Competence"]
FIVEC_SUB = [n for n in FIVEC if n != "Teacher Credibility"]   # one alpha / M / SD each
FIVEC_SUB_ROWS = [1, 2, 3, 4, 8, 9, 10]                         # Tables 1 and 3
LWMS = items(5)
FSII = items(5)
RMHI = items(5)
CAS = items(5)
SOBJ = ["Gender", "Grade", "Self-Objectification", "Body Shame", "Self-Disgust",
        "Depression", "Perceived peer connectedness"]
CORES = ["Psychological difficulties", "Social adaptability", "Attitudes toward parents",
         "Co-residence status", "Sex", "Grade"]
CORES_A = ["Psychological difficulties", "Social adaptability", "Attitudes toward parents",
           "Sex", "Grade"]
CORES_B = ["Psychological difficulties", "Social adaptability", "Co-residence status",
           "Sex", "Grade"]

PQM_REL = r"^(?:Functional coping|Symptoms of MPA|Self-efficacy) \(α = (\d?\.\d+)[;,]"
STRIP_ROLE = r"\s*\((?:X|M1|M2|Y|W)\)$"
PRES = r"In the present study, "

CONFIGS = [
    dict(pmcid="PMC13260422", label="Table 4", table="wnuk_2026_ewaq8", n=754,
         names=EWAQ, parts=[dict(names=EWAQ, rows=[None] + list(range(1, 8)),
                                 cols=list(range(1, 8)) + [None])]),
    dict(pmcid="PMC10507718", label="Table 2", table="austriacorrales_2023_cssrs6", n=3645,
         names=CSSRS, parts=[dict(names=CSSRS, rows=list(range(1, 7)), cols=list(range(1, 7)))],
         moments=row_moments("mean", CSSRS, "Table 2", 7, list(range(1, 7)))
         + row_moments("sd", CSSRS, "Table 2", 8, list(range(1, 7)))),
    dict(pmcid="PMC12992244", label="Table 4", table="spahn_2026_pqm10", n=605,
         names=PQM, label_col=0,
         parts=[dict(names=PQM, rows=list(range(2, 12)), cols=list(range(1, 10)) + [None])],
         moments=[dict(stat="rel", var=v, label="Table 2", seq=PQM_REL, k=i)
                  for i, v in enumerate(PQM[:9])]),
    dict(pmcid="PMC13727553", label="Table 5", table="sun_2026_teacher5cs8", n=446,
         names=FIVEC, label_col=0,
         parts=[dict(names=FIVEC, rows=list(range(1, 9)), cols=list(range(1, 9)))],
         moments=col_moments("mean", FIVEC_SUB, "Table 1", FIVEC_SUB_ROWS, 2)
         + col_moments("sd", FIVEC_SUB, "Table 1", FIVEC_SUB_ROWS, 3)
         + col_moments("rel", FIVEC_SUB, "Table 3", FIVEC_SUB_ROWS, 2),
         moment_label_col=0),
    dict(pmcid="PMC13112981", label="Table 3", table="banoschaparro_2026_lwms5", n=345,
         names=LWMS, parts=[dict(names=LWMS, rows=list(range(1, 6)), cols=list(range(6, 11)))],
         moments=col_moments("mean", LWMS, "Table 3", list(range(1, 6)), 1)
         + col_moments("sd", LWMS, "Table 3", list(range(1, 6)), 2)),
    dict(pmcid="PMC13323221", label="Table 3", table="banoschaparro_2026_fsii5", n=962,
         names=FSII, parts=[dict(names=FSII, rows=list(range(1, 6)), cols=list(range(6, 11)))],
         moments=col_moments("mean", FSII, "Table 3", list(range(1, 6)), 1)
         + col_moments("sd", FSII, "Table 3", list(range(1, 6)), 2)),
    dict(pmcid="PMC13696408", label="Table 3", table="banoschaparro_2026_rmhi5", n=2978,
         names=RMHI, parts=[dict(names=RMHI, rows=list(range(1, 6)), cols=list(range(6, 11)))],
         moments=col_moments("mean", RMHI, "Table 3", list(range(1, 6)), 1)
         + col_moments("sd", RMHI, "Table 3", list(range(1, 6)), 2)),
    dict(pmcid="PMC13330301", label="Table 4", table="kattan_2026_cas5", n=648,
         names=CAS, parts=[dict(names=CAS, rows=list(range(1, 6)), cols=list(range(1, 6)))],
         moments=col_moments("mean", CAS, "Table 3", list(range(3, 8)), 6, MSD_M)
         + col_moments("sd", CAS, "Table 3", list(range(3, 8)), 6, MSD_S)),
    dict(pmcid="PMC13405790", label="Table 1", table="yue_2026_selfobjectification7", n=1181,
         names=SOBJ, label_col=0, label_strip=STRIP_ROLE,
         parts=[dict(names=SOBJ, rows=list(range(1, 8)), cols=list(range(3, 10)))],
         moments=col_moments("mean", SOBJ, "Table 1", list(range(1, 8)), 1)
         + col_moments("sd", SOBJ, "Table 1", list(range(1, 8)), 2)
         + [text_moment("rel", "Self-Objectification", PRES + r"the body surveillance subscale demonstrated good internal consistency \(Cronbach’s α = (\d?\.\d+)\)"),
            text_moment("rel", "Body Shame", PRES + r"the body shame subscale showed good internal consistency \(Cronbach’s α = (\d?\.\d+)\)"),
            text_moment("rel", "Self-Disgust", r"Self-Disgust[^α]{0,1500}?" + PRES + r"the scale exhibited excellent internal consistency \(Cronbach’s α = (\d?\.\d+)\)"),
            text_moment("rel", "Depression", r"Depressive Symptoms[^α]{0,1500}?Internal consistency in the present study was good \(Cronbach’s α = (\d?\.\d+)\)"),
            text_moment("rel", "Perceived peer connectedness", r"Perceived Peer Connectedness[^α]{0,1500}?" + PRES + r"the scale demonstrated good internal consistency \(Cronbach’s α = (\d?\.\d+)\)")]),
    dict(pmcid="PMC13661461", label="Table 2", table="li_2026_coresidence6", n=34097,
         names=CORES, label_col=0,
         parts=[dict(names=CORES_A, rows=list(range(2, 7)), cols=list(range(3, 8))),
                dict(names=CORES_B, rows=list(range(8, 13)), cols=list(range(3, 8)))],
         blank=[("Co-residence status", "Attitudes toward parents")],
         moments=col_moments("mean", CORES_A, "Table 2", list(range(2, 7)), 1)
         + col_moments("sd", CORES_A, "Table 2", list(range(2, 7)), 2)
         + [dict(stat="mean", var="Co-residence status", label="Table 2", row=10, col=1),
            dict(stat="sd", var="Co-residence status", label="Table 2", row=10, col=2),
            text_moment("rel", "Psychological difficulties", r"In this sample, Cronbach’s α was (\d?\.\d+) for the 35-item total"),
            text_moment("rel", "Social adaptability", r"Social Adaptability Diagnostic Scale.{0,1200}?In this sample, Cronbach’s α was (\d?\.\d+)\.")],
         # the panel-B copies of shared moments must equal panel A's
         moment_checks=[("Table 2", (r, c), (r + 6, c)) for r in (2, 3, 5, 6) for c in (1, 2)]),
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
    return [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in tws[0].iter("tr")]


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
        elif "seq" in m:  # k-th match of a regex over the table's cells in reading order
            t = table_rows(root, m["label"])
            hits = [h.group(1) for c in (c for r in t for c in r)
                    for h in [re.search(m["seq"], c)] if h]
            raw = hits[m["k"]]
            if len(hits) != m.get("of", 9):
                raise SystemExit(f"{where}: {len(hits)} matches of {m['seq']!r}")
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
        raise SystemExit("usage: python3 pmc_article_tables_x.py <out dir>")
    main(sys.argv[1])
