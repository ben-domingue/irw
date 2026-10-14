"""gimenez_espert_2026_aco, gimenez_espert_2026_unipsico, gimenez_espert_2026_violence.

Source: Giménez-Espert, M. d. C., Sanchis-Giménez, L., Prado-Gascó, V. J., &
Ibrahim, M. I. (2026). Words on fire: Nurses' communication attitudes in the
burnout equation. PLOS ONE, 21(9), e0358785, doi:10.1371/journal.pone.0358785.
Data: Supporting Information S1 Data, ACOBurnout_PLS (semicolon-separated
CSV, pinned by sha256).

Licence: the article is CC BY 4.0, which covers its SI.

193 direct-care nurses from four public hospitals in the Valencian Community,
Spain, convenience sample, Spanish-language questionnaire. The deposit holds
71 item columns, IT1..IT74 with IT42, IT67 and IT68 absent, and no variable
list. The paper's Instruments section describes 71 items in three response
formats, and the formats partition the columns exactly:

- IT1..IT12   (1 - 5)  Attitudes Towards Communication, reduced version
              (ACO-R), 12 items, 1 = strongly disagree, 5 = strongly agree.
              The affective items are worded negatively and left as
              administered (several correlate negatively with the rest).
- IT13..IT66  (0 - 4)  53 items, 0 = never, 4 = very frequently (every day):
              the UNIPSICO battery scales (interpersonal conflicts 6, inequity
              6, role conflict 4, role clarity 5, workload 6, social support
              6, autonomy 5, resources 8) and the 7-item reduced Burnout
              Syndrome Evaluation Questionnaire (CESQT). The order of these
              scales within the block is NOT recoverable: the paper's order
              does not reproduce its reported alphas, and no codebook is
              deposited. They ship as one table, `..._unipsico`, with the
              deposit's item codes, rather than as a split that cannot be
              verified.
- IT69..IT74  (1 - 5)  Workplace violence, 6 items (physical, verbal and
              psychological violence, each from patients/visitors and from
              colleagues/supervisors), 1 = strongly disagree, 5 = strongly
              agree. Cronbach's alpha here is .82, the paper reports .83.

Blank cells (a single space) are missing responses.

Mapping
- id = codigo (OA1..OA193; unique)
No covariates are deposited.

Item text: not shipped. CESQT and the UNIPSICO battery are published
instruments, and ACO is registered intellectual property of the University of
Valencia; wording is not in the deposit.
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
       "&id=10.1371/journal.pone.0358785.s001")
SHA256 = "f2a112bd8d429f9b372b956734e844d99a3a6de9a291081443b70b945e083f2b"
CACHE = Path.home() / ".cache" / "irw-plos" / "gimenez_espert_2026.csv"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_csv(CACHE, sep=";", encoding="utf-8-sig", na_values=[" "])
w = w.rename(columns={"codigo": "id"})
assert w.shape == (193, 72) and w["id"].is_unique
present = [c for c in w.columns if c.startswith("IT")]
assert len(present) == 71 and {"IT42", "IT67", "IT68"}.isdisjoint(present)

TABLES = {  # table: (item columns, permitted values)
    "gimenez_espert_2026_aco": ([f"IT{i}" for i in range(1, 13)], {1, 2, 3, 4, 5}),
    "gimenez_espert_2026_unipsico": ([f"IT{i}" for i in range(13, 67) if i != 42], {0, 1, 2, 3, 4}),
    "gimenez_espert_2026_violence": ([f"IT{i}" for i in range(69, 75)], {1, 2, 3, 4, 5}),
}
assert sum(len(v[0]) for v in TABLES.values()) == 71
for table, (items, ok) in TABLES.items():
    df = w.melt(id_vars=["id"], value_vars=items, var_name="item", value_name="resp")
    df = df.dropna(subset=["resp"])
    df["resp"] = df["resp"].astype(int)
    assert df["resp"].isin(ok).all(), table
    df = df[["id", "item", "resp"]].sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values={i: ok for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    df.to_csv(f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
