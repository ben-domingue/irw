"""Covariance family (irw_cov, source = "cov"): correlation tables printed in
CC BY open-access articles, read from the article's JATS XML in PubMed Central
(pilot of source "article tables", #3582).

Source: Europe PMC full-text XML,
https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML.
Each article's <license> is read and must be CC BY (creativecommons.org/licenses/by/)
or CC0; the script stops otherwise. Every DOI was checked on Crossref (2026-11-17).

Tables built (CONFIGS below): one correlation table per article, among observed
scale or item scores, with N stated in the table note or the text.

Parsing: cells are read as text. Significance stars (*, **, ***) are stripped
from each correlation; nothing else is changed. Unicode minus (U+2212) and en
dash used as a minus are read as "-". Leading-dot decimals are allowed. Diagonal
cells (1, a dash, or blank) are written as 1. For tables printed as a full
square, the script checks the upper triangle equals the lower exactly (as text)
and writes the lower. Values are written in shortest round-trip form of the
published decimal (e.g. "0.42"), i.e. unchanged. Mean and SD columns, where the
table has them, become mean/sd rows. A reliability the article prints for a
variable (Cronbach's alpha or McDonald's omega, same sample) becomes a rel row,
value as printed: from another table of the article (`rel`, matched on the row
label given for each variable) or from the article text (`rel_text`, one regex
per variable with one capture group, which must match exactly one distinct
value). The coefficient is named in matrices.csv notes.

Modification (2026-11-18): rel rows added (#3607 standard) for
almutairi_2026, cammarata_2026, ozdemir_2026 and morillosarto_2025; other rows
unchanged.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md; stars stripped; values unchanged.

Usage: python3 data/covariance/pmc_article_tables.py <out dir>
(set IRW_PMC_XML_DIR=<dir of PMCxxxx.xml> to read saved copies instead of Europe PMC)
"""
import csv
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# (pmcid, table label, irw table, N, layout, first data row, label col,
#  first matrix col, mean col, sd col; optional k = number of variables when
#  mean/SD are printed as rows below the matrix, at table rows mean_row/sd_row)
#  layout: "lower" (lower triangle printed) or "full" (full square printed)
#  optional rel = dict(label=<table label>, col=<cell index>, rows={variable: <first
#  cell of its row in that table>}) and rel_text = {variable: regex}: see header.
CONFIGS = [
    dict(pmcid="PMC13624096", label="Table 3", table="cammarata_2026_gibs6", n=263,
         layout="lower", row0=1, labcol=0, col0=1, mean=None, sd=None,
         rel_text={  # Study 2 Measures: "Cronbach's α was ..." after each scale's description
             "RWA": r"Right Wing Authoritarianism \(RWA\):[^α]*Cronbach’s α was (\d?\.\d+)",
             "MHS-G": r"Modern Homonegativity Scale - Gay men \(MHS-G[^α]*Cronbach’s α was (\d?\.\d+)",
             "ATG-S": r"\(ATG-S; Herek, 1994\)[^α]*Cronbach’s α was (\d?\.\d+)",
             "GCBS": r"Generic Conspiracist Beliefs Scale \(GCBS\):[^α]*Cronbach’s α was (\d?\.\d+)"}),
    dict(pmcid="PMC13677849", label="Table 4", table="almutairi_2026_tpbsocialmedia5", n=258,
         layout="lower", row0=1, labcol=0, col0=1, mean=None, sd=None,
         rel=dict(label="Table 2", col=4, rows={  # Cronbach's alpha column
             "Attitudes": "Attitudes (6 items)",
             "Subjective Norms": "Subjective Norms (4 items)",
             "Perceived Behavioural Control": "Perceived Behavioural Control (4 items)",
             "Behavioural Intention": "Behavioural Intention (3 items)",
             "BSMAS Total": "BSMAS Total Score (6 items)"})),
    dict(pmcid="PMC13662749", label="TABLE 2", table="ozdemir_2026_mentormindsets8", n=316,
         layout="lower", row0=1, labcol=0, col0=3, mean=1, sd=2,
         rel=dict(label="TABLE 4", col=2, rows={"Enforcer": "Enforcer", "Protector": "Protector"})),  # α column
    dict(pmcid="PMC13665093", label="Table 8", table="green_2026_caregiverwellness9", n=225,
         layout="full", row0=1, labcol=0, col0=1, mean=None, sd=None),
    dict(pmcid="PMC12293092", label="Table 1", table="morillosarto_2025_adolescentdistress5", n=908,
         layout="lower", row0=1, labcol=0, col0=1, mean=None, sd=None, k=5, mean_row=6, sd_row=7,
         rel_text={  # McDonald's omega, printed "ɷ" in 2.2 Measurements
             "Psychological distress": r"Fourteen items \(ɷ = (\d?\.\d+)\)",
             "Intolerance of uncertainty": r"Twelve items \(ɷ = (\d?\.\d+)\)",
             "Social media use disorder": r"during the past year \(ɷ = (\d?\.\d+);",
             "Family functioning": r"by five items \(ɷ = (\d?\.\d+)\)",
             "Community social disorder": r"three-question scale \(ɷ = (\d?\.\d+)\)"}),
    dict(pmcid="PMC12325398", label="Table 1", table="chen_2025_aistories3", n=120,
         layout="lower", row0=1, labcol=0, col0=3, mean=1, sd=2),
]

