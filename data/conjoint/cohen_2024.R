##Polling-location conjoints (three US studies) from
##Cohen, M. J., & Sheagley, G. (2024). Partisan poll watchers and Americans' perceptions of
##electoral fairness. Public Opinion Quarterly, 88(SI), 536-560.
##https://doi.org/10.1093/poq/nfae024
##Replication data: Harvard Dataverse doi:10.7910/DVN/MDQS4H, CC0 1.0. Files read:
##Study1_Clean.csv, Study2_Clean.csv (Qualtrics exports, wide), study3_conjointdata_wave1.dta
##(long, 6 rows per respondent). The authors' R code (dataformatting_study1/2.R,
##dataanalysis_study1/2.R, analyses_study3_conjointReplication.R) and ReadMe.txt read as
##text. The article was not accessible; design and outcome descriptions come from the
##AsPredicted pre-registrations #62225 (2021-03-30, Study 1) and #88510 (2022-02-18,
##Study 2): "a binary indicator measuring which of two hypothetical polling locations
##would conduct an election more fairly" / "would have fairer results", and "a five-point
##measure of the intensity of this belief" for each location. Exact question wording and
##scale anchors are not in the deposit.
##Usage: Rscript cohen_2024.R <dir holding the three files> <output dir>
##
##Three separate experiments -> three tables (different fieldings, and the poll-watcher
##and vote-method level sets differ):
## cohen_2024_poll_watchers_s1: Study 1 (2021, Bovitz online panel per prereg), 6 pairs of
##   polling locations; watchers = state / party / both, with or without badges.
## cohen_2024_poll_watchers_s2: Study 2 (2022), 5 pairs; watchers = Democratic /
##   Republican / both, with or without badges; 4 vote methods.
## cohen_2024_poll_watchers_s3: Study 3 conjoint ("Study 3 (Replication)" in the authors'
##   code), 3 pairs; watcher wording "... Party poll watchers", 6 vote methods. The file
##   has NO task or profile column. It is three stacked blocks of 3,570 rows (1,785
##   respondents x 2, each block sorted by ResponseId, each respondent twice in a row);
##   task = block (1-3) and profile = row within the respondent's pair are INFERRED from
##   row order. Check: every
##   pair has at most one chosen, and for the 1,555 respondents who chose in all three
##   tasks every pair has exactly one; the first row of a pair is chosen 51% of answered
##   pairs. Task numbers therefore need not be the display order, and profile 1/2 need
##   not be left/right.
##Tasks, profiles (S1, S2): task = Qualtrics choice<k> block, profile = location 1/2
##(choice<k>_<attr>1/2, recorded). Attribute text = the strings in the export (leading
##space in " Photo ID + Signature on Sign in" trimmed). Respondents whose attribute
##fields are empty (S1: 2, S2: 4; the authors drop the same rows by row number, S3: 8
##respondents' tasks with NA attributes) are dropped.
##Outcomes:
##  choice: which of the two polling locations would conduct the election more fairly
##    (paraphrase of prereg; source <k>_pref = 1/2, S3 `chosen`). Forced choice, no
##    opt-out; tasks left unanswered are NA (S1/S2 keep the task if an intensity rating
##    was given, else omit it). S3: tasks with no chosen profile (657 of 5,355; 207
##    respondents chose none) are treated as unanswered and omitted, as the authors'
##    code drops them.
##  rating (S1, S2 only): five-point intensity of the fairness belief for each location
##    (<k>_intensity_1/2, S2 <k>_int_1/2), 1-5 stored raw. Direction: higher = fairer is
##    INFERRED (the chosen location has the higher rating in 92% of tasks with unequal
##    ratings; the authors analyse int1 - int2 as preference for location 1). Anchors
##    unknown.
##Restrictions: none (prereg: attributes "will vary at random across the listed values").
##Covariate: cov_pid3_lean = the authors' party-ID recode with leaners folded in
##(Democrat / Republican / Independent; S1 from Q3/Q6, S2 Q7/Q10, S3 `pid` value labels).
##Dropped: Qualtrics ResponseId and the panel's RESPONDENT_ID (platform IDs; re-keyed),
##free-text answers (Q3_4_TEXT, Q35_7_TEXT, Q8-Q10 open definitions of poll watchers in
##S1; Q7_4_TEXT, Q4_7_TEXT in S2), all other survey items (unlabelled Qualtrics codes),
##S2's separate vignette treatments (treat_*, carlos_parent), state codes. No weights.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c("id", "votemethod", "watcher", "speech", "wait", "registration")
nm <- c(id = "attr_voter_id", votemethod = "attr_vote_method", watcher = "attr_poll_watchers",
        speech = "attr_campaigning", wait = "attr_wait_time", registration = "attr_registration")
