"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AN batch, 2026-11-19).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License", optionally with a version) or CC0; the script stops otherwise. An article
whose own metadata (<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article,
so they are not read.

Tables built (CONFIGS below): from agent AM's screened-only row and the scale-level
pass over the AC candidate list of 2026-11-18 (resumed at AM's stopping point,
PMC11020644). Attachment orientation and exploratory behaviour of older couples
(husbands' and wives' scores, couple as the unit); the eleven NEPT items (Needs and
Experiences in Psychiatric Treatment), item level; child maltreatment, ICD-11 PTSD and
DSO symptoms and emotion-regulation difficulties of trauma-clinic patients; executive
functions and early math of Yazidi, Syrian refugee and Italian preschoolers (three
groups); anxiety sensitivity, DASS-21 and dry-eye symptoms; social anhedonia and
internalizing symptoms of autistic children; drinking motives, protective behavioural
strategies and alcohol outcomes of hazardous-drinking college students. The N of each
is from the caption, a table note or the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_am.py (whose build code this file copies unchanged).
Each table is expanded into a grid (a cell with rowspan/colspan fills every position it
spans), so the `rows` and `cols` indices of a config are grid positions. Cells are read
as text. Significance stars are stripped; nothing else is changed. Unicode minus
(U+2212) and an en dash used as a minus are read as "-", and spaces inside a cell are
dropped ("0.22 **" -> "0.22"). For each pair of variables the script reads both cells
(row i/column j and row j/column i): exactly one must hold a number and the other must
be empty or a dash, or both must hold the same number. Where the two triangles hold two
samples (pellizzoni_2020_efmath11, Table 2: Yazidi children above the diagonal, Syrian
refugee children below), each group reads its own triangle (`lower_only` /
`upper_only`). A matrix printed as an upper triangle with no column for its first
variable (pellizzoni_2020_efmath11, Table 3) has that column given as None.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). Variable names are the printed
scale names, codes or NEPT component names (one or two words each); none is item
wording. Where a printed name carries a footnote marker ("Gendera") the marker is
dropped from the name; en dashes and U+2010 hyphens inside names are written as "-".

Mean and SD cells are read from the cell a config names; the row label of each moment
is checked the same way as the matrix rows, and the column header is checked too
(`hdr`). "M (SD)" cells are split by two regexes. They become mean/sd rows, values as
printed.
In nothel_2023_albs10 Cronbach's alpha is printed in parentheses on the diagonal
(`diag_rx`; "(–)" for single items): the diagonal is written 1 and the alphas become rel
rows (`diag_mom`).

