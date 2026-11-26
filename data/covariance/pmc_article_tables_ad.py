"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AD batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article with a retraction notice
(<related-article related-article-type="retraction-forward">) is refused.

Tables built (CONFIGS below): eleven tables (eleven matrices) from eleven articles,
vetted from the AC candidate list of 2026-11-18 (Europe PMC searches for "inter-item
correlation matrix", "polychoric correlation matrix" and similar, open access, CC BY /
CC0; the item-level-caption subset first). All are item-level matrices of one scale
(inter-item correlations), several with item means and SDs. The N of each is from the
caption, a table note or the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_ac.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions; None means the variable has no printed row (or column),
as when a lower triangle omits the first row and the diagonal. Cells are read as text.
Significance stars and daggers are stripped; nothing else is changed. Unicode minus
(U+2212) and an en dash used as a minus are read as "-", and spaces inside a cell are
dropped ("0.38 *" -> 0.38). Where a table prints decimal commas ("0,62"; `comma` in a
config), the comma is read as the decimal point. For each pair of variables the script
reads both cells (row i/column j and row j/column i): exactly one must hold a number and
the other must be empty or a dash, or both must hold the same number (a full square).
Two exceptions, each set in a config:
- `lower_only`: only the cell below the diagonal is read, because the cell above it
  holds a different statistic (montanesmuro_2022_ercbs24: Spearman above, Pearson
  below; only the Pearson triangle is built).
- `asym` (with `lower_only`): a full square whose two printed copies of a cell differ.
  The cell below the diagonal is used, and the script checks that the copies differ in
  exactly the listed pairs (zapataospina_2025_etam22; named in matrices.csv notes).
Where a table pads its empty triangle with one cell spanning several columns
(zieff_2023_snapiv18 in the Europe PMC copy: "Item 2" then "0.55" spanning 17 columns),
`span_fill=False` puts the text in the first spanned position only and leaves the rest
empty, so the value is not copied into the empty triangle.
Diagonal cells (1, 1.00, 1.000, a dash or blank) are written as 1. Values are written in
shortest round-trip form of the published decimal (for example "0.40" -> "0.4"), i.e.
unchanged.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or number
of a label (so that item wording printed as a row label is never copied here).
Variable names are the source's item codes (Q1, FSS1, 5a, ...); where the source prints
only a number or item content, items are written as item1, item2, ..., never with item
wording.

Mean and SD cells are read from the cell a config names (with a regular expression
when the cell holds more than the number, as "4.24 (0.67)"); the row label of each
moment is checked the same way, and for moments printed as a row under the matrix
(one column per item) the column header is checked too. They become mean/sd rows,
values as printed.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_ad.py <out dir>
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


def moments(stat, label, names, rows, col, rx=None, labels=None, label_col=0, label_rx=None,
            comma=False):
    """One moment per variable, read from rows[i] of column col of table label."""
    labels = labels or names
    return [dict(stat=stat, var=v, label=label, row=r, col=col, rx=rx, lab=l,
                 label_col=label_col, label_rx=label_rx, comma=comma)
            for v, r, l in zip(names, rows, labels) if r is not None]


def moments_row(stat, label, names, row, cols, rowlab, header_row, headers, comma=False):
    """One moment per variable, printed as a row (row label rowlab) under the matrix,
    one column per variable; the column header (headers[i]) is checked as well."""
    return [dict(stat=stat, var=v, label=label, row=row, col=c, rx=None, lab=rowlab,
                 label_col=0, label_rx=None, comma=comma, hdr=(header_row, h))
            for v, c, h in zip(names, cols, headers)]


M_BR = r"^(\S+) \("            # "4.24 (0.67)" -> 4.24
SD_BR = r"\((\S+)\)$"           # "4.24 (0.67)" -> 0.67
NUMLAB = r"^(\d+)\."            # "3. <item wording>" -> 3

# --- configs -----------------------------------------------------------------
VOP = items(24)
ERC = items(23) + ["ERCB-T"]
ERC_RX = r"^(?:Item (\d+)\.|(ERCB-T)$)"
ETAM = items(22, "Item")
ETAM_ASYM = [("Item5", "Item4"), ("Item7", "Item1"), ("Item11", "Item10"), ("Item14", "Item1"),
             ("Item15", "Item1"), ("Item16", "Item4"), ("Item20", "Item2")]  # copies differ by .01
EDL = [f"D{d}S{s}" for d, k in ((1, 3), (2, 4), (3, 3), (4, 5), (5, 3), (6, 3)) for s in range(1, k + 1)]
IDS = items(18)
SNAP = items(18)
TOPS_NUM = [3, 6, 12, 14, 16, 17, 19, 24, 27, 28, 30, 33, 36, 37, 38, 39, 43]
TOPS = [f"item{i}" for i in TOPS_NUM]
CSAT = items(17, "Q")
GAIN = ["1", "2", "3", "4", "5a", "5b", "5c", "5d", "5e", "5f", "5g"]
SOM = items(9) + ["timing"]
FSS = items(9, "FSS")

