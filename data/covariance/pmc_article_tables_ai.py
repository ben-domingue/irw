"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AI batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article whose own metadata
(<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article
(PMC9798258 and PMC7714254 cite retracted papers), so they are not read.

Tables built (CONFIGS below): twelve tables (13 matrices) from twelve articles, vetted
from the AC candidate list of 2026-11-18 (Europe PMC searches for "inter-item
correlation matrix", "polychoric correlation matrix" and similar, open access, CC BY /
CC0; the item-level-caption subset, continuing after the articles agent AH vetted).
Each is an item-level matrix of one scale (inter-item correlations), several with item
means and SDs. stewart_2020_chymhanx6 holds two samples (groups ChYMH and ChYMH-DD). The N
of each is from the caption, a table note or the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_ah.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions. Cells are read as text. Significance stars and daggers are
stripped; a printed 95% CI after a coefficient (stewart_2020_chymhanx6) is stripped
(`strip`); nothing else is changed. Unicode minus (U+2212) and an en dash used as a
minus are read as "-", and spaces inside a cell are dropped. For each pair of variables
the script reads both cells (row i/column j and row j/column i): exactly one must hold
a number and the other must be empty or a dash, or both must hold the same number.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or number of
a label (so that item wording printed as a row label is never copied here). Printed
column headers are checked too (`col_labels`). A block title printed inside the table
(the sample name of each ChYMH panel) is checked (`title`). Variable names are the
source's item codes or labels (P2, CHE_1, BWS1, A1, PPFVD1, Chewing, ...); where the
source prints only a number or item content, items are written as item1, item2, ...,
never with item wording.

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). "M (SD)" and "M ± SD" cells are split by a regex (`rx`). They become mean/sd
rows, values as printed.

