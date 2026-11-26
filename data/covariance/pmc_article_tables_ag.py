"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AG batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article with a retraction notice
(<related-article related-article-type="retraction-forward">) is refused.

Tables built (CONFIGS below): eleven tables (12 matrices) from eleven articles,
vetted from the AC candidate list of 2026-11-18 (Europe PMC searches for "inter-item
correlation matrix", "polychoric correlation matrix" and similar, open access, CC BY /
CC0; the item-level-caption subset, continuing after the articles agent AF vetted).
Each is an item-level matrix of one scale (inter-item correlations), some with item
means and SDs. aguilarraab_2015_evos9 holds two samples printed in one square (Study 1
above the diagonal, Study 2 below; 2 groups). duman_2019_ipat10 and halman_2018_ocat9
are printed as full squares, whose two copies of each cell are checked to agree. The N
of each is from the caption, a table note or the article text, as noted in
matrices.csv.

Parsing: as pmc_article_tables_af.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions. Cells are read as text. Significance stars and daggers are
stripped, and so is a footnote letter where a config names it (`strip`: the "a" after
each cell of razki_2023_iped8, Table 2); nothing else is changed. Unicode minus
(U+2212) and an en dash used as a minus are read as "-", and spaces inside a cell are
dropped. For each pair of variables the script reads both cells (row i/column j and
row j/column i): exactly one must hold a number and the other must be empty or a dash,
or both must hold the same number (a full square). A part may instead read only the
lower (`lower_only`) or only the upper (`upper_only`) triangle, when the other
triangle holds a second sample (aguilarraab_2015_evos9).

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or number of
a label (so that item wording printed as a row label is never copied here). Printed
column headers are checked too (`col_labels`). Where both the row labels and the column
headers are item wording (rogers_2025_pesns9), `label_col` is None and each row label
is instead checked to equal the column header of the same item (`same_labels`), so the
wording is compared but never written down. Variable names are the source's item codes
(I1, IPAT_1, Q1, COM, ...); where the source prints only a number or item content,
items are written as item1, item2, ..., never with item wording.

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). Moments printed one column per variable (pretorius_2022_pis10, Table 2) use
`mom_t`; a "M (SD)" cell (diviani_2017_eheals8, Table 1) is split by a regex (`rx`).
Where the moment's row label is item wording, it is checked to equal the matrix row
label of the same item (`lab_ref`; rogers_2025_pesns9, Table 1, whose items are printed
in a different order from Table 4). They become mean/sd rows, values as printed.

