"""vanhoef_2024_picture_naming (+ vanhoef_2024_picture_naming_nom).

Source: van Hoef, R., Lynott, D. & Connell, L. (2024). Timed picture naming
norms for 800 photographs of 200 objects in English. Behavior Research
Methods, 56, 6655-6672, doi:10.3758/s13428-024-02380-w. Data: OSF osf.io/r3hbz,
"2 - BRM - data and analysis/The Norms/
van_Hoef_et_al_picture_naming_trial_level_data.csv" (pinned by sha256).

Licence: OSF node licence "CC-By Attribution 4.0 International". The
photographs themselves carry their own credits and are not redistributed here;
only the typed names are.

60 participants each typed a name for 200-800 photographs (25,850 trials);
each of the 200 objects has 4 photographs. Picture naming has no key: the
measurement object is which name a person produces, so the nominal table (the
name) is the primary one, and the score is name agreement.

Mapping
- id         = ppn
- item       = image (800)
- resp       = is_modal: 1 if the name given is the image's modal name, else 0.
               The 579 trials the authors flag is_invalid (almost all "dk",
               don't know, plus keyboard slips such as "sk") have no is_modal
               and are scored 0: no name was produced.
- resp_raw   = the name, as the authors corrected it for spelling
               (response_corrected: "brocolli" -> "broccoli"), so misspellings
               do not split a category. The authors did not correct the 1,485
               RT-outlier trials, so for those the name is as typed.
- rt         = recognition_RT / 1000: seconds from image onset to the
               spacebar press that signalled the object was recognised.
- item_family = object (the 4 photographs of one object)
- trial_response_typed = response, the name exactly as typed
- trial_invalid, trial_rt_outlier = the authors' flags (0/1)
- itemcov_is_natural = is_natural (0 artefact, 1 natural kind), per object

Dropped: the image-level norms repeated on every row (name agreement, H, word
frequencies and lengths), which are derived from these responses, and
first_key_RT, whose unit the README does not give.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "https://osf.io/download/hp7d2/"
SHA256 = "5bbda4a2075aac7d00d1b68d1b1df645269ac90bfc7545f372f314585ab75235"
CACHE = Path.home() / ".cache" / "irw-nominal" / "pn_trials.csv"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

d = pd.read_csv(CACHE)
assert len(d) == 25850 and d["ppn"].nunique() == 60 and d["image"].nunique() == 800
assert not d.duplicated(["ppn", "image"]).any()
## is_modal is missing exactly on the invalid trials
assert (d["is_modal"].isna() == (d["is_invalid"] == 1)).all()

name = d["response_corrected"].where(d["response_corrected"].notna(), d["response"])
df = pd.DataFrame({
    "id": d["ppn"].str.replace("ppt_", "", regex=False).astype(int),
    "item": d["image"].str.replace(r"\.png$", "", regex=True),
    "resp": d["is_modal"].fillna(0).astype(int),
    "resp_raw": name.str.strip(),
    "rt": d["recognition_RT"] / 1000,
    "itemcov_is_natural": d.groupby("object")["is_natural"].transform("max"),
    "item_family": d["object"],
    "trial_response_typed": d["response"],
    "trial_invalid": d["is_invalid"],
    "trial_rt_outlier": d["is_rt_outlier"],
})
## one response is empty in the source; it is an invalid trial, scored 0
df["resp_raw"] = df["resp_raw"].fillna("")
assert df["itemcov_is_natural"].notna().all()
df["itemcov_is_natural"] = df["itemcov_is_natural"].astype(int)
assert (df.groupby("item")["item_family"].nunique() == 1).all()
assert np.isfinite(df["rt"]).all() and (df["rt"] > 0).all()

cols = ["id", "item", "resp", "resp_raw", "rt", "itemcov_is_natural",
        "item_family", "trial_response_typed", "trial_invalid", "trial_rt_outlier"]
df = df[cols].sort_values(["id", "item"], kind="stable")

checks = run_qc(df, permitted_values={i: {0, 1} for i in df["item"].unique()})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails

df.to_csv("vanhoef_2024_picture_naming.csv", index=False)
df.rename(columns={"resp_raw": "text"}).to_csv("vanhoef_2024_picture_naming_nom.csv", index=False)
print(len(df), df["id"].nunique(), df["item"].nunique(), df["resp_raw"].nunique())
