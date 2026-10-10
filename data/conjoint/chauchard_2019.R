##Politician-wealth vignette conjoint (Bihar, India, lab-in-the-field, spring 2015) from
##Chauchard, S., Klasnja, M., & Harish, S. P. (2019). Getting rich too fast? Voters' reactions
##to politicians' wealth accumulation. The Journal of Politics, 81(4), 1197-1209.
##https://doi.org/10.1086/704222
##Replication data: Harvard Dataverse doi:10.7910/DVN/NMCOBF, CC0 1.0, no restricted files.
##File read: conjoint-survey.dta (Dataverse original format; one row per respondent x vignette,
##Stata value labels on the attribute codes). Read as text only: README.txt, paper.do,
##appendix.do. The article text (author manuscript, Leiden repository) gives the design and
##outcome paraphrases; its Appendix A9/A13 (example vignette, questionnaire) is NOT deposited.
##Usage: Rscript chauchard_2019.R <dir holding conjoint-survey.dta> <output dir>
##
##1,021 respondents (Madhepura district lab) each rated 3 single-politician vignettes
##(task = `vignette`, the presentation position; profile = 1). Each vignette showed a
##photograph and a summary of randomized attributes, described by enumerators as a "current
##state legislator and likely candidate in the upcoming state elections" (article p. 8).
##Outcomes (article p. 12, paraphrased; full wording in the undeposited Appendix A13):
##  choice          = dv_vote, whether they would consider voting for the politician (yes 1 /
##                    no 0); single-profile accept/reject, so opt_out = yes. 88 don't-knows
##                    (dv_vote_dk = 1) are NA.
##  rating_repr     = dv_repr, how good a job the politician would do addressing constituents'
##                    problems, 1-5
##  rating_personal = dv_person, how helpful the politician would be for the respondent
##                    personally, 1-5
##  rating_corrupt  = dv_corrupt, how likely the politician was corrupt, 1-5
##  rating_violence = dv_violence, how likely the politician would engage in violent
##                    activities, 1-5
##  Stored as in the source. Scale anchors are not deposited. Direction from the article's
##  results (higher = better job / more helpful / more corrupt / more violent: e.g. mean
##  dv_repr 4.1 for a good vs 2.8 for a disappointing record, dv_corrupt 3.2 charged vs 2.7 not).
##Attributes: level text is the authors' Stata value labels (English), NOT the displayed wording
##(the article gives some displayed phrases, quoted here; the survey language is not stated):
##  attr_photo     photo 1-6, stored "Photo 1".."Photo 6" (the authors' figure labels; the
##                 photographs are not deposited; politicians are described as "his")
##  attr_district  dist: Banka / Jahanabad / Katihar / Lakhisarai / Madhubani / Muzaffarpur /
##                 Navada / Samastipur
##  attr_caste     ethn, subcaste as recorded in the data (lower case, as stored). Design
##                 restriction: one of the three vignettes (co_ethn_vignette) carries the
##                 respondent's own subcaste (from the pre-treatment survey, spelled as
##                 recorded); the other two are drawn from the eleven largest subcastes.
##  attr_party     RJD / JDU / Congress / BJP
##  attr_record    Good / Disappointing (displayed: "[very active/not very active] in terms of
##                 development and infrastructure", done "[a lot/very little] for his
##                 constituency")
##  attr_family    Poor / Middle-income / Rich (displayed: hailed from a "poor", "middle
##                 income" or "rich" family)
##  attr_crime     No crime / Crime (displayed: "not charged in any criminal cases" / "charged
##                 in several criminal cases")
##  attr_wealth_2010     5 lakh / 8 lakh / 20 lakh / 45 lakh / 85 lakh / 2 crore / 4 crore
##  attr_wealth_increase No increase / 0.2x (displayed as "slight increase", article fn 12) /
##                       2x / 3x / 5x / 10x / 30x
##  attr_legality  No suspicion / Suspicion (press had / had not reported suspicions of
##                 illegality); "(not shown)" with No increase (by design, article p. 11; the
##                 source codes it N/A = 0).
##Attribute order randomized per vignette and recorded (*_order, positions 1-7 of the seven
##text attributes; the three wealth attributes share one position, wealth_order): attrpos_*.
##The photograph has no position. Level probabilities are not documented.
##Covariates: cov_gender (_female 1 = female, 0 = male; unlabelled, coding from the variable
##name), cov_age (_age, Q2, years), cov_schooling (_schooling, Q6, as stored: years),
##cov_caste (_ethnicity, as recorded), cov_urban (urban 0/1). No survey weight.
##Dropped: filename, URI, interviewer and field investigator codes, location (village/ward
##names), date, other demographics and asset items, and the authors' derived dummies
##(co_ethn_dummy, non_co_ethn, out_party, w2010r, wmultr, _occ*, _yadav1, _muslim1, ...).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_dta(file.path(raw, "conjoint-survey.dta"))
lab <- function(v) as.character(as_factor(v, levels = "labels"))
dk <- as.integer(x$dv_vote_dk)
stopifnot(all(is.na(x$dv_vote) == (dk == 1)), all(x$photo %in% 1:6), all(lab(x$legal)[lab(x$wmult) == "No increase"] == "N/A"),
          !any(lab(x$legal)[lab(x$wmult) != "No increase"] == "N/A"))
d <- data.table(id = as.integer(x$id), task = as.integer(x$vignette), profile = 1L, choice = as.integer(x$dv_vote),
                rating_repr = as.integer(x$dv_repr), rating_personal = as.integer(x$dv_person),
                rating_corrupt = as.integer(x$dv_corrupt), rating_violence = as.integer(x$dv_violence),
                attr_photo = paste("Photo", as.integer(x$photo)), attr_district = lab(x$dist), attr_caste = x$ethn,
                attr_party = lab(x$party), attr_record = lab(x$record), attr_family = lab(x$family), attr_crime = lab(x$crime),
                attr_wealth_2010 = lab(x$w2010), attr_wealth_increase = lab(x$wmult), attr_legality = lab(x$legal),
                attrpos_district = as.integer(x$dist_order), attrpos_caste = as.integer(x$ethn_order),
                attrpos_party = as.integer(x$party_order), attrpos_record = as.integer(x$record_order),
                attrpos_family = as.integer(x$family_order), attrpos_crime = as.integer(x$crime_order),
                attrpos_wealth_2010 = as.integer(x$wealth_order), attrpos_wealth_increase = as.integer(x$wealth_order),
                attrpos_legality = as.integer(x$wealth_order),
                cov_gender = c("male", "female")[as.integer(x[["_female"]]) + 1L], cov_age = as.integer(x[["_age"]]),
                cov_schooling = as.integer(x[["_schooling"]]), cov_caste = x[["_ethnicity"]], cov_urban = as.integer(x$urban))
d[attr_legality == "N/A", attr_legality := "(not shown)"]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]), d[, .N, .(id, task)][, all(N == 1)], uniqueN(d$id) == 1021)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "chauchard_2019_wealth_accumulation.csv"))
