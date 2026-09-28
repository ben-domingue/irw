#!/usr/bin/env python3
# Source: Harvard Dataverse, Cella, D. (2016). NeuroQOL Wave 1b.
#   https://doi.org/10.7910/DVN/TLCDRX  (12 recoded SAS files, forms A-L, with
#   codebooks and READMEs; files fetched by Dataverse file id, see FORMS)
# Paper: Cella, D., Lai, J.-S., Nowinski, C. J., Victorson, D., Peterman, A.,
#   Miller, D., ... Moy, C. (2012). Neuro-QOL: Brief measures of health-related
#   quality of life for clinical research in neurology. Neurology, 78(23),
#   1860-1867. doi:10.1212/WNL.0b013e318258f744
# Data DOI: 10.7910/DVN/TLCDRX
# License: CC0 1.0 (Dataverse dataset license field, checked on the Dataverse
#   API 2026-09-27; no restricted files).
#
# Design: Neuro-QOL wave 1b is the item-bank calibration in a U.S. internet
#   panel (Greenfield, 2008). Each respondent took ONE form; each form carries
#   one to four item banks. "NeuroQOL form assignment.tab" (actually an xlsx):
#     adult     English A / Spanish G: social role participation, satisfaction
#               with social roles
#               English B / Spanish H: assistive devices, lower extremity
#               (mobility), upper extremity (ADL / fine motor)
#               English C / Spanish I: positive psychological function,
#               depression, anxiety
#               English D / Spanish J: cognition (perceived + applied)
#     pediatric English E / Spanish K: emotional functioning, social relations
#     (12-17)   English F / Spanish L: upper extremity, lower extremity, walking
#               aid, wheelchair
#   Banks are assigned by the README's variable ranges, read in the codebook's
#   (administration) order. One table per bank per language: banks are separate
#   instruments (the promis1wave1 and PROMISPME_Forrest_2021 precedent), and the
#   Spanish forms are a different language version with a different sample (the
#   blotner_2023_sd4 precedent). Item names are the source variable names, which
#   are shared by the English and Spanish forms, so neuroqol1b_X_eng and
#   neuroqol1b_X_spa use the same item codes. A table under the 100-id floor is
#   not written: the branched blocks asked only of device users (assistive
#   devices, forms B/H, 92 and 21 respondents; pediatric walking aid, F/L, 24
#   and 28; pediatric wheelchair, F/L, 8 and 15). 24 tables result.
#
# Responses are RAW as collected (punch codes). For many negatively worded
#   items the instrument's own response coding already runs the other way (the
#   READMEs: "Never=5 rather than Never=1"); that is how the data were
#   collected and is kept. Items the READMEs say "should be reverse coded"
#   (forms E, F, K, L) are NOT recoded, per the data standard.
#   Form A: NQPRF45, NQPRF47, NQPRF49 and NQSAT51 were collected with the scale
#   running opposite to their siblings and the deposit supplies corrected
#   copies (*_cor); the README says not to use the originals. The *_cor values
#   are shipped under the base names so they match form G, where the same four
#   were corrected in place.
#   Form L: the walking-aid block carries names without the _NQ suffix that
#   form F uses (PF_WA_New2 vs PF_WA_New2_NQ, same codebook question number and
#   wording); the suffix is added so both languages share item codes.
#   Form F: the deposit gave one name, PWG_2202R2_NQ, to two questions ("walk
#   across the room", lower extremity, and "move up and down inclines or ramps
#   using a wheelchair", wheelchair block), and only one column survives. Form
#   L's v2 README documents the same clash and splits them (PWG_WC_2202R2_NQ).
#   The surviving F column has 501 values, so it holds the walking item, but
#   for the 8 respondents routed to the wheelchair block it could hold either;
#   their value is dropped.
#
# Covariates: age, gender (1 Male / 2 Female as labelled). NOT carried:
#   telephone area code, height, weight, race, occupation, education and the
#   disease-burden / comorbidity check lists. RESPID (the survey system's
#   respondent number, unique within a form) is kept as id; bank tables from
#   the same form share ids.
#
# Item text: NOT extracted. Neuro-QOL is a HealthMeasures (PROMIS-family)
#   instrument, and IRW does not ship that wording (ruling 2026-09-05).

