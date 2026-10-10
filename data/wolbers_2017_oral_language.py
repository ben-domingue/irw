#!/usr/bin/env python3
# Source: https://doi.org/10.17026/dans-xjd-rgey
# DOI: 10.17026/dans-xjd-rgey (dataset; the study report is deposited with it)
#   Wolbers, M., Teunissen, C., van Druten, L., & Geelen, A. (2017). Peilingsonderzoek
#   Mondelinge Taalvaardigheid in het basisonderwijs [Data set]. DANS Data Station
#   Social Sciences and Humanities. KBA Nijmegen, for the Dutch Inspectorate of
#   Education (Peil.onderwijs), with Expertisecentrum Nederlands, Bureau ICE, ResearchNed.
# Data: "llntotaal_mtv_ivho 271117.sav" (pupil file): 2,324 grade-8 (groep 8) pupils
#       in 121 Dutch primary schools x 206 columns -- background, the Luisteren
#       (listening) test, the Spreken (vlog) and Gesprekken (group conversation) rating
#       forms, and the pupil questionnaire. "2018-01-12_Rapport MTV definitief.pdf"
#       describes the instruments; "Informatie databestanden ... .pdf" says the labels
#       and values are in the data file. The school file (scholentotaal) is not used.
# License: CC0 1.0 (DANS record).
#
# Item text: not shipped. Cheap at both label levels -- Dutch stems in the variable
#   labels for every questionnaire item and every rating criterion, value labels for
#   every option -- but it needs an IRW-written English translation for 13 tables;
#   left for a later pass. The listening items' wording is not in the deposit (the
#   variable labels repeat the item codes); the test ran in the TOA system.
#
# Tables (one row per pupil; id = Leerlingnummer, the study's pupil number;
#   cluster_id = schoolnummer):
#   wolbers_2017_listening      30 PO.NeLu.* items, 0 fout / 1 goed. N=1,531 (the test
#                               was given to a subsample). cov_test_version: A (90%,
#                               fixed order) or B (pupils could navigate), from
#                               Luisteren_toetsB; the report (4.4.2) treats them as one
#                               test.
#   wolbers_2017_speaking       Spreken (a 3-5 minute vlog), 15 trichotomous criteria
#                               (0-2; criterion 14 is only ever 1-2) + criterion 16, the
#                               global judgement (0 zwak .. 4 zeer goed). No rater
#                               column (see below). Item codes spreken_<n>, n = the
#                               criterion number that starts each variable label.
#   wolbers_2017_conversation   Gesprekken (a group conversation in threes), 20 criteria
#                               0-2 + criterion 22, the global judgement 0-4; code 9
#                               ("inbreng is onvoldoende om te beoordelen", too little
#                               input to rate) is a non-response and is dropped.
#                               rater = Beoordelaar. Items gesprek_<n>.
#   wolbers_2017_parent_dutch   QL_8.1-8.4: how well father/mother speak/understand
#                               Dutch, 1 heel goed .. 4 heel slecht; 5 "kan ik niet
#                               invullen" dropped.
#   wolbers_2017_home_lang_act  QL_9.1-9.6: language activities at home last week,
#                               1 nooit, 2 1 of 2 x, 3 vaker dan 2 x.
#   wolbers_2017_lang_act_par   QL_10.1-10.8: language activities together with parents,
#                               same 1-3 scale.
#   wolbers_2017_home_resources QL_11.1-11.9: present at home, 1 nee / 2 ja;
#                               3 "weet ik niet" dropped.
#   wolbers_2017_parent_lit_act QL_12.1-12.7: parents' literacy activities, 1 (bijna)
#                               nooit, 2 soms, 3 (heel) vaak.
#   wolbers_2017_class_contact  QL_13.1-13.6: contact with classmates, 1-5.
#   wolbers_2017_teach_contact  QL_13.7-13.13: contact with the teacher, 1-5.
#   wolbers_2017_speak_climate  QL_13.14-13.16: safe speaking climate in class, 1-5.
#   wolbers_2017_speak_anxiety  QL_14.1, .3, .5, .7, .8: speaking in class is
#                               frightening (the report's "spreken spannend" scale), 1-5.
#   wolbers_2017_speak_enjoy    QL_14.2, .4, .6: speaking in class is fun ("spreken
#                               leuk"), 1-5.
#   The QL_13/14 scale is 1 klopt helemaal niet .. 5 klopt precies, EXCEPT QL_13.2,
#   13.5, 13.13 and 13.15, whose value labels run the other way (1 klopt precies ..
#   5 klopt helemaal niet): the deposit stores those negatively worded items already
#   reversed. Shipped as stored; no other item is recoded.
# Skipped: @0 (precondition "task performed", constant 1); Gesprekken criterion 4
#   ("Gedrag van de toetsleider", whether the test leader may have affected the
#   conversation -- a judgement about the examiner, not the pupil); QL_1-QL_7 and
#   their ANDERS free-text fields (home languages, nominal); all N_* columns (scale
#   and total scores the analysts derived); Score_begrijpend_lezen and its centred
#   copy (another test's score); VOadvies, Leerlinggewicht, Datum_eerste_schooldag,
#   In_Nederland_sinds_jaartal, the per-parent birth-country and education codes and
#   the education dummies (their harmonised versions ship).
# Covariates: cov_sex (Geslacht: 0 vrouw, 1 man), cov_age_months (leeftijdmnd),
#   cov_parent_education (hoogsteopleidingouders: 1 zeer laag .. 4 hoog, 5 onbekend),
#   cov_parents_born_nl (geboortelandouders: 1 nederland, 0 ander geboorteland),
#   cov_pupil_birth_country (Geboorteland_leerling, codes as labelled in the .sav).
# Beoordelaar (rater) is a single column. It is present for exactly the 1,380 pupils
#   with a Gesprekken rating (and for none of the 723 pupils rated on Spreken only),
#   so it is the conversation rater and ships as `rater` on that table only; the
#   deposit has no rater column for the vlogs.

