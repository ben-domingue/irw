##Electoral-reform scenario conjoint (US, Study 1) from
##Mayne, Q., & Singh, S. P. (2026). Attitudes toward electoral system reform and party system
##change in the U.S. American Political Science Review, 1-24.
##https://doi.org/10.1017/S0003055426101658
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZQNHB1, CC0 1.0. File read:
##"Study 1 Source.xlsx" (raw Qualtrics export, sheet Sheet0). Wording from "Study 1
##Questionnaire.pdf"; levels and coding from "Study 1 Preparation.do" and Codebook.pdf (read as
##text, not run); counts from "Supplementary Material.pdf".
##Usage: Rscript mayne_2026.R <dir holding "Study 1 Source.xlsx"> <output dir>
##
##Study 1 only. Study 2 is a within-subjects vignette experiment with five fixed scenarios (no
##randomized attributes), so it is not a conjoint and is not built.
##2,297 US respondents in the export (all passed the instructed-response item, IMC = 4); 2,177
##answered at least one task and are kept. 3 tasks of 2 scenarios ("Scenario 1/2"), 5 attributes.
##The Supplementary Material reports 12,842 profile rows (2 profiles x mean 2.95 tasks x 2,177
##respondents), which this table reproduces. Task, profile and attribute row position are recorded
##(Qualtrics F-<task>-<profile>-<row> columns); attribute order was randomized by respondent and is
##the same in all three tasks (attrpos_*). The order of the four follow-up questions was also
##randomized (not kept). Levels were "randomly displayed" (Supplementary Material §3); no
##restrictions are stated.
##Preamble (each task): "Below are two potential scenarios concerning a change to electoral rules."
##Four forced-choice questions per task, all Scenario 1 / Scenario 2, no opt-out:
##  choice:                "If you had to choose one of these scenarios, which would you pick?"
##  choice_voice:          "Which of these scenarios do you think would best ensure Americans' views and
##                          policy preferences on important issues get fully aired and debated in the
##                          House of Representatives?"
##  choice_governability:  "Which of these scenarios do you think would make it more difficult for
##                          legislation on important issues to get passed by the House of
##                          Representatives?" (1 = LESS governability, as in the source)
##  choice_responsiveness: "Which of these scenarios do you think would best ensure that the majority of
##                          Americans' views and policy preferences on important issues get included in
##                          legislation that is passed by the House of Representatives?"
##Every kept task has all four answers (a task is kept when any was answered; none is partial).
##Attributes (labels = the Qualtrics row labels, levels = the text shown): Partisan Support for
##Reform (3 sentences), Number of Parties with Seats in the House (Two/Three/Five), Ideological
##Representation, Ballot Structure (2 sentences), Number of Representatives per House District
##(One/Three/Five). Ideological Representation was shown as "Ideologically, members of the House are
##distributed like this:" plus a graph (an <img> link in the export). The graph cannot be stored as
##text; the level is that sentence plus "[graph: Unimodal|Flat|Bipolar]", the authors' names for the
##three images, mapped from the image IDs exactly as the preparation .do file's encode/recode does
##(IM_0Ojv... = Unimodal, IM_cZwp... = Flat, IM_3giQ... = Bipolar). Check: the voice marginal mean
##for Bipolar matches Table SM3 (0.400).
##Covariates (codes as in the source; labels from the .do file / questionnaire): cov_gender (1 Man,
##2 Woman, 3 Nonbinary, 4 Something else), cov_age (2025 - birth year, as the authors), cov_income
##(1 <$10k ... 6 $250k+; "Prefer not to say" blank), cov_education (1-16, the 16 questionnaire
##options; "Other" blank), cov_hispanic (1 yes, 0 no), cov_ideology (1 extremely liberal - 7
##extremely conservative; "Haven't thought much" blank), cov_satisfaction_democracy (0-10),
##cov_party_id (1 Republican, 2 Democrat, 3 Independent, 4 Other), cov_party_id7 (the authors' 1 strong
##Democrat - 7 strong Republican). Dropped: Qualtrics ResponseId (re-keyed to integers in file order),
##free-text "specify" fields, race (multi-select codes), state, recall/manipulation checks.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_excel(file.path(raw, "Study 1 Source.xlsx"), sheet = "Sheet0", col_types = "text"))
stopifnot(nrow(s) == 2297, all(s$IMC == "4"))
s[, rid := .I]
attrs <- c("Partisan Support for Reform" = "party_support", "Number of Parties with Seats in the House" = "num_parties",
           "Ideological Representation" = "ideo_rep", "Ballot Structure" = "ballot_struc",
           "Number of Representatives per House District" = "district_mag")
