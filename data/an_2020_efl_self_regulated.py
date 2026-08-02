from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0240094
# DOI: 10.1371/journal.pone.0240094
# An et al. (2020), "Profiling Chinese EFL students' technology-based
# self-regulated English learning strategies". S1 Data. CC BY 4.0. N=525.
# 51-item scale (Q1-Q51), 1-7. The SPSS export kept numeric string codes
# for the middle of the scale (2-6) but exported the two endpoint labels
# as Chinese text mis-decoded as Latin-1 (readable again via
# .encode('latin1').decode('gb18030')): "一点也不符合" (not at all
# matching) = 1, "非常符合" (very much matching) = 7 -- mapped explicitly
# using the raw mis-decoded byte strings as keys. `totalseconds` kept as
# `rt`. Derived composite columns (CET4/totalvalue/enjoyment/MRS/GS/SS/
# TE/Tv/selfperceived/interaction/speaking/listening/reading/writing/SRL)
# not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0240094.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {"·Ç³£·ûºÏ": 7, "Ò»µãÒ²²»·ûºÏ": 1}
# Q51 is not part of the 1-7 Likert battery (values up to 197 observed --
# a different question, e.g. hours/frequency), excluded.
ITEM_COLS = [f"Q{i}" for i in range(1, 51)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"index": "id", "totalseconds": "rt"})


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id", "rt"], value_vars=ITEM_COLS, var_name="item", value_name="resp_raw")
    long["resp"] = pd.to_numeric(long["resp_raw"].astype(str).map(LIKERT_MAP).combine_first(
        pd.to_numeric(long["resp_raw"], errors="coerce")), errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "rt"]]
    out_path = OUT_DIR / "an_2020_efl_self_regulated.csv"
    long.to_csv(out_path, index=False)
    print(f"an_2020_efl_self_regulated: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
