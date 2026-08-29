"""Dictionary-sheet rows for the Zenodo backlog-sweep batch (24 tables).

Fully-quoted, LF-terminated, ASCII .csv for File > Import > Append (comma).

Counts are read from the staged `irw_output/*.csv`, guarded by an assert on the
expected table count -- so running this after an upload has emptied the
directory fails loudly rather than writing a header-only file.
"""
import csv
import os
import unicodedata

import pandas as pd

OUT = "biblio_zenodo_backlog_2026-08-29.csv"
STAGED = "irw_output"
DATE = "8/29/2026"
EXPECTED = 24

COLUMNS = ["table", "table.lower", "Description", "URL (for data)", "Reference",
           "DOI (for paper)", "Original License", "Custom License",
           "Public Reshare?", "Derived License", "Custom License", "Notes",
           "Contributor", "Date"]

CC_BY = "CC BY 4.0"

OSO = ("https://zenodo.org/records/8300667",
       "Osorio, A. (2023). Dataset for the article \"Differentiation of Self in "
       "Adolescents: Measurement Invariance Analysis across six "
       "Spanish-Speaking Countries\" [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.8300667",
       "10.5281/zenodo.8300667")
SIL = ("https://zenodo.org/records/6557048",
       "Silva, S. M., Silva, A. M., Faria, S., & Nata, G. (2022). Development "
       "and validation of a Community Resilience Scale for Youth (CRS-Y) "
       "[Data set]. Zenodo. https://doi.org/10.5281/zenodo.6557048",
       "10.5281/zenodo.6557048")
YE = ("https://zenodo.org/records/18092016",
      "Ye, L. (2025). Raw data: Imposter Phenomenon and Social Anxiety among "
      "College Students -- The Chain Mediating Roles of Self-Compassion and "
      "Shame [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18092016",
      "10.5281/zenodo.18092016")
SKA = ("https://zenodo.org/records/21134839",
       "Skarzauskiene, A., Maciuliene, M., & Guleviciute, G. (2026). "
       "INFODEMIJA: Survey of Lithuanian Residents on Science Communication, "
       "Trust in Science, and Misinformation (2024) [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.21134839",
       "10.5281/zenodo.21134839")
HER = ("https://zenodo.org/records/13997042",
       "Hernandez Mantilla, G. E., Sancerni Beitia, M. D., & Cortes Tomas, "
       "M. T. (2024). Data base: Influence of Gender on Binge Drinking among "
       "Female Ecuadorian Undergraduates -- Masculine and Feminine Norms "
       "[Data set]. Zenodo. https://doi.org/10.5281/zenodo.13997042",
       "10.5281/zenodo.13997042")
LAP = ("https://zenodo.org/records/19473011",
       "Lapietra, I., Mele, D., & Dellino, P. (2026). Variables and indicators "
       "of volcanic risk perception in the Vesuvius area [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.19473011",
       "10.5281/zenodo.19473011")
BAE = ("https://zenodo.org/records/7742956",
       "Baekgaard, M., & Madsen, J. K. (2023). Replication data and R script "
       "for \"Anticipated administrative burdens: How proximity to upcoming "
       "compulsory meetings affect welfare recipients' experiences\" "
       "[Data set]. Zenodo. https://doi.org/10.5281/zenodo.7742956",
       "10.5281/zenodo.7742956")

SKA_S = "Lithuanian residents, general-population survey"
BAE_S = "Danish welfare recipients facing compulsory meetings"