import os
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.17026_dans-xjd-rgey"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DV = "https://ssh.datastations.nl/api"
FNAME = "llntotaal_mtv_ivho 271117.sav"
P = "wolbers_2017_"
COVS = {"Geslacht": "cov_sex", "leeftijdmnd": "cov_age_months",
        "hoogsteopleidingouders": "cov_parent_education",
        "geboortelandouders": "cov_parents_born_nl",
        "Geboorteland_leerling": "cov_pupil_birth_country"}
QL = {  # table suffix -> (items, valid codes)
    "parent_dutch": ([f"QL_8.{i}" for i in range(1, 5)], range(1, 5)),
    "home_lang_act": ([f"QL_9.{i}" for i in range(1, 7)], range(1, 4)),
    "lang_act_par": ([f"QL_10.{i}" for i in range(1, 9)], range(1, 4)),
    "home_resources": ([f"QL_11.{i}" for i in range(1, 10)], range(1, 3)),
    "parent_lit_act": ([f"QL_12.{i}" for i in range(1, 8)], range(1, 4)),
    "class_contact": ([f"QL_13.{i}" for i in range(1, 7)], range(1, 6)),
    "teach_contact": ([f"QL_13.{i}" for i in range(7, 14)], range(1, 6)),
    "speak_climate": ([f"QL_13.{i}" for i in range(14, 17)], range(1, 6)),
    "speak_anxiety": ([f"QL_14.{i}" for i in (1, 3, 5, 7, 8)], range(1, 6)),
    "speak_enjoy": ([f"QL_14.{i}" for i in (2, 4, 6)], range(1, 6)),
}
REVERSED_LABELS = {"QL_13.2", "QL_13.5", "QL_13.13", "QL_13.15"}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"{DV}/datasets/:persistentId/",
                         params={"persistentId": "doi:10.17026/DANS-XJD-RGEY"},
                         headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == FNAME][0]
        r = requests.get(f"{DV}/access/datafile/{fid}?format=original", headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def melt(d, cols, covs, extra=()):
    t = d.melt(id_vars=["id", *extra, "cluster_id"] + covs, value_vars=cols,
               var_name="item", value_name="resp").dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    return t


def main() -> None:
    d, meta = pyreadstat.read_sav(str(fetch()))
    lab = meta.column_names_to_labels
    vl = meta.variable_value_labels
    assert d.shape == (2324, 206) and d["Leerlingnummer"].is_unique
    d["id"] = d["Leerlingnummer"].astype(int)
    d["cluster_id"] = d["schoolnummer"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {}

    # listening
    lis = [c for c in d.columns if c.startswith("PO.NeLu.")]
    assert len(lis) == 30 and d[lis].isin([0, 1, float("nan")]).all().all()
    d["cov_test_version"] = d["Luisteren_toetsB"].map({0: "A", 1: "B"})
    sub = d[d[lis].notna().any(axis=1)]
    t = melt(sub, lis, covs + ["cov_test_version"])
    t = t[["id", "item", "resp", "cluster_id"] + covs + ["cov_test_version"]]
    out[P + "listening"] = (t, {i: {0, 1} for i in lis})

    # rating forms: '@<n>.<criterion>' columns; Spreken block first, then Gesprekken
    at = [c for c in d.columns if c.startswith("@")]
    i1 = [k for k, c in enumerate(at) if c.startswith("@1.")]
    assert len(at) == 17 + 22 and len(i1) == 2
    spreken, gesprek = at[:i1[1]], at[i1[1]:]
    assert spreken[0].startswith("@0.") and len(spreken) == 17 and len(gesprek) == 22
    print("  [skip] @0.PreconditieInhoudelijkeadequaatheid: constant 1")
    assert (d[spreken[0]].dropna() == 1).all()
    d["rater"] = d["Beoordelaar"].astype("Int64")
    for kind, cols, drop_n in (("speaking", spreken[1:], ()), ("conversation", gesprek, (4,))):
        extra = ("rater",) if kind == "conversation" else ()
        num = {c: int(re.match(r"@(\d+)\.", c).group(1)) for c in cols}
        pre = "spreken" if kind == "speaking" else "gesprek"
        keep = [c for c in cols if num[c] not in drop_n]
        for c in cols:
            if num[c] in drop_n:
                print(f"  [skip] {c}: judgement about the test leader, not the pupil")
            # the value labels must agree with the stored codes
            assert set(d[c].dropna().unique()) <= set(vl[c]), c
        x = d[d[keep].notna().any(axis=1)].copy()
        assert x["rater"].notna().all() == (kind == "conversation")
        x = x.rename(columns={c: f"{pre}_{num[c]:02d}" for c in keep})
        codes = [f"{pre}_{num[c]:02d}" for c in keep]
        t = melt(x, codes, covs, extra=extra)
        n9 = (t["resp"] == 9).sum()
        t = t[t["resp"] != 9]
        print(f"  [{kind}] dropped {n9} code-9 (too little input to rate) responses")
        glob = codes[-1]
        assert t.loc[t["item"] != glob, "resp"].isin([0, 1, 2]).all()
        assert t.loc[t["item"] == glob, "resp"].isin(range(5)).all()
        t = t[["id", "item", "resp", "cluster_id"] + covs + list(extra)]
        pv = {c: ({0, 1, 2, 3, 4} if c == glob else {0, 1, 2}) for c in codes}
        out[P + kind] = (t, pv)

    # questionnaire
    for suf, (its, valid) in QL.items():
        for c in its:
            labs = vl[c]
            if c in REVERSED_LABELS:
                assert labs[1.0] == "klopt precies", c
            elif suf in ("class_contact", "teach_contact", "speak_climate",
                         "speak_anxiety", "speak_enjoy"):
                assert labs[1.0] == "klopt helemaal niet", c
        x = d[d[its].notna().any(axis=1)]
        t = melt(x, its, covs)
        bad = ~t["resp"].isin(list(valid))
        if bad.any():
            print(f"  [{suf}] dropped {bad.sum()} non-response codes "
                  f"{sorted(t.loc[bad, 'resp'].unique())}")
        t = t[~bad]
        t = t[["id", "item", "resp", "cluster_id"] + covs]
        out[P + suf] = (t, {i: set(valid) for i in its})

    # books: every source column is an item, a covariate/design column, or skipped
    used = set(lis) | set(at) | {c for its, _ in QL.values() for c in its} \
        | set(COVS.values()) | {"Leerlingnummer", "schoolnummer", "Luisteren_toetsB",
                                "Beoordelaar"}
    skip_re = re.compile(r"^(N_|QL_\d+(\.\d+)?_|QL_\d+ANDERS$|Score_begrijpend|n_cen|"
                         r"VOadvies|Leerlinggewicht|Datum_eerste|In_Nederland|"
                         r"Geboorteland_ouder|Opleidingscategorie)")
    rest = [c for c in d.columns if c not in used and c not in
            ("id", "cluster_id", "rater", "cov_test_version") and not skip_re.match(c)]
    assert not rest, rest
    for name, (t, _) in out.items():
        out[name] = (t.sort_values(["id", "item"]).reset_index(drop=True), out[name][1])
    emit(out)


if __name__ == "__main__":
    main()
