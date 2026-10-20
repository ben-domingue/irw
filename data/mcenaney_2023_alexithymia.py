#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/alexithymia_emotional_vocabulary_McEnaney_Ryan_xlsx/21747236
# DOI: 10.6084/m9.figshare.21747236.v2
#   McEnaney, E., & Ryan, C. (2023). alexithymia_measurement_emotional
#   vocabulary.xlsx [Dataset]. figshare, v2, published 2023-02-03.
# Data: "alexithymia_measurement_emotional vocabulary_dataset.xlsx", sheet
#   "Data" -- 366 participants in an online study of alexithymia, emotional
#   vocabulary use, verbal IQ and autistic traits. The workbook's second
#   sheet, "Dictionary", documents all 35 variable groups and is what
#   identifies the instruments below.
# License: CC BY 4.0 (verified on the figshare article record via
#   api.figshare.com/v2/articles/21747236, 2026-10-20).
#
# Item text: NOT shipped, for any of the three tables. The source gives no
#   stems at either available level: this is an .xlsx, so there is no
#   variable-label or value-label level at all, and the "Dictionary" sheet --
#   the one place wording could have been -- carries only positional
#   descriptors ("Wordsum score item 1", "Autism Spectrum Quotient (AQ-10)
#   score item 1", "Bermond-Vorst Alexithymia Questionnaire-B (BVAQ-B) score
#   item 1"). So the dictionary identifies the INSTRUMENT but never quotes an
#   item. All three are published third-party instruments, which is where the
#   wording lives and also what each would need a rights ruling for:
#   Checked by NAME against itemtext/instrument_rights_register.csv, not just
#   by running the gate -- which matters here, because the two checks
#   disagree:
#     - Wordsum (the GSS/NORC ten-word vocabulary test) is registered
#       "GSS Wordsum vocabulary test (10 items)", verdict BLOCK. The gate did
#       NOT warn on it: its match_item_code pattern cannot match this
#       deposit's codes `ws1`..`ws10`. This is the documented failure mode --
#       the register's patterns miss freely -- and running the gate alone
#       would have missed a live prohibition.
#     - AQ-10 is registered "Autism Spectrum Quotient (AQ-50, AQ-28, AQ-10),
#       Autism Research Centre, University of Cambridge, incl. translations",
#       verdict BLOCK. The gate DID warn here, matching all ten `aq*` codes.
#       Note what the warning says and does not say: response data from a
#       blocked instrument can ship, its wording cannot. That is why the
#       aq10 table below is written and only its item text is withheld.
#     - BVAQ-B (Bermond & Vorst's Alexithymia Questionnaire, form B) has NO
#       row at all. The only alexithymia row is the Toronto Alexithymia Scale
#       (TAS-20, block), which is a different instrument. So nothing would
#       have warned for BVAQ-B, and silence does not ship: it needs a row
#       written, verdict included, before its wording is ever extracted.
#   In all three cases the item codes are the source's own column names
#   rather than item wording, so the gate's advice to rename codes before
#   publication does not apply and nothing here needs renaming.
#
# THREE tables -- three separate published instruments, three different
# response formats, all administered to the same 366 respondents, so `id` is
# shared and a user can join across them:
#   mcenaney_2023_wordsum -- 10 vocabulary items, scored 0/1
#   mcenaney_2023_aq10    -- 10 AQ-10 items, scored 0/1
#   mcenaney_2023_bvaq    -- 20 BVAQ-B items, 1-5
# They are NOT merged: the same-instrument merge rule is about one instrument
# given to several samples, which is the opposite case.
#
# NOT shipped -- the APRQ, deliberately:
#   aprq1..aprq17 are the Alexithymia Provoked Response Questionnaire's
#   open-ended answers, stored as the participant's own free text ("Angry but
#   determined to prove my innocence", "Betrayed by the system that is there
#   to protect me"), with 205-292 distinct strings per column. Free text is
#   not a response value -- it is not numeric and carries no ordering -- so
#   it cannot be `resp`, and there is no per-item score in the file to put
#   there instead. The deposit does ship APRQ TOTALS (author_1, author_2 and
#   computer_score, the two authors' hand scores and a lexicon-based
#   computer score), but those are whole-instrument composites, not item
#   responses, so they are dropped rather than reshaped.
#
# Dropped as composites, not responses: ws (Wordsum total), aq (AQ-10 total),
#   bvaq (BVAQ-B total), the five BVAQ facet scores (bvaq_verb, bvaq_fant,
#   bvaq_iden, bvaq_emo, bvaq_ana) and the two BVAQ higher-order scores
#   (bvaq_cog, bvaq_aff), plus the three APRQ totals named above.
#
# id: the deposit's own "id" column, documented in the Dictionary sheet as
#   "Unique identifier for each participant". 366 unique values over 366
#   rows, a study-assigned sequence, not PII.
#
# Covariates: the deposit's six demographics, carried on all three tables.
#   `residence` is free-typed and the raw values collide on whitespace and
#   case ("Ireland", "Ireland ", "ireland"; "Australia", "Australia "), so it
#   is whitespace-stripped and title-cased, which collapses 28 raw strings to
#   the ~24 distinct countries actually present. PNTA ("prefer not to
#   answer") is kept as its own category rather than nulled, because it is a
#   real answer the form offered.
#
# PII: none, and the free text was checked rather than assumed. The screen
#   selects text columns with pd.api.types.is_string_dtype -- never
#   dtype == object -- and prints the denominator, asserted non-zero, so an
#   empty selection cannot report clean; it finds 22 string columns.
#   Structurally there is no column whose job is to collect an identifier:
#   no name, email, phone, date of birth, address or national ID field
#   exists. `residence` is COUNTRY-level ("Ireland", "United States of
#   America", "The Philippines") -- it is not a postal code and does not
#   approach the block-level re-identification surface that made full
#   Canadian postal codes structural in the 2026-10-19 ruling. The 17
#   free-text APRQ columns are the one place an incidental identifier could
#   hide, so all 186,669 characters of them were regex-scanned for email
#   addresses, phone-shaped digit runs and UK postcodes: zero hits of any
#   kind. They are emotion words and short phrases about hypothetical
#   scenarios. Nothing had to be nulled, and in any case none of those
#   columns reaches the output.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s5"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare" / "21747236"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE = 21747236
FNAME = "alexithymia_measurement_emotional vocabulary_dataset.xlsx"

