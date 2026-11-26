"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AQ batch, 2026-11-19).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License", optionally with a version) or CC0; the script stops otherwise. An article
whose own metadata (<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article,
so they are not read.

Tables built (CONFIGS below): from agent AP's screened-only row and the scale-level
pass over the AC candidate list of 2026-11-18 (resumed at AP's stopping point,
PMC9805668). Cognitive and behavioural COPD diagnostic adherence and its correlates in
rural China; nursing work environment, communication and fatigue of Korean nurses; the
Immunization Scale (IMS) with depression, anxiety, expectations and inflexibility in two
studies (two groups with different variables); mindfulness facets, perceived stress and
burnout subtypes of Spanish students; sublime emotion toward nature and environmental
attitudes in Madrid; online fraud susceptibility, threat awareness, self-efficacy and
prevention behaviour of Chinese students; the LGBT-DOCSS-JP with attitude and social
desirability scales (Spearman; the table's rows are the first eight variables and its
columns the last eight); cognitive load in AI-assisted L2 writing; psychological need
thwarting and turnover intention of teachers at two waves; parental self-compassion,
depressive symptoms and child adjustment; children's ADHD symptoms and aggression with
parental SCL-90-R dimensions. The N of each is from the caption, a table note or the
article text, as noted in matrices.csv. Moments come from the same table except
kim_2026_medicationerror9 (TABLE 2) and bethelmy_2019_sublimenature9 (Table 5).

Parsing: as pmc_article_tables_am.py to pmc_article_tables_ap.py (whose build code this
file copies unchanged).
Each table is expanded into a grid (a cell with rowspan/colspan fills every position it
spans), so the `rows` and `cols` indices of a config are grid positions. Cells are read
as text. Significance stars are stripped; nothing else is changed. Unicode minus
(U+2212) and an en dash used as a minus are read as "-", and spaces inside a cell are
dropped ("0.22 **" -> "0.22"). For each pair of variables the script reads both cells
(row i/column j and row j/column i): exactly one must hold a number and the other must
be empty or a dash, or both must hold the same number. A matrix with no column for its
last variable has that column given as None; kanakubo_2024_lgbtdocss9 has no row for its
last variable and no column for its first (rows [1..8, None], columns [None, 1..8]).

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). Variable names are the printed
scale names; where a table prints codes or abbreviations (kim_2026_medicationerror9:
X1-Y5; chen_2026_onlinefraud8: MM-PB; tzang_2021_adhdparent9: "Soma (P)" etc.;
ewen_2022_ims9: "Factor 1-3") the names are spelled out from the table note and the
printed labels are checked. Codings printed in a label ("(in RMB)") are dropped from the
name; U+2010 hyphens and curly apostrophes are written as "-" and "'".

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). "M (SD)" cells are split by two regexes. They become mean/sd rows, values as
printed. Cronbach's alpha in its own column (chen_2026_onlinefraud8) becomes rel rows.
cheung_2022_parentselfcomp8's income mean has a thousands comma and is not read.

