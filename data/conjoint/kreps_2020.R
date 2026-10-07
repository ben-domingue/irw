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
##(labels in the .dta); age is converted from code (1 = 18) to years. The consent item
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
d[, cov_age := as.integer(zap_labels(k$age)) + 17L]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kreps_2020_covid_vaccine.csv"))
