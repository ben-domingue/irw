"""uritani_2023_ases8.

Source: Uritani, D., Kubo, T., Yasuura, Y., & Fujii, T. (2023). Reliability
and validity of the Japanese short-form arthritis self-efficacy scale in
patients with knee osteoarthritis: A cross-sectional study. PLOS ONE, 18(10),
e0292426, doi:10.1371/journal.pone.0292426. Data: Supporting Information S1
Dataset, journal.pone.0292426_S1_Dataset.xlsx (pinned by sha256).

Licence: article CC BY 4.0, which covers its SI.

179 Japanese adults with knee osteoarthritis.
- ASES1_1..8  Japanese 8-item short-form Arthritis Self-Efficacy Scale
              (ASES-8J), 1-10. ASES2total is a retest total with no item
              columns, so the retest is not shipped.

Mapping
- id         = ID_1 (1-179; unique). The column name carries a U+200E
               mark in the deposit, so it is found by prefix.
- cov_site   = the letter prefix of the participant code ID_2 (K 90, S 59,
               M 17, F 13). Not documented; possibly the recruiting site
               (the paper recruited at five clinics and hospitals).
- cov_age    = age
- cov_sex    = sex, as coded in the deposit (0/1; no codebook is deposited)

Item text: not shipped -- the deposit has column codes only; the ASES-8J
wording is in Uritani et al.'s earlier cross-cultural adaptation paper
(rights not checked).

Not shipped: the other measures (WOMAC, PCS, PSEQ, DASS, fear of movement),
which are deposited only as totals or subscale scores.
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
       "&id=10.1371/journal.pone.0292426.s001")
SHA256 = "ef1e5e2e896e386fc34e405f8821c0081e9b06e9fbdaad1cda5b372745f178e5"
CACHE = Path.home() / ".cache" / "irw-plos" / "uritani_2023.xlsx"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_excel(CACHE)
id_col = next(c for c in w.columns if c.startswith("ID") and c != "ID_2")
assert len(w) == 179 and w[id_col].is_unique and w["ID_2"].is_unique
items = [f"ASES1_{i}" for i in range(1, 9)]
w["cov_site"] = w["ID_2"].str[0]
assert set(w["cov_site"]) == {"K", "S", "M", "F"}
w = w.rename(columns={id_col: "id", "age": "cov_age", "sex": "cov_sex"})
covs = ["cov_site", "cov_age", "cov_sex"]
df = w.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
df["resp"] = pd.to_numeric(df["resp"], errors="coerce")
df = df.dropna(subset=["resp"])
assert (df["resp"] % 1 == 0).all() and df["resp"].between(1, 10).all()
df["resp"] = df["resp"].astype(int)
df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

checks = run_qc(df, permitted_values={i: set(range(1, 11)) for i in items})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
df.to_csv("uritani_2023_ases8.csv", index=False)
print(f"uritani_2023_ases8: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
