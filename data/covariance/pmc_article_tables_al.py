"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(source "article tables", #3582; agent AL batch, 2026-11-18).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/
or the words "Creative Commons Attribution (CC BY)" / "Creative Commons Attribution
License") or CC0; the script stops otherwise. An article whose own metadata
(<article-meta>) carries a retraction link (<related-article
related-article-type="retraction-forward"> or "retracted-article") is refused. Links of
that kind inside the reference list mark a retracted *cited* paper, not this article,
so they are not read.

Tables built (CONFIGS below): eleven tables (thirteen matrices) from eleven articles,
from the scale-level pass over the AC candidate list of 2026-11-18 (resumed at agent
AK's stopping point). Three are item-level matrices of one scale (18 remote-working
disadvantage items, pilot study; the Arabic WEMWBS, Spearman; the OHIP-14 among pregnant
women with a self-rated oral-health item, Spearman); eight are scale-level matrices
(shared reality, three studies as groups; job characteristics and burnout of nurses at
two waves; generative-AI job crafting; self-care activities during the COVID-19
lockdown; PE teachers' controlling behaviour and adolescents' motivation and activity;
post-traumatic growth after stem-cell transplantation; children's magnitude judgement
and maths at two time points; political stress and protective factors of Hong Kong
adolescents). The N of each is from the caption, a table note or the article text, as
noted in matrices.csv.

Parsing: as pmc_article_tables_ak.py. Each table is expanded into a grid (a cell with
rowspan/colspan fills every position it spans), so the `rows` and `cols` indices of a
config are grid positions. Cells are read as text. Significance stars are stripped;
nothing else is changed. Unicode minus (U+2212) and an en dash used as a minus are read
as "-", and spaces inside a cell are dropped ("− 0.06" -> "-0.06"). For each pair of
variables the script reads both cells (row i/column j and row j/column i): exactly one
must hold a number and the other must be empty or a dash, or both must hold the same
number. Where the other triangle holds something else (Cronbach's alphas of dimension
pairs in yang_2022_ohip15), only the lower triangle is read (`lower_only`).

New here: `diag_rx`, a regex a diagonal cell may match instead of being 1 or a dash
(liu_2026_aijobcrafting15 prints Cronbach's alphas in parentheses on the diagonal; they
are written as `rel` rows by `diag_mom`, and the diagonal as 1).

Printed row labels are checked against the expected labels of each part (`labels`,
or the variable names), after an optional `label_rx` that keeps the code or name of a
label. Printed column headers are checked too (`col_labels`), except in
chew_2019_magnitude16, whose header row is printed one column to the right of the
values (the row labels and the 1 diagonal fix the positions there). Variable names are
the source's item or scale codes (DISADV1, MH1, HC, ...) or scale names as printed
(Epistemic trust, Job autonomy, ...); items printed by number only are written item1,
item2, ..., never with item wording.

