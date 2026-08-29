"""Dictionary-sheet rows for the 2026-08-29 Zenodo lead-work batch (44 tables).

Fully-quoted, LF-terminated, ASCII .csv for File > Import > Append (comma).

Counts are read from the staged `irw_output/*.csv`, guarded by an assert on the
expected table count -- so running this after an upload has emptied the
directory fails loudly rather than writing a header-only file.
"""
import csv
import os
import unicodedata

import pandas as pd

OUT = "biblio_2026-08-29b.csv"
STAGED = "irw_output"
DATE = "8/29/2026"
EXPECTED = 44
CC_BY = "CC BY 4.0"

COLUMNS = ["table", "table.lower", "Description", "URL (for data)", "Reference",
           "DOI (for paper)", "Original License", "Custom License",
           "Public Reshare?", "Derived License", "Custom License", "Notes",
           "Contributor", "Date"]

SOD = ("https://zenodo.org/records/13332148",
       "Soderberg, P., & Molsa, M. E. (2024). A 10-day experience sampling "
       "dataset on subjective experiences of middle and secondary school "
       "students in 2022 [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.13332148",
       "10.5281/zenodo.13332148")
EST = ("https://zenodo.org/records/5156068",
       "Estevez, I., Valle, A., Rodriguez, S., Pineiro, I., Vieites, T., "
       "Gonzalez-Suarez, R., & Rodriguez-Llorente, C. (2021). Intrinsic "
       "motivation, perceived competence, negative feelings, and math "
       "academic performance [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.5156068",
       "10.5281/zenodo.5156068")
CHE = ("https://zenodo.org/records/13855427",
       "Chen, B. (2024). Exploring the Impact of Curiosity and Sport "
       "Commitment on Creativity among Fitness Coaches: The Mediating Role of "
       "Knowledge-Sharing and Flow Experience [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.13855427",
       "10.5281/zenodo.13855427")
TOR = ("https://zenodo.org/records/15168213",
       "Torok, B., Rab, A., Punkosty, A., Labody, P., Sorban, K., Menyhard, "
       "A., Szikora, T., Vadasz, P., & Zodi, Z. (2025). Trust, Awareness, and "
       "Risk Perception in the Online Environment [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.15168213",
       "10.5281/zenodo.15168213")

S_STU = "Finnish middle- and upper-secondary school students"
S_ESM = ("Finnish middle- and upper-secondary school students, one response "
         "per momentary assessment with wave giving the study's occasion order")
S_EST = "Spanish primary school students aged 9-13"
S_CHE = "Chinese fitness coaches"
S_TOR = "a nationally representative CATI sample of Hungarian adults, fielded 2019"