Diagonal cells (1, 1.00, a dash or blank) are written as 1. Values are written in
shortest round-trip form of the published decimal (for example "0.40" -> "0.4", ".80"
-> "0.8", "-0.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_aq.py <out dir>
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

COPD = ["Cognitive Dimension", "Behavioral Dimension", "COPD Knowledge", "Health Beliefs", "Social Support",
        "Economic Toxicity", "Health Literacy", "Anxiety", "Living Alone"]
NWE_LAB = ["X1", "X2", "X3", "X4", "Y1", "Y2", "Y3", "Y4", "Y5"]
NWE = ["Nurse participation in hospital affairs", "Nursing foundations for quality of care",
       "Nurse manager ability, leadership, and support for nurses", "Staffing and resource adequacy",
       "Nurse-physician communication", "Nurse-nurse communication", "Depletive fatigue", "Nervous fatigue",
       "Chronic fatigue"]
NWE_T2 = NWE[:4] + ["Nurse–physician communication", "Nurse–nurse communication", "Depletive", "Nervous", "Chronic"]
IMS1_LAB = ["BDI-II", "BAI", "DES", "FAH-II", "73-item IMS", "23-item IMS", "Factor 1", "Factor 2", "Factor 3"]
IMS1 = ["BDI-II", "BAI", "DES", "FAH-II", "IMS 73-item total", "IMS 23-item total", "IMS negative expectations",
        "IMS assimilation", "IMS cognitive immunization"]
IMS2_LAB = ["BDI-II", "BAI", "DES", "FAH-II", "IMS", "Factor 1", "Factor 2", "Factor 3"]
IMS2 = ["BDI-II", "BAI", "DES", "FAH-II", "IMS total", "IMS negative expectations", "IMS assimilation",
        "IMS cognitive immunization"]
MBS = ["Awareness", "Non-judging", "Describing", "Non-reacting", "Perceived stress", "Overload",
       "Lack of development", "Neglect"]
SEN = ["Awe", "Inspiring energy", "Love and care for nature", "Anthropocentrism", "Environmental apathy",
       "Emotional affinity toward nature", "Connectedness with nature", "Environmental intention",
       "Environmental behaviors"]

FRA_LAB = ["MM", "HP", "FR", "AK", "SS", "TA", "SE", "PB"]
FRA = ["Monetary motivation", "Heuristic processing", "Financial risk preference", "Anti-fraud knowledge",
       "Susceptibility to social influence", "Threat awareness", "Anti-fraud self-efficacy",
       "Online scam prevention behavior"]
LGB = ["LGBT-DOCSS-JP total", "Attitudinal Awareness", "Basic Knowledge", "Clinical Preparedness", "Clinical Training",
       "ATLG-J6R", "J-GTS-R-SF", "J-RWA", "J-BIDR"]
LGB_LAB = ["LGBT-DOCSS-JP Total scale scores"] + LGB[1:8] + [None]
CLW = ["CL-AI-L2W total", "Prompt management", "Critical evaluation", "Integrative synthesis",
       "Authorial core processing", "Overall mental effort", "Writing anxiety", "Writing self-efficacy"]
PNT = ["PNT-A at T1", "PNT-C at T1", "PNT-R at T1", "Turnover Intention at T1", "PNT-A at T2", "PNT-C at T2",
       "PNT-R at T2", "Turnover Intention at T2"]
PSC = ["Child gender", "Parent gender", "Monthly family income", "Parents' self-compassion",
       "Parents' depressive symptoms", "Children's prosocial behavior", "Children's externalizing problems",
       "Children's internalizing problems"]
PSC_LAB = PSC[:2] + ["Monthly family income (in RMB)"] + PSC[3:]
ADH = ["Inattention", "Hyperactivity", "Aggression", "ODD", "Somatization (parent)",
       "Obsessive-compulsive (parent)", "Interpersonal sensitivity (parent)", "Depression (parent)",
       "Anxiety (parent)"]
ADH_LAB = ["Inattention", "Hyperactivity", "Aggression", "ODD", "Soma (P)", "ObsComp (P)", "InterPers (P)",
           "Depression (P)", "Anxiety (P)"]


def ims(group, label, n, lab, names):
    """Ewen et al. (2022): study 1 (TABLE 3) and study 2 (TABLE 4), upper triangles with a
    dash diagonal; printed abbreviations checked as row labels and column headers."""
    k = len(names)
    return dict(pmcid="PMC9773141", label=label, table="ewen_2022_ims9", n=n, names=names, label_col=0,
                label_rx=None, group=group,
                parts=[dict(names=names, labels=lab, rows=seq(1, k), cols=seq(1, k), col_labels=(0, lab))])


CONFIGS = [
    # Wang et al. (2026), Table 3: "j. label", lower triangle with a 1.00 diagonal and
    # dashes above it in columns 1-9.
    square("PMC13665099", "Table 3", "wang_2026_copdadherence9", 248, COPD, seq(1, 9), seq(1, 9), 0, NUMS(1, 9),
           label_rx=DOTNUM),
    # Kim & Song (2026), TABLE 3: codes X1-Y5 (table note), lower triangle with a 1 diagonal
    # in columns 1-9 (tolerance and VIF columns not read); Mean and SD from TABLE 2 (subscale
    # rows only; the total rows NWE, CHP, Fatigue and Medication error are not read).
    square("PMC13140185", "TABLE 3", "kim_2026_medicationerror9", 230, NWE, seq(1, 9), seq(1, 9), 0, NWE_LAB,
           labels=NWE_LAB,
           moments=mom("mean", "TABLE 2", NWE, [2, 3, 4, 5, 7, 8, 10, 11, 12], 1, 0, "Mean", labels=NWE_T2)
           + mom("sd", "TABLE 2", NWE, [2, 3, 4, 5, 7, 8, 10, 11, 12], 2, 0, "SD", labels=NWE_T2)),
    # Ewen et al. (2022): study 1 (n = 230) and study 2 (n = 299), two groups.
    ims("study1", "TABLE 3", 230, IMS1_LAB, IMS1),
    ims("study2", "TABLE 4", 299, IMS2_LAB, IMS2),
    # Martínez-Rubio et al. (2020), Table 2: "j. label", lower triangle, dashes on and above
    # the diagonal.
    square("PMC7579009", "Table 2", "martinezrubio_2020_mindfulburnout8", 1233, MBS, seq(1, 8), seq(1, 8), 0,
           NUMS(1, 8), label_rx=DOTNUM),
    # Bethelmy & Corraliza (2019), Table 6: "j. label", lower triangle with a blank diagonal,
    # no column for the last variable; M (SD) from Table 5.
    square("PMC6424873", "Table 6", "bethelmy_2019_sublimenature9", 280, SEN, seq(1, 9), seq(1, 8) + [None], 0,
           NUMS(1, 8), label_rx=DOTNUM,
           moments=msd("Table 5", SEN, seq(1, 9), 1, 0, "M (SD)", MSD_M, MSD_SD)),
    # Chen et al. (2026), Table 2: "j. ABBR", M and SD in columns 1-2, lower triangle with a
    # dash diagonal in columns 3-10, Cronbach's alpha in column 11 (rel rows); names spelled
    # out from the table note.
    square("PMC13387045", "Table 2", "chen_2026_onlinefraud8", 765, FRA, seq(1, 8), seq(3, 10), 0, NUMS(1, 8),
           labels=FRA_LAB, label_rx=DOTNUM,
           moments=mom("mean", "Table 2", FRA, seq(1, 8), 1, 0, "M", labels=FRA_LAB, label_rx=DOTNUM)
           + mom("sd", "Table 2", FRA, seq(1, 8), 2, 0, "SD", labels=FRA_LAB, label_rx=DOTNUM)
           + mom("rel", "Table 2", FRA, seq(1, 8), 11, 0, "α", labels=FRA_LAB, label_rx=DOTNUM)),
    # Kanakubo et al. (2024), Table 3: Spearman; rows are the first eight variables, columns
    # the last eight (no row for J-BIDR, no column for the total), values above the diagonal.
    square("PMC10971768", "Table 3", "kanakubo_2024_lgbtdocss9", 381, LGB, seq(1, 8) + [None], [None] + seq(1, 8), 0,
           LGB[1:], labels=LGB_LAB),
    # Yao & Fan (2025), Table 4 (main study): "j. label", M and SD in columns 1-2, lower
    # triangle with a dash diagonal in columns 3-9, no column for the last variable.
    square("PMC12611650", "Table 4", "yao_2025_clail2w8", 305, CLW, seq(1, 8), seq(3, 9) + [None], 0, NUMS(1, 7),
           label_rx=DOTNUM,
           moments=mom("mean", "Table 4", CLW, seq(1, 8), 1, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 4", CLW, seq(1, 8), 2, 0, "SD", label_rx=DOTNUM)),
    # Song et al. (2026), TABLE 2: "j. label", M (SD) in column 1, lower triangle with a dash
    # diagonal in columns 2-9; both-wave completers (listwise, table note).
    square("PMC13715077", "TABLE 2", "song_2026_needthwarting8", 332, PNT, seq(1, 8), seq(2, 9), 0, NUMS(1, 8),
           label_rx=DOTNUM,
           moments=msd("TABLE 2", PNT, seq(1, 8), 1, 0, "M (SD)", MSD_M, MSD_SD, label_rx=DOTNUM)),
    # Cheung et al. (2022), Table 1: "(j) label", M and SD in columns 1-2 (dashes for the two
    # genders; the income mean, printed with a thousands comma, is not read), lower triangle
    # with a dash diagonal in columns 3-9, no column for the last variable.
    square("PMC9103894", "Table 1", "cheung_2022_parentselfcomp8", 189, PSC, seq(1, 8), seq(3, 9) + [None], 0,
           [f"({i})" for i in range(1, 8)], labels=PSC_LAB, label_rx=PARNUM,
           moments=mom("mean", "Table 1", PSC[3:], seq(4, 8), 1, 0, "M", labels=PSC_LAB[3:], label_rx=PARNUM)
           + mom("sd", "Table 1", PSC[3:], seq(4, 8), 2, 0, "SD", labels=PSC_LAB[3:], label_rx=PARNUM)),
    # Tzang et al. (2021), Table 2: "j. label", lower triangle with a dash diagonal in columns 1-8,
    # no column for the last variable; parent symptom abbreviations spelled out from the note.
    square("PMC8507797", "Table 2", "tzang_2021_adhdparent9", 231, ADH, seq(1, 9), seq(1, 8) + [None], 0, NUMS(1, 8),
           labels=ADH_LAB, label_rx=DOTNUM),
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
        if (d is not None and d.strip() not in DIAG | set(cfg.get("diag_extra", ()))
                and not (cfg.get("diag_rx") and re.fullmatch(cfg["diag_rx"], d.strip()))):
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
        raise SystemExit("usage: python3 pmc_article_tables_aq.py <out dir>")
    main(sys.argv[1])
