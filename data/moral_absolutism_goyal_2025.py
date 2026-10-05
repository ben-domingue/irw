"""Goyal, De Gregori, Savani & Liu (2025), political ideology and moral relativism.

Source: OSF qehna (https://osf.io/qehna/files/osfstorage), shared with
permission by email (Derived_License CC BY-NC 4.0). Paper: 10.1037/pspa0000464.
Files read (sha256 checked against OSF on 2026-10-05):

  Study 3 Data.sav                                  223 rows, one per person
  Study 4 Data Experimental NFC.sav                 251 rows, one per person
  Study 5 Data Long Format Support for Bans.dta     200 people x 11 issue rows
  Study 6 Data Long Format .dta                     405 people x 6 issue rows
  Study 7 Data Long Format.dta                      302 people x 6 trial rows
  Study 8 data long format.dta                      262 people x 6 trial rows

Tables written (rebuilt 2026-10-05, irw#2563):

  _mfq          Study 6. Moral Foundations Questionnaire, relevance part: 15
                items, 1-6 (not at all .. extremely relevant). The catch item
                "whether or not someone was good at math" (source `math`, the
                6th item) is not written.
  _pp           Study 6. Promotion/prevention (Regulatory Focus) items pp1-pp11,
                1-5.
  _dt           Study 6. Three moral dilemmas (deontological inclinations),
                1 = appropriate, 2 = inappropriate.
  _nfc15        Study 6. Need for Closure, 15-item short form, 1-5 (strongly
                disagree .. strongly agree).
  _nfc41        Study 3. Need for Closure, 41-item revised form, 1-6. Some
                items are stored with 1 = strongly AGREE (the source's own value
                labels, i.e. reverse-keyed items); they are left as they are.
  _mr           Studies 3, 6 and 7. The 9-item Moral Relativism Questionnaire:
                for each pair of views, a 1-10 point between the absolutist
                (1) and relativist (10) pole. Same nine pairs, same order and
                same 1-10 scale in all three surveys, so they are pooled;
                `cov_study` says which study. Study 3 calls the items Q3.1_1 ..
                Q5.5_1, Study 7 moral1-9, Study 6 mr1-9; all become mr1-mr9.
  _mr_agree     Study 4. The same nine absolutist statements rated 1-7
                (strongly disagree .. strongly agree): a different response
                format, so not pooled with _mr. Between-subjects time-pressure
                manipulation: `treat` = 1 time pressure (n=122), 0 control
                (n=129). Each condition answered its own block of nine
                questions (Q3.1/Q127-Q134 control; Q137-Q146 time pressure).
  _immorality   Study 5. "Do you consider ... immoral?", 11 issues, 1-7.
  _stance       Studies 6, 7, 8. Stance on an issue, coded 1 = oppose,
                2 = neither/other, 3 = support. Studies 6 and 7 ask the same six
                questions (stance_abortion ..). Study 8 asks a different six
                (adds same-sex marriage, asks about free access to guns rather
                than gun control), so its items are stance8_*. Study 8's
                political-ideology question (source Q2_2) is not a stance item
                and is not written.

`id` is the respondent: "study<k>_<Qualtrics ResponseID>". The Study 5-8 long
files repeat each person's questionnaire answers on every issue/trial row; only
the issue-specific ban/immorality/attitude-strength columns vary, and none of
those is written here. The script asserts that every column it writes is
identical across a person's rows before keeping one row per person.

`cov_completion_time_s` is the survey's total duration in seconds (it is the
same for every item, so it is not `rt`). `date` is RecordedDate (Studies 3, 4,
5, 8; day precision only in the 5 and 8 Stata files) or StartDate (6, 7), in
Unix seconds. `cov_gender` 1 female, 2 male, 3 another term; `cov_socialclass`
1 working .. 5 upper class.

Until 2026-10-05 this script appended the issue/trial to `id` (one person
became up to 11 ids with identical answers), coded stance "neither" and
"support" both 4, pooled the 41- and 15-item NFC forms, pooled three different
moral-relativism instruments into `_moral` (Study 4's condition suffixes were
on the wrong block for 12 of 18 item codes, and its item numbers were shifted
by three), served Study 3's NFC items 13 and 15 from the consent questions
(constant 1), and took Study 3's education, social class and country of
residence as age, gender and social class. See irw#2563.

Usage: python3 moral_absolutism_goyal_2025.py [raw_dir] [out_dir]
"""
import os
import sys

