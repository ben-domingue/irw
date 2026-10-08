#!/usr/bin/env python3
# Source: https://zenodo.org/records/17982683
# DOI: 10.5281/zenodo.17982683 (dataset; no paper DOI on the record)
#   Gwen, Cheryl, Ramadhan, Ghaffy & Ramadhani, Safa (2025). "Social Support in
#   Mediating The Relationship Between Interpersonal Communication, Self-Esteem, and
#   Mental Health Among Young Adults" [data set]. Zenodo.
# Data: "The Role of Social Support ... (Responses).xlsx" (Google Forms export): 226
#       Indonesian young adults x Timestamp, age band, and 22 items whose column
#       headers are the full Indonesian statements, all scored 1-5. No codebook and no
#       option labels in the deposit.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (the column headers ARE the administered Indonesian stems; built
#   by automated_finding/itemtext_verification/make_itemtext_gwen_2025.py). English
#   item_text_translated is IRW's own translation. Option labels are not in the
#   deposit, so option_text is blank.
#
# Tables (block boundaries from the statements' content and the record's four
#   constructs, in deposit column order; codes are positional, assigned to the
#   headers in order -- STEMS below lists the exact header each code stands for):
#   gwen_2025_interpersonal_comm  ic1-ic13  (openness, empathy, support, positiveness,
#                                            equality, ... adapting to the situation)
#   gwen_2025_self_esteem         se1-se2
#   gwen_2025_social_support      ss1-ss3   (emotional, informational, practical)
#   gwen_2025_mental_health       mh1-mh4   (depression, anxiety, trauma, sleep
#                                            symptoms; higher = more symptoms)
# Not shipped: Timestamp (form metadata). Covariate: cov_age_band ("Usia Anda").
# Missing cells (1-2 per item) are dropped.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "gwen_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = ("The Role of Social Support in Mediating the Relationship Between Interpersonal "
         "Communication, Self-Esteem, and Mental Health Among Young Adults (Responses).xlsx")
URL = "https://zenodo.org/api/records/17982683/files/" + requests.utils.quote(FNAME) + "/content"
BLOCKS = [("gwen_2025_interpersonal_comm", "ic", 13), ("gwen_2025_self_esteem", "se", 2),
          ("gwen_2025_social_support", "ss", 3), ("gwen_2025_mental_health", "mh", 4)]


def fetch() -> Path:
    p = RAW_DIR / "responses.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def stems() -> dict:
    """{table: [(code, exact source header), ...]} -- also used by the item text builder."""
    d = pd.read_excel(fetch())
    assert d.shape == (226, 24)
    assert d.columns[0] == "Timestamp" and d.columns[1].strip() == "Usia Anda"
    heads, out, k = list(d.columns[2:]), {}, 0
    for name, pre, n in BLOCKS:
        out[name] = [(f"{pre}{i + 1}", heads[k + i]) for i in range(n)]
        k += n
    assert k == len(heads) == 22
    assert out["gwen_2025_self_esteem"][0][1].startswith("Saya merasa bahwa saya adalah pribadi")
    assert out["gwen_2025_social_support"][0][1].startswith("Saya merasa memiliki seseorang")
    assert out["gwen_2025_mental_health"][0][1].startswith("Saya merasa mengalami gejala depresi")
    return out


def main() -> None:
    d = pd.read_excel(fetch())
    print("  [skip] Timestamp: form metadata")
    d.insert(0, "id", range(1, len(d) + 1))     # no id column in the deposit
    d = d.rename(columns={d.columns[2]: "cov_age_band"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, pairs in stems().items():
        ren = {h: c for c, h in pairs}
        codes = list(ren.values())
        t = d.rename(columns=ren).melt(id_vars=["id", "cov_age_band"], value_vars=codes,
                                       var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "cov_age_band"]].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(codes) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: {1, 2, 3, 4, 5} for i in codes}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