Diagonal cells (1, 1.00, 1.0, 1.000, a dash or blank; in montagni_2022_dvl7 the first dash
carries a footnote mark, `diag_extra`) are written as 1. Values are written in shortest
round-trip form of the published decimal (for example "0.40" -> "0.4", ".800" -> "0.8"),
i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_ai.py <out dir>
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
    label (labels[i]) and the column header (row hdr_row) are checked."""
    labels = labels or names
    return [dict(stat=stat, var=v, label=label, row=r, col=col, rx=None, lab=l,
                 label_col=label_col, label_rx=label_rx, comma=False, hdr=(hdr_row, hdr))
            for v, r, l in zip(names, rows, labels)]


NUMLAB = r"^(\d+)\."            # "3. <item wording>" -> 3
NUMS = lambda a, b: [str(i) for i in seq(a, b)]
MSD_M, MSD_SD = r"^(-?[\d.,]+) \(", r"\(([\d.,]+)\)$"   # "7.08 (1.97)"

MSD_PM_M, MSD_PM_SD = r"^(-?[\d.]+) ± ", r" ± ([\d.]+)$"   # "4.68 ± 2.31"
CI = r"\(.*\)$"                 # ".546 (.519–.575)" -> .546

OIDP = ["Chewing", "Talking", "Cleaning", "Sleeping", "Smiling", "Emotion", "Activities", "Enjoying"]
HDCQ = ["P2", "P3", "P5_rev", "P6", "P7", "P8", "P9"]
CHE = [f"CHE_{i}" for i in seq(1, 7)]
BWS = [f"BWS{i}" for i in seq(1, 7)]
BWS_LAB = [f"BWS {i}" for i in seq(1, 7)]
SDT = [f"A{i}" for i in seq(1, 7)]
PPFVD = [f"PPFVD{i}" for i in seq(1, 6)]


def row_mom(stat, label, names, row, cols, lab, hdr_row, hdrs, label_col=0):
    """One moment per variable, read from one row (label `lab`) across columns cols; each
    column header (row hdr_row) is checked."""
    return [dict(stat=stat, var=v, label=label, row=row, col=c, rx=None, lab=lab,
                 label_col=label_col, label_rx=None, comma=False, hdr=(hdr_row, h))
            for v, c, h in zip(names, cols, hdrs)]


def chymh(group, n, title_row, first):
    """Stewart et al. (2020), Table 4: one panel per sample, lower triangle, dash diagonal,
    each coefficient followed by its 95% CI (stripped); rows "1. <item label>"."""
    names = items(6)
    return dict(pmcid="PMC7390192", label="Table 4", table="stewart_2020_chymhanx6", n=n,
                group=group, names=names, label_col=0, label_rx=NUMLAB, strip=CI,
                title=(title_row, 0, f"{group} Sample"),
                parts=[dict(names=names, labels=NUMS(1, 6), rows=seq(first, first + 5),
                            cols=seq(1, 6), col_labels=(1, NUMS(1, 6)))])


CONFIGS = [
    # Amilani et al. (2020), Table 4: lower triangle, 1.0 diagonal; the eight performances
    # named as printed.
    dict(pmcid="PMC6975056", label="Table 4", table="amilani_2020_oidp8", n=220,
         names=OIDP, label_col=0,
         parts=[dict(names=OIDP, rows=seq(1, 8), cols=seq(1, 8), col_labels=(0, OIDP))]),
    # Aridi et al. (2025), Table 10: polychoric, upper triangle, 1.000 diagonal (the seven
    # 3-point performance items; binary items P1 and P4 not analysed).
    dict(pmcid="PMC11955105", label="Table 10", table="aridi_2025_hdcqperf7", n=750,
         names=HDCQ, label_col=0,
         parts=[dict(names=HDCQ, rows=seq(1, 7), cols=seq(1, 7), col_labels=(0, HDCQ))]),
    # Jiao et al. (2022), Table 1: lower triangle, 1 diagonal; item wording as row labels.
    dict(pmcid="PMC9455677", label="Table 1", table="jiao_2022_emoselfeff7", n=441,
         names=items(7), label_col=0, label_rx=NUMLAB,
         parts=[dict(names=items(7), labels=NUMS(1, 7), rows=seq(1, 7), cols=seq(1, 7),
                     col_labels=(0, NUMS(1, 7)))]),
    # Caycho-Rodriguez et al. (2022), Table 3: polychoric, lower triangle under two header
    # rows, item wording as row labels; Mean and Standard deviation rows below the matrix.
    dict(pmcid="PMC9702644", label="Table 3", table="caychorodriguez_2022_mfs7", n=451,
         names=items(7), label_col=0, label_rx=NUMLAB,
         parts=[dict(names=items(7), labels=NUMS(1, 7), rows=seq(2, 8), cols=seq(1, 7),
                     col_labels=(1, NUMS(1, 7)))],
         moments=row_mom("mean", "Table 3", items(7), 9, seq(1, 7), "Mean", 1, NUMS(1, 7))
         + row_mom("sd", "Table 3", items(7), 10, seq(1, 7), "Standard deviation", 1, NUMS(1, 7))),
    # Guevara-Perez et al. (2022), Table 5: polychoric, lower triangle, rows numbered 1-7;
    # item means and SDs from Table 2 (item 8, excluded after the EFA, is not taken).
    dict(pmcid="PMC8997617", label="Table 5", table="guevaraperez_2022_canoetalent7", n=167,
         names=items(7), label_col=0,
         parts=[dict(names=items(7), labels=NUMS(1, 7), rows=seq(1, 7), cols=seq(1, 7),
                     col_labels=(0, NUMS(1, 7)))],
         moments=mom("mean", "Table 2", items(7), seq(1, 7), 1, 0, "Mean", labels=NUMS(1, 7))
         + mom("sd", "Table 2", items(7), seq(1, 7), 2, 0, "SD", labels=NUMS(1, 7))),
    # Montagni et al. (2022), Table 4: polychoric, lower triangle; the diagonal and the
    # upper triangle are dashes (the first with footnote mark a).
    dict(pmcid="PMC9798258", label="Table 4", table="montagni_2022_dvl7", n=848,
         names=items(7), label_col=0, diag_extra={"—a"},
         parts=[dict(names=items(7), labels=NUMS(1, 7), rows=seq(1, 7), cols=seq(1, 7),
                     col_labels=(0, NUMS(1, 7)))]),
    # Barello et al. (2019), Table 4: polychoric, upper triangle, dash diagonal.
    dict(pmcid="PMC6880352", label="Table 4", table="barello_2019_ches7", n=198,
         names=CHE, label_col=0,
         parts=[dict(names=CHE, rows=seq(1, 7), cols=seq(1, 7), col_labels=(0, CHE))]),
    # Lee-Baggley et al. (2026), Table 4 (Study 1): lower triangle, 1.000 diagonal, dashes
    # above; item M and SD from Table 3 (Study 1 EFA).
    dict(pmcid="PMC13068280", label="Table 4", table="leebaggley_2026_bws7", n=1535,
         names=BWS, label_col=0,
         parts=[dict(names=BWS, labels=BWS_LAB, rows=seq(1, 7), cols=seq(1, 7),
                     col_labels=(0, BWS_LAB))],
         moments=mom("mean", "Table 3", BWS, seq(2, 8), 1, 1, "M", labels=BWS_LAB)
         + mom("sd", "Table 3", BWS, seq(2, 8), 2, 1, "SD", labels=BWS_LAB)),
    # Xue et al. (2026), Table 2: upper triangle, 1 diagonal; the Total column is not read.
    # Item M and SD from Table 1, total-sample column ("M ± SD").
    dict(pmcid="PMC13106355", label="Table 2", table="xue_2026_sdtqols7", n=608,
         names=SDT, label_col=0,
         parts=[dict(names=SDT, rows=seq(1, 7), cols=seq(1, 7), col_labels=(0, SDT))],
         moments=[dict(m, rx=rx) for st, rx in (("mean", MSD_PM_M), ("sd", MSD_PM_SD))
                  for m in mom(st, "Table 1", SDT, seq(1, 7), 3, 0, "Total sample (n = 608), M ± SD")]),
    # Elemo et al. (2020), Table 4: Pearson, lower triangle, dash diagonal; the corrected
    # item-total column is not read. Item M and SD from Table 2 ("Mean (SD)").
    dict(pmcid="PMC7714254", label="Table 4", table="elemo_2020_fcv19s7", n=307,
         names=items(7), label_col=0,
         parts=[dict(names=items(7), labels=[f"Item {i}" for i in seq(1, 7)], rows=seq(1, 7),
                     cols=seq(1, 7), col_labels=(0, [f"Item {i}" for i in seq(1, 7)]))],
         moments=[dict(m, rx=rx) for st, rx in (("mean", MSD_M), ("sd", MSD_SD))
                  for m in mom(st, "Table 2", items(7), seq(1, 7), 2, 0, "Mean (SD)",
                               labels=[f"Item {i}" for i in seq(1, 7)])]),
    # Mahmood et al. (2023), Table 4: lower triangle, 1.000 diagonal; item M and SD from
    # Table 3.
    dict(pmcid="PMC10483759", label="Table 4", table="mahmood_2023_ppfvd6", n=457,
         names=PPFVD, label_col=0,
         parts=[dict(names=PPFVD, rows=seq(1, 6), cols=seq(1, 6), col_labels=(0, PPFVD))],
         moments=mom("mean", "Table 3", PPFVD, seq(1, 6), 1, 0, "Mean")
         + mom("sd", "Table 3", PPFVD, seq(1, 6), 2, 0, "SD")),
    # Stewart et al. (2020), Table 4: two panels (ChYMH and ChYMH-DD samples).
    chymh("ChYMH", 6086, 2, 3),
    chymh("ChYMH-DD", 657, 9, 10),
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
    meta = root.find(".//article-meta")
    for ra in (meta.iter("related-article") if meta is not None else []):
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
        if d is not None and d.strip() not in DIAG | set(cfg.get("diag_extra", ())):
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
                    va = num(a, where, comma, strip)
                    if key in asym:             # a listed disagreement: the upper copy differs
                        try:                    # by at most 0.01, or cannot be read as a number
                            vb = num(b, where, comma, strip)
                        except SystemExit:
                            vb = None
                        if vb == va or (vb is not None and abs(float(va) - float(vb)) > 0.01 + 1e-9):
                            raise SystemExit(f"{where}: listed pair ({names[i]}, {names[j]}): {a!r} / {b!r}")
                        seen_asym.add(key)
                    elif va != num(b, where, comma, strip):
                        raise SystemExit(f"{where}: asymmetric ({names[i]}, {names[j]}): {a!r} / {b!r}")
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
        raise SystemExit("usage: python3 pmc_article_tables_ah.py <out dir>")
    main(sys.argv[1])
