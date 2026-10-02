"""geography_nom: nominal companion of core `geography` (#2658).

Source: slepemapy.cz adaptive geography practice data, 2015-05-21 dump,
https://www.fi.muni.cz/adaptivelearning/data/slepemapy/2015-05-21.zip (pinned by
sha256) -> answer.csv, place.csv, place_type.csv. Papousek, Pelanek &
Stanislav (2016), Journal of Learning Analytics 3(2), 317-321,
doi:10.18608/jla.2016.32.17. The same file data/geography.R builds the core
table from (10,087,305 answers, 91,331 users, 1,458 places asked).

Licence: README "Open Database License"; contents under the Database
Contents License.

Built from the raw file because data/geography.R drops `place_answered`, the
place the learner chose. The core table is NOT rebuilt here: its own repairs
(restore `inserted` as date, NA the rt sentinel) are queued in #2558, which is
part of the paused corpus audit. This table carries both repairs itself.

Mapping
- id    = user
- item  = place_asked (as in the core table's `item`)
- resp  = 1 if place_answered == place_asked, 0 if another place, and missing
          for "I don't know": the same values data/geography.R produces (R's
          `==` against NA)
- text  = place_answered (place id), or "dont_know" for "I don't know"
          (281,706 answers): a choice the system offered, so kept as a category
- rt    = response_time / 1000 (seconds). Values >= 2,147,483,647 ms are set
          missing (64,651): 64,131 sit exactly at the INT32 maximum, a logging
          sentinel, and 520 just under the UINT32 maximum, which reads as a
          negative duration wrapped around. 2,654 values between 1 hour and
          the sentinel are left as recorded.
- date  = inserted as Unix seconds (UTC assumed; the source gives no zone)
- itemcov_place_name, itemcov_place_type = the asked place's name and type
          (country, city, river, ...) from place.csv / place_type.csv, so the
          ids in `item` and `text` stay readable
- trial_type    = 1 find the named place on the map, 2 name the highlighted place
- trial_options = the option ids offered, "."-separated, the asked place
                  included; blank for open questions (no option list, 6.87M
                  answers), where any place on the map could be chosen
- trial_map     = place_map, the map the question was asked on

Repeated id-item rows are real: the system re-asks places adaptively, and
`date` orders them. Dropped: ip_country, ip_id (not needed and closer to
identifying), and `language`, which the README does not document.
"""
import hashlib
import sys
import zipfile
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "https://www.fi.muni.cz/adaptivelearning/data/slepemapy/2015-05-21.zip"
SHA256 = "3fd3f49bb231d2d0e1e3c8f672ffff5e8f27a1dda944cb396aa3fb9d81be6edf"
CACHE = Path.home() / ".cache" / "irw-nominal" / "geography" / "slepemapy_2015-05-21.zip"
RT_SENTINEL = 2147483647

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r, open(CACHE, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
h = hashlib.sha256()
with open(CACHE, "rb") as f:
    while chunk := f.read(1 << 20):
        h.update(chunk)
assert h.hexdigest() == SHA256

with zipfile.ZipFile(CACHE) as z:
    with z.open("answer.csv") as f:
        d = pd.read_csv(f, sep=";", low_memory=False,
                        usecols=["user", "place_asked", "place_answered", "type",
                                 "inserted", "response_time", "place_map", "options"],
                        dtype={"place_answered": "Int64", "place_map": "Int64"})
    with z.open("place.csv") as f:
        place = pd.read_csv(f, sep=";")
    with z.open("place_type.csv") as f:
        ptype = pd.read_csv(f, sep=";")
assert len(d) == 10087305 and d["user"].nunique() == 91331

dk = d["place_answered"].isna()
resp = pd.Series(np.where(dk, np.nan, (d["place_answered"] == d["place_asked"]).astype(float)))
opts = d["options"].fillna("[]").str.strip("[]").str.replace(", ", ".", regex=False)

pname = place.set_index("id")["name"]
ptyp = place.set_index("id")["type"].map(ptype.set_index("id")["name"])

df = pd.DataFrame({
    "id": d["user"],
    "item": d["place_asked"],
    "resp": resp.astype("Int64"),
    "text": d["place_answered"].astype(str).where(~dk, "dont_know"),
    "rt": np.where(d["response_time"] >= RT_SENTINEL, np.nan, d["response_time"] / 1000),
    "date": (pd.to_datetime(d["inserted"], utc=True)
             - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s"),
    "itemcov_place_name": d["place_asked"].map(pname),
    "itemcov_place_type": d["place_asked"].map(ptyp),
    "trial_type": d["type"],
    "trial_options": opts,
    "trial_map": d["place_map"],
})
del d
assert int(dk.sum()) == 281706 and int(np.isnan(df["rt"]).sum()) == 64651
assert df["itemcov_place_name"].notna().all() and df["itemcov_place_type"].notna().all()
## 2012-2015 in Unix seconds
assert df["date"].between(1325376000, 1435708800).all()
df = df.sort_values(["id", "date"], kind="stable")

checks = run_qc(df.drop(columns=["text"]),
                permitted_values={i: {0, 1} for i in df["item"].unique()})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails

df.to_csv("geography_nom.csv", index=False)
print(len(df), df["id"].nunique(), df["item"].nunique(), df["text"].nunique())
