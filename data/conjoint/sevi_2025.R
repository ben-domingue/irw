##Mayoral-candidate conjoint (promise keeping x candidate gender) from
##Sevi, S., Crabtree, C., & Blais, A. Do voters punish women politicians more? The deposit
##names American Politics Research; no published version was found (2026-10-23), so the
##table year is the deposit's.
##Replication data: OSF https://osf.io/mgkup/, CC BY 4.0. The OSF licence field was empty
##until the depositor set CC BY 4.0 on 2026-10-23 in reply to an IRW licence ask
##(oneoff/licence-asks-2026-10/outbox/mgkup_sevi.txt). File read:
##"gender_October 15, 2021_02.06.csv", the raw Qualtrics export. analyses.Rmd was read as
##text (not run) for the outcome coding and the authors' sample filters.
##Usage: Rscript sevi_2025.R <raw dir> <output dir>
##
##A nationally representative US sample fielded through Lucid Theorem on 28 July 2021
##(analyses.Rmd). Each respondent saw 7 pairs of hypothetical city-council candidates and
##said which they would vote for as mayor. 5 attributes, 12 levels:
##  attr_gender             Man / Woman
##  attr_leadership_style   Decisive / Looks for compromises
##  attr_policy_priority    Build new schools / Increase recycling / Keep taxes low
##  attr_previous_term      Kept all of their promises / Broke most of their promises
##  attr_occupation         Businessperson / Lawyer / Teacher
##Attribute ORDER was randomized once per respondent and is identical across that
##respondent's 7 tasks (checked below), so attrpos_* give the row each attribute occupied.
##Levels are the text displayed in the Qualtrics table (F-<task>-<row> names the attribute
##in row <row>, F-<task>-<profile>-<row> gives its level).
##
##Outcome: choice = Q17, Q19, Q21, Q23, Q25, Q27, Q29 for tasks 1-7, "Candidate 1" or
##"Candidate 2" (the authors' recode, analyses.Rmd L49-58), so exactly one profile of each
##task is chosen and opt_out = no. Question wording, verbatim from the export's question-text
##row: "Suppose you lived in that city. Which of these two candidates would you be likely to
##vote for mayor?"
##
##Sample. 2,107 response rows. Kept: the 2 Qualtrics preview responses are dropped
##(Status "Survey Preview"), consent must be "Yes" (Q2), and a task is kept only when it has
##a choice; that leaves 1,971 respondents and 27,402 rows. 1,948 of them answered all 7
##tasks and the other 23 answered between one and six, so the per-task counts fall slightly.
##This is WIDER than the paper's analysis sample of 1,495, which also requires
##Finished == "True" and both attention checks passed (analyses.Rmd L159-165, L211). The two
##checks are kept as covariates instead, so that sample can be reconstructed:
##  cov_attention_pass_1  Q3, 1 = "I understand."
##  cov_attention_pass_2  Q4, 1 = "Extremely interested,Very interested" -- the item asks
##                        respondents who are reading to select both options
##Other covariates: cov_gender (Q5 "Do you describe yourself as a man, woman, or in some
##other way?", Man -> male, Woman -> female, "Other (Specify)" -> other), cov_age (Q6,
##years), cov_education (Q10 answer text), cov_race (Q11 answer text, a multi-select whose
##stored value is the chosen option), cov_party_id (Q12 answer text), cov_party_strength
##(Q13/Q14 answer text, asked only of Republicans and Democrats respectively, NA otherwise),
##cov_issue_first and cov_issue_second (Q8, Q9: which of the three policy issues matters most,
##then most among the two remaining), cov_consideration (Q30, asked after the 7 tasks: which
##attribute mattered most), cov_duration_sec (Qualtrics survey duration).
##Dropped: IP address, latitude/longitude, ZIP code, the Lucid respondent id (rid), the
##Qualtrics ResponseId (id is re-keyed to 1..n), the free-text "Other (Specify)" fields
##(Q5_3_TEXT, Q11_6_TEXT, Q30_6_TEXT), start/end/recorded timestamps, Progress, Finished,
##consent, and the Lucid panel columns age/gender/hhi/ethnicity/hispanic/education/region/
##political_party, which repeat the Q items as bare numeric codes with no codebook.
##No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "gender_October 15, 2021_02.06.csv"), colClasses = "character",
           na.strings = "", header = TRUE)
r <- r[-(1:2)]   # question-text and ImportId rows
r <- r[Status != "Survey Preview" & Q2 == "Yes"]
stopifnot(!anyDuplicated(r$ResponseId))
chk <- function(x, lv) { stopifnot(all(is.na(x) | x %in% lv)); x }

