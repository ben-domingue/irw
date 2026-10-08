##Global-governance-institution design conjoints (nonstate actor inclusion) from
##Ecker-Ehrhardt, M., Verhaegen, S., & Quack, S. (2025). Nonstate actor inclusion and the social
##legitimacy of global governance institutions. International Studies Quarterly, 69(2), sqaf040.
##https://doi.org/10.1093/isq/sqaf040
##Replication data: Harvard Dataverse doi:10.7910/DVN/CJAETN, CC0 1.0, no restricted files.
##File read: replication2.dta (Dataverse original; long file, one row per respondent x scenario x
##proposal). Replication_corrected.do read as text. Instrument and design: the article's online
##appendix (sqaf040_supplemental_file.docx, Appendix A questionnaire, English master version).
##replication1.dta (respondent covariates) was read but NOT used: it has no respondent id and its row
##order does not match replication2 (country and weight sequences differ), so it cannot be linked.
##replication3.dta (78 MB, WVS-based) not downloaded.
##Usage: Rscript eckerehrhardt_2025.R <raw dir> <output dir>
##
##Dynata online samples with census quotas in Brazil, Germany, South Africa and the US (21 Aug -
##29 Sep 2023), 12,059 respondents (3,037 / 3,010 / 3,011 / 3,001). Each did TWO experiments, in
##randomized block order, about a proposed new global organization: one on energy production and
##consumption, one on internet content moderation. Different object and attribute texts, so TWO
##TABLES (same respondents, same ids):
##  eckerehrhardt_2025_energy_governance, eckerehrhardt_2025_internet_governance.
##Countries are pooled in each table (cov_country), as in the authors' analysis (pooled AMCEs,
##country splits in the appendix); the attribute text is the same English master text.
##In each experiment the respondent first read a vignette with three between-subject factors
##(trial_government, trial_scope, trial_costs_benefits; per respondent and experiment), rated how
##much say each actor should have, then saw "three pairs of alternative proposals" (task 1-3:
##Proposal A/B, C/D, E/F = source Profile 1/2, 3/4, 5/6; profile 1 = A, C, E). Task and profile are
##recorded (Profile); task order = page order.
##Proposal table: "The proposals suggest giving the following groups a lot of say in all major
##decisions:" with one row per actor and Yes/No per proposal (Con_a1..Con_a4 = 1/0). Rows (energy /
##internet): "Energy companies" / "Internet companies"; "Scientists doing research on energy
##production and consumption" / "... on internet content moderation"; "Civil-society organizations
##dealing with energy production and consumption" / "... with internet content moderation";
##"Individual energy consumers" / "Individual internet users". Stored as attr_companies,
##attr_scientists, attr_csos, attr_citizens = "Yes"/"No". The 16 combinations were drawn at random
##(article: "randomly drawn from 16 possible combinations").
##Outcomes:
##  choice: "Which proposal do you find most appropriate?" (forced, two options, no opt-out).
##  rating: "How much confidence would you have in this new organization if created as proposed?",
##    7 points, shown from "A lot of confidence" to "None at all"; stored 1 = no confidence at all
##    .. 7 = a lot of confidence (article; chosen proposals average 4.8, others 3.3).
##trial_ fields: trial_government (1 "Governments will participate in the decision-making of the
##organization. In addition, other groups independent from any government may have a say in all
##major decisions as well." / 0 "No government will participate ..."), trial_scope (0 no text,
##1 "The new organization will have to decide about technical aspects of <topic>.", 2 "... about
##all aspects of <topic>."), trial_costs_benefits (0 no text, 1 "very different costs and benefits
##for different groups of people", 2 "very similar costs and benefits for all people"),
##trial_block_order (position of this experiment's block among the survey's 3 blocks).
##Covariates: cov_country, cov_survey_weight (W, the authors' weight).
##Display language: the appendix gives only the English master questionnaire; the language(s) used
##in Brazil and Germany are not documented.
##No PII in the file used. N = 12,059 matches the article; spot check: share chosen by number of
##included actors reproduces appendix Table C1a (energy .23/.33/.50/.66/.78 for 0-4 actors).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "replication2.dta"))))
stopifnot(nrow(s) == 144708, uniqueN(s$id) == 12059, all(s$Profile %in% as.character(1:6)))
cty <- c("Brazil", "Germany", "South Africa", "United States")
yn <- function(x) { stopifnot(all(x %in% 0:1)); c("No", "Yes")[x + 1L] }
for (sc in c("Energy", "Internet")) {
  x <- s[Scenario == sc]
  p <- as.integer(x$Profile)
  d <- data.table(id = as.integer(x$id), task = (p + 1L) %/% 2L, profile = 2L - p %% 2L,
                  choice = as.integer(x$Con_ch), rating = as.integer(x$Con_rate),
                  attr_companies = yn(x$Con_a1), attr_scientists = yn(x$Con_a2), attr_csos = yn(x$Con_a3), attr_citizens = yn(x$Con_a4),
                  trial_government = as.integer(x$Vig_F1), trial_scope = as.integer(x$Vig_F2), trial_costs_benefits = as.integer(x$Vig_F3),
                  trial_block_order = as.integer(if (sc == "Energy") x$BlockOrderr2 else x$BlockOrderr3),
                  cov_country = cty[x$dCountry], cov_survey_weight = x$W)
  stopifnot(!anyNA(d), all(d$rating %in% 1:7), d[, .N, .(id, task, profile)][, all(N == 1)])
  stopifnot(d[, .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)])
  stopifnot(d[, uniqueN(trial_government) + uniqueN(trial_scope) + uniqueN(trial_costs_benefits), id][, all(V1 == 3)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("eckerehrhardt_2025_", tolower(sc), "_governance.csv")))
}
