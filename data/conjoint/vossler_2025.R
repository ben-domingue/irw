##Farmworker-assistance project DCE (incentivized online field experiment, New York) from
##Vossler, C. A., & Zawojska, E. (2025). From simple to complex: A revealed preference test of
##discrete choice experiment designs. Journal of the Association of Environmental and Resource
##Economists (manuscript 2025232; DOI not given in the deposit).
##Replication data: Harvard Dataverse doi:10.7910/DVN/KP7PU4, CC0 1.0, no restricted files.
##File read: DCE_field_raw.dta. Level text, wording and the arm/question/level mapping from
##"Farmworker DCE survey.pdf" (Qualtrics instrument) and DCE_field_log.pdf (the authors'
##annotated Stata log, steps 21-67 and the Single-BC / Seq-BC / Seq-TC expansion blocks), read
##as text; the do-file itself is not in the deposit.
##Usage: Rscript vossler_2025.R <raw dir> <output dir>
##
##1,200 New York residents (Prolific; one survey, EN). Each started with $15; groups of 50 voted on
##projects run by the Cornell Farmworker Program, and one vote was binding (real payment).
##A project = Educational materials (sets of English workbooks & sets of children's books:
##"1 of each set"/"3 of each set"/"5 of each set"), Winter clothing (gloves, coats & blankets:
##"1 of each item"/"3 ..."/"5 ..."), Emergency transportation services ("1 service provided"/
##"2 services provided"/"3 services provided") and "Cost to you" ($5, $8, $11 or $15, random per
##respondent and question). The fixed "No project" column (None, None, None, $0) is the opt-out,
##not a profile. Question: "Which option do you vote for?"
##Three randomized arms, ONE table (one experiment, one attribute set, one fielding; the authors
##compare the arms in one analysis), arm in trial_mechanism:
##  single_binary (treatment 1, n = 600): one question, project vs no project; half saw the small
##     project S3 (1 set, 3 items, 1 service; Q149) and half the large L3 (3, 5, 3; Q161).
##  sequential_binary (treatment 2, n = 300): 9 questions (Q203, Q131-Q145), project vs no project.
##  sequential_trinary (treatment 4, n = 300): 9 questions (Q66, Q206-Q241), Project A vs Project B
##     vs no project; profile 1 = Project A, 2 = Project B.
##The nine projects are fixed (a fixed design; the authors' S1-S3, M1-M3, L1-L3); only costs vary.
##task = display position (task_order_k, recorded, a permutation of 1-9 per respondent);
##trial_question = k, the question's number in the instrument. choice = 1 for the project voted
##for; "No project" = 0 on all profiles (opt-out).
##Covariates (answer text): cov_gender (Q55: Male/Female/"Do not identify myself as male or
##female" = other), cov_age (Q56, years), cov_education (Q58), cov_race (Q57), cov_marital
##(Q59), cov_employment (Q60), cov_income (Q61), cov_ny_tenure (Q62), cov_residence (Q245
##Rural/Suburban/Urban; asked only of the second 600, NA for the first 600 per the log),
##cov_donated (Q52), cov_adults (Q63), cov_children (Q64), cov_device (Q65),
##cov_vote_as_if_binding (Q86, trinary arm), cov_duration_sec (whole survey).
##PII dropped: PROLIFIC_PID, Q247 and Q187 (Prolific IDs re-entered), ResponseId, timestamps;
##IP/location columns are blank or masked. Free text (Q60_7_TEXT) and the comprehension and
##attitude items are not kept. id = RespondentID.
##N = 1,200 (600/300/300), as in the log's treatment counts.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "DCE_field_raw.dta")))
stopifnot(nrow(s) == 1200L, all(s$treatment %in% c(1, 2, 4)), !anyDuplicated(s$RespondentID))
lv <- function(e, c, t) list(e = paste(e, "of each set"), c = paste(c, "of each item"),
                             t = ifelse(t == 1, "1 service provided", paste(t, "services provided")))
