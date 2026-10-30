#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/3BZAUD
# DOI: 10.7910/DVN/3BZAUD
# Deposit: Trusz, S. (2022). Supplementary materials for the chapter "Math and
#   literacy anxiety, study major preferences, and expectancy effects",
#   prepared for "The international handbook of gender beliefs, stereotype
#   threat, and teacher expectations", ed. P. Watson, Routledge. Harvard
#   Dataverse. Pedagogical University in Krakow.
# Data: 8_AnxietyAchievementExpectancies_Routledge_n897.tab, downloaded with
#   `?format=original` -- it is an SPSS .sav, and the .tab conversion would
#   have dropped every variable and value label.
# Codebook: the deposit's own 1_IIEQ.docx and 2_LAS.docx, which print the
#   instruments item by item with their anchors and subscale assignments.
# License: CC0 1.0 (Dataverse license field on the deposit).
#
# TWO DOIs, ONE DEPOSIT. 10.7910/DVN/IEEH3O (deposited 2022-02-08) and
# 10.7910/DVN/3BZAUD (2022-06-06, titled "... After Review") hold the same
# eight files; all three downloaded files are byte-identical by md5 across the
# two. This script cites 3BZAUD, the later one, and IEEH3O is marked a
# superseded duplicate in the leads file so a later pass does not build it a
# second time.
#
# Five output tables, one per instrument/section, which is also one per
# response scale and per referent:
#
#   SelfExp1-14     IIEQ I,   students' own expectancies about their matura
#   ParentExp1-14   IIEQ II,  what the student's parents said or thought
#   TeacherExp1-14  IIEQ III, what the student's teachers said or thought
#                   all three 1-4: definitely disagree .. definitely agree
#   AMAS1-9         Abbreviated Math Anxiety Scale, 1-5
#   LAS1-9          Literacy Anxiety Scale, 1-5: no anxiety .. paralyzing
#
# The three IIEQ sections are separate tables rather than one crossed 42-item
# table: unlike the lee_whiting trust_actors case, these are not one stem asked
# about three referents, they are three different sets of statements, and the
# deposit's own derived variables treat them as three scales (SSEMat/SSELit,
# PEMat/PELit, TEMat/TELit).
#
# EVERY `_1` COLUMN IS DROPPED -- they are the imputed copies, and the file
# says so: a string variable named `AfterImputationMissingData` sits between
# the raw block and the `_1` block as a section marker, labelled "Imputation of
# missing data - Linear interpolation", and `EgzamMat_1`'s own label is
# literally "LINT(EgzamMat)". The arithmetic confirms it item by item: AMAS1 is
# integer-only with 867 of 897 answered, while AMAS1_1 is complete and carries
# 23 cells at 1.333.., 1.5, 1.666.. and the like. Shipping the `_1` block would
# have put 1,050-odd interpolated values into `resp` behind a plausible-looking
# 1-5 range. The raw blocks are integer-only -- asserted below.
#
# The `r` columns (SelfExp6r/7r/8r/10r, ParentExp2r/3r) are the depositor's
# reverse-scored copies of items the IIEQ marks "* reverse scale". The raw item
# is shipped as collected and the recode dropped; nothing is lost, and which
# items are reversed is in the item text table's own notes via the instrument.
#
# Item text: SHIPPED for the three IIEQ sections and the LAS, from the
# deposit's 1_IIEQ.docx and 2_LAS.docx -- both print all 14/14/14/9 stems, the
# anchor wording, and which subscale (math vs. literacy; learning vs. testing)
# each item belongs to, so `section_id` carries the subscale. Both instruments
# are Trusz's own and arrive under the deposit's CC0.
#   NOT SHIPPED for AMAS1-9. Two independent reasons: the wording is not in
#   this deposit at all (there is no AMAS docx), so it would have to come from
#   Hopko, Mahadevan, Bare & Junt (2003), Assessment 10(2):178-182 -- a SAGE
#   subscription article with no located grant -- and the AMAS had no row in
#   itemtext/instrument_rights_register.csv. A row is written for it with this
#   batch, verdict `hold`. The LAS is registered separately as `ship`, with the
#   note that it is Trusz's literacy-domain instrument built on the AMAS's
#   two-subscale template rather than a translation or reproduction of AMAS
#   items.
#   The administration was in POLISH and the deposited wording is the authors'
#   English: Trusz is at the Pedagogical University in Krakow, the sample sat
#   the Polish matura ("matriculation test"), and the file's own id column is
#   named `lp` (liczba porzadkowa). The deposit states no translation, so this
#   is an inference and it is recorded as one -- `language` names Polish while
#   `item_text` is the English, which is the standard's documented fallback,
#   and a public note is owed. Same handling as zhang_2026_ai_companion.
#
# Dropped covariates: `Faculty`, the student's degree programme, 118 distinct
# values over 897 students ("Arabic studies", "Acoustic engineering") -- several
# are near-unique and `StudyMajor` already carries the humanities/sciences
# split that the chapter analyses. The four `TimeMat_m*`/`TimeLit_m*` columns
# (minutes per day spent learning, at two measurements each) are dropped as
# ambiguous to collapse into one covariate.
#
# PII: screened. Two string columns (`age`, `Faculty`), count asserted
# non-zero; no email, name, phone, postal code or date. Neither is shipped as
# typed: `age` becomes a covariate, `Faculty` is dropped above.

