"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AC batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article with a retraction notice
(<related-article related-article-type="retraction-forward">) is refused.

Tables built (CONFIGS below): ten tables (twelve matrices) from ten articles, found by
new Europe PMC searches of 2026-11-18 (open access, CC BY / CC0, 2015-2026: "inter-item
correlation matrix", "polychoric correlation matrix", "item correlation matrix",
"correlation matrix" + "confirmatory factor analysis" + "scale development",
"zero-order correlations" + "means and standard deviations"). All ten are item-level
matrices of a scale (inter-item correlations), several with item means and SDs. The N
of each is from the caption, a table note or the article text, as noted in
matrices.csv.

Parsing: as pmc_article_tables_y.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions; None means the variable has no printed row (or column),
as when a lower triangle omits the first row and the diagonal. Cells are read as text.
Significance stars and daggers are stripped; nothing else is changed. Unicode minus
(U+2212) and an en dash used as a minus are read as "-", and spaces inside a cell are
dropped ("− .13" -> -0.13). Where a cell also prints a standard error in brackets
("0.06 (0.02)"), the part's `cell_rx` keeps the number before the bracket. For each
pair of variables the script reads both cells (row i/column j and row j/column i):
exactly one must hold a number and the other must be empty or a dash, or both must
hold the same number (a full square). Diagonal cells (1, 1.00, 1.000, a dash or blank)
are written as 1. Values are written in shortest round-trip form of the published
decimal (for example "0.40" -> "0.4", "−0.00" -> "-0.0"), i.e. unchanged.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or number
of a label (so that item wording printed as a row label is never copied here).
Variable names are the source's item codes (i1, Item_1, Syfor1, CPRS 1, WAI1, ...);
where the source prints only a number or item content, items are written as item1,
item2, ..., never with item wording. Cells a config lists in `empty` must be blank
(the items a sample did not administer).

Mean and SD cells are read from the cell a config names (with a regular expression
when the cell holds more than the number, as "4.12 (0.86)" or "0.23 ± 0.42"); the row
label of each moment is checked the same way. They become mean/sd rows, values as
printed.

`n` is the matrix N, written on every row. A table with several samples has a
`group` column.

