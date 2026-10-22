"""
The Italian Intolerance of Uncertainty Scale-Revised validation battery: a
community sample of 761 adults and a separate sample of 163 psychology
undergraduates retested one month later. The community file merges four
related studies run between 2012 and 2017, so not everyone answered every
instrument -- which is why the per-table N below ranges from 127 to 761.

Source: Bottesi G, Noventa S, Freeston MH, Ghisi M (2019). Seeking certainty
        about Intolerance of Uncertainty: Addressing old and new issues
        through the Intolerance of Uncertainty Scale-Revised. PLOS ONE 14(2):
        e0211929.
DOI: 10.1371/journal.pone.0211929
Data: https://plos.figshare.com/articles/dataset/_/7703045 --
        pone.0211929.s002.csv (community sample, 761 x 388) and
        pone.0211929.s003.csv (undergraduate retest sample, 163 x 43). Both
        are ';'-delimited, latin-1, with decimal commas.
License: CC BY 4.0 (verified on the figshare record and on the PLOS ONE
        article page; figshare article 7703045, license.name "CC BY 4.0")
Item text: shipped for the IUS-R only -- HELD, see below. Not shipped for the
        other eleven tables. Nine of them are published instruments whose
        wording is NOT in the deposit: the Italian OBQ-87 (Sica et al.), NPOQ
        (Bottesi & Ghisi 2017), PSWQ (Morani, Pricci & Sanavio 1999), BAI and
        BDI-II (Sica et al. / Ghisi et al.; both Pearson instruments), DASS-21
        (Bottesi et al. 2015), OCI-R and SPS (Sica et al.), and the NJRE-Q-R.
        Each would need its published Italian form, which is a multi-hop
        citation away, and several are commercially licensed. The remaining
        two (WW, CAQ) are not even named in the paper -- see "Two unidentified
        blocks" below.
        The IUS-R's own 12 Italian stems and all five anchor labels ARE in
        hand: pone.0211929.s001.pdf is the complete Italian IUS-R form,
        numbered 1-12 with "Per niente d'accordo .. Completamente d'accordo"
        printed against every item. It is NOT shipped: the Intolerance of
        Uncertainty Scale family carries a `block` verdict in
        itemtext/instrument_rights_register.csv (2026-10-15 counsel ruling --
        the only located statement is a distributor's, and Freeston's own 1994
        terms were never found). An IUS-R row has been added as `hold` with
        the one fact that could change it: Freeston is a co-author of THIS
        CC BY article, and its S1 File is the instrument in full. Overriding
        a standing `block` is Ben's call, not this script's.

PII: none. Two free-text clinical self-report columns were DROPPED and are not
carried forward in any form -- not as cov_*, not hashed, not bucketed:
  s002: `tipo_probl`  ("type of psychological problem", 58 distinct answers,
                       one of which narrates a sibling's death)
        `tipo_farmaci` ("medication taken", 39 distinct, e.g. a named list)
  s003: `Probl_Psico_Tipo`, `Probl_Psico_Fam_Tipo`, `Mal_Fisiche_Tipo`,
        `Mal_Neuro_Tipo`, `Farmaci_Tipo` (same shape)
The binary yes/no flags those columns followed up (`probl_psico`, `farmaci`)
are kept as covariates; it is the free text that is dropped. There are no
names, emails, dates of birth, locations, postal codes or platform IDs
anywhere in either file. Ruled by ben-domingue 2026-10-21 on exactly this
deposit: a short free-text condition/medication field is a drop-the-column
case, like a postal code, rather than the whole-candidate skip that the
"free-text clinical narratives" line in the pipeline's PII rule would
otherwise make it.

`id` is the deposit's own sequential respondent number, prefixed with the
sample it came from: the community file's `ID_new` (1-761, unique) and the
undergraduate file's `ID` (1-163). The prefix is load-bearing twice over --
the two samples' numbers overlap, and the prefix is applied in EVERY table so
that a reader joining, say, bottesi_2019_pswq to bottesi_2019_ius_r gets the
same respondent under the same id. The community file also carries `Old_ID`,
a study-specific alphanumeric code with 37 duplicate values; it is not used.

Covariate codings are not documented anywhere in the deposit, but the paper's
Participants section reports every category's percentage, which pins all of
them exactly -- 1 = 302 men and 2 = 459 women against "302 men and 459
women", and nine distinct occupation percentages matching nine codes. The
mapping is asserted against those published counts below rather than assumed,
so a mis-ordered label fails the run instead of shipping.

Two unidentified blocks: `WW_01..WW_37` and `CAQ_01..CAQ_35` are clean 1-5
agreement batteries answered by the same 429 respondents as the NPOQ and
PSWQ, i.e. by one of the four merged studies. The paper's Measures section
lists only the nine instruments it analyses and names neither block, and
neither is a prefix of any instrument cited in the paper (checked: no WW or
CAQ column equals any IUS-R item, and the block means correlate r = .43 and
.42 with the IUS-R, so both are related-but-distinct constructs). They are
shipped as item-level responses under the deposit's own item codes with the
construct unidentified, which is what the data supports; a later pass with
the other three source papers in hand could name them.

Output: 13 tables. One instrument per file -- they are not one scale, and
their response formats differ (1-5, 1-7, 0-3, 0-4, 0-10).
  bottesi_2019_ius_r     12 items, 1-5,  921 ids (both samples, wave 1-2)
  bottesi_2019_ww37      37 items, 1-5,  429 ids   (construct unidentified)
  bottesi_2019_caq35     35 items, 1-5,  429 ids   (construct unidentified)
  bottesi_2019_npoq      12 items, 1-5,  429 ids
  bottesi_2019_pswq      16 items, 1-5,  429 ids
  bottesi_2019_bai       21 items, 0-3,  259 ids
  bottesi_2019_bdi2      21 items, 0-3,  259 ids
  bottesi_2019_obq87     87 items, 1-7,  213 ids
  bottesi_2019_njre_checklist 10 items, 0-1, 213 ids
  bottesi_2019_njre_severity   7 items, 1-7, 213 ids
  bottesi_2019_dass21    21 items, 0-3,  170 ids
  bottesi_2019_oci_r     18 items, 0-4,  127 ids
  bottesi_2019_sps       20 items, 0-4,  127 ids
Skipped: `ocid1..ocid42`, a 42-item 0-4 block, because only 86 respondents
answered it -- below the N(unique id) >= 100 floor.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

S002 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("pone.0211929.s002.csv")
S003 = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("pone.0211929.s003.csv")
OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

IUS = [f"IUS2_{i:02d}" for i in range(1, 13)]

# One instrument per table. The key is the output table's suffix.
BLOCKS = [
    ("ww37",   [f"WW_{i:02d}" for i in range(1, 38)]),
    ("caq35",  [f"CAQ_{i:02d}" for i in range(1, 36)]),
    ("npoq",   [f"NPOQ_{i:02d}" for i in range(1, 13)]),
    ("pswq",   [f"PSWQ_{i:02d}" for i in range(1, 17)]),
    ("bai",    [f"BAI{i}" for i in range(1, 22)]),
    ("bdi2",   [f"BDI{i}" for i in range(1, 22)]),
    ("obq87",  [f"OBQ{i}" for i in range(1, 88)]),
    # The NJRE-Q-R is two scales in one block and must not be one table: a
    # ten-item 0/1 checklist of Not Just Right Experiences, then seven 1-7
    # severity ratings about the most recent one. NJRE11 and NJRE12 are the
    # two follow-up counts, answered by 51-52 respondents on their own
    # formats -- below both floors, so they are skipped.
    ("njre_checklist", [f"NJRE{i}" for i in range(1, 11)]),
    ("njre_severity",  [f"NJRE{i}" for i in range(13, 20)]),
    ("dass21", [f"DASS{i}" for i in range(1, 22)]),
    ("oci_r",  [f"OCI{i}" for i in range(1, 19)]),
    ("sps",    [f"SPS{i}" for i in range(1, 21)]),
]

# Below the N >= 100 floor: 86 respondents. Kept here so the column-balance
# assertion can account for it explicitly rather than by omission.
OCID = [f"ocid{i}" for i in range(1, 43)]
NJRE_FOLLOWUP = ["NJRE11", "NJRE12"]

GENDER = {1: "male", 2: "female"}
MARITAL = {1: "single/living alone", 2: "married/in a domestic relationship",
           3: "separated/divorced", 4: "widowed"}
OCCUPATION = {1: "student", 2: "full-time employment",
              3: "part-time employment", 4: "occasionally employed",
              5: "full-time homemaker", 6: "unemployed", 7: "retired",
              8: "unable to work due to disability", 9: "other"}

# Published counts and percentages from the paper's Participants section,
# used to pin the covariate codings rather than guess them.
COMMUNITY_GENDER_N = {"male": 302, "female": 459}
COMMUNITY_MARITAL_PCT = {"single/living alone": 54.7,
                         "married/in a domestic relationship": 39.3,
                         "separated/divorced": 5.1, "widowed": 0.9}
COMMUNITY_OCCUPATION_PCT = {"full-time employment": 43.8, "student": 28.1,
                            "part-time employment": 7.9,
                            "full-time homemaker": 3.8,
                            "occasionally employed": 3.9, "retired": 3.3,
                            "unemployed": 3.4,
                            "unable to work due to disability": 0.4,
                            "other": 5.4}
STUDENT_GENDER_N = {"male": 47, "female": 116}

COVS = ["cov_sample", "cov_age", "cov_gender", "cov_marital_status",
        "cov_education_years", "cov_occupation", "cov_psych_problem",
        "cov_medication"]

# Free-text clinical self-report. Dropped outright -- see the header.
DROPPED_FREE_TEXT = {
    "tipo_probl": "free-text 'type of psychological problem'",
    "tipo_farmaci": "free-text 'medication taken'",
    "Probl_Psico_Tipo": "free-text 'type of psychological problem'",
    "Probl_Psico_Fam_Tipo": "free-text family psychiatric history",
    "Mal_Fisiche_Tipo": "free-text physical illness",
    "Mal_Neuro_Tipo": "free-text neurological illness",
    "Farmaci_Tipo": "free-text 'medication taken'",
}


def read(path: Path) -> pd.DataFrame:
    """The source files are ';'-delimited latin-1 with decimal commas."""
    return pd.read_csv(path, sep=";", decimal=",", encoding="latin-1")


def pii_screen(df: pd.DataFrame, label: str) -> None:
    """Print the denominator, then name every text column.

    A screen that selects nothing reports clean, which is the worst possible
    shape for a safety check -- hence the explicit non-zero assertion and the
    use of is_string_dtype rather than `dtype == object`.
    """
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen [{label}]: examined {len(text_cols)} text column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0, "nothing to screen"
    unexpected = [c for c in text_cols
                  if c not in DROPPED_FREE_TEXT and c not in ("Old_ID", "Codice")]
    assert not unexpected, f"unscreened text column(s): {unexpected}"
    # Old_ID / Codice are study-specific alphanumeric codes, not identifiers
    # of a person outside the deposit; neither is carried into the output.


def label(series: pd.Series, mapping: dict, name: str) -> pd.Series:
    bad = set(series.dropna().unique()) - set(mapping)
    assert not bad, f"{name}: unmapped code(s) {bad}"
    return series.map(mapping)


def community() -> pd.DataFrame:
    df = read(S002)
    print("community raw shape", df.shape)
    pii_screen(df, "s002")

    assert df["ID_new"].is_unique, "ID_new is not one row per respondent"
    assert df["ID_new"].between(1, 761).all()
    out = pd.DataFrame(index=df.index)
    out["id"] = "community_" + df["ID_new"].astype(int).astype(str)

    out["cov_sample"] = "community"
    out["cov_age"] = df["age"]
    out["cov_gender"] = label(df["gender"], GENDER, "gender")
    out["cov_marital_status"] = label(df["stCivile"], MARITAL, "stCivile")
    out["cov_education_years"] = df["scolarita"]
    out["cov_occupation"] = label(df["occupazione"], OCCUPATION, "occupazione")
    out["cov_psych_problem"] = df["probl_psico"]
    out["cov_medication"] = df["farmaci"]

    # The codings are not documented in the deposit; these assertions are what
    # establishes them, against the paper's own published figures.
    counts = out["cov_gender"].value_counts().to_dict()
    assert counts == COMMUNITY_GENDER_N, (counts, COMMUNITY_GENDER_N)
    for key, pct in COMMUNITY_MARITAL_PCT.items():
        got = round(100 * (out["cov_marital_status"] == key).sum() / len(out), 1)
        assert got == pct, ("marital", key, got, pct)
    for key, pct in COMMUNITY_OCCUPATION_PCT.items():
        got = round(100 * (out["cov_occupation"] == key).sum() / len(out), 1)
        assert got == pct, ("occupation", key, got, pct)
    print("covariate codings confirmed against the paper's published "
          "percentages (gender, marital status, all nine occupations)")

    items = [c for _, cols in BLOCKS for c in cols] + IUS
    for c in items + OCID + NJRE_FOLLOWUP:
        assert c in df.columns, c
    out = pd.concat([out, df[items + OCID]], axis=1)

    # Balance the books: every source column is either in the output, or
    # skipped for a printed reason.
    used = {"ID_new", "age", "gender", "stCivile", "scolarita", "occupazione",
            "probl_psico", "farmaci"} | set(items) | set(OCID)
    composites = [
        "bai", "bdi2tot", "DASSTotal", "PSWQ", "IUSTotal", "IUS_P", "IUS_I",
        "NPOQTotal", "tolerance", "OCI_Totale", "SPSTotal",
    ] + [f"PSWQ_{i:02d}rev" for i in (1, 3, 8, 10, 11)]
    skipped = {c: "subscale or total score computed across items -- a "
                  "composite, not a response" for c in composites}
    skipped.update({f"PSWQ_{i:02d}rev": "reverse-coded copy of an item "
                                        "already shipped unrecoded"
                    for i in (1, 3, 8, 10, 11)})
    for c in NJRE_FOLLOWUP:
        n = df[c].notna().sum()
        skipped[c] = (f"NJRE-Q-R follow-up count answered by {n} "
                      "respondents, on its own format -- below the N >= 100 "
                      "floor and below the 3-item floor on its own")
    skipped["Old_ID"] = ("study-specific alphanumeric code with 37 duplicate "
                         "values; ID_new is the unique respondent number")
    skipped.update({c: f"{why} -- DROPPED, not carried forward in any form"
                    for c, why in DROPPED_FREE_TEXT.items()
                    if c in df.columns})
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted s002 columns: {leftover}"
    for c, why in sorted(skipped.items()):
        print(f"  skipped s002 column {c}: {why}")
    return out


def students() -> pd.DataFrame:
    """The 163 undergraduates, long over the two IUS-R administrations.

    `IUS2_nn_R` is the one-month RETEST, not a reverse-coded copy: across the
    12 items it correlates r = .44-.62 with the first administration and is
    identical on only 40-79% of respondents, where a reverse-code would be
    exactly 6 - x on every row (it is on 1-17%).
    """
    df = read(S003)
    print("student raw shape", df.shape)
    pii_screen(df, "s003")

    # One of the 163 rows (Codice LC0390) has a blank `ID` but a complete
    # pair of IUS-R administrations. The 162 numbers that are present cover
    # 1-163 with exactly one gap, so the missing respondent's own number is
    # recoverable rather than invented -- which is better than dropping a
    # respondent who answered everything.
    missing = sorted(set(range(1, 164)) - set(df["ID"].dropna().astype(int)))
    assert len(missing) == 1 and df["ID"].isna().sum() == 1, \
        (missing, df["ID"].isna().sum())
    df.loc[df["ID"].isna(), "ID"] = missing[0]
    print(f"recovered the one blank student ID as {missing[0]} -- the single "
          f"gap in the otherwise complete 1-163 sequence")
    assert df["ID"].is_unique, "ID is not one row per student"
    base = pd.DataFrame(index=df.index)
    base["id"] = "student_" + df["ID"].astype(int).astype(str)
    base["cov_sample"] = "students"
    base["cov_age"] = df["Età"]
    base["cov_gender"] = label(df["Genere"], GENDER, "Genere")
    base["cov_marital_status"] = label(df["Stato_Civile"], MARITAL,
                                       "Stato_Civile")
    base["cov_education_years"] = df["Freq_Scolastica"]
    base["cov_occupation"] = label(df["Occupazione"], OCCUPATION,
                                   "Occupazione")
    base["cov_psych_problem"] = df["Probl_Psico"]
    base["cov_medication"] = df["Farmaci"]

    counts = base["cov_gender"].value_counts().to_dict()
    assert counts == STUDENT_GENDER_N, (counts, STUDENT_GENDER_N)

    retest = [f"{c}_R" for c in IUS]
    for c in IUS + retest:
        assert c in df.columns, c
    for c in IUS:
        pair = df[[c, f"{c}_R"]].dropna()
        exact_reverse = ((6 - pair[c]) == pair[f"{c}_R"]).mean()
        assert exact_reverse < 0.25, \
            f"{c}_R looks like a reverse-code, not a retest ({exact_reverse:.2f})"

    waves = []
    for wave, cols in ((1, IUS), (2, retest)):
        block = pd.concat([base, df[cols]], axis=1)
        block.columns = list(base.columns) + IUS
        block["wave"] = wave
        waves.append(block)

    used = {"ID", "Età", "Genere", "Stato_Civile", "Freq_Scolastica",
            "Occupazione", "Probl_Psico", "Farmaci"} | set(IUS) | set(retest)
    skipped = {
        "Codice": "study-specific alphanumeric code; ID is the respondent "
                  "number",
        "Peso": "body weight, collected only in this sample -- the merged "
                "IUS-R table carries the covariates both samples share",
        "Altezza": "body height, collected only in this sample",
        "Probl_Psico_Fam": "family psychiatric history flag, collected only "
                           "in this sample",
        "Mal_Fisiche": "physical illness flag, collected only in this sample",
        "Mal_Neuro": "neurological illness flag, collected only in this "
                     "sample",
    }
    skipped.update({c: f"{why} -- DROPPED, not carried forward in any form"
                    for c, why in DROPPED_FREE_TEXT.items()
                    if c in df.columns})
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted s003 columns: {leftover}"
    for c, why in sorted(skipped.items()):
        print(f"  skipped s003 column {c}: {why}")
    return pd.concat(waves, ignore_index=True)


def write(wide: pd.DataFrame, cols: list[str], table: str,
          extra: list[str] = ()) -> None:
    long = wide[["id"] + COVS + list(extra) + cols].melt(
        id_vars=["id"] + COVS + list(extra), var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(float)
    assert not (long["resp"] % 1 != 0).any(), f"{table}: fractional responses"
    long["resp"] = long["resp"].astype(int)
    order = ["id", "item", "resp"] + list(extra) + \
            [c for c in long.columns if c.startswith("cov_")]
    long = long[order].sort_values(["id"] + list(extra) + ["item"])
    assert long["id"].nunique() >= 100, \
        f"{table}: {long['id'].nunique()} ids, below the floor of 100"
    assert long["item"].nunique() >= 3, f"{table}: fewer than 3 items"
    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


def main() -> None:
    comm = community()
    stud = students()

    # The IUS-R is the same 12 items on the same 1-5 scale in both samples,
    # so it is one file with cov_sample, not two (and `wave` carries the
    # undergraduates' one-month retest).
    comm_ius = comm[["id"] + COVS + IUS].copy()
    comm_ius["wave"] = 1
    ius = pd.concat([comm_ius, stud[["id"] + COVS + IUS + ["wave"]]],
                    ignore_index=True)
    assert ius.groupby(["id", "wave"]).size().max() == 1, "duplicate id x wave"
    write(ius, IUS, "bottesi_2019_ius_r", extra=["wave"])

    for suffix, cols in BLOCKS:
        wide = comm[["id"] + COVS + cols]
        n = wide[cols].notna().any(axis=1).sum()
        if n < 100:
            print(f"skipped block {suffix}: {n} respondents, below the floor")
            continue
        write(wide, cols, f"bottesi_2019_{suffix}")

    n_ocid = comm[OCID].notna().any(axis=1).sum()
    print(f"skipped block ocid1..ocid42: {n_ocid} respondents answered it, "
          "below the N(unique id) >= 100 floor")
    assert n_ocid < 100, "ocid now clears the floor -- ship it"


if __name__ == "__main__":
    main()