import numpy as np
import pandas as pd
import pyreadstat

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw_data"
OUT = sys.argv[2] if len(sys.argv) > 2 else "irw_processed_tables"
PREFIX = "moral_absolutism_goyal_2025_"

COV_ORDER = ["cov_study", "cov_age", "cov_gender", "cov_socialclass", "cov_completion_time_s"]


def unix_seconds(s):
    """Datetime column -> Unix seconds (Int64). Unit-safe under pandas 3."""
    s = pd.to_datetime(s, errors="coerce")
    out = (s - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)
    return out.astype("Int64")


def read_sav(name):
    return pyreadstat.read_sav(os.path.join(RAW, name), apply_value_formats=False)


def read_long(name, key, keep):
    """One row per person from a long file, asserting the kept columns never vary."""
    df = pd.read_stata(os.path.join(RAW, name), convert_categoricals=False)
    varying = df.groupby(key)[keep].nunique(dropna=False)
    bad = [c for c in keep if (varying[c] > 1).any()]
    assert not bad, f"{name}: columns vary within person: {bad}"
    one = df.drop_duplicates(key)
    assert len(one) == df[key].nunique()
    return one.reset_index(drop=True)


def person_cols(df, study, rid, date, age, gender, cls, dur):
    df = df.copy()
    df["_id"] = f"study{study}_" + df[rid].astype(str)
    assert df["_id"].is_unique, f"study {study}: ids not unique"
    df["_date"] = unix_seconds(df[date])
    df["_cov_age"] = df[age]
    df["_cov_gender"] = df[gender]
    df["_cov_socialclass"] = df[cls]
    df["_cov_completion_time_s"] = df[dur]
    return df


def melt(df, study, items):
    """items: {source column: item name}. One row per person-item with a response."""
    base = df[list(items)].rename(columns=items)
    base.insert(0, "id", df["_id"].values)
    for c in ["date", "cov_age", "cov_gender", "cov_socialclass", "cov_completion_time_s"]:
        base[c] = df["_" + c].values
    base["cov_study"] = study
    long = base.melt(id_vars=[c for c in base.columns if c not in items.values()],
                     value_vars=list(items.values()), var_name="item", value_name="resp")
    return long.dropna(subset=["resp"])


