##Income-reform conjoints (US) from
##Bechtel, M. M., & Liesch, R. (2020). Reforms and redistribution: Disentangling the egoistic
##and sociotropic origins of voter preferences. Public Opinion Quarterly, 84(1), 1-23.
##https://doi.org/10.1093/poq/nfaa006
##Replication data: Harvard Dataverse doi:10.7910/DVN/QUPGIN, CC0 1.0, no restricted files.
##Files read (Dataverse "original format" .dta downloads, renamed): POQ_Bechtel_Liesch_Main_Survey
##(main.dta), POQ_Bechtel_Liesch_Pilot (pilot.dta), POQ_Bechtel_Liesch_Validation_Study
##(valid.dta). Read as text, not run: POQ_Bechtel_Liesch_Replication_Archive.do. Wording and
##design from the deposit's Main Questionnaire.pdf (Qualtrics export) and the deposited
##article + supplementary material PDF ("Bechtel Liesch Reforms and Redistribution.pdf").
##Usage: Rscript bechtel_2020.R <raw dir> <output dir>
##
##THREE TABLES, three separate experiments (different samples, attribute sets or level text):
##
##1. bechtel_2020_income_reforms -- main study. 2,721 US respondents (Respondi online quota
##   panel, Sept/Oct 2016), up to 4 pairs of policy proposals ("Policy 1"/"Policy 2"), 6
##   attributes, each the proposal's income change for a group: attr_income_us ("Average
##   income in the United States"), attr_income_personal ("Your personal income"),
##   attr_income_sector ("Average income in your sector of employment"), attr_income_10k /
##   _85k / _375k ("Individuals earning about $10,000 / $85,000 / $375,000 per year"); article
##   Table 1. Levels are the .dta value labels: -$5000, -$2500, $0, +$2500, +$5000. Fully
##   randomized ("a restricted randomization is neither necessary nor beneficial"); attribute
##   order randomized across respondents, fixed within (article; not recorded).
##   task = conjointno, profile = scenario ("Parameter sequence number"), both recorded.
##   Respondents have 1-4 tasks (95 have 1, 258 have 2, 630 have 3): the deposit holds 18,906
##   rated policies, exactly the article's N (2,721 respondents, 18,906 rated policies).
##   choice = chosen: "Which policy do you prefer?" forced, no opt-out (choice matches chosen).
##   rating = vote: "If you could vote on each of these policies in a referendum, how likely is
##   it that you would vote in favor or against each of the proposals? Please give your answer
##   on the following scale from definitely against (1) to definitely in favor (10)."
##   trial_page_submit_sec = pagesubmit_cj (seconds on that conjoint page; Qualtrics timer).
##   Covariates (text from .dta value labels; mis-encoded apostrophes/dashes in labels repaired):
##   cov_age (years), cov_gender (male: 1 = male, 0 = female), cov_leftright (0 left - 10 right),
##   cov_party_id (partyID_US "R identifies with this party": Republican/Democrat/Other; NA for
##   8,578 rows -- the supplement's wording asks "Is there a particular party you feel closer
##   to...?" first, so NA likely includes "no", not only missing), cov_race, cov_education
##   (education_US), cov_occupation (occSituation_US), cov_income (income_US_raw; "Prefer not to
##   say" -> NA), cov_income_high (highInc, asked of $150,000+), cov_sector (NAICS_Sector as
##   stored, "" / "." -> NA), cov_county_unemployment_rate (authors' BLS match, %),
##   cov_altruism_donation (% of a $100 voucher donated), cov_know_defense / cov_know_house /
##   cov_know_senate_term (0/1 correct), cov_attention_pass (screenerCorrect), cov_socid_<group>
##   (importance of occupation/race/nationality/class to identity, 1 = not at all .. 5 = very
##   important), cov_survey_weight (weight, entropy-balancing weights used in all the paper's
##   estimates), cov_weight_likely_voter (weightLikelyVoter, the authors' Figure A.12 weights).
##   Dropped: derived dummies and groupings (age/edu/income/ideology groups, rBenefits, etc.),
##   acceptedd/rejectedd (recodes of vote), income_combined/altru_combined (US/German pooled
##   coding), contestid, Sector (duplicate of NAICS_Sector grouping), IndustryUnemp_Oct2016.
##   Spot check: weighted OLS of choice on the attributes (ref $0), clustered by id: average US
##   income +$5000 = +0.04, personal income +$5000 = +0.11 (article: "about 4 percentage
##   points" and "about 11 percentage points").
##
##2. bechtel_2020_income_reforms_pilot -- 307 MTurk respondents (May/June 2016; supplement C),
##   same 6 dimensions with income changes in percent; levels are the .dta labels -5%, -2%, 0%,
##   +2%, +5%. Only chosen is deposited (no rating, no task/profile columns): task and profile
##   are INFERRED from row order (rows sorted by respondent; consecutive rows form a pair;
##   verified: every pair has exactly one chosen profile; 2-8 rows per respondent). N = 307 and
##   2,222 rated policies match supplement Figure A.6.
##
##3. bechtel_2020_income_reforms_validation -- 2,003 MTurk respondents (validation study;
##   article: 2,300 fielded), up to 15 pairs. Five attributes, income changes for people
##   "earning less than $18,000, between $18,000 and $35,000, between $35,000 and $60,000,
##   between $60,000 and $100,000, more than $100,000" (article), levels -$5000 .. +$5000.
##   Respondents were randomly assigned to one framing, held for all their tasks
##   (trial_version, from Conjoint: Normal -> "generic policy", HealthCPolConjoint -> "health
##   care policy", TradePolConjoint -> "trade policy", CandidConjoint -> "candidate platform");
##   one table since the attributes are identical across versions. Only chosen is deposited
##   (choice; question wording of the validation instrument not deposited, the main study's is
##   "Which policy do you prefer?"; candidate version "which candidate you prefer").
##   task = conjointno (recorded); profile INFERRED from row order within task (verified: 2
##   consecutive rows per task, exactly one chosen). N = 2,003 and 54,342 rated options match
##   article Figure 6.
##No covariates ship with the pilot or validation files.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); stopifnot(!anyNA(y[!is.na(x)])); y }
fix <- function(x) { x <- gsub("Õ", "'", x, fixed = TRUE); gsub("Ð", "-", x, fixed = TRUE) }
## 1. main
m <- as.data.table(read_dta(file.path(raw, "main.dta")))
stopifnot(uniqueN(m$uniqueID) == 2721, nrow(m) == 18906, m[, all(chosen == (choice == scenario))])
d <- m[, .(id = as.integer(uniqueID), task = as.integer(conjointno), profile = as.integer(scenario),
           choice = as.integer(chosen), rating = as.integer(zap_labels(vote)))]
