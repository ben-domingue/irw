#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10567698
# DOI: 10.1038/s41598-023-44300-6
#   "Long-lasting effects of World War II trauma on PTSD symptoms and
#   embodiment levels in a national sample of Poles" (Rzeszutek, Dragan,
#   Lis-Turlejska, Schier, Holas, Pieta, Van Hoy, Drabarek, Poncyliusz,
#   Michalowska, Wdowczyk, Borowska & Szumial, 2023), Scientific Reports 13:17348.
# Data: the article's supplementary files, fetched from the Europe PMC
#       supplementaryFiles zip: 41598_2023_44300_MOESM2_ESM.xlsx (sheet "dane2",
#       1,598 x 627, one row per respondent, all numeric except one free-text
#       column). The other SI file, MOESM1_ESM.docx, is the English "Knowledge
#       about World War II events" questionnaire (27 events x yes/no/don't know).
#       There is no codebook; column meanings come from the paper's Methods and
#       Table 2 and from the checks asserted below.
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# PII: `pds5inne` (PDS-5 "other traumatic event, specify") holds free-text
#   narratives of respondents' own traumatic events naming places and family
#   deaths. Ruled by ben-domingue 2026-10-04: drop the column and ship. It is
#   dropped immediately after reading and is never printed or written. It is
#   the ONLY non-numeric column in the file (asserted): no other free-text,
#   name, e-mail, phone, date-of-birth, address or ID column exists. `year`
#   is age in whole years (mean 48.78, SD 20.50, range 18-97 -- the paper's
#   figures exactly), not a birth date. The source `Id` (1..1598) is replaced
#   by the row index.
#
# Item text: not shipped. Both label levels empty: the .xlsx has no variable
#   labels or value labels, only short Polish column codes (problemy_1_22_r_r1,
#   sdc_r1, rapr_r_r1, kszz_r1). The wording lives in the published Polish
#   adaptations cited by the paper -- Danieli Inventory (ref 18), PDS-5 (Foa et
#   al. 2016 / Polish adaptation, ref 52), Experience of Embodiment Scale
#   (Piran et al.; Polish adaptation, ref 53), SWLS (Diener 1985; Polish
#   Juczynski) -- none of which is in the deposit. The only text in the SI is
#   the WWII-events questionnaire, whose responses are not shipped (nominal).
#
# Tables:
#   rzeszutek_2023_danieli       Danieli Inventory of Multigenerational Legacies
#                                of Trauma (Survivors' Posttrauma Adaptational
#                                Styles), 60 items, 1-5. Each respondent rated
#                                exactly ONE generation (asserted): parents
#                                (rapr_r_*, n=658), grandparents (rapr_d_*,
#                                n=736) or great-grandparents (rapr_pd_*,
#                                n=204); the other two blocks are 99 = not
#                                administered. Same 60 items, so one table,
#                                with the generation in cov_danieli_target and
#                                the item code rapr_<target>_r<k> -> rapr_<k>.
#   rzeszutek_2023_pds5          PDS-5 items 1-22 (20 DSM-5 symptoms + distress
#                                + interference), 0-4. Answered only by the 964
#                                respondents who endorsed a traumatic event
#                                (pds5_r98 "none" = 0); 99 = not administered
#                                (all-or-nothing per row, asserted). Sum of
#                                items 1-20 ranges 0-80 as in Table 2.
#   rzeszutek_2023_pds5_events   PDS-5 Part 1 trauma checklist, 8 binary
#                                checkboxes (pds5_r1..r7 + r97 "other"), 0/1,
#                                all 1,598 respondents.
#   rzeszutek_2023_ees           Experience of Embodiment Scale, 34 items, 1-5
#                                (sum equals SDC.tot on every row, asserted).
#   rzeszutek_2023_swls          Satisfaction With Life Scale, 5 items, 1-7
#                                (sum equals SWLS on every row, asserted). Not
#                                named in the paper but in the file in full.
#
# Skipped (books balanced below): PDS-5 items 23-24 (onset / duration, 1-2
# timing criteria rather than severity items); problemy_25_r_r1..r4 (four 0-3
# items asked of the PDS-5 subsample that the paper does not describe -- not
# among the PDS-5's 24 items, unidentifiable); pds5_2_r2 (index of the worst
# event, categorical); the 270 pzt_* WWII-knowledge items (27 events x 10
# ancestors, 1 = yes / 2 = no / 3 = don't know: three unordered categories,
# a nominal-standard candidate, not core); al1-2 and xa1-4 (undocumented
# categorical items); routing flags (kto*, pzt_full/rodzice/...); and every
# composite (subscale sums, criterion flags, counts, *.dich recodes).

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
CACHE = REPO_ROOT / "automated_finding" / "runs" / "raw" / "rzeszutek_2023"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10567698/supplementaryFiles"
XLSX = "41598_2023_44300_MOESM2_ESM.xlsx"
FREE_TEXT_DROP = ["pds5inne"]   # free-text trauma narratives (PII ruling)

COV = {
    "sex": "cov_sex",                        # 1/2 (810 F / 788 M per Table 1)
    "year": "cov_age",                       # age in years
    "age": "cov_age_group",                  # 5 bands (2..6)
    "miasta": "cov_residence",               # 1 village .. 5 city >500k
    "wyksztalcenie": "cov_education",        # 1 primary .. 5 higher
    "stancywilny": "cov_relationship_status",  # 1..6 (Table 1 order)
    "proba": "cov_sample",                   # Polish "sample"; 1/2, coding undocumented
    "survey_finish_time": "cov_completion_time_s",  # whole-survey seconds
}

