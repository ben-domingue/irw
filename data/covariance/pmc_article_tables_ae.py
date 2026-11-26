"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AE batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article with a retraction notice
(<related-article related-article-type="retraction-forward">) is refused.

Tables built (CONFIGS below): eleven tables (22 matrices) from eleven articles,
vetted from the AC candidate list of 2026-11-18 (Europe PMC searches for "inter-item
correlation matrix", "polychoric correlation matrix" and similar, open access, CC BY /
CC0; the item-level-caption subset, continuing after the articles agent AD vetted).
Ten are item-level matrices of one scale (inter-item correlations), several with item
means and SDs; caychorodriguez_2023_who5 holds one WHO-5 matrix for each of twelve
Latin American countries (12 groups, printed one block per country); kahaki_2022_wdq23
holds the 21 Work Design Questionnaire dimension scores plus job satisfaction and
perceived stress. The N of each is from the caption,
a table note or the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_ad.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions; None means the variable has no printed row (or column) in
that panel. Cells are read as text. Significance stars and daggers are stripped;
nothing else is changed. Unicode minus (U+2212) and an en dash used as a minus are read
as "-", and spaces inside a cell are dropped ("- 0.05" -> -0.05). For each pair of
variables the script reads both cells (row i/column j and row j/column i): exactly one
must hold a number and the other must be empty or a dash, or both must hold the same
number (a full square). A table printed in two panels (kahaki_2022_wdq23: columns 1-11,
then columns 12-22 under a repeated header) is read as two parts; a part reads only the
pairs it prints a number for, and every pair must be read from exactly one part (or
agree where two parts print it).

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or number
of a label (so that item wording printed as a row label is never copied here). Where
the row labels are item wording with no code (boateng_2019_bsesebf11), `label_col` is
None and the printed column numbers are checked instead (`col_labels`, header row and
expected labels). Variable names are the source's item codes (SEA_1, FAAM1, Q1, EMT1,
RQ1, ...) or dimension names; where the source prints only a number or item content,
items are written as item1, item2, ..., never with item wording.

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). They become mean/sd rows, values as printed.

