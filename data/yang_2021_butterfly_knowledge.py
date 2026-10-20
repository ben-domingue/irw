#!/usr/bin/env python3

# Source: https://zenodo.org/records/4924405
# DOI: 10.5061/dryad.v9s4mw6w2
#   Yang, R. (2021). Questionnaire data, butterfly images and analysis code
#   [Dataset]. Dryad, mirrored on Zenodo (record 4924405, published
#   2021-12-10). Supports Yang et al., "Biased local ecological knowledge of
#   butterfly diversity provided by the ethnic minority in Southwest China's
#   biodiversity hotspot".
# Data: "Questionnaire_data__butterfly_wing_color_brightness_and_contrast
#   .xlsx", sheet "Original data" -- 236 local Dai people in the Menglun
#   area, Xishuangbanna, Yunnan, answering twenty questions about butterfly
#   knowledge, perceived decline, and conservation attitudes.
# License: CC0 1.0 (the Zenodo record reports license id "cc-zero",
#   verified 2026-10-20).
#
# Item text: IN HAND and cheap, but NOT shipped here -- the blocker is file
#   ownership in this session, not the text. Every stem is present twice in
#   the deposit: as the column header on "Original data" and in the
#   "Questions" column of the "proportion" sheet, which also supplies the
#   authors' own item codes and the five response anchors by name. The items
#   are study-authored (they are the paper's own instrument, not a published
#   scale), and the deposit is CC0, so there is no third-party rights
#   question and no register row is needed -- this is about as cheap as
#   Step 3.5 ever gets. It is left for the next pass only because shipping
#   item text also requires rows in itemtext/mapping_verification.csv and
#   automated_finding/itemtext_provenance.csv, and this session does not own
#   those two files. Whoever picks it up needs no new research: stems,
#   codes and anchors are all in the two sheets this script already reads,
#   and the code-to-stem tie is verified by text below rather than by
#   position.
#
# ONE table: the 20 questions, asked of every respondent.
#
# Item codes are the AUTHORS' OWN, not positional. The deposit's description
# says so explicitly ("Questions were indexed as the abbreviation of the
# categories from BK1 to AK5. See the second column on sheet 'proportion'"),
# giving five documented blocks: BK1-BK7 butterfly knowledge, BD1-BD3
# perceived butterfly decline, HI1-HI2 human impact, CS1-CS3 culture and
# sources of information, AK1-AK5 attitudes and conservation knowledge. The
# mapping is established by matching each stem TEXT between the two sheets,
# with punctuation and whitespace normalised, and the script asserts that
# all twenty match one-to-one. It deliberately does not rely on the two
# sheets being in the same order, even though they are -- a positional tie
# would be invisible to every set-comparing check if one sheet were ever
# reordered, and the whole point of having the authors' codes is not to
# guess.
#
# id: the deposit's own sequence column, named with the Chinese for "serial
#   number". 236 unique values over 236 rows. Not PII.
#
# resp: 1-5, and the five anchors are named in the "proportion" sheet's
#   header: 1 = strongly disagree, 2 = disagree, 3 = UNKNOWN, 4 = agree,
#   5 = strongly agree. All five are shipped as collected, including the 3s.
#   That choice is deliberate and worth stating, because 3 is a don't-know
#   option sitting in the midpoint position rather than a neutral: it is
#   common on these items (7% to 36% depending on the item) and the
#   depositors themselves reran their ordinal models both ways -- the
#   workbook carries both a "CLMM results" and a "CLMM results without
#   'unknown'" sheet. Dropping the 3s would recode the scale to four points
#   and discard roughly a fifth of all responses, which is an analytic
#   decision belonging to whoever uses the table, not to its ingestion. IRW
#   stores what was collected, the anchor is documented here and in the
#   dictionary note, and a user who wants the authors' second specification
#   can filter resp == 3 themselves. Nothing is imputed or recoded.
#
# Dropped as a composite, not a response: "total score" (41 distinct values,
#   the sum of the twenty items).
#
# Covariates: the deposit's three demographics, kept as the source's own
#   integer codes because the workbook supplies no legend for them -- gender
#   is 1-2, age is 1-3 (a band, not a year) and village is 1-5. Expanding
#   them would mean guessing which code is which, so the codes are preserved
#   and named instead. The deposit's other 20 files are butterfly images,
#   wing measurements and analysis code, none of them questionnaire data.
#
# PII: none. The screen uses pd.api.types.is_string_dtype -- never
#   dtype == object -- and prints the denominator, asserted non-zero. Every
#   column in the sheet is numeric: a serial number, twenty 1-5 item
#   responses, three coded demographics and a total. There is no name,
#   email, date of birth, phone number, address or free-text field, and no
#   geographic unit finer than "village" as one of five integer codes, which
#   does not single out a respondent among 236.
import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s5"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "zenodo" / "4924405"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 4924405
FNAME = ("Questionnaire_data__butterfly_wing_color_brightness_and_contrast"
         ".xlsx")
