"""panth_2026_bipq and panth_2026_cdrisc10.

Source: Panth, S., Panta, S., Cadel, S., et al. (2026). A cross-sectional
study on illness perception and resiliency among cancer patients, in
Bhaktapur cancer hospital. PLOS ONE, doi:10.1371/journal.pone.0356524.
Data: Supporting Information S1 Data, journal.pone.0356524.s001 (.xlsx,
pinned by sha256). Licence: the article is CC BY 4.0, which covers its SI.

170 adult cancer patients at Bhaktapur Cancer Hospital, Nepal (paper: mean
age 50; 52% male). The deposit holds item codes and totals only; no
demographics beyond the socio-economic score.

Tables
- panth_2026_bipq      IPQ-1..IPQ-8, Brief Illness Perception Questionnaire,
                       0-10 per item. Item 9 (open-ended causes) is not
                       deposited. B-IPQ items 3, 4 and 7 run in the opposite
                       direction from the rest in the source's scoring; the
                       deposit holds the responses as given and nothing is
                       reversed here.
- panth_2026_cdrisc10  CDRISC-1..CDRISC-10, Connor-Davidson Resilience
                       Scale 10-item, 0-4. One cell holds 9 (out of range,
                       a single entry error) and is dropped.
Both: the deposited totals equal the item sums for every row.

Mapping
- id      = row order (1..170). The deposit's SN is duplicated once (two
            different rows both carry 153; the paper's N is 170), so SN is
            not used as the key.
- cov_ses = "Total SE", the Modified Kuppuswamy socio-economic status
            score (the paper names the scale; the deposit's three
            unlabelled components, "Variable 1-3", have the ranges of its
            education, occupation and income sub-scores and sum to this
            total). The components are not shipped.

Item text: not shipped. The deposit has codes only (no labels at any level:
a plain .xlsx with code headers). CD-RISC wording is blocked in the rights
register; B-IPQ wording would need the Nepali version used, which is not
in the deposit or the paper.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = ("https://journals.plos.org/plosone/article/file?type=supplementary"
       "&id=10.1371/journal.pone.0356524.s001")
SHA256 = "68a516b70130c7f86f437a53347ac9410591bc9ba31558c7528a4ed887e5b8ea"
CACHE = Path.home() / ".cache" / "irw-plos" / "panth_2026.xlsx"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_excel(CACHE)
assert len(w) == 170
assert w["SN"].duplicated().sum() == 1 and w.loc[w["SN"].duplicated(), "SN"].item() == 153
w = w.reset_index(drop=True)
w.insert(0, "id", w.index + 1)
w = w.rename(columns={"Total SE": "cov_ses"})
covs = ["cov_ses"]

ipq = [f"IPQ-{i}" for i in range(1, 9)]
cd = [f"CDRISC-{i}" for i in range(1, 11)]
assert (w[ipq].sum(axis=1) == w["IPQ Total"]).all()
assert (w[cd].sum(axis=1) == w["CD-RISC Total"]).all()
assert (w[["Variable 1", "Variable 2", "Variable 3"]].sum(axis=1) == w["cov_ses"]).all()


def build(name, items, allowed):
    df = w.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    bad = ~df["resp"].isin(allowed)
    assert bad.sum() <= 1, df[bad]
    df = df[~bad]
    df["resp"] = df["resp"].astype(int)
    df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")
    checks = run_qc(df, permitted_values={i: set(allowed) for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    df.to_csv(f"{name}.csv", index=False)
    print(f"{name}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()} dropped={int(bad.sum())}")


build("panth_2026_bipq", ipq, range(0, 11))
build("panth_2026_cdrisc10", cd, range(0, 5))
