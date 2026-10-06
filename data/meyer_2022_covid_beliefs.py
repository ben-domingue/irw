"""meyer_2022_covid_beliefs, meyer_2022_covid_selfeff, meyer_2022_pss10,
meyer_2022_bfi.

Source: Meyer, N., Niemand, T., Davila, A., & Kraus, S. (2022). Biting the
bullet: When self-efficacy mediates the stressful effects of COVID-19 beliefs.
PLOS ONE, 17(1), e0263022, doi:10.1371/journal.pone.0263022. Data: Mendeley
Data doi:10.17632/b8zxmw5z3g.1, "Meyer_etal_Biting_the_Bullet.csv" (pinned by
sha256; the hash is the one Mendeley's API reports for the file).

Licence: Mendeley Data record "CC BY 4.0".

23,629 users of Praditus, a French talent-management platform where people
take personality and attitude surveys to get an assessment of themselves
(paper, "Sample and data collection"); mostly French, US, German, Italian,
Mexican and Spanish nationals, mean age 28.5. Four instruments:
- Info_1..10, Invul_1..5, Disrupt_1..4, Health_1..3, Resp_1..5
      COVID-19 beliefs (Clark et al. 2020): information seeking,
      invulnerability, disruption, health importance, response effectiveness.
      One table: they are the subscales of one instrument. 0-4.
- Selfeff_1..3   COVID-19 self-efficacy, 3 items, 0-4.
- Stress_1..10   10-item perceived stress inventory (the PSS-10), 0-4.
- B5Agr_1..4, B5Cons_1..4, B5Extr_1..4, B5Open_1..6, B5Stab_1..4
      22 Big Five items "based on the inventory of John and Srivastava",
      0-6.
The paper says every measure was answered on a five-point scale (1-5). The
deposit holds 0-4 for the first three, consistent with 1-5 shifted down, and
0-6, seven points, for the Big Five. Codes are shipped as stored.

Repeat takers are dropped. In 478 rows some item values are not whole
numbers: 468 rows hold only halves, 7 only thirds, and 3 a mix that sits on
sixths -- what averaging a user's two, three or more attempts produces. It is
not imputation: the deposit's 40 genuinely missing item cells and 175 missing
ages were left blank. An average of two answers can also be a whole number
(2 and 4 give 3), so the integer cells of those rows are not trustworthy
either, and the whole row is dropped, not just its fractional cells.

Item text: not shipped -- the CSV has column codes only. The items are in the
paper's Table 1 (published as an image). PSS is blocked in
itemtext/instrument_rights_register.csv, as is the BFI-44 the Big Five items
are drawn from.

Mapping
- id               = the deposit's unnamed row-number column (1..23629)
- cov_gender       = gender (female, male, non_binary, no_disclosure)
- cov_age          = age
- cov_nationality  = nationality (ISO 3166-1 alpha-2)
- cov_work_experience = the four 0/1 experience dummies collapsed into one
      category (less_1y, 1-5y, 6-10y, more_10y); missing when none is set,
      which is true of 14,283 rows (the paper does not say why)
"""
import hashlib
import re
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = ("https://data.mendeley.com/public-files/datasets/b8zxmw5z3g/files/"
       "4444ee62-aa8e-4922-ac10-a8b9531eebd2/file_downloaded")
SHA256 = "d99f4f53da641e8f27291d736c7db14f08db17ef5c1633f60f549cf7abf18a5d"
CACHE = Path.home() / ".cache" / "irw-plos" / "meyer_2022.csv"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_csv(CACHE)
assert len(w) == 23629
w = w.rename(columns={"Unnamed: 0": "id"})
assert w["id"].is_unique

SCALES = {  # table: (column prefixes, max)
    "meyer_2022_covid_beliefs": (["Info", "Invul", "Disrupt", "Health", "Resp"], 4),
    "meyer_2022_covid_selfeff": (["Selfeff"], 4),
    "meyer_2022_pss10": (["Stress"], 4),
    "meyer_2022_bfi": (["B5Agr", "B5Cons", "B5Extr", "B5Open", "B5Stab"], 6),
}
item_cols = {t: [c for c in w.columns if re.sub(r"_\d+$", "", c) in p]
             for t, (p, _) in SCALES.items()}
all_items = sum(item_cols.values(), [])
assert len(all_items) == 27 + 3 + 10 + 22

## repeat takers: any non-integer item value marks an averaged row
X = w[all_items]
averaged = ((X % 1 != 0) & X.notna()).any(axis=1)
assert averaged.sum() == 478
## missing answers were left missing, not filled
assert X.isna().sum().sum() == 40
w = w[~averaged]

exp = {"exp_less_1y": "less_1y", "exp_1-5y": "1-5y", "exp_6-10y": "6-10y", "exp_more_10y": "more_10y"}
E = w[list(exp)]
assert E.isin([0, 1]).all().all() and (E.sum(axis=1) <= 1).all()
w["cov_work_experience"] = E.idxmax(axis=1).map(exp).where(E.sum(axis=1) == 1)
w["cov_age"] = w["age"].astype("Int64")
w = w.rename(columns={"gender": "cov_gender", "nationality": "cov_nationality"})
covs = ["cov_gender", "cov_age", "cov_nationality", "cov_work_experience"]

for table, (_, hi) in SCALES.items():
    items = item_cols[table]
    df = w.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    df = df.dropna(subset=["resp"])
    assert (df["resp"] % 1 == 0).all() and df["resp"].between(0, hi).all(), table
    df["resp"] = df["resp"].astype(int)
    df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values={i: set(range(0, hi + 1)) for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    df.to_csv(f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