COVS = {"age": "cov_age", "gender": "cov_gender",
        "nationality": "cov_nationality", "residence": "cov_residence",
        "education": "cov_education", "occupation": "cov_occupation"}

# table -> (source item columns, permitted resp values)
TABLES = {
    "mcenaney_2023_wordsum": ([f"ws{i}" for i in range(1, 11)], {0, 1}),
    "mcenaney_2023_aq10": ([f"aq{i}" for i in range(1, 11)], {0, 1}),
    "mcenaney_2023_bvaq": ([f"bvaq{i}" for i in range(1, 21)],
                           set(range(1, 6))),
}
APRQ = [f"aprq{i}" for i in range(1, 18)]
N_RESP = 366


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        meta = requests.get(
            f"https://api.figshare.com/v2/articles/{ARTICLE}",
            headers=UA, timeout=120).json()
        url = next(f["download_url"] for f in meta["files"]
                   if f["name"] == FNAME)
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    path = fetch()
    df = pd.read_excel(path, sheet_name="Data")
    assert len(df) == N_RESP, len(df)
    assert df["id"].nunique() == N_RESP, "id is not unique per respondent"

    # PII screen -- denominator printed, and the free text content-checked.
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] columns examined: {len(df.columns)} total, "
          f"{len(text_cols)} string-dtype")
    assert len(text_cols) > 0, "PII screen selected no columns"
    import re
    blob = " || ".join(df[APRQ].astype(str).stack().tolist())
    hits = {
        "email": re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", blob),
        "phone": re.findall(r"\b\d{3}[- ]?\d{3,4}[- ]?\d{3,4}\b", blob),
        "uk_postcode": re.findall(r"\b[A-Z]{1,2}\d[\dA-Z]?\s?\d[A-Z]{2}\b",
                                  blob),
    }
    print(f"[pii] free text scanned: {len(blob)} chars over {len(APRQ)} "
          f"columns; " + ", ".join(f"{k}={len(v)}" for k, v in hits.items()))
    assert not any(hits.values()), f"identifier found in APRQ free text: {hits}"

    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())
    df["cov_residence"] = (df["cov_residence"].astype(str)
                           .str.strip().str.title())

    for table, (items, scale) in TABLES.items():
        missing = [c for c in items if c not in df.columns]
        assert not missing, missing
        t = (df[["id", *cov_cols, *items]]
             .melt(id_vars=["id", *cov_cols], value_vars=items,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        assert len(t) == N_RESP * len(items), (table, len(t))
        assert (t["resp"] % 1 == 0).all(), f"{table}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{table}: resp outside {sorted(scale)}: {bad}"

        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), f"{table}: dup id/item"
        assert t["id"].nunique() == N_RESP
        assert t["item"].nunique() == len(items)

        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {table} {c.name}: {c.detail[:150]}")
        report = irw_validate.validate_frame(
            t, label=table, profile="upload",
            context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (table, [(f.check, f.message) for f in report.errors])

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        t.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
