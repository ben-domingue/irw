from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0147753
# DOI: 10.1371/journal.pone.0147753
# Mueller, Riemer, Viranyi, Huber & Range (2016), "Inhibitory Control, but
# Not Prolonged Object-Related Experience Appears to Affect Physical
# Problem-Solving Performance of Pet Dogs". S3 File. CC BY 4.0. N=41 dogs.
# Non-human subjects (dogs), included per IRW's id/item/resp format not
# requiring human respondents -- 3-trial inhibitory-control (cylinder)
# task, 0/1/2 ordinal score per trial. `InhibitionScore` (a derived
# summary, not consistently the raw sum of the 3 trials) not shipped. The
# dataset's other tasks (size-constancy, "on/off", "four-string") are
# single binary/latency outcomes per dog, not multi-item, so not shipped
# here -- see BATCH_LOG.md.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0147753.s007")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch().rename(columns={"ID": "id", "Sex": "cov_sex", "Treatment": "cov_treatment"})
    item_cols = ["Inhibition1", "Inhibition2", "Inhibition3"]
    cov_cols = ["cov_sex", "cov_treatment"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "muller_2016_dog_inhibition.csv"
    long.to_csv(out_path, index=False)
    print(f"muller_2016_dog_inhibition: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
