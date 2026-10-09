##Candidate conjoint on crime platforms (US national sample and US student sample) from
##Laterzo-Tingley, I., & Christiani, L. (2024). The "tough-on-crime" left: Race, gender, and
##elections of law-and-order Democrats. Research & Politics, 11(3).
##https://doi.org/10.1177/20531680241261765 (CC BY article; not readable here: publisher blocks)
##Replication data: Harvard Dataverse doi:10.7910/DVN/8ENZUC, CC0 1.0, no restricted files, no terms.
##Files read: survey1_data.rds (national sample), survey2_data.rds (student sample), codebook.pdf
##(covariate codes, attribute levels), readme.txt; maintext_analyses.R read as text, not run.
##Usage: Rscript laterzotingley_2024.R <raw dir> <output dir>
##
##TWO TABLES, one per sample: the authors analyse the national survey in the main text and the
##student survey separately (appendix files), never pooled, and the samples carry different
##covariates:
##  laterzotingley_2024_crime_national  (survey1: 1,499 respondents, "nationally representative")
##  laterzotingley_2024_crime_students  (survey2: 713 respondents, student sample)
##Design (codebook; maintext): paired candidate profiles, five tasks per respondent ("all five
##conjoint tasks", codebook all_candA), five binary attributes: cand_gender (Female/Male), cand_race
##(Black/White), cand_tax (Increase Income Tax / Increase Sales Tax), cand_pubsec (Prevention /
##Tough on Crime), cand_edu (Public School Investment / School Choice). Level text = the codebook /
##data labels; whether respondents saw exactly these short labels or longer platform statements is
##not documented (the article could not be read).
##Outcome: choice = chosen (1 = this candidate profile was chosen). Forced choice: every task has
##exactly one chosen profile. Question wording not in the deposit: unknown.
##TASK / PROFILE RECONSTRUCTION. The files have no task or profile column. Each file is a stack of
##two halves of equal length: rows 1..N/2 are the chosen profiles, rows N/2+1..N the unchosen ones,
##and row r and row r + N/2 always belong to the same respondent (checked for every row), so
##(r, r + N/2) is taken as one task (INFERRED from row order). Which candidate was shown as A or B
##is not recorded (the authors' all_candA/all_candB flags exist only for straight-liners), so,
##to keep profile numbering independent of the outcome, profile 1 is the profile whose attribute
##string (gender|race|tax|pubsec|edu) sorts first; when the two profiles are identical, the chosen
##row is profile 1 in odd-numbered stacked pairs and profile 2 in even ones (alternating, so that
##position carries no information about the choice). profile_source = unknown. Task number = rank
##of the chosen row within the
##respondent's rows (task order unknown). Respondents with fewer than five tasks (national 30, students
##27) are kept with the tasks they have.
##Covariates, national (codebook codes -> text): cov_age_group (age: 1 Under 18, 2 18-24, 3 25-34,
##4 "25-44" in the codebook, written 35-44 here (the band between 25-34 and 45-54), 5 45-54, 6 55 or
##older), cov_gender (female 1/0 -> female/male; NA = neither describes me well or no answer),
##cov_education (edu), cov_sexuality (queer), cov_race (race, select all that apply: codes -> text,
##"; "-joined), cov_party_id (pid, factor labels: Democrat / Republican / Independent / Don't Know),
##cov_party_lean (pidLean factor labels), cov_party_strong_code (pidStrong, stored 0/1 while the
##codebook gives 1 = strong / 2 = not strong: mapping unknown, codes kept), cov_ideology (ideo,
##7-point text, codebook spelling "middle of the raod" corrected), cov_thermometer_dem_party,
##_rep_party, _biden, _trump (0-100), cov_tough_racist (agreement that tough-on-crime policies
##target Black people more than white people, 1 strongly agree ... 7 strongly disagree, as text).
##Students: cov_gender (Female/Male/Other -> female/male/other), cov_age (years).
##Dropped: Qualtrics ResponseIds (re-keyed 1..N), the authors' derived dummies (dems, reps,
##race_white/black/hisp/asian, all_candA, all_candB). No survey weight in the deposit.
##N: unique ids 1,499 (national) and 713 (students); the article's counts could not be checked.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c(cand_gender = "gender", cand_race = "race", cand_tax = "tax", cand_pubsec = "public_security", cand_edu = "education_policy")
pairup <- function(s) {
  s <- as.data.table(s); n <- nrow(s) / 2
  stopifnot(n == round(n), all(s$id[1:n] == s$id[(n + 1):(2 * n)]), all(s$chosen[1:n] == 1), all(s$chosen[(n + 1):(2 * n)] == 0))
  s[, pair := c(1:n, 1:n)][, half := rep(1:2, each = n)]
  for (k in names(attrs)) s[, (k) := as.character(get(k))]
  s[, key := do.call(paste, c(.SD, sep = "|")), .SDcols = names(attrs)]
  s[, tb := fifelse(pair %% 2L == 1L, half, 3L - half)]
  s[, profile := frank(list(key, tb), ties.method = "first"), by = pair]
  s[, task := frank(pair, ties.method = "dense"), by = id]
  s[, rid := match(id, unique(id))]
  stopifnot(s[, .N, .(rid, task)][, all(N == 2)], s[, sum(chosen), .(rid, task)][, all(V1 == 1)], s[, uniqueN(profile), .(rid, task)][, all(V1 == 2)])
  s
}
core <- function(s) {
  d <- s[, .(id = rid, task = as.integer(task), profile = as.integer(profile), choice = as.integer(chosen))]
  for (k in names(attrs)) d[, paste0("attr_", attrs[[k]]) := s[[k]]]
  stopifnot(!anyNA(d))
  d
}
## national
s <- pairup(readRDS(file.path(raw, "survey1_data.rds")))
d <- core(s)
racelab <- c("White", "Black or African-American", "Hispanic or Latino", "Asian", "American Indian, Native American, or Alaska Native",
             "Native Hawaiian or Pacific Islander", "Other")
