##Two campus-diversity conjoints at the U.S. Naval Academy from
##Polga-Hecimovich, J., Carey, J. M., & Horiuchi, Y. (2021). Student attitudes toward campus
##diversity at the United States Naval Academy: Evidence from conjoint survey experiments.
##Armed Forces & Society, 47(2), 386-409. https://doi.org/10.1177/0095327X18824665
##Replication data: Harvard Dataverse doi:10.7910/DVN/AEA4RW, CC0 1.0, no restricted files.
##File read: ReplicationPackage/data/Conjoint-Codes-Data-RanKeys-2018FEB12.xlsx (from
##ReplicationPackage.tar.gz; sheet 2 "data with random key" = data, sheet 1 "codes" = codebook
##of the post-treatment questions). Read as text, not run: ReadMe.txt,
##scripts/10_USNA_data_wrangle.R (attribute names by level number), documents/Supplementary
##Materials.pdf (instrument appendix A-B).
##Usage: Rscript polgahecimovich_2021.R <dir holding the xlsx> <output dir>
##
##1,154 midshipmen; each was assigned ONE of two experiments (`set of cases`), so TWO tables
##(different attribute sets; the authors analyse them separately):
##  polgahecimovich_2021_admissions: 582 respondents, 8 tasks of 2 hypothetical applicants,
##    10 attributes (gender, race/ethnicity, SAT score, high-school class rank, high-school
##    type, geographical representation (home state), parents' education, family income,
##    extra-curricular interest, recruited varsity athlete).
##  polgahecimovich_2021_faculty: 572 respondents, 8 tasks of 2 hypothetical faculty
##    candidates, 9 attributes (department/program, position, civil-military status,
##    race/ethnicity, gender, graduate degree institution, undergraduate degree institution,
##    teaching record, research record).
##Respondent id = the deposit's `Random Key` (1-1154, not a platform ID). Task = case number,
##profile = profile number in the column names ("Applicant: case t, level k, profile p";
##level k = attribute k, names from 10_USNA_data_wrangle.R).
##Outcome: choice only, forced choice of one of the two profiles, no opt-out.
##  Faculty: "Which candidate do you think should be given priority in faculty recruitment?
##  Even if you are not entirely sure, please indicate which of the two you would be most
##  likely to choose." (Supplementary Materials Fig. A.1; the same figure also shows "If you
##  had to choose between them, which of these two applicants should be given priority to be
##  admitted as a new faculty member at USNA?" under the table.)
##  Admissions: wording not in the deposit; paraphrase "which applicant should be given
##  priority in admission to USNA".
##Level text is the cell text as recorded by the survey (e.g. SAT "1180", income "21000",
##"Non-Binary" in admissions vs "Non-binary" in faculty); the authors' relabelling for their
##plots ("25th pctl", "$21,000", "Legacy", ...) is not applied. Differences from the appendix
##list: race "Other" never occurs in either experiment; the faculty department attribute has
##9 levels in the data (Chemistry, Economics, Electrical Engineering, History, Mathematics,
##Mechanical Engineering, Physics, Political Science, Systems Engineering) against 4 in the
##appendix list; the appendix example table also shows "Active duty military" where the data
##have "Military or ex-military" (an earlier instrument draft). Gender is unbalanced
##("Non-binary" ~10% of profiles vs ~45% each for man and woman): level weights OBSERVED.
##Dropped: one admissions task (task 5 of one respondent) with no choice recorded (as in the
##authors' code); free-text PQ3J_other ("other activity, specify") and PQ13 (comments on the
##survey); no survey weight in the deposit.
##Covariates (post-treatment questions, codes -> answer text from the "codes" sheet):
##  cov_years_at_usna (PQ1 "Number of full years at USNA", codes 1-4 = 0-3 years);
##  cov_interest_engineering/_math_science/_humanities (PQ2A-C, 1 = ticked, 0 = not);
##  cov_activity_* (PQ3A-K, 1 = ticked, 0 = not): performing_arts, lgbtq, cultural,
##    publications, religious, outdoor, military_skills, varsity_sports, club_sports, other,
##    none; cov_sat (PQ4), cov_hs_rank (PQ5), cov_gender (PQ6 "With which gender do you most
##  identify?" Man -> male, Woman -> female), cov_race (PQ7), cov_party_id (PQ8 "Generally
##  speaking, do you usually think of yourself as a Democrat, a Republican, an independent, or
##  what?", answer text incl. "Other" and "don't know"), cov_parent_college (PQ9),
##  cov_parent_usna (PQ10), cov_parent_military (PQ11), cov_parent_income (PQ12).
##N: 582 and 572 match the Supplementary Materials figures (e.g. White N = 426 + Non-White
##N = 156 = 582 in the admissions experiment).
##Spot check: OLS of choice on all attributes, SEs clustered by id, reproduces the authors'
##saved cjoint AMCEs (figures/_csv, All Respondents): admissions Non-binary -0.199 (SE 0.019),
##Woman -0.010; faculty Non-binary -0.125 (0.018), Woman 0.022; race/ethnicity AMCEs within
##0.002. No pair of levels is missing in either table.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_xlsx(file.path(raw, "Conjoint-Codes-Data-RanKeys-2018FEB12.xlsx"), sheet = 2))
stopifnot(nrow(x) == 1154, all(x$`Random Key` == seq_len(nrow(x))))
lab <- function(v, l) { v <- as.integer(v); stopifnot(all(is.na(v) | v %in% seq_along(l))); l[v] }
tick <- function(v) { stopifnot(all(is.na(v) | v == 1)); as.integer(!is.na(v)) }
cv <- x[, .(id = as.integer(`Random Key`),
  cov_years_at_usna = lab(PQ1, c("0", "1", "2", "3")),
  cov_interest_engineering = tick(PQ2A), cov_interest_math_science = tick(PQ2B), cov_interest_humanities = tick(PQ2C),
  cov_activity_performing_arts = tick(PQ3A), cov_activity_lgbtq = tick(PQ3B), cov_activity_cultural = tick(PQ3C),
  cov_activity_publications = tick(PQ3D), cov_activity_religious = tick(PQ3E), cov_activity_outdoor = tick(PQ3F),
  cov_activity_military_skills = tick(PQ3G), cov_activity_varsity_sports = tick(PQ3H), cov_activity_club_sports = tick(PQ3I),
  cov_activity_other = tick(PQ3J), cov_activity_none = tick(PQ3K),
  cov_sat = lab(PQ4, c("Above 1600", "1380-1590", "1280-1370", "1180-1270", "Below 1180")),
  cov_hs_rank = lab(PQ5, c("99% or higher", "95%-98%", "90%-94%", "80%-89%", "50%-80%", "Below 50%")),
  cov_gender = lab(PQ6, c("male", "female")),
  cov_race = lab(PQ7, c("Native American", "Asian", "Black", "Hispanic", "White", "Other")),
  cov_party_id = lab(PQ8, c("Strong Democrat", "Democrat", "Independent, lean Democrat", "Independent",
                            "Independent, lean Republican", "Republican", "Strong Republican", "Other", "don't know")),
  cov_parent_college = lab(PQ9, c("No", "Yes")), cov_parent_usna = lab(PQ10, c("Yes", "No")),
  cov_parent_military = lab(PQ11, c("Yes", "No")),
  cov_parent_income = lab(PQ12, c("Less than $25,000", "$25,000-49,000", "$50,000-74,999", "$75,000-99,999", "$100,000-149,999",
                                  "$150,000-199,999", "$200,000-299,999", "$300,000-499,999", "$500,000 or higher")))]
