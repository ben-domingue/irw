"""Build the dictionary-sheet rows for the 2026-08-27 tier-A batch.

Writes a fully-quoted, LF-terminated, ASCII .csv for File > Import > Append
(comma) -- not a TSV and not a paste. See the biblio format notes: Sheets'
paste splits on commas ignoring quoting, and a TSV's three mandated blank
columns collapse under text-to-columns, shifting Contributor and Date three
columns left. Import honours both quoting and empty fields.

Per-table counts are hard-coded from the verified batch tally rather than read
from `irw_output/`, which ben-domingue empties on upload -- regenerating
against an empty directory silently yields a header-only file.
"""
import csv
import unicodedata

OUT = "biblio_tierA_2026-08-27.csv"
DATE = "8/27/2026"

COLUMNS = ["table", "table.lower", "Description", "URL (for data)", "Reference",
           "DOI (for paper)", "Original License", "Custom License",
           "Public Reshare?", "Derived License", "Custom License", "Notes",
           "Contributor", "Date"]

CC_BY = "CC BY 4.0"
CC0 = "CC0 1.0"

# (table, n_resp, n_ids, n_items, blurb, url, reference, doi, license)
ROWS = [
 ("onah_2021_covid_knowledge", 197250, 7890, 25,
  "COVID-19 preventive-measures knowledge items (true/false, scored 1/0) from a Nigerian health information literacy survey",
  "https://data.mendeley.com/datasets/cf3s3v8wb3",
  "Onah, U., Momohjimoh, A., & Okonkwo, E. (2021). Health information literacy of Nigerians on the preventive measures of COVID-19: A cross sectional survey data [Data set]. Mendeley Data. https://doi.org/10.17632/cf3s3v8wb3",
  "10.17632/cf3s3v8wb3", CC_BY),
 ("onah_2021_covid_info_sources", 78900, 7890, 10,
  "Binary endorsement of ten COVID-19 health information sources (WHO/NCDC websites, social media, television, radio, health worker, place of worship, etc.)",
  "https://data.mendeley.com/datasets/cf3s3v8wb3",
  "Onah, U., Momohjimoh, A., & Okonkwo, E. (2021). Health information literacy of Nigerians on the preventive measures of COVID-19: A cross sectional survey data [Data set]. Mendeley Data. https://doi.org/10.17632/cf3s3v8wb3",
  "10.17632/cf3s3v8wb3", CC_BY),
 ("floreskanter_2021_cerq", 247932, 6887, 36,
  "Cognitive Emotion Regulation Questionnaire (CERQ), 36 items on a 1-5 frequency scale, large Argentinean sample",
  "https://data.mendeley.com/datasets/48y8tkf5wh",
  "Flores Kanter, P. E., & Medrano, L. A. (2021). Data for internal structure of the Cognitive Emotion Regulation Questionnaire (CERQ): CFA and ESEM analysis in a large Argentinean sample [Data set]. Mendeley Data. https://doi.org/10.17632/48y8tkf5wh",
  "10.17632/48y8tkf5wh", CC_BY),
 ("emiral_2025_aips", 16767, 729, 23,
  "Artificial Intelligence in Psychotherapy Scale (AIPS), 23 items on a 1-5 agreement scale, Turkish sample",
  "https://zenodo.org/records/14901927",
  "Emiral, E. (2025). Attitudes towards artificial intelligence (AI) in psychotherapy: Artificial Intelligence in Psychotherapy Scale (AIPS). Clinical Psychologist, 29(2). https://doi.org/10.1080/13284207.2025.2515074",
  "10.1080/13284207.2025.2515074", CC_BY),
 ("kalczajanosi_2021_covid_fear", 21042, 1503, 14,
  "COVID-19 fear subscale (14 items, 1-5) of a three-dimensional COVID-19 vaccine hesitancy scale",
  "https://doi.org/10.6084/m9.figshare.15090891.v1",
  "Kalcza-Janosi, K., Kotta, I., & Marschalko, E. E. (2021). The development and validation of a three-dimensional COVID-19 vaccine hesitancy scale [Data set]. figshare. https://doi.org/10.6084/m9.figshare.15090891.v1",
  "10.6084/m9.figshare.15090891", CC_BY),
 ("kalczajanosi_2021_vaccine_skepticism", 16533, 1503, 11,
  "Vaccine skepticism subscale (11 items, 1-5) of a three-dimensional COVID-19 vaccine hesitancy scale",
  "https://doi.org/10.6084/m9.figshare.15090891.v1",
  "Kalcza-Janosi, K., Kotta, I., & Marschalko, E. E. (2021). The development and validation of a three-dimensional COVID-19 vaccine hesitancy scale [Data set]. figshare. https://doi.org/10.6084/m9.figshare.15090891.v1",
  "10.6084/m9.figshare.15090891", CC_BY),
 ("kalczajanosi_2021_covid_risk", 18036, 1503, 12,
  "COVID-19 risk perception subscale (12 items, 1-5) of a three-dimensional COVID-19 vaccine hesitancy scale",
  "https://doi.org/10.6084/m9.figshare.15090891.v1",
  "Kalcza-Janosi, K., Kotta, I., & Marschalko, E. E. (2021). The development and validation of a three-dimensional COVID-19 vaccine hesitancy scale [Data set]. figshare. https://doi.org/10.6084/m9.figshare.15090891.v1",
  "10.6084/m9.figshare.15090891", CC_BY),
 ("risticdedic_2025_dhq_importance", 24756, 834, 30,
  "Democratic Health Questionnaire, school version: 30 statements rated for importance on a 0-100 slider; id is the school",
  "https://zenodo.org/records/15341219",
  "Ristic Dedic, Z., Jokic, B., & Matic Bojic, J. (2025). Democratic Health Questionnaire (DHQ) dataset: School version [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15341219",
  "10.5281/zenodo.15341219", CC_BY),
 ("risticdedic_2025_dhq_currentstate", 24663, 834, 30,
  "Democratic Health Questionnaire, school version: the same 30 statements rated for how far they are currently realised, 0-100 slider; id is the school",
  "https://zenodo.org/records/15341219",
  "Ristic Dedic, Z., Jokic, B., & Matic Bojic, J. (2025). Democratic Health Questionnaire (DHQ) dataset: School version [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15341219",
  "10.5281/zenodo.15341219", CC_BY),
 ("risticdedic_2025_dhq_expectation", 24668, 834, 30,
  "Democratic Health Questionnaire, school version: the same 30 statements rated for expectation, 0-100 slider; id is the school",
  "https://zenodo.org/records/15341219",
  "Ristic Dedic, Z., Jokic, B., & Matic Bojic, J. (2025). Democratic Health Questionnaire (DHQ) dataset: School version [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15341219",
  "10.5281/zenodo.15341219", CC_BY),
 ("benchelbi_2021_mtq48", 40944, 853, 48,
  "Mental Toughness Questionnaire (MTQ48), Arabic version, 48 items on a 1-5 scale, 853 Tunisian athletes and non-athletes",
  "https://zenodo.org/records/6073642",
  "Ben Chelbi, I. E., Alem, J., Boudhiba, D., Hamrouni, S., & Gaied Chortane, S. (2021). Validation psychometrique de la version arabe de la mesure de la force mentale. Zenodo. https://doi.org/10.5281/zenodo.5390587",
  "10.5281/zenodo.5390587", CC_BY),
 ("huang_2023_medseq", 37818, 1719, 22,
  "Medicine Student Experience Questionnaire (MedSEQ), 22 items on a 1-5 agreement scale, medical students",
  "https://doi.org/10.7910/DVN/SQ8PJY",
  "Huang, P.-H., Velan, G., Smith, G., Fentoullis, M., Kennedy, S. E., Gibson, K. J., Uebel, K., & Shulruf, B. (2023). What impacts students' satisfaction the most from Medicine Student Experience Questionnaire [Data set]. Harvard Dataverse. https://doi.org/10.7910/DVN/SQ8PJY",
  "10.7910/dvn/sq8pjy", CC0),
 ("kumlander_2018_scs", 29639, 1710, 26,
  "Self-Compassion Scale (SCS), 26 items on a 1-5 scale, Finnish sample; first measurement wave only",
  "https://doi.org/10.6084/m9.figshare.7426262",
  "Kumlander, S., Lahtinen, O., Turunen, T., & Salmivalli, C. (2018). Two is more valid than one, but is six even better? The factor structure of the Self-Compassion Scale (SCS). PLOS ONE, 13(12), e0207706. https://doi.org/10.1371/journal.pone.0207706",
  "10.1371/journal.pone.0207706", CC_BY),
 ("kumlander_2018_bdi", 14791, 1703, 13,
  "Revised (Raitasalo) Beck Depression Inventory, 13 items on a 1-5 scale, Finnish sample; first measurement wave only",
  "https://doi.org/10.6084/m9.figshare.7426262",
  "Kumlander, S., Lahtinen, O., Turunen, T., & Salmivalli, C. (2018). Two is more valid than one, but is six even better? The factor structure of the Self-Compassion Scale (SCS). PLOS ONE, 13(12), e0207706. https://doi.org/10.1371/journal.pone.0207706",
  "10.1371/journal.pone.0207706", CC_BY),
 ("ilic_2019_whoqol_bref", 19580, 759, 26,
  "WHOQOL-BREF quality of life questionnaire, 26 items on a 1-5 scale, Serbian medical students",
  "https://zenodo.org/records/3404237",
  "Ilic, I. (2019). Psychometric properties of the World Health Organization's Quality of Life (WHOQOL-BREF) questionnaire [Data set]. Zenodo. https://doi.org/10.5281/zenodo.3404237",
  "10.5281/zenodo.3404237", CC_BY),
 ("livacicrojas_2023_lvq", 14421, 759, 19,
  "Leadership Virtues Questionnaire (LVQ), 19 items on a 1-5 scale",
  "https://doi.org/10.7910/DVN/AEX8PP",
  "Livacic-Rojas, P. (2023). Replication data for: Data base of validation and analysis of the metric properties of the Leadership Virtues Questionnaire [Data set]. Harvard Dataverse. https://doi.org/10.7910/DVN/AEX8PP",
  "10.7910/dvn/aex8pp", CC0),
 ("woodall_2020_bfi44", 11924, 271, 44,
  "Big Five Inventory (BFI-44), 44 items on a 1-5 agreement scale; the 16 reverse-keyed items are supplied already reverse-scored and keep an RRRRR suffix",
  "https://zenodo.org/records/3695861",
  "Woodall, T. (2020). BFI inventory scores [Data set]. Zenodo. https://doi.org/10.5281/zenodo.3695861",
  "10.5281/zenodo.3695861", CC_BY),
 ("rodriguezsantero_2024_sats36", 11421, 318, 36,
  "Survey of Attitudes Toward Statistics (SATS-36), 36 items on a 1-7 scale, Spanish education-sciences students",
  "https://zenodo.org/records/10546410",
  "Rodriguez-Santero, J., & Gil-Flores, J. (2024). Instrument and database used in the article: Attitudes towards statistics of education sciences students [Data set]. Zenodo. https://doi.org/10.5281/zenodo.10546410",
  "10.5281/zenodo.10546410", CC_BY),
 ("atik_2026_climate_anxiety", 11148, 929, 12,
  "Climate anxiety scale, 12 items on a 1-5 scale; two Turkish samples (EFA n=606, CFA n=323) pooled with cov_sample",
  "https://zenodo.org/records/18601426",
  "Atik, S. (2026). Climate Anxiety and Psychological Resilience Scale [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18601426",
  "10.5281/zenodo.18601426", CC_BY),
 ("atik_2026_psych_resilience", 11148, 929, 12,
  "Psychological resilience scale, 12 items on a 1-5 scale; two Turkish samples (EFA n=606, CFA n=323) pooled with cov_sample",
  "https://zenodo.org/records/18601426",
  "Atik, S. (2026). Climate Anxiety and Psychological Resilience Scale [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18601426",
  "10.5281/zenodo.18601426", CC_BY),
 ("daderman_2023_wis", 2982, 426, 7,
  "Workplace Incivility Scale (WIS), Swedish version, 7 items on a 0-4 frequency scale where 0 is never",
  "https://data.mendeley.com/datasets/j95y99fzb9",
  "Daderman, A. M., & Cider, A. (2023). Workplace Incivility Scale Swedish version N426 [Data set]. Mendeley Data. https://doi.org/10.17632/j95y99fzb9",
  "10.17632/j95y99fzb9", CC_BY),
 ("daderman_2023_naq_r", 6688, 304, 22,
  "Negative Acts Questionnaire-Revised (NAQ-R), 22 items on a 1-5 frequency scale, Swedish sample",
  "https://data.mendeley.com/datasets/j95y99fzb9",
  "Daderman, A. M., & Cider, A. (2023). Workplace Incivility Scale Swedish version N426 [Data set]. Mendeley Data. https://doi.org/10.17632/j95y99fzb9",
  "10.17632/j95y99fzb9", CC_BY),
 ("hahn_2025_sqc", 3910, 230, 17,
  "Stress Questionnaire for Children and Adolescents (SQC), 17 items on a 0-3 scale; item numbering is non-contiguous, as in the source",
  "https://zenodo.org/records/17159652",
  "Hahn, A., & Winkler, A. (2025). Stress in children and adolescents: Development and validation of a new questionnaire [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17159652",
  "10.5281/zenodo.17159652", CC_BY),
 ("alqerem_2024_diabetic_health_literacy", 2800, 400, 7,
  "Jordanian Diabetic Health Literacy Questionnaire, 7 items on a 1-5 scale",
  "https://zenodo.org/records/10812303",
  "Al-Qerem, W. (2024). Jordanian Diabetic Health Literacy Questionnaire [Data set]. Zenodo. https://doi.org/10.5281/zenodo.10812303",
  "10.5281/zenodo.10812303", CC_BY),
]

