#!/usr/bin/env python3
# Source: https://osf.io/3527a/  (MECO L1: the Multilingual Eye-movement
#   COrpus, L1 releases; release 2.0, version 2.1)
# Papers: Siegelman N, Schroeder S, Acartürk C, et al. (2022). "Expanding
#   horizons of cross-linguistic research on reading: The Multilingual
#   Eye-movement Corpus (MECO)." Behavior Research Methods 54, 2843-2863.
#   https://doi.org/10.3758/s13428-021-01772-6   (wave 1)
#   Wave 2: https://doi.org/10.1038/s41597-025-05453-3 (Scientific Data).
# License: CC BY 4.0 (OSF node 3527a licence record).
# Issue: ben-domingue/irw#2207. Encoding ruled by Ben 2026-10-01.
#
# WHAT IT IS. Adults read 12 short expository texts in their first language
#   while eye-tracked, and after each text answered 4 yes/no comprehension
#   questions: 48 binary items. resp = ACCURACY (1 correct, 0 incorrect), as
#   the release scores it. Only the comprehension accuracy is used here; the
#   eye-movement measures are not (a separate, trials-shaped question).
#
# TWO COLLECTION ROUNDS, ONE TABLE. The release's "wave 1" (13 sites) and
#   "wave 2" (16 sites) are different people, mostly at different sites, so
#   they are not `wave` (same unit measured again). They are pooled, with the
#   round in cov_sample (1, 2). id = uniform_id, which the readme says to use
#   and which never repeats across the rounds (asserted).
#   cov_language = language (English name); cov_site = the release's site
#   code (wave 2 has several sites per language: ge_po/ge_zu,
#   hi_iiith/hi_iitk, ch_s/ch_t).
#
# ITEM CODES: SHARED ONLY WHERE THE QUESTION IS THE SAME. The 12 texts share
#   topics everywhere, but only 5 are translations of a common English
#   original: texts 1, 3, 7, 11, 12 (is.matched = 1 in the authors'
#   simiarlity.osf.csv and simiarlity.osf.w2.csv, identical in both rounds).
#   The other 7 were written locally per language.
#   * Matched texts: text{t}_q{q}, shared by every site, EXCEPT:
#     - wave-1 cells whose question is a different question from the English
#       (read from comp-questions.xlsx, all 13 sites x 20 questions):
#       ee t3 q1, q2 (ethics / IOC ban instead of health effects / calming);
#       sp t3 q3 (repeats q4's wording); he t1 q3 ("closed" in peace, not
#       "open"); he t12 q4 and ru t12 q4 (regions issuing plates); gr t12 q2
#       (WWI, not WWII); tr t12 q3 (whether plates are *required* for boats,
#       not whether registers *include* them: a different proposition, so
#       split). These get {site}_text{t}_q{q}. A wave-2 site that reused a
#       wave-1 site's texts verbatim (no, tr) inherits its deviations, on the
#       same assumption that shares its local-text codes across rounds.
#     - Wave 2 published no question wording at all, so its matched
#       questions share codes on the authors' design (Ben, 10-01), unverified,
#       with two exceptions where the responses contradict it (leave-one-out
#       correlation of per-question accuracy with every other site, matched
#       texts only): ru_mo is negative on 4 of 5 matched texts and does not
#       reproduce wave-1 Russian on verbatim-identical texts (no text shift
#       explains it), so ALL its items are site-specific; ba is negative on
#       text 11 alone (mean accuracy 0.49 vs ~0.9 elsewhere), so ba text 11
#       is site-specific.
#   * Local texts: {version}_text{t}_q{q}, one version per distinct wording
#     (texts compared after lower-casing and dropping punctuation and
#     whitespace). A version is shared across sites and rounds only where the
#     text is identical: no and tr (both rounds), en with en_uk, ru with
#     nobody (ru_mo is site-specific, above), hi_iiith with hi_iitk except
#     text 5 (the authors' supp texts_wave2.xlsx Sheet2 marks iitk texts 3,
#     5, 11 "dif"; 3 and 11 are matched). German wave 2 (ge_po and ge_zu,
#     identical to each other) is a revised text set: version "ge_v2" where it
#     differs from wave 1 (texts 2, 4, 5, 6, 9, 10), "ge" where it does not
#     (text 8). sp_ch differs from sp on texts 6, 8, 10 (localised wording).
#     ch_s and ch_t are different scripts and get their own codes.
#   So the table is sparse by design: a version-specific item is answered
#   only by its own site(s). See metadata/data_notes.csv.
#
# Known gaps, kept as published: the 42 wave-1 Norwegian readers have 47
#   questions (text 6 q4 was not administered, per the readme). Wave 2's
#   readme says "24 questions"; the data hold 48 per reader.