build <- function(set, prefix, attrs, file, nresp) {
  s <- x[`set of cases` == set]
  rows <- list()
  for (t in 1:8) for (p in 1:2) {
    d <- data.table(id = as.integer(s$`Random Key`), task = t, profile = p,
                    choice = as.integer(s[[sprintf("%s: case %d choice", prefix, t)]] == p))
    for (k in seq_along(attrs)) d[, paste0("attr_", attrs[k]) := as.character(s[[sprintf("%s: case %d, level %d, profile %d", prefix, t, k, p)]])]
    rows[[length(rows) + 1]] <- d
  }
  d <- rbindlist(rows)
  d <- d[!is.na(choice)]
  for (v in paste0("attr_", attrs)) stopifnot(!anyNA(d[[v]]), all(nzchar(d[[v]])))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)], uniqueN(d$id) == nresp)
  d <- merge(d, cv, by = "id")
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, file))
}
build("applicant", "Applicant", c("gender", "race_ethnicity", "sat_score", "hs_class_rank", "hs_type", "home_state",
      "parents_education", "family_income", "extracurricular", "recruited_athlete"), "polgahecimovich_2021_admissions.csv", 582)
build("candidate", "Candidate", c("department", "position", "civil_military_status", "race_ethnicity", "gender",
      "graduate_degree", "undergraduate_degree", "teaching_record", "research_record"), "polgahecimovich_2021_faculty.csv", 572)