TRANSLATE = {"‘": "'", "’": "'", "“": '"', "”": '"',
             "–": "-", "—": "-", "…": "...", " ": " ",
             "®": "(R)", "™": "(TM)", "´": "'"}


def ascii_only(value):
    for bad, good in TRANSLATE.items():
        value = value.replace(bad, good)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    assert all(ord(c) < 128 for c in value), \
        f"non-ASCII survived: {[c for c in value if ord(c) > 127]!r}"
    return value


def main():
    out_rows = []
    for (table, n_resp, n_ids, n_items, blurb, url, ref, doi, lic) in ROWS:
        desc = (f"{blurb}. {n_resp:,} responses from {n_ids:,} respondents "
                f"on {n_items} items.")
        row = [table, table.lower(), desc, url, ref, doi, lic, "", "Public",
               lic, "", "", "automated", DATE]
        row = [ascii_only(str(v)) for v in row]
        for v in row:
            assert "\n" not in v and "\r" not in v, f"newline in field: {v!r}"
            assert not (v and v[0] in "=+-@"), f"formula-injection risk: {v!r}"
        assert len(row) == len(COLUMNS)
        out_rows.append(row)

    assert len(out_rows) == 24, f"expected 24 tables, built {len(out_rows)}"
    assert len({r[0] for r in out_rows}) == 24, "duplicate table names"

    with open(OUT, "w", newline="", encoding="ascii") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(out_rows)
    print(f"{OUT}: {len(out_rows)} rows x {len(COLUMNS)} columns")


if __name__ == "__main__":
    main()
