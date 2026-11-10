#!/usr/bin/env python3
# Source: https://doi.org/10.23668/psycharchives.2530
# DOI: 10.1177/0047287520933688 (paper); data 10.23668/psycharchives.2530
#   Yu, G. B., Sirgy, M. J., Bosnjak, M., & Lee, D.-J. (2021). A Preregistered
#   Study of the Effect of Shopping Satisfaction during Leisure Travel on
#   Satisfaction with Life Overall: The Mitigating Role of Financial Concerns.
#   Journal of Travel Research, 60(3), 639-655.
# Data: "Final Data - D-P19-9196 ZPID 3 Studien Studie 3.sav" (500 rows x 97
#   columns; UK online-panel members who took a leisure trip in the last six
#   months, 250 women and 250 men).
# License: CC BY-SA 4.0 (dc.rights.uri on the PsychArchives item; the
#   bundled license.txt is the repository's generic terms-of-use pointer).
#
# Item text: not shipped -- the wording is fully in hand (SPSS variable
#   labels carry each stem, value labels carry the five anchors plus "No
#   Opinion"), but the stems are the authors' adaptations of published scales
#   (SWLS among them, register `block`), so the rights pass is left to a
#   deliberate item-text round. Both label levels checked: present on every
#   item.
#
# SCALE: 1-5 on every item (labels vary by section: dissatisfied..satisfied,
#   disagree..agree, "does not describe me".."describes me completely").
#   Code 0 = "No Opinion" (value label), dropped as non-response.
#
# Tables (codes are the .sav variable names):
#   yu_2021_shopping_satisfaction  v_25-v_47 (20 store/goods attributes, Section A)
#   yu_2021_overspending           v_49-v_51 (Section Ab)
#   yu_2021_trip_pleasure          v_53-v_55
#   yu_2021_trip_detachment        v_57-v_59
#   yu_2021_trip_meaning           v_61-v_63
#   yu_2021_trip_reflection        v_65-v_67
#   yu_2021_trip_satisfaction      v_69-v_71 (the deposit's TSAT = their mean)
#   yu_2021_swls                   v_79-v_83 (Section D)
#   yu_2021_domain_satisfaction    v_91-v_94 (family, job, health, relationships)
#   yu_2021_money_stress           v_96-v_100
#   yu_2021_financial_security     v_102-v_106
# Not shipped: v_85-v_89 (Section Db repeats the five SWLS statements later
#   in the same survey; equal to Section D on 62-74% of rows; why it was asked
#   twice is not stated in the deposit, so only the first administration
#   ships); v_75/v_77 (2-item leisure-life satisfaction, under the floor);
#   v_17-v_21 destinations (free text), v_22/v_23/v_72/v_73 trip and leisure
#   descriptors, v_16 (screener, constant), derived composites.
# Covariates: cov_gender, cov_age, cov_occupation (value labels). id = lfdn.

import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://www.psycharchives.org/rest/bitstreams/"
            "f3bbf9f8-e810-4691-b213-27b51a6b4156/retrieve")


def v(*nums):
    return [f"v_{n}" for n in nums]


SCALES = {
    "yu_2021_shopping_satisfaction": v(25, 26, 27, 28, 29, 30, 31, 32, 33, 35, 36,
                                       37, 38, 40, 41, 42, 43, 45, 46, 47),
    "yu_2021_overspending": v(49, 50, 51),
    "yu_2021_trip_pleasure": v(53, 54, 55),
    "yu_2021_trip_detachment": v(57, 58, 59),
    "yu_2021_trip_meaning": v(61, 62, 63),
    "yu_2021_trip_reflection": v(65, 66, 67),
    "yu_2021_trip_satisfaction": v(69, 70, 71),
    "yu_2021_swls": v(79, 80, 81, 82, 83),
    "yu_2021_domain_satisfaction": v(91, 92, 93, 94),
    "yu_2021_money_stress": v(96, 97, 98, 99, 100),
    "yu_2021_financial_security": v(102, 103, 104, 105, 106),
}
ALLOWED = {1, 2, 3, 4, 5}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tf:
        tf.write(r.content)
        tf.flush()
        d, meta = pyreadstat.read_sav(tf.name)
    assert d.shape == (500, 97), d.shape
    assert d["lfdn"].is_unique
    vl = meta.variable_value_labels
    for cols in SCALES.values():
        for c in cols:
            assert vl[c].get(0.0) == "No Opinion", c
            assert set(vl[c]) == {0.0, 1.0, 2.0, 3.0, 4.0, 5.0}, c

    d["id"] = d["lfdn"].astype(int)
    d["cov_gender"] = d["v_13"].map(vl["v_13"])
    d["cov_age"] = d["v_14"]
    d["cov_occupation"] = d["v_107"].map(vl["v_107"])
    cov_cols = ["cov_gender", "cov_age", "cov_occupation"]

    for table, cols in SCALES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        n0 = int((long["resp"] == 0).sum())
        long = long[long["resp"] != 0]
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - ALLOWED
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: ALLOWED for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:130]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses ({n0} 'No Opinion' "
              f"dropped), {long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
