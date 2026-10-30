#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0309953
# DOI: 10.1371/journal.pone.0309953
# Paper: Lin, C., Xue, X., Zhu, Z., Luo, Y., & Song, R. (2024). Factors related
#   to the intention of choosing shared E-scooters for metro transfer: A survey
#   study integrating weather perception into satisfaction evaluation from
#   Changsha. PLOS ONE 19(9).
# Data: journal.pone.0309953.s001 (S1 Data, .xlsx), 683 rows x 46 columns.
#   A second SI file (S1 File) holds the questionnaire and is not data.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
# 683 respondents surveyed at Changsha metro stations, 24-25 June 2021.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# EIGHT output tables, one per latent construct. The paper's measurement model
# names all eight and the deposit's column prefixes match them one-for-one, so
# unlike several deposits in this batch the construct boundaries here are
# documented rather than inferred:
#   COU  5 items  Convenience of use
#   SAF  5 items  Perceived safety
#   COM  4 items  Comfort
#   TRA  5 items  Ease of transfer
#   PEOU 5 items  Perceived ease of use
#   WEA  4 items  Weather preference -- "different respondents' tolerance to
#                 four weather conditions: haze, light rain, heat, and cold"
#   SAT  4 items  User satisfaction
#   LOF  4 items  User loyalty
# 36 items in all, every one on the paper's single "five-point Likert scale".
#
# These are EIGHT TABLES RATHER THAN ONE because they are eight distinct
# reflective constructs in one structural model, not subscales of a single
# instrument -- the same call made for rosman_2022_* and kendall_2018_* in this
# batch, and the opposite of the call made for
# padchasuwan_2026_sexual_health_literacy and
# oppong_2026_procurement_literacy, where the blocks were dimensions of one
# named instrument. The distinction that decides it: here the paper treats COU,
# SAF, COM and TRA as four second-order latent variables feeding Perceived
# Usefulness, with PEOU, WEA, SAT and LOF as separate constructs in the path
# model -- i.e. the study itself does not treat them as one scale.
#
# Clean source, verified rather than assumed: zero missing cells across all 36
# items and every item's observed domain is exactly 1-5, so there is no
# undeclared no-answer code to strip.
#
# THE NINE DEMOGRAPHIC COLUMNS ARE DROPPED, and that is a real loss stated
# plainly rather than papered over. The deposit names them `1` through `9` --
# bare integers, with no codebook and no mapping in the article. Their value
# distributions are suggestive (column `1` splits 353/330, which looks like
# gender) but suggestive is not documented, and this batch already set the
# rule against inventing covariate semantics when it dropped
# lin_2026_advertising_literacy's No2/No4/No5. So these eight tables carry no
# covariates at all. If the S1 File questionnaire is ever transcribed, the
# mapping is recoverable and the tables can be re-shipped with them.
#
# `id` is the deposit's own ID, verified unique across all 683 rows.
#
# Item text: NOT SHIPPED, though this is the closest call in the batch. The
# companion S1 File is the questionnaire, so the wording very likely exists in
# the deposit, and the article quotes fragments of several items verbatim
# ("wide enough bike lanes", "shaded paths", "willingness to recommend to
# others", "more convenient than bus transfers"). But quoted fragments are not
# a stem list and they cannot be attached to a numbered column code, and the
# instrument is assembled from the TAM and SERVQUAL literatures rather than
# study-authored. Queued in TODO.md as a candidate: transcribing the S1 File
# questionnaire would plausibly yield all 36 stems with their construct
# labels, which is a real extraction job rather than a rights problem.
#
# PII: screened over all 46 columns. Every one is numeric; no names, emails,
# dates, free text, or geography. (Changsha is the study site, named only in
# the paper.)

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LIN_SE_RAW", "journal.pone.0309953_S1_Data.xlsx")

N_ROWS = 683
LO, HI = 1, 5

# prefix -> (table name, expected item count, construct label from the paper)
CONSTRUCTS = {
    "COU": ("lin_2024_escooter_convenience", 5, "Convenience of use"),
    "SAF": ("lin_2024_escooter_safety", 5, "Perceived safety"),
    "COM": ("lin_2024_escooter_comfort", 4, "Comfort"),
    "TRA": ("lin_2024_escooter_transfer_ease", 5, "Ease of transfer"),
    "PEOU": ("lin_2024_escooter_ease_of_use", 5, "Perceived ease of use"),
    "WEA": ("lin_2024_escooter_weather_tolerance", 4, "Weather preference"),
    "SAT": ("lin_2024_escooter_satisfaction", 4, "User satisfaction"),
    "LOF": ("lin_2024_escooter_loyalty", 4, "User loyalty"),
}


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt, f"unexpected text column(s) -- screen them: {txt}"
    print("  every column is numeric; no name, email, date, free text or "
          "geographic column (Changsha is named only in the paper)")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    found = {}
    for c in df.columns:
        m = re.match(r"^([A-Z]+)(\d+)$", str(c))
        if m and m.group(1) in CONSTRUCTS:
            found.setdefault(m.group(1), []).append(c)
    got = {k: len(v) for k, v in found.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"construct counts are {got}, expected {want}"

    # the nine demographic columns are named with bare integers; dropped
    demog = [c for c in df.columns if isinstance(c, int) or str(c).isdigit()]
    assert len(demog) == 9, f"expected 9 bare-integer demographic columns, got {demog}"
    accounted = set(demog) | {"ID"}
    for cols in found.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"dropped {len(demog)} demographic columns named with bare integers "
          f"({demog[:4]}...): no codebook and no mapping in the article, so "
          f"these tables carry no covariates (see header)")

    assert df["ID"].nunique() == len(df), "ID is not unique"
    df = df.rename(columns={"ID": "id"})

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    written = set()
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(found[prefix], key=lambda c: int(re.sub(r"\D", "", str(c))))
        assert name not in written and len(name) <= 40, name
        written.add(name)

        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"], value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()

        long = long[["id", "item", "resp"]]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 36 * N_ROWS, total
    print(f"8 tables, {total} responses (36 items x {N_ROWS} respondents, "
          f"no missing cells)")


if __name__ == "__main__":
    convert()
