#!/usr/bin/env python3
# Source: https://osf.io/vfwus/ (longitudinal T1-T3) and https://osf.io/re7sm/ (T1)
# DOI: 10.1038/s41598-023-36718-9
#   "The longer-term impact of the COVID-19 pandemic on wellbeing and subjective
#   cognitive functioning of older adults in Belgium" (De Pue, Gillebert,
#   Dierckx & Van den Bussche, 2023), Scientific Reports 13:9708. PMC10272225.
# DOI: 10.1038/s41598-021-84127-7
#   "The impact of the COVID-19 pandemic on wellbeing and cognitive functioning
#   of older adults" (De Pue, Gillebert, Dierckx, Vanderhasselt, De Raedt &
#   Van den Bussche, 2021), Scientific Reports 11:4636. PMC7907111.
# Data: osf.io/vfwus "Data/Longitudinal_datafile_DePue et al_OSF.csv" (371 x 285,
#       T1+T2+T3 of the completers) and osf.io/re7sm "Data/De Pue et al. raw
#       data.csv" (640 x 108, T1 of everyone). Both are ';'-delimited with ','
#       decimals and ' ' for missing -- the reason the PMC connector's
#       comma-delimited parse failed. Column meanings: each node's
#       Data/ReadThisFirst.txt.
# License: CC BY 4.0 on both OSF nodes (both public; licence id
#          563c1cf88c5e4a3877f9e96a resolves via api.osf.io/v2/licenses/ to
#          "CC-By Attribution 4.0 International"); both articles also CC BY 4.0.
#
# Item text: not shipped. Both label levels checked: the CSVs carry bare codes
#   (CFQ1, GDS1, Lubben1, M3_HADS1, M3_CERQ1 ...) with no variable or value
#   labels; ReadThisFirst.txt gives English paraphrases of the six ad hoc
#   subjective-cognition questions and their anchors only, and the survey was
#   administered in Dutch (the Dutch wording is not in either deposit). The
#   other instruments' text is in their published Dutch versions: CFQ
#   (Merckelbach et al. 1996), GDS-15 (Bleeker et al. 1985), PWI-A
#   (Van Beuningen & de Jonge 2011), LSNS-6 (Lubben et al. 2006), BRS (Soer et
#   al. 2019), HADS (Spinhoven et al. 1997), CERQ-short (Garnefski & Kraaij 2006).
#
# ONE SAMPLE, TWO DEPOSITS. The 2023 deposit's T1 block is a subset of the 2021
# deposit: every one of its 371 rows matches exactly one 2021 row on 81 T1
# columns (all CFQ/GDS/PWI/LSNS/BRS items, age, gender, duration, ...), with the
# runner-up match at most 66/81 (asserted below). The two files number
# participants differently, so the 2021 `Participant` number is used as `id`
# throughout and the 2023 rows are mapped onto it. Instruments given at several moments become one table with
# `wave` (1 = T1 May-June 2020, 2 = T2 June-July 2020, 3 = T3 December 2020);
# T1 comes from the 2021 file (N = 640, including the 269 who dropped out),
# T2/T3 from the 2023 file (N = 371).
#
# Tables:
#   depue_2023_cfq      Cognitive Failures Questionnaire, 25 items, 0-4, waves 1-3
#                       ("not applicable" is already blank in the files)
#   depue_2023_gds15    Geriatric Depression Scale-15, 0/1 (key-scored), waves 1-3
#   depue_2023_pwi      Personal Wellbeing Index-Adults, 8 items, 0-10. The files
#                       store x10 (0-100); divided back to the 0-10 response scale.
#                       PWIk = past month (waves 1-3); PWIk_pre = the same domain
#                       rated retrospectively for before COVID-19 (asked at T1,
#                       so wave 1) -- a different reference period, so a
#                       different item.
#   depue_2023_subjcog  subjective cognitive functioning: five "problems with ..."
#                       items (1-5, waves 1-3); Cognitive_functioning (1-3, T1
#                       only); CognFunct_pre / CognFunct_now (0-10, the format
#                       that replaced it at T2/T3; _pre is retrospective, T2 only)
#   depue_2021_lsns6    Lubben Social Network Scale-6, 0-5, T1 only
#   depue_2021_brs      Brief Resilience Scale, 1-5, T1 only (items 2/4/6 are
#                       stored reversed, as deposited)
#   depue_2023_hads_a   HADS anxiety items, 0-3, T3 only
#   depue_2023_cerq     CERQ-short, 18 items, 1-5, T3 only
#
# No imputation: neither paper mentions any; every item cell is an integer. No
# PII: postal code and the name-derived linkage code were collected but are not
# in either deposit. Covariates are T1 person-level facts; everything that
# varies by wave (contacts, infection status, completion week) is skipped.

