"""Build the dictionary-sheet rows for the 2026-08-27 tier-B batch.

Fully-quoted, LF-terminated, ASCII .csv for File > Import > Append (comma).

Counts are read from the staged `irw_output/*.csv` -- which only works while
they are still on disk. The expected table count is asserted first, so running
this after an upload has emptied the directory fails loudly instead of writing
a header-only file.
"""
import csv
import os
import unicodedata

import pandas as pd

OUT = "biblio_tierB_2026-08-27.csv"
STAGED = "irw_output"
DATE = "8/27/2026"
EXPECTED = 22

COLUMNS = ["table", "table.lower", "Description", "URL (for data)", "Reference",
           "DOI (for paper)", "Original License", "Custom License",
           "Public Reshare?", "Derived License", "Custom License", "Notes",
           "Contributor", "Date"]

CC_BY = "CC BY 4.0"
CC0 = "CC0 1.0"

TU = ("https://zenodo.org/records/7219876",
      "Tu, S., & Xiao, Q. (2022). Measurement of achievement motivation for "
      "college students [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7219876",
      "10.5281/zenodo.7219876", CC_BY)
WICH = ("https://doi.org/10.34894/8NGA0R",
        "Wicherts, J. M. (2023). Data from 'Cohort Differences in Big Five "
        "Personality Factors Over a Period of 25 Years' [Data set]. DataverseNL. "
        "https://doi.org/10.34894/8NGA0R",
        "10.34894/8nga0r", CC0)
PRIH = ("https://zenodo.org/records/22104768",
        "Prihastiwi, W. J., & Antawati, D. (2026). Supporting dataset and "
        "supplementary materials for the Adaptive Capital Scale (AdCap) "
        "[Data set]. Zenodo. https://doi.org/10.5281/zenodo.22104768",
        "10.5281/zenodo.22104768", CC_BY)
NURJ = ("https://data.mendeley.com/datasets/zr54c7rxs3",
        "Nurjanah, & Rachmani, E. (2019). Data for: Using the feature selection "
        "with genetic algorithm to abbreviate Indonesia's health literacy "
        "questionnaire [Data set]. Mendeley Data. "
        "https://doi.org/10.17632/zr54c7rxs3",
        "10.17632/zr54c7rxs3", CC_BY)
BARS = ("https://zenodo.org/records/15160903",
        "Matosas-Lopez, L. (2022). Datasets on student evaluations of a BARS "
        "questionnaire designed for blended-learning and face-to-face teaching "
        "[Data sets]. Zenodo. https://doi.org/10.5281/zenodo.15160903 and "
        "https://doi.org/10.5281/zenodo.15151307",
        "10.5281/zenodo.15160903", CC_BY)
MAT24 = ("https://zenodo.org/records/15151243",
         "Matosas-Lopez, L. (2024). Dataset on the evaluation of teaching "
         "efficiency comparing Likert-type questionnaires vs BARS [Data set]. "
         "Zenodo. https://doi.org/10.5281/zenodo.15151243",
         "10.5281/zenodo.15151243", CC_BY)
WU = ("https://doi.org/10.6084/m9.figshare.30236404",
      "Wu, J., & Chen, Z. (2025). Anonymized participant background information "
      "and questionnaire scale scores [Data set]. figshare. Supporting PLOS ONE "
      "20(9), e0333422. https://doi.org/10.1371/journal.pone.0333422",
      "10.1371/journal.pone.0333422", CC_BY)
HUANG = ("https://doi.org/10.6084/m9.figshare.24811462",
         "Huang, T. (2023). Research questionnaire data [Data set]. figshare. "
         "Supporting PLOS ONE 18(12), e0295581. "
         "https://doi.org/10.1371/journal.pone.0295581",
         "10.1371/journal.pone.0295581", CC_BY)
APAZA = ("https://zenodo.org/records/22117910",
         "Apaza Arapa, M. A., & Turpo Chaparro, J. E. (2026). Study data: "
         "Psychometric properties of the Multigroup Ethnic Identity "
         "Measure-Revised [Data set]. Zenodo. "
         "https://doi.org/10.5281/zenodo.22117910",
         "10.5281/zenodo.22117910", CC_BY)
KOT = ("https://doi.org/10.6084/m9.figshare.3122734",
       "Kotsou, I. (2016). SCSdata: Validation of the French version of the "
       "Self-Compassion Scale [Data set]. figshare. "
       "https://doi.org/10.6084/m9.figshare.3122734",
       "10.6084/m9.figshare.3122734", CC_BY)
ANT = ("https://zenodo.org/records/18681288",
       "Antunez Vilchez, J. M., & Adan, A. (2013). Circadian typology and "
       "emotional intelligence in healthy adults [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.18681288",
       "10.5281/zenodo.18681288", CC_BY)
