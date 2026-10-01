"""myszkowski_2018_spmls (+ myszkowski_2018_spmls_nom).

Source: Myszkowski, N. & Storme, M. (2018). Data for: A snapshot of g?
Binary and polytomous item-response theory investigations of the last series
of the Standard Progressive Matrices (SPM-LS). Mendeley Data, v1,
doi:10.17632/h3yhs5gy3w.1 (paper: Intelligence 68, 2018,
doi:10.1016/j.intell.2018.03.010). One file, dataset.csv, pinned by sha256.

Licence: CC BY 4.0 (Mendeley API `data_licence`: "You can share, copy and
modify this dataset so long as you give appropriate credit, provide a link to
the CC BY license ...").

The file is 499 rows x SPM1..SPM12, the option each respondent chose (1-8) on
the last series of Raven's SPM. No id column, so id = row number. No missing
values.

Mapping
- item     = SPM1..SPM12
- resp     = 1 if the chosen option is the key, else 0
- resp_raw = the option chosen, 1-8 (7 distractors + the key)

KEY is the SPM-LS key used in the paper. Checked against the data: on every
item the key is the modal choice, and the share choosing it falls across the
series (.76 .91 .80 .82 .86 .76 .70 .58 .57 .39 .36 .32) as an SPM series should.

The nominal companion is the same table with resp_raw renamed to `text`
(datastandard.md, "The raw response and the nominal tranche"). Distractor
choice on this file is the basis of the nested-logit / distractor-IRT
literature on SPM-LS.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = ("https://data.mendeley.com/public-files/datasets/h3yhs5gy3w/files/"
       "96daaa32-c8e9-40f4-b453-ada9cc6320d4/file_downloaded")
SHA256 = "6ec505353613ff41395ab86dda5e4b6344d35ae9aeea3ac974a409ebf76cbb0c"
CACHE = Path.home() / ".cache" / "irw-nominal" / "spmls_dataset.csv"
KEY = [7, 6, 8, 2, 1, 5, 1, 6, 3, 2, 4, 5]

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    ## Mendeley refuses urllib's default user agent (403)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_csv(CACHE)
items = [f"SPM{i}" for i in range(1, 13)]
assert list(w.columns) == items and len(w) == 499 and not w.isna().any().any()
w.insert(0, "id", range(1, len(w) + 1))

df = w.melt(id_vars="id", value_vars=items, var_name="item", value_name="resp_raw")
key = dict(zip(items, KEY))
df["resp"] = (df["resp_raw"] == df["item"].map(key)).astype(int)
df = df[["id", "item", "resp", "resp_raw"]].sort_values(["id", "item"], kind="stable")

## the key must be each item's modal choice (see docstring)
mode = df.groupby("item")["resp_raw"].agg(lambda s: s.value_counts().index[0])
assert all(mode[i] == key[i] for i in items)

checks = run_qc(df, permitted_values={i: {0, 1} for i in items})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails

df.to_csv("myszkowski_2018_spmls.csv", index=False)
df.rename(columns={"resp_raw": "text"}).to_csv("myszkowski_2018_spmls_nom.csv", index=False)
print(len(df), df["id"].nunique(), df["item"].nunique())
