##Job-training conjoints in Germany and South Korea from
##Brehm, N., Zhou, A. H., & Denney, S. (2025). From division to democracy: Integrating
##post-socialist citizens in Germany and South Korea. Communist and Post-Communist Studies.
##https://doi.org/10.1525/cpcs.2025.2636997 (Appendix C, Figures C1-C10, per the deposit README)
##Replication data: Harvard Dataverse doi:10.7910/DVN/WYBIAK (Denney, "Replication Data for:
##Welfare Chauvinism in Divided Societies: The Role of National Identity in Social Policy
##Preferences"), CC0 1.0, no restricted files, no terms. The deposit title names a different
##manuscript; its README cites the CPCS article above, which is used here. Same surveys
##(IFES 2023) as brehm_2025.R (emerging-politician conjoint, deposit 8GUUP5); this is the
##second, separate experiment.
##Files read: germany_job_training.csv, korea_job_training.csv (Dataverse "original format"
##downloads; the authors' long files, one row per respondent x task x profile). Read as text:
##README.md, data_dictionary_germany.md, data_dictionary_korea.md, prepare_data.R, analysis.R.
##Usage: Rscript brehm_2025_job_training.R <raw dir> <output dir>
##
##Respondents chose between two hypothetical people (candidates for state job-training
##support, per the file names and the README's "job-training conjoint"), each described by 6
##attributes: Age (25/35/46/62), Family, Gender, Occupation, Record (None/Theft/Tax evasion)
##and Origin (Germany: Saxony, DE / Hamburg, DE / Bavaria, DE / Bucharest, RO; Korea: North
##Hamgyong, DPRK / Busan, ROK / Gyeonggi, ROK / Hanoi, Vietnam). Attribute text is the
##authors' English translation as deposited (respondents saw German or Korean); the
##dictionaries say Age levels were "standardized to 25, 35, 46, 62 to match the published
##design", so the stored age text may differ slightly from what was displayed. Record "None"
##is a literal level (read with na = "" only).
##Outcome: choice = candidate_choice, 1 = this profile chosen; exactly one per task (checked),
##so forced choice, no opt-out. Question wording is not deposited and the article (paywalled)
##was not read: design_outcomes carries a paraphrase.
##Two tables, one per country (different populations, Origin levels and the authors analyse
##them separately):
##  brehm_2025_job_training_germany  1,882 respondents (README: 1,882, after attention check and
##     non-missing national identity), 6 tasks. The authors' main analysis further restricts
##     to Western, ethnic Germans (derived in analysis.R from state_at_18 and ethnicity); all
##     1,882 are kept here with those covariates. 245 respondents have NA on party_vote and the
##     Q60/Q62/Q63 items (missing in the deposit).
##  brehm_2025_job_training_korea    1,768 respondents (README: 1,768, attention check), 7 tasks.
##task/profile from question_profile ("t.p").
##Record levels are unequal (None ~70%, Theft and Tax evasion ~15% each); no source gives the
##probabilities (level_weights = observed).
##Covariates (raw answer text in German or Korean, per the data dictionaries):
##  cov_birth_year = yob (DE Q2 / KR Q4), as recorded: implausible years remain (Germany 3
##  respondents born after 2005, Korea 12); the authors' age = 2023 - yob is dropped
##  because it inherits them (as in brehm_2025.R); cov_female = the deposit's female (1 = answered
##  "Weiblich"/"여성" to gender at birth, 0 = any other answer; kept as coded, not mapped to
##  cov_gender since 0 is not only "male"); cov_education (DE Q8 / KR Q5, answer text);
##  cov_party_vote (vote intention, not party identification; "don't know" kept as text);
##  DE: cov_state_at_18, cov_current_state, cov_ethnicity, cov_national_identity (0-10),
##  cov_ancestry_importance, cov_birthplace_importance, cov_support_needy_training,
##  cov_support_gdr_training; KR: cov_province, cov_political_ideology, cov_korean_pride,
##  cov_national_identity (0-10), cov_ancestry_importance, cov_birthplace_importance,
##  cov_national_composition, cov_support_nk_engagement, cov_support_nk_defectors.
##Dropped: ResponseId (Qualtrics ID; respondents re-keyed to integers in file order). The
##deposit has no derived variables and no survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(f, name, ntask, nresp) {
  k <- fread(file.path(raw, f), na.strings = "", encoding = "UTF-8", colClasses = "character")
  stopifnot(!anyNA(k$Record), all(k$Record %in% c("None", "Theft", "Tax evasion")))
  ids <- unique(k$ResponseId)
  d <- data.table(id = match(k$ResponseId, ids),
                  task = as.integer(sub("\\..*", "", k$question_profile)),
                  profile = as.integer(sub(".*\\.", "", k$question_profile)),
                  choice = as.integer(k$candidate_choice))
  for (v in c("Age", "Family", "Gender", "Occupation", "Record", "Origin")) d[, paste0("attr_", tolower(v)) := k[[v]]]
  d[, cov_birth_year := as.integer(k$yob)][, cov_female := as.integer(k$female)]
  cv <- setdiff(names(k), c("ResponseId", "question_profile", "candidate_choice", "Age", "Family", "Gender",
                            "Occupation", "Record", "Origin", "age", "yob", "female"))
  for (v in cv) d[, paste0("cov_", v) := k[[v]]]
  d[, cov_national_identity := as.integer(cov_national_identity)]
  stopifnot(uniqueN(d$id) == nresp, max(d$task) == ntask, d[, .N, .(id, task)][, all(N == 2)],
            d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
build("germany_job_training.csv", "brehm_2025_job_training_germany", 6L, 1882L)
build("korea_job_training.csv", "brehm_2025_job_training_korea", 7L, 1768L)
