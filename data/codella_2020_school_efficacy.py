"""Codella et al. (2020), school self-efficacy, gender and motor skills --
PeerJ 8:e8949, CC BY 4.0.

One 12-item school self-efficacy scale, 1-5, with motor-fitness covariates.

Two things about the deposited .xls. Row 0 is a banner, so the real header is
row 1 -- read with `header=0` the whole sheet comes back as `Unnamed: *` and
the item block disappears, which is why upstream triage classified this file as
aggregate rather than item-level. And the LAST data row is not a respondent: it
carries the original ITALIAN wording of each of the 12 items, the English
column headers being a translation. That row is dropped from the responses
here; it is the item text and belongs in the item-text pipeline, not in `resp`.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.7717/peerj.8949"
PMCID = "PMC7195827"
MEMBER = "peerj-08-8949-s002.xls"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE = "codella_2020_school_efficacy"

COV_COLS = {
    "Age (years)": "cov_age",
    "Sex(F/M)": "cov_gender",
    "BMI classes (*)": "cov_bmi_class",
    "6MWT (m)": "cov_6mwt_m",
    "SBJ (cm)": "cov_standing_broad_jump_cm",
    "4x10 (s)": "cov_shuttle_4x10_s",
}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)), header=1)


def convert() -> None:
    raw = fetch()
    item_cols = list(raw.columns[9:21])
    assert len(item_cols) == 12, len(item_cols)

    # Drop the Italian item-text row: it is the only row whose item cells are
    # not numeric.
    numeric = raw[item_cols].apply(pd.to_numeric, errors="coerce")
    raw = raw.loc[numeric.notna().all(axis=1)].reset_index(drop=True)

    raw = raw.rename(columns={"id": "id"})
    present = {s: d for s, d in COV_COLS.items() if s in raw.columns}
    cov = raw[["id"] + list(present)].rename(columns=present)
    cov_cols = [c for c in cov.columns if c != "id"]

    wide = raw[["id"] + item_cols].merge(cov, on="id")
    long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                     var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    # The English item text is the source's column header and is too long to be
    # a table's item id; number the items in source order instead.
    order = {c: f"item_{i}" for i, c in enumerate(item_cols, 1)}
    long["item"] = long["item"].map(order)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    assert long["resp"].between(1, 5).all()
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