# binary question k: (edu, cloth, trans); from the instrument and the log (Seq-BC block)
bc <- rbind(c(1,3,1), c(3,5,3), c(3,1,1), c(1,1,3), c(5,1,2), c(5,3,3), c(3,3,2), c(5,5,1), c(1,5,2))
# trinary question k: Project A then Project B (Seq-TC block)
tcA <- rbind(c(3,5,3), c(1,3,1), c(5,5,1), c(3,1,1), c(1,5,2), c(1,1,3), c(5,3,3), c(5,1,2), c(3,3,2))
tcB <- rbind(c(1,3,1), c(5,1,2), c(1,1,3), c(5,3,3), c(3,1,1), c(3,3,2), c(1,5,2), c(3,5,3), c(5,5,1))
mk <- function(id, task, profile, q, e, c, t, cost, ch, arm) {
  l <- lv(e, c, t)
  data.table(id = as.integer(id), task = as.integer(task), profile = as.integer(profile), choice = as.integer(ch),
             attr_educational_materials = l$e, attr_winter_clothing = l$c, attr_emergency_transport = l$t,
             attr_cost = paste0("$", cost), trial_mechanism = arm, trial_question = as.integer(q))
}
yn <- function(x, yes) { stopifnot(all(x %in% c(yes, "No project"))); as.integer(x == yes) }
# single binary
s1 <- s[treatment == 1]
v1 <- fifelse(s1$small_asked == "yes", s1$Q149, s1$Q161)
big <- s1$small_asked == "no"
d1 <- mk(s1$RespondentID, 1, 1, NA, ifelse(big, 3, 1), ifelse(big, 5, 3), ifelse(big, 3, 1), s1$Cost1a,
         yn(v1, "Project"), "single_binary")
# sequential binary
s2 <- s[treatment == 2]
bq <- c("Q203", "Q131", "Q133", "Q135", "Q137", "Q139", "Q141", "Q143", "Q145")
d2 <- rbindlist(lapply(1:9, function(k) mk(s2$RespondentID, s2[[paste0("task_order_", k)]], 1, k, bc[k, 1], bc[k, 2], bc[k, 3],
                                            s2[[paste0("Cost", k, "a")]], yn(s2[[bq[k]]], "Project"), "sequential_binary")))
# sequential trinary
s4 <- s[treatment == 4]
tq <- c("Q66", "Q206", "Q211", "Q216", "Q221", "Q226", "Q231", "Q236", "Q241")
d4 <- rbindlist(lapply(1:9, function(k) {
  v <- s4[[tq[k]]]; stopifnot(all(v %in% c("Project A", "Project B", "No project")))
  rbind(mk(s4$RespondentID, s4[[paste0("task_order_", k)]], 1, k, tcA[k, 1], tcA[k, 2], tcA[k, 3], s4[[paste0("Cost", k, "a")]],
           as.integer(v == "Project A"), "sequential_trinary"),
        mk(s4$RespondentID, s4[[paste0("task_order_", k)]], 2, k, tcB[k, 1], tcB[k, 2], tcB[k, 3], s4[[paste0("Cost", k, "b")]],
           as.integer(v == "Project B"), "sequential_trinary"))
}))
d <- rbind(d1, d2, d4)
stopifnot(!anyNA(d$task), all(d$attr_cost %in% c("$5", "$8", "$11", "$15")))
g <- s$Q55; stopifnot(all(g %in% c("Male", "Female", "Do not identify myself as male or female")))
blank <- function(x) fifelse(x == "", NA_character_, x)
cv <- data.table(id = as.integer(s$RespondentID),
                 cov_gender = c(Male = "male", Female = "female", "Do not identify myself as male or female" = "other")[g],
                 cov_age = suppressWarnings(as.integer(s$Q56)), cov_education = blank(s$Q58), cov_race = blank(s$Q57),
                 cov_marital = blank(s$Q59), cov_employment = blank(s$Q60), cov_income = blank(s$Q61), cov_ny_tenure = blank(s$Q62),
                 cov_residence = blank(s$Q245), cov_donated = blank(s$Q52), cov_adults = blank(s$Q63), cov_children = blank(s$Q64),
                 cov_device = blank(s$Q65), cov_vote_as_if_binding = blank(s$Q86),
                 cov_duration_sec = as.integer(s$Durationinseconds))
d <- merge(d, cv, by = "id")
stopifnot(uniqueN(d$id) == 1200L, d[, sum(choice), .(id, task)][, all(V1 <= 1)],
          d[trial_mechanism != "single_binary", uniqueN(task), id][, all(V1 == 9)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vossler_2025_farmworker_projects.csv"))
