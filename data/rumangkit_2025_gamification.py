#!/usr/bin/env python3
# Source: https://zenodo.org/records/17628395
# DOI: none recorded on the deposit (no related identifiers).
#   Rumangkit, S. (2025). "247_Dataset_2025." Zenodo.
# Data: Zenodo 17628395, "247_Dataset_2025.xlsx", sheet 'Form Responses 1'
#       (279 respondents x 24 items; Indonesian e-commerce users asked about
#       in-app gamification features -- Shopee Games, Tokopedia Seru, etc.).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# HEADER OFFSET: row 0 is a merged construct banner (Perceived Enjoyment,
#   Percieved Playfulness, Perceived Usefulness, Customer Engagement, Brand
#   Awareness, Customer Loyalty) and row 1 holds the real headers, which are
#   the item codes: PE1-PE4, PP1-PP5, PU1-PU4, CE1-CE5, BA1-BA3, CL1-CL3 --
#   24 in all. So the file is read with header=1; read with the default
#   header=0 every column comes back 'Unnamed: N' and the codes are lost.
#   The codes are matched by pattern rather than hardcoded, because the
#   block sizes are not the regular 4-per-construct they look like (CE has
#   five items, CL three) and one header is typed "CE2." with a trailing
#   full stop, normalised here to CE2. Columns 28-32 are empty padding with
#   a stray repeated banner and carry no data.
#
# Item text: NOT shipped. The deposit holds this one spreadsheet, and its
#   header rows carry the construct names and the item CODES but no item
#   stems -- the wording was in the Google Form, which is not deposited, and
#   the record carries no paper DOI to reach it through. So unlike the other
#   Rumangkit deposits in this batch, here the text is genuinely absent from
#   the source rather than untranslated: a positional code with no stem
#   anywhere in the deposit. That is where the text is (or is not).
#
# Tables:
#   rumangkit_2025_gamification  24 items, the source's own codes, 1-5.
#       One table: one matrix question on one response format; the six
#       prefixes are the paper's constructs, so run_qc's multi_scale warning
#       is expected.
#
# Dropped, with reasons:
#   Nomor                        respondent number -> becomes `id`
#   "Apakah Anda pernah menggunakan fitur permainan ..."  screening question
#   Jenis kelamin, Usia          -> cov_*
# id: the file's own 'Nomor' column.
# Covariates: cov_gender, cov_age_band (Indonesian text as given).

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://zenodo.org/api/records/17628395/files/"
            "247_Dataset_2025.xlsx/content")
TABLE = "rumangkit_2025_gamification"
ALLOWED = {1, 2, 3, 4, 5}
ITEM_RE = re.compile(r"^(PE|PP|PU|CE|BA|CL)(\d{1,2})\.?$")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Form Responses 1",
                      header=1)
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape[0] == 279, d.shape

    ren = {}
    for c in d.columns:
        mm = ITEM_RE.match(c)
        if mm:
            ren[c] = f"{mm.group(1)}{int(mm.group(2))}"
    assert len(set(ren.values())) == len(ren), "item code collision"
    assert len(ren) == 24, sorted(ren.values())
    d = d.rename(columns=ren)
    present = list(ren.values())
    # Balance the books: every column is an item, the id, a covariate or a
    # printed drop.
    idcol = "Nomor"
    covmap = {}
    for c in d.columns:
        if c.lower().startswith("jenis kelamin"):
            covmap[c] = "cov_gender"
        elif c.lower().startswith("usia"):
            covmap[c] = "cov_age_band"
    assert idcol in d.columns and len(covmap) == 2, (idcol, covmap)
    known = set(present) | set(covmap) | {idcol}
    for c in d.columns:
        if c not in known:
            print(f"[drop] {c[:70]}")
    print(f"[cols] {len(present)} items, {len(covmap)} covariates, "
          f"{len(d.columns) - len(known)} dropped")

    d = d.rename(columns={idcol: "id", **covmap})
    d = d[d["id"].notna()].copy()
    d["id"] = pd.to_numeric(d["id"], errors="raise").astype(int)
    assert d["id"].is_unique
    cov_cols = ["cov_gender", "cov_age_band"]
    for c in cov_cols:
        d[c] = d[c].astype(str).str.strip().replace({"nan": pd.NA})

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=present,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["item"].nunique() == len(present)

    checks = run_qc(long, permitted_values={c: ALLOWED for c in present})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
