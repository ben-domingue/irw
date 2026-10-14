##Fairness of conservation-law sanctions and willingness to follow protected-area rules, two factorial survey
##experiments from
##Ibbett, H., et al. (2024). Improving compliance around protected areas through fair administration of rules.
##Conservation Biology. https://doi.org/10.1111/cobi.14332   (author list beyond the first not checked)
##Replication data: figshare doi:10.6084/m9.figshare.25772064 (v1), CC BY 4.0. Files read: Experiment_1.xlsx,
##Experiment_2.xlsx (sheets Experiment_N and code_book), "R Code.R" (text, not run). Saved locally as e1.xlsx, e2.xlsx.
##Usage: Rscript ibbett_2024.R <dir holding e1.xlsx and e2.xlsx> <output dir>
##Writes two tables (two different designs):
##
##1) ibbett_2024_pa_sanction_fairness. Experiment 1, respondents living near Gunung Leuser National Park (Indonesia)
##   and the Ruaha-Rungwa ecosystem (Tanzania). Each saw 8 of 32 vignettes (a full 4 x 2 x 2 x 2 factorial, 4 fixed
##   blocks of 8, one block per respondent): 229 Indonesian + 217 Tanzanian respondents, 3,568 rows. The authors fit
##   the two countries side by side with the same model, so they are POOLED here with cov_country (a judgement; the
##   attribute set is shared and ids restart at 1 in each country, so ids are re-keyed). Attributes (level text from
##   the article's Table 1 as quoted on PMC7617185; the deposit stores tags such as hunting/insider/big/arrest):
##     crime: Hunting protected sambar in the national park / Logging high-value timber in the national park
##       (Indonesia only); Hunting wildlife in the nearest protected area / Grazing livestock in the nearest
##       protected area (Tanzania only). "hunting" has a different text in each country, logging is Indonesia only,
##       grazing is Tanzania only (a restriction by country).
##     offender origin: Someone from the community / Someone from outside the community (insider/outsider)
##     offender power: Someone with little power / Someone with power (small/big)
##     sanction: Arrest and prosecution / Warning with resources confiscated / No repercussions for offender /
##       Bribe accepted by law enforcer and offender allowed to continue (arrest/warning/nothing/bribe).
##   Attribute level text taken from the article (Table 1); the deposit stores short tags. The sanction labels drop
##   the article's parenthetical "(a lawful sanction)".
##   rating = fairness: how fair the sanction was perceived to be, 3 levels as stored: 1 = Unfair, 2 = Neutral,
##   3 = Fair (codebook; the article's 5-point Likert was condensed to 3 by the authors; checked: arrest and
##   warning have the highest means, bribe the lowest). No opt-out. Task = row order within respondent
##   (task_source inferred; vignette_id is the design cell, kept as trial_vignette_id). 2 rows with missing
##   fairness are omitted. Dropped: lawful (derived from sanction). Covariates: cov_country, cov_gender (female/male),
##   cov_age, cov_mpi (multidimensional poverty index, 0-1 deprived, as stored). No survey weight.
##
##2) ibbett_2024_pa_compliance_scenario. Experiment 2, one scenario per respondent (2 x 2 between-subject;
##   id = respondent within country, re-keyed), 240 Indonesian + 224 Tanzanian respondents; rows with no
##   willingness answer are omitted (10), leaving 454 (the paper analyses 432 = complete cases with the
##   covariates; the covariates here keep NA). Scenario attributes (paper wording, paraphrased from the PMC text,
##   not the full vignette):
##     peer_compliance: "Your fellow community members rarely break rules and enter the protected area to collect
##       resources" (High) / "... often break rules ..." (Low)
##     enforcer_corruption: law enforcers "highly likely" (High) / "highly unlikely" (Low) to accept a small
##       amount of money so that charges or fines disappear (paraphrased)
##   rating = scenario_intention1, "How willing would you be to follow protected area rules?", 1-5, RAW: 1 = very
##   willing ... 5 = very unwilling (higher = LESS willing; not recoded). rating_attitude = scenario_attitude3,
##   agreement with "The rules of the protected area are fair and consistent with the law" (the codebook names the
##   park rules; raw, 1 = agree ... 5 = disagree; NA kept). Dropped: intention3, attitude (recoded copies), condition.
##   Covariates: cov_country, cov_gender, cov_age, cov_education_years (completed_ind), cov_mpi. No weight.
##Judgement for Ben: the Exp. 2 factors describe the situation (peers' behaviour, enforcers' corruption) rather
##than an evaluated object; built as a 2 x 2 factorial scenario per the batch-7 ruling.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
## ---- Experiment 1
d <- as.data.table(read_excel(file.path(raw, "e1.xlsx"), sheet = "Experiment_1", na = "NA"))
stopifnot(nrow(d) == 3568)
d[, key := paste(country, id)]
d[, rid := match(key, unique(key))]
d[, task := seq_len(.N), by = key]
beh <- function(b, ctry) {
  fifelse(b == "hunting" & ctry == "Indonesia", "Hunting protected sambar in the national park",
  fifelse(b == "logging", "Logging high-value timber in the national park",
  fifelse(b == "hunting", "Hunting wildlife in the nearest protected area",
  fifelse(b == "grazing", "Grazing livestock in the nearest protected area", NA_character_))))
}
map <- function(x, from, to) to[match(x, from)]
r1 <- d[, .(id = rid, task, profile = 1L, rating = as.integer(fairness),
  attr_crime = beh(behaviour, country),
  attr_offender_origin = map(actor, c("insider", "outsider"), c("Someone from the community", "Someone from outside the community")),
  attr_offender_power = map(power, c("small", "big"), c("Someone with little power", "Someone with power")),
  attr_sanction = map(sanction, c("arrest", "warning", "nothing", "bribe"),
    c("Arrest and prosecution", "Warning with resources confiscated", "No repercussions for offender",
      "Bribe accepted by law enforcer and offender allowed to continue")),
  trial_vignette_id = as.integer(vignette_id), cov_country = country, cov_gender = gender,
  cov_age = as.integer(age), cov_mpi = as.numeric(MPI))]