att <- c(IncomeUS_ = "us", IncomePers_ = "personal", IncomeSector_ = "sector", Income10k_ = "10k",
         Income85k_ = "85k", Income375k_ = "375k")
for (k in names(att)) d[, paste0("attr_income_", att[[k]]) := lab(m[[k]])]
d[, trial_page_submit_sec := as.numeric(m$pagesubmit_cj)]
g <- as.integer(zap_labels(m$male)); stopifnot(all(g %in% 0:1))
na_lab <- function(x, drop = character()) { y <- fix(lab(x)); y[y %in% drop] <- NA_character_; y }
sec <- trimws(m$NAICS_Sector); sec[sec %in% c("", ".")] <- NA_character_
d[, `:=`(cov_age = as.integer(m$age), cov_gender = c("female", "male")[g + 1L],
         cov_leftright = as.integer(zap_labels(m$leftright)), cov_party_id = na_lab(m$partyID_US),
         cov_race = na_lab(m$race), cov_education = na_lab(m$education_US),
         cov_occupation = na_lab(m$occSituation_US), cov_income = na_lab(m$income_US_raw, "Prefer not to say"),
         cov_income_high = na_lab(m$highInc), cov_sector = sec,
         cov_county_unemployment_rate = as.numeric(m$unemploymentrate),
         cov_altruism_donation = as.numeric(m$altruistic),
         cov_know_defense = as.integer(zap_labels(m$know1correct)), cov_know_house = as.integer(zap_labels(m$know2correct)),
         cov_know_senate_term = as.integer(zap_labels(m$know3correct)),
         cov_attention_pass = as.integer(zap_labels(m$screenerCorrect)),
         cov_socid_occupation = as.integer(zap_labels(m$socidOccupation)), cov_socid_race = as.integer(zap_labels(m$socidRace)),
         cov_socid_nationality = as.integer(zap_labels(m$socidNationality)), cov_socid_class = as.integer(zap_labels(m$socidClass)),
         cov_survey_weight = as.numeric(m$weight), cov_weight_likely_voter = as.numeric(m$weightLikelyVoter))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:10), all(d$cov_attention_pass %in% 0:1))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bechtel_2020_income_reforms.csv"))
## 2. pilot (task/profile from row order)
p <- as.data.table(read_dta(file.path(raw, "pilot.dta")))
stopifnot(all(diff(p$uniqueID) >= 0), p[, .N, uniqueID][, all(N %% 2 == 0)], uniqueN(p$uniqueID) == 307)
p[, r := seq_len(.N), uniqueID]
e <- p[, .(id = as.integer(uniqueID), task = (r + 1L) %/% 2L, profile = 2L - r %% 2L, choice = as.integer(chosen))]
patt <- c(NFeatIncomeUS_ = "us", NFeatIncomePers_ = "personal", NFeatIncomeSector_ = "sector",
          NFeatIncome10k_ = "10k", NFeatIncome85k_ = "85k", NFeatIncome375k_ = "375k")
for (k in names(patt)) e[, paste0("attr_income_", patt[[k]]) := lab(p[[k]])]
stopifnot(e[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(e, id, task, profile)
fwrite(e, file.path(out, "bechtel_2020_income_reforms_pilot.csv"))
## 3. validation (profile from row order within task)
v <- as.data.table(read_dta(file.path(raw, "valid.dta")))
stopifnot(all(diff(v$uniqueID) >= 0), uniqueN(v$uniqueID) == 2003, nrow(v) == 54342)
v[, o := .I]
stopifnot(v[, .N, .(uniqueID, conjointno)][, all(N == 2)], v[, all(diff(o) == 1), .(uniqueID, conjointno)][, all(V1)])
v[, profile := seq_len(.N), .(uniqueID, conjointno)]
ver <- c(Normal = "generic policy", HealthCPolConjoint = "health care policy", TradePolConjoint = "trade policy",
         CandidConjoint = "candidate platform")
stopifnot(all(v$Conjoint %in% names(ver)))
f <- v[, .(id = as.integer(uniqueID), task = as.integer(conjointno), profile = as.integer(profile), choice = as.integer(chosen))]
vatt <- c(Incomeb18k_ = "below_18k", Income18less35k_ = "18k_35k", Income35less60k_ = "35k_60k",
          Income60less100k_ = "60k_100k", Income100kp_ = "above_100k")
for (k in names(vatt)) f[, paste0("attr_income_", vatt[[k]]) := lab(v[[k]])]
f[, trial_version := unname(ver[v$Conjoint])]
stopifnot(f[, sum(choice), .(id, task)][, all(V1 == 1)], f[, uniqueN(trial_version), id][, all(V1 == 1)])
setorder(f, id, task, profile)
fwrite(f, file.path(out, "bechtel_2020_income_reforms_validation.csv"))
