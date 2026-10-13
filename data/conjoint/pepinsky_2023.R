##Refugee gender x country-of-origin survey experiment (Hungary, November 2022) from
##Pepinsky, T. B., Reiff, A., & Szabo, A. (2023). The Ukrainian refugee crisis and the politics of public opinion:
##evidence from Hungary. OSF preprint. https://doi.org/10.31219/osf.io/4mvc6
##Replication data: Harvard Dataverse doi:10.7910/DVN/A83JTQ, CC0 1.0, no restricted files. File read:
##omni2211_workfile.dta (Dataverse "original format" download of omni2211_workfile.tab; TARKI Omnibus, interviews
##18-29 Nov 2022, n = 1,000), replication_file_..._Sections_1_2_3_4_5.do (as text; Table 5, Figure 10).
##Usage: Rscript pepinsky_2023.R <dir holding n11.dta> <out dir>
##
##Each respondent was asked ONE question with two randomized parts (the file's "random numbers" male_femaleNUM and
##afg_ukrNUM): who is admitted (male / female and children) and from where (Afghanistan / Ukraine); a 2 x 2
##between-subject vignette, one task, one profile, id = interview number (number). Level text = value labels of the
##two randomization variables (the Hungarian wording is not in the deposit).
##Outcome: rating = m_afgukrGENDER "Gov should allow the entry of male/female from AFG/UKR", 1 Strongly disagree,
##2 Disagree, 3 Neither agree nor disagree, 4 Agree, 5 Strongly agree (value labels). Higher = more support for entry.
##"Does not know" (88, n = 15) and "Refuse to answer" (99, n = 1) are dropped (no rating): 984 respondents.
##Covariates: cov_gender (gender: 1 male, 2 female), cov_age (age), cov_education (educ value-label text),
##cov_survey_weight (weight, the TARKI 4-dimension weight used in the authors' regressions).
##Dropped: the other split-ballot items in the file (Afghan/Pakistani and Ukrainian/Belarusian source-country items,
##importance-of-characteristics items), vote choice, geography below region, derived dummies. The merged
##historical file (omni2211_EN_withTARKI_final.tab) and the April 2022 wave (impwhite / impvalue importance
##questions: each respondent asked one characteristic, not a profile) are not built.
##Count check: n = 1,000 as in the readme; paper's Table 5 uses m_afgukrGENDER100 = (rating - 1) * 25.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "n11.dta"))
stopifnot(nrow(s) == 1000, !anyDuplicated(s$number), all(s$male_femaleNUM %in% 1:2), all(s$afg_ukrNUM %in% 1:2))
lab <- function(v) as.character(as_factor(s[[v]], levels = "labels"))
r <- as.integer(s$m_afgukrGENDER)
d <- data.table(id = as.integer(s$number), task = 1L, profile = 1L, rating = ifelse(r %in% 1:5, r, NA_integer_),
  attr_refugee_group = c("male", "female and children")[s$male_femaleNUM],
  attr_origin = c("Afghanistan", "Ukraine")[s$afg_ukrNUM],
  cov_gender = c("male", "female")[as.integer(s$gender)], cov_age = as.integer(s$age),
  cov_education = lab("educ"), cov_survey_weight = as.numeric(s$weight))
d <- d[!is.na(rating)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pepinsky_2023_refugee_gender.csv"))