def build():
    tables = {}

    # ---- Study 3 (wide; Qualtrics question ids) ----
    s3raw, s3meta = read_sav("Study 3 Data.sav")
    s3 = person_cols(s3raw, 3, "ResponseId", "RecordedDate", "Q197", "Q194", "Q213",
                     "Duration__in_seconds_")
    # NFC items are Q1..Q41, except that items 13 and 15 are Q13.0 / Q15.0 because
    # Q13 / Q15 are consent screens (and Q22.0, Q24.0-Q32.0 are a different block).
    nfc41 = {(f"Q{i}.0" if i in (13, 15) else f"Q{i}"): f"nfc{i}" for i in range(1, 42)}
    for src in nfc41:
        lab = s3meta.column_names_to_labels[src]
        assert "uncomfortable answering" not in lab and "Title of Study" not in lab \
            and "never justified" not in lab, (src, lab)
    tables["nfc41"] = [melt(s3, 3, nfc41)]
    mr3 = {"Q3.1_1": "mr1", "Q3.3_1": "mr2", "Q3.5_1": "mr3", "Q4.1_1": "mr4", "Q4.3_1": "mr5",
           "Q4.5_1": "mr6", "Q5.1_1": "mr7", "Q5.3_1": "mr8", "Q5.5_1": "mr9"}
    tables["mr"] = [melt(s3, 3, mr3)]

    # ---- Study 4 (wide; one block of nine per condition) ----
    s4raw, _ = read_sav("Study 4 Data Experimental NFC.sav")
    s4 = person_cols(s4raw, 4, "ResponseId", "RecordedDate", "Q7.7", "Q7.6", "Q7.14",
                     "Duration__in_seconds_")
    control = ["Q3.1", "Q127", "Q128", "Q129", "Q130", "Q131", "Q132", "Q133", "Q134"]
    timed = ["Q137", "Q138", "Q139", "Q141", "Q142", "Q143", "Q144", "Q145", "Q146"]
    assert (s4.loc[s4[control].notna().any(axis=1), "condname"] == "control").all()
    assert (s4.loc[s4[timed].notna().any(axis=1), "condname"] == "timepressure").all()
    a = melt(s4[s4.condname == "control"], 4, {q: f"mr{k}" for k, q in enumerate(control, 1)})
    b = melt(s4[s4.condname == "timepressure"], 4, {q: f"mr{k}" for k, q in enumerate(timed, 1)})
    a["treat"], b["treat"] = 0, 1
    tables["mr_agree"] = [a, b]

    # ---- Study 5 (long: 11 issue rows per person) ----
    imm = {"abortion": "abortion", "death": "deathpenalty", "euth": "euthanasia", "hunt": "hunting",
           "marij": "marijuana", "homosex": "homosexuality", "gun": "gunownership", "bribes": "bribes",
           "pesticide": "pesticide", "refusecharity": "refusecharity", "oldagehomes": "oldagehomes"}
    pc5 = ["ResponseID", "RecordedDate", "age", "gender", "class", "Durationinseconds"]
    s5 = person_cols(read_long("Study 5 Data Long Format Support for Bans.dta", "MID", list(imm) + pc5),
                     5, "ResponseID", "RecordedDate", "age", "gender", "class", "Durationinseconds")
    tables["immorality"] = [melt(s5, 5, imm)]

    # ---- Study 6 (long: 6 issue rows per person) ----
    mfq = {f"mfq{i}": f"mfq{i}" for i in range(1, 17) if i != 6}   # 6th item is `math`, a catch item
    pp = {f"pp{i}": f"pp{i}" for i in range(1, 12)}
    dt = {f"dt{i}": f"dt{i}" for i in range(1, 4)}
    nfc15 = {f"nfc{i}": f"nfc{i}" for i in range(1, 16)}
    mr6 = {f"mr{i}": f"mr{i}" for i in range(1, 10)}
    st6 = {"abortion": "stance_abortion", "deathpenalty": "stance_deathpenalty",
           "guncontrol": "stance_guncontrol", "weed": "stance_marijuana",
           "hunting": "stance_hunting", "euthanasia": "stance_euthanasia"}
    pc6 = ["ResponseID", "StartDate", "age", "gender", "class", "totalduration"]
    s6 = read_long("Study 6 Data Long Format .dta", "PID",
                   list(mfq) + list(pp) + list(dt) + list(nfc15) + list(mr6) + list(st6) + pc6)
    s6 = person_cols(s6, 6, "ResponseID", "StartDate", "age", "gender", "class", "totalduration")
    tables["mfq"] = [melt(s6, 6, mfq)]
    tables["pp"] = [melt(s6, 6, pp)]
    tables["dt"] = [melt(s6, 6, dt)]
    tables["nfc15"] = [melt(s6, 6, nfc15)]
    tables["mr"].append(melt(s6, 6, mr6))
    # Studies 6 and 7 store 1 = support, 2 = oppose, 3 = neither/other (the survey's
    # option order; Study 7's own `oppose*` flags are exactly code == 2, and
    # `opposegun` is code == 1, since supporting gun control is opposing guns).
    stance67 = {1: 3, 2: 1, 3: 2}
    st = melt(s6, 6, st6)
    st["resp"] = st["resp"].map(stance67)
    tables["stance"] = [st]

    # ---- Study 7 (long: 6 trial rows per person) ----
    mr7 = {f"moral{i}": f"mr{i}" for i in range(1, 10)}
    st7 = {"abortion": "stance_abortion", "deathpenalty": "stance_deathpenalty",
           "guncontrol": "stance_guncontrol", "marijuana": "stance_marijuana",
           "hunting": "stance_hunting", "euthanasia": "stance_euthanasia"}
    pc7 = ["ResponseID", "StartDate", "age", "gender", "class", "totalduration"]
    s7 = person_cols(read_long("Study 7 Data Long Format.dta", "MID", list(mr7) + list(st7) + pc7),
                     7, "ResponseID", "StartDate", "age", "gender", "class", "totalduration")
    tables["mr"].append(melt(s7, 7, mr7))
    st = melt(s7, 7, st7)
    st["resp"] = st["resp"].map(stance67)
    tables["stance"].append(st)

    # ---- Study 8 (long: 6 trial rows per person) ----
    # Value labels: 0 = Oppose, 1 = Support, 2 = Neither. Q2_2 (political ideology) is skipped.
    st8 = {"Q108": "stance8_abortion", "Q2_3": "stance8_samesexmarriage", "Q2_4": "stance8_marijuana",
           "Q2_5": "stance8_deathpenalty", "Q2_6": "stance8_hunting", "Q2_7": "stance8_gunaccess"}
    pc8 = ["ResponseId", "RecordedDate", "Q8_7", "Q8_6", "Q8_14", "Duration__in_seconds_"]
    s8 = person_cols(read_long("Study 8 data long format.dta", "ResponseId", list(st8) + pc8),
                     8, "ResponseId", "RecordedDate", "Q8_7", "Q8_6", "Q8_14", "Duration__in_seconds_")
    st = melt(s8, 8, st8)
    st["resp"] = st["resp"].map({0: 1, 2: 2, 1: 3})
    tables["stance"].append(st)

    return {k: pd.concat(v, ignore_index=True) for k, v in tables.items()}