TABLE = "yang_2021_butterfly_knowledge"

ID_COL = "序号"
TOTAL_COL = "total score"
COVS = {"21、gender": "cov_gender", "22、age": "cov_age_group",
        "23、village": "cov_village"}
SCALE = {1, 2, 3, 4, 5}
ANCHORS = {1: "strongly disagree", 2: "disagree", 3: "unknown",
           4: "agree", 5: "strongly agree"}
N_RESP, N_ITEMS = 236, 20


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://zenodo.org/api/records/{RECORD}/files/{FNAME}/content"
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def norm(text) -> str:
    """Normalise a stem for matching: drop a leading question number, strip
    punctuation and case, collapse whitespace."""
    s = str(text)
    s = re.sub(r"^\s*\d+\s*[.、,]?\s*", "", s)
    s = re.sub(r"[^0-9a-z]+", " ", s.lower())
    return " ".join(s.split())


def main():
    path = fetch()
    df = pd.read_excel(path, sheet_name="Original data")
    codes = pd.read_excel(path, sheet_name="proportion")
    assert len(df) == N_RESP, len(df)
    assert df[ID_COL].nunique() == N_RESP, "serial number is not unique"

    # PII screen -- print the denominator so an empty selection is visible.
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] columns examined: {len(df.columns)} total, "
          f"{len(text_cols)} string-dtype")
    assert len(df.columns) > 0, "PII screen selected no columns"

    # Confirm the anchor names the header note relies on.
    anchor_cols = [str(c) for c in codes.columns]
    for name in ANCHORS.values():
        assert any(name in c.lower() for c in anchor_cols), \
            f"anchor {name!r} not found in the proportion sheet header"

    # Tie the authors' item codes to the data columns BY STEM TEXT.
    stem_to_code = {norm(q): str(c).strip()
                    for q, c in zip(codes.iloc[:, 0], codes.iloc[:, 1])
                    if pd.notna(q) and pd.notna(c)}
    item_cols = [c for c in df.columns
                 if c != ID_COL and c != TOTAL_COL and c not in COVS]
    assert len(item_cols) == N_ITEMS, (len(item_cols), item_cols)
    mapping = {}
    for c in item_cols:
        code = stem_to_code.get(norm(c))
        assert code, f"no authors' code matches the stem {str(c)[:60]!r}"
        mapping[c] = code
    assert len(set(mapping.values())) == N_ITEMS, "codes are not one-to-one"
    print(f"[items] all {N_ITEMS} data columns matched to the authors' own "
          f"codes by stem text (not by position): "
          f"{', '.join(sorted(set(mapping.values()))[:6])}, ...")

    df = df.rename(columns={ID_COL: "id", **COVS})
    cov_cols = list(COVS.values())

    t = (df[["id", *cov_cols, *item_cols]]
         .melt(id_vars=["id", *cov_cols], value_vars=item_cols,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    t["item"] = t["item"].map(mapping)
    assert t["item"].notna().all(), "unmapped item column"
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the documented 1-5 scale: {bad}"

    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any(), "duplicate id/item"
    assert t["id"].nunique() == N_RESP
    assert t["item"].nunique() == N_ITEMS

    share3 = (t["resp"] == 3).mean()
    print(f"[note] resp == 3 is the deposit's 'unknown' option and is "
          f"{share3:.1%} of all responses; shipped as collected (see header)")

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
