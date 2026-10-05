#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6884994
# DOI: 10.7717/peerj.7575
#   "The discriminative power of the ReproQ: a client experience questionnaire
#   in maternity care" (Scheerhagen, van Stel, Franx, Birnie & Bonsel, 2019),
#   PeerJ 7:e7575.
# Data: PeerJ supplementary files peerj-07-7575-s001.sav (antenatal ReproQ,
#       6387 rows, pregnancy phase) and peerj-07-7575-s002.sav (postnatal
#       ReproQ, 9588 rows, birth + postnatal phases), fetched from the Europe
#       PMC supplementaryFiles zip. s003/s004 are R output and a technical
#       supplement (no data).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary files.
#
# Item text: not shipped. Variable labels exist on every item but are short
#   English glosses ("Item Considering your privacy , Birth,"), not the wording
#   respondents read: the ReproQ was administered in Dutch and neither the
#   deposit nor the SI carries the questionnaire. Value labels (never /
#   sometimes / most of the time / always + the not-applicable codes) are
#   present on every item. The wording is in the ReproQ development paper
#   (Scheerhagen et al. 2015, PLoS ONE 10:e0117031 and its S1 appendix).
#
# Table: scheerhagen_2019_reproq -- ReproQ client-experience items (WHO
#   responsiveness domains: dignity R, autonomy A, confidentiality P,
#   communication C, prompt attention T, social consideration S, basic
#   amenities F, choice/continuity K), 1 = never ... 4 = always.
#   Item codes are the .sav column names. In s002, suffix _A = birth phase and
#   _B = postnatal phase (from the variable labels); RQ_A_Pnb and RQ_A_Gbp have
#   no suffix and refer to birth. In s001 every phase item is suffixed _B but
#   means PREGNANCY, which would collide with s002's postnatal _B, so s001 codes
#   are renamed reversibly: trailing "_B" -> "_P", and "_P" is appended to the
#   two unsuffixed s001 items (RQ_A_Svd -> RQ_A_Svd_P, RQ_A_Gbp -> RQ_A_Gbp_P).
#   wave = 1 for the antenatal questionnaire (s001), 2 for the postnatal (s002).
#
# Recoding (non-response categories are not steps on the scale -> dropped):
#   4-point items: codes 1-4 kept; 5 (no emergency / do not remember / no
#     postnatal care / i was home / no need / no change in professional / no
#     referral) dropped. s001 RQ_S_Rhm_B carries 116 unlabelled 5s, also dropped.
#   RQ_A_Gbp(_P) birth-plan influence: 1 determined it all myself ... 4 no
#     influence (without a medical reason) kept; 5 (no influence, medical
#     reason) and 6 (not come up yet) dropped.
#   RQ_A_Pnb pain-medication decision: 1 all mine, 2 involved, 3 not involved
#     but wanted to be, kept; 4 (did not want to be involved), 5/6 (not
#     applicable) dropped.
#   RQ_A_Svd_P Down's-syndrome screening offered: 1 yes, 2 no kept; 3 (don't
#     recall) dropped.
#   The *_M, *_Cat4/_Cat5 recodes, domain/total scores and overall ratings are
#   not shipped (derived, or single global items outside the ReproQ).
#
# id. `token` is the survey's invitation token (6-digit number or 15-character
#   random string; no PII). It is not shipped -- persons get a row-index id.
#   It links the two files: after de-duplication 2,770 tokens occur once in
#   each (2,743 before; agreement measured on those): the
#   perinatal unit agrees 91%, parity 99% and age band 90% (vs 3%/48%/32% under
#   random pairing), so they are one woman at two time points and share an id.
#   Duplicates: rows identical on every column INCLUDING token are double
#   submissions (44 pairs in s001, 47 in s002, plus 3 pairs among the 1,590
#   blank-token s002 rows); one copy is kept. Tokens that recur with different
#   answers (43 in s001, 49 in s002; nearly all in different perinatal units)
#   are token collisions between different women: each row is its own person
#   and none of them is linked across files. Blank-token rows are never linked.
#   Rows identical in content but under different tokens (8 pairs in s001, 5 in
#   s002, all near-straight-line ceiling patterns) are kept.
#
# Covariates, one value per person (taken from the antenatal record when the
#   woman has one, else the postnatal): cov_age_cat (1 <=24, 2 25-29, 3 30-34,
#   4 >=35), cov_parity (1 primiparous, 2 multiparous); antenatal only:
#   cov_ethnicity (1 western, 2 non-western), cov_education (1 low, 2 middle,
#   3 high); 999 = missing -> NA. cov_unit is the perinatal unit (VSVnr,
#   an anonymous number) of the same record. All are SPSS-coded.

