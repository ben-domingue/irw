##Immigrant-group partisanship vignette experiment (USA) from
##McDowell, D., & Steinberg, D. A. (2025). Do immigrants' partisan preferences influence Americans'
##support for immigration? Journal of Experimental Political Science.
##https://doi.org/10.1017/XPS.2025.10013 (open access; read)
##Replication data: Harvard Dataverse doi:10.7910/DVN/MFRCTU, CC0 1.0. File read:
##McDowell&Steinberg_JEPS_Dataset.dta (original Stata file, value labels). Read as text only: the
##ReadMe and McDowell&Steinberg_JEPS_Code.do.
##Usage: Rscript mcdowell_2025.R <dir holding the .dta> <output dir>
##
##Dynata online panel (quotas on gender, age, education), fielded to 1 November 2024, days before
##the presidential election; the article reports 3,000 subjects; 3,002 respondents have the
##outcome (2 rows have no assigned version and no answer and are dropped). Each respondent answered
##ONE question about immigration from one country (task = 1, profile = 1), a 2 x 2 factorial
##(hQ15Ver Q15A-D, 744-759 each; mapping from the authors' do-file: A = Venezuela/control,
##B = Venezuela/treatment, C = Vietnam/control, D = Vietnam/treatment). Exact text (article p. 4):
##"In the last ten years, a significant number of immigrants into the United States have come from
##[Vietnam/Venezuela]. [A majority of immigrants from [Vietnam/Venezuela] support Donald Trump and
##the Republican Party.] Do you agree or disagree that the United States should permit higher levels
##of immigration from [Vietnam/Venezuela]?" Both factors describe the evaluated immigrant group:
##  attr_origin        Vietnam / Venezuela
##  attr_partisanship  "A majority of immigrants from <country> support Donald Trump and the Republican
##                     Party." in the treatment arm; "(not shown)" in the control arm (the sentence was
##                     left out by design).
##Outcome: rating = Q15A-Dr1, agreement that the US should permit higher levels of immigration from
##the country, 0 = "strongly disagree" ... 10 = "strongly agree" (stored raw; higher = more support).
##id = row number of the source file (Dynata uuid, psid, rid and quality-analyzer ids are dropped).
##Covariates (answer text from the value labels): cov_gender (Q5 Male/Female/Other ->
##male/female/other), cov_birth_year (Q4), cov_age (dummy_QAGE, the panel's calculated age),
##cov_race (Q2), cov_education (Q3), cov_state (Q6), cov_household_income (Q13), cov_ideology (Q26r1,
##0-10 as stored; anchors truncated in the source), cov_party (Q27 text), cov_vote_intention (Q29),
##cov_manicheck (Q15E_New, which candidate the respondent thinks the group supports, asked after the
##outcome), cov_attention_pass (Q1 instruction check: 1 = "I understand", 0 otherwise),
##cov_survey_weight (dem_weights, the post-stratification weight used in the authors' robustness
##checks; 7 NA), cov_duration_sec (LOI, survey length in seconds).
##Dropped: platform/quality ids and scores, timestamps, attitude batteries Q20-Q25 (an embedded
##attention item among them), all derived dummies and interactions.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "McDowell&Steinberg_JEPS_Dataset.dta")))
stopifnot(nrow(s) == 3004L)
s[, id := .I]
s <- s[!is.na(hQ15Ver)]
v <- as.integer(s$hQ15Ver)
y <- s[, cbind(Q15Ar1, Q15Br1, Q15Cr1, Q15Dr1)][cbind(seq_along(v), v)]
stopifnot(nrow(s) == 3002L, !anyNA(y), rowSums(!is.na(s[, .(Q15Ar1, Q15Br1, Q15Cr1, Q15Dr1)])) == 1)
ctry <- fifelse(v %in% 3:4, "Vietnam", "Venezuela")
lab <- function(x) trimws(as.character(as_factor(x, levels = "labels")))
d <- data.table(id = s$id, task = 1L, profile = 1L, rating = as.integer(y),
  attr_origin = ctry,
  attr_partisanship = fifelse(v %in% c(2L, 4L), paste0("A majority of immigrants from ", ctry, " support Donald Trump and the Republican Party."), "(not shown)"),
  cov_gender = c(Male = "male", Female = "female", Other = "other")[lab(s$Q5)],
  cov_birth_year = as.integer(s$Q4), cov_age = as.integer(s$dummy_QAGE),
  cov_race = lab(s$Q2), cov_education = lab(s$education), cov_state = lab(s$Q6),
  cov_household_income = lab(s$income), cov_ideology = as.integer(s$ideology), cov_party = lab(s$Q27),
  cov_vote_intention = lab(s$Q29), cov_manicheck = lab(s$Q15E_New),
  cov_attention_pass = as.integer(s$Q1 == 1), cov_survey_weight = as.numeric(s$dem_weights),
  cov_duration_sec = as.numeric(s$LOI))
d[is.na(cov_vote_intention) | cov_vote_intention == "NA", cov_vote_intention := NA]
stopifnot(!anyNA(d$cov_gender), d$rating %in% 0:10, d[, .N, .(attr_origin, attr_partisanship)][, .N] == 4L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mcdowell_2025_immigrant_partisanship.csv"))
