"""tolomeo_2026_icar16, tolomeo_2026_crt.

Source: Tolomeo, E., Ceraudo, L., Balducci, M., & Liuzza, M. T. (2026). Italian
adaptation and validation of the International Cognitive Ability Resource 16
sample test. Frontiers in Psychology, doi:10.3389/fpsyg.2026.1998035.
(Tolomeo and Ceraudo share first authorship.)
Data: Zenodo 10.5281/zenodo.23035572, a snapshot of the GitHub repository
Mac3581/Italian-Adaptation-and-Validation-of-the-ICAR-16-Sample-Test at v1.0.3,
file "Data and Script/icar_p.csv" (the zip is pinned by sha256).

Licence: the Zenodo record carries CC BY 4.0, as does the article. The ICAR
itself is a public-domain instrument (Condon & Revelle); the Italian wording is
these authors' own work and is covered by the deposit's licence.

494 Italian-speaking adults aged 18-78 completed, online, the 16-item ICAR
sample test and the long form of the Cognitive Reflection Test. Both are scored
0/1 in the deposit, so each ships as its own table over the same respondents:
`id` is the deposit's row order in both, which is what lets a user join them.

The paper analyses 486 respondents, not 494: its own script subsets to
`Nationality == "Italiana"` (`Revised ICAR 16 SAMPLE TEST_Italian Validation.R`
line 33), which drops exactly the 8 rows with another nationality. All 494 ship
with `cov_nationality` so that sample is reproducible. 326 of 494 are female
(66.0%); the paper's 66.4% is 322 of the 485 Italian-nationality respondents
with a recorded sex, its script treating the one Intersex respondent as NA.

Two rows are duplicates of another row across every column, demographics
included. They are kept: nothing distinguishes a real repeat pattern from a
double submission here, and 22 of 494 share a response pattern with someone.

The deposit's `ICAR` and `CRT` columns are row sums of the item columns
(verified) and are not shipped -- a total is derivable from the responses.

The ICAR codes carry four prefixes -- VR verbal reasoning, LN letter and number
series, MR matrix reasoning, R3D three-dimensional rotation -- which the
validator flags as a possible multi-scale file. They are the ICAR-16's four
domains within one instrument, and the paper's accepted model is a second-order
latent variable over exactly those four, so they ship as one table.

Mapping
- id               = row number in icar_p.csv (the deposit has no id column),
                     the same respondent in both tables
- item             = the deposit's own ICAR codes (VR4, LN7, MR45, R3D3, ...)
                     and CRT1-CRT6
- resp             = 0/1 as scored in the deposit
- cov_sex          = Sex, F / M / Intersex as recorded
- cov_age          = Age, years
- cov_education    = Education_level, Italian labels verbatim
- cov_employment   = Current_Employment, Italian labels verbatim
- cov_civil_status = Civil_status, Italian labels verbatim
- cov_nationality  = Nationality, Italian labels verbatim
- cov_region       = Region, Italian region names verbatim

Item text: not shipped here. The deposit publishes the Italian wording
("ICAR 16 ITEMS.pdf") and an English codebook, which is an item-text
extraction, not a job for this script.
"""
import hashlib
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

## the file key itself contains a slash (the GitHub owner), and Zenodo serves it
## only unencoded -- %2F returns 403
URL = ("https://zenodo.org/api/records/23035572/files/"
       "Mac3581/Italian-Adaptation-and-Validation-of-the-ICAR-16-Sample-Test-v1.0.3.zip/content")
SHA256 = "cbae7fd0c955d0a0ee42bd8cca597a6f6fbb9cb86af8052f48133c141f8d905a"
MEMBER = ("Mac3581-Italian-Adaptation-and-Validation-of-the-ICAR-16-Sample-Test-27d0830/"
          "Data and Script/icar_p.csv")
CACHE = Path.home() / ".cache" / "irw-zenodo" / "tolomeo_2026_icar16.zip"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    ## Zenodo 403s a "Mozilla/5.0" User-Agent and serves a named one
    req = urllib.request.Request(URL, headers={"User-Agent": "irw/1.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

with zipfile.ZipFile(CACHE) as z:
    w = pd.read_csv(io.BytesIO(z.read(MEMBER)))
assert w.shape == (494, 31)

ICAR = ["VR4", "VR16", "VR17", "VR19", "LN7", "LN33", "LN34", "LN58",
        "MR45", "MR46", "MR47", "MR55", "R3D3", "R3D4", "R3D6", "R3D8"]
CRT = [f"CRT{i}" for i in range(1, 7)]

## the deposit's totals are row sums of the items, so they carry nothing the
## responses do not
assert (w[ICAR].sum(axis=1) == w["ICAR"]).all()
assert (w[CRT].sum(axis=1) == w["CRT"]).all()
assert not w[ICAR + CRT].isna().any().any()

## the paper's sample is this file subset to Italian nationality: 486 rows (its
## script, line 33). Its "66.4% female" is over the 485 with a recorded sex --
## the same script treats the one Intersex respondent as NA (lines 41-42) --
## not over all 486, which would read 66.3%
it = w[w["Nationality"] == "Italiana"]
assert len(it) == 486
sexed = it[it["Sex"].isin(["F", "M"])]
assert len(sexed) == 485
assert round(100 * (sexed["Sex"] == "F").mean(), 1) == 66.4

w = w.rename(columns={"Sex": "cov_sex", "Age": "cov_age",
                      "Education_level": "cov_education",
                      "Current_Employment": "cov_employment",
                      "Civil_status": "cov_civil_status",
                      "Nationality": "cov_nationality",
                      "Region": "cov_region"})
COVS = ["cov_sex", "cov_age", "cov_education", "cov_employment",
        "cov_civil_status", "cov_nationality", "cov_region"]
w.insert(0, "id", range(1, len(w) + 1))

for name, items in (("tolomeo_2026_icar16", ICAR), ("tolomeo_2026_crt", CRT)):
    df = w.melt(id_vars=["id"] + COVS, value_vars=items,
                var_name="item", value_name="resp")
    df["resp"] = df["resp"].astype(int)
    permitted = {i: {0, 1} for i in items}
    assert all(df.loc[df["item"] == i, "resp"].isin(v).all()
               for i, v in permitted.items())
    df = df[["id", "item", "resp"] + COVS].sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    df.to_csv(f"{name}.csv", index=False)
    print(f"{name}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()} "
          f"mean_resp={df['resp'].mean():.3f}")
