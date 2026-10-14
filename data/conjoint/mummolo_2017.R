##Community (neighbourhood) choice conjoint from
##Mummolo, J., & Nall, C. (2017). Why partisans do not sort: The constraints on political segregation.
##The Journal of Politics, 79(1), 45-59. https://doi.org/10.1086/687569
##Replication data: Harvard Dataverse doi:10.7910/DVN/EDGRDC, CC0 1.0. File read:
##conj.data.party.Rdata ("original format"; object conj.data.party, long: respondent x task x profile).
##Also read as text (not run): conjoint.estimation.R, "READ ME FIRST.pdf". The article is in a public
##course-reading copy (question wording is the paper's description, a paraphrase).
##Usage: Rscript mummolo_2017.R <dir holding conj.data.party.Rdata> <output dir>
##
##4,812 self-identified Democrats (2,524) and Republicans (2,288), quota-sampled panel from Survey Sampling
##International (paper p. 48; paper says "approximately 4,800"). Each respondent saw 5 tasks of 2 communities
##("Community A", "Community B"), 7 attributes, fully randomized ("any combination of levels may appear"):
##housing cost (share of pre-tax income), 2012 presidential vote share in the community, racial composition,
##school quality (score out of 10), commute, crime rate vs national average, type of place.
##  choice = the community the respondent prefers (paper: "choose the preferred community from each pair");
##  forced choice, exactly one per task (checked). 16 task-pairs (8 respondents) have NA responses on both
##  profiles and are omitted (rows with no outcome).
##task = recorded `task` column (1-5), profile = recorded A/B (A = 1). Level text as stored (trailing blanks
##trimmed; the school score is stored as "5"/"9" and shown "5 out of 10"/"9 out of 10" per the paper, the
##commute as stored). The housing-cost levels are 15/30/40 percent in the data; the paper's text says
##15/25/40 (the data, the authors' estimation code and its labels all say 30). Attribute display order is not
##documented.
##Respondent IDs are Qualtrics response ids (R_...): re-keyed to integers, no other identifiers in the file.
##Covariates (authors' coding, no codebook beyond variable names): cov_gender from `female` (1 = female,
##0 = male), cov_age (years), cov_party_lean from `partywlean` (dem/rep: party identification including
##leaners, as text "Democrat"/"Republican"), cov_race_white / cov_race_black (0/1 `white_race`, `black`),
##cov_income_1000 (`income`, household income in $1,000s, category midpoints as coded by the authors),
##cov_education_years (`education`). Dropped: authors' derived dummies (libdem, conrep, rich, old, educ, city,
##black.therm, ...), housing and household indicators of unclear meaning (ownrent, homelast5, kidshome, working,
##retired, single, same.msa).
##Not built: the deposit's second experiment (quickfire data, a paired comparison of single trait labels with no
##profiles) is not a profile conjoint.
##The paper reports 5 tasks per respondent and nine pairs in the Figure 1 caption (a typo); the data have 5.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "conj.data.party.Rdata"), e)
k <- as.data.table(e$conj.data.party); setnames(k, make.unique(names(k)))
stopifnot(identical(k$task, k$task.1))
k[, id := as.integer(factor(respid, levels = unique(respid)))]
d <- data.table(id = k$id, task = as.integer(k$task), profile = as.integer(k$profile), choice = as.integer(k$response))
tr <- function(x) trimws(gsub("\\s+", " ", x))
d[, attr_housing_cost := tr(k$conj.house)]
d[, attr_partisan_vote := tr(k$conj.pres)]
d[, attr_racial_composition := tr(k$conj.race)]
d[, attr_school_quality := paste(tr(k$conj.school), "out of 10")]
d[, attr_commute := tr(k$conj.commute)]
d[, attr_crime := tr(k$conj.crime)]
d[, attr_type_of_place := tr(gsub("–", "-", k$conj.place))]
d[, cov_gender := c("male", "female")[k$female + 1L]]
d[, cov_age := as.integer(k$age)]
d[, cov_party_lean := c(dem = "Democrat", rep = "Republican")[k$partywlean]]
d[, cov_race_white := as.integer(k$white_race)]
d[, cov_race_black := as.integer(k$black)]
d[, cov_income_1000 := k$income]
d[, cov_education_years := as.integer(k$education)]
d <- d[!is.na(choice)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mummolo_2017_community_choice.csv"))
