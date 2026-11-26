"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AW batch, 2026-11-19).

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
2026-11-18, resumed at agent AV's stopping point (queue line 273). Exposure to online
authority and non-authority sources of COVID-19 vaccine information, information
engagement, fear and hope about vaccination and perceived benefits and barriers (US adults);
boredom frequency, intensity, dislike and normalcy with mental well-being (Study 1, printed
below the diagonal; Study 2 above it is not read); neurocognitive ability, psychoticism,
perspective taking, theory of mind and hostile attribution bias (footnote letters dropped
from three labels); social identification, trust, well-being and distress during the Italian
lockdown ("M (SD)" cells); burnout, emotional intelligence, motivation, citizenship behaviors
and work misbehaviors of first-level, mid-level and top-level managers (three groups printed
in each cell as "a (b) [c]", read with `pick`); mental state inference, empathy and burnout
of Spanish healthcare professionals; age, gender, physical activity, mental toughness and
academic burnout of Hong Kong students (alpha row -> rel); autonomy support, sense of
coherence, growth mindset and demographics of Chinese undergraduates; parental
self-efficacy, promotive parenting and adolescents' externalizing (US parents, 1999-2000);
resting heart rate variability, trait anxiety and rumination facets (panel A, zero-order;
panel B, partial correlations, is not read); and person-level correlations of challenge
stressors, appraisals and thriving in a diary study (below the diagonal; day-level
correlations above it are not read). The N of each is from the caption, a table note or the
article text, as noted in matrices.csv.

Parsing: as pmc_article_tables_am.py to pmc_article_tables_av.py (whose build code this
file copies, adding only the `pick` option below). Each table is expanded into a grid (a cell with rowspan/colspan
fills every position it spans), so the `rows` and `cols` indices of a config are grid
positions. Cells are read as text. Significance stars are stripped; nothing else is
changed. Unicode minus (U+2212) and an en dash used as a minus are read as "-", and spaces
inside a cell are dropped ("− .371**" -> "-.371"). For each pair of variables the script
reads both cells (row i/column j and row j/column i): exactly one must hold a number and
the other must be empty or a dash, or both must hold the same number (a part marked
`lower_only` reads the lower side only: tam_2022_boredom5 and prem_2016_thriving7 print a
second sample above the diagonal). A matrix with no column for its last variable has that
column given as None (sariraei_2024_burnoutmgr8). A config's `pick` = (regex, i) reads
group i out of a cell that prints several groups; the regex must match the whole cell.

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the name of a label.
Printed column headers are checked too (`col_labels`). The comparison ignores everything
but letters and digits, so a footnote marker ("Anxiety *") does not count. Variable names
are the printed labels without footnote markers and without their "j." / "(j)" numbers.

Mean, SD and reliability cells are read from the cell a config names; the row label of
each moment is checked the same way as the matrix rows, and the column header is checked
too (`hdr`). They become mean/sd/rel rows, values as printed.