import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW = REPO_ROOT / "automated_finding" / "runs" / "raw" / "scheerhagen_2019"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6884994/supplementaryFiles"
NAME = "scheerhagen_2019_reproq"


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    z = RAW / "supp.zip"
    if not z.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        z.write_bytes(r.content)
    out = []
    for f in ("peerj-07-7575-s001.sav", "peerj-07-7575-s002.sav"):
        p = RAW / f
        if not p.exists():
            p.write_bytes(zipfile.ZipFile(z).read(f))
        out.append(pyreadstat.read_sav(str(p)))
    return out


def is_item(c):
    return (c.startswith("RQ_") and "_M" not in c and "Dom" not in c
            and "EvT" not in c)


def recode(item, v):
    stem = item[:8]  # e.g. RQ_A_Gbp
    if stem == "RQ_A_Gbp":
        keep = {1, 2, 3, 4}
    elif stem == "RQ_A_Pnb":
        keep = {1, 2, 3}
    elif stem == "RQ_A_Svd":
        keep = {1, 2}
    else:
        keep = {1, 2, 3, 4}
    return v.where(v.isin(keep))


def main():
    (a, ma), (b, mb) = fetch()
    assert a.shape == (6387, 98) and b.shape == (9588, 181), (a.shape, b.shape)

    ia = [c for c in a.columns if is_item(c)]
    ib = [c for c in b.columns if is_item(c)]
    assert len(ia) == 30 and len(ib) == 58, (len(ia), len(ib))
    for m, items in ((ma, ia), (mb, ib)):
        for c in items:
            lab = m.variable_value_labels[c]
            if c[:8] not in ("RQ_A_Gbp", "RQ_A_Pnb", "RQ_A_Svd"):
                assert lab[1.0] == "never" and lab[4.0] == "always", (c, lab)
    # phase in the variable label: s001 = pregnancy, s002 _A birth / _B postnatal
    for c in ia:
        if c.endswith("_B"):
            assert "Pregnancy" in ma.column_names_to_labels[c], c
    for c in ib:
        if c.endswith("_A"):
            assert "Birth" in mb.column_names_to_labels[c], c
        if c.endswith("_B"):
            assert "Postnatal" in mb.column_names_to_labels[c], c

    ren_a = {}
    for c in ia:
        ren_a[c] = c[:-2] + "_P" if c.endswith("_B") else c + "_P"
    assert set(ren_a.values()).isdisjoint(ib)
    assert len(set(ren_a.values())) == len(ia)

    # ---- columns not shipped (books must balance) ----
    cov_a = {"SD_Lft_M_Cat4": "cov_age_cat", "EE_Par_M_Cat2": "cov_parity",
             "SD_Etm_M_Cat2": "cov_ethnicity", "SD_Opl_M_Cat3": "cov_education",
             "VSVnr": "cov_unit"}
    cov_b = {"SD_Lft_M_Cat4": "cov_age_cat", "EE_Par_M_Cat2": "cov_parity",
             "VSVnr": "cov_unit"}
    for d, items, cov, nm in ((a, ia, cov_a, "s001"), (b, ib, cov_b, "s002")):
        skipped = [c for c in d.columns if c not in items and c not in cov
                   and c != "token"]
        for c in skipped:
            assert ("_M" in c or "Dom" in c or "EvT" in c or c.startswith("OV_")
                    or c.startswith("VSV") or c.startswith("F_VSV")), (nm, c)
        print(f"  {nm}: skipped {len(skipped)} derived/recode/global/filter "
              f"columns (*_M*, *Dom*, *EvT*, OV_*, VSV size/filters)")
        assert len(skipped) + len(items) + len(cov) + 1 == d.shape[1]

    # ---- duplicates: identical on every column incl. token ----
    na, nb = len(a), len(b)
    a = a[~a.duplicated(keep="first")].reset_index(drop=True)
    b = b[~b.duplicated(keep="first")].reset_index(drop=True)
    print(f"  dropped exact duplicate submissions: s001 {na - len(a)}, "
          f"s002 {nb - len(b)}")
    assert na - len(a) == 44 and nb - len(b) == 50, (na - len(a), nb - len(b))

    # ---- person keys ----
    def keys(d, tag):
        tok = d["token"].astype(str).str.strip()
        cnt = tok.map(tok.value_counts())
        ok = (tok != "") & (cnt == 1)
        return np.where(ok, "tok:" + tok, f"{tag}:" + d.index.astype(str))
    a["pkey"] = keys(a, "a")
    b["pkey"] = keys(b, "b")
    linked = set(a["pkey"]) & set(b["pkey"])
    assert all(k.startswith("tok:") for k in linked)
    print(f"  women linked across the two questionnaires: {len(linked)}")
    order = list(dict.fromkeys(list(a["pkey"]) + list(b["pkey"])))
    pid = {k: i + 1 for i, k in enumerate(order)}
    a["id"] = a["pkey"].map(pid)
    b["id"] = b["pkey"].map(pid)

    # ---- covariates: one value per person, antenatal record first ----
    a = a.rename(columns=cov_a)
    b = b.rename(columns=cov_b)
    covs = ["cov_age_cat", "cov_parity", "cov_ethnicity", "cov_education",
            "cov_unit"]
    pc = pd.concat([a[["id"] + covs], b[["id"] + cov_b_vals(cov_b)]],
                   ignore_index=True)
    pc = pc.replace(999.0, np.nan)
    pc = pc.groupby("id", sort=False).first()  # first non-null, s001 first
    for c in covs:
        pc[c] = pc[c].astype("Int64")

    # ---- long ----
    la = a.rename(columns=ren_a).melt(id_vars=["id"], value_vars=list(
        ren_a.values()), var_name="item", value_name="resp")
    la["wave"] = 1
    lb = b.melt(id_vars=["id"], value_vars=ib, var_name="item",
                value_name="resp")
    lb["wave"] = 2
    t = pd.concat([la, lb], ignore_index=True)
    n0 = t["resp"].notna().sum()
    t["resp"] = t.groupby("item", group_keys=False)["resp"].apply(
        lambda v: recode(v.name, v))
    t = t.dropna(subset=["resp"])
    print(f"  non-response codes dropped: {n0 - len(t)}")
    t["resp"] = t["resp"].astype(int)
    t = t.merge(pc.reset_index(), on="id", how="left")
    t = t[["id", "item", "resp", "wave"] + covs].sort_values(
        ["id", "wave", "item"])
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100

    pv = {}
    for i in t["item"].unique():
        s = i[:8]
        pv[i] = ({1, 2} if s == "RQ_A_Svd" else {1, 2, 3} if s == "RQ_A_Pnb"
                 else {1, 2, 3, 4})
        assert set(t.loc[t["item"] == i, "resp"]) <= pv[i], i
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail}")
    report = irw_validate.validate_frame(
        t, label=NAME, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


def cov_b_vals(cov_b):
    return list(cov_b.values())


if __name__ == "__main__":
    main()
