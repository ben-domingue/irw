"""sirota_2018_crt (+ sirota_2018_crt_nom).

Source: Sirota, M. & Juanchich, M. (2018). Effect of response format on
cognitive reflection: Validating a two- and four-option multiple choice
question version of the Cognitive Reflection Test. Behavior Research Methods,
50, 2511-2522, doi:10.3758/s13428-018-1029-4. Data: OSF osf.io/mzhyc,
"Data and codebook/MCQCRTdata.csv" (pinned by sha256) and
Codebook_MCQCRTdata.txt.

Licence: OSF node licence "CC-By Attribution 4.0 International".

452 participants x 7 CRT items (the 3 original + 4 from Toplak et al. 2014),
randomly assigned to one of three response formats (XP): 0 = open answer,
1 = 2-option multiple choice, 2 = 4-option multiple choice. The deposit codes
each answer as 1 = correct, 2 = intuitive incorrect, 3 = other incorrect; the
raw typed or chosen answers are not deposited. Three unordered categories, so
the nominal table is the point: it separates the intuitive lure from other
errors, which the 0/1 score collapses.

Mapping
- id        = ID
- item      = CRT1..CRT7 (bat & ball, widgets, lily pads, barrel, class, pig,
              stock market)
- resp      = 1 if the answer was correct (code 1), else 0
- resp_raw  = 1 correct / 2 intuitive incorrect / 3 other incorrect
- cov_format = XP, the response-format condition (0 open, 1 2-option,
              2 4-option). In the 2-option condition the options are the
              correct and the intuitive answer, so code 3 cannot occur.
- cov_age, cov_gender (1 male, 2 female), cov_edu (1-5, codebook)

Dropped: questionnaire time, summed scores and the other scales (PBS, belief
bias, AOT, denominator neglect, numeracy), which are person-level scores, not
items.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "https://osf.io/download/d43sh/"
SHA256 = "3d71dc055397e1f199f8c8934da1342f01f64f28f43caf00e8fc7e5628780e42"
CACHE = Path.home() / ".cache" / "irw-nominal" / "MCQCRTdata.csv"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_csv(CACHE)
items = [f"CRT{i}" for i in range(1, 8)]
assert len(w) == 452 and w["ID"].is_unique
assert w[items].isin([1, 2, 3]).all().all()
## a 2-option item offers only the correct and the intuitive answer
assert not (w.loc[w["XP"] == 1, items] == 3).any().any()

w = w.rename(columns={"ID": "id", "XP": "cov_format", "Age": "cov_age",
                      "Gender": "cov_gender", "Edu": "cov_edu"})
covs = ["cov_format", "cov_age", "cov_gender", "cov_edu"]
df = w.melt(id_vars=["id"] + covs, value_vars=items, var_name="item",
            value_name="resp_raw")
df["resp"] = (df["resp_raw"] == 1).astype(int)
df = df[["id", "item", "resp", "resp_raw"] + covs].sort_values(["id", "item"], kind="stable")

checks = run_qc(df, permitted_values={i: {0, 1} for i in items})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails

df.to_csv("sirota_2018_crt.csv", index=False)
df.rename(columns={"resp_raw": "text"}).to_csv("sirota_2018_crt_nom.csv", index=False)
print(len(df), df["id"].nunique(), df["item"].nunique())
