"""Covariance family (irw_cov, source = "cov"): Paquin & Keating (2016), identity in
the reasoned action framework, study-level correlation matrices.

HELD (2026-11-17): not in irw_cov. Ben is holding this table pending a ruling on
CC BY supplements to paywalled articles (data/covariance/held.csv).

Source: figshare (Taylor & Francis) item 2306437, https://doi.org/10.6084/m9.figshare.2306437,
supplementary material to Paquin, R. S., & Keating, D. M. (2016/2017). Fitting identity
in the reasoned action framework: A meta-analysis and model comparison. The Journal of
Social Psychology, 157(1), 47-63. https://doi.org/10.1080/00224545.2016.1152217
Licence of the figshare item: CC BY 4.0.

File vsoc_a_1152217_sm9566.docx ("Online Supplement B"), Table B1: one block per study
with author(s), N, and a lower-triangle "effect size matrix" of INT, ATT, NORM, PBC, ID,
BEH, followed by M and SD rows. Per the table note:
- an N written "177[156]" gives the listwise n for coefficients involving behaviour in
  brackets; those cells carry the bracketed n, all others the main N (pairwise n, as
  the README allows);
- the diagonal holds Cronbach's alpha in parentheses; it is not part of the layout and
  the diagonal is written as 1;
- M and SD were rescaled by the meta-analysts to a 1-7 metric, so they are not used.
A variable whose correlations are all "—" was not measured and is dropped from that
study. A study with any other missing cell, an |r| >= 1, or footnote c (a sign the
meta-analysts judged a typo, so possibly altered) is not built and is printed as held.
Values are written as printed (".56" -> 0.56 is the same number; the text is parsed,
not rounded).

Usage: python3 data/covariance/figshare_paquin2016_identity.py <out dir>
"""
import csv
import html
import io
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = "https://ndownloader.figshare.com/files/3944089"
TABLE = "paquin_2016_identity6"
VARS = ["INT", "ATT", "NORM", "PBC", "ID", "BEH"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def rows_of(blob):
    x = zipfile.ZipFile(io.BytesIO(blob)).read("word/document.xml").decode()
    t = re.findall(r"<w:tbl>.*?</w:tbl>", x, flags=re.S)[0]
    for r in re.findall(r"<w:tr[ >].*?</w:tr>", t, flags=re.S):
        yield [html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", c))).strip()
               for c in re.findall(r"<w:tc>.*?</w:tc>", r, flags=re.S)]


def num(s):
    s = s.replace("−", "-").replace("–", "-")
    if not re.fullmatch(r"-?\d*\.\d+|-?\d+", s):
        raise ValueError(s)
    return repr(float(s))


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    studies, cur = [], None
    for r in rows_of(get(URL)):
        if len(r) != 13:
            continue
        if r[0]:
            cur = {"author": r[0], "N": r[1], "rows": {}}
            studies.append(cur)
        if cur is not None and re.fullmatch(r"[1-6]\.", r[6]):
            cur["rows"][int(r[6][0])] = r[7:13]
    long, held, seen = [], [], {}
    for s in studies:
        m = re.fullmatch(r"([\d,]+)(?:\[([\d,]+)\])?", s["N"])
        n_all = int(m.group(1).replace(",", ""))
        n_beh = int(m.group(2).replace(",", "")) if m.group(2) else n_all
        foot = re.search(r"\)\s*([a-e](?:,\s*[a-e])*)\s*$", s["author"])
        foot = set(re.findall(r"[a-e]", foot.group(1))) if foot else set()
        name = re.sub(r"\)\s*[a-e](?:,\s*[a-e])*\s*$", ")", s["author"])
        if sorted(s["rows"]) != [1, 2, 3, 4, 5, 6]:
            held.append((s["author"], "matrix rows incomplete"))
            continue
        cell = {}
        for i in range(1, 7):
            for j in range(1, i):
                cell[(i, j)] = s["rows"][i][j - 1]
        dash = lambda v: v in ("—", "-", "")
        measured = [k for k in range(1, 7)
                    if not all(dash(cell[(max(k, o), min(k, o))]) for o in range(1, 7) if o != k)]
        miss = [(i, j) for (i, j), v in cell.items() if i in measured and j in measured and dash(v)]
        if "c" in foot:
            held.append((s["author"], "footnote c: sign judged a typo by the meta-analysts"))
            continue
        if miss or len(measured) < 2:
            held.append((s["author"], f"missing cells {miss}"))
            continue
        vals = {k: num(cell[k]) for k in cell if k[0] in measured and k[1] in measured}
        if any(abs(float(v)) >= 1 for v in vals.values()):
            held.append((s["author"], "|r| >= 1"))
            continue
        seen[name] = seen.get(name, 0) + 1
        g = name if seen[name] == 1 else f"{name} ({seen[name]})"
        for i in measured:
            for j in measured:
                if j > i:
                    continue
                n = n_beh if 6 in (i, j) and i != j else n_all
                long.append(["cor", VARS[i - 1], VARS[j - 1], "1" if i == j else vals[(i, j)], n, g])
    with open(out / f"{TABLE}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stat", "var1", "var2", "value", "n", "group"])
        w.writerows(long)
    print(f"{len(studies)} study blocks; built {len({r[5] for r in long})}")
    for h in held:
        print("held:", h)


if __name__ == "__main__":
    main(sys.argv[1])
