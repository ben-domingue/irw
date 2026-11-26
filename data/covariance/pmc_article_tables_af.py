"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AF batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article with a retraction notice
(<related-article related-article-type="retraction-forward">) is refused.

Tables built (CONFIGS below): thirteen tables (24 matrices) from eleven articles,
vetted from the AC candidate list of 2026-11-18 (Europe PMC searches for "inter-item
correlation matrix", "polychoric correlation matrix" and similar, open access, CC BY /
CC0; the item-level-caption subset, continuing after the articles agents AD and AE
vetted). Each is an item-level matrix of one scale or domain (inter-item correlations),
some with item means and SDs. kang_2022_obsqor12 adds the global health NRS, printed as
a column of correlations with the items; swain_2022_perfusion10 holds the perfusion
index measured on ten fingers; the three stanifer_2015_ckd* tables are the three domain
blocks of one printed table (the same 606 respondents); caychorodriguez_2021_pcibs5
holds one matrix for each of twelve Latin American countries (12 groups, printed one
block per country; the same samples as caychorodriguez_2023_who5). The N of each is
from the caption, a block title, a table note or the article text, as noted in
matrices.csv.

Parsing: as pmc_article_tables_ae.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions; None means the variable has no printed row (or column) in
that panel. Cells are read as text. Significance stars and daggers are stripped;
nothing else is changed. Unicode minus (U+2212) and an en dash used as a minus are read
as "-", and spaces inside a cell are dropped ("- 0.05" -> -0.05). For each pair of
variables the script reads both cells (row i/column j and row j/column i): exactly one
must hold a number and the other must be empty or a dash, or both must hold the same
number (a full square). A table may be read as several parts (panels); a part reads
only the pairs it prints a number for, and every pair must be read from exactly one
part (or agree where two parts print it). A variable printed only as a column (the
global health NRS of kang_2022_obsqor12) has row None.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or number
of a label (so that item wording printed as a row label is never copied here). Where
the row labels are item wording with no code, `label_col` is
None and the printed column numbers are checked instead (`col_labels`, header row and
expected labels). Block titles of grouped or stacked tables are checked as printed
(`title`). Variable names are the source's item codes (M1, R1, P2, ...); where the source prints only a number or item content,
items are written as item1, item2, ..., never with item wording.

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). Moments printed one column per variable (swain_2022_perfusion10, Table 2) use
`mom_t`; a "M (SD)" cell (perski_2020_dbci10, Table 2) is split by a regex (`rx`).
They become mean/sd rows, values as printed.

