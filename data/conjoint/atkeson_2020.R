##School board candidate conjoint (MTurk) from
##Atkeson, L. R., & Hamel, B. T. (2020). Fit for the job: Candidate qualifications and vote choice
##in low information elections. Political Behavior, 42(1), 59-82.
##https://doi.org/10.1007/s11109-018-9486-0
##Replication data: Harvard Dataverse doi:10.7910/DVN/1HPT9N, CC0 1.0. File read: mturk_dta.tab
##(Dataverse "original format" download, a CSV). The authors' mturk_replication.R was read as text,
##not run. The deposit's other file (caschool_dta, California school board election returns) is
##observational and not a conjoint. The article (paywalled) was not read.
##Usage: Rscript atkeson_2020.R <dir holding mturk_dta.csv> <output dir>
##
##atkeson_2020_school_board: 1,500 MTurk respondents, 3 tasks of 2 hypothetical school board
##  candidates (candoption 1-6 numbers the 6 profiles in display order; profile = 1 for the first
##  of each pair). 5 attributes, level text as in the deposit: occupation (Attorney, Business
##  Owner, School Guidance Counselor, School Janitor, School Teacher), party (Democrat,
##  Republican, No Party), incumbent (Yes / No), race (Asian, Black or African-American, Hispanic
##  or Latino, White), gender (Female / Male). How the screen worded the attribute rows (and
##  whether race and gender were shown as words) is not documented in the deposit.
##  Outcome: choice = vote, which of the two candidates the respondent would vote for (exact
##  wording in the article, not the deposit). Forced choice, no opt-out: one chosen in every task.
##  Attribute order and randomization restrictions not documented.
##  Covariates (text as answered unless noted): cov_birth_year (born), cov_gender (female / male /
##  other, from the deposit's own answer text in mturk_dta.csv gender: Female, Male, "Other [Please
##  Specify]:"), cov_race, cov_income, cov_education (answer text), cov_party_id (party: Democrat,
##  Independent, Republican, "Other [Please Specify]:"), cov_party_strength (Strong/Weak,
##  partisans only), cov_party_lean (independents only), cov_ideology. Blank answers are left
##  empty. No survey weight in the deposit.
##  Dropped: mturk_ids_rep (Qualtrics ResponseId; ids re-keyed to integers in file order), the
##  free-text "other" fields (gender_other, race_other, education_other, party_other), and the
##  authors' derived shared_party / Candidate-Respondent Party.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "mturk_dta.csv"), na.strings = NULL)
stopifnot(nrow(s) == 9000, s[, .N, mturk_ids_rep][, all(N == 6)], all(s$candoption == 2L * s$choicetask - 1L | s$candoption == 2L * s$choicetask))
s[, id := match(mturk_ids_rep, unique(mturk_ids_rep))]
d <- s[, .(id, task = as.integer(choicetask), profile = as.integer(candoption - 2L * (choicetask - 1L)), choice = as.integer(vote),
           attr_occupation = occup_profile, attr_party = party_profile, attr_incumbent = incumb_profile,
           attr_race = race_profile, attr_gender = gender_profile,
           cov_birth_year = suppressWarnings(as.integer(born)),
           cov_gender = unname(c(Female = "female", Male = "male", "Other [Please Specify]:" = "other")[gender]), cov_race = race, cov_income = income,
           cov_education = education, cov_party_id = party, cov_party_strength = party_strength, cov_party_lean = party_indep,
           cov_ideology = ideology)]
for (v in grep("^cov_", names(d), value = TRUE)) if (is.character(d[[v]])) set(d, which(d[[v]] == ""), v, NA_character_)
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 1500)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "atkeson_2020_school_board.csv"))
