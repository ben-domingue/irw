"""wilkins_2018_phq9.

Source: Wilkins, S. S., Akhtar, N., Salam, A., Bourke, P., Joseph, S.,
Santos, M., & Shuaib, A. (2018). Acute post stroke depression at a Primary
Stroke Center in the Middle East. PLOS ONE, 13(12), e0208708,
doi:10.1371/journal.pone.0208708. Data: Supporting Information S1 Dataset,
journal.pone.0208708_S1_Dataset.xls (pinned by sha256).

Licence: the article is CC0 (public domain dedication), which covers its SI.

Acute stroke patients at Hamad General Hospital, Doha, screened by stroke-unit
nurses within days of the stroke, March 2016 - March 2017.
- PHQ1..PHQ9  Patient Health Questionnaire-9, 0 (not at all) - 3 (nearly every day)
- "." marks an item not recorded and is dropped.

Mapping
- id         = SN (serial number; unique)
- cov_age    = Age
- cov_gender = Gender, as coded in the deposit (no codebook is deposited;
               1/2, labels not given)

Not shipped: the PHQ-2/PHQ-9 scores and cut-offs, the Mini-Cog, the
"how difficult" item (Bothers03nottovery, a functional-impact question
outside the 9 symptom items), and the clinical record fields.
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
       "&id=10.1371/journal.pone.0208708.s001")
SHA256 = "94631fdc2dcf271b0ffde9f8baf36b329fe74204b9a38d48c623074299f8e9b4"
CACHE = Path.home() / ".cache" / "irw-plos" / "wilkins_2018.xls"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_excel(CACHE)
assert len(w) == 291 and w["SN"].is_unique
items = [f"PHQ{i}" for i in range(1, 10)]
w = w.rename(columns={"SN": "id", "Age": "cov_age", "Gender": "cov_gender"})
covs = ["cov_age", "cov_gender"]
df = w.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
assert set(df["resp"].astype(str)) <= {"0", "1", "2", "3", "."}
df["resp"] = pd.to_numeric(df["resp"], errors="coerce")
df = df.dropna(subset=["resp"])
df["resp"] = df["resp"].astype(int)
df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

checks = run_qc(df, permitted_values={i: {0, 1, 2, 3} for i in items})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
df.to_csv("wilkins_2018_phq9.csv", index=False)
print(f"wilkins_2018_phq9: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
