##Ukraine-support strategy conjoint (France, Germany, Italy, United Kingdom) from
##Rudolph, L., Haggerty, F., & Thurner, P. W. (2026). Examining public support for Ukraine's
##defense against autocratic aggression. Nature Communications, 17.
##https://doi.org/10.1038/s41467-025-67913-z
##Replication data: Harvard Dataverse doi:10.7910/DVN/UDBPS1, CC0 1.0, no restricted files.
##Files read: ukr_conjoint_replication_data.dta (long conjoint file; Dataverse "original format"
##download, saved as ukr.dta) and ukr_master_and_vignette_replication_data.dta (one row per
##respondent, saved as master.dta; covariates only). readme.txt and ukr_data_preparation.do
##(read as text): the conjoint file is the master reshaped long with id = master row number
##(checked: ID, Country and W8 agree on every row).
##Usage: Rscript rudolph_2026_western.R <dir holding ukr.dta and master.dta> <output dir>
##
##US RESPONDENTS ARE NOT INCLUDED. The same survey (YouGov, June 14 - August 28 2023, same
##9-attribute design) supplied the US sample already in IRW as rudolph_2026_ukraine_support
##(Rudolph 2026, POQ; 2,334 US respondents from yougov_master.dta); the 2,003 US respondents
##here are very probably a subset of those (the ids cannot be linked). This table keeps the
##other four countries: Germany 2,003, Italy 2,001, United Kingdom 2,002, France 2,002 =
##8,008 respondents (the article: 10,011 in five countries). The authors pool the countries
##(country fixed effects / interactions), the attributes are the same, so one table with
##cov_country.
##4 tasks of 2 "strategies" to end the war, 9 attributes. Level text is the authors' English
##labels (.dta value labels = ukr_data_preparation.do "conjoint attribute labels"), the same
##labels as rudolph_2026_ukraine_support; respondents saw German, French, Italian or English
##text (master questionnaire with the OSF pre-registration doi:10.17605/OSF.IO/TVZSA, not
##read). The two aid attributes are "[Country] contribution to military/economic aid" as a
##share of GDP (the US version showed a dollar amount too; whether these did is not known).
##The article: "three to four uniformly randomized levels"; attribute order block-randomized
##within dimensions (not recorded).
##task = the source's task (screen 1-4), profile = concept (1 = Strategy A, 2 = Strategy B).
##trial_task_no = UKR_ROUND2_task<k>, as in rudolph_2026_ukraine_support.
##Outcome: choice: "Wenn Sie sich zwischen einer der beiden Strategien entscheiden müssten,
##..." (German master label, cut in the .dta; the US version reads "If you had to choose
##between one of the two strategies, which would you personally prefer?"), forced, no opt-out.
##NOT included: the 1-7 rating of each strategy (Q12B_, asked in 2 of the 4 tasks). The US
##version randomized the scale endpoints and the author reversed half of the answers; this
##deposit has no scale-order variable and no value labels for Q12B, so whether these values
##are already aligned is not documented (they agree with the choice in about 88% of untied
##tasks, which suggests they are). Ben may decide to add it.
##Covariates: cov_country (Country value labels in English: Deutschland -> "Germany",
##Italia -> "Italy", the UK -> "United Kingdom", France -> "France"), cov_gender (gender:
##männlich -> male, weiblich -> female), cov_age (age, years), cov_education_level (education:
##the master's harmonized "Low/Medium/High education", text), cov_party_id (partyID_DE/_FR/
##_IT/_UK value-label text in the survey language; Skipped/Not Asked -> NA), cov_survey_weight
##(W8, "Weight"). Dropped: postcode (master.dta; PII), the authors' rescaled left-right
##(leftright11, "Rescaled (1-11)", derived from country scales), PCA scores and split
##indicators, open answers.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "ukr.dta"))))
m <- read_dta(file.path(raw, "master.dta"),
              col_select = c("ID", "Country", "W8", "age", "gender", "education", "partyID_DE", "partyID_FR", "partyID_IT", "partyID_UK"))
stopifnot(nrow(s) == 80088L, all(s$ID == as.numeric(zap_labels(m$ID))[s$id]), all(s$Country == as.numeric(zap_labels(m$Country))[s$id]))
s <- s[Country %in% 1:4]
lab <- list(c("12,500", "25,000", "50,000"), c("25,000", "50,000", "100,000"), c("4,000", "8,000", "16,000"),
            c("$50B", "$100B", "$200B"), c("0.1% of GDP", "0.2% of GDP", "0.3% of GDP"),
            c("0.1% of GDP", "0.2% of GDP", "0.3% of GDP"), c("Not present (0%)", "Low (5%)", "Moderate (10%)"),
            c("None", "Crimea (4%)", "2014 LoC (8%)", "2023 LoC (16%)"), c("Full", "No EU/NATO", "Russian influence"))
anm <- c("ukr_soldiers_killed", "rus_soldiers_killed", "ukr_civilians_killed", "infrastructure_destroyed",
         "military_aid", "economic_aid", "nuclear_risk", "territorial_cessions", "self_determination")
d <- s[, .(id = as.integer(id), task = as.integer(task), profile = as.integer(concept), choice = as.integer(choice))]
for (k in 1:9) {
  v <- s[[sprintf("q2_attr%d_concept_task", k)]]
  stopifnot(all(v %in% seq_along(lab[[k]])))
  d[, paste0("attr_", anm[k]) := lab[[k]][v]]
}
tn <- as.matrix(s[, paste0("UKR_ROUND2_task", 1:4), with = FALSE])
d[, trial_task_no := as.integer(tn[cbind(seq_len(.N), task)])]
txt <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y[y %in% c("Skipped", "Not Asked")] <- NA; y }
ctry <- as.integer(zap_labels(m$Country)); pid <- rep(NA_character_, nrow(m))
for (k in 1:4) { v <- c("partyID_DE", "partyID_IT", "partyID_UK", "partyID_FR")[k]; pid[ctry == k] <- txt(m[[v]])[ctry == k] }
g <- as.integer(zap_labels(m$gender)); stopifnot(all(g %in% 1:2))
ag <- as.integer(zap_labels(m$age)); ag[ag < 18] <- NA
r <- d$id
d[, `:=`(cov_country = c("Germany", "Italy", "United Kingdom", "France")[ctry[r]], cov_gender = c("male", "female")[g[r]],
         cov_age = ag[r], cov_education_level = txt(m$education)[r], cov_party_id = pid[r],
         cov_survey_weight = as.numeric(m$W8)[r])]
stopifnot(d[, .(sum(choice), .N), .(id, task)][, all(V1 == 1 & N == 2)], d[, uniqueN(id)] == 8008L)
stopifnot(d[, uniqueN(trial_task_no), id][, all(V1 == 4)])
d[, id := match(id, sort(unique(id)))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "rudolph_2026_ukraine_western.csv"))