SEK = ("https://doi.org/10.7910/DVN/HXI9SZ",
       "Sekowski, M. (2025). Dataset for: A 12-item version of the "
       "Multi-Attitude Suicide Tendency Scale [Data set]. Harvard Dataverse. "
       "https://doi.org/10.7910/DVN/HXI9SZ",
       "10.7910/dvn/hxi9sz", CC0)

BLURB = {
 "tu_2022_achievement_motivation": ("Achievement Motivation Scale, 30 items on a 1-4 scale, Chinese college students", TU),
 "wicherts_2023_5pft": ("Five Personality Factors Test (5PFT), 70 items on a 1-7 scale (14 per Big Five factor), Dutch cohorts 1982-2007", WICH),
 "prihastiwi_2026_adcap": ("Adaptive Capital Scale (AdCap), 60 items on a 1-4 scale across five aspects, Indonesian sample; itemcov_aspect carries the aspect", PRIH),
 "nurjanah_2019_hls47": ("Indonesian Health Literacy Survey (HLS-EU-Q47), 47 items on a 1-4 difficulty scale", NURJ),
 "matosaslopez_2022_bars_teaching": ("Student evaluation of teaching on a 10-item behaviourally-anchored rating scale, 1-5; two deposits pooled with cov_teaching_mode (blended vs face-to-face)", BARS),
 "matosaslopez_2024_teacher_assessment": ("Ten items rating the teacher, 1-5; cov_questionnaire_type records the study's Likert vs BARS comparison", MAT24),
 "matosaslopez_2024_questionnaire_quality": ("Three items rating the questionnaire itself (ambiguity, clarity, precision), 1-5", MAT24),
 "wu_2025_drone_delivery": ("Environmental concern and drone-delivery acceptance, 38 items on a 1-5 agreement scale; itemcov_construct carries the construct", WU),
 "huang_2023_utaut_mobile_shopping": ("UTAUT2 mobile-shopping questionnaire, 37 items on a 1-7 scale; itemcov_construct carries the UTAUT2 construct", HUANG),
 "apaza_2026_meim_r": ("Multigroup Ethnic Identity Measure-Revised, 6 items on a 1-5 scale, Peruvian students", APAZA),
 "apaza_2026_self_esteem": ("Self-esteem scale, 10 items on a 1-4 scale, Peruvian students", APAZA),
 "apaza_2026_sdo": ("Social Dominance Orientation, 14 items on a 1-7 scale, Peruvian students", APAZA),
 "kotsou_2016_scs": ("Self-Compassion Scale, French version, 26 items on a 1-5 scale", KOT),
 "kotsou_2016_panas": ("PANAS, 20 items on a 1-5 scale (stored in the source as the strings A1-A5)", KOT),
 "kotsou_2016_plc": ("15-item scale on a 1-6 scale, administered alongside the French SCS validation", KOT),
 "kotsou_2016_bdi": ("Beck Depression Inventory, 13 items on a 0-3 scale", KOT),
 "kotsou_2016_life_satisfaction": ("Life satisfaction, 5 items on a 1-7 scale", KOT),
 "kotsou_2016_happiness": ("Subjective happiness, 4 items on a 1-7 scale", KOT),
 "antunez_2013_tmms24": ("Trait Meta-Mood Scale (TMMS-24), 24 items on a 1-5 scale, Spanish adults", ANT),
 "antunez_2013_rmeq": ("Reduced Morningness-Eveningness Questionnaire, 5 items; the items use different response formats (1-4, 1-5, 0-6), as the published instrument does", ANT),
 "sekowski_2025_mast": ("Multi-Attitude Suicide Tendency Scale, 30 items on a 1-5 scale, Polish sample", SEK),
 "sekowski_2025_pies": ("PIES, 24 items on a 1-5 scale, Polish sample", SEK),
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
        "directory has been emptied by an upload, re-run the batch's data/*.py "
        "scripts before rebuilding this file.")
    assert set(staged) == set(BLURB), \
        f"staged/described mismatch: {set(staged) ^ set(BLURB)}"

    rows = []
    for table in staged:
        blurb, (url, ref, doi, lic) = BLURB[table]
        d = pd.read_csv(os.path.join(STAGED, f"{table}.csv"), low_memory=False)
        desc = (f"{blurb}. {len(d):,} responses from {d['id'].nunique():,} "
                f"respondents on {d['item'].nunique()} items.")
        row = [table, table.lower(), desc, url, ref, doi, lic, "", "Public",
               lic, "", "", "automated", DATE]
        row = [ascii_only(str(v)) for v in row]
        for v in row:
            assert "\n" not in v and "\r" not in v, f"newline in field: {v!r}"
            assert not (v and v[0] in "=+-@"), f"formula-injection risk: {v!r}"
        assert len(row) == len(COLUMNS)
        rows.append(row)

    with open(OUT, "w", newline="", encoding="ascii") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
    print(f"{OUT}: {len(rows)} rows x {len(COLUMNS)} columns")


if __name__ == "__main__":
    main()
