##Income- and inheritance-tax plan conjoint (England and Wales) from
##Elkjaer, M. A., Ansell, B., Bokobza, L., Cansunar, A., Haslberger, M., & Nyrup, J. (2025). Why is it so hard
##to counteract wealth inequality? Evidence from the United Kingdom. World Politics, 77(3), 515-561.
##https://doi.org/10.1353/wp.2025.a964464
##Replication data: Harvard Dataverse doi:10.7910/DVN/L6HYCL, CC0 1.0. File read: df_conjoint.rds
##(100 MB, one tibble, 31,860 rows x 277 columns; read with readRDS). Authors' code 01_mainanalysis.R read as text.
##Usage: Rscript elkjaer_2025.R <dir holding df_conjoint.rds> <output dir>
##
##3,186 adults in England and Wales (online survey, May-June 2021; weight w8 kept), 5 tasks x 2 plans (A/B).
##Each plan is a tax schedule: four income-tax rates (one per income band) and four inheritance-tax rates (one per
##inheritance band); 8 attributes. Level text is the deposit's own ("<GBP125k: 10%" style, with the pound sign).
##Task = `table` (1-5), profile = `plan` (A=1, B=2), both recorded. Two choices on the same rows:
##  choice: chose_plan (which plan the respondent prefers on the income-tax rates; forced, one per task)
##  choice_inheritance: chose_plan_inh (same for the inheritance-tax rates; forced, one per task; the authors' AMCEs).
##The questionnaire is not in the deposit: that both attribute sets appear on one plan, and the exact wording of
##the two questions, are INFERRED from the row structure and variable names (outcome wording is a paraphrase).
##Opt-out: none (exactly one plan chosen per task on each question, checked).
##Randomization: rates drawn per band; all level combinations occur, no restriction documented. Attributes have 3-6
##levels; shares within an attribute are near-equal (no source gives probabilities). Attribute order not documented.
##Covariates: cov_age (age in years, as recorded), cov_gender (text Female/Male -> female/male),
##cov_education (education_code text, as stored), cov_survey_weight (w8). trial_info_treatment = arm of the
##information treatment (factor_qtreatment: Control / National / National+local), assigned per respondent.
##Dropped: start/end times, constituency/MP/local-authority and house-price fields, all other survey items,
##free-text answers (q26, q28, q30, q34: not kept), derived indicators and factors. No names/IPs/GPS found; the file
##holds free text and area names (dropped): no respondent identifiers kept. IDs are integers in the source.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "df_conjoint.rds")))
stopifnot(uniqueN(x$id) == 3186, nrow(x) == 31860)
d <- x[, .(id = as.integer(id), task = as.integer(table), profile = match(plan, c("A", "B")),
           choice = as.integer(chose_plan), choice_inheritance = as.integer(chose_plan_inh),
           attr_income_lt12_5k = income_gr1, attr_income_12_5k_50k = income_gr2, attr_income_50k_150k = income_gr3,
           attr_income_gt150k = income_gr4, attr_inheritance_lt125k = inheritance_gr1,
           attr_inheritance_125k_500k = inheritance_gr2, attr_inheritance_500k_1m = inheritance_gr3,
           attr_inheritance_gt1m = inheritance_gr4,
           cov_age = as.integer(age), cov_gender = tolower(gender), cov_education = education_code,
           cov_survey_weight = w8, trial_info_treatment = as.character(factor_qtreatment))]
stopifnot(!anyNA(d$profile), d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, sum(choice_inheritance), .(id, task)][, all(V1 == 1)])
stopifnot(d[, .N, .(id, task)][, all(N == 2)], all(d$cov_gender %in% c("female", "male")))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "elkjaer_2025_inheritance_tax.csv"))
