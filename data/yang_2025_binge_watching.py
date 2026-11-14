#!/usr/bin/env python3
# Source: https://zenodo.org/records/16738481
# DOI: 10.5281/zenodo.16738481 (data)
#   Yang X (2025). Dataset for: Binge-Watching and Gender-Specific Effects on Academic, Social, and
#   Mental Well-being in Children and Adolescents [Data set]. Zenodo. (PLOS ONE submission.)
# License: CC BY 4.0 (Zenodo record metadata)
# Data: Binge watching_PLOSOne_2.sav, 2,267 Hong Kong primary and secondary students (all under 18;
#   the file's filter_$ = Q13_Age < 18 is 1 for every row). Anonymous survey; the record states no
#   identifiable data were collected. Variable labels give each question in English; value labels
#   give the anchors. id = the deposit's ID (unique).
#
# Tables (item = the .sav variable name; resp as stored, with the .sav's value labels):
#   yang_2025_igd9   -- Q2.1-Q2.9 gaming-disorder criteria, 0 No / 1 Yes (IGD_result = their sum).
#                       Answered by all 2,267, including the 231 who said they had not gamed.
#   yang_2025_bsmas  -- Q5a-f social media addiction (Bergen-style), 1 Very rarely .. 5 Very often
#                       (SMA_result = their sum).
#   yang_2025_mspss  -- Q6.1-6.12 Multidimensional Scale of Perceived Social Support, 1-7.
#   yang_2025_ucla3  -- Q7.1-7.3 UCLA 3-item loneliness, 1 Hardly ever .. 3 Often.
#   yang_2025_dass21 -- Q8.1-8.21 DASS-21, stored 1 Never .. 4 Almost always (not the usual 0-3; the
#                       deposit's DASS_*_result = 2 x the stored subscale sum). Subscale in the code
#                       suffix (_D/_A/_S).
#   yang_2025_psqi_disturbance -- Q10.5a-j PSQI sleep-disturbance frequencies, 0-3.
#   yang_2025_ese    -- Q11.1-11.5 educational self-efficacy, 1 Not at all .. 5 Extremely confident
#                       (ESES_result = their sum).
# Not shipped: screen-time hours (Q3, Q4), Q9 (four unrelated items), the other PSQI questions
#   (clock times, minutes, single ratings), single-item Q15-Q21, and every derived score.
# Covariates: cov_gender, cov_age, cov_living_with_parents (value labels applied).
# Not carried: Q10.5j_PSQI_Sleep_others (free text).
# Item text: not shipped -- the English variable labels are present, but the instruments are
#   third-party (DASS-21, MSPSS, UCLA-3, BSMAS, PSQI) and the administration language is not stated
#   (the labels mix in Chinese punctuation); no register rows written.
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/16738481/files/Binge%20watching_PLOSOne_2.sav/content"


def main():
    r = requests.get(URL, timeout=180)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 2267 and d["ID"].is_unique
    vl = meta.variable_value_labels
    cols = list(d.columns)
    blocks = {
        "yang_2025_igd9": ([c for c in cols if c.startswith("Q2.")], (0, 1), "IGD_result"),
        "yang_2025_bsmas": ([c for c in cols if c.endswith("_SMA_SocialMediaAddiction")], (1, 5), "SMA_result"),
        "yang_2025_mspss": ([c for c in cols if c.endswith("_MSPSS_SocialSupport")], (1, 7), None),
        "yang_2025_ucla3": ([c for c in cols if c.endswith("_UCLA_3_item_Loneliness")], (1, 3), "loneliness_result"),
        "yang_2025_dass21": ([c for c in cols if c.startswith("Q8.")], (1, 4), None),
        "yang_2025_psqi_disturbance": ([c for c in cols if c.startswith("Q10.5") and c.endswith("_PSQI_Sleep")],
                                       (0, 3), None),
        "yang_2025_ese": ([c for c in cols if c.endswith("_Educational_self_efficacy")], (1, 5), "ESES_result"),
    }
    sizes = {"yang_2025_igd9": 9, "yang_2025_bsmas": 6, "yang_2025_mspss": 12, "yang_2025_ucla3": 3,
             "yang_2025_dass21": 21, "yang_2025_psqi_disturbance": 10, "yang_2025_ese": 5}
    d["id"] = d["ID"].astype(str)
    d["cov_gender"] = d["Q12_Gender"].map(vl["Q12_Gender"])
    d["cov_age"] = d["Q13_Age"]
    d["cov_living_with_parents"] = d["Q14_LivingWithParents"].map(vl["Q14_LivingWithParents"])
    covs = ["cov_gender", "cov_age", "cov_living_with_parents"]
    for name, (items, (lo, hi), total) in blocks.items():
        assert len(items) == sizes[name], (name, items)
        if total:
            full = d[items].notna().all(axis=1)
            assert (d.loc[full, items].sum(axis=1) == d.loc[full, total]).all(), name
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all() and (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
