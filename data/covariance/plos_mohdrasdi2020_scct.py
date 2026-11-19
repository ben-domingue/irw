"""Covariance family (irw_cov, source = "cov"): SCCT well-being model and life
satisfaction of university students MASEM (Mohd Rasdi & Ahrari, PLOS ONE 2020),
study-level raw correlations.

Source: Mohd Rasdi, R., & Ahrari, S. (2020). The applicability of social cognitive
career theory in predicting life satisfaction of university students: A meta-analytic
path analysis. PLOS ONE, 15(8), e0237838. https://doi.org/10.1371/journal.pone.0237838
Licence: CC BY 4.0 (the <license> element of the article XML; the script stops if it
is not CC BY).

Read from the article XML (journals.plos.org, type=manuscript):
- Table 4, "Raw correlation coefficient and two-tailed p-value included for the
  meta-analytic processes": one row per sample (No. 1-20) and 16 pair columns among
  ES, PT, SE, OE, GP, DS, LS. The table note says a dash marks a correlation the study
  did not report. Five of the 21 pairs have no column at all (ES-LS, PT-OE, PT-GP,
  SE-LS, OE-LS).
- Table 3, "A short review of included studies": the same No. 1-20, with author,
  year, country, sample, sample size (N) and mean age.

Each sample's variables are those with at least one printed correlation (a variable
with none was not measured there and is dropped). A pair between two such variables
that is a dash, or has no column in Table 4, is written as a row with an empty value
(blank cells allowed, Ben, 2026-11-18). A sample with an |r| >= 1 or fewer than two
variables would be held; none is. Significance stars are stripped; values are written
in shortest round-trip form of the printed decimal (".43" -> "0.43"), i.e. unchanged.
The diagonal is written as 1. N is Table 3's sample size ("1,187" -> 1187) on every
row. Table 3's means and SDs are not used (see the notes in matrices.csv).

Modification (2026-11-18): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per sample, labelled "<author> (<year>)" from
Table 3. Values unchanged.

Usage: python3 data/covariance/plos_mohdrasdi2020_scct.py <out dir>
"""
import csv
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0237838&type=manuscript"
VARS = ["ES", "PT", "SE", "OE", "GP", "DS", "LS"]     # Table 4, order of first appearance
TABLE = f"mohdrasdi_2020_scct{len(VARS)}"
COUNTRY = {"USA": "US", "Portugal": "PT", "Turkey": "TR", "Argentina": "AR", "Canada": "CA",
           "Taiwan": "TW", "Singapore": "SG", "China": "CN", "Spain": "ES",
           "Brazil and Portugal": "BR;PT", "Australia": "AU"}
DASH = {"-", "–", "—", ""}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read().decode("utf8")


def table(x, label):
    for tw in re.findall(r"<table-wrap .*?</table-wrap>", x, re.S):
        if re.search(r"<label>(.*?)</label>", tw).group(1) == label:
            return [[html.unescape(re.sub("<[^>]+>", "", c)).strip()   # <td .../> is an empty cell
                     for c in re.findall(r"<t[hd](?:[^>]*/>|[^>]*>(.*?)</t[hd]>)", tr, re.S)]
                    for tr in re.findall(r"<tr>(.*?)</tr>", tw, re.S)]
    raise SystemExit(f"{label} not found")


def num(s):
    s = re.sub(r"\*+$", "", s.strip()).replace("−", "-")
    if not re.fullmatch(r"-?\d*\.\d+", s):
        raise SystemExit(f"not a correlation: {s!r}")
    return repr(float(s))


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    x = get(URL)
    lic = re.search(r'<license xlink:href="([^"]+)"', x).group(1)
    if not re.search(r"creativecommons\.org/licenses/by/", lic):
        raise SystemExit(f"licence is not CC BY: {lic}")
    t3, t4 = table(x, "Table 3"), table(x, "Table 4")
    h3, h4 = t3[0], t4[0]
    if h3[:3] != ["No.", "Author(s)", "Year"] or h3[5] != "Country" or h3[8:] != ["Sample size", "Mean age"]:
        raise SystemExit(f"Table 3 header changed: {h3}")
    if h4[:2] != ["No.", "Study"] or len(h4) != 18:
        raise SystemExit(f"Table 4 header changed: {h4}")
    pairs = [tuple(p.split("-")) for p in h4[2:]]
    if any(a not in VARS or b not in VARS for a, b in pairs):
        raise SystemExit(f"unknown variable in {h4}")
    info = {r[0]: r for r in t3[1:]}
    long, records, held = [], [], []
    for r in t4[1:]:
        s = info[r[0]]
        author = re.sub(r"\s*\[\d+\]$", "", s[1]).strip()
        label = f"{author} ({s[2]})"
        if any(rec["group"] == label for rec in records):
            raise SystemExit(f"duplicate label {label}")
        n = int(s[8].replace(",", ""))
        r_of = {frozenset(p): num(c) for p, c in zip(pairs, r[2:]) if c not in DASH}
        v = [x for x in VARS if any(x in p for p in r_of)]
        if len(v) < 2 or any(abs(float(c)) >= 1 for c in r_of.values()):
            held.append({"group": label, "n": n, "why": "|r| >= 1 or < 2 variables"})
            continue
        blank = []
        for a, i in enumerate(v):
            for j in v[:a + 1]:
                val = "1" if i == j else r_of.get(frozenset((i, j)), "")
                if i != j and val == "":
                    blank.append(f"{j}-{i}")
                long.append({"stat": "cor", "var1": i, "var2": j, "value": val, "n": n, "group": label})
        mage = s[9] if s[9] not in DASH else ""
        records.append({"group": label, "no": int(r[0]), "table4_label": r[1], "n_obs": n,
                        "vars": v, "blank": blank, "dropped": [x for x in VARS if x not in v],
                        "year": s[2][:4], "country": "" if s[5] in DASH else COUNTRY[s[5]],
                        "country_printed": s[5], "sample": s[6], "type": s[3], "mean_age": mage})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} samples built, {len(held)} held")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 plos_mohdrasdi2020_scct.py <out dir>")
    main(sys.argv[1])
