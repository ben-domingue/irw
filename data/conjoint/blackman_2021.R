##Candidate-choice conjoints in Tunisia (two surveys) from
##Blackman, A. D., & Jackson, M. (2021). Gender stereotypes, political leadership, and voting
##behavior in Tunisia. Political Behavior, 43(3), 1037-1066 (online 2019).
##https://doi.org/10.1007/s11109-019-09582-5
##Replication data: Harvard Dataverse doi:10.7910/DVN/HPMEVO, CC0 1.0, no restricted files.
##Files read: femalepol_bjka.xlsx (BJKA household survey, July 2017) and femalepol_yg.xlsx
##(YouGov online survey, April 2019); level text is stored in both. Codebook.pdf gives the
##covariate wording and codes; 1.survey_cleaning.R and 3.main_analyses.R read as text only
##(they define the task pairing and the authors' renames).
##Usage: Rscript blackman_2021.R <raw dir> <output dir>
##
##TWO TABLES, one per survey: different samples, years, modes and partly different level sets
##(party lists, ages, town wording); the authors analyse them separately.
##
##(1) blackman_2021_tunisia_household: 1,193 face-to-face respondents in 5 governorates (Beja,
##Bizerte, Sfax, Sidi Bouzid, Sousse); 709 answered at least one task and are kept. Profiles
##sex_k ... exper_k, k = 1..8; contest_k pairs them into 4 tasks (k = 1,2 -> task 1, ...);
##profile = position in the pair. choice_k: exactly one of the pair is 1 in every answered
##task; 2,571 unanswered tasks (both NA) are dropped. trial_election = tassign_conjoint, the
##randomized election prompt read before the conjoint ("municipal" = local council elections,
##"natl_parl" = 2019 national parliamentary elections; codebook; the Arabic prompt is
##tinsert3). The interview was in Tunisian Arabic (tinsert3); the level text survives only in
##English as stored.
##(2) blackman_2021_tunisia_online: 574 YouGov online respondents (April 2019), all answered all
##5 tasks; questionnaire in Arabic (540) or English (34), cov_language. Profiles A..J
##(A1_profileX..A8_profileX), tasks QS3_cj1..5 = pairs A/B, C/D, E/F, G/H, I/J; choice = the
##chosen "Candidate X". Level text as stored (the English-version wording), NOT the authors'
##renames ("Jabha Shabiyya" -> Popular Front, "Studied outside of Tunis" -> "...Tunisia",
##"Director of an organization" -> Director, which their analysis code applies).
##Attributes (both): attr_sex, attr_party, attr_job, attr_town, attr_education, attr_age,
##attr_policy, attr_experience. Randomization rules, attribute order and display format are not
##documented in the deposit. Outcome wording is not in the deposit or codebook (paraphrase:
##the respondent chose one of the two candidates; the paper's outcome is vote support). No
##opt-out in the data.
##Covariates. Household: cov_gender (female; Male/Female), cov_age (age_4_text, whole numbers
##18-100 kept), cov_education (educ_level answer text: None, Elementary, Preparatory, Secondary,
##BA, MA or higher, Don't Know; "Refused to answer" -> NA), cov_governorate (loc_2),
##cov_enumerator_gender (enum_gen), cov_party_id (pol_party, "Currently, which of the existing
##parties is closest to representing your political, social, and economic aspirations?", answer
##text; refusal -> NA), cov_women_leaders / cov_women_education / cov_women_jobs
##(att_women_1..3: "In general, men are better political leaders than women." / "University
##education for men is more important than university education for women." / "When jobs are
##scarce, men should have more right to a job than women.", answer text, refusal -> NA).
##Online: cov_gender (gender), cov_age_group (vage), cov_education (education, answer text),
##cov_women_leaders / _education / _jobs (QS1_women_leaders/_edu/_jobs, answer text),
##cov_city (city/region), cov_nationality (TUNISIANat: Tunisian / Expat), cov_language (lang),
##cov_survey_weight (weight).
##Dropped (PII or identifying): responseid / RecordNo (re-keyed to integers in file order),
##recorded/end dates, loc_3 delegation, loc_4 sector, loc_5 (degree-minute-second coordinate
##codes), hh_id / v23 / hh_num_1 (household numbers), free-text "other" answers
##(priority_9_text, QS5/QS6 *_t). Also dropped: the separate Miriam/Ahmed vignette experiments
##(stored as arm codes only, no vignette text) and all other survey items.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
nar <- function(x) { x[x %in% c("Refuse to answer", "Refused to answer")] <- NA; x }
## (1) household
x <- as.data.table(read_excel(file.path(raw, "femalepol_bjka.xlsx"), guess_max = 5000))
stopifnot(!anyDuplicated(x$responseid))
x[, id := seq_len(.N)]
st <- c(sex = "sex", party = "party", job = "job", town = "town", education = "educ", age = "age",
        policy = "policy", experience = "exper")