ATTRS <- c(gender = "Gender", leadership_style = "Leadership style",
           policy_priority = "Policy priority", previous_term = "Previous Term",
           occupation = "Occupation")
LEVELS <- list(gender = c("Man", "Woman"),
               leadership_style = c("Decisive", "Looks for compromises"),
               policy_priority = c("Build new schools", "Increase recycling", "Keep taxes low"),
               previous_term = c("Broke most of their promises", "Kept all of their promises"),
               occupation = c("Businessperson", "Lawyer", "Teacher"))
QCOL <- c(Q17 = 1, Q19 = 2, Q21 = 3, Q23 = 4, Q25 = 5, Q27 = 6, Q29 = 7)

## the attribute in row k, and its position, per respondent x task
rowname <- function(t, k) chk(r[[sprintf("F-%d-%d", t, k)]], ATTRS)
stopifnot(all(sapply(2:7, function(t) all(sapply(1:5, function(k)
  identical(rowname(t, k), rowname(1, k)))))))   # order fixed within respondent

d <- rbindlist(lapply(seq_along(QCOL), function(t) rbindlist(lapply(1:2, function(p) {
  ch <- chk(r[[names(QCOL)[t]]], c("Candidate 1", "Candidate 2"))
  x <- data.table(rid = seq_len(nrow(r)), task = t, profile = p,
                  choice = as.integer(ch == paste("Candidate", p)))
  for (k in 1:5) {
    nm <- rowname(t, k); lv <- r[[sprintf("F-%d-%d-%d", t, p, k)]]
    for (a in names(ATTRS)) {
      sel <- which(nm == ATTRS[[a]])
      x[sel, paste0("attr_", a) := lv[sel]][sel, paste0("attrpos_", a) := k]
    }
  }
  x
}))))
for (a in names(ATTRS)) {
  d[[paste0("attr_", a)]] <- chk(d[[paste0("attr_", a)]], LEVELS[[a]])
  d[, (paste0("attrpos_", a)) := as.integer(get(paste0("attrpos_", a)))]
}
stopifnot(d[!is.na(choice), .(s = sum(choice)), .(rid, task)][, all(s == 1)],
          d[, all(!is.na(attr_gender))],
          d[, uniqueN(unlist(.SD)) == 5, .SDcols = patterns("^attrpos_"), by = .(rid)][, all(V1)])

cv <- data.table(
  rid = seq_len(nrow(r)),
  cov_gender = c(Man = "male", Woman = "female", `Other (Specify)` = "other")[chk(r$Q5, c("Man", "Woman", "Other (Specify)"))],
  cov_age = as.integer(r$Q6),
  cov_education = chk(r$Q10, c("Grade School", "Some High School", "High School Diploma",
                               "Some College, no Degree", "College Degree/ Post-grad")),
  cov_race = chk(r$Q11, c("White", "Black or African-American", "Asian", "American Indian or Alaska Native",
                          "Native Hawaiian or Pacific Islander", "Other (Specify)")),
  cov_party_id = chk(r$Q12, c("Republican", "Democrat", "Independent", "Other")),
  cov_party_strength = fcoalesce(chk(r$Q13, c("Strong Republican", "Not very strong Republican")),
                                 chk(r$Q14, c("Strong Democrat", "Not very strong Democrat"))),
  cov_issue_first = chk(r$Q8, c("Keep taxes low", "Increasing recycling", "Building new schools")),
  cov_issue_second = chk(r$Q9, c("Keep taxes low", "Increasing recycling", "Building new schools")),
  cov_consideration = chk(r$Q30, c("Gender", "Leadership style", "Occupation", "Policy priority",
                                   "Previous record", "Other")),
  cov_attention_pass_1 = as.integer(chk(r$Q3, c("I understand.", "I do not understand.")) == "I understand."),
  cov_attention_pass_2 = as.integer(!is.na(r$Q4) & r$Q4 == "Extremely interested,Very interested"),
  cov_duration_sec = as.integer(r[["Duration (in seconds)"]]))
cv[is.na(r$Q4), cov_attention_pass_2 := NA_integer_]
stopifnot(all(cv$cov_age %in% c(18:120, NA)), is.na(r$Q13) | is.na(r$Q14))

d <- d[!is.na(choice)]
d <- merge(d, cv, by = "rid")
d[, id := match(rid, sort(unique(rid)))][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
stopifnot(d[, .N, .(id, task)][, all(N == 2)], uniqueN(d$id) > 100)
fwrite(d, file.path(out, "sevi_2025_promise_keeping.csv"))