CONFIGS = [
    dict(pmcid="PMC8548739", label="TABLE 2", table="aubouinbonnaventure_2021_vopi24", n=606,
         names=VOP, label_col=0,
         parts=[dict(names=VOP, labels=items(24, "Item "), rows=seq(1, 24), cols=seq(1, 24))],
         moments=moments("mean", "TABLE 1", VOP, seq(1, 24), 1, labels=items(24, "Item "))
         + moments("sd", "TABLE 1", VOP[:14], seq(1, 14), 2, labels=items(14, "Item "))
         # Item 15's SD is printed "1,00" (a decimal comma in a table of decimal points)
         + moments("sd", "TABLE 1", ["item15"], [15], 2, labels=["Item 15"], comma=True)
         + moments("sd", "TABLE 1", VOP[15:], seq(16, 24), 2, labels=items(24, "Item ")[15:])),
    dict(pmcid="PMC8750684", label="Table 2", table="montanesmuro_2022_ercbs24", n=232,
         names=ERC, label_col=0, label_rx=ERC_RX,
         parts=[dict(names=ERC, labels=[str(i) for i in seq(1, 23)] + ["ERCB-T"],
                     rows=seq(1, 24), cols=seq(1, 24), lower_only=True)],
         moments=moments("mean", "Table 1", ERC[:23], seq(1, 23), 1,
                         labels=[str(i) for i in seq(1, 23)], label_rx=ERC_RX)
         + moments("sd", "Table 1", ERC[:23], seq(1, 23), 2,
                   labels=[str(i) for i in seq(1, 23)], label_rx=ERC_RX)),
    dict(pmcid="PMC11821628", label="Table 6", table="zapataospina_2025_etam22", n=512,
         names=ETAM, label_col=0,
         parts=[dict(names=ETAM, rows=seq(1, 22), cols=seq(1, 22), lower_only=True,
                     asym=ETAM_ASYM)]),
    dict(pmcid="PMC8446468", label="Table 9", table="papamitsiou_2021_edl21", n=210,
         names=EDL, label_col=0,
         parts=[dict(names=EDL, rows=seq(2, 22), cols=seq(2, 22))],
         moments=moments("mean", "Table 9", EDL, seq(2, 22), 1, rx=M_BR)
         + moments("sd", "Table 9", EDL, seq(2, 22), 1, rx=SD_BR)),
    dict(pmcid="PMC12281048", label="Table I.", table="agudelohernandez_2025_ids18", n=204,
         names=IDS, label_col=0, comma=True,
         parts=[dict(names=IDS, labels=[str(i) for i in seq(1, 18)], rows=seq(1, 18),
                     cols=seq(1, 18))],
         moments=moments_row("mean", "Table I.", IDS, 19, seq(1, 18), "M", 0,
                             [str(i) for i in seq(1, 18)], comma=True)
         + moments_row("sd", "Table I.", IDS, 20, seq(1, 18), "DE", 0,
                       [str(i) for i in seq(1, 18)], comma=True)),
    dict(pmcid="PMC10290592", label="Table 3", table="zieff_2023_snapiv18", n=201,
         names=SNAP, label_col=0, span_fill=False,
         parts=[dict(names=SNAP, labels=items(18, "Item "), rows=seq(1, 18),
                     cols=seq(1, 17) + [None])],
         moments=moments("mean", "Table 2", SNAP, seq(3, 11) + seq(13, 21), 9, rx=M_BR,
                         labels=[str(i) for i in seq(1, 18)])
         + moments("sd", "Table 2", SNAP, seq(3, 11) + seq(13, 21), 9, rx=SD_BR,
                   labels=[str(i) for i in seq(1, 18)])),
    dict(pmcid="PMC5156692", label="Table 1", table="martinanton_2016_tops17", n=169,
         names=TOPS, label_col=0, label_rx=NUMLAB,
         parts=[dict(names=TOPS, labels=[str(i) for i in TOPS_NUM], rows=seq(2, 18),
                     cols=seq(1, 17))],
         moments=moments_row("mean", "Table 1", TOPS, 20, seq(1, 17), "M", 0,
                             [str(i) for i in TOPS_NUM])
         + moments_row("sd", "Table 1", TOPS, 21, seq(1, 17), "SD", 0,
                       [str(i) for i in TOPS_NUM])),
    dict(pmcid="PMC7037848", label="Table 2", table="penasanchez_2020_4cornersat17", n=1003,
         names=CSAT, label_col=0,
         parts=[dict(names=CSAT, rows=seq(1, 17), cols=seq(2, 18))]),
    dict(pmcid="PMC5331633", label="Table 4", table="henderson_2017_gainss11", n=2313,
         names=GAIN, label_col=0, label_rx=r"^(\d[a-g]?)\.",
         parts=[dict(names=GAIN, rows=seq(1, 11), cols=seq(1, 10) + [None])]),
    dict(pmcid="PMC8100192", label="Table 4", table="paschke_2021_somedisa10", n=931,
         names=SOM, label_col=0,
         parts=[dict(names=SOM, labels=items(9, "Item ") + ["Timing item"], rows=seq(1, 10),
                     cols=seq(1, 10))]),
    dict(pmcid="PMC5516613", label="Table 4", table="rostiotajarvi_2017_fss9", n=553,
         names=FSS, label_col=0,
         parts=[dict(names=FSS, labels=items(9, "FSS "), rows=seq(1, 9), cols=seq(1, 9))]),
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


def num(cell, where, comma=False):
    s = cell.replace("−", "-").replace("–", "-").replace(" ", "")
    s = re.sub(r"[*∗†⁎]+$", "", s)
    if comma:
        s = s.replace(",", ".")
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


def table_rows(root, label, span_fill=True):
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
                for b in range(cs):  # without span_fill only the first spanned cell holds the text
                    grid[(i + a, j + b)] = txt(c) if span_fill or (a, b) == (0, 0) else ""
            j += cs
    nr = max(k[0] for k in grid) + 1
    return [[grid.get((i, j), "") for j in range(max([k[1] for k in grid if k[0] == i] + [-1]) + 1)]
            for i in range(nr)]


def read_part(cfg, part, rows, where):
    """{frozenset(pair): (value, raw)} for the pairs printed in one panel."""
    names, ridx, cidx = part["names"], part["rows"], part["cols"]
    labels = part.get("labels", names)
    comma = cfg.get("comma", False)
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
        return rows[r][c]

    asym = {frozenset(p) for p in part.get("asym", [])}
    seen_asym = set()
    got = {}
    for i in range(k):
        d = cell(i, i)
        if d is not None and d.strip() not in DIAG:
            raise SystemExit(f"{where}: diagonal {names[i]} is {d!r}")
        for j in range(i):
            a, b = cell(i, j), cell(j, i)       # a: below the diagonal, b: above it
            a = None if a is None or a.strip() in EMPTY else a
            b = None if b is None or b.strip() in EMPTY else b
            key = frozenset((names[i], names[j]))
            if part.get("lower_only"):
                if a is None:
                    raise SystemExit(f"{where}: missing lower cell ({names[i]}, {names[j]})")
                if part.get("asym") is not None:   # a full square: the copies must agree
                    if b is None:
                        raise SystemExit(f"{where}: missing upper cell ({names[j]}, {names[i]})")
                    if num(a, where, comma) != num(b, where, comma):
                        if key not in asym:
                            raise SystemExit(f"{where}: asymmetric ({names[i]}, {names[j]}): {a!r} / {b!r}")
                        seen_asym.add(key)
                b = None
            if a is None and b is None:
                raise SystemExit(f"{where}: missing cell ({names[i]}, {names[j]})")
            if a is not None and b is not None and num(a, where, comma) != num(b, where, comma):
                raise SystemExit(f"{where}: asymmetric ({names[i]}, {names[j]}): {a!r} / {b!r}")
            raw = a if a is not None else b
            v = num(raw, f"{where} ({names[i]},{names[j]})", comma)
            if abs(float(v)) >= 1:
                raise SystemExit(f"{where}: |r| >= 1 at ({names[i]},{names[j]})")
            got[key] = (v, raw)
    if seen_asym != asym:
        raise SystemExit(f"{where}: asymmetric pairs {seen_asym} are not the listed {asym}")
    return got


def build(cfg, root):
    where = f"{cfg['pmcid']} {cfg['label']} {cfg.get('group', '')}".strip()
    rows = table_rows(root, cfg["label"], cfg.get("span_fill", True))
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
        if m.get("hdr"):
            hr, h = m["hdr"]
            if norm(t[hr][m["col"]]) != norm(h):
                raise SystemExit(f"{where}: {m['label']} column {m['col']} is {t[hr][m['col']]!r}, not {h!r}")
        c = t[m["row"]][m["col"]].strip()
        if m.get("rx"):
            hit = re.search(m["rx"], c)
            if not hit:
                raise SystemExit(f"{where}: {m['stat']} cell {c!r} for {m['var']!r}")
            raw = hit.group(1)
        else:
            raw = c
        v = num(raw, f"{where} {m['stat']} {m['var']}", m.get("comma", False))
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
        raise SystemExit("usage: python3 pmc_article_tables_ad.py <out dir>")
    main(sys.argv[1])
