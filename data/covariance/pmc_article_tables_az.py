"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY / CC0 open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AZ batch, 2026-11-25).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License", optionally with a version) or CC0; the script stops otherwise (no exceptions in
this batch). An article whose own metadata (<article-meta>) carries a retraction link
(<related-article related-article-type="retraction-forward"> or "retracted-article") is
refused. Links of that kind inside the reference list mark a retracted *cited* paper, not
this article, so they are not read.

Tables built (CONFIGS below), from the scale-level pass over the AC candidate list of
2026-11-18, queue lines 352-391: nursing care motivation subscales of nurses at a university
hospital (Turkish-language scale);
cognitive toughness, stress appraisal and coping of Chinese athletes training in heat;
social burnout, social skills and interpersonal trust of Chinese medical students (with
gender, grade and major); satisfaction with educational activities on social media among
Spanish physiotherapy students; social anxiety cognition subscales of Chinese college
students; social media-related nightmares, anxiety, peace of mind and sleep of Iranian
adults; owners' ratings of their dogs' executive functions (Pearson); race-related stress,
postpartum depression and anxiety of Black mothers in the United States (M (SD) on the
diagonal); social goals and coping with friendship stress of Japanese adolescents;
physical activity, life satisfaction, self-efficacy and emerging-adulthood dimensions of
Chinese university students (Pearson); generative-AI-assisted learning use, self-efficacy,
AI literacy and perceived academic performance of Chinese undergraduates (Pearson below
a square-root-of-AVE diagonal, HTMT ratios above it: the lower triangle alone is read); and campus climate, stressful life events, school
engagement, distress and GPA of Southern California high-school students (Pearson). The N
of each is from the caption, a table note or the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_am.py to pmc_article_tables_ay.py (whose build code this
file copies unchanged). Each table is expanded
into a grid (a cell with rowspan/colspan fills every position it spans), so the `rows` and
`cols` indices of a config are grid positions. Cells are read as text. Significance stars
are stripped; nothing else is changed. Unicode minus (U+2212) and an en dash used as a
minus are read as "-", and spaces inside a cell are dropped ("− .371**" -> "-.371",
"0. 958" -> "0.958"). For each pair of variables the script reads both cells (row
i/column j and row j/column i): exactly one must hold a number and the other must be empty
or a dash, or both must hold the same number (a part marked `lower_only` / `upper_only`
reads one side only, when the other side prints another sample). A matrix with no row or
column for a variable has it given as None. `strip` is a regex removed from each cell
before it is read (leading stars, "** 0.827"; here the footnote letters d-f printed after
the values in La Touche et al., "0.17d"). `title` = (row, col, text) checks a block
title printed in the table.

Build options kept from AX and AY (none of them is used here):
- `blank` = {pair: printed text}: a cell printed as something that is not a number is
  written with an empty value (V4). The printed text must match exactly, and the blank
  cells must be exactly the listed ones. No value is ever invented.
- `cell_n` = dict(dr, dc, rx, lab, vlab): per-cell n, printed beside each value. `n_fn(a,
  b)`: per-cell n by a rule quoted from the table note (`n_fn(a, a)` is a variable's own
  n). `diag_n`: each variable's own n, read from a printed cell. The own n goes on the
  diagonal row and on the variable's moment rows.
- `label_dr`: the row label is printed dr rows away from the value row.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). The comparison ignores everything
but letters and digits, so a footnote marker ("Anxiety *") does not count. Variable names
are the printed labels without their "j." / "j" numbers.

Mean, SD and reliability cells are read from the cell a config names; the row label of
each moment is checked the same way as the matrix rows, and the column header is checked
too (`hdr`). They become mean/sd/rel rows, values as printed.

Diagonal cells (1, 1.00, 1.000, a dash or blank; "—c" where `diag_extra` allows it, and
"M (SD)" or a square root of AVE where `diag_rx` allows it) are written as 1. A diagonal "M (SD)" (Maxwell et
al.) is also read as the mean and SD rows of that variable (`dmsd`). Values are written in shortest round-trip form of the published decimal
(for example "0.40" -> "0.4", ".80" -> "0.8"), i.e. unchanged.

`n` is the matrix N on every row, unless the config gives per-cell n (above).

Usage: python3 data/covariance/pmc_article_tables_az.py <out dir>
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