BLURB = {
 "soderberg_2024_peer_support": (f"Perceived peer support at school, 6 items on a labelled 1-5 scale, {S_STU}, from the study's one-off start-up survey", SOD),
 "soderberg_2024_teacher_support": (f"Perceived teacher and school support, 9 items on a labelled 1-5 scale, {S_STU}, from the study's one-off start-up survey", SOD),
 "soderberg_2024_family_support": (f"Perceived family support for school, 4 items on a labelled 1-5 scale, {S_STU}, from the study's one-off start-up survey", SOD),
 "soderberg_2024_general_selfefficacy": (f"Short General Self-Efficacy scale, 5 items on a labelled 1-5 scale, {S_STU}, from the study's one-off start-up survey", SOD),
 "soderberg_2024_academic_selfefficacy": (f"Academic self-efficacy, 4 items on a labelled 1-5 scale, {S_STU}, from the study's one-off start-up survey", SOD),
 "soderberg_2024_esm_affect": (f"Momentary affect at school (enjoyment, stress, motivation, anger, feeling liked, loneliness, alertness, feeling stupid), 8 items on a labelled 1-5 scale, {S_ESM}", SOD),
 "soderberg_2024_esm_lecture": (f"Ratings of the most recent lecture and its teacher, 6 items on a labelled 1-5 scale, {S_ESM}", SOD),
 "soderberg_2024_esm_morning": (f"Morning check-in (sleep quality and readiness for school), 2 items on a labelled 1-5 scale, {S_ESM}", SOD),
 "estevez_2021_homework_engagement": (f"Homework amount, time spent and use of time, 5 items on a 1-5 scale, {S_EST}", EST),
 "estevez_2021_motiv": (f"12 items on a 1-5 scale, {S_EST}; the source labels the block only as MOTIV and ships no codebook, so the codes are kept verbatim rather than named", EST),
 "estevez_2021_gest": (f"4 items on a 1-5 scale, {S_EST}; the source labels the block only as GEST and ships no codebook, so the codes are kept verbatim rather than named", EST),
 "estevez_2021_inter": (f"3 items on a 1-5 scale, {S_EST}; the source labels the block only as INTER and ships no codebook, so the codes are kept verbatim rather than named", EST),
 "estevez_2021_actitu": (f"4 items on a 1-5 scale, {S_EST}; the source labels the block only as ACTITU and ships no codebook, so the codes are kept verbatim rather than named", EST),
 "estevez_2021_feepr": (f"6 items on a 1-5 scale, {S_EST}; the source labels the block only as FEEPR and ships no codebook, so the codes are kept verbatim rather than named", EST),
 "estevez_2021_feepad": (f"5 items on a 1-5 scale, {S_EST}; the source labels the block only as FEEPAD and ships no codebook, so the codes are kept verbatim rather than named", EST),
 "estevez_2021_math_attitudes": (f"Mathematics attitudes inventory, 43 items on a 1-5 scale, {S_EST}; the deposit's composites identify four subscales within it (perceived competence IAM1-4, anxiety IAM9-11, intrinsic motivation IAM35-39, negative feelings IAM40/42/43)", EST),
 "chen_2024_je": (f"5 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as JE and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_ds": (f"5 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as DS and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_sc": (f"5 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as SC and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_ts": (f"Thrill seeking, 5 items on a 1-7 agreement scale, {S_CHE}", CHE),
 "chen_2024_ec": (f"6 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as EC and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_cc": (f"5 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as CC and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_spe": (f"5 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as SPE and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_kc": (f"4 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as KC and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_kd": (f"4 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as KD and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_uf": (f"4 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as UF and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_cg": (f"4 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as CG and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_cotah": (f"4 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as COTAH and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_tot": (f"4 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as TOT and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_ae": (f"4 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as AE and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "chen_2024_cr": (f"Creativity, 9 items on a 1-7 agreement scale, {S_CHE}", CHE),
 "chen_2024_smu": (f"5 items on a 1-7 agreement scale, {S_CHE}; the source labels the block only as SMU and ships no codebook, so the codes are kept verbatim rather than named", CHE),
 "torok_2025_internet_use_frequency": (f"Frequency of using the internet for 18 named purposes, 1-5 frequency scale, {S_TOR}", TOR),
 "torok_2025_manipulation_fear": (f"Fear of being manipulated by 13 named online actors and platforms, 1-5 scale, {S_TOR}", TOR),
 "torok_2025_news_consumption": (f"How news of five kinds is consumed (ignored, read if encountered, actively sought), 5 items on a 1-3 scale, {S_TOR}", TOR),
 "torok_2025_news_source_frequency": (f"Frequency of using 8 information sources for world news, 1-5 frequency scale, {S_TOR}", TOR),
 "torok_2025_news_source_trust": (f"Trust in the credibility of information from 8 named sources, 1-5 scale, {S_TOR}", TOR),
 "torok_2025_social_media_effects": (f"Agreement with 4 statements about the effects of online contact on relationships, 1-5 scale, {S_TOR}", TOR),
 "torok_2025_facebook_uses": (f"Agreement with 4 statements about what Facebook is good for, 1-5 scale, {S_TOR}", TOR),
 "torok_2025_data_disclosure": (f"Willingness to disclose each of 8 kinds of personal data in exchange for a free service, yes/no, {S_TOR}", TOR),
 "torok_2025_legality_beliefs": (f"Beliefs about whether each of 8 online acts is lawful, yes/no, {S_TOR}; the stem asks for the respondent's own opinion and no answer key is shipped -- the battery mixes four copyright-infringement acts with two that are lawful (using Bitcoin, transferring money outside the EU), so scoring for correctness would reverse two of the eight items", TOR),
 "torok_2025_data_security": (f"How secure personal data is felt to be with each of 12 named institutions and platforms, 1-4 scale, {S_TOR}", TOR),
 "torok_2025_ai_acceptance": (f"Acceptance of artificial intelligence in 4 named domains, 1-3 scale, {S_TOR}", TOR),
 "torok_2025_discourse_responsibility": (f"How far each of 6 named actors should be responsible for improving the quality of online discourse, 1-5 scale, {S_TOR}", TOR),
}

TRANSLATE = {"‘": "'", "’": "'", "“": '"', "”": '"',
             "–": "-", "—": "-", "…": "...", "\xa0": " ",
             "\xae": "(R)", "™": "(TM)", "\xb4": "'"}


def ascii_only(value):
    for bad, good in TRANSLATE.items():
        value = value.replace(bad, good)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    assert all(ord(c) < 128 for c in value), \
        f"non-ASCII survived: {[c for c in value if ord(c) > 127]!r}"
    return value


def main():
    staged = sorted(f[:-4] for f in os.listdir(STAGED) if f.endswith(".csv"))
    assert len(staged) == EXPECTED, (
        f"expected {EXPECTED} staged tables, found {len(staged)}. If the "
        "directory has been emptied by an upload, re-run the batch's "
        "data/*.py scripts before rebuilding this file.")
    assert set(staged) == set(BLURB), \
        f"staged/described mismatch: {sorted(set(staged) ^ set(BLURB))}"

    rows = []
    for table in staged:
        blurb, (url, ref, doi) = BLURB[table]
        d = pd.read_csv(os.path.join(STAGED, f"{table}.csv"), low_memory=False)
        desc = (f"{blurb}. {len(d):,} responses from {d['id'].nunique():,} "
                f"respondents on {d['item'].nunique()} items.")
        row = [table, table.lower(), desc, url, ref, doi, CC_BY, "", "Public",
               CC_BY, "", "", "automated", DATE]
        row = [ascii_only(str(v)) for v in row]
        for v in row:
            assert not (set('"\t\r\n') & set(v)), f"bad char in field: {v!r}"
            assert not (v and v[0] in "=+-@'"), f"formula-injection risk: {v!r}"
        assert len(row) == len(COLUMNS)
        rows.append(row)

    with open(OUT, "w", newline="", encoding="ascii") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
    print(f"{OUT}: {len(rows)} rows x {len(COLUMNS)} columns")


if __name__ == "__main__":
    main()
