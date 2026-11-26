"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AM batch, 2026-11-19).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License", optionally with a version, as in the Europe PMC copy of PMC6266527: "Creative
Commons Attribution (CC BY) 3.0 License") or CC0; the script stops otherwise. An article whose own metadata
(<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article,
so they are not read.

Tables built (CONFIGS below): twelve tables (fourteen matrices) from twelve articles,
from the scale-level pass over the AC candidate list of 2026-11-18 (resumed at agent
AL's stopping point, after AL's screened-only row). All are scale-level matrices: job
satisfaction and information paucity in the German BIBB/BAuA Employment Survey 2012;
leisure-time physical activity, academic stressors, exhaustion and anxiety of
university faculty at three waves; mental recovery, passion and running-related
injuries; four brief narcissism measures; AI-ecological coupling and language-learning
engagement; job stressors, workaholism and health; the Impostor Phenomenon Assessment
with personality and self-esteem; online group polarization and value judgements;
workaholism, work engagement and work-life interference; role demands, work-family
conflict and burnout of nurses; teachers' personal responsibility (pre-service and
practicing teachers, one group each); managerial interpersonal skills (Studies 2 and 3,
one group each). The N of each is from the caption, a table note or the article text,
as noted in matrices.csv.

Parsing: as pmc_article_tables_al.py (whose build code this file copies, with one change: the
licence-text regex also accepts a version number before "License").
Each table is expanded into a grid (a cell with rowspan/colspan fills every position it
spans), so the `rows` and `cols` indices of a config are grid positions; section rows
printed between blocks of variables are skipped by listing only the variable rows.
Cells are read as text. Significance stars are stripped; nothing else is changed.
Unicode minus (U+2212) and an en dash used as a minus are read as "-", and spaces
inside a cell are dropped ("− 0.06" -> "-0.06"). For each pair of variables the script
reads both cells (row i/column j and row j/column i): exactly one must hold a number and
the other must be empty or a dash, or both must hold the same number. Where the two
triangles hold two samples (daniels_2017_responsibility12: pre-service teachers below
the diagonal, practicing teachers above), each group reads its own triangle
(`lower_only` / `upper_only`).

The diagonal may hold Cronbach's alpha in parentheses (`diag_rx`; written as `rel` rows
by `diag_mom`, and the diagonal as 1) or, in henttonen_2022_narcissism15, the average
inter-item correlation in parentheses (not a reliability: not taken, diagonal written
1). In beenen_2021_mips11 (Study 3) one diagonal cell is printed "0(.87)"; it is
accepted as a diagonal (`diag_extra`) and its alpha is not taken.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). Variable names are the printed
scale names or codes (PA_T1, Q1, EPC, ...); none is item wording.

