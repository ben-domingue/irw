"""treglown_2016_burnout, treglown_2016_rs14.

Source: Treglown, L., Palaiou, K., Zarola, A., & Furnham, A. (2016). The Dark
Side of Resilience and Burnout: A Moderation-Mediation Model. PLOS ONE, 11(6),
e0156279, doi:10.1371/journal.pone.0156279. Data: figshare
doi:10.6084/m9.figshare.3413665, "PlosOne SPSS File.sav" (pinned by sha256).

Licence: figshare record "CC BY 4.0".

451 employees of a UK organisation, assessed in a selection and development
programme:
- BOUT1..6  Copenhagen Burnout Inventory, work-related burnout scale, 1-5.
            The deposit holds item 4 only as BOUT4REC, i.e. already
            reverse-scored; the item is shipped under that name so the
            recoding is visible. The other five are as administered.
- RES1..14  Resilience Scale-14 (Wagnild), 1-7.

Not shipped: the eleven Hogan Development Survey columns, which are scale
scores rather than items, and the totals, factor scores and z-scored
interaction terms. No demographics are deposited.

id = row number (the deposit has no id column). No missing or fractional
item values.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "https://ndownloader.figshare.com/files/5343973"
SHA256 = "6c92c552c4ce018314695d32999939f8e92bf88074daae48cc0f1729652dc4ae"
CACHE = Path.home() / ".cache" / "irw-plos" / "treglown_2016.sav"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

w = pd.read_spss(CACHE, convert_categoricals=False)
assert len(w) == 451
w.insert(0, "id", range(1, len(w) + 1))

SCALES = {
    "treglown_2016_burnout": (["BOUT1", "BOUT2", "BOUT3", "BOUT4REC", "BOUT5", "BOUT6"], 1, 5),
    "treglown_2016_rs14": ([f"RES{i}" for i in range(1, 15)], 1, 7),
}
for table, (items, lo, hi) in SCALES.items():
    df = w.melt(id_vars=["id"], value_vars=items, var_name="item", value_name="resp")
    df = df.dropna(subset=["resp"])
    assert (df["resp"] % 1 == 0).all() and df["resp"].between(lo, hi).all(), table
    df["resp"] = df["resp"].astype(int)
    df = df.sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values={i: set(range(lo, hi + 1)) for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    df.to_csv(f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
