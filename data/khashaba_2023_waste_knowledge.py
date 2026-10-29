"""
A hospital waste-management intervention measured before and after on 133
nurses and housekeepers: a knowledge test and an attitude battery, each item
answered at both waves.

Source: Khashaba, E. (2023). Effect of waste management intervention program on
        knowledge attitude and practice (KAP) of nurses and house keepers: A
        quasi-experimental study in Mansoura Emergency Hospital, Egypt
        [Dataset]. Harvard Dataverse.
DOI: 10.7910/DVN/TN3UNW
Data: https://doi.org/10.7910/DVN/TN3UNW ("waste management
        intervention_Final", downloaded with format=original, which returns
        the original SPSS .sav)
License: CC0 1.0 (verified on the Dataverse record's licence block)
Item text: PARTLY in the deposit and NOT shipped yet. 50 of the 147 variables
        carry a variable label, and for the attitude block every one of the ten
        is the item's own wording ("it is necessary to dispose chemicals in
        special containers", "attending training programs is waste of time").
        The knowledge block is the problem: only 8 of its ~30 items are
        labelled, the labels that exist are abbreviations rather than wording
        ("haz_ waste def_pre", "cartoon boxes"), and the item codes are
        inconsistent SPSS 8-character names. So the attitude block is a cheap
        extraction and the knowledge block is not, and shipping one without the
        other is not worth a separate pass -- recorded here instead, with the
        pairing this script establishes, so a later pass starts from an answer.
        Where the rest is: the paper this deposit supports, which the record
        does not link.

**THIS IS A REAL TWO-WAVE DESIGN, which is why it is worth the trouble.** Every
item was asked before the intervention and again after it, at two genuine
occasions -- not a retrospective recall -- so `wave` 1 (pre) and 2 (post) is
exactly what the standard means by it.

**The pre/post pairing had to be established, because the column names do not
pair cleanly.** They are truncated SPSS names that drift between the two
waves: `wast_manQ3_Pre`/`waste_manag_Q3_Post`, `Cont.test.tube_Q13Pre`/
`Cont.test.tube_Q13_Post`, `amp.fing_Q14_Pre`/`amp.fings_Q14_Post`. What is
stable is the question NUMBER inside the name, so the pairing is keyed on
(block, number) and and the number is not even reliable -- two different
knowledge questions are both labelled Q9 (`Vaccin_Q9`, `Sharps_Q9`), and
several carry the number without a Q and sometimes after the wave marker
(`Clos_red.bags22_pre`, `Dis.chem_pre_23`).

So the pairing is positional -- each block alternates Pre, Post, Pre, Post
strictly -- and that is CHECKED three ways before any pair is accepted, because
a one-position slip is exactly what would otherwise ship silently:

  1. the two names must share a normalised prefix of at least 3 characters.
     The tightest real pair shares exactly 3 (`bio`, from
     `Bio.fluids.radio_Q19_Pre` / `Bio.radio_Q19_Post`), and a slip would
     break it.
  2. where both names carry a question number, it must be the same number.
  3. where both carry a variable label, the labels must share a normalised
     prefix of at least 4 characters ("hospital waste def_pre" /
     "hospital waste def_pos").

The run prints every accepted pair with its shared prefix, so the whole mapping
is reviewable rather than asserted.

The item code is the question number within its block (`k1`..`k27`, `a1`..`a10`),
which is the one part of the source naming that is consistent across the two
waves. The full source column name of each wave is printed by the run, so the
mapping is recoverable.

**The attitude block's 0/1 means "desirable response", not a scale direction.**
Its value labels differ by item -- some read `['dont know or disagree',
'agree']` and others `['agree 0r dont know', 'disagree']` -- because the
undesirable items are reverse-worded ("attending training programs is waste of
time", "ventillation of storage room not necessary"). In both cases 1 is the
desirable answer, exactly as 1 is the correct answer in the knowledge block.
That is a scored-correctness coding, not a mixed Likert direction, so one table
is right; the script asserts every attitude item is 0/1 and nothing else.

**The practice block is NOT shipped**, and the reason is a coding mix the
deposit itself introduces. It holds nine items at two waves, and they do not
share a response set: five are genuine 0-3 frequencies
(`no`/`fewtimes`/`sometimes`/`always`) while four are a COLLAPSED BINARY coded
at the ENDPOINTS of that same scale -- value labels
`['sometimes-always-fewtimes', 'No']`, with only 0 and 3 ever observed. Putting both in one table mixes a four-category frequency
with a two-category recode wearing the same numbers. Splitting them would make
two thin tables whose boundary is an artefact of the depositor's scoring rather
than of the instrument. Deferred with this diagnosis rather than guessed at.

PII: none. The screen below prints its denominator. There is no name, email,
date of birth or identifier; the one Arabic-named column is the study centre
(a single value, "مستشفي الطوارئ") and is dropped as a constant.

Expect heavy `imputed_values*` concentration warnings: the intervention
worked, so most post-test items are answered correctly by nearly everyone (98%
on one knowledge item, 99% on one attitude item). That is the result, not a
data defect.

Output: two tables, 9,888 responses.
  * khashaba_2023_waste_knowledge -- 29 items x 2 waves, resp 0/1 (correct)
  * khashaba_2023_waste_attitude  -- 10 items x 2 waves, resp 0/1 (desirable)
"""
from __future__ import annotations