Diagonal cells (1, 1.00, 1.0, 1.000, a dash or blank) are written as 1. Values are
written in shortest round-trip form of the published decimal (for example "0.40" ->
"0.4", ".800" -> "0.8"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_ag.py <out dir>
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
    label (labels[i]; a ("ref", table, row, col, prefix) tuple names a cell whose text the label
    must equal) and the column header (row hdr_row) are checked."""
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
MSD_M, MSD_SD = r"^(-?[\d.,]+) \(", r"\(([\d.,]+)\)$"   # "3.56 (0.996)"

PIS = items(10)
IPAT = [f"IPAT_{i}" for i in seq(1, 10)]
IDAF = [f"I{i}" for i in seq(1, 8)]
PESNS = items(9)
PESNS_T1 = [38, 43, 48, 3, 8, 14, 20, 25, 31]   # Table 1 row of each Table 4 item
CUAFYS = items(9)
TDS = items(8)
IPED = items(8)
EDS = items(8)
EHEALS = items(8)
EVOS = ["COM", "COH", "G&T", "ATM", "AIM", "RES", "DEC", "SOL", "ADA"]
EVOS_LAB = ["communication", "cohesion", "giving and taking", "atmosphere", "aims", "resources",
            "decisions", "solutions", "adaptability"]
OCAT = [f"Q{i}" for i in seq(1, 9)]

CONFIGS = [
    # Pretorius et al. (2022), Table 2: lower triangle, dash diagonal; item wording as row
    # labels ("1. ..."); Mean and SD rows under the matrix (the Rasch/Mokken rows are not read).
    dict(pmcid="PMC9365210", label="Table 2", table="pretorius_2022_pis10", n=355,
         names=PIS, label_col=0, label_rx=NUMLAB,
         parts=[dict(names=PIS, labels=NUMS(1, 10), rows=seq(1, 10), cols=seq(1, 10),
                     col_labels=(0, NUMS(1, 10)))],
         moments=mom_t("mean", "Table 2", PIS, 11, seq(1, 10), "Mean", hdrs=NUMS(1, 10))
         + mom_t("sd", "Table 2", PIS, 12, seq(1, 10), "SD", hdrs=NUMS(1, 10))),
    # Duman et al. (2019), Table 3: full square (both copies checked to agree).
    dict(pmcid="PMC7018335", label="Table 3", table="duman_2019_ipat10", n=98,
         names=IPAT, label_col=0,
         parts=[dict(names=IPAT, rows=seq(1, 10), cols=seq(1, 10), col_labels=(0, IPAT),
                     lower_only=True, asym=[])]),
    # Done et al. (2023), Table 1: upper triangle, dash diagonal; item means (no SDs); the
    # corrected item-total and alpha-if-deleted columns are not read.
    dict(pmcid="PMC10419272", label="Table 1", table="done_2023_idaf8", n=239,
         names=IDAF, label_col=0,
         parts=[dict(names=IDAF, rows=seq(2, 9), cols=seq(2, 9), col_labels=(1, IDAF))],
         moments=mom("mean", "Table 1", IDAF, seq(2, 9), 1, 1, "Mean")),
    # Rogers & Parulekar (2025), Table 4: upper triangle; rows and columns are item wording,
    # so each row label is checked against the column header of the same item; means and
    # SDs from Table 1 (a different item order), matched by the printed wording (for the
    # fourth item, whose Table 1 wording spells out an abbreviation that Table 4 uses, by
    # the first 50 letters and digits).
    dict(pmcid="PMC12747458", label="Table 4.", table="rogers_2025_pesns9", n=262,
         names=PESNS, label_col=None,
         parts=[dict(names=PESNS, rows=seq(1, 9), cols=seq(1, 9), same_labels=(0, 0),
                     col_labels=(0, None))],
         moments=[dict(m, lab=("ref", "Table 4.", r4, 0, 50 if r4 == 4 else None))
                  for st, col, h in (("mean", 2, "Mean"), ("sd", 3, "SD"))
                  for m, r4 in zip(mom(st, "Table 1.", PESNS, PESNS_T1, col, 0, h), seq(1, 9))]),
    # Moreno-Lavaho et al. (2024), Table A2: the polychoric matrix (Table 3, Pearson with
    # item variances on the diagonal, is not taken).
    dict(pmcid="PMC10815366", label="Table A2", table="morenolavaho_2024_paknow9", n=321,
         names=CUAFYS, label_col=0,
         parts=[dict(names=CUAFYS, labels=NUMS(1, 9), rows=seq(1, 9), cols=seq(1, 9),
                     col_labels=(0, NUMS(1, 9)))]),
    # Plesec et al. (2024), Table 3: lower triangle; item wording as row labels ("1. ...");
    # the item-total column and the average/alpha rows are not read.
    dict(pmcid="PMC11675277", label="Table 3", table="plesec_2024_tdshf8", n=159,
         names=TDS, label_col=0, label_rx=NUMLAB,
         parts=[dict(names=TDS, labels=NUMS(1, 8), rows=seq(2, 9), cols=seq(2, 9),
                     col_labels=(1, NUMS(1, 8)))]),
    # Razki et al. (2023), Table 2: lower triangle, each value followed by a footnote "a";
    # the item-total row is not read.
    dict(pmcid="PMC10506069", label="TABLE 2", table="razki_2023_iped8", n=2011,
         names=IPED, label_col=0, strip=r"a$",
         parts=[dict(names=IPED, labels=[f"Item {i}" for i in seq(1, 8)], rows=seq(1, 8),
                     cols=seq(1, 8), col_labels=(0, [f"Item {i}" for i in seq(1, 8)]))]),
    # Ulusoy et al. (2023), Table 4 (Pearson, lower triangle; the item-total column is not
    # read) with item means and SDs from Table 3.
    dict(pmcid="PMC10250171", label="Table 4", table="ulusoy_2023_eds8", n=302,
         names=EDS, label_col=0,
         parts=[dict(names=EDS, labels=[f"Item {i}" for i in seq(1, 8)], rows=seq(2, 9),
                     cols=seq(1, 8), col_labels=(1, [f"Item {i}" for i in seq(1, 8)]))],
         moments=mom("mean", "Table 3", EDS, seq(1, 8), 1, 0, "Mean", labels=NUMS(1, 8))
         + mom("sd", "Table 3", EDS, seq(1, 8), 2, 0, "SD", labels=NUMS(1, 8))),
    # Diviani et al. (2017), Table 1: lower triangle; "Mean (SD)" cells split.
    dict(pmcid="PMC5405289", label="Table 1", table="diviani_2017_eheals8", n=296,
         names=EHEALS, label_col=0,
         parts=[dict(names=EHEALS, labels=NUMS(1, 8), rows=seq(2, 9), cols=seq(4, 11),
                     col_labels=(1, NUMS(1, 8)))],
         moments=[dict(m, rx=rx) for st, rx in (("mean", MSD_M), ("sd", MSD_SD))
                  for m in mom(st, "Table 1", EHEALS, seq(2, 9), 1, 1, "Mean (SDa)",
                               labels=NUMS(1, 8))]),
] + [
    # Aguilar-Raab et al. (2015), Table 2: Study 1 above the diagonal, Study 2 below.
    dict(pmcid="PMC4511583", label="Table 2", table="aguilarraab_2015_evos9", group=g, n=n,
         names=EVOS, label_col=0,
         parts=[dict(names=EVOS, labels=EVOS_LAB, rows=seq(1, 9), cols=seq(1, 9),
                     col_labels=(0, EVOS), **{side: True})])
    for g, n, side in (("Study 1", 537, "upper_only"), ("Study 2", 558, "lower_only"))
] + [
    # Halman et al. (2018), Table 5 (Appendix 2): full square (both copies checked to agree).
    dict(pmcid="PMC6148769", label="Table 5", table="halman_2018_ocat9", n=390,
         names=OCAT, label_col=0,
         parts=[dict(names=OCAT, rows=seq(1, 9), cols=seq(1, 9), col_labels=(0, OCAT),
                     lower_only=True, asym=[])]),
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
    for attempt in range(6):  # Europe PMC sometimes answers with an HTTP 5xx or an HTML error page
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                b = r.read()
            if b.lstrip()[:1] == b"<" and b"<article" in b[:3000]:
                return b
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"{pmcid}: {e}; retrying", file=sys.stderr)
        time.sleep(10 * (attempt + 1))
    raise SystemExit(f"{pmcid}: no article XML from Europe PMC")


def num(cell, where, comma=False, strip=None):
    s = cell.replace("−", "-").replace("–", "-").replace(" ", "")
    if strip:
        s = re.sub(strip, "", s)
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
    comma, strip = cfg.get("comma", False), cfg.get("strip")
    k = len(names)
    if len(ridx) != k or len(cidx) != k or len(labels) != k:
        raise SystemExit(f"{where}: bad part config")
    for nm, r in zip(labels, ridx):  # printed row labels must be the expected ones
        if r is not None and cfg["label_col"] is not None:
            lab = label_of(rows[r][cfg["label_col"]], cfg.get("label_rx"), where)
            if norm(lab) != norm(nm):
                raise SystemExit(f"{where}: row label {lab!r} is not {nm!r}")
    if part.get("same_labels"):         # row label i must equal column header i (item wording)
        lc, hr = part["same_labels"]
        for a, (r, c) in enumerate(zip(ridx, cidx)):
            if not norm(rows[r][lc]) or norm(rows[r][lc]) != norm(rows[hr][c]):
                raise SystemExit(f"{where}: row {r} label is not column {c} header")
        if len({norm(rows[r][lc]) for r in ridx}) != k:
            raise SystemExit(f"{where}: repeated row labels")
    if part.get("col_labels") and part["col_labels"][1] is not None:  # printed column headers
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
            if part.get("upper_only"):          # the lower triangle holds another sample
                if b is None:
                    raise SystemExit(f"{where}: missing upper cell ({names[j]}, {names[i]})")
                a = None
            if part.get("lower_only"):
                if a is None:
                    raise SystemExit(f"{where}: missing lower cell ({names[i]}, {names[j]})")
                if part.get("asym") is not None:   # a full square: the copies must agree
                    if b is None:
                        raise SystemExit(f"{where}: missing upper cell ({names[j]}, {names[i]})")
                    if num(a, where, comma, strip) != num(b, where, comma, strip):
                        if key not in asym:
                            raise SystemExit(f"{where}: asymmetric ({names[i]}, {names[j]}): {a!r} / {b!r}")
                        seen_asym.add(key)
                b = None
            if a is None and b is None:
                if absent(i, j) or absent(j, i):   # the pair is printed in another panel
                    continue
                raise SystemExit(f"{where}: missing cell ({names[i]}, {names[j]})")
            if a is not None and b is not None and num(a, where, comma, strip) != num(b, where, comma, strip):
                raise SystemExit(f"{where}: asymmetric ({names[i]}, {names[j]}): {a!r} / {b!r}")
            raw = a if a is not None else b
            v = num(raw, f"{where} ({names[i]},{names[j]})", comma, strip)
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
        if isinstance(m["lab"], tuple):     # the label must equal the text of a named cell
            _, rl, rr, rc, pre = m["lab"]   # pre: compare only the first `pre` letters/digits
            want = norm(table_rows(root, rl)[rr][rc])[:pre]
            if not want or norm(t[m["row"]][m["label_col"]])[:pre] != want:
                raise SystemExit(f"{where}: {m['label']} row {m['row']} is not {rl} row {rr}")
        elif m["lab"] is not None:          # None: the row label is item wording (not checked)
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
        raise SystemExit("usage: python3 pmc_article_tables_ag.py <out dir>")
    main(sys.argv[1])
