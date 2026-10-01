"""experimental_iq_nom: nominal companion of core `experimental_iq`.

Source: Open Psychometrics, "Experimental IQ Test" raw data,
http://openpsychometrics.org/_rawdata/IQ1.zip (pinned by sha256), the same
file data/experimental_iq.R scores. Licence as recorded for the core table.

Codebook: 25 matrix items, each with 8 answer tiles; "if Q1 is 4, that means
they chose 4.png ... If it is 10, that means they chose a.png", the correct
tile. 1.png-7.png are the seven wrong tiles; 0 means no answer. The core table
keeps only right/wrong; this one keeps which tile was chosen.

Built from the raw file rather than from the core table, because the core
table dropped the choice. ids and items follow data/experimental_iq.R exactly
(id = row number, item = question number 1-25), and the script asserts that
resp agrees with the published core table row for row.

- text = the tile chosen: "1".."7" (distractors) or "a" (the key, coded 10 in
         the source, written as the codebook's file name so it reads as a
         category rather than a quantity)
- resp = 1 if text == "a", else 0, identical to the core table

Rows with no answer (code 0) are dropped: they carry no choice. The core table
keeps them with resp missing.
"""
import hashlib
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "http://openpsychometrics.org/_rawdata/IQ1.zip"
SHA256 = "99e3a918c0f3452ea25c38788bfa713b34a49f4370529dc0591cc4fc12ec2743"
CACHE = Path.home() / ".cache" / "irw-nominal" / "IQ1.zip"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

with zipfile.ZipFile(CACHE) as z:
    w = pd.read_csv(io.BytesIO(z.read("IQ1/data.csv")))
qs = [f"Q{i}" for i in range(1, 26)]
assert len(w) == 400 and w[qs].isin([0, 1, 2, 3, 4, 5, 6, 7, 10]).all().all()
w.insert(0, "id", range(1, len(w) + 1))

df = w.melt(id_vars="id", value_vars=qs, var_name="item", value_name="code")
df["item"] = df["item"].str[1:].astype(int)
df = df[df["code"] != 0].copy()
df["text"] = df["code"].map(lambda c: "a" if c == 10 else str(c))
df["resp"] = (df["code"] == 10).astype(int)

## must reproduce the published core table
import irw  # noqa: E402
core = pd.DataFrame(irw.fetch("experimental_iq"))
## irw returns pyarrow doubles, where NaN is a value rather than a null, so
## isna() misses it; go through numpy floats
core["resp"] = core["resp"].to_numpy(dtype=float, na_value=float("nan"))
core = core[core["resp"].notna()]
m = df.merge(core, on=["id", "item"], how="outer", suffixes=("", "_core"), indicator=True)
assert (m["_merge"] == "both").all(), m["_merge"].value_counts()
assert (m["resp"] == m["resp_core"]).all()

df = df[["id", "item", "resp", "text"]].sort_values(["id", "item"], kind="stable")
checks = run_qc(df, permitted_values={i: {0, 1} for i in df["item"].unique()})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
df.to_csv("experimental_iq_nom.csv", index=False)
print(len(df), df["id"].nunique(), df["item"].nunique(), df["text"].value_counts().to_dict())