import sys
import time
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL_T1 = "https://osf.io/download/8bgnt/"    # re7sm: De Pue et al. raw data.csv
URL_LONG = "https://osf.io/download/3db96/"  # vfwus: Longitudinal_datafile...csv


def fetch(url: str) -> pd.DataFrame:
    for attempt in range(6):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 200:
            break
        time.sleep(15 * (attempt + 1))  # OSF answers 429 under load
    r.raise_for_status()
    return pd.read_csv(StringIO(r.content.decode("utf-8-sig")), sep=";",
                       decimal=",", na_values=[" ", ""])


def rng(prefix, n):
    return [f"{prefix}{i}" for i in range(1, n + 1)]


CFQ, GDS, LSNS, BRS = rng("CFQ", 25), rng("GDS", 15), rng("LSNS", 6), rng("BRS", 6)
SUBDOM = ["Remembering", "Concentration", "Doing_two_things", "Recalling",
          "Forgetfulness"]
HX = ["Parkinson", "Dementia", "Stroke", "Diabetes", "Epilepsy"]


def convert() -> None:
    a = fetch(URL_T1)
    b = fetch(URL_LONG)
    assert a.shape == (640, 108) and b.shape == (371, 285), (a.shape, b.shape)
    assert a["Participant"].is_unique and b["Participant"].is_unique

    # ---- books: 2021 file ---------------------------------------------------
    A_ITEMS = (CFQ + GDS + LSNS + BRS + SUBDOM + ["Cognitive_functioning"]
               + [f"PWI{i}_{p}" for i in range(1, 9) for p in ("pre", "covid")])
    A_COV = ["Age", "Gender", "Living_situation", "Cohabitants",
             "Educational_level", "Work_situation",
             "Monthly_individual_net_income"] + HX + ["None"]
    A_SKIP = {
        "Participant": "becomes id",
        "Nationality": "coded 1 (Belgian) for all 640, but the paper's Supp. "
                       "Table 1 reports 8 non-Belgians -- unreliable",
        **{c: "time-varying (differs by wave), not a person-level covariate"
           for c in ["Contact_outside", "Contact_inside", "Contact_telephone",
                     "Contact_internet", "Corona_self", "Corona_other",
                     "Week_completed"]},
        "Progress": "survey administration metadata",
        "Duration": "survey administration metadata (used only for linkage)",
        **{c: "composite score" for c in ["CFQ_total", "GDS_total",
           "PWI_pre_total", "PWI_covid_total", "LSNS_total", "BRS_total"]},
        **{c: "single-item activity/sleep rating (two constructs, one item "
              "each per period) -- not a scale"
           for c in ["Activity_pre", "Activity_covid", "Sleep_pre",
                     "Sleep_covid"]},
    }
    acc = set(A_ITEMS) | set(A_COV) | set(A_SKIP)
    assert not [c for c in a.columns if c not in acc], \
        [c for c in a.columns if c not in acc]
    assert not [c for c in acc if c not in a.columns]

    # ---- link the 2023 rows to 2021 participant numbers ---------------------
    t1map = {f"Lubben{i}": f"LSNS{i}" for i in range(1, 7)}
    t1map.update({f"PWI{i}_post": f"PWI{i}_covid" for i in range(1, 9)})
    t1map.update({"Activity_post": "Activity_covid", "Sleep_post": "Sleep_covid",
                  "PWI_post_total": "PWI_covid_total",
                  "Lubben_total": "LSNS_total"})
    bt1 = b.rename(columns=t1map)
    key = [c for c in A_ITEMS if c in bt1.columns] + [
        "Age", "Gender", "Duration", "Educational_level",
        "Monthly_individual_net_income", "Activity_pre", "Sleep_pre"]
    K = len(key)
    assert K == 81, K
    A = a[key].to_numpy(float)
    B = bt1[key].to_numpy(float)
    link = {}
    for i in range(len(B)):
        eq = ((A == B[i]) | (np.isnan(A) & np.isnan(B[i]))).sum(axis=1)
        j = int(eq.argmax())
        best, second = eq[j], np.sort(eq)[-2]
        assert second <= K - 15 and best >= K - 1, (b.Participant[i], best, second)
        if best == K - 1:  # the one disagreement must be gender (corrected in 2023)
            diff = [k for k, x, y in zip(key, A[j], B[i])
                    if x != y and not (np.isnan(x) and np.isnan(y))]
            assert diff == ["Gender"], diff
        link[int(b.Participant[i])] = int(a.Participant[j])
    assert len(set(link.values())) == 371
    b = b.copy()
    b["id"] = b["Participant"].map(link)
    print(f"  linked 371/371 T2-T3 participants onto the 2021 numbering")

    # ---- books: 2023 file ---------------------------------------------------
    B_T1 = [c for c in b.columns[:108]]           # T1 block, duplicate of 2021
    m2 = {"M2_" + c: c for c in CFQ + GDS + SUBDOM}
    m2.update({f"M2_PWI{i}_post": f"PWI{i}" for i in range(1, 9)})
    m2.update({"M2_CognFunct_pre": "CognFunct_pre",
               "M2_CognFunct_post": "CognFunct_now"})
    m3 = {"M3_" + c: c for c in CFQ + GDS + SUBDOM}
    m3.update({f"M3_PWI{i}_post": f"PWI{i}" for i in range(1, 9)})
    m3.update({"M3_CognFunct_post": "CognFunct_now"})
    m3.update({f"M3_HADS{i}": f"HADS_A{i}" for i in range(1, 8)})
    m3.update({f"M3_CERQ{i}": f"CERQ{i}" for i in range(1, 19)})
    B_SKIP = {"id": "linkage (added above)"}
    for w in ("M2_", "M3_"):
        B_SKIP.update({w + c: "time-varying / administration metadata" for c in
                       ["Week_completed", "Progress", "Duration", "Age",
                        "Contact_outside", "Contact_inside",
                        "Contact_telephone", "Contact_internet", "Corona_self",
                        "Corona_other"]})
        B_SKIP.update({w + c: "composite score" for c in
                       ["PWI_post_total", "CFQ_total", "GDS_total"]})
        B_SKIP.update({w + c: "single-item activity/sleep rating -- not a scale"
                       for c in ["Activity_post", "Sleep_post"]})
        B_SKIP[w + "Gender"] = "used only to confirm the T1 gender correction"
    B_SKIP["M3_Vaccin"] = "single attitude question asked once at T3"
    B_SKIP["M3_HADS_total"] = "composite score"
    B_SKIP.update({c: "CERQ-short strategy sum (composite)" for c in b.columns
                   if c.startswith("M3_CERQ_")})
    accb = set(B_T1) | set(m2) | set(m3) | set(B_SKIP)
    assert not [c for c in b.columns if c not in accb], \
        [c for c in b.columns if c not in accb]
    print("  [skip] 2023 T1 block (108 cols): exact duplicate of the 2021 rows "
          "(verified by the linkage above); only its gender is used")

    # T1 gender: the 2023 file corrects 3 participants; take its value where
    # all three waves of the 2023 file agree.
    ga = a.set_index("Participant")["Gender"].copy()
    bg = b.set_index("id")[["Gender", "M2_Gender", "M3_Gender"]]
    for pid, row in bg.iterrows():
        if row["Gender"] != ga[pid]:
            assert row["Gender"] == row["M2_Gender"] == row["M3_Gender"], row
            print(f"  gender for id {pid}: {ga[pid]} -> {row['Gender']} "
                  f"(2023 file, consistent over T1-T3)")
            ga[pid] = row["Gender"]

    # ---- covariates (T1, person-level) --------------------------------------
    cov = pd.DataFrame({"id": a["Participant"].astype(int)})
    cov["cov_age"] = a["Age"].astype(int)
    cov["cov_gender"] = a["Participant"].map(ga).astype(int)  # 1 m, 2 f, 3 other
    cov["cov_living_situation"] = a["Living_situation"]
    cov["cov_cohabitants"] = a["Cohabitants"]
    cov["cov_education"] = a["Educational_level"]
    cov["cov_work_situation"] = a["Work_situation"]
    cov["cov_income"] = a["Monthly_individual_net_income"].where(
        a["Monthly_individual_net_income"] != 10).astype("Int64")  # 10 = refused
    flags = a[HX].fillna(0).astype(int)
    answered = (a["None"] == 1) | (flags.sum(axis=1) > 0)
    assert not ((a["None"] == 1) & (flags.sum(axis=1) > 0)).any()
    for h in HX:
        cov[f"cov_hx_{h.lower()}"] = flags[h].where(answered).astype("Int64")
    COVS = [c for c in cov.columns if c != "id"]

    # ---- long frames per wave ------------------------------------------------
    w1 = a.rename(columns={f"PWI{i}_covid": f"PWI{i}" for i in range(1, 9)})
    w1 = w1.rename(columns={"Participant": "id"})
    w2 = b[["id"] + list(m2)].rename(columns=m2)
    w3 = b[["id"] + list(m3)].rename(columns=m3)

    def melt(df, items, wave):
        cols = [c for c in items if c in df.columns]
        t = df[["id"] + cols].melt(id_vars="id", var_name="item",
                                   value_name="resp").dropna(subset=["resp"])
        t["wave"] = wave
        return t

    PWI = rng("PWI", 8)
    PWI_PRE = [f"PWI{i}_pre" for i in range(1, 9)]
    SUBJ = ["Cognitive_functioning"] + SUBDOM + ["CognFunct_pre",
                                                 "CognFunct_now"]
    HADS, CERQ = rng("HADS_A", 7), rng("CERQ", 18)
    tables = {
        # name: (items, waves, permitted values, source-supported construct map)
        "depue_2023_cfq": (CFQ, (1, 2, 3), range(0, 5)),
        "depue_2023_gds15": (GDS, (1, 2, 3), range(0, 2)),
        "depue_2023_pwi": (PWI + PWI_PRE, (1, 2, 3), range(0, 11)),
        "depue_2023_subjcog": (SUBJ, (1, 2, 3), None),
        "depue_2021_lsns6": (LSNS, (1,), range(0, 6)),
        "depue_2021_brs": (BRS, (1,), range(1, 6)),
        "depue_2023_hads_a": (HADS, (3,), range(0, 4)),
        "depue_2023_cerq": (CERQ, (3,), range(1, 6)),
    }
    subj_perm = {"Cognitive_functioning": set(range(1, 4)),
                 **{c: set(range(1, 6)) for c in SUBDOM},
                 "CognFunct_pre": set(range(0, 11)),
                 "CognFunct_now": set(range(0, 11))}
    assert len(tables) == len(set(tables)), "duplicate output filenames"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = {1: w1, 2: w2, 3: w3}
    for name, (items, waves, perm) in tables.items():
        t = pd.concat([melt(frames[w], items, w) for w in waves],
                      ignore_index=True)
        if name == "depue_2023_pwi":
            assert (t["resp"] % 10 == 0).all()
            t["resp"] = t["resp"] / 10          # stored x10; back to 0-10
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t["id"] = t["id"].astype(int)
        assert set(t["item"]) == set(items), (name, set(items) - set(t["item"]))
        t = t.merge(cov, on="id", how="left", validate="many_to_one")
        cols = ["id", "item", "resp"] + (["wave"] if len(waves) > 1 else []) + COVS
        t = t[cols].sort_values(["id"] + (["wave"] if len(waves) > 1 else [])
                                + ["item"]).reset_index(drop=True)
        keys = ["id", "item"] + (["wave"] if len(waves) > 1 else [])
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100, name

        pv = subj_perm if perm is None else {i: set(perm) for i in items}
        for i, s in pv.items():
            bad = set(t.loc[t["item"] == i, "resp"]) - s
            assert not bad, (name, i, bad)
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")

        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        wv = (f" waves={ {int(k): int(v) for k, v in t.groupby('wave')['id'].nunique().items()} }"
              if "wave" in t else "")
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}{wv}")


if __name__ == "__main__":
    convert()