Diagonal cells (1, 1.00, 1.0, 1.000, 1.0000, a dash, a hyphen or blank) are written as
1. Values are written in shortest round-trip form of the published decimal (for example
"0.40" -> "0.4", "-.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_af.py <out dir>
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


def mom_t(stat, label, names, row, cols, lab, hdr_row=0, hdrs=None):
    """Moments printed one column per variable (a row per statistic): the row label (lab)
    and each column header (hdrs[i], or the variable name) are checked."""
    hdrs = hdrs or names
    return [dict(stat=stat, var=v, label=label, row=row, col=c, rx=None, lab=lab, label_col=0,
                 label_rx=None, comma=False, hdr=(hdr_row, h))
            for v, c, h in zip(names, cols, hdrs)]


NUMLAB = r"^(\d+)\."            # "3. <item wording>" -> 3
NUMS = lambda a, b: [str(i) for i in seq(a, b)]

OBSQOR = ["global_nrs"] + items(11)
MOTIV = [f"M{i}" for i in seq(1, 11)]
SSOD = items(11)
PI = ["R1", "R2", "R3", "R4", "R5", "L1", "L2", "L3", "L4", "L5"]
HBMP = ["P2", "P3", "P4", "P7", "P8", "P9", "P10", "P11", "P12", "P13", "P14"]
PRAQ_NUM = [1, 2, 6, 4, 8, 9, 10, 3, 5, 7]
PRAQ = [f"item{i}" for i in PRAQ_NUM]
PPS = items(10)
MPPUS = items(10)
DBCI = items(10)
CKD_K = [f"item{i}" for i in seq(1, 10)]
CKD_A = [f"item{i}" for i in seq(11, 18)]
CKD_P = [f"item{i}" for i in seq(19, 26)]
ITEMLAB = r"^Item (\d+)"         # "Item 3 (<item content>)" -> 3

PCIBS = items(5)
PCIBS_GROUPS = [("Mexico", 300), ("Guatemala", 324), ("El Salvador", 698), ("Cuba", 317),
                ("Peru", 360), ("Bolivia", 252), ("Ecuador", 451), ("Colombia", 372),
                ("Chile", 524), ("Argentina", 325), ("Uruguay", 383), ("Paraguay", 877)]

CONFIGS = [
    # Kang et al. (2022), Table 4: the global health NRS column is a variable with no row
    # (its correlations with the items are printed as the first column); the "Total
    # ObsQoR-11K Score" column (item-total) is not read.
    dict(pmcid="PMC8871019", label="Table 4", table="kang_2022_obsqor12", n=120,
         names=OBSQOR, label_col=0,
         parts=[dict(names=OBSQOR, labels=["global"] + NUMS(1, 11), rows=[None] + seq(1, 11),
                     cols=[1] + seq(3, 13), col_labels=(0, ["Global Health NRS ¥"] + NUMS(1, 11)))]),
    dict(pmcid="PMC4429816", label="Table 3", table="morrison_2015_motivation11", n=137,
         names=MOTIV, label_col=0,
         parts=[dict(names=MOTIV, rows=seq(1, 11), cols=seq(1, 11), col_labels=(0, MOTIV))]),
    dict(pmcid="PMC12062546", label="Table 3.", table="fereidooni_2024_ssod11", n=143,
         names=SSOD, label_col=0, label_rx=NUMLAB,
         parts=[dict(names=SSOD, labels=NUMS(1, 11), rows=seq(1, 11), cols=seq(1, 11),
                     col_labels=(0, NUMS(1, 11)))]),
    dict(pmcid="PMC9176686", label="Table 3", table="swain_2022_perfusion10", n=391,
         names=PI, label_col=0,
         parts=[dict(names=PI, rows=seq(1, 10), cols=seq(1, 10), col_labels=(0, PI))],
         moments=mom_t("mean", "Table 2", PI, 1, seq(1, 10), "Mean")
         + mom_t("sd", "Table 2", PI, 2, seq(1, 10), "Standard deviation")),
    dict(pmcid="PMC9770370", label="Table 5", table="tareke_2022_hbmpractice11", n=576,
         names=HBMP, label_col=0,
         parts=[dict(names=HBMP, rows=seq(2, 12), cols=seq(1, 11), col_labels=(1, HBMP))]),
    dict(pmcid="PMC10341067", label="Table A2", table="shirabe_2023_praqr2_10", n=112,
         names=PRAQ, label_col=0,
         parts=[dict(names=PRAQ, labels=[str(i) for i in PRAQ_NUM], rows=seq(1, 10),
                     cols=seq(1, 10), col_labels=(0, [str(i) for i in PRAQ_NUM]))]),
    dict(pmcid="PMC6980607", label="Table 2", table="footer_2020_pps10", n=250,
         names=PPS, label_col=0,
         parts=[dict(names=PPS, labels=NUMS(1, 10), rows=seq(1, 10), cols=seq(2, 11))]),
    dict(pmcid="PMC7283544", label="Table 2", table="mach_2020_mppus10", n=629,
         names=MPPUS, label_col=0,
         parts=[dict(names=MPPUS, labels=NUMS(1, 10), rows=seq(1, 10), cols=seq(1, 10),
                     col_labels=(0, NUMS(1, 10)))]),
    dict(pmcid="PMC8411853", label="Table 3", table="perski_2020_dbci10", n=203,
         names=DBCI, label_col=0, label_rx=NUMLAB,
         parts=[dict(names=DBCI, labels=NUMS(1, 10), rows=seq(1, 10), cols=seq(1, 10),
                     col_labels=(0, [f"{i}." for i in seq(1, 10)]))],
         moments=[dict(m, rx=rx) for st, rx in (("mean", r"^(-?[\d.,]+) \("), ("sd", r"\(([\d.,]+)\)$"))
                  for m in mom(st, "Table 2", DBCI, seq(2, 11), 2, 0, "Mean (SD)",
                               labels=NUMS(1, 10), label_rx=NUMLAB)]),
] + [
    # Stanifer et al. (2015), Table 3a-c: three domain matrices printed one under another
    # in one table; each is its own IRW table (the same 606 respondents).
    dict(pmcid="PMC4374886", label="Table 3", table=t, n=606, names=nm, label_col=0, label_rx=ITEMLAB,
         title=(tr, 0, tt),
         parts=[dict(names=nm, labels=[x[4:] for x in nm], rows=seq(r0, r0 + len(nm) - 1),
                     cols=seq(1, len(nm)), col_labels=(r0 - 1, [f"Item {x[4:]}" for x in nm]))])
    for t, nm, r0, tr, tt in (
        ("stanifer_2015_ckdknowledge10", CKD_K, 2, 0, "3a. Correlation among items within the knowledge domain *"),
        ("stanifer_2015_ckdattitudes8", CKD_A, 14, 12, "3b. Correlation among items within the attitudes domain †"),
        ("stanifer_2015_ckdpractices8", CKD_P, 24, 22, "3c. Correlation among items within the practices domain ‡"))
] + [
    # Caycho-Rodriguez et al. (2021), Table 3: one block of five rows per country, in the
    # printed order; the block title ("Mexico (n = 300)") is checked as printed.
    dict(pmcid="PMC8634949", label="TABLE 3", table="caychorodriguez_2021_pcibs5",
         group=country, n=n, title=(2 + 5 * g, 0, f"{country} (n = {n})"),
         names=PCIBS, label_col=1,
         parts=[dict(names=PCIBS, labels=NUMS(1, 5), rows=seq(2 + 5 * g, 6 + 5 * g), cols=seq(6, 10),
                     col_labels=(1, NUMS(1, 5)))],
         moments=mom("mean", "TABLE 3", PCIBS, seq(2 + 5 * g, 6 + 5 * g), 2, 0, "M",
                     labels=NUMS(1, 5), label_col=1)
         + mom("sd", "TABLE 3", PCIBS, seq(2 + 5 * g, 6 + 5 * g), 3, 0, "SD",
               labels=NUMS(1, 5), label_col=1))
    for g, (country, n) in enumerate(PCIBS_GROUPS)
]

DIAG = {"1", "-", "–", "—", "‐", "", "1.00", "1.0", "1.000", "1.0000"}
EMPTY = {"", "-", "–", "—", "‐", "--"}


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
        raise SystemExit("usage: python3 pmc_article_tables_af.py <out dir>")
    main(sys.argv[1])
