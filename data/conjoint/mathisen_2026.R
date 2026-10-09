##Government-satisfaction factorial vignette (US, YouGov, May 2023) from
##Mathisen, R. (2026). Coincidental representation: How congruence and influence shape public
##satisfaction with government. Political Behavior. https://doi.org/10.1007/s11109-026-10195-y
##Replication data: Harvard Dataverse doi:10.7910/DVN/X0J2JI, CC0 1.0, no restricted files.
##File read: data.sav (2,448 rows, one per respondent; SPSS value labels give the level text).
##Read as text: code.R (the author's analysis code) and the article (Springer HTML, Table 2
##"Treatment formulations").
##Usage: Rscript mathisen_2026.R <raw dir> <output dir>
##
##2,448 US adults (YouGov panel, quotas on gender, age, region, education, race; article), each
##rating three hypothetical countries, "Country A", "Country B", "Country C" (tasks 1-3, one
##profile each; task = the country letter, which the questionnaire shows in that order; task
##and profile are therefore read from the variable names, not from a display-order record).
##Each country has three randomized text components (presentation = text), "simple
##randomization with a uniform probability distribution" (article):
##  attr_influence (UB_TREATMENT_1/4/7): political equality vs inequality paragraph;
##  attr_economic  (UB_TREATMENT_2/5/8): very/somewhat liberal/conservative on economic issues;
##  attr_moral     (UB_TREATMENT_3/6/9): very/somewhat liberal/conservative on moral issues.
##Level text = the SPSS value labels, which SPSS cuts at 120 characters. The cut labels (both
##influence levels, the two liberal economic levels) are completed from the article's Table 2:
##influence equality "... Whether you are poor or rich, you have approximately the same level
##of influence on government decisions as everyone else."; inequality "... The richest 1
##percent of the population has strong influence on government decisions, while ordinary
##citizens like yourself have little or no influence."; liberal economic "... government-provided
##health care, etc.)". The final full stop of the two influence paragraphs is assumed. The
##influence text names the country (A/B/C) as displayed, so each influence level has three
##spellings, one per task; the Country A inequality label reads "when it comes policymaking"
##(no "to") in the data and is kept. The frame sentence joining the components (fixed country
##background: high living standards, free speech, free elections) is not deposited.
##Outcome, stored raw: rating (UB6_1/UB7_1/UB8_1) "As an ordinary citizen of Country A, how
##satisfied would you be with the government? Please answer on a scale from 0 to 10, where 0
##means 'Extremely dissatisfied' and 10 means 'Extremely satisfied'." No missing ratings.
##Covariates (value-label text): cov_gender (Male/Female -> male/female), cov_age_group
##(age_cross), cov_race (race_xbreak), cov_education (educ_w8), cov_income (gross household
##income band; "Don't know / Prefer not to say" -> NA), cov_party_id (pid3; "Other", "Not sure"
##kept as text), cov_econ_liberal / cov_econ_conservative / cov_moral_liberal /
##cov_moral_conservative (q1_1..q4_1, 0-10 self-placements, raw), cov_equal_say (UB5 answer
##text, "Don't know" kept), cov_survey_weight (weight, used in all the author's models).
##RecordNo (YouGov record number) is replaced by a 1..N id. The author's derived distances and
##dummies are not kept. n = 2,448 and 7,344 observations as in the article.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_sav(file.path(raw, "data.sav"))
stopifnot(nrow(s) == 2448, uniqueN(s$RecordNo) == 2448)
lab <- function(x) as.character(as_factor(x, levels = "labels"))
inf_full <- function(x, L) {
  out <- character(length(x))
  eq <- grepl("listens more or less equally", x); ineq <- grepl("does not listen equally", x)
  stopifnot(all(eq | ineq))
  out[eq] <- paste0(sub(" Whethe$", "", x[eq]),
    " Whether you are poor or rich, you have approximately the same level of influence on government decisions as everyone else.")
  out[ineq] <- paste0(sub(" The r$| Th$", "", x[ineq]),
    " The richest 1 percent of the population has strong influence on government decisions, while ordinary citizens like yourself have little or no influence.")
  stopifnot(all(grepl(paste0("Country ", L), out)))
  out
}
eco_full <- function(x) {
  i <- grepl("government-provided hea?$", x); x[i] <- sub("government-provided hea?$", "government-provided health care, etc.)", x[i])
  stopifnot(all(grepl("\\)\\.?$", x))); x
}
ids <- seq_len(nrow(s))
cv <- data.table(
  cov_gender = c(Male = "male", Female = "female")[lab(s$gender)],
  cov_age_group = lab(s$age_cross), cov_race = lab(s$race_xbreak), cov_education = lab(s$educ_w8),
  cov_income = lab(s$profile_gross_household_r), cov_party_id = lab(s$pid3),
  cov_econ_liberal = as.integer(s$q1_1), cov_econ_conservative = as.integer(s$q2_1),
  cov_moral_liberal = as.integer(s$q3_1), cov_moral_conservative = as.integer(s$q4_1),
  cov_equal_say = lab(s$UB5), cov_survey_weight = as.numeric(s$weight))
cv[cov_income == "Don't know / Prefer not to say", cov_income := NA]
stopifnot(!anyNA(cv$cov_gender))
d <- rbindlist(lapply(1:3, function(t) {
  L <- LETTERS[t]; k <- 3 * (t - 1)
  data.table(id = ids, task = t, profile = 1L,
             rating = as.integer(s[[paste0("UB", 5 + t, "_1")]]),
             attr_influence = inf_full(lab(s[[paste0("UB_TREATMENT_", k + 1)]]), L),
             attr_economic = eco_full(lab(s[[paste0("UB_TREATMENT_", k + 2)]])),
             attr_moral = lab(s[[paste0("UB_TREATMENT_", k + 3)]]), cv)
}))
stopifnot(!anyNA(d$rating), all(d$rating %in% 0:10), d[, uniqueN(attr_economic)] == 4, d[, uniqueN(attr_moral)] == 4,
          d[, uniqueN(attr_influence)] == 6)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mathisen_2026_satisfaction.csv"))
