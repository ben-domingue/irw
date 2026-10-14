"""caprara_2020_mnesres, caprara_2020_panas.

Source: Caprara, M., Di Giunta, L., Bermúdez, J., Caprara, G. V., & Iannello,
P. (2020). How self-efficacy beliefs in dealing with negative emotions are
associated to negative affect and to life satisfaction across gender and age.
PLOS ONE, 15(11), e0242326, doi:10.1371/journal.pone.0242326. Data:
Supporting Information S1 Data, journal.pone.0242326_S1_Data.xlsx (pinned by
sha256): sheet Hoja2 is a variable list, sheet Hoja3 the headerless data.

Licence: the article is CC BY 4.0, which covers its SI.

Spanish adults born in Spain, mostly from the Madrid area, recruited through
the Open University in Madrid (UDIMA) and students' relatives and friends,
2014-2017. Spanish versions of the instruments, administered individually.

- AE1..AE40   Multidimensional Negative Emotions Self-Regulatory Efficacy
              Scale (MNESRES) item pool, 1 (not at all well) - 5 (very well).
              The paper's MNESRES is 15 items, three per emotion (anger,
              sadness, fear, shame, guilt); the deposit's standardised
              columns ZAE* identify them as AE3, 5, 7, 10, 13, 15, 19, 21, 24,
              26, 29, 31, 32, 35, 39. Which three belong to which emotion is
              not recorded. All 40 administered items ship; the other 25 were
              administered but not analysed in the paper.
- PN1..PN20   PANAS, 1 (not at all) - 5 (very much). The paper scores only
              the ten negative-affect items; all 20 ship. Which columns are
              the negative items is not recorded.
Not shipped: LS1..LS12 (twelve columns on 1 - 5). The paper's life
satisfaction measure is the 5-item SWLS on 1 - 7, which these cannot be, and
no other instrument is described. Held until the columns can be identified.

Values 99 (and a handful of 6 or 8, outside the scale) are set missing.

Rows: 1,701 in the deposit; the paper reports 1,695 (ages 20-94). The six
rows the authors left without an age group are all aged 19 and are dropped,
which reproduces the paper's N and its sex split (915 men, 780 women).
The deposit's ID_ldg column is not unique (104 codes shared by respondents
with different ages and responses), so it is not used.

Mapping
- id          = row number in the deposit (after dropping the six)
- cov_age     = Edad, in years (decimal, from date of birth)
- cov_gender  = Sexo, 1 = male, 2 = female (variable list: {1, Varón})
- cov_marital = EstadoCivil, 1 = single (Soltero); other codes not listed
- cov_education = NivelEstudios, 1 = illiterate (Analfabeta) ... 9; other
                code labels are not in the variable list

Item text: not shipped. The deposit has no wording.
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
       "&id=10.1371/journal.pone.0242326.s001")
SHA256 = "25aafc2ecc0ed599425db7893f29a5b5f446cd664ed5561df6fe59e0e104466c"
CACHE = Path.home() / ".cache" / "irw-plos" / "caprara_2020.xlsx"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

names = pd.read_excel(CACHE, sheet_name="Hoja2", header=None)[0].tolist()
w = pd.read_excel(CACHE, sheet_name="Hoja3", header=None)
assert w.shape == (1701, 145) and len(names) == 145
w.columns = names
w = pd.concat([pd.Series(range(1, len(w) + 1), name="id"), w], axis=1)
dropped = w["gruppo_edad"].isna()
assert dropped.sum() == 6 and (w.loc[dropped, "Edad"] < 20).all()
w = w[~dropped]
assert len(w) == 1695 and w["Sexo"].value_counts().to_dict() == {1: 915, 2: 780}

COVS = {"Edad": "cov_age", "Sexo": "cov_gender", "EstadoCivil": "cov_marital",
        "NivelEstudios": "cov_education"}
w = w.rename(columns=COVS)
covs = list(COVS.values())
w["cov_education"] = w["cov_education"].astype("Int64")

TABLES = {
    "caprara_2020_mnesres": [f"AE{i}" for i in range(1, 41)],
    "caprara_2020_panas": [f"PN{i}" for i in range(1, 21)],
}
OK = {1, 2, 3, 4, 5}
for table, items in TABLES.items():
    X = w[items].where(w[items].isin(OK))
    df = w[["id"] + covs].join(X)
    df = df.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    df = df.dropna(subset=["resp"])
    df["resp"] = df["resp"].astype(int)
    df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values={i: OK for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    df.to_csv(f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()} "
          f"out_of_scale_dropped={int((w[items].notna() & ~w[items].isin(OK)).values.sum())}")