rc <- strsplit(as.character(s$race), ",")
stopifnot(all(unlist(rc) %in% as.character(1:7) | is.na(unlist(rc))))
edu <- c("Did not attend high school", "some high school, did not graduate", "high school graduate", "some college", "Associate's Degree",
         "Bachelor's Degree", "Master's Degree", "Professional Degree (e.g., JD, MD)", "Doctorate")
ideo <- c("strongly liberal", "liberal", "weak liberal", "moderate; middle of the road", "weak conservative", "conservative", "strongly conservative")
tr <- c("strongly agree", "agree", "somewhat agree", "neither agree nor disagree", "somewhat disagree", "disagree", "strongly disagree")
stopifnot(all(s$age %in% 1:6), all(s$edu %in% c(1:9, NA)), all(s$ideo %in% c(1:7, NA)), all(s$queer %in% c(0:3, NA)), all(s$tough_racist %in% c(1:7, NA)))
num <- function(x) suppressWarnings(as.numeric(as.character(x)))
d[, `:=`(cov_age_group = c("Under 18", "18-24", "25-34", "35-44", "45-54", "55 or older")[s$age],
         cov_gender = c(`0` = "male", `1` = "female")[as.character(s$female)],
         cov_education = edu[s$edu],
         cov_sexuality = c("straight, heterosexual", "Gay, Lesbian, Homosexual", "Bisexual, pansexual", "Other")[s$queer + 1],
         cov_race = vapply(rc, function(z) if (all(is.na(z))) NA_character_ else paste(racelab[as.integer(z)], collapse = "; "), ""),
         cov_party_id = as.character(s$pid), cov_party_lean = as.character(s$pidLean),
         cov_party_strong_code = as.integer(as.character(s$pidStrong)), cov_ideology = ideo[s$ideo],
         cov_thermometer_dem_party = num(s$thermometer_1), cov_thermometer_rep_party = num(s$thermometer_2),
         cov_thermometer_biden = num(s$thermometer_3), cov_thermometer_trump = num(s$thermometer_4),
         cov_tough_racist = tr[s$tough_racist])]
setorder(d, id, task, profile)
cat("national", uniqueN(d$id), "respondents", nrow(d), "rows\n")
fwrite(d, file.path(out, "laterzotingley_2024_crime_national.csv"))
## students
s <- pairup(readRDS(file.path(raw, "survey2_data.rds")))
d <- core(s)
stopifnot(all(s$gender %in% c("Female", "Male", "Other")))
d[, `:=`(cov_gender = c(Female = "female", Male = "male", Other = "other")[as.character(s$gender)], cov_age = as.integer(s$age))]
setorder(d, id, task, profile)
cat("students", uniqueN(d$id), "respondents", nrow(d), "rows\n")
fwrite(d, file.path(out, "laterzotingley_2024_crime_students.csv"))