import os
import re

import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
ITEMTEXT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "automated_finding", "itemtext_output")

RAW = os.environ.get("TRUSZ_RAW", "data.sav")

AGREE = {1: "definitely disagree", 2: "rather disagree", 3: "rather agree",
         4: "definitely agree"}
ANXIETY = {1: "no anxiety", 2: "low anxiety", 3: "medium anxiety",
           4: "severe anxiety", 5: "paralyzing anxiety"}

IIEQ_INSTRUMENT = ("Interpersonal and Intrapersonal Expectancies Questionnaire "
                   "(IIEQ), Trusz 2022")
LAS_INSTRUMENT = "Literacy Anxiety Scale (LAS), Trusz 2022"

# 1_IIEQ.docx, section I. The '*' items are the ones that document marks
# "* reverse scale"; they ship as collected, not reversed.
SELF = {
    1: "I believed that I would be able to complete most of the math section of the matriculation test",
    2: "Taking the literacy section of the matriculation test I believed that I would succeed",
    3: "I was convinced that I would pass the literacy section of the matriculation test with a higher grade than most of my friends",
    4: "I expected to graduate from high school with a better grade in math than my classmates",
    5: "I was convinced that I would pass the math section of the matriculation test with a higher grade than most of my friends",
    6: "I assumed that I would not be able to pass the math section of the matriculation test",
    7: "I assumed that I would not be able to pass the literacy section of the matriculation test",
    8: "In the final year of secondary school, I was more concerned about the math than the literacy section of the matriculation test",
    9: "In the final year of secondary school, I believed that I would be able to pass the math section of the matriculation test at a high level",
    10: "In the final year of secondary school, I was more concerned about the literacy than the math section of the matriculation test",
    11: "I expected to graduate from high school with a better grade in literacy than my classmates",
    12: "I believed that I would be able to complete most of the literacy section of the matriculation test",
    13: "Taking the math section of the matriculation test I believed that I would succeed",
    14: "In the final year of secondary school, I believed that I would be able to pass the literacy section of the matriculation test at a high level",
}
SELF_MATH = {1, 4, 5, 6, 8, 9, 13}

# 1_IIEQ.docx, section II
PARENT = {
    1: "My parents told me that I am good at math",
    2: "My parents think I am weak at arts",
    3: "My parents are convinced that I cannot deal well with science",
    4: "My parents believed that I would get a high grade in literacy on my high school diploma",
    5: "My parents used to tell me that I had humanistic talents",
    6: "My parents assumed I was better at science than humanities",
    7: "My parents believed that I would be successful in the literacy section of the matriculation test",
    8: "My parents assumed I was better at humanities than science",
    9: "My parents believed in my humanistic skills",
    10: "My parents were confident that I would get a high grade in math on my high school diploma",
    11: "My parents have always emphasized that humanities are my strong point",
    12: "My parents believed that I would easily pass the math section of the matriculation test",
    13: "My parents gave me the impression that science was my strong point",
    14: "My parents gave me the impression that they believed in my math skills",
}
PARENT_MATH = {1, 3, 6, 10, 12, 13, 14}

