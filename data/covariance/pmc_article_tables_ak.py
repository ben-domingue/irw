"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AK batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article whose own metadata
(<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article,
so they are not read.

Tables built (CONFIGS below): eleven tables (eleven matrices) from eleven articles. Six
are item-level matrices of one scale (Caregiver Preparedness Scale, Kendall's tau-b,
held earlier only for its coefficient; F-SIM16, tetrachoric within four domains;
Teaching Satisfaction Scale; German PROMIS Parent Proxy Anger Scale, Spearman; BER-5,
Spearman; Thai TIBSCSM, 32 items; a 26-item fall health-belief scale; 20 PANAS items
rated as anticipated affect), vetted from agent AJ's buildable-looking list and the AC
candidate list of 2026-11-18; three are scale-level matrices (schadenfreude and related
traits; mental health of Hong Kong students; motivation, needs and affect of French
older adults in after-care). The N of each is from the caption, a table note or the
article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_aj.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions. Cells are read as text. Significance stars are stripped;
nothing else is changed, except the footnote marker "b" after one F-SIM16 value
(0.999b, `strip`). Unicode minus (U+2212) and an en dash used as a minus are read as
"-", and spaces inside a cell are dropped. For each pair of variables the script reads
both cells (row i/column j and row j/column i): exactly one must hold a number and the
other must be empty or a dash, or both must hold the same number.
crysel_2018_schadenfreude29 prints zero-order correlations below the diagonal and
partial correlations above it: only the lower triangle is read (`lower_only`).
shek_2023_covidmentalhealth22 prints no column for its last variable and no diagonal
cell for its last five.

filia_2022_fsim16 prints four within-domain blocks (`parts`) and no correlations
between domains: with `blank_across_parts`, each pair of items from different blocks
is written with an empty value (README V4: measured, not reported).

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or number of
a label (so that item wording printed as a row label is never copied here). Printed
column headers are checked too (`col_labels`). Variable names are the source's item or
scale codes (IB1, Q1, C19S_DC, ...) or scale names as printed (Envy, DTDD, ...); where
the source prints only a number or item content, items are written as item1, item2,
..., never with item wording.

Mean, SD and reliability (Cronbach's alpha, `rel`) cells are read from the cell a
config names; the row label of each moment is checked the same way as the matrix rows,
and the column header is checked too (`hdr`). "M (SD)" cells are split by a regex
(`rx`). They become mean/sd/rel rows, values as printed.

Diagonal cells (1, 1.00, 1.000, a dash or blank) are written as 1. Values are written
in shortest round-trip form of the published decimal (for example "0.40" -> "0.4",
".80" -> "0.8", "-.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_ak.py <out dir>
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


def row_mom(stat, label, names, row, cols, lab, hdr_row, hdrs, label_col=0):
    """One moment per variable, read from one row (label `lab`) across columns cols; each
    column header (row hdr_row) is checked."""
    return [dict(stat=stat, var=v, label=label, row=row, col=c, rx=None, lab=lab,
                 label_col=label_col, label_rx=None, comma=False, hdr=(hdr_row, h))
            for v, c, h in zip(names, cols, hdrs)]


def msd(label, names, rows, col, hdr_row, hdr, m_rx, sd_rx, **kw):
    """Mean and SD printed in one cell ("M (SD)" or "M ± SD"), split by two regexes."""
    return [dict(m, rx=rx) for st, rx in (("mean", m_rx), ("sd", sd_rx))
            for m in mom(st, label, names, rows, col, hdr_row, hdr, **kw)]


NUMLAB = r"^(\d+)\."           # "3. <item wording>" -> 3
LEADNUM = r"^(\d+)"             # "6 (R)" -> 6
NUMS = lambda a, b: [str(i) for i in seq(a, b)]
MSD_M, MSD_SD = r"^(-?[\d.]+) \(", r"\(([\d.]+)\)$"          # "3.15 (1.55)"
MSD_PM_M, MSD_PM_SD = r"^(-?[\d.]+) ?± ?", r" ?± ?([\d.]+)$"     # "4.68 ± 2.31", "5.67±2.09"

def lower_sq(pmcid, label, table, n, k, first, hdr_row, hdrs, label_rx=NUMLAB, labels=None, **kw):
    """A lower-triangle (or diagonal-only upper) square: rows first..first+k-1, columns
    1..k, row labels numbered (label_rx) and column headers hdrs."""
    names = items(k)
    return dict(pmcid=pmcid, label=label, table=table, n=n, names=names, label_col=0,
                label_rx=label_rx,
                parts=[dict(names=names, labels=labels or NUMS(1, k), rows=seq(first, first + k - 1),
                            cols=seq(1, k), col_labels=(hdr_row, hdrs))], **kw)


def wording_sq(pmcid, label, table, n, k, full=False, **kw):
    """A square whose row labels and column headers are item content (not copied): each
    row label must equal the column header of the same position; a full square
    (`full`) must be symmetric."""
    names = items(k)
    part = dict(names=names, rows=seq(1, k), cols=seq(1, k), same_labels=(0, 0))
    if full:
        part.update(lower_only=True, asym=[])
    return dict(pmcid=pmcid, label=label, table=table, n=n, names=names, label_col=None,
                parts=[part], **kw)


def square(pmcid, label, table, n, names, rows, cols, hdr_row, hdrs, labels=None, label_col=0,
           label_rx=None, part_kw=None, **kw):
    """One square printed as a lower triangle (rows and columns in the same order); row
    labels (after label_rx) must be `labels` (default: the names) and the column headers
    of row hdr_row must be hdrs."""
    part = dict(names=names, labels=labels or names, rows=rows, cols=cols, col_labels=(hdr_row, hdrs))
    part.update(part_kw or {})
    return dict(pmcid=pmcid, label=label, table=table, n=n, names=names, label_col=label_col,
                label_rx=label_rx, parts=[part], **kw)


CPS = [f"item{c}" for c in "ABCDEFGH"]
FSIM = [f"Q{i}" for i in seq(1, 16)]
BER = [f"Q{i}_12" for i in seq(1, 5)]
IB = [f"IB{i}" for i in seq(1, 32)]
SCH = ["Schadenfreude", "Benign", "Malicious", "Krizan & Johar", "Envy", "Empathy", "Humor Sense",
       "Humor Style", "DTDD", "Mach", "Psych", "Narc", "BAQ", "Physical", "Verbal", "Anger", "Hostility",
       "Extraversion", "Agreeableness", "Conscientious", "Neuroticism", "Imagination", "Desirability",
       "SISE", "State SE", "Social", "Appear", "Perform", "GAC"]
HK = ["C19S_DC", "C19S_SC", "C19S_CB", "SE", "DASS-21", "PTSD", "CESD-R", "SB", "IAT", "HL", "LS", "FL",
      "BA", "RE", "EC", "PFAM", "PS", "CA", "NEED", "DIF", "US", "ES"]
SOU = ["mot_autonomous", "mot_controlled", "amotivation", "ib_autonomy_support", "ib_control_autonomy",
       "ib_competence_support", "ib_control_competence", "ib_relatedness_support", "ib_control_relatedness",
       "gco_autonomy", "gco_control", "gco_impersonal", "boredom", "apathy", "affect_positive",
       "affect_negative", "need_autonomy", "need_competence", "need_relatedness"]
SOU_LAB = ["Autonomous", "Controlled", "Amotivation", "Autonomy support", "Control of autonomy",
           "Competence support", "Control of competence", "Relatedness support", "Control of relatedness",
           "Autonomy", "Control", "Impersonal", "Boredom", "Apathy", "Positive", "Negative", "Autonomy",
           "Competence", "Relatedness"]

CONFIGS = [
    # Remr & Gray (2026), Table 3: Caregiver Preparedness Scale, Kendall's tau-b, lower
    # triangle, 1.000 diagonal, rows and columns "Item A" .. "Item H"; item Mean and SD
    # from Table 2 (rows "(a) <item wording>" .. "(h) ...", n = 512 printed per item).
    square("PMC13119223", "Table 3", "remr_2026_cps8", 512, CPS, seq(1, 8), seq(1, 8), 0,
           [f"Item {c}" for c in "ABCDEFGH"], labels=[f"Item {c}" for c in "ABCDEFGH"],
           moments=mom("mean", "Table 2", CPS, seq(1, 8), 2, 0, "Mean", labels=list("abcdefgh"),
                       label_rx=r"^\(([a-h])\)")
           + mom("sd", "Table 2", CPS, seq(1, 8), 3, 0, "SD", labels=list("abcdefgh"),
                 label_rx=r"^\(([a-h])\)")),
    # Filia et al. (2022), Table 3.: F-SIM16 tetrachoric correlations within four
    # 4-item domains (HN, SOC, EE, FIN), each block a lower triangle with a 1.000
    # diagonal under a header row "(1)" .. "(16)"; row labels "<short title> (k)"; the
    # item-total (polyserial) column and the alphas are not read. No correlations are
    # printed between domains (written blank).
    dict(pmcid="PMC8786614", label="Table 3.", table="filia_2022_fsim16", n=506, names=FSIM,
         label_col=0, label_rx=r".*\((\d+)\)\s*$", strip=r"b$", blank_across_parts=True,
         parts=[dict(names=FSIM[4 * d:4 * d + 4], labels=NUMS(4 * d + 1, 4 * d + 4),
                     rows=seq(r0, r0 + 3), cols=seq(1, 4),
                     col_labels=(r0 - 1, [f"({i})" for i in seq(4 * d + 1, 4 * d + 4)]))
                for d, r0 in enumerate([3, 9, 15, 21])]),
    # Pretorius et al. (2023), TABLE 1: Teaching Satisfaction Scale, lower triangle,
    # "-" diagonal and upper triangle, item wording as row labels ("1. ..."); Mean and
    # SD rows of the same table.
    lower_sq("PMC12082223", "TABLE 1", "pretorius_2023_tss5", 355, 5, 2, 1, NUMS(1, 5),
             moments=row_mom("mean", "TABLE 1", items(5), 7, seq(1, 5), "Mean", 1, NUMS(1, 5))
             + row_mom("sd", "TABLE 1", items(5), 8, seq(1, 5), "SD", 1, NUMS(1, 5))),
    # Kaman et al. (2022), Table 3: German PROMIS Parent Proxy Anger Scale, Spearman,
    # lower triangle, dash diagonal, item number in column 0 and item wording in
    # column 1 (not read); item M (SD) from Table 2.
    square("PMC8921038", "Table 3", "kaman_2022_promisanger5", 8746, items(5), seq(1, 5), seq(2, 6), 0,
           NUMS(1, 5), labels=NUMS(1, 5),
           moments=msd("Table 2", items(5), seq(2, 6), 2, 1, "Mean (SD)", MSD_M, MSD_SD,
                       labels=NUMS(1, 5))),
    # Dibaj et al. (2025), Table 1: BER-5 items at the 12.4-year follow-up, Spearman,
    # lower triangle, 1.00 diagonal, rows and columns Q1_12 .. Q5_12.
    square("PMC11905671", "Table 1", "dibaj_2025_ber5", 60, BER, seq(1, 5), seq(1, 5), 0, BER),
    # Imkome (2025), Table 2.: TIBSCSM, 32 items IB1 .. IB32, lower triangle, 1.00 diagonal.
    square("PMC12120408", "Table 2.", "imkome_2025_tibscsm32", 142, IB, seq(1, 32), seq(1, 32), 0, IB),
    # Li et al. (2019), Table A1: fall-related health belief scale, 26 items; rows
    # "Item1" .. "Item26" (rows 3-28), matrix columns 7-32 headed "Item 1" .. "Item 26"
    # (row 2); response distribution, item-scale and whole-scale cells are not read.
    square("PMC6926647", "Table A1", "li_2019_fallhealthbelief26", 5833, items(26), seq(3, 28), seq(7, 32), 2,
           [f"Item {i}" for i in seq(1, 26)], labels=[f"Item{i}" for i in seq(1, 26)]),
    # Crysel & Webster (2018), Table 3 (Study 4): zero-order correlations below the
    # diagonal (read), partial correlations above it (not read); Mean, SD and alpha
    # rows of the same table (no alpha printed for the single-item SISE).
    square("PMC6124730", "Table 3", "crysel_2018_schadenfreude29", 261, SCH, seq(1, 29), seq(1, 29), 0,
           NUMS(1, 29), label_rx=r"^\d+\.\s*(.+)$", part_kw=dict(lower_only=True),
           moments=row_mom("mean", "Table 3", SCH, 31, seq(1, 29), "Mean", 0, NUMS(1, 29))
           + row_mom("sd", "Table 3", SCH, 32, seq(1, 29), "SD", 0, NUMS(1, 29))
           + [m for m in row_mom("rel", "Table 3", SCH, 33, seq(1, 29), "Α", 0, NUMS(1, 29))
              if m["var"] != "SISE"]),
    # Zampetakis et al. (2015), Table 1: 20 PANAS items rated as anticipated affect,
    # product-moment correlations, lower triangle, dash diagonal; item number in column 0
    # and the affect term in column 1 (not read); M and SD columns 2-3.
    square("PMC4585228", "Table 1", "zampetakis_2015_anticipatedaffect20", 1624, items(20), seq(1, 20),
           seq(4, 23), 0, NUMS(1, 20), labels=NUMS(1, 20),
           moments=mom("mean", "Table 1", items(20), seq(1, 20), 2, 0, "M", labels=NUMS(1, 20))
           + mom("sd", "Table 1", items(20), seq(1, 20), 3, 0, "SD", labels=NUMS(1, 20))),
    # Shek et al. (2023), Table 5: 22 variables, lower triangle; "--" diagonal for 1-17,
    # blank for 18-21, and no column for variable 22.
    square("PMC10391639", "Table 5", "shek_2023_covidmentalhealth22", 978, HK, seq(1, 22), seq(1, 21) + [None],
           0, NUMS(1, 21), labels=[f"{i}. {v}" for i, v in enumerate(HK, 1)], diag_extra={"--"}),
    # Souesme et al. (2020), TABLE 3: 19 variables in seven groups (group name in column
    # 0, variable label in column 1), M and SD in columns 2-3, lower triangle with a dash
    # diagonal in columns 4-22 (headers 1-12, blank, blank, 15-19 in row 1).
    square("PMC7793817", "TABLE 3", "souesme_2020_needsmotivation19", 146, SOU, seq(2, 20), seq(4, 22), 1,
           NUMS(1, 12) + ["", ""] + NUMS(15, 19), labels=SOU_LAB, label_col=1,
           label_rx=r"^(?:\d+|[A-Z])\.\s*(.+)$",
           moments=mom("mean", "TABLE 3", SOU, seq(2, 20), 2, 0, "M", labels=SOU_LAB, label_col=1,
                       label_rx=r"^(?:\d+|[A-Z])\.\s*(.+)$")
           + mom("sd", "TABLE 3", SOU, seq(2, 20), 3, 0, "SD", labels=SOU_LAB, label_col=1,
                 label_rx=r"^(?:\d+|[A-Z])\.\s*(.+)$")),
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
                if cfg.get("blank_across_parts") and not any(key <= set(p["names"]) for p in cfg["parts"]):
                    cells[key] = ("", "")       # measured, not reported (different blocks)
                else:
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
            if norm(lab) != norm(m["lab"]) or (not norm(m["lab"]) and lab != m["lab"]):
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
        raise SystemExit("usage: python3 pmc_article_tables_ak.py <out dir>")
    main(sys.argv[1])