def diag_mom(label, names, rows, cols, hdr_row, hdrs, rx, label_rx=None, labels=None, label_col=0):
    """A reliability printed on the diagonal (cell rows[i], cols[i]), split by rx."""
    labels = labels or names
    return [dict(stat="rel", var=v, label=label, row=r, col=c, rx=rx, lab=l, label_col=label_col,
                 label_rx=label_rx, comma=False, hdr=(hdr_row, h))
            for v, r, c, l, h in zip(names, rows, cols, labels, hdrs)]


DOTNUM = r"^\d+\.\s*(.+)$"      # "1. Demand" -> "Demand"
PARNUM = r"^\(\d+\)\s*(.+)$"    # "(1) Global job satisfaction" -> "Global job satisfaction"
PAREN = r"^\(([\d.]+)\)$"        # "(0.83)" -> "0.83"
PAREN_OR_DASH = r"^\((–|[\d.]+)\)$"   # "(–)" or "(0.954)"
LEADNUM_M = r"^([−-]?[\d.]+)"      # "0.54 #" -> "0.54"


PAR = lambda a, b: [f"({i})" for i in seq(a, b)]


def row_msd(label, names, row, cols, lab, hdr_row, hdrs, m_rx, sd_rx, label_col=0):
    """Mean and SD printed in one cell ("M (SD)") along one row, split by two regexes."""
    return [dict(m, rx=rx) for st, rx in (("mean", m_rx), ("sd", sd_rx))
            for m in row_mom(st, label, names, row, cols, lab, hdr_row, hdrs, label_col)]


def pair(a, b):
    return frozenset((a, b))


def nolab(stat, label, names, rows, col, hdr_row, hdr, labels, label_col=0, label_rx=None):
    return mom(stat, label, names, rows, col, hdr_row, hdr, labels=labels, label_col=label_col, label_rx=label_rx)


def sub(xs, idx):
    return [xs[i] for i in idx]


def dmsd(label, names, rows, cols, hdr_row, hdrs, label_rx=None, labels=None, label_col=0):
    """Mean and SD printed on the diagonal as "M (SD)" (cell rows[i], cols[i])."""
    labels = labels or names
    return [dict(stat=st, var=v, label=label, row=r, col=c, rx=rx, lab=l, label_col=label_col,
                 label_rx=label_rx, comma=False, hdr=(hdr_row, h))
            for st, rx in (("mean", MSD_M), ("sd", MSD_SD))
            for v, r, c, l, h in zip(names, rows, cols, labels, hdrs)]


NCM = ["SCC", "PIV", "PCO", "SAC", "SSS", "NCMS"]
HEAT = ["Cognitive toughness", "Challenging evaluation", "Threatening evaluation", "Team support",
        "Attention flexibility", "Emotion regulation"]
SBU = ["Gender", "Grade", "Major", "SB", "SS", "IT"]
CUS = ["ASS", "Social media experience", "CuSAERS total", "Perception of learning", "Task satisfaction",
       "Self-realization"]
SAC = ["SP", "SS", "EC", "CE", "Total", "IAS"]
SMN = ["Social media-related nightmare", "Social media use integration", "Anxiety", "Peace of mind",
       "Sleep quality", "Nightmare distress"]
DEF = ["Behavioural flexibility", "Motor regulation", "Attention towards owner", "Instruction following",
       "Delay inhibition", "Working memory"]
RRS = ["Number of Children", "Income", "Mental Health Diagnosis", "IRRS Scale (Race-Related Stress)",
       "PPD Scale (Postpartum depression)", "PSAS Scale (Postnatal anxiety)"]
SGC = ["Social learning goals", "Social performance-approach goals", "Social performance-avoidance goals",
       "Relationship-rebuilding and positive reappraisal coping", "Relationship-changing coping",
       "Relationship-withdrawal coping", "Sex"]
EMA = ["Physical activity", "Life satisfaction", "Self-efficacy", "Responsibility", "Self-exploration",
       "Instability", "Possibilities"]
GAI = ["GAIU", "SE", "AIL", "PAP"]
CAM = ["Gender", "School engagement", "Stressful life events", "Campus climate", "Psychological distress",
       "Academic achievement"]