Diagonal cells (1, 1.00, a dash or blank) are written as 1. Values are written in
shortest round-trip form of the published decimal (for example "0.40" -> "0.4", ".80"
-> "0.8", "-0.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_an.py <out dir>
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

WANG = [f"{v} ({s})" for s in ("H", "W") for v in ("Secure", "Avoidance", "Anxiety", "Engagement", "Enjoyment", "Distress")]
WANG_T3 = ["Avoidance", "Anxiety", "Secure", "Engagement", "Enjoyment", "Distress"]   # Table 3 row order
NEPT = ["Flexibility", "Activity", "Preventing (stigmatization)", "Compatibility with everyday life", "Autonomy",
        "Safety", "Continuity", "Intensity", "Knowledge", "Time", "Solidarity"]
NEPT_RX = r"^\d+ (.+)$"           # "3 Preventing (stigmatization)" -> "Preventing (stigmatization)"
KNE = ["PTSD", "DSO", "Child abuse", "Child neglect", "Adult re-victimisation", "ER non-accept", "ER goals",
       "ER impulse", "ER aware", "ER strategies", "ER clarity"]
PEL = ["Age", "STM", "WM", "Inhibitory control", "Forward counting (1-10)", "Forward counting (11-50)",
       "Backward counting (10-1)", "Backward counting (50-11)", "Digit-quantity mapping", "Digit naming (1-10)",
       "Digit naming (11-16)"]
PEL_LAB = ["Age (in months)"] + PEL[1:]
TOT = ["Gender", "Age", "OSDI", "ASI", "ASI-phy", "ASI-psy", "ASI-soc", "DASS-21", "DASS-dep", "DASS-anx", "DASS-stress"]
TOT_LAB = ["Gendera"] + TOT[1:]
GER = ["Age", "Male", "ADOS-2 CSS", "Composite IQ", "SRS-2 Total T-Score", "CASI-5 ADHD T-Score",
       "CASI-5 Social Anxiety T-Score", "CASI-5 Generalized Anxiety T-Score", "CASI-5 Separation Anxiety T-Score",
       "CASI-5 Depression T-Score", "CASI-5 Social Anhedonia Total"]
HAR = ["Substance Use Composite", "Drinks", "Drinking Days", "Drinks per Drinking Day", "RAPI", "DMQ Conformity",
       "DMQ Coping", "DMQ Enhancement", "DMQ Social", "PBSS Harm Reduction", "PBSS Limiting/Stopping",
       "PBSS Manner of Drinking"]
SON = ["Quantitative demands", "Organizational constraints", "Perceived prosocial impact", "Baseline negative affect",
       "Baseline positive affect", "Negative affect", "Positive affect", "Negative thinking", "Positive thinking",
       "Detachment experience", "Hobby"]
SON_ROWS = [2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 14]   # section rows 1, 7 and 10 skipped
GIB = ["Adoption beliefs scale", "Adoption in general", "International adoption", "Interethnic by Ladinos",
       "Interethnic by Indigenous", "Ethnicity", "MEIM-S", "Social distance from Ladinos",
       "Social distance from Indigenous", "ALG", "AIG"]
GHO = [f"Ghost {i}" for i in range(1, 11)]
NOE = ["Follower Age", "Follower Gender", "Leader Age", "Leader Gender", "Lengths of relationship (Dyad)",
       "Adaptive Leadership Behavior (FR)", "Job Satisfaction (FR)", "Perc. Leader Effectiveness (FR)",
       "Perc. Employee Effectiveness (LR)", "Leader's Irritability (LR)"]
NOE_LAB = ["Follower Gendera" if v == "Follower Gender" else "Leader Gendera" if v == "Leader Gender" else v
           for v in NOE]
NOE_REL = [5, 7, 8, 9]   # alphas printed on the diagonal; "(–)" for the others


def pel_moments(group_cols):
    """Pellizzoni et al. (2020), Table 1: M and SD of the ten task scores (not Age) for
    one group, in columns (m, sd); header row 1."""
    m, s = group_cols
    return (mom("mean", "TABLE 1", PEL[1:], seq(2, 11), m, 1, "M")
            + mom("sd", "TABLE 1", PEL[1:], seq(2, 11), s, 1, "SD"))


CONFIGS = [
    # Wang et al. (2021), Table 4: number in column 0, label in column 1 (H = husband's,
    # W = wife's score); lower triangle in columns 2-12 with a blank diagonal, no column
    # for the last variable. M (SD) per spouse from Table 3 (rows in another order).
    square("PMC8245056", "Table 4", "wang_2021_attachexplore12", 49, WANG, seq(1, 12), seq(2, 12) + [None], 0,
           NUMS(1, 11), label_col=1,
           moments=[m for sp, col, hdr in (("H", 2, "HusbandsM (SD)"), ("W", 3, "WivesM (SD)"))
                    for m in msd("Table 3", [f"{v} ({sp})" for v in WANG_T3], seq(1, 6), col, 0, hdr,
                                 MSD_M, MSD_SD, labels=WANG_T3, label_col=1)]),
    # von Peter et al. (2022), Table 2: NEPT items ("j Name"), lower triangle with a 1
    # diagonal; the corrected item-total and alpha-if-deleted rows below are not taken.
    # M and SD of the full sample from Table 1 (columns 5-6); the full-sample mean of
    # Knowledge (3.95) is not taken: it lies below both the men's (3.97) and the women's
    # (4.07) mean, so one of the three is misprinted.
    square("PMC8829038", "Table 2", "vonpeter_2022_nept11", 327, NEPT, seq(1, 11), seq(1, 11), 0, NUMS(1, 11),
           label_rx=NEPT_RX,
           moments=mom("mean", "Table 1", [v for v in NEPT if v != "Knowledge"],
                       [r for v, r in zip(NEPT, seq(2, 12)) if v != "Knowledge"], 5, 1, "M")
           + mom("sd", "Table 1", NEPT, seq(2, 12), 6, 1, "SD")),
    # Knefel et al. (2018), Table 1: upper triangle in columns 3-13 with a dash diagonal
    # (U+2010); M and SD in columns 1-2; no significance marks.
    square("PMC6686279", "Table 1", "knefel_2018_cptsd11", 193, KNE, seq(1, 11), seq(3, 13), 0, NUMS(1, 11),
           label_rx=DOTNUM,
           moments=mom("mean", "Table 1", KNE, seq(1, 11), 1, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 1", KNE, seq(1, 11), 2, 0, "SD", label_rx=DOTNUM)),
    # Pellizzoni et al. (2020), Table 2: Yazidi children (n = 48) above the diagonal,
    # Syrian refugee children (n = 47) below; header row 1. Table 3: Italian children
    # (n = 55), upper triangle with no column for Age (columns 1-10 are variables 2-11)
    # and dashes below. M and SD of the task scores from Table 1.
    dict(pmcid="PMC7076912", label="TABLE 2", table="pellizzoni_2020_efmath11", n=48, names=PEL, label_col=0,
         label_rx=DOTNUM, group="yazidi",
         parts=[dict(names=PEL, labels=PEL_LAB, rows=seq(2, 12), cols=seq(1, 11), col_labels=(1, NUMS(1, 11)), upper_only=True)],
         moments=pel_moments((3, 4))),
    dict(pmcid="PMC7076912", label="TABLE 2", table="pellizzoni_2020_efmath11", n=47, names=PEL, label_col=0,
         label_rx=DOTNUM, group="syrian",
         parts=[dict(names=PEL, labels=PEL_LAB, rows=seq(2, 12), cols=seq(1, 11), col_labels=(1, NUMS(1, 11)), lower_only=True)],
         moments=pel_moments((1, 2))),
    dict(pmcid="PMC7076912", label="TABLE 3", table="pellizzoni_2020_efmath11", n=55, names=PEL, label_col=0,
         label_rx=DOTNUM, group="italian",
         parts=[dict(names=PEL, labels=PEL_LAB, rows=seq(2, 12), cols=[None] + seq(1, 10), col_labels=(1, NUMS(2, 11)))],
         moments=pel_moments((5, 6))),
    # Toth & Jokic-Begic (2020), Table 2: lower triangle with a dash diagonal, no column
    # for the last variable; M and SD in columns 11-12 (none for gender).
    square("PMC8114394", "Table 2.", "toth_2020_dryeye11", 381, TOT, seq(1, 11), seq(1, 10) + [None], 0,
           NUMS(1, 10), labels=TOT_LAB, label_rx=DOTNUM,
           moments=mom("mean", "Table 2.", TOT[1:], seq(2, 11), 11, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 2.", TOT[1:], seq(2, 11), 12, 0, "SD", label_rx=DOTNUM)),
    # Gerber et al. (2025), Table 2: lower triangle with a blank diagonal in columns 3-12,
    # no column for the last variable; M and SD in columns 1-2.
    square("PMC12094631", "Table 2.", "gerber_2025_anhedonia11", 276, GER, seq(1, 11), seq(3, 12) + [None], 0,
           NUMS(1, 10), label_rx=DOTNUM,
           moments=mom("mean", "Table 2.", GER, seq(1, 11), 1, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 2.", GER, seq(1, 11), 2, 0, "SD", label_rx=DOTNUM)),
    # Hardee et al. (2026), Table 2: an empty row 1 under the header; lower triangle with a
    # blank diagonal in columns 1-11, no column for the last variable.
    square("PMC13389929", "Table 2.", "hardee_2026_drinkmotives12", 109, HAR, seq(2, 13), seq(1, 11) + [None], 0,
           NUMS(1, 11), label_rx=DOTNUM),
    # Sonnentag & Niessen (2020), Table 1: Study 1 (students, N = 122) above the diagonal,
    # Study 2 (employees, N = 159) below; section rows skipped; blank diagonal. Study 1
    # has no cells for variables 1-3 (work variables, measured only in Study 2), so its
    # matrix holds variables 4-11.
    dict(pmcid="PMC7596587", label="TABLE 1", table="sonnentag_2020_detach11", n=122, names=SON[3:], label_col=0,
         label_rx=PARNUM, group="study1",
         parts=[dict(names=SON[3:], rows=SON_ROWS[3:], cols=seq(4, 11), col_labels=(0, NUMS(4, 11)),
                     upper_only=True)]),
    dict(pmcid="PMC7596587", label="TABLE 1", table="sonnentag_2020_detach11", n=159, names=SON, label_col=0,
         label_rx=PARNUM, group="study2",
         parts=[dict(names=SON, rows=SON_ROWS, cols=seq(1, 11), col_labels=(0, NUMS(1, 11)), lower_only=True)]),
    # Gibbons et al. (2015), Table 3: lower triangle with a dash diagonal; N = 165-177
    # (pairwise; n written is the sample N of 177, an upper bound).
    square("PMC4684562", "Table 3", "gibbons_2015_adoption11", 177, GIB, seq(1, 11), seq(1, 11), 0, NUMS(1, 11),
           label_rx=DOTNUM),
    # Jahrami et al. (2023), Table 1: GHOST items (labels "Ghost j"), M and SD in columns
    # 1-2, lower triangle in columns 3-12 with a dash diagonal.
    square("PMC10361225", "Table 1", "jahrami_2023_ghost10", 811, GHO, seq(1, 10), seq(3, 12), 0, GHO,
           moments=mom("mean", "Table 1", GHO, seq(1, 10), 1, 0, "M")
           + mom("sd", "Table 1", GHO, seq(1, 10), 2, 0, "SD")),
    # Nothel et al. (2023), Table 3 (Study 3, 155 leader-follower dyads): M and SD in
    # columns 1-2; lower triangle in columns 3-12 with Cronbach's alpha in parentheses on
    # the diagonal ("(–)" for single items and demographics).
    square("PMC10565815", "TABLE 3", "nothel_2023_albs10", 155, NOE, seq(1, 10), seq(3, 12), 0, NUMS(1, 10),
           labels=NOE_LAB, label_rx=DOTNUM, diag_rx=PAREN_OR_DASH,
           moments=diag_mom("TABLE 3", [NOE[i] for i in NOE_REL], [i + 1 for i in NOE_REL], [i + 3 for i in NOE_REL],
                            0, [str(i + 1) for i in NOE_REL], PAREN, label_rx=DOTNUM,
                            labels=[NOE_LAB[i] for i in NOE_REL])
           + mom("mean", "TABLE 3", NOE, seq(1, 10), 1, 0, "M", labels=NOE_LAB, label_rx=DOTNUM)
           + mom("sd", "TABLE 3", NOE, seq(1, 10), 2, 0, "SD", labels=NOE_LAB, label_rx=DOTNUM)),
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
        raise SystemExit("usage: python3 pmc_article_tables_an.py <out dir>")
    main(sys.argv[1])