# 1_IIEQ.docx, section III
TEACHER = {
    1: "My high school teachers were convinced that I was better at science than humanities",
    2: "My teachers were convinced that I would select technology or science study majors",
    3: "My teachers were convinced that I would do well in the literacy section of the matriculation test",
    4: "My high school teachers used to tell me to select a science major",
    5: "In high school, my teachers emphasized that I was good at literacy",
    6: "My teachers gave me the impression that they believed in my math skills",
    7: "My teachers used to tell me that I would be successful in the math section of the matriculation test",
    8: "In high school, my teachers emphasized that I was good at math",
    9: "My teachers were confident that I would get a high score in the math section of the matriculation test",
    10: "My teachers assumed that I would select humanities or social science majors",
    11: "My teachers believed in my humanistic skills",
    12: "My teachers were convinced that I would do well in the literacy section of the matriculation test",
    13: "My high school teachers were convinced that I was better at humanities than science",
    14: "My high school teachers used to tell me to select humanistic majors",
}
TEACHER_MATH = {1, 2, 4, 6, 7, 8, 9}

# 2_LAS.docx
LAS = {
    1: "Learning the rules of punctuation from the literacy handbook",
    2: "Thinking about an upcoming literacy test one day before",
    3: "Watching a teacher explaining the difference between parts of a sentence and parts of speech",
    4: "Taking a test in a literacy course",
    5: "Being given a homework assignment with many difficult problems that is due the next literacy class meeting",
    6: "Listening to a lecture in literacy class",
    7: "Listening to a classmate explaining grammar rules",
    8: "Being given a quiz in literacy class without knowing in advance",
    9: "Starting a new chapter in a literacy handbook",
}
LAS_LEARNING = {1, 3, 6, 7, 9}

IIEQ_SELF_INSTR = ("Please recall how you felt and what you were thinking in "
                   "your final year of secondary school, just before you took "
                   "the matriculation exam.")
IIEQ_PARENT_INSTR = ("Please recall what your parents thought or said about "
                     "you in your final year of high school?")
IIEQ_TEACHER_INSTR = ("Please recall what your teachers thought or said about "
                      "you in your final year of high school?")
LAS_INSTR = "Please rate your anxiety during different activities."

# name -> (column prefix, n items, anchors, instrument, instructions,
#          {item -> text} or None when item text is not shipped,
#          math-subscale set or None)
TABLES = {
    "trusz_2022_iieq_self": ("SelfExp", 14, AGREE, IIEQ_INSTRUMENT,
                             IIEQ_SELF_INSTR, SELF, SELF_MATH),
    "trusz_2022_iieq_parent": ("ParentExp", 14, AGREE, IIEQ_INSTRUMENT,
                               IIEQ_PARENT_INSTR, PARENT, PARENT_MATH),
    "trusz_2022_iieq_teacher": ("TeacherExp", 14, AGREE, IIEQ_INSTRUMENT,
                                IIEQ_TEACHER_INSTR, TEACHER, TEACHER_MATH),
    "trusz_2022_las": ("LAS", 9, ANXIETY, LAS_INSTRUMENT, LAS_INSTR,
                       LAS, LAS_LEARNING),
    "trusz_2022_amas": ("AMAS", 9, ANXIETY, None, None, None, None),
}

DEMOG = {"sample": "cov_sample", "sex": "cov_sex", "age": "cov_age",
         "StudyMajor": "cov_study_major", "EgzamMat": "cov_exam_math_pct",
         "EgzamLit": "cov_exam_literacy_pct", "MarkMat": "cov_mark_math",
         "MarkLit": "cov_mark_literacy"}

DROP_EXACT = ["id", "Faculty", "AfterImputationMissingData", "Summary",
              "filter_$", "ForFigures", "PredictedProbabilities",
              "TimeMat_m1", "TimeMat_m2", "TimeLit_m1", "TimeLit_m2",
              "TimeMat_mean", "TimeLit_mean", "AMAS_total", "LAS_total",
              "SSEMat", "SSELit", "PEMat", "PELit", "TEMat", "TELit",
              "AMASCategories_Females", "AMASCategories_Males",
              "LASCategories_Females", "LASCategories_Males"]
# every imputed copy, every reverse-scored copy, and the predicted-probability
# columns used only to draw the chapter's figures
DROP_RE = re.compile(r"_1$|^(Self|Parent)Exp[0-9]+r$|^(Fem|Mal)(AMAS|LAS)x")


