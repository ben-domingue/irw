##Two adaptive (bandit) paired-profile experiments from
##Gosciak, J., Molitor, D., & Lundberg, I. (2026). Adaptive randomization in conjoint survey
##experiments. Political Analysis, 1-28. https://doi.org/10.1017/pan.2026.10040
##Replication data: Harvard Dataverse doi:10.7910/DVN/7EBDDY, CC0 1.0. Files read ("original
##format" downloads): immigrants_{main,max,min}_response.csv, immigrants_{main,max,min}_metadata.csv,
##job_applicants_data_clean_2025_08_01.csv. data/README.md, README.md, immigrants_plots.R and
##job_applicants_plots.R read as text (not run). Design facts are from the article (open access).
##Usage: Rscript gosciak_2026.R <raw dir> <output dir>
##Writes two tables (different attribute sets, populations and fieldings):
##
##1. gosciak_2026_immigrant_admission. Prolific, US adults, 24-30 June 2024. ONE task per
##respondent: two immigrant profiles, 5 attributes: education (focal: "College degree" vs "No
##formal education", always one of each), profession, origin, reason for application, prior trips.
##The 4 context attributes take one of 2 values per pair (16 contexts = arms; e.g. European vs
##African origin), and within a pair each profile carries one of two "signals" of that value
##(Poland/Germany, Sudan/Somalia, ...); the metadata files give the two profiles of each arm, and the
##college profile always has the same signals within an arm. Arms were assigned by Thompson
##sampling (warm-up ~equal, then adaptive search for the max, then the min, of P(choose college)),
##so level weights are nonuniform by design. Validation phases (immigrants_max/min_*) showed only
##arm 7 (max) or arm 10 (min) to new respondents; they are included (same profiles; the max/min
##metadata files match main arms 7 and 10) with trial_phase = validation_max / validation_min.
##trial_arm = arm id. Position: the article says the two profiles were randomly permuted left/right.
##The deposit records option_preference (0/1, the option chosen) and discriminated (TRUE = chose the
##college profile), so the college profile's position is INFERRED: option_preference + 1 if
##discriminated, else the other position (profile 1 = option 0; that option 0 is the left/first
##option is an assumption).
##  choice: "Which of these two immigrant profiles would you select for admission to the United
##  States?" (article Figure 4), forced choice.
##Covariates: cov_gender (sex: female/male; blank -> NA), cov_age (age as entered; entries outside
##10-120, e.g. 4 or 633, set NA), cov_race (authors' clean_race(): single code -> label, several codes -> "Two or
##More Races"; blank -> NA), cov_hispanic (authors' clean_ethnicity() labels), cov_commitment
##(yes/unsure), cov_check_correct (1 if option_attention == option_attention_truth: a post-task
##check whose wording is not in the deposit), cov_garbage (the authors' exclusion flag; data
##README: "filter out the bad responses"). Dropped: prolific_id and captcha (the captcha
##free-text field holds Prolific IDs in 2 rows: PII), consent/in_usa (all TRUE), batch ids.
##Rows: main 8,031 + validation max ~1,000 + min ~1,000. 108 Prolific IDs submitted 2-6 times in
##the main phase; for each, exactly one submission is non-garbage and the repeats (121 rows, all
##garbage = TRUE) are dropped. No ID appears in two phases. ids re-keyed 1..N (phase order). The
##article reports 10,000 recruited (2,000 warm-up, 6,000 adaptive, 2,000 validation); the deposit
##has 9,146 non-garbage responses (7,279 main + 946 max + 921 min).
##
##2. gosciak_2026_job_applicants. Prolific, US adults, Feb-Mar 2024 (the article says 8 Feb - 13
##Mar; StartDate range in the file is 25 Feb - 13 Mar). One task: two resumes for a marketing
##coordinator applying to an HR position. Profile 1 = "Candidate 1" (name1/education1/volunteer1),
##profile 2 = "Candidate 2". Randomized: race context via names (Laurie Schmitt / Allison O'Connell
##= white; Tanisha Rivers / Keisha Mosely = Black), school-rank context (mid: California State
##University, Long Beach / San Diego State University; high: University of Pennsylvania / MIT), and
##which candidate carries the motherhood signal (PTA volunteer line + cover-letter sentence vs a
##neighbourhood-association treasurer line). Contexts assigned adaptively in batches of 200
##(nonuniform). Other resume text (experience, phone, cover-letter opening) is fixed per position
##and not stored. attr_ text is as displayed (resume lines; the cover-letter sentence is
##attr_cover_letter_volunteer).
##  choice: Q1-Q8 (one per batch block; Q*_orig hold "Candidate 1"/"Candidate 2"). Question wording
##  is not in the deposit or the article: paraphrase. Forced choice; the authors' chose_mother
##  equals "chose the PTA candidate" in every row (checked).
##Covariates: cov_gender (QD5: Female/Male; "Prefer not to disclose" -> NA), cov_age (authors' clean
##age; entries below 10 set NA), cov_race (authors' clean race text; "Prefer not to disclose" -> NA), cov_hispanic (QD4 text;
##"Prefer not to disclose" -> NA), cov_duration_sec (Qualtrics whole-survey duration),
##trial_phase (batch_type), trial_context (context_label). Dropped (PII FOUND): IPAddress,
##LocationLatitude/Longitude, PROLIFIC_PID, STUDY_ID, SESSION_ID, free-text fields; also the
##manipulation check (wording not in deposit) and assignment probabilities.
##4,053 respondents = sum of the article's Figure 9 Ns (574 + 1,031 + 1,550 + 898).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
## ---- immigrants
meta <- fread(file.path(raw, "immigrants_main_metadata.csv"))
stopifnot(meta[, .N, arm_id][, all(N == 2)])
rd <- function(f, ph) { x <- fread(file.path(raw, f), colClasses = list(character = c("sex", "race", "captcha", "prolific_id"))); x[, phase := ph]; x }
r <- rbind(rd("immigrants_main_response.csv", NA_character_), rd("immigrants_max_response.csv", "validation_max"),
           rd("immigrants_min_response.csv", "validation_min"), fill = TRUE)
