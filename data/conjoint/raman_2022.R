##COVID-19 booster / vaccine single-profile conjoint (US) from
##Raman, S., Kriner, D., Ziebarth, N., Simon, K., & Kreps, S. (2022). COVID-19 booster uptake
##among US adults: Assessing the impact of vaccine attributes, incentives, and context in a
##choice-based experiment. Social Science & Medicine, 310, 115277.
##https://doi.org/10.1016/j.socscimed.2022.115277
##Replication data: Harvard Dataverse doi:10.7910/DVN/DMIMUL ("Omicron and Likelihood of Receiving
##a COVID-19 Vaccine Booster"), CC0 1.0, no restricted files. File read:
##boosters_ssm_replication_data.dta (Dataverse "original format" download; long, one row per
##respondent x profile, plus the full Qualtrics/Lucid export repeated on every row). The authors'
##boosters_ssm_replication_revision_do.do was read as text (not run). Design facts from the article
##(PMC9376982).
##Usage: Rscript raman_2022.R <dir holding the .dta> <output dir>
##
##Lucid quota sample of US adults, 14-17 December 2021 (article: 2,241 recruited). Each respondent
##saw 5 hypothetical vaccine profiles ONE AT A TIME ("Vaccine 1".."Vaccine 5"; task = choice_set,
##profile = 1) with 5 attributes in a fixed order (the .dta's F-t-p attribute-name fields are the
##same for every respondent and task): "Efficacy -- protection against symptomatic infection from
##current variants" (50%/70%/90%), "Protection duration (against current variants)" (6 months /
##1 year / 2 years), "Protection against potential future variants" (Protects against future
##variants / May require a booster against future variants), "Manufacturer" (Pfizer / Moderna /
##Johnson & Johnson), "Financial incentive" (You receive: $10 / $100 / $1,000 incentive / (1) day of
##guaranteed paid time off (PTO)). Level text = the .dta *_string columns, identical to the
##displayed F-t-1-p fields. The article says 288 unique profiles; these levels give 216.
##Outcomes (wording from the .dta variable/value labels; Qualtrics piped "e" for the unvaccinated
##and "e booster" for everyone else, so the object reads "vaccine" or "vaccine booster"):
##  choice = receive = vax_bin<t> "If you had to choose, would you choose to get this vaccin[e /
##           e booster]": 1 "I would choose to get this vaccine (booster)", 0 "I would NOT choose
##           ..." (single profile, so rejecting is the outside option: opt_out yes). Verified equal
##           to the wide vax_bin<t> for every row.
##  rating = vax_likely = vax_<t>_likely "How likely or unlikely would you be to get the vaccin[e /
##           e booster] d..." (label truncated in the .dta), 1 Extremely unlikely .. 7 Extremely
##           likely, stored raw (higher = more likely). Verified equal to the wide vax_<t>_likely.
##trial_omicron_info = the randomized contextual prime before the conjoint (lesslethal; value
##labels "Unknown" = control: experts do not yet know whether the variant spreads more or less
##quickly; "Likely more contagious, less lethal" = treatment), constant within respondent.
##ONE TABLE for all vaccination groups (same attributes and questions, only the piped noun
##differs); the article analyses the fully vaccinated, unboosted (cov_vax_status = fully
##vaccinated & cov_booster_status = No; article n = 548, here 548 after the 3 drops) and, in the appendix, the
##unvaccinated (article n = 619, here 619).
##Dropped: 3 respondents (15 rows) whose attribute fields are empty (the .do: "Attribute data is
##missing for three people"); Lucid rid (re-keyed to integers in file order); zip code; the empty
##Qualtrics PII placeholders (IPAddress, Recipient*, Location*, ExternalReference hold one blank
##value each); free-text comments; the authors' derived dummies (dem3, gop5, female, black, work_*,
##conservatism, fully_vax_unboosted ...) and string duplicates; all other survey items.
##Covariates (.dta value-label text unless noted): cov_gender ("What is your gender?" 1 Male = male,
##2 Female = female, 3 Prefer not to say = NA), cov_age (years = the .dta's "Age (in 10s)" x 10, as in
##the authors' .do), cov_education, cov_party_id (party3 "In politics, as of today, do you consider
##yourself a Republican, a Democrat, or an Independent?"), cov_party_lean, cov_ideology, cov_income,
##cov_state, cov_race_<k> (check-all race items: 1 = checked, NA = not; 1 American Indian, 2 Asian,
##3 Black or African American, 4 Hispanic, 5 White, 6 Other), cov_vax_status (covid_vax_status
##text), cov_booster_status ("Have you received a COVID-19 vaccine booster?" Yes/No, asked of the
##vaccinated), cov_duration_sec (Qualtrics survey duration in seconds). No survey weight.
##Spot check: in the fully vaccinated unboosted group, the raw share choosing a 90%-efficacy profile
##is 0.72 (article: marginal mean 0.73 from OLS with all attributes and the prime).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "boosters_ssm_replication_data.dta")))
k <- k[efficacy_string != ""]
stopifnot(k[, .N, rid][, all(N == 5)], k[, all(sort(choice_set) == 1:5), rid]$V1)
d <- data.table(id = match(k$rid, unique(k$rid)), task = as.integer(k$choice_set), profile = 1L,
                choice = as.integer(k$receive), rating = as.integer(k$vax_likely))
stopifnot(all(d$choice %in% 0:1), all(d$rating %in% 1:7))
for (v in c("efficacy", "duration", "protection", "manufacturer", "incentive")) {
  x <- k[[paste0(v, "_string")]]; stopifnot(all(x != "")); d[, paste0("attr_", v) := x]
}
d[, trial_omicron_info := as.character(as_factor(k$lesslethal, levels = "labels"))]
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); y }
stopifnot(all(k$gender %in% 1:3))
d[, cov_gender := c("male", "female", NA)[as.integer(k$gender)]]
d[, cov_age := as.integer(round(as.numeric(k$age) * 10))]
d[, cov_education := lab(k$education)]
d[, cov_party_id := lab(k$party3)]
d[, cov_party_lean := lab(k$party_lean)]
d[, cov_ideology := lab(k$ideology)]
d[, cov_income := lab(k$income)]
d[, cov_state := lab(k$state)]
for (r in 1:6) d[, paste0("cov_race_", r) := as.integer(zap_labels(k[[paste0("race_", r)]]))]
d[, cov_vax_status := lab(k$covid_vax_status)]
d[, cov_booster_status := lab(k$covid_booster_status)]
d[, cov_duration_sec := as.integer(k$Duration__in_seconds_)]
# respondent-level fields constant within respondent
stopifnot(d[, lapply(.SD, uniqueN), id, .SDcols = c("trial_omicron_info", "cov_age", "cov_vax_status")][, all(trial_omicron_info == 1 & cov_age == 1 & cov_vax_status == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "raman_2022_covid_booster.csv"))