import io
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
API = "https://dataverse.harvard.edu/api/access/datafile/{}?format=original"

# form: (language, data file id, codebook file id, expected shape)
FORMS = {
    "a": ("eng", 3005037, 3005038, (549, 191)),
    "b": ("eng", 3005040, 3005041, (518, 184)),
    "c": ("eng", 3005043, 3005044, (513, 172)),
    "d": ("eng", 3005046, 3005047, (533, 177)),
    "e": ("eng", 3005050, 3005051, (513, 122)),
    "f": ("eng", 3005053, 3005054, (505, 149)),
    "g": ("spa", 3005058, 3005056, (253, 187)),
    "h": ("spa", 3005059, 3005060, (254, 182)),
    "i": ("spa", 3005062, 3005063, (252, 172)),
    "j": ("spa", 3005065, 3005066, (251, 175)),
    "k": ("spa", 3005068, 3005069, (255, 122)),
    "l": ("spa", 3005071, 3005072, (263, 150)),
}
# (table stem, first variable, last variable) in codebook order, from READMEs
BANKS = {
    "a": [("social_roles", "SRPPER22", "NQPRF49"),
          ("social_satisfaction", "SRPSAT27", "NQSAT51")],
    "b": [("assistive_devices", "AP_AD4_NQ", "NQASD13"),
          ("lower_extremity", "AP_M1_NQ", "PFC45"),
          ("upper_extremity", "AP_U1_NQ", "PF_N_U1_NQ")],
    "c": [("positive_affect", "NQPPF01", "NQPPF27"),
          ("depression", "EDDEP02", "EDDEP56"),
          ("anxiety", "NQANX01", "EDANX55")],
    "d": [("cognition", "NQCOG01", "SILF3_NQ")],
    "e": [("ped_emotional", "PWG_5040R1_NQ", "EH_NEW23"),
          ("ped_social", "PWG_9003R2_NQ", "PWG_2964R1_NQ")],
    "f": [("ped_upper_extremity", "PF_S_New29_NQ", "NQUEXped41"),
          ("ped_lower_extremity", "PF_M_New24", "PWG_2707R2_NQ"),
          ("ped_walking_aid", "PF_WA_New2_NQ", "WA_PWG_2118_NQ"),
          ("ped_wheelchair", "PWG_New4_NQ", "PF_W_New1_NQ")],
}
BANKS.update({"g": BANKS["a"],
              "h": BANKS["b"], "i": BANKS["c"], "j": BANKS["d"], "k": BANKS["e"],
              "l": BANKS["f"][:2] + [("ped_walking_aid", "PF_WA_New2", "WA_PWG_2118")]
              + BANKS["f"][3:]})
FORM_A_COR = ["NQPRF45", "NQPRF47", "NQPRF49", "NQSAT51"]
EXPECTED_ITEMS = {  # bank sizes checked against the form-assignment sheet's banks
    "social_roles": 49, "social_satisfaction": 51, "assistive_devices": 13,
    "lower_extremity": 37, "upper_extremity": 44, "positive_affect": 27,
    "depression": 30, "anxiety": 28, "cognition": 88, "ped_emotional": 46,
    "ped_social": 38, "ped_upper_extremity": 40, "ped_lower_extremity": 39,
    "ped_walking_aid": 11, "ped_wheelchair": 20,
}


def fetch(fid: int) -> bytes:
    for attempt in range(5):
        r = requests.get(API.format(fid), headers=UA, timeout=180)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"file {fid} failed after 5 attempts")


def read_form(form: str):
    lang, did, cid, shape = FORMS[form]
    with tempfile.NamedTemporaryFile(suffix=".sas7bdat") as tmp:
        tmp.write(fetch(did))
        tmp.flush()
        d = pd.read_sas(tmp.name, encoding="latin1")
    assert d.shape == shape, (form, d.shape)
    cb = pd.read_excel(io.BytesIO(fetch(cid)))
    cb.columns = [c.lower() for c in cb.columns]
    return d, cb


