"""zhao_2025_technophobia, zhao_2025_htse, zhao_2025_eheals, zhao_2025_ssrs.

Source: Zhao, J., Hu, D., Du, H., Wang, H., Tu, X., Wang, A., & Parvar, S. Y.
(2025). Social support and technophobia in older patients with coronary heart
disease: The mediating roles of eHealth literacy and healthcare technology
self-efficacy. PLOS ONE, 20(6), e0325202, doi:10.1371/journal.pone.0325202.
Data: Supporting Information S1 File, journal.pone.0325202_S1_File.xlsx
(pinned by sha256).

Licence: the article is CC BY 4.0, which covers its SI.

396 community-dwelling patients aged 60+ with coronary heart disease, four
communities in Qingdao, China, paper questionnaires, December 2023 - May 2024.
Chinese versions of four instruments (paper, Measures):
- TA1..TA13     Technophobia Scale, 1 (strongly disagree) - 5 (strongly agree)
- HTSE1..HTSE12 Healthcare Technology Self-Efficacy Scale, 1 - 5. The paper
                says items 3, 6 and 10 are reverse-scored; in the deposit it is
                HTSE4 and HTSE8 that correlate negatively with the rest, so the
                file is taken to hold responses as administered and nothing is
                recoded.
- eHEALS1..8    eHealth Literacy Scale, 1 - 5
- SSRS1..SSRS10 Social Support Rating Scale (Xiao 1994). Items 1-4 and 8-10 are
                single-choice, 1 - 4. Items 6 and 7 are the number of support
                sources listed (1 - 6 here). Item 5 is deposited only as the
                sum of its five sub-items (8 - 20) and is NOT shipped: it is a
                score, not a response.
Technophobia totals average 38.0, matching the paper's Table 1 (37.4 men,
38.7 women), so the TA columns are as administered.

Mapping
- id                  = row number (the deposit has no id column). Two rows
                        are identical across all 51 columns and both are kept.
- cov_age_group       = age, 1 = 60-69, 2 = 70+
- cov_gender          = gender, 1 = male, 2 = female
- cov_residence       = Residence, 1 = city, 2 = rural
- cov_marital         = Marital status, 1 = married, 2 = single
- cov_household       = Type of residence, 1 = alone, 2 = spouse only,
                        3 = children only, 4 = spouse and children
- cov_work            = Work status, 1 = mental labour, 2 = physical labour,
                        3 = partly mental and partly physical
- cov_education       = Educational level, 1 = elementary or below, 2 = junior
                        high, 3 = high school / technical secondary, 4 = junior
                        college, 5 = bachelor or above
- cov_income          = Family monthly income (RMB), 1 = 0-6000, 2 = 6000-10000,
                        3 = 10000+
All code labels come from the paper's Table 1; the counts per code match it.

Item text: not shipped. The deposit has no wording; the instruments are
published scales administered in Chinese.
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
       "&id=10.1371/journal.pone.0325202.s001")
SHA256 = "97d104ef102fbd036b1d64e0e8206abb8638b049de239c0bddcd4b5f2b349c74"
CACHE = Path.home() / ".cache" / "irw-plos" / "zhao_2025.xlsx"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_excel(CACHE)
assert w.shape == (396, 51)
w.insert(0, "id", range(1, len(w) + 1))
COVS = {
    "age": "cov_age_group", "gender": "cov_gender", "Residence": "cov_residence",
    "Marital status": "cov_marital", "Type of residence": "cov_household",
    "Work status": "cov_work", "Educational level": "cov_education",
    "Family monthly income(RMB)": "cov_income",
}
w = w.rename(columns=COVS)
covs = list(COVS.values())
## code counts from the paper's Table 1
assert w["cov_age_group"].value_counts().to_dict() == {1: 202, 2: 194}
assert w["cov_gender"].value_counts().to_dict() == {1: 196, 2: 200}
assert w["cov_residence"].value_counts().to_dict() == {1: 303, 2: 93}
assert w["cov_household"].value_counts().to_dict() == {1: 29, 2: 307, 3: 18, 4: 42}
assert w["cov_work"].value_counts().to_dict() == {1: 104, 2: 169, 3: 123}
assert w["cov_income"].value_counts().to_dict() == {1: 78, 2: 181, 3: 137}
assert abs(w[[f"TA{i}" for i in range(1, 14)]].sum(axis=1).mean() - 38.0) < 0.1

SCALES = {  # table: (items, permitted values)
    "zhao_2025_technophobia": ([f"TA{i}" for i in range(1, 14)], {1, 2, 3, 4, 5}),
    "zhao_2025_htse": ([f"HTSE{i}" for i in range(1, 13)], {1, 2, 3, 4, 5}),
    "zhao_2025_eheals": ([f"eHEALS{i}" for i in range(1, 9)], {1, 2, 3, 4, 5}),
    "zhao_2025_ssrs": ([f"SSRS{i}" for i in (1, 2, 3, 4, 6, 7, 8, 9, 10)], None),
}
SSRS_OK = {f"SSRS{i}": {1, 2, 3, 4} for i in (1, 2, 3, 4, 8, 9, 10)}
SSRS_OK.update({"SSRS6": set(range(0, 10)), "SSRS7": set(range(0, 10))})
for table, (items, ok) in SCALES.items():
    permitted = {i: ok for i in items} if ok else SSRS_OK
    df = w.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    df = df.dropna(subset=["resp"])
    df["resp"] = df["resp"].astype(int)
    assert all(df.loc[df["item"] == i, "resp"].isin(v).all() for i, v in permitted.items()), table
    df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    df.to_csv(f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
