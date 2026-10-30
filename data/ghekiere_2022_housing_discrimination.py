#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0276698
# DOI: 10.1371/journal.pone.0276698
# Paper: Ghekiere, A., Verhaeghe, P.-P., Baert, S., Derous, E., &
#   Schelfhout, S. (2022). Introducing a vignette experiment to study
#   mechanisms of ethnic discrimination on the housing market. PLOS ONE 17(10).
# Data: journal.pone.0276698.s001 (S1 Data, .csv), 575 rows x 47 columns.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
# 575 respondents in a Flemish housing-discrimination vignette experiment.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ONE output table, 44 items. The design is crossed: each respondent read one
# vignette, then rated FOUR fictitious rental candidates on the SAME ELEVEN
# statements about why they would or would not choose that candidate. The
# paper: "The respondent had to comment, for every candidate, on different
# items which signal drivers or reasons behind the choice of the candidate. A
# 7-point rating scale indicated the likeliness to agree to the statement,
# ranging from (1): I do not agree to this statement, to (7): I agree with
# this statement."
#
# So 11 statements x 4 candidates = 44 item-by-candidate cells per respondent,
# which ship as 44 items in ONE table keyed by the deposit's own
# `Q<block>_<n>` codes. This follows the lee_whiting_2025_trust_actors
# precedent: one stem crossed with several targets becomes one table whose
# items are the stem-target combinations, not several tables.
#
# WHICH BLOCK IS WHICH CANDIDATE IS NOT RECOVERABLE, and that is the real
# limitation of this table. The whole point of the experiment is that the four
# candidates differ in ETHNICITY (the paper reports results "classified by the
# ethnicity of the assigned rental candidate"), but the deposit labels the
# blocks only Q63, Q126, Q127 and Q128 and nothing maps a block to a
# candidate. So the item codes preserve the crossing faithfully while the
# substantive contrast -- majority vs minority applicant -- cannot be read off
# this table alone. Stated in the description, because a user who assumes the
# blocks are in a meaningful order would be inventing the study's independent
# variable.
#
# THE VIGNETTE MANIPULATION *IS* RECOVERABLE, from the vignette text itself,
# and that is the main thing this script adds. The `KF` column holds the full
# Dutch vignette each respondent read, and three crossed factors are parsed out
# of it deterministically:
#   cov_neighbourhood   "Vlaamse, witte buurt" (Flemish, white) vs "buurt met
#                       veel migranten" (many migrants)        293 / 282
#   cov_monthly_rent    the euro figure in the text: 650 or 1050  329 / 246
#   cov_landlord_request  which discriminatory request the landlord makes:
#                       quiet_clean / bad_exp_self / bad_exp_neighbour /
#                       cheap_rundown                    172/170/156/77
# These are person-level (one vignette per respondent), so they are `cov_`
# columns rather than a treatment column -- and deliberately not `treat`,
# which datastandard.md defines as 1/0 treatment-vs-control. A 2 x 2 x 4
# partial factorial has no control arm to encode, the same situation as
# lin_2026_advertising_literacy earlier in this batch.
#
# MOJIBAKE HALVED THE APPARENT NUMBER OF CONDITIONS, which is why the parse is
# done on repaired text. The raw `KF` column has 28 distinct values, but 14 of
# them are UTF-8-through-MacRoman corruptions of the other 14 -- the euro sign
# arrives as "‚Ç¨" and the curly quotes as "‚Äú"/"‚Äù". Reading the raw
# strings would treat each condition as two, splitting every cell of the
# design. Repaired with `.encode("mac_roman").decode("utf-8")` and asserted
# down to exactly 14 vignettes. (Second mojibake in this batch, after the
# kendall_2018 GBK labels -- worth knowing that it changes counts, not just
# looks.)
#
# `id` is the deposit's `ResponseId`, verified unique over all 575 rows.
# `Uni_ID` has 10 values of very unequal size (11 to 161) and groups
# respondents, so it ships as `cluster_id` -- the design column
# datastandard.md reserves for nesting and forbids `cov_`-prefixing.
#
# Clean source: zero missing cells across all 44 items, every observed value
# in 1-7.
#
# Item text: NOT SHIPPED. The eleven statements are printed in the article's
# Table 2, so the wording exists -- but Table 2 is an image in the HTML and,
# more decisively, nothing maps a printed statement to one of the deposit's
# `Q<block>_<n>` codes, nor a block to a candidate. Attaching 11 stems to 44
# codes under a guessed ordering is precisely the error an itemtext table must
# not make. The instrument is the authors' own vignette instrument under the
# article's CC BY 4.0, so a register row is written with verdict ship: the
# rights are clear and only the mapping blocks it.
#
# PII: screened over all 47 columns. One free-text column (`KF`, the vignette
# text, which is researcher-written stimulus material and not respondent
# input) and no names of real people, emails, dates or respondent-level
# geography -- the neighbourhood factor is a vignette attribute, not where the
# respondent lives.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("GHEKIERE_RAW", "journal.pone.0276698_S1_Data.csv")

TABLE = "ghekiere_2022_housing_discrimination"
N_ROWS = 575
N_ITEMS = 44
N_VIGNETTES = 14
LO, HI = 1, 7

