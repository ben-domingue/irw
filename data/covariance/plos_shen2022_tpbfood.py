"""Covariance family (irw_cov, source = "cov"): TPB and sustainable food consumption
MASEM (Shen, Xu & Liu, PLOS ONE 2022), study-level raw correlations.

Source: PLOS ONE 17(11): e0275312, https://doi.org/10.1371/journal.pone.0275312,
"Predicting sustainable food consumption across borders based on the theory of planned
behavior: A meta-analytic structural equation model", CC BY 4.0 (licence element of the
article XML). Table 2, "Raw correlations considered for the meta-analytic procedures":
one row per sample with Sample size (N) and the ten pairwise correlations among ATT,
SN, PBC, PI (purchase intention) and PB (purchase behaviour). The table note says
"n.a." marks correlations the original papers did not report.

A variable whose correlations are all "n.a." is dropped from that sample. A sample
with any other "n.a." among its reported variables, an |r| >= 1, or fewer than two
variables is not built (printed as held). Values are parsed from the article XML text
as printed (shortest round-trip form).

Usage: python3 data/covariance/plos_shen2022_tpbfood.py <out dir>
"""
import csv
import html
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0275312&type=manuscript"
TABLE = "shen_2022_tpbfood5"
VARS = ["ATT", "SN", "PBC", "PI", "PB"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read().decode("utf8")


def table(x, label):
    for tw in re.findall(r"<table-wrap .*?</table-wrap>", x, re.S):
        if re.search(r"<label>(.*?)</label>", tw).group(1) == label:
            return [[html.unescape(re.sub("<[^>]+>", "", c)).strip()
                     for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
                    for r in re.findall(r"<tr>(.*?)</tr>", tw, re.S)]
    raise SystemExit(f"{label} not found")


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = table(get(URL), "Table 2")
    head = rows[0]
    pairs = [tuple(h.split("-")) for h in head[2:]]
    assert head[1] == "Sample size (N)" and all(a in VARS and b in VARS for a, b in pairs)
    long, held = [], []
    for r in rows[1:]:
        if len(r) != len(head):
            continue
        g = re.sub(r"\s*\[\d+\]$", "", r[0])
        n = int(r[1].replace(",", ""))
        cell = {frozenset(p): v for p, v in zip(pairs, r[2:])}
        vs = [v for v in VARS if any(x != "n.a." for k, x in cell.items() if v in k)]
        miss = [(a, b) for i, a in enumerate(vs) for b in vs[:i] if cell[frozenset((a, b))] == "n.a."]
        if miss or len(vs) < 2:
            held.append((g, vs, miss))
            continue
        vals = {k: repr(float(v.replace("−", "-"))) for k, v in cell.items() if v != "n.a."}
        if any(abs(float(v)) >= 1 for v in vals.values()):
            held.append((g, "|r| >= 1"))
            continue
        for i, a in enumerate(vs):
            for b in vs[: i + 1]:
                long.append(["cor", a, b, "1" if a == b else vals[frozenset((a, b))], n, g])
    groups = [r[5] for r in long]
    assert len(set(groups)) == len(dict.fromkeys(groups))
    with open(out / f"{TABLE}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stat", "var1", "var2", "value", "n", "group"])
        w.writerows(long)
    print(f"built {len(set(groups))} samples")
    for h in held:
        print("held:", h)


if __name__ == "__main__":
    main(sys.argv[1])