# Allowed resp values per table (from each questionnaire's response options).
SCALE = {"mfq": range(1, 7), "pp": range(1, 6), "dt": range(1, 3), "nfc15": range(1, 6),
         "nfc41": range(1, 7), "mr": range(1, 11), "mr_agree": range(1, 8),
         "immorality": range(1, 8), "stance": range(1, 4)}
POOLED = {"mr", "stance"}   # more than one study: keep cov_study


def finish(name, d):
    assert d["resp"].notna().all(), f"{name}: unmapped resp"
    assert np.allclose(d["resp"], d["resp"].round())
    d["resp"] = d["resp"].round().astype(int)
    bad = d.loc[~d["resp"].isin(list(SCALE[name])), ["item", "resp"]].drop_duplicates()
    assert bad.empty, f"{name}: out-of-scale values\n{bad}"
    assert not d.duplicated(["id", "item"]).any(), f"{name}: duplicate id-item"
    for c in ["cov_age", "cov_gender", "cov_socialclass", "cov_completion_time_s"]:
        d[c] = pd.to_numeric(d[c]).round().astype("Int64")
    covs = [c for c in COV_ORDER if c != "cov_study" or name in POOLED]
    cols = ["id", "item", "resp"] + [c for c in ("treat", "date") if c in d] + covs
    return d[cols].sort_values(["id", "item"]).reset_index(drop=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, d in build().items():
        d = finish(name, d)
        path = os.path.join(OUT, f"{PREFIX}{name}.csv")
        d.to_csv(path, index=False, na_rep="")
        print(f"{PREFIX}{name}: {len(d)} rows, {d['id'].nunique()} ids, {d['item'].nunique()} items")


if __name__ == "__main__":
    main()