h <- rbindlist(lapply(1:8, function(k) {
  stopifnot(all(x[[paste0("contest_", k)]] == (k + 1) %/% 2))
  z <- data.table(id = x$id, task = (k + 1L) %/% 2L, profile = 2L - k %% 2L,
                  choice = as.integer(x[[paste0("choice_", k)]]))
  for (s in names(st)) z[, paste0("attr_", s) := as.character(x[[paste0(st[[s]], "_", k)]])]
  z }))
h <- h[!is.na(choice)]
stopifnot(h[, .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)],
          !anyNA(h[, .SD, .SDcols = patterns("^attr_")]))
age_yrs <- suppressWarnings(as.numeric(x$age_4_text))
age_yrs[!(age_yrs %in% 18:100)] <- NA
cvh <- x[, .(id, trial_election = tassign_conjoint,
  cov_gender = tolower(female), cov_age = as.integer(age_yrs[id]),
  cov_education = nar(educ_level), cov_governorate = loc_2, cov_enumerator_gender = tolower(enum_gen),
  cov_party_id = nar(pol_party),
  cov_women_leaders = nar(att_women_att_women_1), cov_women_education = nar(att_women_att_women_2),
  cov_women_jobs = nar(att_women_att_women_3))]
stopifnot(all(cvh$cov_gender %in% c("female", "male")), all(cvh$trial_election %in% c("municipal", "natl_parl")))
h <- merge(h, cvh, by = "id")
setcolorder(h, c("id", "task", "profile", "choice", grep("^attr_", names(h), value = TRUE), "trial_election"))
setorder(h, id, task, profile)
fwrite(h, file.path(out, "blackman_2021_tunisia_household.csv"))
## (2) online
y <- as.data.table(read_excel(file.path(raw, "femalepol_yg.xlsx"), guess_max = 5000))
stopifnot(!anyDuplicated(y$RecordNo))
y[, id := seq_len(.N)]
an <- c(sex = 1, party = 2, job = 3, town = 4, education = 5, experience = 6, policy = 7, age = 8)
o <- rbindlist(lapply(1:10, function(k) {
  L <- LETTERS[k]; t <- (k + 1L) %/% 2L
  z <- data.table(id = y$id, task = t, profile = 2L - k %% 2L,
                  choice = as.integer(y[[paste0("QS3_cj", t)]] == paste("Candidate", L)))
  stopifnot(all(y[[paste0("QS3_cj", t)]] %in% paste("Candidate", LETTERS[c(2 * t - 1, 2 * t)])))
  for (s in names(an)) z[, paste0("attr_", s) := as.character(y[[sprintf("A%d_profile%s", an[[s]], L)]])]
  z }))
setcolorder(o, c("id", "task", "profile", "choice", paste0("attr_", names(st))))
stopifnot(o[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(o))
cvo <- y[, .(id, cov_gender = tolower(gender), cov_age_group = vage, cov_education = education,
  cov_women_leaders = QS1_women_leaders, cov_women_education = QS1_women_edu, cov_women_jobs = QS1_women_jobs,
  cov_city = city, cov_nationality = TUNISIANat, cov_language = lang, cov_survey_weight = as.numeric(weight))]
stopifnot(all(cvo$cov_gender %in% c("female", "male")))
o <- merge(o, cvo, by = "id")
setorder(o, id, task, profile)
fwrite(o, file.path(out, "blackman_2021_tunisia_online.csv"))
