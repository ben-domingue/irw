"""Dictionary-sheet rows for the 2026-09-01 PLOS weekly batch (21 tables).

Fully-quoted, LF-terminated, ASCII .csv for File > Import > Append (comma).

Counts are read from the staged `irw_output/*.csv`. The directory can hold
other batches' staged tables, so the guard is on this batch's own table list
rather than on the directory count -- every table named below must be present.
"""
import csv
import os
import unicodedata

import pandas as pd

OUT = "biblio_2026-09-01.csv"
STAGED = "irw_output"
DATE = "9/1/2026"
CC_BY = "CC BY 4.0"

COLUMNS = ["table", "table.lower", "Description", "URL (for data)", "Reference",
           "DOI (for paper)", "Original License", "Custom License",
           "Public Reshare?", "Derived License", "Custom License", "Notes",
           "Contributor", "Date"]


def plos(doi, ref):
    return (f"https://journals.plos.org/plosone/article?id={doi}", ref, doi)


WANG = plos(
    "10.1371/journal.pone.0297517",
    "Wang, Y.; Sun, P. P. (2024). Development and validation of scales for "
    "speaking self-efficacy: Constructs, sources, and relations. PLOS ONE, "
    "19(1), e0297517. https://doi.org/10.1371/journal.pone.0297517")
XUE = plos(
    "10.1371/journal.pone.0338956",
    "Xue, C.; Helian, Z.; Li, Y. (2025). Academic pressure and academic "
    "procrastination: The mediating role of negative coping strategies. PLOS "
    "ONE, 20(12), e0338956. https://doi.org/10.1371/journal.pone.0338956")
ZHOU16 = plos(
    "10.1371/journal.pone.0157013",
    "Zhou, J.; Yang, Y.; Qiu, X.; Yang, X.; Pan, H.; Ban, B.; Qiao, Z.; Wang, "
    "L.; Wang, W. (2016). Relationship between Anxiety and Burnout among "
    "Chinese Physicians: A Moderated Mediation Model. PLOS ONE, 11(8), "
    "e0157013. https://doi.org/10.1371/journal.pone.0157013")
TEO = plos(
    "10.1371/journal.pone.0244338",
    "Teo, Y. H.; Xu, J. T. K.; Ho, C.; Leong, J. M.; Tan, B. K. J.; Tan, E. K. "
    "H.; Goh, W.; Neo, E.; Chua, J. Y. J.; Ng, S. J. Y.; Cheong, J. J. Y.; "
    "Hwang, J. Y.; Lim, S. M.; Soo, T.; Sng, J. G. K.; Yi, S. (2021). Factors "
    "associated with self-reported burnout level in allied healthcare "
    "professionals in a tertiary hospital in Singapore. PLOS ONE, 16(1), "
    "e0244338. https://doi.org/10.1371/journal.pone.0244338")
SMIRNOV = plos(
    "10.1371/journal.pone.0330679",
    "Smirnov, N.; Tarasova, E. (2025). Motivation matters: How enrollment "
    "motives shape doctoral experiences and career aspirations. PLOS ONE, "
    "20(9), e0330679. https://doi.org/10.1371/journal.pone.0330679")
SHAO = plos(
    "10.1371/journal.pone.0320839",
    "Shao, Y.; Jiang, W.; Wang, N.; Zhang, C.; Zhang, L. (2025). The impact of "
    "authentic leadership on the work engagement of primary and secondary "
    "school teachers: The serial mediation role of school climate and teacher "
    "efficacy. PLOS ONE, 20(5), e0320839. "
    "https://doi.org/10.1371/journal.pone.0320839")
ZHOU25 = plos(
    "10.1371/journal.pone.0320845",
    "Zhou, X.; Zhang, M.; Chen, L.; Li, B.; Xu, J. (2025). The effect of peer "
    "relationships on college students' behavioral intentions to be physically "
    "active: The chain-mediated role of social support and exercise "
    "self-efficacy. PLOS ONE, 20(5), e0320845. "
    "https://doi.org/10.1371/journal.pone.0320845")
KOHLMANN = plos(
    "10.1371/journal.pone.0156167",
    "Kohlmann, S.; Gierk, B.; Murray, A. M.; Scholl, A.; Lehmann, M.; Lowe, B. "
    "(2016). Base Rates of Depressive Symptoms in Patients with Coronary Heart "
    "Disease: An Individual Symptom Analysis. PLOS ONE, 11(5), e0156167. "
    "https://doi.org/10.1371/journal.pone.0156167")

S_WANG = ("Chinese non-English-major undergraduates, pooling the scale's EFA "
          "and CFA validation samples with cov_study marking which")
S_XUE = "Chinese university students across five institutions in Hebei Province"
S_ZHOU16 = ("physicians at two tertiary grade-A hospitals in Heilongjiang "
            "Province, China")
S_TEO = ("allied health professionals at a Singapore tertiary hospital, "
         "surveyed 2019")
