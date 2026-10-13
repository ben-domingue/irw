##Factorial vignette on international vaccine solidarity (Germany, May 2021) from
##Leuffen, D., Mounchid, P. M., Heermann, M., & Koos, S. (2023). Mobilizing domestic support for international vaccine
##solidarity: recommendations for health crisis communication. npj Vaccines, 8.
##https://doi.org/10.1038/s41541-023-00625-x
##Replication data: Harvard Dataverse doi:10.7910/DVN/6KJHSN, CC0 1.0. File read: data.tab (DDI
##variable labels read from the Dataverse DDI export, datafile 6903180). code.Rmd read as text.
##Usage: Rscript leuffen_2023.R <dir holding data.tab> <output dir>
##
##4,022 respondents of the Respondi online access panel (quota sample on age, gender, education, region),
##one vignette each (task 1, profile 1; one row per respondent). A hypothetical recipient country in need of
##vaccines is described by five randomized attributes (levels = the DDI value labels, English; respondents
##saw German text, which the deposit does not hold):
##  demok   political system of the destination country: Autocracy / Democracy
##  geo     geographic proximity: Neighbouring country EU / Latin-American country
##  kontrol Covid-19 policy of the destination country: Slow / Fast implementation of Covid-Policies
##  need    medical situation: Strained medical situation / Moderate medical condition
##  kosten  herd immunity in the EU: Herd immunity impending / Herd immunity far away
##A sixth randomized factor, the information treatment (an explanation of the medical logic of vaccine
##solidarity, shown before the vignette), is not an attribute of the described country: kept as
##trial_info_treatment (Treatmentgroup / Controlgroup), not as attr_.
##Outcome: rating = Selection, support for sending vaccines to the country, 7-point, 1 'I do not support at
##all' to 7 'I fully support' (paper text; the deposit gives no value labels for it). Higher = more support.
##Not a choice among profiles. Attribute and treatment coding: 1/2 codes mapped through the DDI value labels.
##Restrictions: none documented; all 2^6 cells occur (49-93 respondents each) so level_weights 'uniform' is not
##asserted by a source (shares 0.49-0.51).
##Covariates kept: cov_gender (Gender, 'Sind Sie...': 1 maennlich = male, 2 weiblich = female, 3 divers = other,
##DDI labels), cov_age (Age), cov_birth_year (stat2), cov_education_group (stat3_gr3, 1/2/3 = Low/Middle/High,
##the authors' recode in code.Rmd), cov_survey_weight (gewichtRespondi), cov_altruism (Altruism_1, 1-7 agree),
##cov_leftright_code (inst3, codes). Dropped: other demographics and state, income, vaccination state, patent
##item (not needed), derived age group (stat2_gr5). Respondent ID is a survey case number (re-keyed 1..n in row order).
##Count check: the paper reports n = 4,022 (treatment 1,974, control 2,048): both reproduce.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "data.tab"))
lv <- function(x, m) unname(m[as.character(x)])
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, rating = as.integer(k$Selection))
d[, attr_political_system := lv(k$Demok, c("1" = "Autocracy", "2" = "Democracy"))]
d[, attr_geographic_proximity := lv(k$Geo, c("2" = "Neighbouring country EU", "1" = "Latin-American country"))]
d[, attr_covid_policy := lv(k$Kontrol, c("1" = "Slow implementation of Covid-Policies", "2" = "Fast implementation of Covid-Policies"))]
d[, attr_medical_situation := lv(k$Need, c("2" = "Strained medical situation", "1" = "Moderate medical condition"))]
d[, attr_herd_immunity_eu := lv(k$Kosten, c("2" = "Herd immunity impending", "1" = "Herd immunity far away"))]
d[, trial_info_treatment := lv(k$Treatment, c("2" = "Treatmentgroup", "1" = "Controlgroup"))]
d[, cov_gender := lv(k$Gender, c("1" = "male", "2" = "female", "3" = "other"))]
d[, cov_age := as.integer(k$Age)]
d[, cov_birth_year := as.integer(k$stat2)]
d[, cov_education_group := lv(k$stat3_gr3, c("1" = "Low", "2" = "Middle", "3" = "High"))]
d[, cov_survey_weight := k$gewichtRespondi]
d[, cov_altruism := as.integer(k$Altruism_1)]
d[, cov_leftright_code := as.integer(k$inst3)]
stopifnot(!anyNA(d[, .(rating, attr_political_system, attr_geographic_proximity, attr_covid_policy, attr_medical_situation, attr_herd_immunity_eu)]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "leuffen_2023_vaccine_solidarity.csv"))
