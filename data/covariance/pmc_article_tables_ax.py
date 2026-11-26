"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY / CC0 open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AX batch, 2026-11-25).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License", optionally with a version) or CC0; the script stops otherwise. The one
exception is NC_EXCEPTION below (PMC5577646, read as CC BY-NC by Ben on 2026-11-25): its
exact licence text, for that PMCID only; its config is in PENDING (held for licence) and
is built only with IRW_COV_PENDING=1. An article whose own metadata (<article-meta>)
carries a retraction link (<related-article related-article-type="retraction-forward"> or
"retracted-article") is refused. Links of that kind inside the reference list mark a
retracted *cited* paper, not this article, so they are not read.

Tables built (CONFIGS below). First, cases held by earlier batches and buildable under
Ben's rulings of 2026-11-25: the European American group of elam_2021_alcoholprs7 (the
released African American group is copied unchanged from pmc_article_tables_as.py);
Kendall's tau among the IPQ-O sub-scales with per-cell N rows; Spearman correlations of
proactive health literacy with sociodemographics and lifestyle (per-cell n from the table
note); parents' and children's ethnic prejudice and parenting styles (stacked "r = / p = /
d = / n =" cells); promotion and prevention focus of students (one "< 0.01" cell written
blank); and perceptions of sexual harassment (two "− 06" cells written blank). Then the
scale-level pass over the AC candidate list of 2026-11-18, queue lines 296-315: change
scores after ACT for chronic pain (two titled blocks); children's gender flexibility
(girls above, boys below the diagonal); nap beliefs (pilot below, replication above);
media vicarious traumatization; body appreciation (boys below, girls above); polychoric
inter-item correlations of a physicians' autonomy-support measure ("r (SE)" cells, read
with `pick`); Hong Kong students' perceptions of the curriculum; perceived team
performance (per-cell n from the table note); dizziness and balance questionnaires
(Spearman, full square); and nurses' attitudes towards research (Spearman). The N of each
is from the caption, a table note or the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_am.py to pmc_article_tables_aw.py (whose build code this
file copies, adding the options below). Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions. Cells are read as text. Significance stars are stripped;
nothing else is changed. Unicode minus (U+2212) and an en dash used as a minus are read as
"-", and spaces inside a cell are dropped ("− .371**" -> "-.371"). For each pair of
variables the script reads both cells (row i/column j and row j/column i): exactly one
must hold a number and the other must be empty or a dash, or both must hold the same
number (a part marked `lower_only` / `upper_only` reads one side only, when the other side
prints another sample). A matrix with no row or column for a variable has it given as
None. A config's `pick` = (regex, i) reads group i out of a cell that prints several
values; the regex must match the whole cell. `title` = (row, col, text) checks a block
title printed in the table.

New in AX:
- `blank` = {pair: printed text}: a cell printed as something that is not a number ("<
  0.01", "− .0.02", "− 06") is written with an empty value (V4; Ben, 2026-11-25). The
  printed text must match exactly, and the blank cells must be exactly the listed ones.
  No value is ever invented for such a cell.
- `cell_n` = dict(dr, dc, rx, lab, vlab): per-cell n, printed beside each value (the cell
  dr rows and dc columns from it, fully matching rx); `lab` and `vlab` are the exact labels
  of the n row and of the value row. `n_fn(a, b)`: per-cell n by a rule quoted from the
  table note. `diag_n`: each variable's own n, read from a printed cell (it must be at
  least every cell n of that variable); without it a variable's own n is the largest n
  among its cells. The own n goes on the diagonal row and on the variable's moment rows.
- `label_dr`: the row label is printed dr rows away from the value row.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). The comparison ignores everything
but letters and digits, so a footnote marker ("Anxiety *") does not count. Variable names
are the printed labels without footnote markers and without their "j." / "(j)" numbers.

Mean, SD and reliability cells are read from the cell a config names; the row label of
each moment is checked the same way as the matrix rows, and the column header is checked
too (`hdr`). They become mean/sd/rel rows, values as printed.

