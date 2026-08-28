"""Dictionary-sheet rows for the 2026-08-28 Zenodo re-run batch (15 tables).

Fully-quoted, LF-terminated, ASCII .csv for File > Import > Append (comma).

Counts are read from the staged `irw_output/*.csv`, guarded by an assert on the
expected table count -- so running this after an upload has emptied the
directory fails loudly rather than writing a header-only file.
"""
import csv
import os
import unicodedata

import pandas as pd

OUT = "biblio_zenodo_2026-08-28.csv"
STAGED = "irw_output"
DATE = "8/28/2026"
EXPECTED = 15

COLUMNS = ["table", "table.lower", "Description", "URL (for data)", "Reference",
           "DOI (for paper)", "Original License", "Custom License",
           "Public Reshare?", "Derived License", "Custom License", "Notes",
           "Contributor", "Date"]

CC_BY = "CC BY 4.0"

ALK = ("https://zenodo.org/records/7852343",
       "Alkhaldi, S. (2023). Data set Quality of Life Autism [Data set]. "
       "Zenodo. https://doi.org/10.5281/zenodo.7852343",
       "10.5281/zenodo.7852343")
CHA = ("https://zenodo.org/records/5646614",
       "Chatzoudes, D., & Theriou, G. (2021). The effect of ethical leadership "
       "on organizational outcomes in the hospitality industry [Data set]. "
       "Zenodo. https://doi.org/10.5281/zenodo.5646614",
       "10.5281/zenodo.5646614")
LI = ("https://zenodo.org/records/21445573",
      "Li, J. (2026). Coach leadership behavior and team cohesion among "
      "adolescent handball players [Data set]. Zenodo. "
      "https://doi.org/10.5281/zenodo.21445573",
      "10.5281/zenodo.21445573")
TUR = ("https://zenodo.org/records/20516198",
       "Turpo Chaparro, J. E. (2026). Dataset on self-esteem, family "
       "communication, and social network addiction among Peruvian university "
       "students [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20516198",
       "10.5281/zenodo.20516198")
WU = ("https://zenodo.org/records/11095879",
      "Wu, Y. (2024). Chinese secondary EFL learners' achievement emotions "
      "[Data set]. Zenodo. https://doi.org/10.5281/zenodo.11095879",
      "10.5281/zenodo.11095879")
YSL = ("https://zenodo.org/records/8374494",
       "Yslado-Mendez, R. M., Sanchez-Broncano, J., & De la Cruz-Valdiviano, C. "
       "(2023). Psychometric properties of the Maslach Burnout Inventory in "
       "healthcare professionals, Ancash [Data set]. Zenodo. "
       "https://doi.org/10.5281/zenodo.8374494",
       "10.5281/zenodo.8374494")

BLURB = {
 "alkhaldi_2023_whoqol_autism": ("WHOQOL-BREF quality of life, 26 items on a 1-5 scale, respondents in an autism quality-of-life study; itemcov_domain carries the WHOQOL domain", ALK),
 "chatzoudes_2021_ethical_leadership": ("Ethical leadership, 9 items on a 1-5 agreement scale, hospitality employees in Greece", CHA),
 "chatzoudes_2021_service_delivery": ("Service delivery, 8 items on a 1-5 agreement scale, hospitality employees", CHA),
 "chatzoudes_2021_job_satisfaction": ("Job satisfaction, 5 items on a 1-5 agreement scale, hospitality employees", CHA),
 "chatzoudes_2021_emotional_exhaustion": ("Emotional exhaustion, 4 items on a 1-5 agreement scale, hospitality employees", CHA),
 "chatzoudes_2021_turnover_intention": ("Turnover intention, 3 items on a 1-5 agreement scale, hospitality employees", CHA),
 "chatzoudes_2021_trust": ("Trust in the supervisor, 3 items on a 1-5 agreement scale, hospitality employees", CHA),
 "li_2026_coach_leadership": ("Coach leadership behaviour, 25 items on a 1-5 scale, adolescent handball players; item codes are the source's Chinese labels", LI),
 "li_2026_sport_commitment": ("Sport commitment, 20 items on a 1-5 scale, adolescent handball players; item codes are the source's Chinese labels", LI),
 "li_2026_team_cohesion": ("Team cohesion, 18 items on a 1-5 scale, adolescent handball players; item codes are the source's Chinese labels", LI),
 "turpochaparro_2026_social_network_addiction": ("Social network addiction, 24 items on a 0-4 scale, Peruvian university students", TUR),
 "turpochaparro_2026_self_esteem": ("Self-esteem, 10 items on a 1-4 scale, Peruvian university students", TUR),
 "turpochaparro_2026_family_communication": ("Family communication, 10 items on a 1-5 scale, Peruvian university students", TUR),
 "wu_2024_achievement_emotions": ("Achievement emotions, 19 items on a 1-5 scale, Chinese secondary EFL learners; itemcov_subscale carries the emotion subscale group", WU),
 "ysladomendez_2023_mbi": ("Maslach Burnout Inventory, 22 items on the instrument's 0-6 frequency scale, Peruvian healthcare professionals", YSL),
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
