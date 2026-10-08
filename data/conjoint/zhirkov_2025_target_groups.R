##Immigrant-illegality rating conjoint (US) from
##Zhirkov, K., & Van De Hey, L. (2025). Multidimensional constructions of target groups and their
##political implications: The case of immigrant (il)legality. PS: Political Science & Politics,
##58(4), 641-650. https://doi.org/10.1017/S1049096525000034
##Replication data: Harvard Dataverse doi:10.7910/DVN/HPFSZJ, CC0 1.0, no restricted files.
##Files read (from replication_materials.zip): data/data_02_conjoint.dta (profiles, ratings),
##data/data_01_survey.dta (respondent covariates). Level text = Stata value labels; question
##wording and design from the article and its supplement (no codebook in the deposit).
##Usage: Rscript zhirkov_2025_target_groups.R <raw dir holding data/> <output dir>
##
##928 non-Hispanic white US adults (Lucid, December 2021). The article's final N is 935 (after
##the authors dropped 79 straight-liners, who are not in the deposit); data_01_survey has 935
##respondents but 7 of them have no conjoint rows, so the table has 928. Each rated 20 single
##profiles of hypothetical immigrants (19 respondents rated 14-19): one profile per task, so
##task = source `profile` (Conjoint profile no.) and profile = 1.
##Outcome: rating = likelihood of belonging to an "illegal/undocumented immigrant" group,
##0 = Extremely unlikely .. 10 = Extremely likely (article wording; higher = judged more likely
##undocumented, which is the authors' direction, not a favourability scale). No choice question.
##Attributes (8): age (number, 25-54), gender, race/ethnicity (White/Black/Hispanic/Asian), years
##stayed in the U.S. (number, 1-20), English fluency, education, government benefits, police
##record (benefits: None / Food stamps / Medicaid / SSI / Welfare). Numeric age and years are stored as the number; the displayed wording around them is
##not deposited. Randomization (article): fully independent, but police record and benefits are
##"no" vs "yes" with probability 1/2 each, the "yes" half split equally across the specific
##crimes/programmes. The value-label set for police record also lists Drunk driving and
##Trespassing, which never occur (only Assault, Drug possession, Theft are used).
##Covariates (data_01_survey): cov_age years; cov_gender 1=Male 2=Female; cov_education 1-8
##(1 = some high school or less .. 8 = doctorate); cov_income household income bracket 1-..
##(1 = < $14,999, $5,000 steps; labels in the .dta); cov_pid7 1 = Strong Democrat .. 7 = Strong
##Republican; cov_policy_daca_oppose, cov_policy_sb1070_support, cov_policy_sanctuary_oppose,
##cov_policy_wall_support (1-7, direction as named; wording in the supplement). Dropped: the
##authors' dummies (conj_*, female, college, pid3, policy index).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "data", "data_02_conjoint.dta"))
s <- read_dta(file.path(raw, "data", "data_01_survey.dta"))
lab <- function(x) { l <- attr(x, "labels"); v <- as.integer(zap_labels(x)); stopifnot(all(v %in% l)); unname(names(l)[match(v, l)]) }
d <- data.table(id = as.integer(k$respid), task = as.integer(k$profile), profile = 1L, rating = as.integer(k$rate),
                attr_age = as.character(as.integer(k$attr_ages)), attr_gender = lab(k$attr_gend), attr_race = lab(k$attr_race),
                attr_years_in_us = as.character(as.integer(k$attr_stay)), attr_english = lab(k$attr_engl),
                attr_education = lab(k$attr_educ), attr_benefits = lab(k$attr_welf), attr_police_record = lab(k$attr_crim))
stopifnot(all(d$rating %in% 0:10), !anyDuplicated(d[, .(id, task)]))
# labels agree with the authors' dummies
stopifnot(all((k$conj_males == 1) == (d$attr_gender == "Man")), all((k$conj_crime == 1) == (d$attr_police_record != "No record")),
          all((k$conj_welfr == 1) == (d$attr_benefits != "None")), all((k$conj_hispn == 1) == (d$attr_race == "Hispanic")),
          all((k$conj_pengl == 1) == (d$attr_english == "Poor")))
r <- data.table(id = as.integer(s$respid), cov_age = as.integer(s$age), cov_gender = as.integer(zap_labels(s$gender)),
                cov_education = as.integer(zap_labels(s$education)), cov_income = as.integer(zap_labels(s$income)),
                cov_pid7 = as.integer(zap_labels(s$pid7)), cov_policy_daca_oppose = as.integer(s$policy1),
                cov_policy_sb1070_support = as.integer(s$policy2), cov_policy_sanctuary_oppose = as.integer(s$policy3),
                cov_policy_wall_support = as.integer(s$policy4))
stopifnot(!anyDuplicated(r$id), all(d$id %in% r$id))
d <- merge(d, r, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zhirkov_2025_immigrant_illegality.csv"))
