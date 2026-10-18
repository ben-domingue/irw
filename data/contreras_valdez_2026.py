#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/gw4wcb9rft/2
# DOI: 10.17632/gw4wcb9rft.2
# Data: CEP_Mexico_Dataset_2021.sav
# License: CC BY 4.0 (verified on the deposit record)
# Reference: Contreras-Valdez, J., Bermúdez Pavón, M., & Solís Elizarrarás, S. (2026). Low Self-Esteem as the Central Vulnerability in Core Eating Psychopathology. Mendeley Data.
#
#  respondents. 3 table(s) ship:
#   contreras_valdez_2026_cpq                               10 items, 1-4
#   contreras_valdez_2026_perci                              8 items, 1-7
#   contreras_valdez_2026_rses                               8 items, 1-4
#
# Three shippable blocks. RSES is the Rosenberg Self-Esteem Scale,
#   register verdict SHIP; eight of its ten items are deposited, so the
#   table is the deposited subset and says so. CPQ (Clinical
#   Perfectionism Questionnaire) and PERCI (Perth Emotion Regulation
#   Competency Inventory) have NO register row -- both logged as
#   register-row requests.
# The five ALL-CAPS columns are the paper's derived subscale scores and
#   are dropped as such, not as unexplained losses.
#
# PII: none. All three screen surfaces were checked -- column name, values, and
#   the SPSS/Stata variable label where the file has one.
#
# Item text: not shipped. Variable labels are present but Spanish-only administration with no author-supplied English, so the English would be IRW-generated and owes a translation_source plus an issues-page callout. Where the text is: the .sav variable labels.
#
# From the #3077 blank-flag re-mine: this key was written to
# repo_triage_seen_keys.csv before irw#2222 added the flag column, so the key was
# recorded and the verdict never was. It was not a rejection -- nobody had looked.
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402
from irw_triage_updated import load_table  # noqa: E402

# --- raw input -------------------------------------------------------------
# Self-contained by design: fetches the deposit itself and caches it, so it
# re-runs in a fresh checkout (which is what metadata/covariate_labels/
# harvest.py does). Set CONTRERAS_RAW to point at an already-downloaded copy.
_URL = "https://data.mendeley.com/public-files/datasets/gw4wcb9rft/files/8f860ff4-21ff-4d40-9617-7cb06a8dd072/file_downloaded"
_NAME = "CEP_Mexico_Dataset_2021.sav"


def _raw():
    override = os.environ.get("CONTRERAS_RAW")
    if override:
        return override if os.path.isfile(override) else os.path.join(override, _NAME)
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "automated_finding", "runs", "raw_cache")
    os.makedirs(cache, exist_ok=True)
    dest = os.path.join(cache, _NAME)
    if not os.path.exists(dest):
        import urllib.request
        req = urllib.request.Request(
            _URL, headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as fh:
            fh.write(r.read())
    return dest


OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

STEM = "contreras_valdez_2026"
BLOCKS = {'cpq': (['CPQ1', 'CPQ2', 'CPQ3', 'CPQ4', 'CPQ5', 'CPQ6', 'CPQ7', 'CPQ8', 'CPQ9', 'CPQ10'], {1, 2, 3, 4}), 'perci': (['PERCI1', 'PERCI2', 'PERCI3', 'PERCI4', 'PERCI5', 'PERCI6', 'PERCI7', 'PERCI8'], {1, 2, 3, 4, 5, 6, 7}), 'rses': (['RSES1', 'RSES2', 'RSES3', 'RSES4', 'RSES5', 'RSES6', 'RSES7', 'RSES8'], {1, 2, 3, 4})}
COVS = {'Age': 'cov_age', 'Sex': 'cov_sex', 'Education': 'cov_education', 'Currentstudies': 'cov_current_studies', 'Residence': 'cov_residence', 'Version': 'cov_counterbalance_version'}
IDCOL = None
SKIP = {'ERI1': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI2': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI3': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI4': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI5': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI6': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI7': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI8': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI9': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI10': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI11': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'ERI12': "ERI1-ERI12: a 12-item block whose instrument I could not identify. The register's only ERI row is Siegrist's 16-item Effort-Reward Imbalance work-stress measure, which this is not (12 items, eating-disorder study), so that block row does not apply and no other does -- deferred rather than guessed", 'EDEQ22': 'EDE-Q items 22-23 only. The EDE-Q is a register BLOCK row; two items are also too thin to be a table', 'EDEQ23': 'see EDEQ22', 'CLINICALPERFECTIONISM': 'derived subscale score, not item-level', 'LOWSELF_ESTEEM': 'derived subscale score', 'MOODINTOLERANCE': 'derived subscale score', 'INTERPERSONALDIFFICULTIES': 'derived subscale score', 'COREEATINGPSYCHOPATHOLOGY': 'derived subscale score'}


def convert():
    df = load_table(open(_raw(), "rb").read(), filename="CEP_Mexico_Dataset_2021.sav")
    print(f"raw: {df.shape}")

    if IDCOL:
        assert df[IDCOL].nunique() == len(df), (
            f"{IDCOL} is not unique ({df[IDCOL].nunique()} of {len(df)}) -- "
            "it cannot be the person id")
        ids = df[IDCOL].astype(str).values
    else:
        # No person identifier is deposited, so the row index IS the person.
        ids = [str(i + 1) for i in range(len(df))]

    # Balance the books: every source column is shipped, a covariate, the id,
    # or skipped for a printed reason.
    shipped = {c for cols, _ in BLOCKS.values() for c in cols}
    accounted = shipped | set(COVS) | set(SKIP) | ({IDCOL} if IDCOL else set())
    for c, why in SKIP.items():
        if c in df.columns:
            print(f"  skip {c!r}: {why}")
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    missing = [c for c in shipped if c not in df.columns]
    assert not missing, f"expected item columns absent: {missing}"

    cov = {v: df[k] for k, v in COVS.items() if k in df.columns}
    written = []
    for suffix, (cols, permitted) in BLOCKS.items():
        long = df[cols].copy()
        long.insert(0, "id", ids)
        for name, series in cov.items():
            long[name] = series.values
        out = long.melt(id_vars=["id"] + list(cov),
                        value_vars=cols, var_name="item", value_name="resp")
        out = out.dropna(subset=["resp"])
        out["resp"] = out["resp"].astype(int)
        # The permitted set is asserted PER TABLE, never inherited from a
        # sibling block -- that is what catches a 1-6 block in a 1-5 family.
        extra = set(out["resp"].unique()) - permitted
        assert not extra, f"{suffix}: resp values outside {sorted(permitted)}: {extra}"
        assert out["item"].nunique() > 1, f"{suffix}: only one distinct item"
        assert out["id"].nunique() >= 100, (
            f"{suffix}: {out['id'].nunique()} unique ids, below the floor of 100")
        out = out[["id", "item", "resp"] + list(cov)]

        pv = {i: set(permitted) for i in cols}
        checks = run_qc(out, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (suffix, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(out, label=f"{STEM}_{suffix}",
                                             profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors,             (suffix, [(f.check, f.message) for f in report.errors])

        name = f"{STEM}_{suffix}"
        assert name not in written, f"duplicate output name {name}"
        written.append(name)
        path = os.path.join(OUT_DIR, name + ".csv")
        out.to_csv(path, index=False, na_rep="NA")
        print(f"  {name}: {out['id'].nunique()} ids x {out['item'].nunique()} "
              f"items = {len(out)} responses -> {path}")
    return written


if __name__ == "__main__":
    convert()
