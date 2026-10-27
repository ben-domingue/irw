"""ding_2014_sas, ding_2014_eri, ding_2014_overcommitment, ding_2014_mbi.

Source: Ding, Y., Qu, J., Yu, X., & Wang, S. (2014). The mediating effects of
burnout on the relationship between anxiety symptoms and occupational stress
among community healthcare workers in China: A cross-sectional study. PLoS
ONE, 9(9), e107130, doi:10.1371/journal.pone.0107130.
Data: figshare 1136113, the deposited SPSS file (pinned by sha256).

Licence: the figshare deposit carries CC BY 4.0, as does the article.

1,243 effective respondents (of 1,752 approached, 70.95%) from 52 Community
Health Centers in nine cities of Liaoning Province, China, self-administered
questionnaires, November-December 2012. Column labels in the deposit are
Chinese; the blocks below are identified by the deposit's own subscale totals.

- E1..E20   Zung Self-Rating Anxiety Scale (SAS), 20 items, 1-4. The deposit's
            anxiety total JIAOLV equals the plain sum of these columns for
            1,220 of the 1,243 rows, so they are stored as administered.
            Columns are named E<n>M_1 or E<n>N_1; the five N-marked ones are
            items 5, 9, 13, 17 and 19, which are the SAS's reverse-worded
            items.
- B1..B17   Chinese effort-reward imbalance scale, 1-5: B1..B6 effort,
            B7..B17 reward. FC (the deposit's effort total) is the exact sum
            of B1..B6. HB (its reward total) equals the sum of B7..B17 with
            the seven N-marked columns taken as 6 - x, for 97.99% of rows, so
            the reward items too are stored as administered and it is the
            total that applies the reversal.
- C1..C6    Effort-reward imbalance overcommitment, 1-4. NZTR is their exact
            sum.
- D1..D15   Maslach Burnout Inventory-General Survey, 0-6. The deposit's three
            subscale totals split the block exactly as the paper describes it
            (5, 4 and 6 items): QXSJ = D1..D5 emotional exhaustion,
            XJDM = D6..D9 cynicism, CJG = D10..D15 professional efficacy.

Effort and reward ship as one table: they are one instrument on one response
format, and the deposit's two totals identify which items are which.
Overcommitment is a third ERI subscale but on 1-4, so it ships separately
rather than mixing response formats in a table.

Not shipped, being scores rather than responses: FC, HB, NZTR, QXSJ, XJDM,
CJG, JIAOLV, the effort-reward ratio ERR, and the grouped covariates A2M and
A3M (A2 and A3 themselves ship).

Two deposit defects, both left visible rather than repaired:
- 276 item cells hold non-integer values (0.38% of 71,078 across 17 rows),
  which is SPSS mean substitution for missing responses. They are identifiable
  exactly because they are not integers, and are set missing here.
- 100 cells in 7 of the 20 SAS columns hold a 5 on a scale the instrument and
  the paper both define as 1-4. The remaining 13 columns never use a 5 across
  1,243 respondents, so this is not a 1-5 item; the values cannot be responses
  and are set missing.

Mapping
- id               = row number. The deposit's BIANHAO is an 11-digit
                     questionnaire serial that encodes the health centre, so
                     it is not shipped.
- cov_marital      = A1, 1-3
- cov_work_years   = A2, years (0.5-39)
- cov_weekly_hours = A3, hours actually worked per week
No age or sex is deposited, though the paper adjusts for demographics.

Item text: not shipped. The deposit carries item codes only; the SAS, ERI and
MBI-GS are published instruments administered here in Chinese.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd
import pyreadstat

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "https://ndownloader.figshare.com/files/1631983"
SHA256 = "4ad4a71f7f968246049efead14dfc13a5f3859e9c41f243792f68ed0a459d37a"
CACHE = Path.home() / ".cache" / "irw-plos" / "ding_2014.sav"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w, _ = pyreadstat.read_sav(str(CACHE))
assert w.shape == (1243, 72)


def block(prefix):
    return [c for c in w.columns if c.startswith(prefix) and c.endswith("_1")]


SAS, ERI, OC, MBI = block("E"), block("B"), block("C"), block("D")
assert (len(SAS), len(ERI), len(OC), len(MBI)) == (20, 17, 6, 15)

## the deposit's own totals identify every block
assert (w[ERI[:6]].sum(axis=1) == w["FC"]).all()
assert (w[OC].sum(axis=1) == w["NZTR"]).all()
assert (w[MBI[:5]].sum(axis=1) == w["QXSJ"]).all()    # emotional exhaustion
assert (w[MBI[5:9]].sum(axis=1) == w["XJDM"]).all()   # cynicism
assert (w[MBI[9:]].sum(axis=1) == w["CJG"]).all()     # professional efficacy
rew = w[ERI[6:]].copy()
for c in [c for c in ERI[6:] if "N_1" in c]:
    rew[c] = 6 - rew[c]
assert abs((rew.sum(axis=1) == w["HB"]).mean() - 0.9799) < 0.001
assert abs((w[SAS].sum(axis=1) == w["JIAOLV"]).mean() - 0.9815) < 0.001
## the paper's headline figure: 38.0% anxiety, SAS raw >= 40 (Chinese norm)
assert abs((w["JIAOLV"] >= 40).mean() - 0.380) < 0.005


def _alpha(df):
    k = df.shape[1]
    return k / (k - 1) * (1 - df.var(ddof=1).sum() / df.sum(axis=1).var(ddof=1))


## the paper's reported reliabilities, reproduced on the deposited columns
assert abs(_alpha(w[SAS]) - 0.85) < 0.005   # paper: 0.85
assert abs(_alpha(w[MBI]) - 0.84) < 0.005   # paper: 0.84

COVS = {"A1": "cov_marital", "A2": "cov_work_years", "A3": "cov_weekly_hours"}
w = w.rename(columns=COVS)
covs = list(COVS.values())
w.insert(0, "id", range(1, len(w) + 1))

SCALES = {
    "ding_2014_sas": (SAS, {1, 2, 3, 4}),
    "ding_2014_eri": (ERI, {1, 2, 3, 4, 5}),
    "ding_2014_overcommitment": (OC, {1, 2, 3, 4}),
    "ding_2014_mbi": (MBI, {0, 1, 2, 3, 4, 5, 6}),
}
dropped = 0
for table, (items, ok) in SCALES.items():
    df = w.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    ## SPSS mean substitution (non-integer) and out-of-scale codes are not responses
    keep = df["resp"].notna() & ((df["resp"] % 1) == 0) & df["resp"].isin(list(ok))
    dropped += int((~keep).sum())
    df = df[keep].copy()
    df["resp"] = df["resp"].astype(int)
    permitted = {i: ok for i in items}
    df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    df.to_csv(f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
assert dropped == 376, dropped  # 276 imputed + 100 out-of-scale SAS fives
print(f"cells set missing: {dropped} (276 mean-substituted, 100 out-of-scale)")