BLOCKS = ["Q63", "Q126", "Q127", "Q128"]
MESSAGES = [("rustige, propere", "quiet_clean"),
            ("slechte ervaringen gehad met allochtonen", "bad_exp_self"),
            ("buurman heeft slechte ervaringen", "bad_exp_neighbour"),
            ("bouwvallig", "cheap_rundown")]


def repair_mojibake(s):
    """The deposit's vignette text is UTF-8 that went through MacRoman. Without
    repair the euro sign and curly quotes differ between otherwise identical
    vignettes and each condition counts twice."""
    try:
        return s.encode("mac_roman").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}: "
          f"{strings}")
    assert set(strings) <= {"KF", "ResponseId"}, f"unexpected strings: {strings}"
    pat = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")
    hits = [(c, v[:40]) for c in strings
            for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(pat, regex=True, case=False).any()]
    assert not hits, f"PII screen hit: {hits[:3]}"
    print("  clean: the only free text is KF, the researcher-written vignette "
          "stimulus (not respondent input). The fictitious landlord name in it "
          "is study material; no real person, email, date or respondent-level "
          "geography appears")


def parse_vignette(df):
    kf = df["KF"].astype(str).map(repair_mojibake)
    n_raw, n_fixed = df["KF"].nunique(), kf.nunique()
    assert n_fixed == N_VIGNETTES, (
        f"{n_fixed} distinct vignettes after mojibake repair, expected "
        f"{N_VIGNETTES} -- the repair or the file has changed")
    assert n_raw > n_fixed, "no mojibake found; the repair may now be a no-op"
    print(f"vignette text: {n_raw} distinct raw strings collapse to {n_fixed} "
          f"after mojibake repair (UTF-8 via MacRoman). Parsing 3 factors from "
          f"the repaired text")

    white = kf.str.contains("Vlaamse, witte buurt", regex=False)
    migrant = kf.str.contains("buurt met veel migranten", regex=False)
    assert (white ^ migrant).all(), "a vignette names neither or both neighbourhoods"
    nb = white.map({True: "flemish_white", False: "many_migrants"})

    rent = kf.str.extract(r"€\s?(\d+)")[0]
    assert rent.notna().all(), "a vignette has no euro rent figure"
    assert set(rent.unique()) == {"650", "1050"}, sorted(rent.unique())

    msg = pd.Series(["" for _ in range(len(kf))], index=kf.index)
    for needle, label in MESSAGES:
        hit = kf.str.contains(needle, regex=False) & (msg == "")
        msg[hit] = label
    assert (msg != "").all(), "a vignette matched no landlord request"

    print(f"  cov_neighbourhood {nb.value_counts().to_dict()}")
    print(f"  cov_monthly_rent {rent.value_counts().to_dict()}")
    print(f"  cov_landlord_request {msg.value_counts().to_dict()}")
    return nb, rent.astype(int), msg


def convert():
    df = pd.read_csv(RAW)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    items = [c for c in df.columns if re.fullmatch(r"Q\d+_\d+", str(c))]
    assert len(items) == N_ITEMS, (len(items), N_ITEMS)
    seen_blocks = sorted({c.split("_")[0] for c in items})
    assert seen_blocks == sorted(BLOCKS), seen_blocks
    for b in BLOCKS:
        n = sum(1 for c in items if c.startswith(b + "_"))
        assert n == 11, (b, n, "expected 11 statements per candidate")
    left_out = [c for c in df.columns
                if c not in items and c not in {"Uni_ID", "ResponseId", "KF"}]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"{N_ITEMS} items = 11 statements x {len(BLOCKS)} candidates "
          f"(blocks {', '.join(BLOCKS)}); which block is which candidate is "
          f"NOT recoverable from the deposit -- see header")

    nb, rent, msg = parse_vignette(df)

    assert int(df[items].isna().sum().sum()) == 0, "unexpected missing cells"
    stacked = df[items].stack().dropna()
    assert pd.to_numeric(stacked, errors="coerce").notna().all(), "non-numeric"
    vals = pd.to_numeric(stacked)
    assert vals.between(LO, HI).all(), sorted(vals.unique())

    assert df["ResponseId"].nunique() == len(df), "ResponseId is not unique"
    out = df.rename(columns={"ResponseId": "id", "Uni_ID": "cluster_id"}).copy()
    out["cov_neighbourhood"] = nb.values
    out["cov_monthly_rent"] = rent.values
    out["cov_landlord_request"] = msg.values
    cov_cols = ["cov_landlord_request", "cov_monthly_rent", "cov_neighbourhood"]

    long = out.melt(id_vars=["id", "cluster_id"] + cov_cols, value_vars=items,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)

    assert long["id"].nunique() == N_ROWS
    assert long["item"].nunique() == N_ITEMS
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == N_ITEMS * N_ROWS, len(long)
    assert len(TABLE) <= 40, (TABLE, len(TABLE))

    long = long[["id", "item", "resp", "cluster_id"] + cov_cols]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                            for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:165]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} "
          f"clusters={long['cluster_id'].nunique()}")


if __name__ == "__main__":
    convert()