r0 <- fread(file.path(raw, "immigrants_main_response.csv"), select = "phase")
r[seq_len(nrow(r0)), phase := c(warmup = "warmup", max = "adaptive_max", min = "adaptive_min")[r0$phase]]
stopifnot(!anyNA(r$phase), r[phase == "validation_max", all(arm_id == 1)], r[phase == "validation_min", all(arm_id == 1)])
for (f in c("max", "min")) {   # validation arms equal main arms 7 / 10
  m <- fread(file.path(raw, sprintf("immigrants_%s_metadata.csv", f)))
  k <- if (f == "max") 7L else 10L
  stopifnot(all(m[, .(education, prior_trips, origin, reason, profession)] == meta[arm_id == k, .(education, prior_trips, origin, reason, profession)]))
}
r[phase == "validation_max", arm_id := 7L][phase == "validation_min", arm_id := 10L]
# 108 Prolific IDs submitted 2-6 times in the main phase; exactly one submission per ID is
# non-garbage, the repeats are all garbage = TRUE: drop the repeats (121 rows).
r[, nsub := .N, prolific_id]
stopifnot(r[nsub > 1, sum(!garbage), prolific_id][, all(V1 == 1)])
r <- r[nsub == 1 | !garbage]
stopifnot(uniqueN(r$prolific_id) == nrow(r))
r[, id := .I]
r[, cpos := fifelse(discriminated, option_preference + 1L, 2L - option_preference)]
col <- meta[education == "College degree"]; non <- meta[education != "College degree"]
stopifnot(nrow(col) == 16, nrow(non) == 16)
mk <- function(p) {
  isc <- r$cpos == p
  m <- rbind(col, non)[match(paste(r$arm_id, isc), paste(c(col$arm_id, non$arm_id), rep(c(TRUE, FALSE), each = 16)))]
  data.table(id = r$id, task = 1L, profile = p, choice = as.integer(r$option_preference + 1L == p),
             attr_education = m$education, attr_profession = m$profession, attr_origin = m$origin,
             attr_reason = m$reason, attr_prior_trips = m$prior_trips, trial_arm = r$arm_id, trial_phase = r$phase)
}
d <- rbind(mk(1L), mk(2L))
stopifnot(!anyNA(d), d[, sum(choice), id][, all(V1 == 1)], d[, uniqueN(attr_education), id][, all(V1 == 2)])
stopifnot(all(d[choice == 1, .(id, c = attr_education == "College degree")][order(id)]$c == r$discriminated))
levs <- c(race_white = "White", race_black = "Black or African American", race_asian = "Asian",
          race_aian = "American Indian or Alaska Native", race_nhpi = "Native Hawaiian or Pacific Islander", race_other = "Other")
