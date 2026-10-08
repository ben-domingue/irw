##Muslim-candidate information conjoint (Norway) from
##Finseraas, H., & Heim, R. (2026; year of the Dataverse deposit, Aug 2026). What drives voter bias against Muslim politicians? An
##experimental examination. Political Behavior (replication deposit in the journal's dataverse; the
##published article was not found, so no article DOI).
##Replication data: Harvard Dataverse doi:10.7910/DVN/A1OKBZ, CC0 1.0. File read:
##experimental_data.dta (Dataverse "original format" download). Design from README.pdf, the authors'
##analysis_experimental_data.do (read as text, not run) and the authors' public working-paper draft
##(muslim_draft_aug8.pdf, linked from Finseraas's NTNU page): research design and Table 1.
##Usage: Rscript finseraas_2026_muslim.R <dir holding experimental_data.dta> <output dir>
##
##Two independent samples from Verian's Norwegian online panel, pooled here because the authors pool
##them ("As pre-registered, we include this data in the second-stage to improve statistical power"):
##  trial_stage = 1: first-stage survey, 629 respondents, baseline attributes only (source group 0).
##  trial_stage = 2: second-stage survey, 2,542 respondents (the draft's N) randomized with equal
##    probability to five arms (trial_arm, source `group`): 1 baseline only, 2 + party label,
##    3 + general policy positions (urban/rural spending, Ukraine, EU), 4 + minority-rights positions
##    (refugees, Pride flag, discrimination law), 5 + personal characteristics (network, personal
##    votes, social media). Stage 1 rows have trial_arm = 0. Attributes not shown in an arm are "(not shown)".
##The source responseid restarts across the two samples (592 ids occur in both and are different
##people: the draft says the samples are independent), so id is re-keyed by (stage, responseid).
##6 tasks (source `round`) of 2 candidates (source `candidate`) per respondent; task and profile are
##recorded. The draft says the sixth pair repeats the first with the two profiles swapped (to measure
##swapping error); the table keeps it as task 6, with trial_repeat_of = 1 on its rows (NA on tasks
##1-5). Checked: task 6's two profiles are task 1's with positions swapped for every respondent.
##Outcome: choice = selected, forced choice between the two candidates (the draft speaks of voters'
##"willingness to vote for them"; the verbatim Norwegian question is not in the deposit or draft).
##No opt-out; exactly one candidate chosen in every pair.
##Attribute text: respondents presumably saw Norwegian (not stated in the material read). The deposit's English value labels are used (gender,
##age "Age: 30", occupation, family situation, experience, religion, and the arm-specific
##attributes), except party, whose deposit labels are Norwegian abbreviations (Ap, SV, Sp, V, H, FrP)
##and are written out with the draft's Table 1 English names (Labour Party, Socialist Left Party,
##Center Party, Liberal Party, Conservative Party, Progress Party). Table 1's wording differs from
##the deposit labels in places (e.g. "care worker" where the deposit says "Nurse"), and how religion
##was displayed (a stated religion or a name) is not documented in the material read.
##Randomization: "independent, and all levels within an attribute had the same probability of
##selection"; attribute order randomized across respondents but fixed across tasks (not recorded).
##Covariates: cov_age; cov_gender from the 0/1 dummy female (variable label "Female", so 1 = female,
##0 = male); cov_high_education (the authors' 0/1 "High education" dummy, the only education variable in
##the deposit; kept under its name); cov_paid_work; cov_left_right (0-1, higher = right). Check: the baseline Muslim-vs-Christian AMCE (arms 0-1) is -0.093, the draft's "9 percentage
##points". Dropped: municipality, post-task evaluation items, the authors' derived flags (baseline,
##leftist, rightist, id_round).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "experimental_data.dta"))
lab <- function(v) { x <- as.character(as_factor(k[[v]], levels = "labels")); x[is.na(k[[v]])] <- NA_character_; x }
s <- data.table(stage = ifelse(k$group == 0, 1L, 2L), rid = as.integer(k$responseid), task = as.integer(k$round),
                profile = as.integer(k$candidate), choice = as.integer(k$selected), trial_arm = as.integer(k$group))
s[, trial_stage := stage]
for (v in c("gender", "age", "occupation", "familysit", "experience", "religion", "party", "cities", "ukraine", "eu",
            "immigration", "pride", "discrimination", "network", "persvotes", "socialmedia"))
  s[, paste0("attr_", v) := lab(paste0("c_", v))]
party <- c(Ap = "Labour Party", SV = "Socialist Left Party", Sp = "Center Party", V = "Liberal Party", H = "Conservative Party", FrP = "Progress Party")
stopifnot(all(na.omit(s$attr_party) %in% names(party)))
s[, attr_party := unname(party[attr_party])]
arm <- list(`2` = "party", `3` = c("cities", "ukraine", "eu"), `4` = c("immigration", "pride", "discrimination"),
            `5` = c("network", "persvotes", "socialmedia"))
for (g in names(arm)) for (v in paste0("attr_", arm[[g]])) {
  stopifnot(s[trial_arm == as.integer(g), !anyNA(get(v))], s[trial_arm != as.integer(g), all(is.na(get(v)))])
  s[trial_arm != as.integer(g), (v) := "(not shown)"]
}
stopifnot(!anyNA(s[, grep("^attr_", names(s)), with = FALSE]))
s[, `:=`(cov_age = as.numeric(k$age), cov_gender = c("male", "female")[as.integer(k$female) + 1L], cov_high_education = as.integer(k$highedu),
         cov_paid_work = as.integer(k$paidwork), cov_left_right = as.numeric(k$rightwing))]
stopifnot(s[, .N, .(stage, rid)][, all(N == 12)], !anyDuplicated(s[, .(stage, rid, task, profile)]))
stopifnot(s[, sum(choice), .(stage, rid, task)][, all(V1 == 1)], s[, uniqueN(trial_arm), .(stage, rid)][, all(V1 == 1)])
key <- unique(s[, .(stage, rid)])[order(stage, rid)][, id := .I]
s <- merge(s, key, by = c("stage", "rid"))[, c("stage", "rid") := NULL]
s[, trial_repeat_of := fifelse(task == 6L, 1L, NA_integer_)]
stopifnot(s[trial_stage == 1, uniqueN(id)] == 629, s[trial_stage == 2, uniqueN(id)] == 2542)
setcolorder(s, c("id", "task", "profile", "choice"))
setorder(s, id, task, profile)
fwrite(s, file.path(out, "finseraas_2026_muslim_candidates.csv"))