from pathlib import Path
import os
import re
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("waste management intervention_Final.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

PERMITTED = [0, 1]

# The two shipped blocks, as the deposit's own section markers delimit them:
# Table_1 "Knowledge" at column 16 and Table_3_attitude at 77, with
# Table_4_practicescore at 98 closing the attitude block.
BLOCKS = {
    "khashaba_2023_waste_knowledge": ("k", "Table_1", "Table_3_attitude"),
    "khashaba_2023_waste_attitude": ("a", "Table_3_attitude",
                                     "Table_4_practicescore"),
}


COV_MAP = {
    "age": "cov_age",
    "Gender": "cov_gender",
    "education": "cov_education",
    "Job_description": "cov_job_description",
    "department": "cov_department",
    "Duration_Employment": "cov_years_employed",
    "daily_hours": "cov_daily_hours",
    "H.C.V.Infection": "cov_hcv_infection",
    "H.B.V.Vaccin": "cov_hbv_vaccinated",
    "Was.mangement.training": "cov_prior_waste_training",
}

# The wave marker is not always a suffix: it appears as `..._Pre`, `...Pre`,
# `..._pre_23` and `..._pre24`. Only its presence is needed, not its position.
WAVE_RE = re.compile(r"(?<![a-z])(pre|post|pos)(?![a-z])", re.I)
QNUM_RE = re.compile(r"(\d{1,2})")


def _wave_of(col: str) -> str:
    m = WAVE_RE.search(col)
    assert m, f"{col} carries no Pre/Post marker"
    return "pre" if m.group(1).lower() == "pre" else "post"


def _slug(col: str) -> str:
    """The source column name with the wave marker removed, as an item code.

    `med_w_Q1_Pre` -> `med_w_q1`, `Bio.fluids.radio_Q19_Pre` ->
    `bio_fluids_radio_q19`. Derived from the source name and reversible, rather
    than a positional index.
    """
    out = WAVE_RE.sub("", col)
    out = re.sub(r"[^A-Za-z0-9]+", "_", out).strip("_").lower()
    return re.sub(r"_+", "_", out)


def _norm(col: str) -> str:
    return re.sub(r"[^a-z0-9]", "", WAVE_RE.sub("", col).lower())


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 133, len(df)

    cols = list(df.columns)
    labels = {c: (meta.column_names_to_labels.get(c) or "").strip()
              for c in cols}
    blocks = {}
    for table, (_prefix, start, end) in BLOCKS.items():
        block = cols[cols.index(start) + 1:cols.index(end)]
        assert len(block) % 2 == 0, (table, len(block))
        # The block alternates Pre, Post, Pre, Post ... strictly, which is
        # asserted rather than assumed, and each adjacent pair is then CHECKED
        # three ways before it is accepted as the same item at two waves.
        waves = [_wave_of(c) for c in block]
        assert waves == ["pre", "post"] * (len(block) // 2), \
            f"{table}: the block does not alternate Pre/Post: {waves}"
        pairs, dropped = {}, []
        for i in range(0, len(block), 2):
            pre, post = block[i], block[i + 1]
            # 1. the names must share a normalised prefix. A one-position slip
            #    breaks this: the shortest real pair here shares 3 characters
            #    ('bio', Bio.fluids.radio_Q19 / Bio.radio_Q19).
            shared = os.path.commonprefix([_norm(pre), _norm(post)])
            assert len(shared) >= 3, (table, pre, post, shared)
            # 2. where both carry a question number, it must be the same one.
            npre, npost = QNUM_RE.findall(pre), QNUM_RE.findall(post)
            if npre and npost:
                assert npre[-1] == npost[-1], (pre, post, npre, npost)
            # 3. where both carry a variable label, the labels must correspond.
            lpre, lpost = labels[pre], labels[post]
            if lpre and lpost:
                lshared = os.path.commonprefix(
                    [_norm(lpre), _norm(lpost)])
                assert len(lshared) >= 4, (pre, post, lpre, lpost, lshared)
            code = _slug(pre)
            assert code not in pairs, (table, code)
            # One knowledge question is not correct/incorrect at all: "how do
            # you dispose of chemicals" offers three UNORDERED categories
            # (Don't know / after dilution / in a special container). It is
            # dropped rather than forced into a 0/1 table, and it is the only
            # one -- the loop below asserts every surviving pair is binary.
            vals = set(df[pre].dropna().unique()) | set(df[post].dropna().unique())
            if not vals <= set(PERMITTED):
                print(f"    skipped {code}: responses {sorted(vals)} are not "
                      f"the block's correct/incorrect 0/1 -- value labels "
                      f"{list(meta.variable_value_labels.get(pre, {}).values())}")
                dropped.append(code)
                continue
            pairs[code] = {"pre": pre, "post": post, "shared": shared}
        blocks[table] = pairs
        assert len(dropped) <= 1, dropped
        print(f"{table}: {len(pairs)} item(s), each paired Pre/Post and "
              f"checked on name, question number and variable label")
        for code, v in pairs.items():
            print(f"    {code:<26} pre={v['pre']:<40} post={v['post']:<40} "
                  f"(shared '{v['shared']}')")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    practice = cols[cols.index("Table_4_practicescore") + 1:
                    cols.index("job_desc2")]
    item_cols = {c for pairs in blocks.values() for v in pairs.values()
                 for c in v.values()}
    accounted = (set(COV_MAP) | set(covs) | item_cols | set(practice)
                 | {"id"} | set(BLOCKS[k][1] for k in BLOCKS)
                 | {"Table_4_practicescore"})
    leftover = [c for c in df.columns if c not in accounted]
    print(f"skipped {len(practice)} practice column(s) (9 items x 2 waves): "
          "five are genuine 0-3 frequencies and four a COLLAPSED BINARY coded "
          "at the endpoints 0 and 3, so one table would mix a four-category "
          "frequency with a two-category recode wearing the same numbers -- "
          "see the docstring")
    print(f"skipped {len(leftover)} further column(s): the depositor's totals, "
          f"difference and percent-change scores, recoded demographics, an "
          f"SPSS filter, the constant study centre, and the conditional "
          f"follow-ups")
    assert len(leftover) == 38, len(leftover)

    for table, pairs in blocks.items():
        waves = []
        for wave, side in ((1, "pre"), (2, "post")):
            cmap = {v[side]: code for code, v in pairs.items()}
            part = df[["id"] + covs + list(cmap)].rename(columns=cmap)
            part = part.melt(id_vars=["id"] + covs, var_name="item",
                             value_name="resp")
            part["wave"] = wave
            waves.append(part)
        write(pd.concat(waves, ignore_index=True), table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(PERMITTED)].copy()
    assert before == len(long), \
        f"{table}: {before - len(long)} cell(s) outside {PERMITTED}"
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + covs].sort_values(
        ["id", "item", "wave"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={sorted(long['wave'].unique())} "
          f"resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
