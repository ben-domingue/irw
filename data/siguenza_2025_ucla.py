"""siguenza_2025_ucla.

Source: Siguenza Campoverde, W. G., & Chamba Leiva, K. M. (2025). Factorial
structure, validity, and gender invariance of the UCLA-R loneliness scale in
ecuadorian adolescents. PLOS One, 20(9), e0328163,
doi:10.1371/journal.pone.0328163.
Data: OSF node 9zw43, "Datos UCLA..xlsx" (pinned by sha256).

Licence: the OSF node carries CC0 1.0 Universal. The article is separately
CC BY 4.0, but the deposit is what governs the data.

718 school-attending adolescents aged 14-18 from four educational institutions
in Loja, Ecuador, probabilistic sampling. The Spanish 20-item UCLA-R
Loneliness Scale, 1 = never, 2 = rarely, 3 = sometimes, 4 = frequently.

The deposit reproduces the paper's sample exactly: 718 rows, 288 male and 430
female, mean age 15.728 (SD 0.751) against the reported M = 15.72, SD = 0.747.
One respondent is 18, where the paper's range is 14-17; the row is kept.

Responses are as administered and nothing is recoded. The paper names items 1,
5, 6, 9, 10, 15, 16, 19 and 20 as the positively worded ones, which must be
reversed before the total is summed. In the deposit those nine still carry
their administered direction: alpha over the 20 raw columns is 0.55, reversing
exactly those nine raises it to 0.854, and the two subscale sums correlate
-0.433 raw. The paper reports alpha = .876 for a 19-item version; it does not
name the item it dropped, and no single deletion from the reversed 20 reaches
.876 (the best is .859, dropping UCLA9). All 20 items ship.

Mapping
- id         = row number (the deposit has no id column)
- item       = UCLA1..UCLA20
- resp       = 1-4 as administered
- cov_gender = Sexo, 1 = male, 2 = female (counts match the paper)
- cov_age    = Edad, years

Item text: not shipped. The deposit has item codes only; the wording is the
published Spanish UCLA-R.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "https://osf.io/download/q3m6h/"
SHA256 = "9ff5d1f0d787ea4bccc9aea2aba5b8142a6a799edaff1eec3aae3f6ee41172af"
CACHE = Path.home() / ".cache" / "irw-plos" / "siguenza_2025_ucla.xlsx"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_excel(CACHE)
assert w.shape == (718, 22)
ITEMS = [f"UCLA{i}" for i in range(1, 21)]
w = w.rename(columns={"Sexo": "cov_gender", "Edad": "cov_age"})
w.insert(0, "id", range(1, len(w) + 1))

## the paper's sample: 288 males, 430 females, M = 15.72, SD = 0.747
assert w["cov_gender"].value_counts().to_dict() == {2: 430, 1: 288}
assert abs(w["cov_age"].mean() - 15.72) < 0.01
assert abs(w["cov_age"].std() - 0.747) < 0.01

## the nine positively worded items are still as administered: reversing them
## takes alpha from 0.55 to 0.854 (paper: .876 on 19 items)
POSITIVE = [1, 5, 6, 9, 10, 15, 16, 19, 20]


def _alpha(df):
    k = df.shape[1]
    return k / (k - 1) * (1 - df.var(ddof=1).sum() / df.sum(axis=1).var(ddof=1))


rev = w[ITEMS].copy()
for i in POSITIVE:
    rev[f"UCLA{i}"] = 5 - rev[f"UCLA{i}"]
assert abs(_alpha(w[ITEMS]) - 0.55) < 0.01
assert abs(_alpha(rev) - 0.854) < 0.01

covs = ["cov_gender", "cov_age"]
df = w.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
df = df.dropna(subset=["resp"])
df["resp"] = df["resp"].astype(int)
permitted = {i: {1, 2, 3, 4} for i in ITEMS}
assert all(df.loc[df["item"] == i, "resp"].isin(v).all() for i, v in permitted.items())
df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

checks = run_qc(df, permitted_values=permitted)
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
df.to_csv("siguenza_2025_ucla.csv", index=False)
print(f"siguenza_2025_ucla: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
