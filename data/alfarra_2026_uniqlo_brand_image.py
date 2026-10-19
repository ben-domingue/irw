#!/usr/bin/env python3
# Source: https://zenodo.org/records/20783961
# DOI: none recorded on the deposit (no related identifiers).
#   Alfarra, M., Samsul Bahri, & Ronny (2026). "Research Questionnaire - The
#   Mediating Role of e-WOM in the Relationship Between Product Quality,
#   e-Content Marketing, and Brand Image: Evidence from Fashion Industry
#   Generation Z Consumers in Indonesia." Zenodo.
# Data: Zenodo 20783961, "Research Questionnaire - Analysis of the Influence
#       of Product Quality, e-Content Marketing and e-WOM in Uniqlo's App to
#       Brand Image (Responses).xlsx", sheet 'Form responses 1' (300 rows x
#       27 columns; Indonesian Generation Z UNIQLO app users).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: NOT shipped, and this is a rights-and-schema call rather than a
#   missing source -- the text is fully in hand. The Google Form export's own
#   column headers ARE the item stems, each ending in its own code ("Produk
#   UNIQLO memiliki kinerja yang baik sesuai fungsinya. (PQ1)"), so the
#   code-to-wording tie is the source's own and a later pass can parse it in
#   one line with CODE_RE below. What stops it here: the administration is
#   Indonesian, and itemtext_standard.md requires the administered wording in
#   the base fields WITH the English in the parallel _translated fields. The
#   authors ship no English version, so that English would be IRW-generated,
#   which needs a translation_source and a public issues-page callout per
#   table (check_provenance.R). Eight deposits in this batch are in the same
#   position; they belong in one deliberate translation round, not bolted on
#   to a response batch. These are the authors' own marketing-construct items
#   (product quality, e-content marketing, e-WOM, brand image), not a named
#   third-party instrument, so no register entry blocks them.
#
# Tables:
#   alfarra_2026_uniqlo_brand_image  21 items, codes PQ1-PQ5, ECM1-ECM5,
#       EWOM1-EWOM6, BI1-BI5 as printed in the headers, 1-5 Likert.
#       One table: one matrix question, one response format; the four
#       prefixes are the paper's constructs and run_qc's multi_scale warning
#       is expected.
#
# Dropped, with reasons:
#   Timestamp  form submission time, not a response
#   "Apakah Anda pernah membeli produk UNIQLO?"  screening question (all Ya)
#   4 demographics -> cov_*
# id: row index + 1 (the export carries no respondent identifier).
# Covariates: cov_gender, cov_age_band, cov_domicile, cov_income_band
#   (Indonesian text as given).

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
DATA_URL = ("https://zenodo.org/api/records/20783961/files/"
            "Research%20Questionnaire%20-%20Analysis%20of%20the%20Influence"
            "%20of%20Product%20Quality%2C%20e-Content%20Marketing%20and%20"
            "e-WOM%20in%20Uniqlo%E2%80%99s%20App%20to%20Brand%20Image%20"
            "%28Responses%29.xlsx/content")
TABLE = "alfarra_2026_uniqlo_brand_image"
ALLOWED = {1, 2, 3, 4, 5}
CODE_RE = re.compile(r"\(([A-Z]{2,4}\d{1,2})\)\s*$")

COVS = {"Jenis Kelamin": "cov_gender", "Usia": "cov_age_band",
        "Domisili": "cov_domicile", "Pendapatan per Bulan": "cov_income_band"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Form responses 1")
    assert d.shape == (300, 27), d.shape
    d.columns = [str(c) for c in d.columns]

    # The item columns are exactly those whose header ends in a (CODE).
    stems, items = {}, []
    for c in d.columns:
        mm = CODE_RE.search(c)
        if mm:
            code = mm.group(1)
            stems[code] = CODE_RE.sub("", c).strip().rstrip(".").strip()
            items.append((c, code))
    codes = [c for _, c in items]
    assert len(set(codes)) == len(codes), "duplicate item code in headers"
    assert len(codes) == 21, len(codes)

    covmap = {}
    for c in d.columns:
        key = c.strip()
        if key in COVS:
            covmap[c] = COVS[key]
    assert len(covmap) == 4, sorted(covmap.values())

    known = {c for c, _ in items} | set(covmap)
    for c in d.columns:
        if c not in known:
            print(f"[drop] {c[:70]}")
    print(f"[cols] {len(codes)} items, {len(covmap)} covariates, "
          f"{d.shape[1] - len(known)} dropped")

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    sub = d[["id"] + list(covmap) + [c for c, _ in items]].rename(
        columns={**covmap, **{c: k for c, k in items}})
    cov_cols = sorted(set(covmap.values()))
    for c in cov_cols:
        sub[c] = sub[c].astype(str).str.strip().replace({"nan": pd.NA})

    long = sub.melt(id_vars=["id"] + cov_cols, value_vars=codes,
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
    assert long["item"].nunique() == 21

    checks = run_qc(long, permitted_values={c: ALLOWED for c in codes})
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
