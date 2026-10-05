"""Anunciacao (2026), ASQ:SE-2 renorming sample (developmental delay paper).

Source: OSF n5ksw (https://osf.io/n5ksw/), CC BY 4.0. Paper: 10.1007/s13158-026-00488-y.
File read: "Original data/asqse_results.csv" (https://osf.io/download/zythu/,
sha256 343273b2f89889b5d8c4cea0e77c3ee459ad368ffb0240c772be02585b380821 on
2026-10-05): 25,733 rows, one per completed questionnaire.

Tables written (rebuilt 2026-10-05, irw#2834):

  development_delay_anunciacao_asqse     the scored ASQ:SE-2 items
  development_delay_anunciacao_concerns  the per-item "check if this is a
                                         concern" circles and the two OVERALL
                                         yes/no questions

The ASQ:SE-2 is nine separate questionnaires, one per age interval (2, 6, 12,
18, 24, 30, 36, 48, 60 months; `cov_quest`), each with its own items. The
deposit stores them in positional columns asqse1..asqse39 / con1..con39, so
column k is item k *of that interval's form*. Item codes are therefore
`q<interval>m_<kk>`, the form's own item number zero-padded: `q2m_01` ..
`q2m_16`, ..., `q60m_01` .. `q60m_36`. The same code never means two questions.

Form lengths (scored items), checked against the published ASQ:SE-2 forms
(Squires, Bricker & Twombly, 2015) and against the data (the last position
with any non-zero value at each interval):

  interval  2  6 12 18 24 30 36 48 60
  scored   16 23 27 31 31 33 35 36 36

Each scored item has a "check if this is a concern" circle, and each form ends
with an OVERALL page: item L+1 "Do you have concerns about your child's eating
or sleeping [or toileting] behaviors?" (YES/NO), item L+2 "Does anything about
your child worry you?" (YES/NO), item L+3 "What do you enjoy about your
child?" (free text). In the deposit:

  asqseK (K <= L)    item K's score as printed on the form: Z = 0, V = 5,
                     X = 10. The key is already applied, so 10 is always the
                     answer of most concern ("rarely or never" on positively
                     worded items, "often or always" on negatively worded
                     ones). Kept as is.
  conK (K <= L)      item K's concern circle: 5 = checked, 0 = not checked (the
                     form adds 5 points for a checked concern). Kept as is.
  con(L+1), con(L+2) the two OVERALL yes/no questions, 5 = yes, 0 = no (a 5 on
                     L+2 goes with a written answer to "worries" for 82-92% of
                     rows that have one, and 1-7% of rows that do not). They
                     are form items L+1 and L+2, so they appear in _concerns as
                     q<m>m_<L+1> and q<m>m_<L+2>. Not part of the total score.
  asqseK (K > L), conK (K > L+2)
                     padding: no such item on that interval's form. Asserted to
                     be 0 for every row, then dropped.

The deposit's `asqse_total` equals sum(asqse1..L) + sum(con1..L) for 94-99% of
rows at each interval; it is kept as `cov_asqse_total` as supplied. (The
paper's Method reports one item fewer per interval, 15 .. 35; its notebook uses
range(1, L), which leaves out item L, "Has anyone shared concerns about your
child's behaviors?". The forms and the data both have L scored items.)

`id` is the deposit's id, a UUID per completed questionnaire. The deposit has
no child identifier, so `id` does not link a child across intervals; some
children were probably screened more than once, but they could only be matched
on the personal data, which is not published here. `date` is the completion
date (`datcom`), Unix seconds, day precision.

Covariates kept (source codes unless noted): cov_quest (interval, months),
cov_age_m (age in whole months; source "35m"), cov_gender (1 male, 2 female,
3/4 as in the source), cov_ethnicity, cov_premature, cov_mom_edu, cov_mom_age,
cov_author (who completed the form), cov_income, cov_disability, cov_services,
cov_teen_mom, cov_asqse_total, cov_asqse_monitor_cutoff, cov_asqse_cutoff.

Not written:
  personal data  initials, zipcode, dob, cdob (child's and corrected date of
                 birth; no complete dates of birth).
  free text      disability_txt, services_txt, state (597 spellings, incl.
                 city names), and the open-ended answers eating_other,
                 over_and_over, fearful, behavior_concern, habit_concern,
                 worries, enjoy (they include children's names).
  other          weight (undocumented; mixes 0/1 with yes/no/decline/unknown);
                 language, asqse_version, project, contact, referral
                 (constant); se_eligibility (one non-empty value);
                 disability_code, services_code, at_risk, has_validity,
                 program, method (empty).

Until 2026-10-05 this script melted asqse1..39 / con1..39 across all nine
intervals, so one code meant a different question at each interval, wrote the
padding positions as real 0 answers (22.7% of _asqse rows), and published the
personal data and free text above. See irw#2834.

Usage: python3 developmental_delay_anunciacao_2026.py [raw_csv] [out_dir]
"""
import os
import sys

