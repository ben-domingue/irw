##Asylum-seeker conjoint (15 European countries) from
##Bansak, K., Hainmueller, J., & Hangartner, D. (2016). How economic, humanitarian, and
##religious concerns shape European attitudes toward asylum-seekers. Science, 354(6309),
##217-222. https://doi.org/10.1126/science.aag2147
##Replication data: Harvard Dataverse doi:10.7910/DVN/KL0FDF, CC0 1.0. Files read:
##conjoint_data_final.csv and respondent_data_final.csv (Dataverse "original format"
##downloads), with conjoint_variable_codebook.pdf and respondent_variable_codebook.pdf
##for the level labels. ConjointRegressions.R was read as text, not run.
##Usage: Rscript bansak_2016.R <dir holding the two .csv files> <output dir>
##
##bansak_2016_asylum: online survey of eligible voters in 15 European countries (Austria,
##  Czech Republic, Denmark, France, Germany, Greece, Hungary, Italy, Netherlands, Norway,
##  Poland, Spain, Sweden, Switzerland, United Kingdom; about 1,200 each), fielded 2016.
##  ONE TABLE with cov_country: the same design (same 9 attributes and levels, translated)
##  was fielded in every country, and the deposit stores only the English master labels,
##  so splitting by country would not change what attr_* hold. Each respondent saw 5
##  pairs of asylum-seeker profiles (10 profiles; source "mix" A..J = task 1 profile 1,
##  task 1 profile 2, task 2 profile 1, ...). attr_* hold the codebook's English level
##  labels; the language attribute was shown with the respondent's national language in
##  place of the codebook's "[language of respondent's country]", which is kept verbatim
##  because the deposit does not say which language was named in multilingual countries.
##  The deposit does not record attribute order or document randomization restrictions.
##  Outcomes: choice = pref (1 = the preferred profile of the pair; forced choice, no
##  opt-out) and rating = rate (1-7 "degree of support" for granting asylum, per the
##  codebook; higher = more supportive, raw scale kept). The exact question wording is in
##  the article's Supplementary Materials, which are not in the deposit and were not
##  retrieved. The authors' derived ratebin and ratescaled are dropped.
##  9 respondents (90 profiles) have no attribute levels at all in the deposit and are
##  dropped (the authors drop them too), leaving 18,021 respondents; the paper reports
##  18,000 voters (a round number) and 180,000 profiles.
##  Covariates: cov_country (text), cov_survey_weight (entropy-balancing post-stratification
##  weight, NA for 147 respondents with missing education; the authors top-code it at 6
##  for analysis, it is kept raw here), cov_home_born (1 = born in country), cov_asylum_home
##  (-2 greatly decrease ... 2 greatly increase the number granted asylum), cov_ideology
##  (0 left - 10 right), cov_party_id (country-specific party code, listed in the
##  respondent codebook), cov_empathy1 (empathic concern, -6..6), cov_empathy2 (perspective
##  taking, -6..6), cov_female (1 = female), cov_age (years), cov_employment (1 paid
##  employee, 2 self-employed, 3 student, 4 unemployed searching, 5 unemployed not
##  searching, 6 chronic illness/disability, 7 retired, 8 working at home), cov_eisced
##  (education, European ISCED), cov_income_decile.
##  Dropped: Qualtrics respid (re-keyed to the deposit's integer id), survey duration, the
##  party's Chapel Hill placement (lrgen, an external score), and derived bins/dummies/
##  counts (L/C/R, Ideo5, OldAge, AgeGroup, HighEducation, Empathy sum, NAsySeek*, Cat*).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cj <- fread(file.path(raw, "conjoint_data_final.csv")); rs <- fread(file.path(raw, "respondent_data_final.csv"))
cj <- cj[!is.na(cconsist)]
k <- match(cj$mix, LETTERS[1:10]); stopifnot(!anyNA(k))
d <- data.table(id = as.integer(cj$id), task = (k + 1L) %/% 2L, profile = 2L - k %% 2L,
                choice = as.integer(cj$pref), rating = as.integer(cj$rate))
labs <- list(
  consistency = c("No inconsistencies", "Minor inconsistencies", "Major inconsistencies"),
  gender = c("Female", "Male"),
  origin = c("Syria", "Afghanistan", "Kosovo", "Eritrea", "Pakistan", "Ukraine", "Iraq"),
  age = c("21 years", "38 years", "62 years"),
  occupation = c("Unemployed", "Cleaner", "Farmer", "Accountant", "Teacher", "Doctor"),
  vulnerability = c("None", "Post-traumatic stress disorder (PTSD)", "Victim of torture", "No surviving family members", "Physically handicapped"),
  reason = c("Persecution for political views", "Persecution for religious beliefs", "Persecution for ethnicity", "Seeking better economic opportunities"),
  religion = c("Christian", "Agnostic", "Muslim"),
  language = c("Speaks fluent [language of respondent's country]", "Speaks broken [language of respondent's country]", "Speaks no [language of respondent's country]"))
src <- c(consistency = "cconsist", gender = "cgender", origin = "corigin", age = "cage", occupation = "cjob",
         vulnerability = "cvulner", reason = "creason", religion = "creligion", language = "clang")
for (v in names(src)) { x <- labs[[v]][cj[[src[[v]]]]]; stopifnot(!anyNA(x)); d[, paste0("attr_", v) := x] }
r <- rs[, .(id, cov_country = cty, cov_survey_weight = weight, cov_home_born = HomeBorn, cov_asylum_home = AsylumHome,
            cov_ideology = IdeoScale, cov_party_id = PartyID, cov_empathy1 = Empathy1, cov_empathy2 = Empathy2,
            cov_female = Female, cov_age = Age, cov_employment = as.integer(sub("\\..*", "", EmpStatus)),
            cov_eisced = EISCED, cov_income_decile = IncomeDecile)]
stopifnot(!anyNA(r$cov_employment), uniqueN(r$id) == nrow(r))
d <- merge(d, r, by = "id", all.x = TRUE); stopifnot(!anyNA(d$cov_country))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bansak_2016_asylum.csv"))
