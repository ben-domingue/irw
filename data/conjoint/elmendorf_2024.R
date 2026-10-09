##Platform-choice conjoint on state housing and other policy positions (US) from
##Elmendorf, C. S., Nall, C., & Oklobdzija, S. (2024). What state housing policies do voters want?
##Evidence from a platform-choice experiment. Journal of Political Institutions and Political
##Economy, 5(1), 117-152. https://doi.org/10.1561/113.00000096 (not read)
##Replication data: Harvard Dataverse doi:10.7910/DVN/U7ABJF, CC0 1.0, no restricted files. The
##deposit's NEO_PIPE.qmd (pre-analysis plan + replication code, read as text, not run) is the
##design source.
##File read: "NEO - Housing Policy Efficacy Survey (2024)_March 13, 2024_14.39-1.tab" (Dataverse
##original-format download, the raw Qualtrics numeric export, 2024 survey; row 1 names, rows 2-3
##question text and ImportId, then data).
##Usage: Rscript elmendorf_2024.R <dir holding NEO.csv (that .tab, original format, renamed)> <output dir>
##
##Design (qmd "Block 5: Policy Priorities Conjoint"): after stating their own positions on 10
##issues, each respondent made 5 choices between two 3-policy platforms, "Set A" and "Set B":
##"Question k of 5. Given this choice, which set of positions would you prefer?" The two sets hold
##the same three issues with contrary positions (e.g. "Increase taxes on the wealthy" vs "Reduce
##taxes on the wealthy"), drawn from 17 housing and 22 non-housing issues; only the position text
##is shown, one row per issue (the issue name is not displayed in these 5 tasks). Forced choice
##between the sets (codes 1 = Set A, 2 = Set B; the qmd recodes '1' ~ 1 for Set A); no opt-out.
##Layout: one attribute per ISSUE (39 issues, column names from the Qualtrics issue codes
##c_i_code_k, e.g. attr_taxes_upper): the position text shown for that issue in that set, or
##"(not shown)" when the issue is not in the task; attrpos_<issue> = its row (1-3) in the task, NA
##when not shown. Embedded fields: c_i_code_<3(t-1)+r>, c_i_position_A_.., c_i_position_B_.. for
##task t, row r. Issues are drawn per task, not restricted further in the export (restrictions:
##the two profiles of a task always take the two opposite positions of the same three issues).
##Task 6 = the retest of task 1 (Q14.6, block 6, shown later in the survey) with the sets SWAPPED
##(left column "Set A" shows the original Set B positions) and, by the authors' oversight (qmd
##L4838), an extra "Issue" column naming each issue; trial_repeat_of = 1 on its rows. Its wording:
##"Give this choice, which set of positions would you prefer?" (sic). Profile 1 = left column.
##Sample (as the qmd): Finished == 1, passed the two screening/attention items (Q2.1 == 1,
##Q2.2 == "1,2"), and not a speeder (duration > 1/3 of the median duration among those kept).
##Tasks without an answer omitted. Covariates: cov_state (State embedded field, as text),
##cov_duration_sec (Qualtrics "Duration (in seconds)", whole survey). The rest of the survey
##(efficacy pairs, own policy positions, demographics) is not carried here.
##Dropped and NOT redistributed: IP addresses, LocationLatitude/Longitude (PII in the deposit's
##raw export), the Forthright panel ID (PID), Qualtrics ResponseId (re-keyed to integers),
##browser metadata, free text.
##N: 6,050 records in the export; 5,127 respondents after the qmd's filters, with at least one
##answered task (the article's count was not checked; press coverage says a national online survey
##of about 5,000 urban and suburban adults). Spot check: when taxes on the wealthy is in the task,
##the set with "Increase taxes on the wealthy" is chosen 68% of the time; 81% of retest answers
##(task 6) pick the same platform as task 1.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
keep <- c("ResponseId", "Finished", "Q2.1", "Q2.2", "Duration (in seconds)", "State",
          paste0("Q13.", c(2, 4, 6, 8, 10)), "Q14.6",
          paste0("c_i_code_", 1:15), paste0("c_i_position_A_", 1:15), paste0("c_i_position_B_", 1:15))
s <- fread(file.path(raw, "NEO.csv"), select = keep, colClasses = "character", encoding = "UTF-8")
stopifnot(grepl("ImportId", s$ResponseId[2]))   # rows 1-2: question text and ImportId
s <- s[-(1:2)]
s <- s[Finished == "1" & Q2.1 == "1" & Q2.2 == "1,2"]
s[, dur := as.numeric(`Duration (in seconds)`)]
s <- s[dur > median(dur, na.rm = TRUE) / 3]
s[, id := seq_len(.N)]
q <- paste0("Q13.", c(2, 4, 6, 8, 10))
L <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:3, function(r) {
  k <- 3 * (t - 1) + r
  data.table(id = s$id, task = t, pos = r, issue = s[[paste0("c_i_code_", k)]],
             A = s[[paste0("c_i_position_A_", k)]], B = s[[paste0("c_i_position_B_", k)]], y = s[[q[t]]])
}))))
# retest of task 1, sets swapped: left column (profile 1) shows the B positions
L <- rbind(L, L[task == 1][, `:=`(task = 6L, y = s$Q14.6[match(id, s$id)], tmp = A)][, `:=`(A = B, B = tmp)][, tmp := NULL])
L <- L[y %in% c("1", "2")]
stopifnot(all(L$issue != ""), all(L$A != "" & L$B != "" & L$A != L$B), L[, .N, .(id, task)][, all(N == 3)],
          L[, uniqueN(issue), .(id, task)][, all(V1 == 3)])
# each issue has exactly two position texts, always opposite across the two sets
pp <- unique(rbind(L[, .(issue, p = A)], L[, .(issue, p = B)]))
stopifnot(pp[, .N, issue][, all(N == 2)], uniqueN(L$issue) == 39)
iss <- sort(unique(L$issue)); cn <- gsub("[^a-z0-9]+", "_", tolower(iss))
P <- rbind(L[, .(id, task, profile = 1L, pos, issue, txt = A, y)], L[, .(id, task, profile = 2L, pos, issue, txt = B, y)])
d <- unique(P[, .(id, task, profile, choice = as.integer(y == as.character(profile)))])
for (i in seq_along(iss)) {
  x <- P[issue == iss[i]]
  d[x, on = .(id, task, profile), `:=`(a = i.txt, p = i.pos)]
  d[is.na(a), a := "(not shown)"]
  setnames(d, c("a", "p"), paste0(c("attr_", "attrpos_"), cn[i]))
}
d[, trial_repeat_of := fifelse(task == 6L, 1L, NA_integer_)]
d[, `:=`(cov_state = s$State[id], cov_duration_sec = as.integer(s$dur[id]))]
d[cov_state == "", cov_state := NA]
d[, id := match(id, sort(unique(id)))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)])
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "elmendorf_2024_housing_platforms.csv"))
cat(uniqueN(d$id), "respondents", nrow(d), "rows\n")
