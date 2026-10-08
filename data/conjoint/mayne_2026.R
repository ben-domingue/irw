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
##Covariates (text from Study 1 Questionnaire.pdf, codes matched via "Study 1 Preparation.do"):
##cov_gender ("What is your gender?" p.1: 1 Man -> "male", 2 Woman -> "female", 3 Nonbinary and
##4 "Something else (please specify)" -> "other"; .do L738 "1 if man; 2 if woman; 3 if
##non-binary; 4 if other"), cov_age (2025 - birth year, as the authors compute it, Preparation.do
##L755), cov_birth_year ("In what year were you born?"), cov_income (1 <$10k ... 6 $250k+; "Prefer not to say"
##blank), cov_education (answer text of "What is your highest level of school you have
##completed or highest degree that you received?", p.6, e.g. "Bachelor’s degree (For example:
##BA, AB, BS)"; codes 1-16 per .do label educ_categories L792-811, code 95 = "Other (please
##specify)"), cov_hispanic (1 yes, 0 no), cov_ideology (1 extremely liberal - 7 extremely
##conservative; "Haven't thought much" blank), cov_satisfaction_democracy (0-10), cov_party_id
##(answer text of "Generally speaking, do you think of yourself as a Republican, Democrat, or an
##independent?", p.10: "Republican", "Democrat", "Independent", "Other party (please
##specify)"; codes per .do party_id_labels L1017-1022), cov_party_id7 (the authors' 7-point
##scale from PID and the strength/lean follow-ups, as text with the .do labels L1040-1048:
##"Strong Democrat", "Weak Democrat", "Independent Democrat", "Independent", "Independent
##Republican", "Weak Republican", "Strong Republican"). No survey weight in the deposit. Every
##respondent passed the instructed-response item (IMC = 4), so no attention column is kept.
##No task is repeated. Dropped: Qualtrics ResponseId (re-keyed to integers in file order),
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
educ_txt <- c("Less than 1st grade", "1st, 2nd, 3rd or 4th grade", "5th or 6th grade", "7th or 8th grade", "9th grade",
              "10th grade", "11th grade", "12th grade no diploma",
              "High school graduate - High school diploma or equivalent (for example: GED)", "Some college but no degree",
              "Associate degree in college - Occupational/vocational program", "Associate degree in college - Academic program",
              "Bachelor\u2019s degree (For example: BA, AB, BS)", "Master\u2019s degree (For example: MA, MS, MEng, MEd, MSW, MBA)",
              "Professional school degree (For example: MD, DDS, DVM, LLB, JD)", "Doctorate degree (For example: PhD, EdD)")
stopifnot(all(s$gender %in% c("1", "2", "3", "4", NA)), all(s$educ %in% c(as.character(c(1:16, 95)), NA)), all(s$PID %in% c("1", "2", "3", "4", NA)))
cv <- s[, .(rid, cov_gender = c("male", "female", "other", "other")[num(gender)], cov_age = 2025 - num(birth_year), cov_birth_year = as.integer(birth_year),
            cov_income = num(income, 99),
            cov_education = fifelse(educ == "95", "Other (please specify)", educ_txt[num(educ, 95)]),
            cov_hispanic = c(1, 0)[match(num(hispanic, 99), c(1, 2))],
            cov_ideology = num(ideo, 99), cov_satisfaction_democracy = num(SWD, 99), pid = num(PID))]
cv[, cov_party_id := c("Republican", "Democrat", "Independent", "Other party (please specify)")[pid]]
cv[, cov_party_id7 := c("Strong Democrat", "Weak Democrat", "Independent Democrat", "Independent", "Independent Republican",
                        "Weak Republican", "Strong Republican")[fcase(pid == 2 & s$PID_Dem_Strength == "1", 1, pid == 2 & s$PID_Dem_Strength == "2", 2,
                            pid == 3 & s$PID_Ind_Lean == "2", 3, pid == 3 & s$PID_Ind_Lean == "3", 4,
                            pid == 3 & s$PID_Ind_Lean == "1", 5, pid == 1 & s$PID_Rep_Strength == "2", 6,
                            pid == 1 & s$PID_Rep_Strength == "1", 7)]][, pid := NULL]
d <- merge(d, cv, by = "rid")
ids <- sort(unique(d$rid)); d[, id := match(rid, ids)][, rid := NULL]
for (o in c("choice", "choice_voice", "choice_governability", "choice_responsiveness"))
  stopifnot(d[!is.na(get(o)), sum(get(o)), .(id, task)][, all(V1 == 1)])
stopifnot(uniqueN(d$id) == 2177, nrow(d) == 12842)
setcolorder(d, c("id", "task", "profile", "choice", "choice_voice", "choice_governability", "choice_responsiveness",
                 paste0("attr_", attrs), paste0("attrpos_", attrs)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mayne_2026_electoral_reform.csv"))