import re
import sys
import unicodedata
from io import BytesIO
from pathlib import Path

import pandas as pd
import pyreadr
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
TABLE = "meco_l1_comprehension"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OSF = "https://osf.io/download/{}/"
# release 2.0 / version 2.1
FILES = {
    "w1_acc": "xdt3c",      # wave 1/primary data/comprehension data/joint_l1_acc_full_breakdown.rda
    "w2_acc": "y76a9",      # wave 2/.../joint_l1_wave2_acc_full_breakdown_trimmed.rda
    "w1_texts": "mz48p",    # wave 1/auxiliary files/reading task materials/supp texts.xlsx
    "w2_texts": "nukg9",    # wave 2/auxiliary files/reading task materials/supp texts_wave2.xlsx
    "w1_sim": "hjsm6",      # wave 1/.../simiarlity.osf.csv
    "w2_sim": "x7sf5",      # wave 2/.../simiarlity.osf.w2.csv
}

# site code -> (cov_sample, cov_language, row label in the supp texts sheet)
SITES = {
    "du": (1, "Dutch", "Dutch"), "ee": (1, "Estonian", "Estonian"),
    "en": (1, "English", "English"), "fi": (1, "Finnish", "Finnish"),
    "ge": (1, "German", "German"), "gr": (1, "Greek", "Greek"),
    "he": (1, "Hebrew", "Hebrew"), "it": (1, "Italian", "Italian"),
    "ko": (1, "Korean", "Korean"), "no": (1, "Norwegian", "Norwegian"),
    "ru": (1, "Russian", "Russian"), "sp": (1, "Spanish", "Spanish"),
    "tr": (1, "Turkish", "Turkish"),
    "ba": (2, "Basque", "Basque"),
    "bp": (2, "Portuguese", "Portuguese(Brazil)"),
    "ch_s": (2, "Chinese", "Chinese(simplified)"),
    "ch_t": (2, "Chinese", "Chinese(traditional)"),
    "da": (2, "Danish", "Danish"), "en_uk": (2, "English", "English (uk)"),
    "ge_po": (2, "German", "German Wave 2"),
    "ge_zu": (2, "German", "German Wave 2 Zurich"),
    "hi_iiith": (2, "Hindi", "Hindi iiith"),
    "hi_iitk": (2, "Hindi", "Hindi iitk"),
    "ic": (2, "Icelandic", "Icelandic"), "no2": (2, "Norwegian", "Norwegian Wave 2"),
    "ru_mo": (2, "Russian", "Russian Wave 2"), "se": (2, "Serbian", "Serbian"),
    "sp_ch": (2, "Spanish", "Spanish(Chile)"),
    "tr2": (2, "Turkish", "Turkish Wave 2"),
}
# the release reuses "no" and "tr" as wave-2 site codes; keyed apart here only
W2_ALIAS = {"no": "no2", "tr": "tr2"}

MATCHED = [1, 3, 7, 11, 12]
LOCAL = [t for t in range(1, 13) if t not in MATCHED]
# (site, text, question) whose wave-1 question differs from the English one
DEVIANT = {("ee", 3, 1), ("ee", 3, 2), ("sp", 3, 3), ("he", 1, 3),
           ("he", 12, 4), ("ru", 12, 4), ("gr", 12, 2), ("tr", 12, 3)}
SITE_SPECIFIC_ALL = {"ru_mo"}           # responses contradict equivalence
SITE_SPECIFIC_TEXT = {("ba", 11)}
# Sheet2 of supp texts_wave2.xlsx: iitk texts that differ from iiith
IITK_DIF = {3, 5, 11}
# names for versions shared only by wave-2 sites
W2_VERSION_LABEL = {frozenset({"ge_po", "ge_zu"}): "ge_v2",
                    frozenset({"hi_iiith", "hi_iitk"}): "hi"}


def fetch(key: str) -> bytes:
    r = requests.get(OSF.format(FILES[key]), headers=UA, timeout=300)
    r.raise_for_status()
    return r.content


def read_rda(key: str) -> pd.DataFrame:
    path = OUT_DIR / f"_meco_{key}.rda"
    path.write_bytes(fetch(key))
    res = pyreadr.read_r(str(path))
    path.unlink()
    (df,) = res.values()
    return df


def norm(s) -> str:
    s = unicodedata.normalize("NFC", str(s)).lower()
    s = s.replace("\\\\n", " ").replace("\\n", " ")
    return re.sub(r"[\W_]+", "", s)


