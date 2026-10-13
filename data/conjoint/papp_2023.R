##COVID-19 vaccine choice conjoint, Hungary
##Papp, Z., & Nkansah, G. B. (2023). The political component of COVID-19 vaccine choice: Results from a
##conjoint experiment. Public Health, 217, 33-40. https://doi.org/10.1016/j.puhe.2023.01.014
##Replication data: figshare doi:10.6084/m9.figshare.21186319, CC BY 4.0. Files read: REPLICATION DATA.dta
##(saved as data.dta; value labels give the level text) and REPLICATION CODE.do (read as text; variable
##codebook in its header, lines 1-80). Usage: Rscript papp_2023.R <dir holding data.dta> <output dir>
##
##324 respondents of an online panel (Hungary, September 2022; quotas on vaccination status and party
##preference), 6 tasks of 2 hypothetical vaccines = 3,888 profiles (the paper's figure), 10 attributes
##(origin, EU authorization, trial phase, severe side effects, mild side effects, efficacy, doses, cost,
##availability, transmission). Forced choice, no opt-out (exactly one chosen profile in all 1,944 tasks).
##Outcome: choice = the vaccine selected in the task (do-file: "The respondent selected the vaccine in a
##task"); the deposit has no questionnaire, so the question wording is a paraphrase.
##Level text = the Stata value labels, which are short forms of the codebook wording (e.g. severe side effects:
##"Not common", "Rare", "Extremely rare" for "Severe side effects are not common/rare/extremely rare").
##Label typos fixed: "No eductation" -> "No education", "10000HUF" -> "10000 HUF". Task_n and Profile_n are recorded
##(rank of the task 1-6 and of the profile 1-2); rows in the file are shuffled and are sorted here.
##Randomization restrictions and attribute-order randomization are not documented.
##Covariates: cov_gender (labels Male/Female), cov_age (years), cov_education (value-label text),
##cov_residency (label text), cov_family (label text), cov_income (1-11, 1 very low - 11 very high),
##cov_religion (1-11, how religious, larger = stronger), cov_polint (1-11, political interest, larger = more),
##cov_riskofcovid (1-11, likelihood of contracting COVID in the next 6 months, 11 = very likely),
##cov_gotcovid (Prior infection / No prior infection), cov_vaccinated (Not vaccinated / At least 1 jab),
##cov_vote_side (the authors' coding of party preference: Government parties / Opposition parties).
##Dropped: nothing else (no identifiers in the file; Panelist_id re-keyed to integers).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "data.dta")))
lab <- function(v) as.character(as_factor(x[[v]], levels = "labels"))
d <- data.table(id = as.integer(factor(x$Panelist_id)), task = as.integer(x$Task_n), profile = as.integer(x$Profile_n), choice = as.integer(x$choice))
for (v in c("origin", "euauthorization", "trialphase", "severe", "mild", "efficacy", "doses", "cost", "availability", "transmission")) d[, paste0("attr_", v) := lab(v)]
d[attr_cost == "10000HUF", attr_cost := "10000 HUF"]
d[, cov_gender := tolower(lab("gender"))]
d[, cov_age := as.integer(x$age)]
d[, cov_education := sub("No eductation", "No education", lab("education"), fixed = TRUE)]
d[, cov_residency := lab("residency")][, cov_family := lab("family")]
for (v in c("income", "religion", "polint", "riskofcovid")) d[, paste0("cov_", v) := as.integer(zap_labels(x[[v]]))]
d[, cov_gotcovid := c("Prior infection", "No prior infection")[as.integer(x$gotcovid)]]
d[, cov_vaccinated := c("Not vaccinated", "At least 1 jab")[as.integer(x$vaccinated) + 1L]]
d[, cov_vote_side := c("Opposition parties", "Government parties")[as.integer(x$winner) + 1L]]
stopifnot(uniqueN(d$id) == 324, nrow(d) == 3888, d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "papp_2023_covid_vaccine_hungary.csv"))