Diagonal cells (1, 1.00, 1.000, a dash or blank) are written as 1. Values are written in
shortest round-trip form of the published decimal (for example "0.40" -> "0.4", ".80" ->
"0.8", "-0.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N on every row, unless the config gives per-cell n (above).

Usage: python3 data/covariance/pmc_article_tables_ax.py <out dir>
(set IRW_PMC_XML_DIR=<dir of PMCxxxx.xml> to read saved copies instead of Europe PMC;
IRW_COV_PENDING=1 also builds the PENDING configs)
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


# Elam et al. (2021), Table 1 (built by agent AS as group african_american; copied unchanged).
PRS = ["PRS"] + [f"Alcohol Use Wave {w} ({a}yo)" for w, a in
                  zip(range(6, 12), ["16–17", "18–19", "23–24", "24–25", "26–27", "28–30"])]
# Pedley et al. (2019), Table 7 (IPQ-O sub-scales); Table 6 labels the same sub-scales.
IPQ = ["Identity", "Consequences", "Control", "Permanence", "Coherence", "Reactivity", "Spectrum",
       "Emotional representation", "Environmental attributions", "Biological attributions",
       "Learned behaviour attributions", "Own characteristics attributions"]
IPQ_T6 = ["Identity scale", "Consequences", "Control", "Permanence", "Coherence", "Reactivity", "Spectrum",
          "Emotional representation", "Environmental stress", "Biological causes", "Learned behaviour",
          "Own characteristics or behaviour"]
NUMLAB2 = r"^\d+\.?\s+(.+)$"             # "5 Coherence" (no full stop) or "6. Reactivity"
T6LAB = r"^(?:\d+\.\s*)?(.+?) \([\d–-]+\)$"   # "1.Environmental stress (7–35)" -> "Environmental stress"
PHL = ["Sex", "Age group", "Education level", "Monthly household income", "Self-rated health (past year)",
       "Smoking status", "Alcohol consumption (past year)", "Dietary habits", "Meal regularity",
       "Proactive health literacy"]
PREJ = ["Parents Blatant", "Parents Subtle", "Child-Implicit", "Child-Explicit", "Authoritative", "Authoritarian",
        "Permissive"]
RFS = ["Promotion focus (t0)", "Prevention focus (t0)", "Perception (t0)", "Self-efficacy (t0)", "Motivation (t0)",
       "Perception (t1)", "Self-efficacy (t1)", "Motivation (t1)"]
MTO = ["Participant gender", "Participant sexual orientation", "Perceived discrimination", "Fear",
       "Perceived sexual harassment", "Past sexual harassment", "Age"]
MTO_L = ["Participant gendera", "Participant sexual orientationb", "Perceived discriminationc", "Feard",
         "Perceived sexual harassmentc", "Past sexual harassmente", "Agef"]
CIV = ["CEAP C", "BMI", "GIS", "Pain", "Physical dimension", "Psychological dimension"]


def n_phl(a, b):
    """Wang et al. (2026), Table 9 note: N = 560 for all variables except education level (N = 549)."""
    return 549 if "Education level" in (a, b) else 560


ACT = ["Pain", "SF-36 physical", "SF-36 social", "PHQ", "CPAQ", "CFQ", "EQ", "CAQ"]
TOY = ["Age", "Gender-typed feminine toy preference", "Gender-typed masculine toy preference",
       "Flexibility in gender-typed toy play", "Gender-typed playmate choice", "Gender-based social exclusion"]
PARLAB = r"^\d+\)\s*(.+)$"       # "1) NBS–Positive Beliefs" -> "NBS–Positive Beliefs"
NAP = ["NBS–Positive Beliefs", "NBS–Negative Beliefs", "Encourage–Child Related", "Encourage–Parent Related",
       "Discourage–Child Preference", "Discourage–Child Functioning", "Discourage–Scheduling"]
MVT = ["MVTS", "WWS", "WARMES", "DFS", "IUS", "GAD", "LOT-R"]
BAS = ["Body appreciation", "SOQ—body functionality", "Self-esteem", "Body dissatisfaction",
       "Disordered eating behaviors", "Body mass index"]
PAS = ["Q46", "Q47", "Q48r", "Q49", "Q50", "Q51"]
NSS = ["Age", "Gender", "Academic and school performance",
       "Fondness for and interest in the junior secondary curriculum (4 items)",
       "Perceived benefits of the junior secondary curriculum (5 items)",
       "Fondness for and interest in the senior secondary curriculum (4 items)",
       "Perceived benefits of the senior secondary curriculum (5 items)"]
NSS_L = ["Age", "Gender a"] + NSS[2:]
PPT = ["Mean PPTSQ", "Effort investment", "Perceived outcome", "Mean GEQ", "Mean TADI", "Objective performance"]
DHI = ["DHI-p", "DHI-e", "DHI-f", "SVQ", "ABC"]
NRA = ["Total factors", "Total Factor 1", "Total Factor 2", "Total Factor 3", "Total Factor 4", "Total Factor 5"]


def n_ppt(a, b):
    """Gershgoren et al. (2021), TABLE 8 note: N = 180 for correlations with objective performance."""
    return 180 if "Objective performance" in (a, b) else 453


CONFIGS = [
    # Elam et al. (2021), Table 1: African Americans above the diagonal (built by agent AS,
    # config copied unchanged), European Americans below it (n = 271, text). One European
    # American cell, PRS with wave 7, is printed "− .0.02" in the XML, the publisher's HTML
    # table and the publisher's PDF alike: written blank. The Mean (SD) row and column are
    # not read (the table does not say which sample each belongs to).
    square("PMC8599703", "Table 1", "elam_2021_alcoholprs7", 192, PRS, seq(1, 7), seq(1, 7), 0, NUMS(1, 7),
           label_rx=DOTNUM, group="african_american",
           part_kw=dict(upper_only=True)),
    square("PMC8599703", "Table 1", "elam_2021_alcoholprs7", 271, PRS, seq(1, 7), seq(1, 7), 0, NUMS(1, 7),
           label_rx=DOTNUM, group="european_american",
           part_kw=dict(lower_only=True), blank={pair("PRS", PRS[2]): "− .0.02"}),
    # Pedley et al. (2019), Table 7: Kendall's tau; each sub-scale has a "τ" row and an "N"
    # row below it (per-cell n); Identity (row 1) has no cells of its own; columns 2-13
    # (column 13 empty); blank diagonal. Each sub-scale's own N is Table 6's "N" column.
    square("PMC6617616", "Table 7", "pedley_2019_ipqo12", 348, IPQ, [1] + list(range(2, 23, 2)),
           seq(2, 13), 0, NUMS(1, 12), label_rx=NUMLAB2,
           cell_n=dict(dr=1, dc=0, rx=r"(\d+)", lab=(1, "N"), vlab=(1, "τ")),
           diag_n=mom("n", "Table 6", IPQ, [1, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14], 2, 0, "Na",
                      labels=IPQ_T6, label_rx=T6LAB)),
    # Wang et al. (2026), Table 9: Spearman; full square with a 1.000 diagonal and dashes above;
    # per-cell n from the table note (n_phl).
    square("PMC12960537", "Table 9", "wang_2026_proactivehl10", 560, PHL, seq(1, 10), seq(1, 10), 0, PHL,
           n_fn=n_phl),
    # Pirchio et al. (2018), Table 1: each cell is four stacked rows "r = ", "p = ", "d = ",
    # "n = "; the r row carries the row label; per-cell n three rows below the r; dash
    # diagonal; "M (SD)" row 26 (none for Permissive).
    square("PMC5811875", "Table 1", "pirchio_2018_prejudice7", 361, PREJ, [1, 2, 6, 10, 14, 18, 22], seq(1, 7), 0,
           NUMS(1, 7), label_rx=PARNUM, strip=r"^r=",
           cell_n=dict(dr=3, dc=0, rx=r"n = (\d+)"),
           moments=row_msd("Table 1", PREJ[:6], 26, seq(1, 6), "M (SD)", 0, NUMS(1, 6), MSD_M, MSD_SD)),
    # Hoch et al. (2024), Table 3 (students): n, M, SD in columns 1-3, lower triangle with a
    # dash diagonal in columns 4-10 (no column for the last variable). Prevention focus (t0)
    # with motivation (t0) is printed "< 0.01" (also on the publisher's page): written blank.
    square("PMC11424645", "Table 3", "hoch_2024_regfocus8", 1127, RFS, seq(1, 8), seq(4, 10) + [None], 0,
           NUMS(1, 7), label_rx=DOTNUM, blank={pair(RFS[1], RFS[4]): "< 0.01"},
           moments=mom("mean", "Table 3", RFS, seq(1, 8), 2, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 3", RFS, seq(1, 8), 3, 0, "SD", label_rx=DOTNUM)),
    # Clarke (2022), Table 3: M and SD in columns 1-2 (dashes for the three coded variables),
    # lower triangle with a 1 diagonal in columns 3-9. Two cells of the Age row are printed
    # "− 06" (the publisher's site refused automated fetches): written blank.
    square("PMC9363338", "Table 3", "clarke_2022_metoo7", 770, MTO, seq(1, 7), seq(3, 9), 0, NUMS(1, 7),
           labels=MTO_L, label_rx=DOTNUM, blank={pair("Fear", "Age"): "− 06", pair("Perceived sexual harassment", "Age"): "− 06"},
           moments=nolab("mean", "Table 3", sub(MTO, [2, 3, 4, 6]), [3, 4, 5, 7], 1, 0, "M", sub(MTO_L, [2, 3, 4, 6]),
                         label_rx=DOTNUM)
           + nolab("sd", "Table 3", sub(MTO, [2, 3, 4, 6]), [3, 4, 5, 7], 2, 0, "SD", sub(MTO_L, [2, 3, 4, 6]),
                   label_rx=DOTNUM)),
    # --- scale-level pass, queue lines 296-315 ---
    # Scott et al. (2016), Table 3: change scores, two blocks titled "Pre to post (n = 384)"
    # (rows 2-8) and "Pre to follow-up (n = 214)" (rows 10-16); Pain has a column but no
    # row, CAQ a row but no column; no diagonal printed.
    *[square("PMC4917588", "Table 3", "scott_2016_actchange8", n, ACT, [None] + seq(r0, r0 + 6), seq(1, 7) + [None],
             0, ACT[:7], labels=ACT, group=g, title=(r0 - 1, 0, tt))
      for g, n, r0, tt in (("pre_to_post", 384, 2, "Pre to post (n = 384)"),
                           ("pre_to_followup", 214, 10, "Pre to follow-up (n = 214)"))],
    # Spinner et al. (2018), Table 1: girls above the dash diagonal (n = 42), boys below
    # (n = 40); M (SD) columns not read (see notes).
    square("PMC6096659", "Table 1", "spinner_2018_toyflex6", 42, TOY, seq(2, 7), seq(3, 8), 1, NUMS(1, 6),
           label_rx=DOTNUM, group="girls", part_kw=dict(upper_only=True)),
    square("PMC6096659", "Table 1", "spinner_2018_toyflex6", 40, TOY, seq(2, 7), seq(3, 8), 1, NUMS(1, 6),
           label_rx=DOTNUM, group="boys", part_kw=dict(lower_only=True)),
    # Newton & Reid (2024), Table 3: pilot sample below the dash diagonal (n = 199),
    # replication sample above it (n = 701); labels "j) label".
    square("PMC12713905", "Table 3", "newton_2024_napbeliefs7", 199, NAP, seq(1, 7), seq(1, 7), 0, PAR(1, 7),
           label_rx=PARLAB, group="pilot", part_kw=dict(lower_only=True)),
    square("PMC12713905", "Table 3", "newton_2024_napbeliefs7", 701, NAP, seq(1, 7), seq(1, 7), 0, PAR(1, 7),
           label_rx=PARLAB, group="replication", part_kw=dict(upper_only=True)),
    # Regnoli et al. (2025), Table 5 (Study II): AVE in column 1 (not read), lower triangle
    # with a dash diagonal in columns 2-8.
    square("PMC12468483", "Table 5", "regnoli_2025_mvts7", 553, MVT, seq(1, 7), seq(2, 8), 0, NUMS(1, 7),
           label_rx=DOTNUM),
    # Baceviciene & Jankauskiene (2020), Table 5: boys below the 1 diagonal (n = 570), girls
    # above (n = 842); boys' M and SD in columns 1-2, girls' in columns 3-4.
    square("PMC7146197", "Table 5", "baceviciene_2020_bodyappr6", 570, BAS, seq(2, 7), seq(5, 10), 0, PAR(1, 6),
           label_rx=PARNUM, group="boys", part_kw=dict(lower_only=True),
           moments=mom("mean", "Table 5", BAS, seq(2, 7), 1, 1, "M", label_rx=PARNUM)
           + mom("sd", "Table 5", BAS, seq(2, 7), 2, 1, "SD", label_rx=PARNUM)),
    square("PMC7146197", "Table 5", "baceviciene_2020_bodyappr6", 842, BAS, seq(2, 7), seq(5, 10), 0, PAR(1, 6),
           label_rx=PARNUM, group="girls", part_kw=dict(upper_only=True),
           moments=mom("mean", "Table 5", BAS, seq(2, 7), 3, 1, "M", label_rx=PARNUM)
           + mom("sd", "Table 5", BAS, seq(2, 7), 4, 1, "SD", label_rx=PARNUM)),
    # Waddimba et al. (2020), Table 3: polychoric inter-item correlations, each printed
    # ".701 (.023)" with its SE in parentheses (`pick` reads the value); 1.000 diagonal;
    # "Mean (SD)" in column 1; item codes only (no wording).
    square("PMC7112234", "Table 3", "waddimba_2020_autonomysupp6", 767, PAS, seq(2, 7), seq(4, 9), 1, PAS,
           pick=(r"(\.\d+) \(\.\d+\)", 1),
           moments=msd("Table 3", PAS, seq(2, 7), 1, 1, "Mean (SD)", MSD_M, MSD_SD)),
    # Dou & Shek (2022), Table 1: number in column 0, label in column 1, Mean and SD in
    # columns 2-3 (none for gender), lower triangle with a blank diagonal in columns 4-9 (no
    # column for the last variable).
    square("PMC9354656", "Table 1", "dou_2022_nsscurric7", 3498, NSS, seq(1, 7), seq(4, 9) + [None], 0, NUMS(1, 6),
           labels=NSS_L, label_col=1,
           moments=nolab("mean", "Table 1", sub(NSS, [0, 2, 3, 4, 5, 6]), [1, 3, 4, 5, 6, 7], 2, 0, "Mean",
                         sub(NSS_L, [0, 2, 3, 4, 5, 6]), label_col=1)
           + nolab("sd", "Table 1", sub(NSS, [0, 2, 3, 4, 5, 6]), [1, 3, 4, 5, 6, 7], 3, 0, "SD",
                   sub(NSS_L, [0, 2, 3, 4, 5, 6]), label_col=1)),
    # Gershgoren et al. (2021), TABLE 8: samples 1 and 2 combined (N = 453); "(j) label",
    # lower triangle with a 1 diagonal; n = 180 for cells with objective performance (note).
    square("PMC7859492", "TABLE 8", "gershgoren_2021_pptsq6", 453, PPT, seq(1, 6), seq(1, 6), 0, PAR(1, 6),
           label_rx=PARNUM, n_fn=n_ppt),
    # Colnaghi et al. (2017), Table 1: Spearman; full square; each variable's "Rho" row
    # (rows 1, 4, ..., 13) is followed by a "p" row and an empty row; 1.000 diagonal; both
    # triangles are read and must agree.
    square("PMC5641311", "Table 1", "colnaghi_2017_dizziness5", 316, DHI, [1, 4, 7, 10, 13], seq(2, 6), 0, DHI,
           part_kw=dict(lower_only=True, asym=[])),
    # Rachmawati et al. (2016), Table 6: Spearman; upper triangle with a dash diagonal;
    # footnote letters "a"/"b" (p values) after each cell are dropped (`strip`).
    square("PMC5340165", "Table 6", "rachmawati_2016_nursresatt6", 92, NRA, seq(2, 7), seq(1, 6), 0, NRA,
           strip=r"[ab]$"),
]

# Not built by default (IRW_COV_PENDING=1 builds them into the same out dir): held for a
# licence question (see held.csv).
PENDING = [
    # Sinožić et al. (2017), Table 4: Spearman; upper triangle; each variable's label row is
    # followed by "rs", "P" and "n" rows; no row for the last variable; per-cell n two rows
    # below the rs. Licence CC BY-NC (Ben, 2026-11-25; NC_EXCEPTION).
    square("PMC5577646", "Table 4", "sinozic_2017_civiq6", 428, CIV, [2, 6, 10, 14, 18, None], seq(1, 6), 0, CIV,
           label_dr=-1, cell_n=dict(dr=2, dc=0, rx=r"(\d+)", lab=(0, "n"))),
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


# The one non-CC BY licence accepted, for this article only (Ben, 2026-11-25, #3564): its
# <license> reads "Creative Commons Attribution License, which permits unrestricted
# non-commercial use" with no URL, read as CC BY-NC.
NC_EXCEPTION = {"PMC5577646": "This is an open access article distributed under the Creative Commons Attribution "
                              "License, which permits unrestricted non-commercial use, distribution, and reproduction "
                              "in any medium, provided the original work is properly cited."}


def check_article(pmcid, root):
    lic = root.find(".//license")
    href = (lic.get("{http://www.w3.org/1999/xlink}href") or "") if lic is not None else ""
    links = " ".join(e.get("{http://www.w3.org/1999/xlink}href") or "" for e in lic.iter()) if lic is not None else ""
    ltxt = txt(lic) if lic is not None else ""
    if pmcid in NC_EXCEPTION:            # exactly the ruled text, with no licence link
        if ltxt != NC_EXCEPTION[pmcid] or links.strip():
            raise SystemExit(f"{pmcid}: licence text is not the one ruled on: {ltxt[:120]}")
    elif re.search(r"NonCommercial|NoDeriv|by-nc|by-nd|by-sa|ShareAlike", href + links + ltxt):
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
    for cfg in CONFIGS + (PENDING if os.environ.get("IRW_COV_PENDING") == "1" else []):
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
        raise SystemExit("usage: python3 pmc_article_tables_ax.py <out dir>")
    main(sys.argv[1])