stopifnot(!anyNA(r1[, .(attr_crime, attr_offender_origin, attr_offender_power, attr_sanction)]))
r1 <- r1[!is.na(rating)]
setorder(r1, id, task, profile)
fwrite(r1, file.path(out, "ibbett_2024_pa_sanction_fairness.csv"))
## ---- Experiment 2
e <- as.data.table(read_excel(file.path(raw, "e2.xlsx"), sheet = "Experiment_2", na = "NA"))
stopifnot(nrow(e) == 464)
e[, rid := .I]
r2 <- e[, .(id = rid, task = 1L, profile = 1L, rating = as.integer(scenario_intention1),
  rating_attitude = as.integer(scenario_attitude3),
  attr_peer_compliance = map(compliance, c("High", "Low"),
    c("Fellow community members rarely break rules and enter the protected area to collect resources",
      "Fellow community members often break rules and enter the protected area to collect resources")),
  attr_enforcer_corruption = map(corruption, c("High", "Low"),
    c("Law enforcers highly likely to accept a small amount of money so charges or fines disappear",
      "Law enforcers highly unlikely to accept a small amount of money")),
  cov_country = country, cov_gender = gender, cov_age = as.integer(age),
  cov_education_years = as.integer(completed_ind), cov_mpi = as.numeric(MPI))]
stopifnot(!anyNA(r2[, .(attr_peer_compliance, attr_enforcer_corruption)]))
r2 <- r2[!is.na(rating)]
setorder(r2, id, task, profile)
fwrite(r2, file.path(out, "ibbett_2024_pa_compliance_scenario.csv"))