CONFIGS = [
    # --- scale-level pass, queue lines 352-391 ---
    # Kurt et al. (2026), TABLE 4: the PCA sample (n = 397, Table 2 and text); lower
    # triangle with "—" on and above the diagonal; no column for the NCMS total.
    square("PMC13530403", "TABLE 4", "kurt_2026_ncms6", 397, NCM, seq(1, 6), seq(1, 5) + [None], 0,
           ["SCC r", "PIV r", "PCO r", "SAC r", "SSS r"]),
    # Guan et al. (2026), Table 1: M and SD in columns 1-2; lower triangle with a "–"
    # diagonal in columns 3-8; N = 240 (caption).
    square("PMC13014484", "Table 1", "guan_2026_heatresil6", 240, HEAT, seq(1, 6), seq(3, 8), 0, NUMS(1, 6),
           label_rx=DOTNUM,
           moments=mom("mean", "Table 1", HEAT, seq(1, 6), 1, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 1", HEAT, seq(1, 6), 2, 0, "SD", label_rx=DOTNUM)),
    # Wang et al. (2024), Table 9 (sample 6): M and SD in columns 1-2; lower triangle with a
    # 1 diagonal in columns 3-8; n = 213 (note).
    square("PMC10991744", "Table 9", "wang_2024_socburnout6", 213, SBU, seq(1, 6), seq(3, 8), 0, NUMS(1, 6),
           label_rx=PARNUM,
           moments=mom("mean", "Table 9", SBU, seq(1, 6), 1, 0, "M", label_rx=PARNUM)
           + mom("sd", "Table 9", SBU, seq(1, 6), 2, 0, "SD", label_rx=PARNUM)),
    # La Touche et al. (2025), Table 5: lower triangle with a "—" diagonal ("—c" in the
    # first row: footnote c, "Not applicable"); footnote letters d-f (P values) printed
    # after the values are stripped; N = 160 (text).
    square("PMC12759299", "Table 5", "latouche_2025_cusaers6", 160, CUS, seq(1, 6), seq(1, 6), 0,
           ["ASSa", "Social media experience", "CuSAERSb total", "Perception of learning", "Task satisfaction",
            "Self-realization"], strip=r"[def]$", diag_extra=("—c",)),
    # Zha et al. (2023), Table 5: n, M and SD in columns 1-3 (n = 500 on every row);
    # lower triangle with a 1 diagonal in columns 4-9.
    square("PMC9892844", "Table 5", "zha_2023_sacscs6", 500, SAC, seq(1, 6), seq(4, 9), 0, SAC,
           moments=mom("mean", "Table 5", SAC, seq(1, 6), 2, 0, "M") + mom("sd", "Table 5", SAC, seq(1, 6), 3, 0, "SD")),
    # Shabahang et al. (2024), Table 4: upper triangle with a 1 diagonal; N = 595 (note).
    square("PMC10936066", "Table 4", "shabahang_2024_smnightmare6", 595, SMN, seq(1, 6), seq(1, 6), 0, NUMS(1, 6),
           label_rx=DOTNUM),
    # Foraita et al. (2022), Table 3: Pearson, N = 714 (caption); upper triangle without
    # a diagonal: the rows are the six subscales, the columns the last five.
    square("PMC9113072", "Table 3", "foraita_2022_defs6", 714, DEF, seq(1, 6), [None] + seq(1, 5), 0, DEF[1:]),
    # Maxwell et al. (2025), Table 3: lower triangle with "M (SD)" on the diagonal (note);
    # N = 79 (caption).
    square("PMC12649430", "Table 3", "maxwell_2025_racestress6", 79, RRS, seq(1, 6), seq(1, 6), 0, NUMS(1, 6),
           label_rx=DOTNUM, diag_rx=r"-?[\d.]+ \([\d.]+\)",
           moments=dmsd("Table 3", RRS, seq(1, 6), seq(1, 6), 0, NUMS(1, 6), label_rx=DOTNUM)),
    # Kuroda (2026), Table 2: lower triangle with a blank diagonal; no column for Sex (1 =
    # boys, 2 = girls); N = 137 (text).
    square("PMC13389936", "Table 2", "kuroda_2026_socialgoals7", 137, SGC, seq(1, 7), seq(1, 6) + [None], 0,
           NUMS(1, 6), label_rx=DOTNUM),
    # Luo (2024), Table 3: Pearson (text); lower triangle with a 1 diagonal; no column for
    # Possibilities; n = 3,387 (caption).
    square("PMC11598934", "Table 3", "luo_2024_lifesat7", 3387, EMA, seq(1, 7), seq(1, 6) + [None], 0,
           NUMS(1, 6), label_rx=DOTNUM),
    # Shen & Um (2026), Table 3: Panel B (rows 7-11): zero-order Pearson correlations below
    # the diagonal, square roots of AVE on it and HTMT ratios above it (note), so the lower
    # triangle alone is read (`lower_only`) and the diagonal is written as 1; alpha, M and
    # SD from Panel A (rows 1-5); N = 376 (text, no missing values).
    square("PMC13680825", "Table 3", "shen_2026_genaiuse4", 376, GAI, seq(8, 11), seq(1, 4), 7, NUMS(1, 4),
           label_rx=DOTNUM, diag_rx=r"0\.\d{3}", part_kw=dict(lower_only=True),
           moments=mom("rel", "Table 3", GAI, seq(2, 5), 2, 1, "α", label_rx=DOTNUM)
           + mom("mean", "Table 3", GAI, seq(2, 5), 5, 1, "M", label_rx=DOTNUM)
           + mom("sd", "Table 3", GAI, seq(2, 5), 6, 1, "SD", label_rx=DOTNUM)),
    # Cruz et al. (2025), TABLE 1: Pearson (caption); lower triangle with a "–" diagonal;
    # Mean and SD rows 7-8; gender coded 0 = boy, 1 = girl (note "a"); N = 293 (text).
    square("PMC12644310", "TABLE 1", "cruz_2025_campusclimate6", 293, CAM, seq(1, 6), seq(1, 6), 0, NUMS(1, 6),
           label_rx=DOTNUM, labels=["Gender a"] + CAM[1:],
           moments=row_mom("mean", "TABLE 1", CAM, 7, seq(1, 6), "Mean", 0, NUMS(1, 6))
           + row_mom("sd", "TABLE 1", CAM, 8, seq(1, 6), "SD", 0, NUMS(1, 6))),
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
    elif not (re.search(r"creativecommons\.org/(licenses/by/|publicdomain/zero)", href + links + ltxt)
              or re.search(r"Creative Commons Attribution( \(CC BY\))?( \d\.\d)? (L|l)icen[cs]e", ltxt)):
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
        if r is not None and cfg["label_col"] is not None:   # label_dr: the label is printed dr rows away
            lab = label_of(rows[r + cfg.get("label_dr", 0)][cfg["label_col"]], cfg.get("label_rx"), where)
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
        v = rows[r][c]
        if cfg.get("pick") and a != b and v.strip() not in EMPTY:   # several groups in one cell
            rx, gi = cfg["pick"]
            m = re.fullmatch(rx, v.strip())
            if not m:
                raise SystemExit(f"{where}: cell {v!r} does not match the group pattern")
            return m.group(gi)
        return v

    def absent(a, b):                   # no printed position for this cell in this part
        return ridx[a] is None or cidx[b] is None

    asym = {frozenset(p) for p in part.get("asym", [])}
    seen_asym = set()
    got = {}
    for i in range(k):
        d = cell(i, i)
        if (d is not None and d.strip() not in DIAG | set(cfg.get("diag_extra", ()))
                and not (cfg.get("diag_rx") and re.fullmatch(cfg["diag_rx"], d.strip()))):
            raise SystemExit(f"{where}: diagonal {names[i]} is {d!r}")
        for j in range(i):
            a, b = cell(i, j), cell(j, i)       # a: below the diagonal, b: above it
            empty = EMPTY | set(cfg.get("empty_extra", ()))
            a = None if a is None or a.strip() in empty else a
            b = None if b is None or b.strip() in empty else b
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
            pos = (ridx[i], cidx[j]) if a is not None else (ridx[j], cidx[i])
            if key in cfg.get("blank", {}):     # printed but not a number: written blank
                if raw.strip() != cfg["blank"][key]:
                    raise SystemExit(f"{where}: blank cell ({names[i]},{names[j]}) is {raw!r}")
                got[key] = ("", raw, pos)
                continue
            v = num(raw, f"{where} ({names[i]},{names[j]})", comma, strip)
            if abs(float(v)) >= 1:
                raise SystemExit(f"{where}: |r| >= 1 at ({names[i]},{names[j]})")
            got[key] = (v, raw, pos)
    if seen_asym != asym:
        raise SystemExit(f"{where}: asymmetric pairs {seen_asym} are not the listed {asym}")
    return got


def cell_ns(cfg, root, rows, names, cells, where):
    """Per-cell n ({pair: n}) and each variable's own n ({name: n}), or {} (matrix N on every
    row). `cell_n` = dict(dr, dc, rx, lab, vlab): the n of the cell printed at grid (r, c) is
    the cell (r + dr, c + dc), which must fully match rx (group 1 is the n); `lab` = (col,
    text) is the label that row must carry, `vlab` = (col, text) the label of the value's
    row. `n_fn(a, b)` gives the n by a rule from the table note (`n_fn(a, a)` a variable's own
    n). A variable's own n (its diagonal row and its moment rows) is `diag_n` when given
    (cells read like moments; the n must be at least every cell n of that variable), else
    the largest n among its cells."""
    if cfg.get("n_fn"):
        f = cfg["n_fn"]
        out = {k: f(*sorted(k)) for k in cells}
        out.update({v: f(v, v) for v in names})
        return out
    if not cfg.get("cell_n"):
        return {}
    cn = cfg["cell_n"]
    out = {}
    for key, (v, raw, pos) in cells.items():
        if pos is None:
            raise SystemExit(f"{where}: no printed position for {sorted(key)}")
        r, c = pos[0] + cn["dr"], pos[1] + cn["dc"]
        if cn.get("lab") and rows[r][cn["lab"][0]].strip() != cn["lab"][1]:
            raise SystemExit(f"{where}: n row {r} label is {rows[r][cn['lab'][0]]!r}")
        if cn.get("vlab") and rows[pos[0]][cn["vlab"][0]].strip() != cn["vlab"][1]:
            raise SystemExit(f"{where}: value row {pos[0]} label is {rows[pos[0]][cn['vlab'][0]]!r}")
        m = re.fullmatch(cn["rx"], rows[r][c].strip())
        if not m:
            raise SystemExit(f"{where}: n cell {rows[r][c]!r} for {sorted(key)}")
        out[key] = int(m.group(1))
    own = {}
    for d in cfg.get("diag_n", []):
        t = table_rows(root, d["label"])
        lab = label_of(t[d["row"]][d["label_col"]], d["label_rx"], where)
        if norm(lab) != norm(d["lab"]):
            raise SystemExit(f"{where}: {d['label']} row {d['row']} is {lab!r}, not {d['lab']!r}")
        if norm(t[d["hdr"][0]][d["col"]]) != norm(d["hdr"][1]):
            raise SystemExit(f"{where}: {d['label']} column {d['col']} header {t[d['hdr'][0]][d['col']]!r}")
        m = re.fullmatch(r"(\d+)[a-z]?", t[d["row"]][d["col"]].strip())   # "260b": footnote letter
        if not m:
            raise SystemExit(f"{where}: own n {t[d['row']][d['col']]!r} for {d['var']}")
        own[d["var"]] = int(m.group(1))
    for v in names:
        ns = [n for k, n in out.items() if v in k]
        if v in own:
            if ns and own[v] < max(ns):
                raise SystemExit(f"{where}: own n {own[v]} of {v} is below a cell n {max(ns)}")
            out[v] = own[v]
        else:
            out[v] = max(ns)
    return out


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
        for key, (v, raw, pos) in read_part(cfg, part, rows, where).items():
            if key in cells and cells[key][0] != v:
                raise SystemExit(f"{where}: panels disagree on {sorted(key)}")
            cells[key] = (v, raw, pos)
    blanks = {k for k, (v, raw, pos) in cells.items() if v == ""}
    if blanks != set(cfg.get("blank", {})):
        raise SystemExit(f"{where}: blank cells {blanks} are not the listed {set(cfg.get('blank', {}))}")
    nn = cell_ns(cfg, root, rows, names, cells, where)

    g = {"group": cfg["group"]} if cfg.get("group") else {}
    out, check = [], []
    for i in range(k):
        for j in range(i):
            key = frozenset((names[i], names[j]))
            if key not in cells:
                if cfg.get("blank_across_parts") and not any(key <= set(p["names"]) for p in cfg["parts"]):
                    cells[key] = ("", "", None)  # measured, not reported (different blocks)
                else:
                    raise SystemExit(f"{where}: pair {sorted(key)} not printed")
            v, raw, pos = cells[key]
            out.append({"stat": "cor", "var1": names[i], "var2": names[j], "value": v,
                        "n": nn.get(key, cfg["n"]), **g})
            check.append((cfg.get("group", ""), names[i], names[j], raw, str(nn.get(key, cfg["n"]))))
        out.append({"stat": "cor", "var1": names[i], "var2": names[i], "value": "1",
                    "n": nn.get(names[i], cfg["n"]), **g})
        check.append((cfg.get("group", ""), names[i], names[i], "diag", str(nn.get(names[i], cfg["n"]))))

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
        out.append({"stat": m["stat"], "var1": m["var"], "var2": "", "value": v,
                    "n": nn.get(m["var"], cfg["n"]), **g})
        check.append((cfg.get("group", ""), m["stat"] + ":" + m["var"], "", raw, str(nn.get(m["var"], cfg["n"]))))
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
        raise SystemExit("usage: python3 pmc_article_tables_az.py <out dir>")
    main(sys.argv[1])