race <- fifelse(r$race == "", NA_character_, fifelse(r$race %in% names(levs), levs[r$race], "Two or More Races"))
cv <- data.table(id = r$id, cov_gender = fcase(r$sex == "female", "female", r$sex == "male", "male", default = NA_character_),
                 cov_age = fifelse(r$age >= 10 & r$age <= 120, r$age, NA_real_), cov_race = race,
                 cov_hispanic = c(hisp_latin_spanish_no = "Not Hispanic or Latino", hisp_latin_spanish_yes = "Hispanic or Latino")[r$ethnicity],
                 cov_commitment = r$commitment, cov_check_correct = as.integer(r$option_attention == r$option_attention_truth),
                 cov_garbage = as.integer(r$garbage))
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gosciak_2026_immigrant_admission.csv"))
## ---- job applicants
j <- fread(file.path(raw, "job_applicants_data_clean_2025_08_01.csv"))
stopifnot(nrow(j) == 4053, uniqueN(j$unique_id) == 4053)
q <- paste0("Q", 1:8, "_orig")
ch <- apply(j[, ..q], 1, function(z) { z <- z[!is.na(z) & z != ""]; if (length(z) == 1) z else NA_character_ })
cp <- as.integer(sub("Candidate ", "", ch)); stopifnot(all(cp %in% 1:2))
mpos <- ifelse(grepl("Parent Teacher", j$volunteer1), 1L, 2L)
stopifnot(all(as.integer(cp == mpos) == j$chose_mother))
cl <- function(x) trimws(x)
jj <- rbind(j[, .(id = unique_id, profile = 1L, choice = as.integer(cp == 1L), attr_name = name1, attr_education = education1,
                  attr_volunteer = cl(volunteer1), attr_cover_letter_volunteer = cl(treatment1))],
            j[, .(id = unique_id, profile = 2L, choice = as.integer(cp == 2L), attr_name = name2, attr_education = education2,
                  attr_volunteer = cl(volunteer2), attr_cover_letter_volunteer = cl(treatment2))])
jj[, task := 1L]
nd <- function(x) fifelse(x == "Prefer not to disclose" | x == "", NA_character_, x)
jc <- j[, .(id = unique_id, trial_phase = batch_type, trial_context = context_label,
            cov_gender = c(Female = "female", Male = "male")[QD5], cov_age = fifelse(age >= 10 & age <= 120, age, NA_real_), cov_race = nd(race), cov_hispanic = nd(QD4),
            cov_duration_sec = `Duration (in seconds)`)]
jj <- merge(jj, jc, by = "id")
setcolorder(jj, c("id", "task", "profile", "choice"))
stopifnot(!anyNA(jj[, .SD, .SDcols = patterns("^attr_")]), jj[, sum(choice), id][, all(V1 == 1)])
setorder(jj, id, task, profile)
fwrite(jj, file.path(out, "gosciak_2026_job_applicants.csv"))