Mean, SD and reliability (Cronbach's alpha, `rel`) cells are read from the cell a
config names; the row label of each moment is checked the same way as the matrix rows,
and the column header is checked too (`hdr`). "M (SD)" cells are split by a regex
(`rx`). They become mean/sd/rel rows, values as printed.

Diagonal cells (1, 1.00, 1.000, a dash or blank) are written as 1. Values are written
in shortest round-trip form of the published decimal (for example "0.40" -> "0.4",
".80" -> "0.8", "-.00" -> "-0.0"), i.e. unchanged.

`n` is the matrix N, written on every row.

Usage: python3 data/covariance/pmc_article_tables_al.py <out dir>
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


DASHNUM = r"^\d+ – (.+)$"       # "1 – SR-T" -> "SR-T"
DOTNUM = r"^\d+\.\s*(.+)$"      # "1. Negative conditional regard" -> "Negative conditional regard"
PAREN = r"^\(([\d.]+)\)$"        # "(0.83)" -> "0.83"
SRT1 = ["SR-T", "Epistemic trust", "Relational motivation", "Outgroup attitude", "IOS", "Social curiosity",
        "Tolerance of ambiguity", "Liking", "SSES (performance)", "SSES (social)", "CM (topic)", "CM (person)",
        "STADI arousal", "STADI anxiety", "STADI euthymia", "METI", "PQ+", "NQ-"]
SRT2 = ["SR-T", "Epistemic trust", "Relational motivation", "Message tuning", "Recall tuning", "NTS self-esteem",
        "NTS belonging", "NTS control", "NTS meaningful existence", "Shared identity", "NFCC PSP", "NFCC PNS",
        "NFCC undecidedness", "IOS"]
SRT3 = ["SR-T", "Recall tuning", "Epistemic trust", "Relational motivation", "Perceived similarity", "IOS",
        "SR need"]
DISADV = [f"DISADV{i}" for i in seq(1, 18)]
PIS_LAB = ["Gendera", "Age", "JD", "JC", "SS", "EE", "DP", "PA", "JD", "JC", "SS", "EE", "DP", "PA"]
PIS = ["Gender", "Age"] + [f"{v}_T{t}" for t in (1, 2) for v in ("JD", "JC", "SS", "EE", "DP", "PA")]
PIS_ROWS = [2, 3] + seq(5, 10) + seq(12, 17)
LIU = ["Gender", "Age", "Industry", "Position", "Education Level", "Tenure with supervisor",
       "AI approach job crafting", "AI avoidance job crafting", "Job autonomy", "Work meaningfulness",
       "Work alienation", "Life satisfaction", "Career satisfaction", "Task performance", "Creative performance"]
SASS = ["Age", "Sex", "Edu", "Inc", "HC", "NPA", "SLP", "IICS", "SASS", "SA", "PRO", "ATM", "EM", "PG", "PL",
        "PWBS", "PSS"]
KOKA = ["Negative conditional regard", "Intimidation", "Controlling use of praise", "Autonomy need frustration",
        "Competence need frustration", "Relatedness need frustration", "Intrinsic motivation in PE",
        "Identified regulation in PE", "Introjected regulation in PE", "External regulation in PE",
        "Intrinsic motivation in LT", "Identified regulation in LT", "Introjected regulation in LT",
        "External regulation in LT", "Objective MVPA (min/day)", "Past LT physical activity"]
PTG = ["PTGI total", "Male", "Age", "Employed post-transplant", "University educated", "Years since transplant",
       "Cancer", "Conditioning", "Chronic GVHD Activity Assessment", "Count GVHD", "GVHD Y/N",
       "Comorbidities Y/N", "Psychologist", "Psychiatrist", "Antidepressants", "Antianxiety",
       "Complementary therapy", "DASS Total", "Total FACT"]
CHEW_LAB = ["NSM correct", "SM correct", "NSM RT", "SM RT", "NSM correct", "SM correct", "NSM RT", "SM RT",
            "VSWM", "NN", "RCPM", "Basic RT", "SDA correct", "Transcoding", "SDA correct", "Transcoding"]
CHEW = ["NSM_correct_T1", "SM_correct_T1", "NSM_RT_T1", "SM_RT_T1", "NSM_correct_T2", "SM_correct_T2",
        "NSM_RT_T2", "SM_RT_T2", "VSWM", "NN", "RCPM", "Basic_RT", "SDA_correct_T1", "Transcoding_T1",
        "SDA_correct_T2", "Transcoding_T2"]
MH = [f"MH{i}" for i in seq(1, 14)]
OHIP = items(14) + ["overall_oral_health"]
HK_LAB = ["Gen", "Age", "Rel", "Edu", "Fat’s Edu", "Mot’s Edu", "MH (DV)", "SPLE (IV)", "ML (MV)", "RE (MV)",
          "SS (MV)", "ASC (MV)", "YEC (MV)", "CEC (MV)"]
HK = ["Gen", "Age", "Rel", "Edu", "Fat_Edu", "Mot_Edu", "MH", "SPLE", "ML", "RE", "SS", "ASC", "YEC", "CEC"]

CONFIGS = [
    # Schmalbach et al. (2019), Tables 5, 9 and 10: correlation matrices of Studies 1-3
    # (one group each), upper triangles with a dash diagonal; row labels "1 – SR-T" ..,
    # column headers 1..k.
    square("PMC6478012", "Table 5", "schmalbach_2019_sharedreality18", 218, SRT1, seq(1, 18), seq(1, 18), 0,
           NUMS(1, 18), label_rx=DASHNUM, group="study1"),
    square("PMC6478012", "Table 9", "schmalbach_2019_sharedreality18", 112, SRT2, seq(1, 14), seq(1, 14), 0,
           NUMS(1, 14), label_rx=DASHNUM, group="study2"),
    square("PMC6478012", "Table 10", "schmalbach_2019_sharedreality18", 192, SRT3, seq(1, 7), seq(1, 7), 0,
           NUMS(1, 7), label_rx=DASHNUM, group="study3"),
    # Ingusci et al. (2022), Table 3: pilot-study disadvantage items DISADV1-DISADV18,
    # lower triangle with a dash diagonal. (Table 2, the benefit items, is held: three
    # off-diagonal cells are 1.000.)
    square("PMC9052188", "Table 3", "ingusci_2023_remotedisadv18", 304, DISADV, seq(1, 18), seq(1, 18), 0,
           DISADV),
    # Pisanti et al. (2016), Table 1: gender, age and six scales at Time 1 and Time 2;
    # section rows (BACKGROUND, TIME 1, TIME 2) between the blocks; lower triangle with a
    # dash diagonal, no column for the last variable; M, SD and alpha in columns 1-3. The
    # gender label carries the footnote marker "a" (coding note), printed "Gendera".
    square("PMC4960268", "Table 1", "pisanti_2016_jobburnout14", 217, PIS, PIS_ROWS, seq(4, 16) + [None], 0,
           NUMS(1, 13), labels=PIS_LAB, label_rx=r"^\(\d+\)\s*(.+)$",
           moments=mom("mean", "Table 1", PIS[1:], PIS_ROWS[1:], 1, 0, "M", labels=PIS_LAB[1:],
                       label_rx=r"^\(\d+\)\s*(.+)$")
           + mom("sd", "Table 1", PIS[1:], PIS_ROWS[1:], 2, 0, "SD", labels=PIS_LAB[1:],
                 label_rx=r"^\(\d+\)\s*(.+)$")
           + mom("rel", "Table 1", PIS[2:], PIS_ROWS[2:], 3, 0, "α", labels=PIS_LAB[2:],
                 label_rx=r"^\(\d+\)\s*(.+)$")),
    # Liu et al. (2026), Table 1: lower triangle, blank diagonal for variables 1-6 and
    # Cronbach's alpha in parentheses on the diagonal for 7-15 (rel rows); Mean and SD
    # rows printed for variables 6-15 only.
    square("PMC13053293", "Table 1", "liu_2026_aijobcrafting15", 287, LIU, seq(1, 15), seq(1, 15), 0,
           NUMS(1, 15), label_rx=DOTNUM, diag_rx=PAREN,
           moments=diag_mom("Table 1", LIU[6:], seq(7, 15), seq(7, 15), 0, NUMS(7, 15), PAREN, label_rx=DOTNUM)
           + row_mom("mean", "Table 1", LIU[5:], 16, seq(6, 15), "Mean", 0, NUMS(6, 15))
           + row_mom("sd", "Table 1", LIU[5:], 17, seq(6, 15), "SD", 0, NUMS(6, 15))),
    # Martínez et al. (2021), Table 3: upper triangle with a dash diagonal, columns headed
    # by the 17 abbreviations; no row for the last variable (PSS); the row label of NPA is
    # printed "HPA".
    square("PMC7776298", "Table 3", "martinez_2021_sass17", 261, SASS, seq(1, 16) + [None], seq(1, 17), 0,
           SASS, labels=SASS[:5] + ["HPA"] + SASS[6:]),
    # Koka et al. (2019), Table 1: lower triangle with a dash diagonal under a header row
    # 1..16; Mean, SD and Cronbach alpha rows (no alpha for variables 15-16).
    square("PMC6695765", "Table 1", "koka_2019_pecontrol16", 159, KOKA, seq(2, 17), seq(1, 16), 1, NUMS(1, 16),
           label_rx=DOTNUM,
           moments=row_mom("mean", "Table 1", KOKA, 18, seq(1, 16), "Mean", 1, NUMS(1, 16))
           + row_mom("sd", "Table 1", KOKA, 19, seq(1, 16), "SD", 1, NUMS(1, 16))
           + row_mom("rel", "Table 1", KOKA[:14], 20, seq(1, 14), "Cronbach alpha (α)", 1, NUMS(1, 14))),
    # McErlean et al. (2023), Table 3: lower triangle with a dash diagonal, no column for
    # the last variable.
    square("PMC10433676", "Table 3", "mcerlean_2023_ptg19", 441, PTG, seq(1, 19), seq(1, 18) + [None], 0,
           NUMS(1, 18), label_rx=DOTNUM),
    # Chew et al. (2019), Table 2: lower triangle with a 1 diagonal; labels in column 1,
    # values in columns 2-17; the header row (numbers 1-16) is printed one column to the
    # right of the values, so it is not checked (col_labels None).
    square("PMC6411817", "Table 2", "chew_2019_magnitude16", 109, CHEW, seq(2, 17), seq(2, 17), 1, None,
           labels=CHEW_LAB, label_col=1, label_rx=DOTNUM),
    # Zayed et al. (2023), Table 2: Spearman matrix of the 14 WEMWBS items MH1-MH14,
    # lower triangle with a 1.00 diagonal.
    square("PMC10657025", "Table 2", "zayed_2023_wemwbs14", 690, MH, seq(1, 14), seq(1, 14), 0, NUMS(1, 14)),
    # Yang et al. (2022), Table 3: Spearman matrix of the 14 OHIP-14 items (rows and
    # columns numbered 1-14) and a last row "Overall oral health" (self-rated oral health, no column);
    # blank diagonal; the upper triangle holds the Cronbach alphas of the seven OHIP-14
    # dimensions in parentheses (not read: `lower_only`).
    square("PMC8951846", "Table 3", "yang_2022_ohip15", 291, OHIP, seq(1, 15), seq(1, 14) + [None], 0,
           NUMS(1, 14), labels=NUMS(1, 14) + ["Overall oral health"], part_kw=dict(lower_only=True)),
    # Chang et al. (2021), Table 2: number in column 0, abbreviation in column 1, lower
    # triangle in columns 2-14 (headers "1." .. "13."), blank diagonal, no column for the
    # last variable; "M (SD)" in column 15, printed for Age and variables 7-14 only.
    square("PMC8468064", "Table 2", "chang_2021_hkpolstress14", 1330, HK, seq(1, 14), seq(2, 14) + [None], 0,
           [f"{i}." for i in seq(1, 13)], labels=HK_LAB, label_col=1,
           moments=msd("Table 2", [HK[1]] + HK[6:], [2] + seq(7, 14), 15, 0, "M (SD)", MSD_M, MSD_SD,
                       labels=[HK_LAB[1]] + HK_LAB[6:], label_col=1)),
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
        raise SystemExit("usage: python3 pmc_article_tables_al.py <out dir>")
    main(sys.argv[1])