def texts() -> dict:
    out = {}
    for key in ("w1_texts", "w2_texts"):
        d = pd.read_excel(BytesIO(fetch(key)), header=None, sheet_name=0)
        for i in range(1, len(d)):
            label = d.iloc[i, 0]
            if pd.isna(label):
                continue
            out[str(label).strip()] = [norm(d.iloc[i, j]) for j in range(1, 13)]
    return out


def version_labels(tx: dict) -> dict:
    """(site, local text) -> version label, sharing only identical wording."""
    lab = {}
    for t in LOCAL:
        groups = {}
        for site, (_, _, row) in SITES.items():
            if site in SITE_SPECIFIC_ALL:
                lab[(site, t)] = site
                continue
            key = tx[row][t - 1]
            if site == "hi_iitk" and t in IITK_DIF:
                key = "iitk-dif:" + key
            groups.setdefault(key, []).append(site)
        for members in groups.values():
            w1 = [s for s in members if SITES[s][0] == 1]
            assert len(w1) <= 1, (t, members)
            if w1:
                name = w1[0]
            elif len(members) == 1:
                name = members[0]
            else:
                name = W2_VERSION_LABEL[frozenset(members)]
            for s in members:
                lab[(s, t)] = name
    return lab


def item_code(site: str, t: int, q: int, lab: dict) -> str:
    out_site = {"no2": "no", "tr2": "tr"}.get(site, site)
    if t in MATCHED:
        w1_twin = {"no2": "no", "tr2": "tr"}.get(site)
        if site in SITE_SPECIFIC_ALL or (site, t) in SITE_SPECIFIC_TEXT:
            return f"{out_site}_text{t}_q{q}"
        if (site, t, q) in DEVIANT or (w1_twin and (w1_twin, t, q) in DEVIANT):
            return f"{out_site}_text{t}_q{q}"
        return f"text{t}_q{q}"
    return f"{lab[(site, t)]}_text{t}_q{q}"


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # the matched set, from the authors' own files, must be the same in both rounds
    for key in ("w1_sim", "w2_sim"):
        sim = pd.read_csv(BytesIO(fetch(key)))
        got = sorted(sim.loc[sim["is.matched"] == 1, "text.num"].unique())
        assert got == MATCHED, (key, got)

    w1 = read_rda("w1_acc")
    w1 = pd.DataFrame({"id": w1["uniform_id"].astype(str),
                       "site": w1["lang"].astype(str),
                       "text": w1["trialid"].astype(int),
                       "q": w1["QUESTIONNUM"].astype(int),
                       "resp": w1["ACCURACY"].astype(int)})
    w2 = read_rda("w2_acc")
    w2 = pd.DataFrame({"id": w2["uniform_id"].astype(str),
                       "site": w2["lang"].astype(str).replace(W2_ALIAS),
                       "text": w2["number"].astype(int),
                       "q": w2["QUESTIONNUM"].astype(int),
                       "resp": w2["ACCURACY"].astype(int)})
    assert len(w1) == 27462 and w1["id"].nunique() == 573, (len(w1), w1["id"].nunique())
    assert len(w2) == 31296 and w2["id"].nunique() == 652, (len(w2), w2["id"].nunique())
    assert not set(w1["id"]) & set(w2["id"])
    d = pd.concat([w1, w2], ignore_index=True)
    assert set(d["site"]) == set(SITES), set(d["site"]) ^ set(SITES)
    assert d["text"].between(1, 12).all() and d["q"].between(1, 4).all()
    assert d["resp"].isin([0, 1]).all()

    lab = version_labels(texts())
    d["item"] = [item_code(s, t, q, lab) for s, t, q in zip(d["site"], d["text"], d["q"])]
    d["cov_sample"] = d["site"].map(lambda s: SITES[s][0])
    d["cov_language"] = d["site"].map(lambda s: SITES[s][1])
    d["cov_site"] = d["site"].replace({"no2": "no", "tr2": "tr"})

    long = d[["id", "item", "resp", "cov_sample", "cov_language", "cov_site"]] \
        .sort_values(["cov_sample", "cov_site", "id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    per_id = long.groupby("id").size()
    no1 = set(long.loc[(long.cov_sample == 1) & (long.cov_site == "no"), "id"])
    assert (per_id[list(no1)] == 47).all() and (per_id.drop(list(no1)) == 48).all()

    pv = {i: {0, 1} for i in long["item"].unique()}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")

    shared = sorted(i for i in long["item"].unique() if i.startswith("text"))
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} (shared {len(shared)}, "
          f"site/version-specific {long['item'].nunique() - len(shared)})")
    print(long.groupby(["cov_sample", "cov_site"]).agg(
        rows=("id", "size"), ids=("id", "nunique")).to_string())


if __name__ == "__main__":
    convert()
