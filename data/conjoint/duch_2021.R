##COVID-19 vaccine prioritisation conjoint (13 countries) from
##Duch, R., Roope, L. S. J., Violato, M., Fuentes Becerra, M., Robinson, T. S., Bonnefon, J.-F.,
##Friedman, J., Loewen, P. J., Mamidi, P., Melegaro, A., Blanco, M., Vargas, J., Seither, J.,
##Candio, P., Gibertoni Cruz, A., Hua, X., Barnett, A., & Clarke, P. M. (2021). Citizens from 13
##countries share similar preferences for COVID-19 vaccine allocation priorities. Proceedings of
##the National Academy of Sciences, 118(38), e2026382118. https://doi.org/10.1073/pnas.2026382118
##Data: nbh_clean_conjoint_global.rds, deposited twice on Harvard Dataverse, both CC0 1.0 and
##byte-identical (MD5 39df0612f62f92d65d8b91f41ee3237f): the original replication deposit
##doi:10.7910/DVN/PMV0TG and the re-host in Robinson & Duch, "How to detect heterogeneity in
##conjoint experiments" (doi:10.7910/DVN/CG9VPE, the deposit this script was screened from). The
##original study's deposit governs and is cited. Also read: codebook.pdf (both deposits),
##"Qualtrics Vaccine Survey - UK - English.pdf" and data_formatting.R (PMV0TG, read as text).
##Usage: Rscript duch_2021.R <dir holding nbh_clean_conjoint_global.rds> <output dir>
##
##15,536 respondents in 13 countries (Australia, Brazil, Canada, Chile, China, Colombia, France,
##India, Italy, Spain, Uganda, UK, US; online samples, CANDOUR project, late 2020), 8 tasks of 2
##hypothetical people (Person A / Person B), 5 attributes. One table with cov_country: the authors
##pool the countries (data_formatting.R stacks them; the paper's pooled model) and the attribute
##text is shared (stored in English). task = `person` (round 1-8), profile = `candidate` (A = 1,
##B = 2); both recorded.
##Outcome: choice = select. UK wording (Q5.3): "Which of the Persons do you think should get the
##vaccine immediately? Select one of them." Person A / Person B, forced choice, no opt-out.
##The questionnaire also asked a 1-7 priority rating of each person (Q5.5/Q5.6, "Very Low
##Priority" - "Very High Priority"), but the deposited data do not contain it.
##Attribute text: the English level text in the data (e.g. "Moderate (Twice the average risk of
##COVID-19 death)", "Key worker: Health and social care", "79 years old"). Respondents outside the
##English-speaking samples saw translated versions that are not deposited; which language each
##country's survey used is not documented beyond the UK English questionnaire. Attribute order and
##randomization restrictions are not documented.
##Covariates (as in the data, English text where the source has text): cov_country, cov_age,
##cov_gender, cov_ideology (0 left - 10 right; not asked in China), cov_income (High/Low relative
##to the country median), cov_education (High/Medium/Low relative to the country),
##cov_side_effect_concern ("I am concerned about serious side effects of the COVID-19 vaccine",
##5-point text + "Do not know"), cov_vaccine_access and cov_pay_privately (text),
##cov_mandatory_vaccine (int_pol_implem_6, 0-100), cov_survey_weight (`weights`; 1 for every
##respondent in Canada, Spain, Uganda and India, where data_formatting.R sets no weights).
##Dropped: `ans` (the chosen letter, duplicates select). Source ids ("Canada_1") are re-keyed to
##integers in order of country and number.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "nbh_clean_conjoint_global.rds")))
stopifnot(nrow(s) == 248576, uniqueN(s$id) == 15536)
key <- unique(s[, .(id, country)])[, n := as.integer(sub(".*_", "", id))][order(country, n)][, k := .I]
d <- s[, .(id = key$k[match(id, key$id)], task = as.integer(sub("person", "", person)), profile = match(candidate, c("A", "B")),
           choice = as.integer(select),
           attr_vulnerability = as.character(vulnerability), attr_transmission = as.character(transmission),
           attr_income = as.character(income), attr_occupation = as.character(occupation), attr_age = as.character(age_category),
           cov_country = country, cov_age = age, cov_gender = gender, cov_ideology = ideology, cov_income = ind_inc,
           cov_education = education, cov_side_effect_concern = hes_covid_2, cov_vaccine_access = wtp_access,
           cov_pay_privately = wtp_private, cov_mandatory_vaccine = int_pol_implem_6, cov_survey_weight = weights)]
stopifnot(!anyDuplicated(d[, .(id, task, profile)]), d[, .N, id][, all(N == 16)])
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$choice == as.integer(s$ans == s$candidate)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "duch_2021_vaccine_priority.csv"))
