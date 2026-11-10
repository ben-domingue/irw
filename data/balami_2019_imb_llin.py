#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6637635
# DOI: 10.1186/s12874-019-0803-z
#   "An information-motivation-behavioural skills analysis of long-lasting
#   insecticidal net use among pregnant women in a hospital in North-Eastern
#   Nigeria" (Balami, Said, Zulkefli, Bachok & Balami, 2019), BMC Medical Research
#   Methodology 19:157.
# Data: the article's supplementary file 12874_2019_803_MOESM2_ESM.xlsx (Europe
#   PMC supplementaryFiles zip): 380 respondents x 29 columns, responses stored as
#   the option text ("Correct", "very good", "effectively"). MOESM1_ESM.docx is
#   the questionnaire.
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Sample: 380 antenatal-care attendees of a hospital in Maiduguri, Borno State,
#   systematically sampled Jan-Mar 2017 (paper Methods; N = 380 in Table 1).
#   id = SNO (1..380, unique).
#
# Tables (paper Methods, "Instrument and data collection"):
#   balami_2019_imb_information  INFO1..INFO18   0/1  18 knowledge questions,
#       "each with three options: Yes, No and I don't know. A correct response was
#       scored one (1), while an incorrect response was scored zero (0)". The
#       deposit holds the scored verdict (Correct / Incorrect / Don't know).
#       "Don't know" is a non-response under the IRW standard and is dropped
#       (the paper's sum score counts it as 0); the raw Yes/No answer is not in
#       the deposit.
#   balami_2019_imb_motivation   MOT1..MOT3      MOT1 1-5 (very bad .. very good),
#       MOT2 1-5 (very unpleasant .. very pleasant), MOT3 1-6 (very untrue ..
#       very true; "untrue"/"true" are the two middle points, and the spreadsheet
#       stored the bare word True as a boolean)
#   balami_2019_imb_skills       BSKILLS1..5     BSKILLS1 1-4 (very hard .. very
#       easy), BSKILLS2-5 1-4 (very ineffectively .. very effectively)
#   The single BEHAVIOUR item (frequency of net use) is not shipped.
#
# Covariates: residence type (permanent resident / internally displaced person).
#
# Item text: not shipped. Levels checked: xlsx headers are codes (INFO1..); cells
#   hold scored verdicts or anchor labels. The wording is in MOESM1_ESM.docx; the
#   information items were "adopted from the instruments used in some previous
#   studies [40-42], after obtaining permission from the authors", so the
#   wording's rights sit with those authors.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "balami_2019"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6637635/supplementaryFiles"
FILE = "12874_2019_803_MOESM2_ESM.xlsx"

INFO = {"Correct": 1, "Incorrect": 0, "Don't know": None}
MOT = {
    "MOT1": {"very bad": 1, "somewhat bad": 2, "neither bad nor good": 3,
             "somewhat good": 4, "very good": 5},
    "MOT2": {"very unpleasant": 1, "someaht unpleasant": 2,
             "neither unpleasant nor pleasant": 3, "somewhat pleasant": 4,
             "very pleasant": 5},
    "MOT3": {"very untrue": 1, "mostly untrue": 2, "untrue": 3, "True": 4,
             "true": 4, "mostly true": 5, "very true": 6},
}
SK1 = {"very hard": 1, "hard": 2, "easy": 3, "very easy": 4}
SK = {"very ineffectively": 1, "ineffectively": 2, "effectively": 3,
      "very effectively": 4}


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        p.write_bytes(z.read([n for n in z.namelist() if n.endswith(FILE)][0]))
    return p


def recode(s: pd.Series, mapping: dict, allow_none=False) -> pd.Series:
    s = s.map(lambda v: str(v).strip() if pd.notna(v) else v)
    bad = s.notna() & ~s.isin(list(mapping))
    assert not bad.any(), (s.name, s[bad].unique())
    return s.map(mapping).astype(float)


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (380, 29), d.shape
    assert d["SNO"].is_unique and d["SNO"].tolist() == list(range(1, 381))
    info = [f"INFO{i}" for i in range(1, 19)]
    mot = ["MOT1", "MOT2", "MOT3"]
    sk = [f"BSKILLS{i}" for i in range(1, 6)]
    accounted = {"SNO", "Residence type", "BEHAVIOUR"} | set(info) | set(mot) | set(sk)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted

    w = pd.DataFrame({"id": d["SNO"],
                      "cov_residence": d["Residence type"].map(
                          {"permanentresident": "permanent resident", "IDP": "internally displaced"})})
    assert w["cov_residence"].notna().all()
    n_dk = 0
    for c in info:
        n_dk += (d[c] == "Don't know").sum()
        w[c] = recode(d[c], INFO)
    for c in mot:
        w[c] = recode(d[c], MOT[c])
    w["BSKILLS1"] = recode(d["BSKILLS1"], SK1)
    for c in sk[1:]:
        w[c] = recode(d[c], SK)
    print(f"  dropped {n_dk} 'Don't know' information responses")

    tables = {
        "balami_2019_imb_information": (info, {i: {0, 1} for i in info}),
        "balami_2019_imb_motivation": (mot, {"MOT1": set(range(1, 6)), "MOT2": set(range(1, 6)),
                                             "MOT3": set(range(1, 7))}),
        "balami_2019_imb_skills": (sk, {i: {1, 2, 3, 4} for i in sk}),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, pv) in tables.items():
        t = w.melt(id_vars=["id", "cov_residence"], value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "cov_residence"]].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message[:150]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