Diagonal cells (1, 1.00, 1.0, a dash, "--", "–-" or blank, or a printed alpha "(0.86)"
where a config's `diag_rx` allows it) are written as 1. Values are written in shortest round-trip form of the
published decimal (for example "0.40" -> "0.4", ".80" -> "0.8", "-0.00" -> "-0.0"), i.e.
unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_aw.py <out dir>
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
VXI = ["Non-Authority Source Exposure", "Authority Source Exposure", "Information Engagement",
       "Fear Connected to Vaccination", "Hope Connected to Vaccination", "Perceived Vaccination Benefits",
       "Perceived Vaccination Barriers"]
BOR = ["Boredom frequency", "Boredom intensity", "Boredom dislike", "Boredom normalcy", "Mental well‐being"]
HAB = ["SPM", "Psychoticism", "Perspective taking", "K-RMET", "AIHQ blame ambiguous", "AIHQ hostility ambiguous",
       "AIHQ aggression ambiguous"]
HAB_L = ["SPMa", "Psychoticism", "Perspective taking", "K-RMETb", "AIHQc blame ambiguous", "AIHQ hostility ambiguous",
         "AIHQ aggression ambiguous"]
ITL = ["Identification with Italians", "Identification with Europeans", "Identification with humankind",
       "Trust toward social and political actors", "Individual wellbeing", "Interdipendent Happiness", "Distress"]
MGR = ["Burnout", "EI", "Aut. Mot.", "Con. Mot.", "OCB-I", "OCB-O", "WMB-I", "WMB-O"]
# "−0.69*** (−0.68***) [−0.64***]": first-level managers, mid-level (in parentheses), top-level [in brackets]
TRIPLE = r"([−-]?\d*\.\d+)\**\s*\(([−-]?\d*\.\d+)\**\)\s*\[([−-]?\d*\.\d+)\**\]"
EMP = ["MenSta", "PerTak", "EmoCon", "PerDis", "EmoExh", "Dep", "PerAcc"]
ABO = ["Age", "Gender", "Physical activity", "Mental toughness", "Emotional exhaustion", "Cynicism",
       "Academic inefficacy"]
GMS = ["PAS", "TAS", "SOC", "GM", "Age", "Gender", "SES"]
GMS_L = ["PAS", "TAS", "SOC", "GM", "Age", "Gender a", "SES"]
PSE = ["PSE", "Promotive parenting", "Target adolescent externalizing", "Older adolescent externalizing",
       "Parents’ sex", "One vs. two parents reporting", "Marital status"]
HRV = ["vmHRV", "Anxiety", "Rumination", "Depressive", "Brooding", "Reflection"]
THR = ["Time pressure", "Learning demands", "Positive Meaning", "Challenge appraisal", "Hindrance appraisal",
       "Learning", "Vitality"]


def nolab(stat, label, names, rows, col, hdr_row, hdr, labels, label_col=0, label_rx=None):
    return mom(stat, label, names, rows, col, hdr_row, hdr, labels=labels, label_col=label_col, label_rx=label_rx)


def sub(xs, idx):
    return [xs[i] for i in idx]


CONFIGS = [
    # Xu & Lin (2024), Table 1: "j. label" rows 1-7, lower triangle with a blank diagonal in
    # columns 1-7 (column 7 is empty); M and SD rows 8-9.
    square("PMC11511211", "Table 1", "xu_2024_vaxinfo7", 630, VXI, seq(1, 7), seq(1, 7), 0, NUMS(1, 7),
           label_rx=DOTNUM,
           moments=row_mom("mean", "Table 1", VXI, 8, seq(1, 7), "M", 0, NUMS(1, 7))
           + row_mom("sd", "Table 1", VXI, 9, seq(1, 7), "SD", 0, NUMS(1, 7))),
    # Tam et al. (2022), TABLE 1: Study 1 below the diagonal (read, lower_only), Study 2 above it
    # (not read: held); Study 1's M and SD in rows 6-7 (Study 2's in the M/SD columns, not read).
    square("PMC9537911", "TABLE 1", "tam_2022_boredom5", 2495, BOR, seq(1, 5), seq(1, 5), 0, NUMS(1, 5),
           label_rx=DOTNUM, part_kw=dict(lower_only=True),
           moments=row_mom("mean", "TABLE 1", BOR, 6, seq(1, 5), "M", 0, NUMS(1, 5))
           + row_mom("sd", "TABLE 1", BOR, 7, seq(1, 5), "SD", 0, NUMS(1, 5))),
    # Koo et al. (2022), Table 1: "j. label" (footnote letters a-c on three labels), Mean and SD
    # in columns 1-2, lower triangle with a dash diagonal in columns 3-9.
    square("PMC9471867", "Table 1", "koo_2022_hostileattrib7", 184, HAB, seq(1, 7), seq(3, 9), 0, NUMS(1, 7),
           labels=HAB_L, label_rx=DOTNUM,
           moments=nolab("mean", "Table 1", HAB, seq(1, 7), 1, 0, "Mean", HAB_L, label_rx=DOTNUM)
           + nolab("sd", "Table 1", HAB, seq(1, 7), 2, 0, "SD", HAB_L, label_rx=DOTNUM)),
    # Paolini et al. (2020), Table 1: "j. label", "M (SD)" in column 1, lower triangle with a
    # 1.00 diagonal in columns 2-8.
    square("PMC7587159", "Table 1", "paolini_2020_lockdowntrust7", 690, ITL, seq(1, 7), seq(2, 8), 0, NUMS(1, 7),
           label_rx=DOTNUM,
           moments=msd("Table 1", ITL, seq(1, 7), 1, 0, "Means (SD)", MSD_M, MSD_SD, label_rx=DOTNUM)),
    # Sariraei et al. (2024), Table 3: three groups in each cell, "first (mid) [top]"; rows 1-8,
    # columns 1-7 (no column for WMB-O), dash diagonal.
    *[square("PMC11069314", "Table 3", "sariraei_2024_burnoutmgr8", n, MGR, seq(1, 8), seq(1, 7) + [None], 0,
             NUMS(1, 7), pick=(TRIPLE, gi), group=g)
      for g, n, gi in (("First-level managers", 513, 1), ("Mid-level managers", 220, 2),
                       ("Top-level managers", 107, 3))],
    # Delgado et al. (2021), Table 2: abbreviated labels, Mean and SD in columns 1-2, lower
    # triangle with a dash diagonal in columns 3-9.
    square("PMC7913277", "Table 2", "delgado_2021_empathyburnout7", 184, EMP, seq(1, 7), seq(3, 9), 0, EMP,
           moments=mom("mean", "Table 2", EMP, seq(1, 7), 1, 0, "Mean")
           + mom("sd", "Table 2", EMP, seq(1, 7), 2, 0, "SD")),
    # Cheung & Li (2019), Table 1: "j. label", lower triangle with a dash diagonal in columns
    # 1-7; alpha, M and SD rows 8-10 (no alpha for age and gender, no M or SD for gender).
    square("PMC6603857", "Table 1", "cheung_2019_burnoutmt7", 1209, ABO, seq(1, 7), seq(1, 7), 0, NUMS(1, 7),
           label_rx=DOTNUM,
           moments=row_mom("rel", "Table 1", ABO[2:], 8, seq(3, 7), "α", 0, NUMS(3, 7))
           + row_mom("mean", "Table 1", sub(ABO, [0, 2, 3, 4, 5, 6]), 9, [1, 3, 4, 5, 6, 7], "M", 0,
                     sub(NUMS(1, 7), [0, 2, 3, 4, 5, 6]))
           + row_mom("sd", "Table 1", sub(ABO, [0, 2, 3, 4, 5, 6]), 10, [1, 3, 4, 5, 6, 7], "SD", 0,
                     sub(NUMS(1, 7), [0, 2, 3, 4, 5, 6]))),
    # Ma et al. (2020), Table 1: number in column 0, label in column 1, M and SD in columns 2-3,
    # lower triangle with a dash diagonal in columns 7-13 (no M or SD for gender).
    square("PMC7494807", "Table 1", "ma_2020_autonomygm7", 1030, GMS, seq(1, 7), seq(7, 13), 0, NUMS(1, 7),
           labels=GMS_L, label_col=1,
           moments=nolab("mean", "Table 1", sub(GMS, [0, 1, 2, 3, 4, 6]), [1, 2, 3, 4, 5, 7], 2, 0, "M",
                         sub(GMS_L, [0, 1, 2, 3, 4, 6]), label_col=1)
           + nolab("sd", "Table 1", sub(GMS, [0, 1, 2, 3, 4, 6]), [1, 2, 3, 4, 5, 7], 3, 0, "SD",
                   sub(GMS_L, [0, 1, 2, 3, 4, 6]), label_col=1)),
    # Glatz et al. (2016), Table 1: "j. label", lower triangle with a dash diagonal (blank for
    # the last variable) in columns 1-7, M and SD in columns 8-9 (none for the three dummies).
    square("PMC5344949", "Table 1", "glatz_2016_parentse7", 130, PSE, seq(1, 7), seq(1, 7), 0, NUMS(1, 7),
           label_rx=DOTNUM,
           moments=mom("mean", "Table 1", PSE[:4], seq(1, 4), 8, 0, "M", label_rx=DOTNUM)
           + mom("sd", "Table 1", PSE[:4], seq(1, 4), 9, 0, "SD", label_rx=DOTNUM)),
    # Williams et al. (2017), Table 2: panel (A), zero-order correlations, rows 2-7 and columns
    # 1-6 (headers in row 1), dash diagonal; panel (B), partial correlations, is not read.
    square("PMC5671536", "Table 2", "williams_2017_hrvrumination6", 203, HRV, seq(2, 7), seq(1, 6), 1, NUMS(1, 6),
           label_rx=DOTNUM),
    # Prem et al. (2016), Table 1: person-level correlations below the diagonal (read,
    # lower_only), day-level correlations above it (not read: held); person-level M and SD in
    # columns 1-2 (day-level M, SD, alpha, omega and 1-ICC in columns 3-7 not read).
    square("PMC5244684", "Table 1", "prem_2016_thriving7", 124, THR, seq(1, 7), seq(8, 14), 0, NUMS(1, 7),
           label_rx=DOTNUM, part_kw=dict(lower_only=True),
           moments=mom("mean", "Table 1", THR, seq(1, 7), 1, 0, "M a", label_rx=DOTNUM)
           + mom("sd", "Table 1", THR, seq(1, 7), 2, 0, "SD a", label_rx=DOTNUM)),
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
        raise SystemExit("usage: python3 pmc_article_tables_aw.py <out dir>")
    main(sys.argv[1])
