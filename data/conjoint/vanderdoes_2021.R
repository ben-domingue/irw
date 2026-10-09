##Participatory (neighbourhood) budgeting conjoints, Studies 2 and 3 (Netherlands), from
##van der Does, R., & Kantorowicz, J. (2021). Why do citizens (not) support democratic
##innovations? The role of instrumental motivations in support for participatory budgeting.
##Research & Politics, 8(2). https://doi.org/10.1177/20531680211024011
##Replication data: Harvard Dataverse doi:10.7910/DVN/YOKCX6, CC0 1.0. Files read: study_2.csv,
##study_3.csv. Also read as text: readme.rtf, study_1.Rmd, study_2.Rmd, study_3.Rmd (the
##authors' analysis, not run), and the article (author manuscript, UCLouvain DIAL repository;
##Table 1, Table 2, Figure 1).
##Usage: Rscript vanderdoes_2021.R <dir holding study_2.csv and study_3.csv> <output dir>
##
##STUDY 1 IS NOT BUILT: its 1,303 respondents (study_1.csv) are all in pb_data.csv of
##doi:10.7910/DVN/IZ1T9I (every responseid matches; rating and attributes identical on all
##15,636 rows), already in IRW as vanderdoes_2022_participatory_budgeting.
##Studies 2 and 3 are new data (no responseid overlaps pb_data) and separate experiments with
##different attribute sets, so they are two tables:
##  vanderdoes_2021_pb_location (Study 2): 538 respondents, 6 tasks x 2 neighbourhood budgets
##    (NBs), 5 attributes: who can submit, allowed projects, municipal support, who chooses
##    the winning project, LOCATION of the winning project (on your street / one street away
##    / four streets away). Before the tasks respondents ranked six projects; the winning
##    project shown in BOTH NBs of every task was the respondent's top-ranked one (article
##    p. 8), so it is a constant, not an attribute.
##  vanderdoes_2021_pb_cost (Study 3): 650 respondents, 6 tasks x 2 NBs, Study 1's design plus
##    the FINAL COST of the winning project (exactly as planned / 5% / 25% / 50% more).
##    The displayed WINNING PROJECT (one of eight types, randomized) is NOT in the deposit:
##    study_3.csv holds only the authors' derived outcome_favorability (Strong if the
##    respondent's own 1-7 rating of the shown project type is above 4, article p. 7), which
##    is respondent-derived, not displayed text, and is DROPPED. The stored attributes remain
##    valid comparisons under independent randomization, but the authors' favorability
##    results cannot be reproduced from this table.
##Both: online samples of citizens in Dutch municipalities > 100,000 inhabitants
##(article Table 1; panel and dates not in the deposit). Article Table 1 counts (538 / 6,456
##and 650 / 7,800 observations) match the files exactly. Task and profile are recorded.
##Outcome: rating = `selected`, "If it thus would be about your neighbourhood, what kind of
##grade would you give to the neighbourhood budgets on a scale from 1 to 7, with 1 meaning 'I
##completely disapprove' and 7 'I completely approve'?" (article Figure 1, English rendering
##of the Dutch instrument), 1-7, higher = more approval. The forced choice "Which of these two
##neighbourhood budgets do you prefer for your neighbourhood?" was asked but is NOT deposited
##for Studies 2-3, so the tables are rating-only.
##Attribute text: the authors' short English labels as stored (e.g. "Residents chosen
##randomly", "On one's street"; "muninipality" typo kept); the Dutch display text and the
##full English wording (article Table 2) are not in the data. Attribute order: not documented
##in the article or deposit. Restrictions: none documented; level shares look uniform.
##Dropped: V1 (row number), responseid (Qualtrics ResponseId, re-keyed to integers in file
##order), respondent (a non-unique index: 407 values for 650 responseids in Study 3),
##outcome_favorability (Study 3, derived), ideology_inequal (Study 3, 1-7, undocumented).
##weights_final.csv (post-stratification weights) covers Study 1 only (no Study 2/3
##responseid matches), so no survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c(attr_who_submits = "residents_allowed_submit", attr_projects_allowed = "projects_allowed",
           attr_municipal_support = "support_municipality", attr_who_chooses_winner = "choice_winning_project")
build <- function(f, extra, n_id, name) {
  s <- fread(file.path(raw, f))
  d <- s[, .(id = match(responseid, unique(responseid)), task = as.integer(task), profile = as.integer(profile),
             rating = as.integer(selected))]
  for (v in names(attrs)) d[, (v) := as.character(s[[attrs[[v]]]])]
  for (v in names(extra)) d[, (v) := as.character(s[[extra[[v]]]])]
  stopifnot(uniqueN(d$id) == n_id, d[, .N, id][, all(N == 12)], !anyDuplicated(d[, .(id, task, profile)]),
            d[, all(rating %in% 1:7)], !anyNA(d), d[, all(task %in% 1:6) && all(profile %in% 1:2)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
build("study_2.csv", c(attr_project_location = "project_location"), 538L, "vanderdoes_2021_pb_location")
build("study_3.csv", c(attr_final_cost = "final_cost"), 650L, "vanderdoes_2021_pb_cost")