def screen_for_pii(df):
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(txt)} of {len(df.columns)} columns: {txt}")
    assert txt, "PII screen selected no columns -- the selector is wrong"
    pat = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
                     r"|\+?\d{9,}"
                     r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str)
            if pat.search(v)]
    assert not hits, f"PII screen hit: {hits[:5]}"
    print("PII screen: clean")


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    raw_cols = list(df.columns)
    screen_for_pii(df)

    assert df["lp"].nunique() == len(df), "lp is not unique"
    # the deposit also carries `id`, which repeats for 22 of the 897 rows and
    # so cannot identify a respondent; `lp` is the row number and does
    df["id_out"] = df["lp"].astype(int)

    items = {n: [f"{pre}{i}" for i in range(1, k + 1)]
             for n, (pre, k, *_rest) in TABLES.items()}
    for n, cols in items.items():
        for c in cols:
            assert c in raw_cols, f"{n}: missing {c}"

    # balance the books
    item_cols = {c for cols in items.values() for c in cols}
    dropped = set(DROP_EXACT) | {c for c in raw_cols if DROP_RE.search(c)}
    accounted = item_cols | set(DEMOG) | {"lp"} | dropped
    left_out = [c for c in raw_cols if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"dropped {len(dropped)} source columns: "
          f"{len([c for c in raw_cols if c.endswith('_1')])} imputed copies, "
          f"{len([c for c in raw_cols if re.match(r'^(Self|Parent)Exp[0-9]+r$', c)])} "
          f"reverse-scored copies, "
          f"{len([c for c in raw_cols if re.match(r'^(Fem|Mal)(AMAS|LAS)x', c)])} "
          f"figure columns, and {len(DROP_EXACT)} composites/markers/"
          f"high-cardinality")

    for src, dst in DEMOG.items():
        labels = meta.variable_value_labels.get(src)
        df[dst] = df[src].map(labels) if labels else df[src]
    cov_cols = sorted(DEMOG.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ITEMTEXT_DIR, exist_ok=True)
    written = set()
    for name in sorted(TABLES):
        pre, k, anchors, instrument, instructions, texts, math_set = TABLES[name]
        cols = items[name]
        lo, hi = min(anchors), max(anchors)

        # the raw blocks must be integer-only; a fractional value here would
        # mean an imputed column slipped through the _1 filter. Test the
        # NON-NULL values only: this pandas' stack() keeps NaN, and NaN % 1
        # is NaN, which != 0 -- so a naive version of this check counts the
        # missing cells as fractional and fires on clean data.
        block = df[cols].to_numpy().ravel()
        block = block[~pd.isna(block)]
        frac = int(((block % 1) != 0).sum())
        assert frac == 0, f"{name}: {frac} fractional cells in the raw block"

        long = df.melt(id_vars=["id_out"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.rename(columns={"id_out": "id"})
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), (name, long["resp"].unique())

        assert name not in written, f"duplicate output table name {name}"
        assert len(name) <= 40, f"{name} is over the 40-character cap"
        written.add(name)
        assert long["id"].nunique() >= 100, (name, long["id"].nunique())
        assert long["item"].nunique() >= 3, (name, long["item"].nunique())

        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

        if texts is None:
            print(f"  {name}: item text NOT shipped (see header)")
            continue

        # subscale label, which is what section_id carries
        if pre == "LAS":
            sub = {True: "learning", False: "testing"}
        else:
            sub = {True: "math", False: "literacy"}
        rows = []
        for i in range(1, k + 1):
            text = texts[i]
            assert text.strip(), f"{name}: item {i} has no text"
            s = sub[i in math_set]
            for code, anchor in anchors.items():
                rows.append({
                    "table": name,
                    "section_id": f"{name}_{s}",
                    "item": f"{pre}{i}",
                    "instrument": instrument,
                    # administered in Polish (inferred, see header); the
                    # deposited wording is the authors' English, so the
                    # _translated columns are left out entirely
                    "language": "Polish",
                    "instructions": instructions,
                    "section_prompt": (
                        f"Items of the {'math' if s == 'math' else s} subscale"
                        if pre != "LAS" else
                        f"Items of the literacy anxiety - {s} subscale"),
                    "item_text": text,
                    "correct_response": "",
                    "option_text": anchor,
                    "resp": code,
                })
        it_df = pd.DataFrame(rows)
        assert len(it_df) == k * len(anchors), len(it_df)
        assert set(it_df["item"]) == set(long["item"]), f"{name}: item sets differ"
        assert set(long["resp"]) <= set(it_df["resp"]), f"{name}: resp sets differ"
        it_df.to_csv(os.path.join(ITEMTEXT_DIR, name + "__items.csv"),
                     index=False)
        print(f"  {name}__items: rows={len(it_df)} items={it_df['item'].nunique()}")


if __name__ == "__main__":
    convert()