Mean, SD and reliability (Cronbach's alpha, `rel`) cells are read from the cell a
config names; the row label of each moment is checked the same way as the matrix rows,
and the column header is checked too (`hdr`). Means printed with a marker ("0.54 #")
are split by a regex (`rx`). They become mean/sd/rel rows, values as printed.

Diagonal cells (1, 1.00, 1.000, a dash or blank) are written as 1. Values are written
in shortest round-trip form of the published decimal (for example "0.40" -> "0.4",
".80" -> "0.8", "-0.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_am.py <out dir>
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

KOT_LAB = ["Global job satisfaction", "Social climate", "Structural conditions", "Growth opportunities",
           "Material incentives", "Paucity of information", "Multiple jobsa", "Tenure (years)",
           "Working hours (week)", "ISEI", "Genderb", "Age", "Workload", "Autonomy"]
KOT = ["Global job satisfaction", "Social climate", "Structural conditions", "Growth opportunities",
       "Material incentives", "Paucity of information", "Multiple jobs", "Tenure", "Working hours", "ISEI",
       "Gender", "Age", "Workload", "Autonomy"]
KOT_ROWS = [1] + seq(3, 8) + seq(10, 12) + [14, 15, 17, 18]
LI = [f"{v}_T{t}" for t in (1, 2, 3) for v in ("PA", "CS", "HS", "EE", "SA")]
DEJ_LAB = ["Gender (0 = female; 1 = male)", "Age (years)", "Training schedule (0 = no; 1 = yes)",
           "Running distance (km)", "Running time (hours)", "Mental detachment from running",
           "Mental recovery after running", "Harmonious passion (HP)", "Obsessive passion (OP)",
           "Mental detachment × HP", "Mental recovery × HP", "Mental detachment × OP", "Mental recovery × OP",
           "RRIs (0 = no; 1 = yes)"]
DEJ = ["Gender", "Age", "Training schedule", "Running distance", "Running time", "Mental detachment",
       "Mental recovery", "HP", "OP", "Mental detachment x HP", "Mental recovery x HP", "Mental detachment x OP",
       "Mental recovery x OP", "RRIs"]
HEN = ["NPI-13 total", "Leadership/authority (LA)", "Grandiose/exhibitionism (GE)",
       "Entitlement/exploitativeness (EE)", "SB-PNI total", "SB-PNI grandiosity", "PNI vulnerability", "HSNS total",
       "Oversensitivity to judgment (OS)", "Egocentrism (EGO)", "g-FLUX total", "Indifference/anger (I)",
       "Grandiosity/shame (G)", "Assertiveness/insecurity (A)", "Age"]
GE = ["AI usage frequency", "Perceived AI-ecological coupling quality (overall)", "AI-empowered perception (overall)",
      "AI-disempowerment perception (overall)", "AI-Teacher", "AI-Peer", "AI-Environment", "Behavioral",
      "Cognitive", "Emotional", "Social"]
GE_ROWS = [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 13]
AND = ["Demand", "Control", "Social support", "Effort–reward ratio", "Overcommitment",
       "Bergen Work Addiction Scale", "Bergen Insomnia Scale", "Emotional exhaustion", "Cynicism",
       "Professional efficacy", "Somatic symptoms", "Anxiety/insomnia", "Social dysfunction", "Severe depression"]
WAL = ["DA", "PD", "SHB", "Total IPA", "Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism",
       "Openness", "Rigid Perfectionism", "Self-critical Perfectionism", "Narcissistic Perfectionism", "Self-esteem"]
HE = ["Q1", "Q2", "Q4", "Q5", "Q7", "Q8", "Q9", "EPC", "EPD", "CDR", "ECR", "VJD", "VCS"]
DIS = ["Gender", "Age", "Tenure", "WIPL", "PLIW", "W-EN", "DE", "AB", "VI", "WO", "WE", "WC"]
ASI = ["Gender", "Marital status", "Age", "Number of older parents", "Weekend work", "Number of children",
       "Family time commitment", "Weekly work hours", "Workload", "Work‐to‐family conflict",
       "Family‐to‐work conflict", "Burnout"]
DAN_LAB = ["Years teaching experience", "Gendera", "Teaching levelb", "Responsibility for motivation",
           "Responsibility for achievement", "Responsibility for relationships", "Responsibility for own teaching",
           "Teacher efficacy", "Teacher engagement", "Mastery approaches", "Performance approaches",
           "Measure of wellbeingc"]
DAN = ["Years teaching experience", "Gender", "Teaching level", "Responsibility for motivation",
       "Responsibility for achievement", "Responsibility for relationships", "Responsibility for own teaching",
       "Teacher efficacy", "Teacher engagement", "Mastery approaches", "Performance approaches",
       "Measure of wellbeing"]
# The printed "Measure of wellbeing" is the Satisfaction with Life Scale for pre-service
# teachers and burnout for practicing teachers (table note c), so each group names it by
# what it measured.
DAN_PRE = DAN[:-1] + ["SWLS"]
DAN_PRA = DAN[:-1] + ["Burnout"]
BEE3 = ["Supporting", "Motivating", "Managing Conflict", "MIPS", "Supervisor Support", "Conflict Avoidance", "OCB",
        "Supervisor Performance", "Organizational Commitment", "Leader-Member Exchange", "Experience with Supervisor"]
BEE2 = ["Supporting", "Motivating", "Managing Conflict", "MIPS", "Extraversion", "Agreeableness", "Job Satisfaction",
        "Managing-self", "Experience with Supervisor"]
BEE3_REL = [0, 1, 2, 3, 4, 6, 7, 8, 9]   # Conflict Avoidance (index 5) has its alpha printed "0(.87)"

CONFIGS = [
    # Kottwitz et al. (2017), Table 1: BIBB/BAuA Employment Survey 2012; lower triangle
    # with a dash diagonal, no column for the last variable; section rows (dimension,
    # context, person and working-condition headings) between the blocks; M and SD in
    # columns 1-2 (no SD for the two dummies). Two labels carry footnote markers
    # ("Multiple jobsa", "Genderb": coding notes).
    square("PMC5526968", "Table 1", "kottwitz_2017_jobsatinfo14", 17782, KOT, KOT_ROWS, seq(3, 15) + [None], 0,
           NUMS(1, 13), labels=KOT_LAB, label_rx=PARNUM,
           moments=mom("mean", "Table 1", KOT, KOT_ROWS, 1, 0, "M", labels=KOT_LAB, label_rx=PARNUM)
           + mom("sd", "Table 1", [v for v in KOT if v not in ("Multiple jobs", "Gender")],
                 [r for v, r in zip(KOT, KOT_ROWS) if v not in ("Multiple jobs", "Gender")], 2, 0, "SD",
                 labels=[l for v, l in zip(KOT, KOT_LAB) if v not in ("Multiple jobs", "Gender")],
                 label_rx=PARNUM)),
    # Li et al. (2026), Table 2: five variables at three waves; lower triangle with a 1
    # diagonal, no column for the last variable; M and SD in columns 1-2.
    square("PMC13203080", "Table 2", "li_2026_academicstress15", 356, LI, seq(1, 15), seq(3, 16) + [None], 0,
           NUMS(1, 14),
           moments=mom("mean", "Table 2", LI, seq(1, 15), 1, 0, "M")
           + mom("sd", "Table 2", LI, seq(1, 15), 2, 0, "SD")),
    # de Jonge et al. (2020), Table 1: lower triangle with a blank diagonal, no column for
    # the last variable; M (dummies marked "#") and SD in columns 1-2.
    square("PMC7037891", "Table 1", "dejonge_2020_runninginjury14", 246, DEJ, seq(1, 14), seq(3, 15) + [None], 0,
           NUMS(1, 13), labels=DEJ_LAB, label_rx=DOTNUM,
           moments=[dict(m, rx=LEADNUM_M) for m in mom("mean", "Table 1", DEJ, seq(1, 14), 1, 0, "M",
                                                         labels=DEJ_LAB, label_rx=DOTNUM)]
           + mom("sd", "Table 1", DEJ, seq(1, 14), 2, 0, "SD", labels=DEJ_LAB, label_rx=DOTNUM)),
    # Henttonen et al. (2022), Table 4: labels in column 0, numbers in column 1, lower
    # triangle in columns 2-15; the diagonal holds average inter-item correlations in
    # parentheses (not taken); Age (last row) has no column.
    square("PMC9589046", "Table 4", "henttonen_2022_narcissism15", 439, HEN, seq(1, 15), seq(2, 15) + [None], 0,
           NUMS(1, 14), diag_rx=PAREN),
    # Ge et al. (2026), Table 2: section rows 5 and 9; lower triangle in columns 5-15 with
    # Cronbach's alpha in parentheses on the diagonal ("(–)" for the single item); M and
    # SD in columns 1-2.
    square("PMC12872916", "Table 2", "ge_2026_aiengagement11", 475, GE, GE_ROWS, seq(5, 15), 0, NUMS(1, 11),
           label_rx=DOTNUM, diag_rx=PAREN_OR_DASH,
           moments=diag_mom("Table 2", GE[1:], GE_ROWS[1:], seq(6, 15), 0, NUMS(2, 11), PAREN, label_rx=DOTNUM)
           + mom("mean", "Table 2", GE, GE_ROWS, 1, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 2", GE, GE_ROWS, 2, 0, "SD", label_rx=DOTNUM)),
    # Andreassen et al. (2018), Table 2: Pearson; lower triangle with a blank diagonal, no
    # column for the last variable.
    square("PMC5800172", "Table 2", "andreassen_2018_workaholism14", 988, AND, seq(1, 14), seq(1, 13) + [None], 0,
           NUMS(1, 13), label_rx=DOTNUM),
    # Walker & Saklofske (2023), Table 9 (Study 3): lower triangle with a dash diagonal;
    # M, SD and alpha in columns 1-3.
    square("PMC10478341", "Table 9.", "walker_2023_impostor13", 562, WAL, seq(1, 13), seq(4, 16), 0, NUMS(1, 13),
           label_rx=DOTNUM,
           moments=mom("mean", "Table 9.", WAL, seq(1, 13), 1, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 9.", WAL, seq(1, 13), 2, 0, "SD", label_rx=DOTNUM)
           + mom("rel", "Table 9.", WAL, seq(1, 13), 3, 0, "α", label_rx=DOTNUM)),
    # He et al. (2026), Table 3: Pearson; lower triangle with a 1 diagonal, columns headed
    # by the codes; M and SD in columns 1-2.
    square("PMC13603983", "Table 3", "he_2026_polarization13", 1335, HE, seq(1, 13), seq(3, 15), 0, HE,
           moments=mom("mean", "Table 3", HE, seq(1, 13), 1, 0, "M")
           + mom("sd", "Table 3", HE, seq(1, 13), 2, 0, "SD")),
    # Di Stefano & Gaudiino (2018), Table 1: number in column 0, abbreviation in column 1;
    # lower triangle in columns 5-15 with a blank diagonal, no column for the last
    # variable; M, SD and alpha in columns 2-4 (no alpha for gender, age, tenure).
    square("PMC6266527", "Table 1", "distefano_2018_workaholism12", 212, DIS, seq(1, 12), seq(5, 15) + [None], 0,
           NUMS(1, 11), label_col=1,
           moments=mom("mean", "Table 1", DIS, seq(1, 12), 2, 0, "M", label_col=1)
           + mom("sd", "Table 1", DIS, seq(1, 12), 3, 0, "SD", label_col=1)
           + mom("rel", "Table 1", DIS[3:], seq(4, 12), 4, 0, "α", label_col=1)),
    # Asiedu et al. (2018), Table 2: number in column 0, label in column 1; lower triangle
    # with a 1.00 diagonal in columns 4-15; Mean and SD in columns 2-3 (dashes for gender
    # and marital status).
    square("PMC6178356", "Table 2", "asiedu_2018_nurseburnout12", 134, ASI, seq(1, 12), seq(4, 15), 0, NUMS(1, 12),
           label_col=1,
           moments=mom("mean", "Table 2", ASI[2:], seq(3, 12), 2, 0, "Mean", label_col=1)
           + mom("sd", "Table 2", ASI[2:], seq(3, 12), 3, 0, "SD", label_col=1)),
    # Daniels et al. (2017), Table 2: pre-service teachers below the diagonal (variable 1,
    # years of teaching experience, not measured: dashes), practicing teachers above;
    # dash diagonal; three labels carry footnote markers (coding notes). The printed "Measure of
    # wellbeing" is named SWLS (pre-service) and Burnout (practicing), per note c.
    dict(pmcid="PMC5449472", label="Table 2", table="daniels_2017_responsibility12", n=130, names=DAN_PRE[1:],
         label_col=0, label_rx=PARNUM, group="preservice",
         parts=[dict(names=DAN_PRE[1:], labels=DAN_LAB[1:], rows=seq(2, 12), cols=seq(2, 12),
                     col_labels=(0, NUMS(2, 12)), lower_only=True)]),
    dict(pmcid="PMC5449472", label="Table 2", table="daniels_2017_responsibility12", n=104, names=DAN_PRA,
         label_col=0, label_rx=PARNUM, group="practicing",
         parts=[dict(names=DAN_PRA, labels=DAN_LAB, rows=seq(1, 12), cols=seq(1, 12),
                     col_labels=(0, NUMS(1, 12)), upper_only=True)]),
    # Beenen et al. (2021), Tables 1 (Study 2) and 3 (Study 3): lower triangles with
    # Cronbach's alpha in parentheses on the diagonal; Experience with Supervisor (last
    # row) has no column; M and SD in columns 1-2.
    square("PMC8039519", "TABLE 1", "beenen_2021_mips11", 157, BEE2, seq(1, 9), seq(3, 10) + [None], 0,
           NUMS(1, 8), diag_rx=PAREN, group="study2",
           moments=diag_mom("TABLE 1", BEE2[:8], seq(1, 8), seq(3, 10), 0, NUMS(1, 8), PAREN)
           + mom("mean", "TABLE 1", BEE2, seq(1, 9), 1, 0, "M")
           + mom("sd", "TABLE 1", BEE2, seq(1, 9), 2, 0, "SD")),
    square("PMC8039519", "TABLE 3", "beenen_2021_mips11", 124, BEE3, seq(1, 11), seq(3, 12) + [None], 0,
           NUMS(1, 10), diag_rx=PAREN, diag_extra=("0(.87)",), group="study3",
           moments=diag_mom("TABLE 3", [BEE3[i] for i in BEE3_REL], [i + 1 for i in BEE3_REL],
                            [i + 3 for i in BEE3_REL], 0, [str(i + 1) for i in BEE3_REL], PAREN)
           + mom("mean", "TABLE 3", BEE3, seq(1, 11), 1, 0, "M")
           + mom("sd", "TABLE 3", BEE3, seq(1, 11), 2, 0, "SD")),
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
        raise SystemExit("usage: python3 pmc_article_tables_am.py <out dir>")
    main(sys.argv[1])
