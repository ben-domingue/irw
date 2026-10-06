"""gori_2020_pss10, gori_2020_cope, gori_2020_dsq40, gori_2020_swls.

Source: Gori, A., Topino, E., & Di Fabio, A. (2020). The protective role of
life satisfaction, coping strategies and defense mechanisms on perceived
stress due to COVID-19 emergency: A chained mediation model. PLOS ONE, 15(11),
e0242402, doi:10.1371/journal.pone.0242402. Data: figshare
doi:10.6084/m9.figshare.13133180, the one .sav file (pinned by sha256).

Licence: figshare record "CC BY 4.0".

1,102 Italian adults, one wave, four instruments (all Italian versions):
- PSS10_1..10   Perceived Stress Scale-10, 0 (never) - 4 (very often)
- COPE_1..60    COPE-NVI, 1 (I don't usually do this at all) - 4 (I usually do this)
- DSQ40_1..40   Defense Style Questionnaire-40, 1 - 9
- SWLS_1..5     Satisfaction With Life Scale, 1 (strongly disagree) - 7 (strongly agree)
Scales and anchors are from the paper's Measures section.

Imputed cells are dropped. The deposit is the analysis file, and 1.3% of item
cells hold a non-integer value. Every item has exactly ONE distinct
non-integer value, i.e. the item mean was written into missing cells; the
script asserts that. A mean-imputed cell is therefore always non-integer
(unless an item mean were a whole number, which the assertion would also
expose as a second distinct value never appearing), so removing non-integer
cells removes every imputed cell rather than only some.

Responses are as administered: the deposit's R_PSS_*_R / R_COPE_*_R columns
are reverse-scored copies of items already present and are not shipped.

Mapping
- id         = row number (the deposit has no id column)
- cov_age    = Age; the one non-integer age (the mean, imputed) is set missing
- cov_gender = Gender (1 Male, 2 Female; SPSS value labels)

Not shipped: Covid19 (Covid-19 infection), which is "No" for every respondent.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "https://ndownloader.figshare.com/files/25205303"
SHA256 = "59ca6de007e27ab58f291e973654bea5de280d8c13356c87120decb278692df2"
CACHE = Path.home() / ".cache" / "irw-plos" / "gori_2020.sav"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_spss(CACHE, convert_categoricals=False)
assert len(w) == 1102
w.insert(0, "id", range(1, len(w) + 1))
assert (w["Covid19"] == 2).all()
w = w.rename(columns={"Age": "cov_age", "Gender": "cov_gender"})
w["cov_age"] = w["cov_age"].where(w["cov_age"] % 1 == 0)
covs = ["cov_age", "cov_gender"]
w[covs] = w[covs].astype("Int64")

SCALES = {  # table: (prefix, n items, min, max)
    "gori_2020_pss10": ("PSS10_", 10, 0, 4),
    "gori_2020_cope": ("COPE_", 60, 1, 4),
    "gori_2020_dsq40": ("DSQ40_", 40, 1, 9),
    "gori_2020_swls": ("SWLS_", 5, 1, 7),
}
for table, (prefix, n, lo, hi) in SCALES.items():
    items = [f"{prefix}{i}" for i in range(1, n + 1)]
    X = w[items]
    nonint = X.notna() & (X % 1 != 0)
    ## mean imputation: one fractional value per item, so every imputed cell is visible
    assert all(X.loc[nonint[c], c].nunique() <= 1 for c in items), table
    df = w[["id"] + covs].join(X.mask(nonint))
    df = df.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    df = df.dropna(subset=["resp"])
    df["resp"] = df["resp"].astype(int)
    assert df["resp"].between(lo, hi).all(), table
    df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values={i: set(range(lo, hi + 1)) for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    df.to_csv(f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()} "
          f"imputed_dropped={int(nonint.values.sum())}")
