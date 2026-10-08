##COVID-19 vaccine choice-based conjoint from
##Kreps, S., Prasad, S., Brownstein, J. S., Hswen, Y., Garibaldi, B. T., Zhang, B., &
##Kriner, D. L. (2020). Factors associated with US adults' likelihood of accepting
##COVID-19 vaccination. JAMA Network Open, 3(10), e2025594.
##https://doi.org/10.1001/jamanetworkopen.2020.25594
##Replication data: Harvard Dataverse doi:10.7910/DVN/6BSJYP, CC0 1.0. File read:
##Kreps_etal_vax_replication_data.dta (Dataverse "original format" download).
##Usage: Rscript kreps_2020.R <dir holding the .dta> <output dir>
##
##1,971 Lucid respondents, 5 tasks of 2 hypothetical vaccines, 7 attributes.
##choice_set encodes task*10 + profile. Outcomes:
##  choice  = vaxbin. The question offered "Vaccine A", "Vaccine B" or "I would choose not
##            to get either vaccine": 2,071 of 9,855 tasks are opt-outs, with choice = 0
##            on both profiles.
##  rating  = vaxord, "How likely or unlikely would you be to get Vaccine A/B", 7-point,
##            7 = extremely likely (the authors' .do file treats 5-7 as willing).
##The FDA attribute's two long texts are shortened to "approved and licensed" and
##"emergency use authorization". Respondent covariates keep the source's numeric codes
##(labels in the .dta), except: cov_gender (gender, "What is your gender?": 1 Male = male,
##2 Female = female, 3 Prefer not to say = missing; .dta value labels and survey PDF p. 14-15),
##cov_education (education, .dta value-label text: Less than High School, High School / GED,
##Some College, 2-year College Degree, 4-year College Degree, Master's Degree, Doctoral Degree,
##Professional Degree), cov_party_id (party3, "In politics, as of today, do you consider
##yourself a Republican, a Democrat, or an Independent?", .dta value-label text: Republican,
##Democrat, Independent, Other/don't know); cov_party_lean keeps its codes (1 Democratic Party,
##2 Republican Party, 3 Neither/don't know). Age is converted from code (1 = 18) to years.
##No survey weight in the .dta. The consent item
##and the authors' derived dummies (*_n, efficacy1, dem3, ...) are dropped.
##From this table the paper's 9 reported choice AMCEs (with 95% CIs) and 9 willingness
##marginal means reproduce exactly.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "Kreps_etal_vax_replication_data.dta"))
d <- data.table(id = as.integer(k$respondent), task = as.integer(k$choice_set) %/% 10L,
                profile = as.integer(k$choice_set) %% 10L, choice = as.integer(k$vaxbin), rating = as.integer(k$vaxord))
for (v in c("efficacy", "duration", "majorside", "minorside", "fda", "origin", "endorsed")) d[, paste0("attr_", v) := as.character(k[[v]])]
d[attr_fda %like% "emergency", attr_fda := "emergency use authorization"][attr_fda %like% "approved and licensed", attr_fda := "approved and licensed"]
kcov <- c("work_status", "work_home", "personal_contact1", "personal_contact2", "covid_future", "covid_fed_approve", "covid_china",
          "flu_vaccine", "vaccine_safety", "mandatory_vax", "insurance", "pharma", "ideology", "party3", "party_lean", "pres_approval",
          "gender", paste0("race_", 1:6), "income", "education", "relig", "evangelical", "state")
for (v in kcov) d[, paste0("cov_", v) := as.integer(zap_labels(k[[v]]))]
stopifnot(all(d$cov_gender %in% 1:3), all(d$cov_education %in% 1:8), all(d$cov_party3 %in% 1:4))
d[, cov_gender := c("male", "female", NA)[cov_gender]]
d[, cov_education := as.character(as_factor(k$education, levels = "labels"))]
d[, cov_party3 := as.character(as_factor(k$party3, levels = "labels"))]
setnames(d, "cov_party3", "cov_party_id")
d[, cov_age := as.integer(zap_labels(k$age)) + 17L]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kreps_2020_covid_vaccine.csv"))