img <- c(IM_0OjvxVJS5b652qq = "Unimodal", IM_cZwpnNA00kJpGOW = "Flat", IM_3giQdp3cE7e2EwS = "Bipolar")
rows <- list()
for (t in 1:3) for (p in 1:2) {
  d <- data.table(rid = s$rid, task = t, profile = p)
  outc <- c(choice = "choice", choice_voice = "voice", choice_governability = "gov", choice_responsiveness = "resp")
  for (o in names(outc)) d[, (o) := as.integer(as.integer(s[[sprintf("conjoint_%d_%s", t, outc[[o]])]]) == p)]
  for (j in 1:5) {
    nm <- attrs[s[[sprintf("F%d%d", t, j)]]]; stopifnot(!anyNA(nm))
    lev <- s[[sprintf("F%d%d%d", t, p, j)]]
    for (k in unique(nm)) { i <- nm == k; d[i, paste0("attr_", k) := lev[i]]; d[i, paste0("attrpos_", k) := j] }
  }
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows, use.names = TRUE)
d <- d[!(is.na(choice) & is.na(choice_voice) & is.na(choice_governability) & is.na(choice_responsiveness))]
id_img <- sub('.*IM=(IM_[A-Za-z0-9]+).*', "\\1", d$attr_ideo_rep)
stopifnot(all(id_img %in% names(img)))
d[, attr_ideo_rep := paste0("Ideologically, members of the House are distributed like this: [graph: ", img[id_img], "]")]
num <- function(x, na = NULL) { x <- as.numeric(x); x[x %in% na] <- NA; x }
cv <- s[, .(rid, cov_gender = num(gender), cov_age = 2025 - num(birth_year), cov_income = num(income, 99),
            cov_education = num(educ, 95), cov_hispanic = c(1, 0)[match(num(hispanic, 99), c(1, 2))],
            cov_ideology = num(ideo, 99), cov_satisfaction_democracy = num(SWD, 99), cov_party_id = num(PID))]
cv[, cov_party_id7 := fcase(cov_party_id == 2 & s$PID_Dem_Strength == "1", 1, cov_party_id == 2 & s$PID_Dem_Strength == "2", 2,
                            cov_party_id == 3 & s$PID_Ind_Lean == "2", 3, cov_party_id == 3 & s$PID_Ind_Lean == "3", 4,
                            cov_party_id == 3 & s$PID_Ind_Lean == "1", 5, cov_party_id == 1 & s$PID_Rep_Strength == "2", 6,
                            cov_party_id == 1 & s$PID_Rep_Strength == "1", 7)]
d <- merge(d, cv, by = "rid")
ids <- sort(unique(d$rid)); d[, id := match(rid, ids)][, rid := NULL]
for (o in c("choice", "choice_voice", "choice_governability", "choice_responsiveness"))
  stopifnot(d[!is.na(get(o)), sum(get(o)), .(id, task)][, all(V1 == 1)])
stopifnot(uniqueN(d$id) == 2177, nrow(d) == 12842)
setcolorder(d, c("id", "task", "profile", "choice", "choice_voice", "choice_governability", "choice_responsiveness",
                 paste0("attr_", attrs), paste0("attrpos_", attrs)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mayne_2026_electoral_reform.csv"))