wide <- function(f, ntask, intpat, pid) {
  s <- fread(file.path(raw, f), encoding = "Latin-1", colClasses = "character")
  s[, rid := .I]
  s[, cov_pid3_lean := pid(s)]
  L <- rbindlist(lapply(1:ntask, function(k) rbindlist(lapply(1:2, function(p) {
    x <- s[, c("rid", "cov_pid3_lean", paste0("choice", k, "_", attrs, p), paste0(k, "_pref"), sprintf(intpat, k, p)), with = FALSE]
    setnames(x, c("rid", "cov_pid3_lean", nm[attrs], "pref", "int"))
    x[, `:=`(task = k, profile = p)]
  }))))
  for (v in nm) L[, (v) := trimws(get(v))]
  bad <- L[, any(sapply(.SD, function(z) is.na(z) | z == "")), by = rid, .SDcols = nm][V1 == TRUE, rid]
  L <- L[!rid %in% bad]
  L[, pref := as.integer(pref)][, rating := as.integer(int)]
  L[, choice := fifelse(is.na(pref), NA_integer_, as.integer(pref == profile))]
  L <- L[L[, .(keep = any(!is.na(choice) | !is.na(rating))), .(rid, task)], on = .(rid, task)][keep == TRUE]
  L[, id := as.integer(frank(rid, ties.method = "dense"))]
  list(d = L[, c("id", "task", "profile", "choice", "rating", nm, "cov_pid3_lean"), with = FALSE], nbad = length(bad))
}
pidfun <- function(q1, q2) function(s) {
  a1 <- suppressWarnings(as.integer(s[[q1]])); a2 <- suppressWarnings(as.integer(s[[q2]]))
  fcase(a1 %in% 1 | a2 %in% 2, "Democrat", a1 %in% 2 | a2 %in% 1, "Republican", a2 %in% 3, "Independent", default = NA_character_)
}
r1 <- wide("Study1_Clean.csv", 6, "%d_intensity_%d", pidfun("Q3", "Q6"))
r2 <- wide("Study2_Clean.csv", 5, "%d_int_%d", pidfun("Q7", "Q10"))
stopifnot(r1$nbad == 2, r2$nbad == 4)
for (r in list(r1, r2)) stopifnot(r$d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], r$d[, .N, .(id, task)][, all(N == 2)],
                                  r$d[, all(is.na(rating) | rating %in% 1:5)])
# Study 3 (long file, task/profile inferred from row order)
s3 <- as.data.table(read_dta(file.path(raw, "study3_conjointdata_wave1.dta")))
stopifnot(nrow(s3) == 3 * 3570, s3[, .N, ResponseId][, all(N == 6)])
s3[, task := (seq_len(.N) - 1L) %/% 3570L + 1L][, profile := seq_len(.N), .(task, ResponseId)]
stopifnot(s3[, uniqueN(ResponseId), task][, all(V1 == 1785)], all(s3$profile %in% 1:2),
          rle(as.character(s3$ResponseId))$lengths == 2)
for (v in attrs) s3[, (nm[[v]]) := trimws(as.character(as_factor(get(v))))]
s3[, cov_pid3_lean := as.character(as_factor(pid))]
s3[, rid := frank(ResponseId, ties.method = "dense")]
bad3 <- s3[, any(is.na(.SD)), by = rid, .SDcols = unname(nm)][V1 == TRUE, rid]
s3 <- s3[!rid %in% bad3]
s3[, choice := as.integer(chosen)]
s3 <- s3[s3[, .(k = sum(choice)), .(rid, task)][k == 1], on = .(rid, task)]
s3[, id := as.integer(frank(rid, ties.method = "dense"))]
d3 <- s3[, c("id", "task", "profile", "choice", unname(nm), "cov_pid3_lean"), with = FALSE]
stopifnot(length(bad3) == 8, d3[, sum(choice), .(id, task)][, all(V1 == 1)], d3[, .N, .(id, task)][, all(N == 2)])
for (x in list(list(r1$d, "s1"), list(r2$d, "s2"), list(d3, "s3"))) {
  d <- x[[1]]; setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("cohen_2024_poll_watchers_", x[[2]], ".csv")))
}
