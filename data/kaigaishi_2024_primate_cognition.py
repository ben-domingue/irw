#!/usr/bin/env python3
# Source: https://www.nature.com/articles/s41598-024-77912-7
# DOI: 10.1038/s41598-024-77912-7
# "Higher eigenvector centrality in grooming network is linked to better
# inhibitory control task performance ..." (Kaigaishi & Yamamoto, 2024),
# Scientific Reports.
# Data: 41598_2024_77912_MOESM2_ESM.xlsx (Tables S7-S9 raw data), via Europe
#       PMC supplementaryFiles for PMC11577106.
# License: CC BY 4.0 (Springer Nature; article-attached Supplementary
#          Information, so the article licence is the source licence).
#
# Item text: NOT shipped, and not worth chasing. The "items" are eight
#   cognitive TASKS administered to macaques, not questions with wording --
#   there is no stem a subject read. The task names are the identifiers, and
#   the procedures are described in the paper's Methods at paragraph length,
#   which is not item text. A task battery of this kind is the case
#   itemtext_standard.md leaves blank rather than invents.
#
# SUBJECTS ARE JAPANESE MACAQUES, WHICH IS NOT A REASON TO SKIP. datastandard.md
# defines `id` as "the focal unit being measured -- typically a person, but
# sometimes another entity", and a repeated-trial battery with a binary
# success per trial fits the long format exactly as a Likert survey does.
# (A cichlid candidate was wrongly dropped on species grounds in PLOS batch 21;
# this is the same shape and ships.)
#
# One table, not three. The workbook splits the battery across three sheets by
# DOMAIN (physical / social / inhibition), but those are domains of one
# battery given to one colony, not three instruments -- and taken separately
# none of them clears the 100-subject floor (81 / 109 / 123 subjects, and
# per-task counts of 75-123). Pooled, the battery has 138 distinct subjects.
# The domain is kept as `itemcov_domain` so a user can split it back out.
#
# THE SOURCE'S `trial` COLUMN DOES NOT UNIQUELY INDEX A TRIAL. 36 (subject,
# task, trial) triples repeat, 20 of them with an identical timestamp -- e.g.
# `ginco` has six rows of cylinder trial 1, all at 2022-02-09 16:58, with
# differing success. So the source counter cannot tell repeated responses
# apart, which is what datastandard.md needs `trial_number` to do. This script
# therefore emits `trial_number` as a sequential index within (subject, task)
# in the file's own row order, and keeps the source's counter as
# `trial_source` so nothing is lost. The row order is the only ordering the
# deposit provides; no claim is made that it is chronological beyond that.

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11577106/supplementaryFiles"
XLSX = "41598_2024_77912_MOESM2_ESM.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
TABLE = "kaigaishi_2024_primate_cognition"
SHEETS = ["physical", "social", "inhibition"]

# Stable subject attributes. The sheets also carry ~25 social-network
# statistics per row (eigen, deg, indeg, bet, st, ... and their _sex
# variants). Those are the paper's derived PREDICTORS, computed per subject
# per observation period rather than being attributes of the subject, and they
# are recomputable from the centrality sheet -- so they are dropped with a
# printed reason rather than frozen into person-level covariates they are not.
COVS = {"sex": "cov_sex", "rank2": "cov_rank", "age_category": "cov_age_category"}


def load():
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=300)
        if r.ok and r.content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                name = next(n for n in z.namelist() if n.endswith(XLSX))
                with z.open(name) as fh:
                    return pd.ExcelFile(BytesIO(fh.read()))
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")


def convert() -> None:
    xl = load()
    frames = []
    for sheet in SHEETS:
        # The real header is the third row; rows 0-1 are the table caption.
        d = xl.parse(sheet, header=2).dropna(axis=1, how="all")
        d = d[d["subject"].notna() & d["success"].notna() & d["task"].notna()]
        d["domain"] = sheet
        frames.append(d)
    a = pd.concat(frames, ignore_index=True)

    dropped = sorted(set(a.columns) - set(COVS)
                     - {"subject", "task", "success", "trial", "domain"})
    print(f"  [skip] {len(dropped)} column(s) not shipped: network statistics "
          f"and observation timestamps -- {', '.join(dropped[:8])}...")

    a["resp"] = pd.to_numeric(a["success"], errors="coerce")
    a = a[a["resp"].isin([0, 1])]
    a["id"] = a["subject"].astype(str)
    a["item"] = a["task"].astype(str)
    a["itemcov_domain"] = a["domain"]
    a["trial_source"] = pd.to_numeric(a["trial"], errors="coerce")
    a["trial_number"] = a.groupby(["id", "item"]).cumcount() + 1
    for src, dst in COVS.items():
        a[dst] = a[src].astype(str).str.strip()

    cov_cols = sorted(COVS.values())
    long = a[["id", "item", "resp", "trial_number", "trial_source",
              "itemcov_domain"] + cov_cols]
    long = long.sort_values(["id", "item", "trial_number"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(float)

    assert long["resp"].isin([0.0, 1.0]).all(), "resp is not binary"
    assert not long.duplicated(["id", "item", "trial_number"]).any(), \
        "duplicate id/item/trial_number"
    assert long["id"].nunique() >= 100, "below the 100-id floor"
    assert long["item"].nunique() == 8, "expected 8 tasks"
    # Gate on the UPLOAD profile, not the legacy compat run_qc. The two
    # disagree on exactly this table: run_qc's `dup_id_item` decides fail-vs-note
    # from ("wave", "timepoint", "date") alone (_checks.py ~line 404) and so
    # hard-fails a table keyed by trial_number, even though the standard says a
    # `trial_` index is what tells repeated responses apart -- and even though
    # the same module's own occasion_columns() counts trial_* for the rescue
    # path. The upload gate applies that rescue and passes. Reported separately;
    # do not "fix" this by inventing a date column the deposit cannot support
    # (the repeated cylinder trials share one timestamp).
    report = irw_validate.validate_frame(long, label=TABLE, profile="upload")
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():g}-"
          f"{long['resp'].max():g}")


if __name__ == "__main__":
    convert()
