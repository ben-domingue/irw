#!/usr/bin/env python3
"""ICF-RS-17 functional assessment, Chinese inpatient rehabilitation.

Source: https://peerj.com/articles/20280/
DOI: 10.7717/peerj.20280
Data: PeerJ Supplemental Information 1 (peerj-13-20280-s001.xlsx), fetched
      from Europe PMC's supplementaryFiles endpoint
License: CC BY 4.0 (Crossref; PeerJ publishes under CC BY)

2,574 inpatients at 12 rehabilitation institutions in Nanjing, Wuxi and
Suzhou, each rated on the 17 ICF categories of the ICF-RS-17 at BOTH
admission and discharge -- so the deposit's 34 item columns are 17 items x 2
waves, not 34 items. Shipped as one longitudinal table with `wave`
(1 = admission, 2 = discharge), which is what the repeated id/item pairs mean.

`resp` is the Numerical Rating Scale the paper defines: "a scale of 0 to 10,
where 0 denotes no problem and 10 signifies a complete problem". Note the
direction -- HIGHER IS WORSE functioning. All eleven levels are used and the
file has no missing cells.

`item` is the ICF category code as the source spells it (d450, b455, ...),
with the _admi/_disch suffix moved into `wave`. These are International
Classification of Functioning category codes, so they carry their meaning
across datasets rather than being positional labels.

A known anomaly, shipped as published: 35 rows (16 profiles) are exact
duplicates across all 37 source columns. Two patients matching on all 34
ratings of an 0-10 scale is not a coincidence, and the profiles are not
degenerate -- one repeated three times spans eight distinct values. But the
file has no id column, the paper's own N is 2,574 (it analyses the same rows
we have), and dropping them would silently publish a different sample than
the one the article reports. They are kept, with the duplication recorded in
the dictionary Notes so a user can find and exclude them: the affected ids
are those whose full response profile is identical.

Item text: not shipped in this pass. It is available -- the paper's Tables 3
and 4 name all 17 ICF categories -- but that is `paper_explicit`, not
`data_labels`, so it needs a Step 5b verification script rather than the
cheap gate. Flagged in TODO.md as a cheap follow-up, since the ICF codes
already identify the items unambiguously.
"""
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
TABLE = "li_2025_icf_rs17"
PMCID = "PMC12614094"
MEMBER = "peerj-13-20280-s001.xlsx"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

WAVES = {"_admi": 1, "_disch": 2}
COV_COLS = {"Age": "cov_age", "Gender": "cov_gender", "Hospital": "cov_hospital"}
NRS_MIN, NRS_MAX = 0, 10


def fetch() -> pd.DataFrame:
    r = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=180)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)))


def convert() -> None:
    raw = fetch()
    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)       # the deposit carries no id column

    cov = raw[["id"] + list(COV_COLS)].rename(columns=COV_COLS)
    cov_cols = [c for c in cov.columns if c != "id"]

    frames = []
    for suffix, wave in WAVES.items():
        cols = [c for c in raw.columns if c.endswith(suffix)]
        assert len(cols) == 17, f"expected 17 items at wave {wave}, found {len(cols)}"
        block = raw[["id"] + cols].rename(columns={c: c[: -len(suffix)] for c in cols})
        long = block.melt(id_vars="id", var_name="item", value_name="resp")
        long["wave"] = wave
        frames.append(long)

    # Every source item column is accounted for: 34 = 17 items x 2 waves.
    used = sum(len([c for c in raw.columns if c.endswith(s)]) for s in WAVES)
    unused = [c for c in raw.columns
              if c not in ("id", *COV_COLS) and not c.endswith(tuple(WAVES))]
    assert not unused, f"source columns neither item nor covariate: {unused}"
    assert used == 34, used

    long = pd.concat(frames, ignore_index=True).merge(cov, on="id")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + cov_cols]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    assert long["resp"].between(NRS_MIN, NRS_MAX).all(), "resp outside the 0-10 NRS"
    assert not long.duplicated(["id", "item", "wave"]).any(), "duplicate id/item/wave"
    assert long["id"].nunique() == len(raw) >= 100, "id count changed or below floor"
    assert long["item"].nunique() == 17, "item count changed"
    assert len(long) == len(raw) * 34, "cells lost between source and long form"

    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={long['wave'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