S_SHAO = ("primary, secondary and high school teachers in a district of "
          "Shandong Province, China")
S_ZHOU25 = "Chinese college students"

BLURB = {
 "wang_2024_speaking_self_efficacy": (f"EFL Speaking Self-Efficacy Scale (EFL-SSES), 15 items on a 7-point agreement scale covering linguistic, self-regulatory, delivery and performance self-efficacy, {S_WANG}", WANG),
 "wang_2024_self_efficacy_sources": (f"EFL Sources of Speaking Self-Efficacy Scale (EFL-SSSES), 13 items on a 7-point agreement scale covering mastery experience, vicarious experience, social persuasion and physiological/emotional states, {S_WANG}", WANG),
 "xue_2025_academic_procrastination": (f"Zhao's College Students' Academic Procrastination Questionnaire, 19 items on a 1-5 agreement scale, {S_XUE}", XUE),
 "xue_2025_academic_stress": (f"Liu's College Students' Academic Stress Scale, 20 items on a 1-5 agreement scale, {S_XUE}", XUE),
 "xue_2025_coping_style": (f"Xie's Simplified Coping Style Questionnaire, 20 items on the instrument's own four-point frequency scale, {S_XUE}", XUE),
 "zhou_2016_burnout": (f"Chinese Maslach Burnout Inventory (15-item revision), scored 1 (never) to 7 (every day), {S_ZHOU16}", ZHOU16),
 "zhou_2016_coping_style": (f"Trait Coping Style Questionnaire, 20 items scored 1 (certainly not) to 5 (certainly), {S_ZHOU16}", ZHOU16),
 "zhou_2016_personality": (f"Eysenck Personality Questionnaire-Revised Short Scale for Chinese (EPQ-RSC), 48 forced-choice items scored 0/1, {S_ZHOU16}", ZHOU16),
 "zhou_2016_anxiety": (f"Zung Self-Rating Anxiety Scale, 20 items scored 1 (never or rarely) to 4 (most of the time), {S_ZHOU16}", ZHOU16),
 "teo_2021_burnout": (f"Maslach Burnout Inventory-Human Services Survey for Medical Personnel, 22 items scored 0 (never) to 6 (every day), {S_TEO}", TEO),
 "teo_2021_worklife": (f"Areas of Worklife Survey, 28 items scored 1 (strongly disagree) to 5 (strongly agree) across workload, control, reward, community, fairness and values, {S_TEO}", TEO),
 "shao_2025_authentic_leadership": (f"Authentic Leadership Questionnaire as adapted for schools, 14 items on a 1-5 agreement scale, {S_SHAO}", SHAO),
 "shao_2025_school_climate": (f"School climate scale covering cooperation and school resources, 10 items on a 1-5 agreement scale, {S_SHAO}", SHAO),
 "shao_2025_teacher_efficacy": (f"Teacher Sense of Efficacy Scale short form, 12 items scored 1 (none at all) to 9 (a great deal), {S_SHAO}", SHAO),
 "shao_2025_work_engagement": (f"UWES-9 work engagement scale, 9 items stored on the deposit's 1-7 coding of the instrument's seven frequency points, {S_SHAO}", SHAO),
 "zhou_2025_peer_relationship": (f"Wei Yunhua's Peer Relationship Scale, 20 items on a 1-5 agreement scale, {S_ZHOU25}", ZHOU25),
 "zhou_2025_social_support": (f"Ye and Dai's Social Support Rating Scale, 17 items on a 1-5 agreement scale covering subjective support, objective support and support utilisation, {S_ZHOU25}", ZHOU25),
 "zhou_2025_exercise_self_efficacy": (f"Chinese version of Motl et al.'s Exercise Self-Efficacy Scale, 8 items on a 1-5 agreement scale, {S_ZHOU25}", ZHOU25),
 "zhou_2025_pa_intention": (f"Physical activity behavioural intention subscale of the Physical Activity Rating Scale, 8 items on a 1-5 agreement scale, {S_ZHOU25}", ZHOU25),
 "smirnov_2025_enrollment_motives": ("Eleven enrollment motives for doctoral study, dummy coded 1 = selected / 0 = not selected; they are the options of one multiple-choice question, which the source itself analyses as eleven binary indicators via latent class analysis. Russian doctoral students from a nationwide survey", SMIRNOV),
 "kohlmann_2016_phq9": ("PHQ-9 depressive symptoms over the past two weeks, 9 items scored 0 (not at all) to 3 (nearly every day), patients with clinically confirmed coronary heart disease recruited consecutively at three cardiology sites in Hamburg, Germany", KOHLMANN),
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
    rows = []
    for table in sorted(BLURB):
        path = os.path.join(STAGED, f"{table}.csv")
        assert os.path.exists(path), (
            f"{table}.csv is not staged in {STAGED}/. If an upload emptied the "
            "directory, re-run this batch's data/*.py scripts first.")
        blurb, (url, ref, doi) = BLURB[table]
        d = pd.read_csv(path, low_memory=False)
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