Usage: python3 data/covariance/pmc_article_tables_ac.py <out dir>
(set IRW_PMC_XML_DIR=<dir of PMCxxxx.xml> to read saved copies instead of Europe PMC)
"""
import csv
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


def items(k, stem="item", sep=""):
    return [f"{stem}{sep}{i}" for i in range(1, k + 1)]


def seq(a, b):
    return list(range(a, b + 1))


def moments(stat, label, names, rows, col, rx=None, labels=None, label_col=0, label_rx=None):
    """One moment per variable, read from rows[i] of column col of table label."""
    labels = labels or names
    return [dict(stat=stat, var=v, label=label, row=r, col=col, rx=rx, lab=l,
                 label_col=label_col, label_rx=label_rx)
            for v, r, l in zip(names, rows, labels) if r is not None]


M_BR = r"^(\S+) \("            # "4.12 (0.86)" -> 4.12
SD_BR = r"\((\S+)\)$"           # "4.12 (0.86)" -> 0.86
M_PM = r"^(\S+) ± "             # "0.23 ± 0.42" -> 0.23
SD_PM = r" ± (\S+)$"            # "0.23 ± 0.42" -> 0.42
NUMLAB = r"^(\d+)\."            # "1. <item wording>" -> 1

# --- configs -----------------------------------------------------------------
NMPQ = items(20)
HADS = items(14)
HADS_T2 = [1, 3, 5, 7, 9, 11, 13, 2, 4, 6, 8, 10, 12, 14]   # item order of Table 2 rows 3-9, 11-17
WAI = ["Age group", "Sex", "WAI total"] + items(7, "WAI")
SYF = items(12, "Syfor")
SYF_Q = [v for v in SYF if v not in ("Syfor4", "Syfor6", "Syfor8")]
AIC = items(35, "i")
PEN = items(13, "Item_")
DSI = items(12)
GDS = items(15, "Item ") + ["GDS-SF"]
ERS = items(11) + ["Wheeze"]
CPRS = items(15, "CPRS ")
CPRS_T = [f"CPRS{i:02d}" for i in range(1, 16)]
SYF_Q_ROWS = {"Syfor2": 15, "Syfor3": 16, "Syfor5": 18, "Syfor7": 20, "Syfor9": 22,
              "Syfor10": 23, "Syfor11": 24, "Syfor12": 25}

CONFIGS = [
    dict(pmcid="PMC12152268", label="TABLE 2", table="jahrami_2025_nmpq20", n=5087,
         names=NMPQ, label_col=0,
         parts=[dict(names=NMPQ, labels=[str(i) for i in seq(1, 20)],
                     rows=seq(1, 20), cols=seq(1, 20))],
         moments=moments("mean", "TABLE 1", NMPQ, seq(2, 21), 1, labels=[str(i) for i in seq(1, 20)])
         + moments("sd", "TABLE 1", NMPQ, seq(2, 21), 2, labels=[str(i) for i in seq(1, 20)])),
    dict(pmcid="PMC5628437", label="Table 3", table="djukanovic_2017_hads14", n=6622,
         names=HADS, label_col=0,
         parts=[dict(names=HADS, labels=[str(i) for i in seq(1, 14)],
                     rows=seq(1, 14), cols=seq(1, 14))],
         moments=moments("mean", "Table 2", [f"item{i}" for i in HADS_T2], seq(3, 9) + seq(11, 17), 2,
                         rx=M_BR, labels=[str(i) for i in HADS_T2], label_rx=NUMLAB)
         + moments("sd", "Table 2", [f"item{i}" for i in HADS_T2], seq(3, 9) + seq(11, 17), 2,
                   rx=SD_BR, labels=[str(i) for i in HADS_T2], label_rx=NUMLAB)),
    dict(pmcid="PMC6531402", label="Table 1", table="freyer_2019_wai10", n=3968,
         names=WAI, label_col=1, label_rx=r"^(Age group|Sex|WAI total|WAI\d)\b",
         parts=[dict(names=WAI, rows=seq(1, 10), cols=seq(4, 12) + [None],
                     cell_rx=r"^(.*?)\s*\(\d?\.\d+\)$")],
         moments=moments("mean", "Table 1", WAI[2:], seq(3, 10), 2, label_col=1,
                         label_rx=r"^(WAI total|WAI\d)\b")
         + moments("sd", "Table 1", WAI[2:], seq(3, 10), 3, label_col=1,
                   label_rx=r"^(WAI total|WAI\d)\b")),
    dict(pmcid="PMC8733345", label="Table 3.", table="frounfelker_2021_syfor12", n=2014,
         group="Belgium", names=SYF, label_col=0,
         parts=[dict(names=SYF, rows=[None] + seq(2, 12), cols=seq(1, 11) + [None])]),
    dict(pmcid="PMC8733345", label="Table 3.", table="frounfelker_2021_syfor12", n=1364,
         group="Quebec", names=SYF_Q, label_col=0,
         parts=[dict(names=SYF_Q, rows=[SYF_Q_ROWS.get(v) for v in SYF_Q],
                     cols=[int(v[5:]) if v != "Syfor12" else None for v in SYF_Q])],
         empty=[(r, c) for r in (17, 19, 21) for c in seq(1, 11)]
         + [(r, c) for r in seq(15, 25) for c in (4, 6, 8)]),
    dict(pmcid="PMC7400145", label="Table 1", table="viejo_2020_aicqc35", n=1032,
         names=AIC, label_col=0,
         parts=[dict(names=AIC, rows=seq(1, 35), cols=seq(1, 35))]),
    dict(pmcid="PMC6926737", label="Table 4", table="siegel_2019_pen13", n=1168,
         names=PEN, label_col=0,
         parts=[dict(names=PEN, rows=seq(1, 13), cols=seq(1, 13))],
         moments=moments("mean", "Table 3", PEN, seq(1, 13), 4, rx=M_BR,
                         labels=[str(i) for i in seq(1, 13)])
         + moments("sd", "Table 3", PEN, seq(1, 13), 4, rx=SD_BR,
                   labels=[str(i) for i in seq(1, 13)])),
    dict(pmcid="PMC8689975", label="TABLE 4", table="zhao_2021_doctoralidentity12", n=491,
         names=DSI, label_col=0,
         parts=[dict(names=DSI, labels=[str(i) for i in seq(1, 12)],
                     rows=[None] + seq(1, 11), cols=seq(1, 11) + [None])],
         moments=moments("mean", "TABLE 3", DSI, seq(1, 12), 1, labels=items(12, "Item "))
         + moments("sd", "TABLE 3", DSI, seq(1, 12), 2, labels=items(12, "Item "))),
    dict(pmcid="PMC9266010", label="Table 3", table="sultana_2022_gdssf16", n=377,
         names=GDS, label_col=0,
         parts=[dict(names=GDS, rows=seq(1, 16), cols=seq(1, 16))],
         moments=moments("mean", "Table 2", GDS[:15], seq(2, 16), 3, rx=M_PM)
         + moments("sd", "Table 2", GDS[:15], seq(2, 16), 3, rx=SD_PM)
         + moments("mean", "Table 2", ["GDS-SF"], [17], 3, rx=M_BR, labels=["GDS-SF"],
                   label_rx=r"^(GDS-SF) scores \(0–15\)$")
         + moments("sd", "Table 2", ["GDS-SF"], [17], 3, rx=SD_BR, labels=["GDS-SF"],
                   label_rx=r"^(GDS-SF) scores \(0–15\)$")),
    dict(pmcid="PMC6545030", label="Table 2", table="nelsen_2019_ers12", n=328,
         names=ERS, label_col=0, label_rx=r"^(?:(\d+)\.|(Wheeze)$)",
         parts=[dict(names=ERS, labels=[str(i) for i in seq(1, 11)] + ["Wheeze"],
                     rows=seq(1, 12), cols=seq(1, 12))]),
    dict(pmcid="PMC7122811", label="Table 3", table="escalantebarrios_2020_cprs15", n=461,
         group="Turkish", names=CPRS, label_col=1,
         parts=[dict(names=CPRS, labels=CPRS_T, rows=seq(2, 16), cols=seq(2, 16))],
         group_row=(0, r"^Turkish \(n = 461\)$")),
    dict(pmcid="PMC7122811", label="Table 3", table="escalantebarrios_2020_cprs15", n=4154,
         group="English", names=CPRS, label_col=1,
         parts=[dict(names=CPRS, rows=seq(18, 32), cols=seq(2, 16))],
         group_row=(17, r"^English \(n = 4154\)$")),
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
    for attempt in range(5):  # Europe PMC sometimes answers with an HTTP 5xx or an HTML error page
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                b = r.read()
            if b.lstrip()[:1] == b"<" and b"<article" in b[:3000]:
                return b
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"{pmcid}: {e}; retrying", file=sys.stderr)
        time.sleep(10 * (attempt + 1))
    raise SystemExit(f"{pmcid}: no article XML from Europe PMC")


def num(cell, where):
    s = cell.replace("−", "-").replace("–", "-").replace(" ", "")
    s = re.sub(r"[*∗†]+$", "", s)
    if not re.fullmatch(r"-?(\d+)?\.\d+|-?\d+", s):
        raise SystemExit(f"{where}: cannot read {cell!r}")
    return repr(float(s))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def label_of(lab, rx, where):
    lab = lab.strip()
    if rx:
        m = re.match(rx, lab)
        if not m:
            raise SystemExit(f"{where}: label {lab!r} does not match {rx!r}")
        lab = next(g for g in m.groups() if g)
    return lab


def check_article(pmcid, root):
    lic = root.find(".//license")
    href = (lic.get("{http://www.w3.org/1999/xlink}href") or "") if lic is not None else ""
    links = " ".join(e.get("{http://www.w3.org/1999/xlink}href") or "" for e in lic.iter()) if lic is not None else ""
    ltxt = txt(lic) if lic is not None else ""
    if re.search(r"NonCommercial|NoDeriv|by-nc|by-nd|by-sa|ShareAlike", href + links + ltxt):
        raise SystemExit(f"{pmcid}: restricted licence {href} {ltxt[:120]}")
    if not (re.search(r"creativecommons\.org/(licenses/by/|publicdomain/zero)", href + links + ltxt)
            or re.search(r"Creative Commons Attribution( \(CC BY\))? (L|l)icen[cs]e", ltxt)):
        raise SystemExit(f"{pmcid}: licence not CC BY / CC0: {href} {ltxt[:120]}")
    for ra in root.iter("related-article"):
        if ra.get("related-article-type") in ("retraction-forward", "retracted-article"):
            raise SystemExit(f"{pmcid}: retracted")


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
    labels = part.get("labels", names)
    k = len(names)
    if len(ridx) != k or len(cidx) != k or len(labels) != k:
        raise SystemExit(f"{where}: bad part config")
    for nm, r in zip(labels, ridx):  # printed row labels must be the expected ones
        if r is not None:
            lab = label_of(rows[r][cfg["label_col"]], cfg.get("label_rx"), where)
            if norm(lab) != norm(nm):
                raise SystemExit(f"{where}: row label {lab!r} is not {nm!r}")

    def cell(a, b):
        r, c = ridx[a], cidx[b]
        if r is None or c is None or c >= len(rows[r]):
            return None
        s = rows[r][c]
        if part.get("cell_rx") and s.strip() not in EMPTY:
            m = re.fullmatch(part["cell_rx"], s.strip())
            if not m:
                raise SystemExit(f"{where}: cell {s!r} does not match cell_rx")
            s = m.group(1)
        return s

    got = {}
    for i in range(k):
        d = cell(i, i)
        if d is not None and d.strip() not in DIAG:
            raise SystemExit(f"{where}: diagonal {names[i]} is {d!r}")
        for j in range(i):
            a, b = cell(i, j), cell(j, i)
            a = None if a is None or a.strip() in EMPTY else a
            b = None if b is None or b.strip() in EMPTY else b
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
    where = f"{cfg['pmcid']} {cfg['label']} {cfg.get('group', '')}".strip()
    rows = table_rows(root, cfg["label"])
    if "group_row" in cfg:  # the panel heading names this sample and its N
        r, rx = cfg["group_row"]
        if not re.match(rx, rows[r][0]):
            raise SystemExit(f"{where}: panel heading {rows[r][0]!r}")
    for r, c in cfg.get("empty", []):
        if c < len(rows[r]) and rows[r][c].strip():
            raise SystemExit(f"{where}: cell ({r},{c}) should be empty: {rows[r][c]!r}")
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

    g = {"group": cfg["group"]} if cfg.get("group") else {}
    out, check = [], []
    for i in range(k):
        for j in range(i):
            key = frozenset((names[i], names[j]))
            if key not in cells:
                raise SystemExit(f"{where}: pair {sorted(key)} not printed")
            v, raw = cells[key]
            out.append({"stat": "cor", "var1": names[i], "var2": names[j], "value": v,
                        "n": cfg["n"], **g})
            check.append((cfg.get("group", ""), names[i], names[j], raw))
        out.append({"stat": "cor", "var1": names[i], "var2": names[i], "value": "1",
                    "n": cfg["n"], **g})

    seen = set()
    for m in cfg.get("moments", []):
        if m["var"] not in names or (m["stat"], m["var"]) in seen:
            raise SystemExit(f"{where}: bad moment {m}")
        seen.add((m["stat"], m["var"]))
        t = table_rows(root, m["label"])
        lab = label_of(t[m["row"]][m["label_col"]], m["label_rx"], where)
        if norm(lab) != norm(m["lab"]):
            raise SystemExit(f"{where}: {m['label']} row {m['row']} is {lab!r}, not {m['lab']!r}")
        c = t[m["row"]][m["col"]].strip()
        if m.get("rx"):
            hit = re.search(m["rx"], c)
            if not hit:
                raise SystemExit(f"{where}: {m['stat']} cell {c!r} for {m['var']!r}")
            raw = hit.group(1)
        else:
            raw = c
        v = num(raw, f"{where} {m['stat']} {m['var']}")
        if m["stat"] == "sd" and float(v) <= 0:
            raise SystemExit(f"{where}: sd {v} for {m['var']}")
        out.append({"stat": m["stat"], "var1": m["var"], "var2": "", "value": v, "n": cfg["n"], **g})
        check.append((cfg.get("group", ""), m["stat"] + ":" + m["var"], "", raw))
    return out, check


def main(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cache, tables = {}, {}
    for cfg in CONFIGS:
        if cfg["pmcid"] not in cache:
            cache[cfg["pmcid"]] = ET.fromstring(get(cfg["pmcid"]))
            check_article(cfg["pmcid"], cache[cfg["pmcid"]])
        rows, check = build(cfg, cache[cfg["pmcid"]])
        t = tables.setdefault(cfg["table"], {"rows": [], "check": [], "grouped": bool(cfg.get("group"))})
        if t["grouped"] != bool(cfg.get("group")):
            raise SystemExit(f"{cfg['table']}: grouped and ungrouped configs")
        t["rows"] += rows
        t["check"] += check
    for name, t in tables.items():
        cols = ["stat", "var1", "var2", "value", "n"] + (["group"] if t["grouped"] else [])
        with open(outdir / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(t["rows"])
        with open(outdir / f"{name}.check.tsv", "w", encoding="utf-8") as f:
            for row in t["check"]:
                f.write("\t".join(row) + "\n")
        print(f"{name}: {len(t['rows'])} rows")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 pmc_article_tables_ac.py <out dir>")
    main(sys.argv[1])