BLURB = {
 "osorio_2023_dos": ("Differentiation of Self, 21 items on a 0-5 scale, adolescents aged 12-19 in six Spanish-speaking countries", OSO),
 "silva_2022_crsy": ("Community Resilience Scale for Youth, all 16 administered items on a 1-5 scale, young people in four Portuguese regions; itemcov_retained marks the 12 items the published scale kept, and items are numbered by their original questionnaire position", SIL),
 "ye_2025_mm": ("20 items on a 1-5 agreement scale, Chinese college students; the source labels the block only as MM and ships no codebook, so the code is kept verbatim rather than named", YE),
 "ye_2025_tq": ("12 items on a 1-5 agreement scale, Chinese college students; the source labels the block only as TQ and ships no codebook, so the code is kept verbatim rather than named", YE),
 "ye_2025_xc": ("25 items on a 1-4 scale, Chinese college students; the source labels the block only as XC and ships no codebook, so the code is kept verbatim rather than named", YE),
 "ye_2025_jl": ("13 items on a 1-5 scale, Chinese college students; the source labels the block only as JL and ships no codebook, so the code is kept verbatim rather than named", YE),
 "skarzauskiene_2026_big_five": (f"Big Five personality items, 14 items on a 1-5 agreement scale, {SKA_S}", SKA),
 "skarzauskiene_2026_attitudes_science": (f"Attitudes toward science and technology, 11 items on a 1-5 agreement scale, {SKA_S}", SKA),
 "skarzauskiene_2026_information_sources": (f"Frequency of use of information sources, 10 items on a 1-5 frequency scale, {SKA_S}", SKA),
 "skarzauskiene_2026_trust_science": (f"Trust in science and institutions, 8 items on a 1-5 agreement scale, {SKA_S}", SKA),
 "skarzauskiene_2026_fake_news_agree": (f"Perceptions of fake news, 6 items on a 1-5 agreement scale, {SKA_S}", SKA),
 "skarzauskiene_2026_social_trust": (f"Social trust, 5 items on a 1-5 agreement scale, {SKA_S}", SKA),
 "skarzauskiene_2026_science_engagement": (f"Engagement with and interest in science, 4 items on a 1-5 scale, {SKA_S}", SKA),
 "skarzauskiene_2026_science_behaviors": (f"Science-related behaviours and participation, 4 items on a 1-5 frequency scale, {SKA_S}", SKA),
 "skarzauskiene_2026_fake_news_frequency": (f"Fake-news-related behaviours, 4 items on a 1-5 frequency scale, {SKA_S}", SKA),
 "hernandezmantilla_2024_cmni": ("Conformity to Masculine Norms Inventory, 97 item labels on a 0-3 scale, female Ecuadorian undergraduates; items 21, 35 and 46 appear as separate Hombre_/Mujer_ wordings because they were administered in two gendered forms", HER),
 "hernandezmantilla_2024_cfni": ("Conformity to Feminine Norms Inventory (CFNI-84), 84 items on a 0-3 scale, female Ecuadorian undergraduates", HER),
 "lapietra_2026_volcanic_risk_perception": ("Volcanic risk perception, 15 items on a 1-5 ordinal scale, residents of 43 municipalities in the Vesuvius area; the person key is the (sample, record) pair", LAP),
 "baekgaard_2023_mastery": (f"Mastery, 7 items on a 0-4 scale, {BAE_S}; the item block was recovered from the file's mastery_add composite, which is their exact mean", BAE),
 "baekgaard_2023_stress": (f"Stress of the upcoming meeting, 4 items on a 0-4 scale, {BAE_S}; the item block was recovered from the file's stress_add composite, which is their exact mean", BAE),
 "baekgaard_2023_autonomy_loss": (f"Loss of autonomy, 4 items on a 0-4 scale, {BAE_S}; the item block was recovered from the file's autonomyloss_add composite, which is their exact mean", BAE),
 "baekgaard_2023_stigma": (f"Stigma, 4 items on a 0-4 scale, {BAE_S}; the item block was recovered from the file's stigma_add composite, which is their exact mean", BAE),
 "baekgaard_2023_learning": (f"Learning, 3 items on a 0-4 scale, {BAE_S}; the item block was recovered from the file's learning_add composite, which is their exact mean", BAE),
 "baekgaard_2023_compliance": (f"Compliance, 3 items on a 0-4 scale, {BAE_S}; the item block was recovered from the file's compliance_add composite, which is their exact mean", BAE),
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
