##Police-cooperation conjoint (Guatemala) from
##Denny, E. K., Dow, D. A., Pitts, W., & Wibbels, E. (2023). Citizen cooperation with the
##police: Evidence from contemporary Guatemala. Comparative Political Studies, 56(7),
##1072-1110 (online November 2022). https://doi.org/10.1177/00104140221139379
##Replication data: Harvard Dataverse doi:10.7910/DVN/9JHGVS, CC0 1.0, no restricted files.
##File read: mpp_cjt_data.Rds. The authors' mpp_cjt_replication.R was read as text (feature
##labels, outcome name). The observational file (mpp_obs_data.tab) is not used.
##Usage: Rscript denny_2022.R <raw dir> <output dir>
##
##1,841 respondents of a large nationwide survey of Guatemalans (abstract), 2 tasks
##(cjt_task) x 2 scenarios, 6 attributes, 7,364 rows. The deposit holds no codebook or
##questionnaire and the article is closed, so:
##  - Levels are the authors' English factor labels in the .Rds (the respondents
##    saw the survey language, not deposited; the displayed wording is not deposited). Attribute names follow the authors'
##    plot labels: POLICE ORIGINS (Police: From here / From another place), CHANCES OF
##    REPRISALS (Reprisal: No/Low/High chance), GENERAL VIOLENCE (Violence: Low/High),
##    ECONOMIC LOSSES (EconLoss: Small/Large), NEIGHBORS HELP (Neighbors: Will probably
##    help / Will probably not help), EFFECT OF HELPING POLICE (Effective: Help some / Not
##    help).
##  - choice = `chosen`, the scenario in which the respondent would cooperate with (share
##    information with) the police. Wording is a PARAPHRASE from the authors' figure title
##    "Attribute Choice for Police Cooperation" and the abstract; verbatim wording unknown.
##    Forced choice: exactly one chosen per task (checked), no opt-out.
##Task = cjt_task (recorded). PROFILE IS ROW ORDER within respondent x task: the .Rds has no
##profile/position column; the chosen scenario is first in 62% of tasks (not by
##construction), so row order is kept as the outcome-independent key, but whether row 1
##was "scenario A" on screen is unknown (profile_source = unknown).
##Respondent id: instanceid (survey-software uuid) re-keyed to integers in order of
##first appearance. cov_pol_legit keeps the source codes of the authors' police-legitimacy
##item (1-5; the replication code treats 1-2 as agree = high legitimacy, 4-5 as disagree,
##888 and 999 as don't know/refused; item wording not deposited). Nothing else is dropped.
##Randomization restrictions and level probabilities are not documented.
##N: the Dataverse/triage count 1,841 is the count in the data; the article was not
##accessible to check its N.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- as.data.table(readRDS(file.path(raw, "mpp_cjt_data.Rds")))
e[, src_row := .I]
e[, id := match(instanceid, unique(instanceid))]
e[, task := as.integer(cjt_task)]
setorder(e, id, task, src_row)
e[, profile := seq_len(.N), by = .(id, task)]
stopifnot(e[, .N, by = .(id, task)][, all(N == 2)])
d <- e[, .(id, task, profile, choice = as.integer(chosen),
           attr_police_origin = as.character(Police),
           attr_reprisal_chance = as.character(Reprisal),
           attr_violence = as.character(Violence),
           attr_economic_losses = as.character(EconLoss),
           attr_neighbors_help = as.character(Neighbors),
           attr_police_effective = as.character(Effective),
           cov_pol_legit = as.integer(pol_legit))]
stopifnot(d[, sum(choice), by = .(id, task)][, all(V1 == 1)],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "denny_2022_police_cooperation.csv"))