Diagonal cells (1, 1.00, 1.0, 1.000, a dash or blank) are written as 1. Values are
written in shortest round-trip form of the published decimal (for example "0.40" ->
"0.4"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_ae.py <out dir>
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


# --- configs -----------------------------------------------------------------
def mom(stat, label, names, rows, col, hdr_row, hdr, labels=None, label_col=0, label_rx=None):
    """One moment per variable, read from rows[i] of column col of table label; the row
    label (labels[i], or None to skip) and the column header (row hdr_row) are checked."""
    labels = labels or names
    return [dict(stat=stat, var=v, label=label, row=r, col=col, rx=None, lab=l,
                 label_col=label_col, label_rx=label_rx, comma=False, hdr=(hdr_row, hdr))
            for v, r, l in zip(names, rows, labels)]


NUMLAB = r"^(\d+)\."            # "3. <item wording>" -> 3
WLEIS = [f"{d}_{i}" for d in ("SEA", "OEA", "UOE", "ROE") for i in range(1, 5)]
FAAM = ["FAAM" + str(i) for i in (1, 3, 4, 6, 8, 10, 11, 16, 17, 19, 21, 5, 9, 12, 15)]
HQ = items(14, "Q")
EMT = ["EMT" + str(i) for i in (1, 3, 6, 7, 13, 15, 20, 34, 35, 36, 39, 48, 2, 18, 28)]
BSES = items(11)
FSDS_NUM = [1, 2, 3, 4, 5, 6, 8, 9, 11, 13, 14, 15, 16]
FSDS = [f"item{i}" for i in FSDS_NUM]
SASEC = items(12)
VAX = items(12)
MWAS = [f"RQ{i}" for i in range(1, 7)] + [f"RE{i}" for i in range(1, 7)]
WDQ = ["Work scheduling autonomy", "Decision-making autonomy", "Work methods autonomy",
       "Task variety", "Task significance", "Task identity", "Feedback from job",
       "Job complexity", "Information processing", "Problem solving", "Skill variety",
       "Specialization", "Social support", "Initiated interdependence",
       "Received interdependence", "Interaction outside organization",
       "Feedback from others", "Ergonomics", "Physical demands", "Work condition",
       "Equipment use", "Job satisfaction", "Perceived stress"]
NONE11 = [None] * 11

WHO5 = items(5)
WHO5_GROUPS = [("Mexico", 300), ("Guatemala", 324), ("El Salvador", 698), ("Cuba", 317),
               ("Peru", 360), ("Bolivia", 252), ("Ecuador", 451), ("Colombia", 372),
               ("Chile", 524), ("Argentina", 325), ("Uruguay", 383), ("Paraguay", 877)]

CONFIGS = [
    dict(pmcid="PMC9150008", label="Table 5", table="acostaprado_2022_wleis16", n=489,
         names=WLEIS, label_col=0,
         parts=[dict(names=WLEIS, rows=seq(1, 16), cols=seq(1, 16))],
         moments=mom("mean", "Table 2", WLEIS, seq(1, 16), 1, 0, "Mean")
         + mom("sd", "Table 2", WLEIS, seq(1, 16), 2, 0, "Standard Deviation")),
    dict(pmcid="PMC5567466", label="Table 3", table="cerveragarvi_2017_faamadl15", n=194,
         names=FAAM, label_col=0,
         parts=[dict(names=FAAM, rows=seq(1, 15), cols=seq(1, 15))]),
    dict(pmcid="PMC4628763", label="Table 4", table="fackrell_2015_hq14", n=264,
         names=HQ, label_col=1,
         parts=[dict(names=HQ, rows=seq(2, 5) + seq(7, 12) + seq(14, 17), cols=seq(2, 15))]),
    dict(pmcid="PMC10461556", label="Table 10", table="fischer_2023_orgtrust15", n=244,
         names=EMT, label_col=0,
         parts=[dict(names=EMT, rows=seq(1, 15), cols=seq(3, 17))],
         moments=mom("mean", "Table 10", EMT, seq(1, 15), 1, 0, "Mean")
         + mom("sd", "Table 10", EMT, seq(1, 15), 2, 0, "SD")),
    dict(pmcid="PMC6380059", label="Table 2", table="boateng_2019_bsesebf11", n=239,
         names=BSES, label_col=None,
         parts=[dict(names=BSES, rows=seq(2, 12), cols=seq(8, 18),
                     col_labels=(1, [str(i) for i in seq(1, 11)]))],
         moments=mom("mean", "Table 2", BSES, seq(2, 12), 1, 1, "Mean", labels=[None] * 11)),
    dict(pmcid="PMC8363413", label="TABLE 4", table="larsson_2021_fsds13", n=203,
         names=FSDS, label_col=0,
         parts=[dict(names=FSDS, labels=[f"Item {i}" for i in FSDS_NUM], rows=seq(1, 13),
                     cols=seq(1, 13))]),
    dict(pmcid="PMC10006262", label="Table 3", table="boyer_2023_sasec12", n=147,
         names=SASEC, label_col=0,
         parts=[dict(names=SASEC, labels=[str(i) for i in seq(1, 12)], rows=seq(1, 12),
                     cols=seq(1, 12))],
         moments=mom("mean", "Table 4", SASEC, seq(1, 12), 1, 0, "M",
                     labels=[str(i) for i in seq(1, 12)])
         + mom("sd", "Table 4", SASEC, seq(1, 12), 2, 0, "SD",
               labels=[str(i) for i in seq(1, 12)])),
    dict(pmcid="PMC10537843", label="Table 1", table="padmanabhanunni_2023_vax12", n=322,
         names=VAX, label_col=0, label_rx=NUMLAB,
         parts=[dict(names=VAX, labels=[str(i) for i in seq(1, 12)], rows=seq(2, 13),
                     cols=seq(1, 12), col_labels=(1, [str(i) for i in seq(1, 12)]))]),
    dict(pmcid="PMC12089860", label="Table 2.", table="rogers_2025_mwas12", n=345,
         names=MWAS, label_col=0, label_rx=r"^(R[QE]\d):",
         parts=[dict(names=MWAS, rows=seq(1, 12), cols=seq(3, 14), col_labels=(0, MWAS))],
         moments=mom("mean", "Table 2.", MWAS, seq(1, 12), 1, 0, "M", label_rx=r"^(R[QE]\d):")
         + mom("sd", "Table 2.", MWAS, seq(1, 12), 2, 0, "(SD)", label_rx=r"^(R[QE]\d):")),
    dict(pmcid="PMC9484222", label="Table 3", table="kahaki_2022_wdq23", n=270,
         names=WDQ, label_col=0, label_rx=r"^\d+\.\s*(.+)$",
         parts=[dict(names=WDQ, rows=seq(1, 23), cols=seq(1, 11) + [None] * 12,
                     col_labels=(0, [str(i) for i in seq(1, 11)])),
                dict(names=WDQ, rows=seq(25, 47), cols=NONE11 + seq(1, 11) + [None],
                     col_labels=(24, [str(i) for i in seq(12, 22)]))]),
] + [
    # Caycho-Rodriguez et al. (2023), Table 2: one block of five rows per country, in the
    # printed order; the block title ("Mexico (n = 300)") is checked as printed.
    dict(pmcid="PMC10078082", label="Table 2", table="caychorodriguez_2023_who5",
         group=country, n=n, title=(2 + 5 * g, 0, f"{country} (n = {n})"),
         names=WHO5, label_col=1,
         parts=[dict(names=WHO5, labels=[str(i) for i in seq(1, 5)],
                     rows=seq(2 + 5 * g, 6 + 5 * g), cols=seq(6, 10),
                     col_labels=(1, [str(i) for i in seq(1, 5)]))],
         moments=mom("mean", "Table 2", WHO5, seq(2 + 5 * g, 6 + 5 * g), 2, 0, "M",
                     labels=[str(i) for i in seq(1, 5)], label_col=1)
         + mom("sd", "Table 2", WHO5, seq(2 + 5 * g, 6 + 5 * g), 3, 0, "SD",
               labels=[str(i) for i in seq(1, 5)], label_col=1))
    for g, (country, n) in enumerate(WHO5_GROUPS)
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
        if r is not None and cfg["label_col"] is not None:
            lab = label_of(rows[r][cfg["label_col"]], cfg.get("label_rx"), where)
            if norm(lab) != norm(nm):
                raise SystemExit(f"{where}: row label {lab!r} is not {nm!r}")
    if part.get("col_labels"):          # printed column headers must be the expected ones
        hr, hl = part["col_labels"]
        got_cols = [c for c in cidx if c is not None]
        if len(got_cols) != len(hl):
            raise SystemExit(f"{where}: bad col_labels config")
        for c, h in zip(got_cols, hl):
            if norm(rows[hr][c]) != norm(h):
                raise SystemExit(f"{where}: column {c} header {rows[hr][c]!r} is not {h!r}")

    def cell(a, b):
        r, c = ridx[a], cidx[b]
        if r is None or c is None or c >= len(rows[r]):
            return None
        return rows[r][c]

    def absent(a, b):                   # no printed position for this cell in this part
        return ridx[a] is None or cidx[b] is None

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
                if absent(i, j) or absent(j, i):   # the pair is printed in another panel
                    continue
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
    if cfg.get("title"):                # a block title printed in the table (group, n)
        tr, tc, tt = cfg["title"]
        if rows[tr][tc].strip() != tt:
            raise SystemExit(f"{where}: block title {rows[tr][tc]!r} is not {tt!r}")
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
        if m["lab"] is not None:            # None: the row label is item wording (not checked)
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
        raise SystemExit("usage: python3 pmc_article_tables_ae.py <out dir>")
    main(sys.argv[1])