import pandas as pd

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw_data/asqse_results.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "irw_processed_tables"

# Scored items per interval (ASQ:SE-2 forms).
FORM_LENGTH = {2: 16, 6: 23, 12: 27, 18: 31, 24: 31, 30: 33, 36: 35, 48: 36, 60: 36}
N_OVERALL_YN = 2  # OVERALL items L+1 (eating/sleeping/toileting) and L+2 (worries)
N_POS = 39

COVS = [
    "cov_quest", "cov_age_m", "cov_gender", "cov_ethnicity", "cov_premature",
    "cov_mom_edu", "cov_mom_age", "cov_author", "cov_income", "cov_disability",
    "cov_services", "cov_teen_mom", "cov_asqse_total", "cov_asqse_monitor_cutoff",
    "cov_asqse_cutoff",
]


def unix_seconds(s):
    """Date column -> Unix seconds (Int64). Unit-safe under pandas 3."""
    s = pd.to_datetime(s, errors="coerce")
    return ((s - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)).astype("Int64")


def to_int(s):
    v = pd.to_numeric(s, errors="raise")
    assert (v.dropna() == v.dropna().round()).all()
    return v.astype("Int64")


def main():
    df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    df = df.apply(lambda c: c.str.strip())
    df = df.replace({"": pd.NA, ".": pd.NA})
    assert df["id"].notna().all() and df["id"].is_unique, "id not unique"
    df["quest"] = to_int(df["quest"])
    assert set(df["quest"].unique()) == set(FORM_LENGTH), sorted(df["quest"].unique())

    a_cols = [f"asqse{k}" for k in range(1, N_POS + 1)]
    c_cols = [f"con{k}" for k in range(1, N_POS + 1)]
    for c in a_cols + c_cols:
        df[c] = to_int(df[c])
    assert df[a_cols + c_cols].notna().all().all(), "missing item values"
    assert set(pd.unique(df[a_cols].values.ravel())) <= {0, 5, 10}
    assert set(pd.unique(df[c_cols].values.ravel())) <= {0, 5}

    cov = pd.DataFrame({"id": df["id"]})
    cov["date"] = unix_seconds(df["datcom"])
    assert cov["date"].notna().all()
    cov["cov_quest"] = df["quest"]
    assert df["age_m"].str.fullmatch(r"\d+m").all()
    cov["cov_age_m"] = to_int(df["age_m"].str[:-1])
    for c in ["gender", "ethnicity", "premature", "mom_edu", "mom_age", "author",
              "income", "disability", "services", "teen_mom",
              "asqse_total", "asqse_monitor_cutoff", "asqse_cutoff"]:
        cov[f"cov_{c}"] = to_int(df[c])

    scored, concern = [], []
    for m, L in FORM_LENGTH.items():
        g = df[df["quest"] == m]
        # Padding: positions past the form must be 0 for every child.
        pad_a = a_cols[L:]
        pad_c = c_cols[L + N_OVERALL_YN:]
        bad = [c for c in pad_a + pad_c if (g[c] != 0).any()]
        if bad:
            sys.exit(f"ABORT: {m} months: padding positions not all 0: {bad}")
        # The last kept position is in use at this interval (sanity check on L).
        assert (g[a_cols[L - 1]] != 0).any(), (m, "asqse", L)
        assert (g[c_cols[L + N_OVERALL_YN - 1]] != 0).any(), (m, "con", L + 2)
        print(f"{m:>2} months: {len(g):,} questionnaires; asqse1-{L} kept, "
              f"{len(pad_a)} padding positions dropped; con1-{L + N_OVERALL_YN} kept, "
              f"{len(pad_c)} dropped (all 0)")
        for cols, out in ((a_cols[:L], scored), (c_cols[:L + N_OVERALL_YN], concern)):
            long = g[["id"] + cols].melt(id_vars="id", var_name="pos", value_name="resp")
            k = long["pos"].str.extract(r"(\d+)$")[0].astype(int)
            long["item"] = f"q{m}m_" + k.map("{:02d}".format)
            long["_k"] = k
            out.append(long[["id", "item", "resp", "_k"]])

    os.makedirs(OUT, exist_ok=True)
    for name, parts in (("development_delay_anunciacao_asqse", scored),
                        ("development_delay_anunciacao_concerns", concern)):
        t = pd.concat(parts, ignore_index=True).merge(cov, on="id", how="left")
        t = t.sort_values(["cov_quest", "id", "_k"], kind="stable")
        t = t[["id", "item", "resp", "date"] + COVS]
        assert not t.duplicated(["id", "item"]).any()
        path = os.path.join(OUT, name + ".csv")
        t.to_csv(path, index=False)
        print(f"{name}: {len(t):,} rows, {t['id'].nunique():,} ids, "
              f"{t['item'].nunique()} items -> {path}")


if __name__ == "__main__":
    main()