DIAG = {"1", "-", "–", "—", "", "1.00", "1.0"}


def txt(e):
    return re.sub(r"\s+", " ", "".join(e.itertext())).strip()


def get(pmcid):
    local = os.environ.get("IRW_PMC_XML_DIR")
    if local:
        return (Path(local) / f"{pmcid}.xml").read_bytes()
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def num(cell, where):
    s = cell.replace(" ", "").replace("−", "-").replace("–", "-")
    s = re.sub(r"\*+$", "", s)
    if not re.fullmatch(r"-?(\d+)?\.\d+|-?\d+", s):
        raise SystemExit(f"{where}: cannot read {cell!r}")
    return repr(float(s)), s


def varname(lab):
    return re.sub(r"^\d+\.?\s+", "", lab).strip()


def build(cfg, root):
    lic = root.find(".//license")
    href = (lic.get("{http://www.w3.org/1999/xlink}href") or "") if lic is not None else ""
    ltxt = txt(lic) if lic is not None else ""
    if not (re.search(r"creativecommons\.org/(licenses/by/|publicdomain/zero)", href + ltxt)
            or re.search(r"Creative Commons Attribution( \(CC BY\))? (L|l)icen[cs]e", ltxt)):
        raise SystemExit(f"{cfg['pmcid']}: licence not CC BY / CC0: {href} {ltxt[:120]}")
    if re.search(r"NonCommercial|NoDeriv|by-nc|by-nd|by-sa|ShareAlike", href + ltxt):
        raise SystemExit(f"{cfg['pmcid']}: restricted licence {href} {ltxt[:120]}")
    tw = next(t for t in root.iter("table-wrap")
              if t.find("label") is not None and txt(t.find("label")) == cfg["label"])
    rows = [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    k = cfg.get("k") or len(rows) - cfg["row0"]
    body = rows[cfg["row0"]:cfg["row0"] + k]
    names = [varname(r[cfg["labcol"]]) for r in body]
    where = f"{cfg['pmcid']} {cfg['label']}"
    out, check = [], []
    for i in range(k):
        r = body[i]
        mat = r[cfg["col0"]:cfg["col0"] + k]
        if len(mat) != k:
            raise SystemExit(f"{where}: row {i} has {len(mat)} matrix cells, want {k}")
        if mat[i].strip() not in DIAG:
            raise SystemExit(f"{where}: diagonal {i} is {mat[i]!r}")
        for j in range(i + 1, k):
            up = mat[j].strip()
            if cfg["layout"] == "lower" and up != "":
                raise SystemExit(f"{where}: upper cell ({i},{j}) {up!r}")
            if cfg["layout"] == "full":
                lo = body[j][cfg["col0"] + i].strip()
                if num(up, where)[0] != num(lo, where)[0]:
                    raise SystemExit(f"{where}: asymmetric ({i},{j}) {up!r} vs {lo!r}")
        for j in range(i):
            v, raw = num(mat[j], f"{where} ({i},{j})")
            if abs(float(v)) >= 1:
                raise SystemExit(f"{where}: |r| >= 1 at ({i},{j})")
            out.append({"stat": "cor", "var1": names[i], "var2": names[j], "value": v, "n": cfg["n"]})
            check.append((names[i], names[j], mat[j]))
        out.append({"stat": "cor", "var1": names[i], "var2": names[i], "value": "1", "n": cfg["n"]})
    for stat in ("mean", "sd"):
        if cfg[stat] is not None:
            for i in range(k):
                out.append({"stat": stat, "var1": names[i], "var2": "",
                            "value": num(body[i][cfg[stat]], where)[0], "n": cfg["n"]})
        if cfg.get(stat + "_row") is not None:
            r = rows[cfg[stat + "_row"]]
            if not r[0].strip().lower().startswith(stat[0]):
                raise SystemExit(f"{where}: row {cfg[stat + '_row']} is {r[0]!r}, not {stat}")
            for i in range(k):
                out.append({"stat": stat, "var1": names[i], "var2": "",
                            "value": num(r[cfg["col0"] + i], where)[0], "n": cfg["n"]})
    if cfg.get("rel"):
        rt = next(t for t in root.iter("table-wrap")
                  if t.find("label") is not None and txt(t.find("label")) == cfg["rel"]["label"])
        rrows = [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in rt.iter("tr")]
        for nm, lab in cfg["rel"]["rows"].items():
            if nm not in names:
                raise SystemExit(f"{where}: rel variable {nm!r} not in the matrix")
            hit = [r for r in rrows if r and r[0] == lab]
            if len(hit) != 1:
                raise SystemExit(f"{where}: reliability row {lab!r} found {len(hit)} times")
            v = num(hit[0][cfg["rel"]["col"]], f"{where} rel {nm}")[0]
            if not 0 < float(v) <= 1:
                raise SystemExit(f"{where}: reliability {v} out of range for {nm}")
            out.append({"stat": "rel", "var1": nm, "var2": "", "value": v, "n": cfg["n"]})
    if cfg.get("rel_text"):
        text = txt(root.find(".//body"))
        for nm, pat in cfg["rel_text"].items():
            if nm not in names:
                raise SystemExit(f"{where}: rel_text variable {nm!r} not in the matrix")
            hits = set(re.findall(pat, text))
            if len(hits) != 1:
                raise SystemExit(f"{where}: reliability for {nm!r} matched {hits}")
            v = num(hits.pop(), where)[0]
            if not 0 < float(v) <= 1:
                raise SystemExit(f"{where}: reliability {v} out of range for {nm}")
            out.append({"stat": "rel", "var1": nm, "var2": "", "value": v, "n": cfg["n"]})
    return out, check, names


def main(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for cfg in CONFIGS:
        root = ET.fromstring(get(cfg["pmcid"]))
        rows, check, names = build(cfg, root)
        with open(outdir / f"{cfg['table']}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n"])
            w.writeheader()
            w.writerows(rows)
        with open(outdir / f"{cfg['table']}.check.tsv", "w", encoding="utf-8") as f:
            for a, b, raw in check:
                f.write(f"{a}\t{b}\t{raw}\n")
        print(f"wrote {cfg['table']}.csv: {len(names)} variables, N = {cfg['n']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 pmc_article_tables.py <out dir>")
    main(sys.argv[1])
