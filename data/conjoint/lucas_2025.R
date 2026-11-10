##Municipal candidate partisanship conjoint (Calgary, Edmonton) from
##Lucas, J., McGregor, R. M., Snagovsky, F., & Wesley, J. (2025). Do municipal voters punish partisan
##candidates? Evidence from a newly partisan municipal election. (No article DOI in the deposit.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/U3AFDM, CC0 1.0. Files read: conjoint.tab (long, one row
##per profile shown), codebook.xlsx (variable meanings, read as text), the Qualtrics exports
##questionnaire_march_2025.qsf and questionnaire_september_2025_leger.qsf (attribute level arrays in the
##survey JavaScript, question wording and answer scales), "1 replication code.R" (read as text).
##Usage: Rscript lucas_2025.R <dir holding conjoint.tab> <output dir>
##
##Online panel surveys (Leger / EveryAnswer) of Alberta residents: March 2025 in Calgary (805) and Edmonton (804),
##September 2025 in Calgary (2,322): 3,931 respondents. Each respondent saw 3 pairs of hypothetical city-council
##candidates (task 1-3, profile 1 = Candidate A, 2 = Candidate B), 6 attributes: age (25/45/65), gender
##(Man/Woman), race (White/South Asian/Chinese), position (Not on Council/Member of Council), ideology
##(Left/Centre/Right), party (Running as an Independent / Running with a municipal political party). Level text
##is taken verbatim from the survey JavaScript arrays (both questionnaires identical); the data store tags
##(southasian, 1/0 dummies) that are mapped to that text.
##One table for all three samples: identical design and text; the authors pool the two Calgary waves (experiment
##covariate; main text uses city == Calgary) and test Calgary against Edmonton in a pooled interaction model
##(Table SM.3). trial_wave = "March 2025"/"September 2025" (source `experiment` 1/2); cov_city = the city.
##Outcomes on the same tasks (both in this table):
##  choice: "If you had to choose between Candidate A and Candidate B, which candidate would you vote for?"
##    (forced choice, no opt-out; source vote_choice).
##  rating_vote: "How likely would you be to vote for Candidate A [B] if they were running in your ward?"
##    0 (No Chance) ... 5 (50-50 Chance) ... 10 (Certain to Support); source vote_cont, kept raw.
##Respondents kept: 3,847 of 3,931 (84 respondents have no outcome on any task).
##Missing outcomes: 910 rows (all September) have no forced choice; 758 of them have no rating either
##(378 tasks with no outcome at all are dropped, and 4 tasks with a rating for only one of the two
##candidates are dropped); 152 rows (76 tasks) have a rating but no choice: kept, choice NA
##on both profiles of the task.
##Randomization (survey JavaScript): every attribute level of every profile drawn independently and with equal
##probability (restrictions none, level_weights uniform); the ORDER of the six attributes is shuffled once per
##respondent and applied to all tasks (attr_order = respondent); the order is not saved in the deposit, so no
##attrpos_ columns. Fixed order of the two candidates within a task.
##Covariates: cov_age (resp_age, years; values above 100 set NA), cov_gender_code (resp_gender: 1 = woman,
##0 = otherwise, per codebook; "otherwise" mixes men and others so it cannot map to the reserved cov_gender),
##cov_degree ("university degree"/"no university degree" from resp_degree 1/0; not the full education question),
##cov_ideology (self-placement 0 left - 10 right), cov_anti_party_index (0 strong support for partisan
##municipal politics - 18 strong opposition), cov_therm_ucp / cov_therm_ndp (0-10 feelings, September only), cov_city.
##Dropped: Qualtrics ResponseId (re-keyed to integer id), derived partisan/incumbent dummies (replaced by text),
##and the other deposit files (candidate placements, vote choice of real candidates, policy positions).
##No survey weight in the deposit. Respondent count vs paper: article not available in the deposit; no check.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjoint.tab"), na.strings = c("", "NA"))
stopifnot(s[, uniqueN(ResponseId)] == 3931, s[, .N, .(ResponseId, task)][, all(N == 2)])
s[, none := all(is.na(vote_choice) & is.na(vote_cont)), .(ResponseId, task)]
print(s[, .(tasks = uniqueN(paste(ResponseId, task))), none])
s[, part := sum(!is.na(vote_cont)) == 1L, .(ResponseId, task)]
print(s[, .(tasks = uniqueN(paste(ResponseId, task))), part])
s <- s[none == FALSE & part == FALSE]
s[, id := as.integer(factor(ResponseId, levels = unique(ResponseId)))]
stopifnot(s[, .N, .(id, task)][, all(N == 2)])
rc <- function(x, from, to) unname(setNames(to, from)[as.character(x)])
d <- s[, .(id = id, task = as.integer(task), profile = as.integer(character),
           choice = as.integer(vote_choice), rating_vote = as.integer(vote_cont),
           attr_age = as.character(cand_age),
           attr_gender = rc(cand_gender, c(0, 1), c("Man", "Woman")),
           attr_race = rc(cand_race, c("white", "southasian", "chinese"), c("White", "South Asian", "Chinese")),
           attr_position = rc(cand_incumbent, c(0, 1), c("Not on Council", "Member of Council")),
           attr_ideology = rc(cand_ideology, c("left", "centre", "right"), c("Left", "Centre", "Right")),
           attr_party = rc(cand_partisan, c(0, 1), c("Running as an Independent", "Running with a municipal political party")),
           cov_age = fifelse(resp_age > 100, NA_integer_, as.integer(resp_age)),
           cov_gender_code = as.integer(resp_gender),
           cov_degree = rc(resp_degree, c(0, 1), c("no university degree", "university degree")),
           cov_ideology = as.integer(resp_ideology),
           cov_anti_party_index = as.integer(resp_partysentiment),
           cov_therm_ucp = as.integer(resp_thermUCP), cov_therm_ndp = as.integer(resp_thermNDP),
           cov_city = city,
           trial_wave = rc(experiment, c(1, 2), c("March 2025", "September 2025")))]
stopifnot(!anyNA(d[, .(attr_age, attr_gender, attr_race, attr_position, attr_ideology, attr_party)]))
stopifnot(d[, sum(choice, na.rm = TRUE), .(id, task)][, all(V1 <= 1)])
stopifnot(d[, uniqueN(is.na(choice)), .(id, task)][, all(V1 == 1)])
stopifnot(d[, uniqueN(is.na(rating_vote)), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lucas_2025_municipal_partisanship.csv"))
