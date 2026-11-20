"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AV batch, 2026-11-19).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License", optionally with a version) or CC0; the script stops otherwise. An article
whose own metadata (<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article,
so they are not read.

Tables built (CONFIGS below): from the scale-level pass over the AC candidate list of
2026-11-18, resumed at agent AU's stopping point (queue line 244). Leadership
characteristics, work and personal resources and counterproductive work behaviour of
employees (Cronbach's alphas on the diagonal become rel rows); the six subscales of the
Online Shopping Addiction Scale in Chinese college students (alphas from their own column
become rel rows); the two Creature of Habit scales with trait anxiety, goal pursuit,
compulsivity and sensation seeking (an SPSS-style full square with "Sig." rows); attachment
anxiety and avoidance, emotional flooding, hostility and withdrawal of expectant couples
(men below the diagonal and women above it, groups "Men" and "Women"); teaching
experience with perceived stress, emotional competence and self-efficacy of Italian
teachers before and after an online intervention; biological sex, three schizotypy
domains, subjective and objective cognitive functioning and their discrepancy index;
smartphone addiction, resilience and PTSD symptoms of South African students; emotions,
vaccine confidence and hesitancy and willingness to vaccinate for COVID-19 in Canada (an
upper triangle without a diagonal); loneliness, ego-resilience, anxiety, depression and
hopelessness of South African young adults; fear of COVID-19, perceived stress, sense of
coherence and PTSD symptoms of South African students; age, gender, partner phubbing,
relationship satisfaction, attachment anxiety and two conflict coping styles of young
adults; fear of COVID-19, anxiety, hopelessness, sense of coherence and life satisfaction
of South African teachers; pre-post change scores of the Clinical Quality of Life Scale
and five well-being measures in a mindfulness program; and the seven Meaning and Purpose
Scales in a German national sample (M, SD and alpha from the article's descriptive table);
and quit intention and anti-industry beliefs and attitudes at baseline and post-test, with
previous quit attempts, of sexual minority women who smoke, in an online message trial. Where a table prints a reliability
row or column, Cronbach's alpha becomes the rel row (an omega row is not read). The N of
each is from the caption, a table note or the article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_am.py to pmc_article_tables_au.py (whose build code this
file copies unchanged). Each table is expanded into a grid (a cell with rowspan/colspan
fills every position it spans), so the `rows` and `cols` indices of a config are grid
positions. Cells are read as text. Significance stars are stripped; nothing else is
changed. Unicode minus (U+2212) and an en dash used as a minus are read as "-", and spaces
inside a cell are dropped ("− .371**" -> "-.371"). For each pair of variables the script
reads both cells (row i/column j and row j/column i): exactly one must hold a number and
the other must be empty or a dash, or both must hold the same number (a part marked
`lower_only` or `upper_only` reads one side only). A matrix with no column for its last
variable has that column given as None, and one with no row for its last variable
(muis_2024_vaxemotion8, an upper triangle without a diagonal, which also has no column for
its first variable) has that row given as None. In ersche_2017_cohs6 one cell ends in a
"+" that the caption explains (it marks the coefficient between the two subscale summary
scores); a config's `strip` removes it before the stars.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). The comparison ignores everything
but letters and digits, so a footnote marker ("Anxiety *") does not count. Variable names
are the printed labels without footnote markers and without their "j." / "(j)" numbers.

Mean, SD and reliability cells are read from the cell a config names; the row label of
each moment is checked the same way as the matrix rows, and the column header is checked
too (`hdr`). They become mean/sd/rel rows, values as printed.

Diagonal cells (1, 1.00, 1.0, a dash, "--", "–-" or blank, or a printed alpha "(0.86)"
where a config's `diag_rx` allows it) are written as 1. In morgan_2026_prenatalconflict5
the diagonal prints the correlation between partners (not read): men are read below the
diagonal (`lower_only`) and women above it (`upper_only`). In ersche_2017_cohs6 both copies
of the full square must agree. Values are written in shortest round-trip form of the
published decimal (for example "0.40" -> "0.4", ".80" -> "0.8", "-0.00" -> "-0.0"), i.e.
unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_av.py <out dir>
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
NUMSP = r"^\d+\s+(.+)$"                     # "1 Salience" -> "Salience"
LCW = ["Psychology", "Behavior", "Ability", "Work resources", "Personal resources", "CWBI", "CWBO"]
OSA = ["Salience", "Tolerance", "Mood modification", "Withdrawal", "Relapse", "Conflict"]
COHS = ["COHS routine", "COHS automaticity", "STAI-T total score", "HSCQ total score", "OCI-R total score",
        "SSS-V total score"]
COHS_H = ["COHS routine", "COHS automaticity", "STAI-T total", "HSCQ total", "OCI-R total", "SSS-V total"]
PNC = ["ANX", "AVO", "FLO", "HOS", "WDR"]
TST = ["Years of teaching experience", "Perceived Stress (PRE)", "Emotional Competence (PRE)", "Self-Efficacy (PRE)",
       "Perceived Stress (POST)", "Emotional Competence (POST)", "Self-Efficacy (POST)"]
SZT = ["Biological sex", "Cognitive perceptual schizotypy", "Interpersonal schizotypy", "Disorganized schizotypy",
       "Subjective cognitive functioning", "Objective cognitive functioning", "SODI"]
SPT = ["Smartphone addiction", "Resilience", "PTSD", "Re-experiencing", "Avoidance", "Negative alterations",
       "Hyperarousal"]
VAX = ["Confidence", "Hesitancy", "Joy", "Hope", "Empathy", "Relief", "Anger", "Willingness"]
LON = ["Collective connectedness", "Isolation", "Relational connectedness", "Ego-resilience", "Anxiety", "Depression",
       "Hopelessness"]
FCP = ["Fear of COVID-19", "Perceived stress", "Sense of coherence", "Re-experiencing", "Avoidance",
       "Negative alterations", "Hyper-arousal"]
PHB = ["Age", "Gender", "Partner phubbing", "Relationship satisfaction", "Attachment anxiety", "Voice", "Loyalty"]
SOC = ["Fear of COVID-19", "Anxiety", "Hopelessness", "Comprehensibility", "Manageability", "Meaningfulness",
       "Life satisfaction"]
CLQ = ["CLINQOL", "MAAS", "AqoL", "PWI", "PA", "NA", "SWLS"]
MAP = ["Meaningfulness", "Crisis of Meaning", "Sustainability", "Faith", "Security", "Community", "Personal Growth"]
AIQ = ["Baseline quit intention", "Post-test quit intention", "Baseline anti-industry beliefs",
       "Post-test anti-industry beliefs", "Baseline anti-industry attitude", "Post-test anti-industry attitude",
       "Previous quit attempts"]
FOOTB = r"^(.+?)b$"                         # "Meaningfulnessb" (footnote b) -> "Meaningfulness"


def sa_table(pmcid, label, table, n, names, alpha_row=None):
    """The Padmanabhanunni & Pretorius layout: "j. label" rows 1-7, lower triangle with an
    em-dash diagonal in columns 1-7 (headers 1-7 in row 0), then Mean and SD rows (8, 9) and
    an Alpha row (alpha_row) read as rel."""
    k = len(names)
    mo = (row_mom("mean", label, names, k + 1, seq(1, k), "Mean", 0, NUMS(1, k))
          + row_mom("sd", label, names, k + 2, seq(1, k), "SD", 0, NUMS(1, k)))
    if alpha_row:
        mo += row_mom("rel", label, names, alpha_row, seq(1, k), "Alpha", 0, NUMS(1, k))
    return square(pmcid, label, table, n, names, seq(1, k), seq(1, k), 0, NUMS(1, k), label_rx=DOTNUM,
                  moments=mo)


CONFIGS = [
    # Shen & Lei (2022), TABLE 6: number and label in columns 0-1, M and SD in 2-3, lower
    # triangle in 4-10 with Cronbach's alphas "(0.840)" on the diagonal (rel rows).
    square("PMC8896057", "TABLE 6", "shen_2022_leadercwb7", 187, LCW, seq(1, 7), seq(4, 10), 0, NUMS(1, 7),
           label_col=1, diag_rx=r"\(0\.\d+\)",
           moments=mom("mean", "TABLE 6", LCW, seq(1, 7), 2, 0, "M", label_col=1)
           + mom("sd", "TABLE 6", LCW, seq(1, 7), 3, 0, "SD", label_col=1)
           + diag_mom("TABLE 6", LCW, seq(1, 7), seq(4, 10), 0, NUMS(1, 7), PAREN, label_col=1)),
    # Zhao et al. (2017), Table 5: "j label", Alpha in column 1 (rel rows), lower triangle with
    # a 1 diagonal in columns 2-7.
    square("PMC5432625", "Table 5", "zhao_2017_osas6", 328, OSA, seq(1, 6), seq(2, 7), 0, NUMS(1, 6),
           label_rx=NUMSP, moments=mom("rel", "Table 5", OSA, seq(1, 6), 1, 0, "Alpha", label_rx=NUMSP)),
    # Ersche et al. (2017), Table 3: each variable has a "Pearson correlation" row (read) and a
    # "Sig. (2-tailed)" row (not read); a full square with a 1 diagonal, the copies must agree.
    square("PMC5473478", "Table 3", "ersche_2017_cohs6", 362, COHS, [1, 3, 5, 7, 9, 11], seq(2, 7), 0, COHS_H,
           part_kw=dict(lower_only=True, asym=[]), strip=r"\+$"),
    # Morgan & Woodin (2026), Table 2: men below the diagonal, women above it, the correlation
    # between partners on it (not read). M and SD of men in rows 6-7, of women in columns 6-7.
    dict(square("PMC13150407", "Table 2", "morgan_2026_prenatalconflict5", 96, PNC, seq(1, 5), seq(1, 5), 0,
                NUMS(1, 5), label_rx=DOTNUM, diag_rx=r"-?0\.\d+\**", part_kw=dict(lower_only=True),
                moments=row_mom("mean", "Table 2", PNC, 6, seq(1, 5), "M(m)", 0, NUMS(1, 5))
                + row_mom("sd", "Table 2", PNC, 7, seq(1, 5), "SD(m)", 0, NUMS(1, 5))),
         group="Men"),
    dict(square("PMC13150407", "Table 2", "morgan_2026_prenatalconflict5", 96, PNC, seq(1, 5), seq(1, 5), 0,
                NUMS(1, 5), label_rx=DOTNUM, diag_rx=r"-?0\.\d+\**", part_kw=dict(upper_only=True),
                moments=mom("mean", "Table 2", PNC, seq(1, 5), 6, 0, "M(w)", label_rx=DOTNUM)
                + mom("sd", "Table 2", PNC, seq(1, 5), 7, 0, "SD(w)", label_rx=DOTNUM)),
         group="Women"),
    # Ornaghi et al. (2026), Table 1: lower triangle with a dash diagonal; Mean and Standard
    # deviation rows below (kurtosis and skewness rows not read).
    square("PMC12827693", "Table 1", "ornaghi_2026_teacherstress7", 151, TST, seq(1, 7), seq(1, 7), 0, NUMS(1, 7),
           moments=row_mom("mean", "Table 1", TST, 8, seq(1, 7), "Mean", 0, NUMS(1, 7))
           + row_mom("sd", "Table 1", TST, 9, seq(1, 7), "Standard deviation", 0, NUMS(1, 7))),
    # Nakirikanti et al. (2026), Table 2: "j. label", lower triangle with a dash diagonal.
    square("PMC13019055", "Table 2", "nakirikanti_2026_schizotypy7", 1036, SZT, seq(1, 7), seq(1, 7), 0, NUMS(1, 7),
           label_rx=DOTNUM),
    # Padmanabhanunni & Pretorius (2025), Healthcare, Table 2 (Alpha row 12).
    sa_table("PMC12692364", "Table 2", "padmanabhanunni_2025_smartphoneptsd7", 491, SPT, alpha_row=12),
    # Muis et al. (2024), Table 2: an upper triangle without a diagonal: rows Confidence..Anger,
    # columns Hesitancy..Willingness (no row for Willingness, no column for Confidence).
    square("PMC11098132", "Table 2", "muis_2024_vaxemotion8", 325, VAX, seq(1, 7) + [None], [None] + seq(1, 7), 0,
           VAX[1:]),
    # Padmanabhanunni & Pretorius (2025), Frontiers in Psychiatry, Table 1 (Alpha row 12; the
    # Omega row 13 is not read).
    sa_table("PMC11739145", "Table 1", "padmanabhanunni_2025_loneliness7", 337, LON, alpha_row=12),
    # Padmanabhanunni & Pretorius (2023), Table 1 (Alpha row 12).
    sa_table("PMC10670897", "Table 1", "padmanabhanunni_2023_covidptsd7", 322, FCP, alpha_row=12),
    # Han et al. (2025), Table 1: "j. label", M and SD in columns 1-2, lower triangle in 3-9
    # (a dash diagonal for Age, 1 for the rest).
    square("PMC11893583", "Table 1", "han_2025_phubbing7", 837, PHB, seq(1, 7), seq(3, 9), 0, NUMS(1, 7),
           label_rx=DOTNUM,
           moments=mom("mean", "Table 1", PHB, seq(1, 7), 1, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 1", PHB, seq(1, 7), 2, 0, "SD", label_rx=DOTNUM)),
    # Pretorius & Padmanabhanunni (2022), Table 1 (Alpha row 10; the Omega row 11 is not read).
    sa_table("PMC9690525", "Table 1", "pretorius_2022_coherence7", 355, SOC, alpha_row=10),
    # Jones & Drummond (2022), Table 5: lower triangle with a 1 diagonal; the column header
    # prints "AQOL" and the row label "AqoL" (same letters, checked case-blind).
    # held by the coordinator (suspected sign slip in the AQoL row; held.csv):
    # square("PMC9429599", "Table 5", "jones_2022_clinqolchange7", 42, CLQ, seq(1, 7), seq(1, 7), 0, CLQ),
    # Schnell & Danbolt (2023), Table 6 (Study 5): an upper triangle with a "--" diagonal, no
    # row for Personal Growth (the rows below Community correlate the scales with
    # sociodemographic variables and are not read). Mean (Crisis of Meaning prints "M [Median]"),
    # SD and Cronbach's alpha ("a[LL, UL]") from Table 5, whose row labels end in footnote b.
    square("PMC10548553", "Table 6", "schnell_2023_maps7", 974, MAP, seq(1, 6) + [None], seq(1, 7), 0, MAP,
           diag_extra=("--",),
           moments=[dict(m, rx=r"^(-?[\d.]+)") for m in mom("mean", "Table 5", MAP, seq(1, 7), 1, 0, "Mean [Med]",
                                                             label_rx=FOOTB)]
           + mom("sd", "Table 5", MAP, seq(1, 7), 2, 0, "SD", label_rx=FOOTB)
           + [dict(m, rx=r"^([\d.]+)\[") for m in mom("rel", "Table 5", MAP, seq(1, 7), 7, 0,
                                                       "Cronbach’s alpha with 95% CI[LL, UL]a", label_rx=FOOTB)]),
    # Zulkiewicz et al. (2024), Table 2: "j. label", Mean and SD in columns 1-2, lower triangle
    # with a 1.000 diagonal in columns 3-9.
    square("PMC11564828", "Table 2", "zulkiewicz_2024_antiindustry7", 966, AIQ, seq(1, 7), seq(3, 9), 0, NUMS(1, 7),
           label_rx=DOTNUM,
           moments=mom("mean", "Table 2", AIQ, seq(1, 7), 1, 0, "Mean", label_rx=DOTNUM)
           + mom("sd", "Table 2", AIQ, seq(1, 7), 2, 0, "SD", label_rx=DOTNUM)),
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
        raise SystemExit("usage: python3 pmc_article_tables_av.py <out dir>")
    main(sys.argv[1])