def bank_items(form, d, cb):
    """{bank: [(data column, item name, permitted punches)]} for one form."""
    order = list(dict.fromkeys(cb["new"].astype(str)))
    low = [o.lower() for o in order]
    dcol = {c.lower(): c for c in d.columns}
    punches = {str(k).lower(): set(int(p) for p in g["punch"].dropna())
               for k, g in cb.groupby(cb["new"].astype(str))}
    out = {}
    for bank, first, last in BANKS[form]:
        i, j = low.index(first.lower()), low.index(last.lower())
        cols = []
        for v in low[i:j + 1]:
            if v not in dcol:
                continue
            if v.endswith("_cor"):
                continue  # placed at its base variable's position below
            name = dcol[v]
            if form == "a" and name in FORM_A_COR:
                name = name + "_cor"  # the README: use the corrected copy
            item = name[:-4] if name.endswith("_cor") else name
            cols.append((name, item, punches.get(v, set())))
        out[bank] = cols
    if form == "l":  # walking-aid names without the form F "_NQ" suffix
        out["ped_walking_aid"] = [(c, i if i.endswith("_NQ") else i + "_NQ", p)
                                  for c, i, p in out["ped_walking_aid"]]
    return out


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    forms = {f: read_form(f) for f in FORMS}
    tables = {}
    for form, (d, cb) in forms.items():
        lang = FORMS[form][0]
        c = {x.lower(): x for x in d.columns}
        assert (d[c["cqa"]] == 1).all() and (d[c["respstatus"]] == 2).all()
        assert d[c["respid"]].is_unique
        base = pd.DataFrame({
            "id": d[c["respid"]].astype(int),
            "cov_age": d[c["cqs2_1"]].astype("Int64"),
            "cov_gender": d[c["cqs3"]].map({1: "male", 2: "female"}),
        })
        for bank, cols in bank_items(form, d, cb).items():
            want = EXPECTED_ITEMS[bank] + (form == "l" and bank == "ped_wheelchair")
            assert len(cols) == want, (form, bank, len(cols))
            parts = []
            pv, cl = {}, {}
            for col, item, allowed in cols:
                x = base.copy()
                if form == "f" and col == "PWG_2202R2_NQ":
                    x = x[d["PWG_New4_NQ"].isna()]
                x["item"] = item
                x["resp"] = d[col]
                x = x.dropna(subset=["resp"])
                assert (x["resp"] == x["resp"].round()).all(), (form, col)
                bad = set(x["resp"].astype(int)) - allowed
                assert not bad, (form, col, bad, allowed)
                parts.append(x)
                pv[item] = allowed
                cl[item] = bank
            t = pd.concat(parts, ignore_index=True)
            t["resp"] = t["resp"].astype(int)
            t = t[["id", "item", "resp", "cov_age", "cov_gender"]]
            tables[f"neuroqol1b_{bank}_{lang}"] = (t, pv, cl)
    for name in [n for n in tables if n.endswith("_eng")]:
        a = set(tables[name][0]["item"])
        b = set(tables[name[:-4] + "_spa"][0]["item"])
        # the one known difference: form L's split-out wheelchair ramp item
        assert a ^ b <= {"PWG_WC_2202R2_NQ"}, (name, sorted(a ^ b))
    return tables


def finish(name, t, pv, cl):
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any(), name
    if t["id"].nunique() < 100:
        return f"{name}: SKIPPED, {t['id'].nunique()} ids (< 100)"
    checks = run_qc(t, permitted_values=pv, item_constructs=cl)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    report = irw_validate.validate_frame(
        t, label=name, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    assert report.conforms and not report.errors, \
        (name, [(f.check, f.message) for f in report.errors])
    for f in report.findings:
        print(f"    [{f.severity}] {name} {f.check}: {f.message}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    return (f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
            f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


def convert() -> None:
    tables = build()
    for name in sorted(tables):
        print(finish(name, *tables[name]))


if __name__ == "__main__":
    convert()
