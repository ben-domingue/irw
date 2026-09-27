#!/usr/bin/env python3
# Source: https://osf.io/p8v3k/  (folder "Latent Analyses": data_SD4_OSF.csv,
#   https://osf.io/download/hvscu/, and "data USA.csv", https://osf.io/download/4zypc/)
# Paper DOI: 10.1027/1015-5759/a000715
#   Blötner, C., Webster, G. D., & Wongsomboon, V. (2023). Measurement invariance
#   of the Short Dark Tetrad across cultures and genders. European Journal of
#   Psychological Assessment, 39(5), 331-336.
# License: CC BY 4.0 (OSF node p8v3k, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27).
#
# Tables: the Short Dark Tetrad (SD4; Paulhus et al. 2021), 28 items 1-5, seven
#   each for Machiavellianism (M1-M7), narcissism (N1-N7), psychopathy (P1-P7)
#   and sadism (S1-S7). Item names are the authors' own shared labels (their
#   MI script renames the German SD4_Mach_1 ... SD4_Sad_7 to M1 ... S7 so the
#   two samples line up).
#   - blotner_2023_sd4_germany: German SD4, 594 adults. The authors' exclusion is
#     reproduced: `random_condition > 0` ("Excluding those who experienced
#     technical problems in the survey presentation"), 600 -> 594. -77/-66/-99
#     are the survey's missing codes (none remain among SD4 items after the
#     exclusion). Covariates: gender (authors' mapping 1 female, 2 male,
#     3 diverse, 4 N/A) and age (one value of 123 set missing).
#     `education` and `native_language` are left out: the deposit carries no
#     value labels for them.
#   - blotner_2023_sd4_usa: English SD4, 451 U.S. adults; blank item cells
#     dropped. Covariate: gender, as recorded (free text, truncated to 8
#     characters in the deposit).
#   The two samples answered different language versions, so they are kept as
#   separate tables (datastandard.md: merge only on confirmed identical
#   administration); ids do not link across them.
#   No SD4 item is reverse-keyed.
#
# Not taken: data_SD4_OSF.csv also holds the German validation battery (BFI-2
#   facets, NARQ-S, PID-5-BF, MACH-IV, SRP-SF, UPPS-P, VAST, RSES, and others,
#   ~330 columns) with no codebook in this deposit. Those scales are outside the
#   paper and their item-to-instrument mapping is not documented here.

import sys
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL_DE = "https://osf.io/download/hvscu/"
URL_US = "https://osf.io/download/4zypc/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {"M": "Mach", "N": "Narc", "P": "Psyc", "S": "Sad"}
ITEMS = [f"{k}{i}" for k in SCALES for i in range(1, 8)]
CONSTRUCT = {f"{k}{i}": v.lower() for k, v in SCALES.items() for i in range(1, 8)}


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def finish(t: pd.DataFrame, name: str) -> None:
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100
    pv = {i: set(range(1, 6)) for i in ITEMS}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    checks = run_qc(t, permitted_values=pv, item_constructs=CONSTRUCT)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=name, profile="upload",
        context={"permitted_values": pv, "item_constructs": CONSTRUCT})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


def long(d: pd.DataFrame, covs: list) -> pd.DataFrame:
    t = d[["id"] + ITEMS + covs].melt(id_vars=["id"] + covs,
                                      var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    assert (t["resp"] == t["resp"].round()).all()
    t["resp"] = t["resp"].astype(int)
    return t[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Germany
    de = pd.read_csv(BytesIO(fetch(URL_DE)), sep=";")
    assert de.shape == (600, 364), de.shape
    assert de["lfdn"].is_unique
    de = de[de["random_condition"] > 0].copy()
    assert len(de) == 594
    src = [f"SD4_{v}_{i}" for v in SCALES.values() for i in range(1, 8)]
    de = de.rename(columns=dict(zip(src, ITEMS)))
    de[ITEMS] = de[ITEMS].where(~de[ITEMS].isin([-77, -66, -99]))
    de["id"] = de["lfdn"].astype(int)
    de["cov_gender"] = de["gender"].map({1: "female", 2: "male", 3: "diverse"})
    de["cov_age"] = de["age"].where(de["age"].between(16, 100))
    print(f"  germany: age set missing for {int(de['cov_age'].isna().sum())} row(s)")
    finish(long(de, ["cov_gender", "cov_age"]), "blotner_2023_sd4_germany")

    # --- USA
    us = pd.read_csv(BytesIO(fetch(URL_US)))
    assert us.shape == (451, 31) and (us["Study"] == "USA").all(), us.shape
    first = us.columns[0]
    assert us[first].is_unique
    us["id"] = us[first].astype(int)
    us["cov_gender"] = us["gender"]
    finish(long(us, ["cov_gender"]), "blotner_2023_sd4_usa")


if __name__ == "__main__":
    convert()