TARGETS = {"r": "parents", "d": "grandparents", "pd": "great_grandparents"}
DAN = {t: [f"rapr_{t}_r{k}" for k in range(1, 61)] for t in TARGETS}
PDS = [f"problemy_1_22_r_r{k}" for k in range(1, 23)]
EVENTS = [f"pds5_r{k}" for k in range(1, 8)] + ["pds5_r97"]
EES = [f"sdc_r{k}" for k in range(1, 35)]
SWLS = [f"kszz_r{k}" for k in range(1, 6)]


def fetch():
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / XLSX
    if not f.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        f.write_bytes(z.read(XLSX))
    d = pd.read_excel(f, sheet_name="dane2")
    # the only non-numeric column; drop before anything else touches it
    text_cols = [c for c in d.columns if not pd.api.types.is_numeric_dtype(d[c])]
    assert text_cols == FREE_TEXT_DROP, text_cols
    return d.drop(columns=FREE_TEXT_DROP)


def skip_reasons(cols):
    """Every source column not used as an item, covariate or id, with why."""
    used = set(sum(DAN.values(), [])) | set(PDS) | set(EVENTS) | set(EES) \
        | set(SWLS) | set(COV) | {"Id"}
    out = {}
    for c in cols:
        if c in used:
            continue
        if c.startswith("pzt_r_") or c.startswith("pzt_d_"):
            why = "WWII-knowledge item, yes/no/don't-know (nominal, not core)"
        elif c in ("pzt_full", "pzt_rodzice", "pzt_dziadkowie", "pzt_pradziadkowie"):
            why = "routing flag for the WWII-knowledge block"
        elif c.startswith("kto"):
            why = "routing: which relatives the respondent reports on"
        elif c in ("problemy_23_r_r1", "problemy_24_r_r1"):
            why = "PDS-5 onset/duration timing criterion"
        elif c.startswith("problemy_25_r_r"):
            why = "undocumented 0-3 item, not among the PDS-5's 24 items"
        elif c == "pds5_2_r2":
            why = "index of worst event (categorical)"
        elif c == "pds5_r98":
            why = "'no event' checkbox = 1 - any(events) (derived)"
        elif c in ("al1", "al2", "xa1", "xa2", "xa3", "xa4"):
            why = "undocumented categorical item"
        elif c in ("age2", "miasta2", "miasta3"):
            why = "undocumented recode / sub-routing of age or residence"
        else:
            why = "composite / derived score"
        out[c] = why
    return out


def melt(d, items, covs, name):
    long = d.melt(id_vars=["id"] + covs, value_vars=items,
                  var_name="item", value_name="resp")
    return long


def check_and_write(long, name, pv, written):
    long = long[["id", "item", "resp"] + [c for c in long.columns
                                          if c.startswith("cov_")]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert set(long["resp"].unique()) <= set(pv), sorted(long["resp"].unique())
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        long, label=name, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    assert name not in written, name
    written.add(name)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    d = fetch()
    assert d.shape == (1598, 626), d.shape
    assert d["Id"].is_unique
    # age check: `year` is age, matching the paper's M = 48.78, SD = 20.50
    assert d["year"].between(18, 97).all()
    assert round(d["year"].mean(), 2) == 48.78

    # books
    skips = skip_reasons(d.columns)
    for c, why in skips.items():
        print(f"  skip {c!r}: {why}")
    accounted = set(skips) | set(sum(DAN.values(), [])) | set(PDS) \
        | set(EVENTS) | set(EES) | set(SWLS) | set(COV) | {"Id"}
    assert accounted == set(d.columns)
    print(f"  dropped free-text column(s): {FREE_TEXT_DROP}")

    # structural checks
    assert (d[EES].sum(axis=1) == d["SDC.tot"]).all()
    assert (d[SWLS].sum(axis=1) == d["SWLS"]).all()
    assert (d["pds5_r98"] == 1 - d["total"]).all()
    pds_na = (d[PDS] == 99)
    assert (pds_na.all(axis=1) | (~pds_na).all(axis=1)).all()
    assert (pds_na.all(axis=1) == (d["pds5_r98"] == 1)).all()
    done = {t: (d[c] != 99).all(axis=1) for t, c in DAN.items()}
    for t, c in DAN.items():
        assert ((d[c] == 99).all(axis=1) | done[t]).all()
    assert (sum(m.astype(int) for m in done.values()) == 1).all()

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1          # row index replaces the source Id
    d = d.rename(columns=COV)
    covs = list(COV.values())
    written = set()

    # Danieli: stack the three generation blocks into one item set
    parts = []
    for t, cols in DAN.items():
        sub = d.loc[done[t], ["id"] + covs + cols].copy()
        sub = sub.rename(columns={c: f"rapr_{k}" for k, c in enumerate(cols, 1)})
        sub["cov_danieli_target"] = TARGETS[t]
        parts.append(sub)
    dan = pd.concat(parts, ignore_index=True)
    long = melt(dan, [f"rapr_{k}" for k in range(1, 61)],
                covs + ["cov_danieli_target"], "danieli")
    check_and_write(long, "rzeszutek_2023_danieli", [1, 2, 3, 4, 5], written)

    sub = d.loc[d["pds5_r98"] == 0]
    long = melt(sub, PDS, covs, "pds5")
    check_and_write(long, "rzeszutek_2023_pds5", [0, 1, 2, 3, 4], written)

    long = melt(d, EVENTS, covs, "pds5_events")
    check_and_write(long, "rzeszutek_2023_pds5_events", [0, 1], written)

    long = melt(d, EES, covs, "ees")
    check_and_write(long, "rzeszutek_2023_ees", [1, 2, 3, 4, 5], written)

    long = melt(d, SWLS, covs, "swls")
    check_and_write(long, "rzeszutek_2023_swls", [1, 2, 3, 4, 5, 6, 7], written)


if __name__ == "__main__":
    convert()
