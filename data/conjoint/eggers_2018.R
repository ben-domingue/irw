##Incumbent-vs-challenger vote conjoint (UK) from
##Eggers, A. C., Vivyan, N., & Wagner, M. (2018). Corruption, accountability, and gender: Do
##female politicians face higher standards in public life? The Journal of Politics, 80(1),
##321-326. https://doi.org/10.1086/694649
##Replication data: Harvard Dataverse doi:10.7910/DVN/MOTRM2, CC0 1.0, no restricted files.
##File read: experiment_data.rds. Design and wording from the accepted manuscript (Eggers'
##Dropbox copy, JOP_submission_FINAL_maintext.pdf), p. 5 and Figure 1 (screenshot of a task).
##Usage: Rscript eggers_2018.R <raw dir> <output dir>
##
##1,962 YouGov respondents (British voters, 2-3 June 2014), 5 vignettes each ("comparison" =
##task in the order shown; the authors' code treats comparison == 1 as the first task). Each
##vignette is a marginal constituency contest: profile 1 = the current MP (incumbent),
##profile 2 = the main challenger. Both show party (with logo), age, gender and former job;
##only the MP has a conduct line, so attr_conduct is "(not shown)" for the challenger.
##  attr_party: from seat.type (ConLab = Conservative MP, Labour challenger; ConLib, LabCon,
##     LabLib likewise; Figure 1 shows a ConLab seat). The vignette text "This is a marginal
##     constituency won narrowly by the <MP party> at the last election. Based on polls, the
##     only other party with a chance of winning this seat are <challenger party>" follows
##     from the same two parties.
##  attr_age "<n> years old": MP 45/52/64, challenger 38/51/62 (the data and the Figure 1
##     screenshot, "62 years old"; the article text says 40/52/64 for the challenger).
##  attr_gender Female/Male; attr_previous_job "Formerly a GP" etc. (5 jobs, as in Figure 1).
##  attr_conduct (MP only): "Last year, the current MP received a commendation for diligent
##     and ethical service from a Westminster watchdog" (good) or "Last year, the current MP
##     was found to have inappropriately claimed over £10,000 on expenses." (bad; Figure 1
##     wording; the article text says "£10,000 in expenses").
##choice: "If you were living in this constituency at the next general election, which party
##  would you vote for?" Options: the current <party> MP (profile 1), the <party> challenger
##  (profile 2), the <third party> candidate, a candidate from another party, or "No one, I
##  would not vote". The last three are opt-outs (choice = 0 on both profiles): 4,305 of
##  9,810 tasks. Every task has exactly one answer.
##Restrictions: MP is Labour or Conservative, the challenger always a different party (only
##  the 4 seat types above occur); age levels differ by role. Otherwise randomized per the
##  article; uniformity not stated.
##Covariates: cov_female (respondent), cov_agegroup, cov_socialgrade (ABC1/C2DE), as deposited.
##Dropped: incid/chaid/minorid (respondent identifies with the MP's / challenger's / another
##  party: task-level derived flags), agegroup.1 (copy of agegroup), the 0/1 dummies
##  mp.female/cha.female (same as attr_gender). No survey weight is deposited.
##N = 1,962 matches the article. Spot check: lm(voteinc ~ mp.misconduct + mp.female +
##  resp.female) on profile 1 reproduces Table 1 col. 1 exactly (0.406, -0.240, 0.014, -0.008).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "experiment_data.rds")))
stopifnot(x[, .N, id][, all(N == 5)], x[, all(voteinc + votecha + voteoth + voteabstain == 1)])
pty <- c(Con = "Conservative", Lab = "Labour", Lib = "Liberal Democrat")
st <- as.character(x$seat.type); stopifnot(all(st %in% c("ConLab", "ConLib", "LabCon", "LabLib")))
sexlab <- function(f) ifelse(f == 1, "Female", "Male")
conduct <- ifelse(x$mp.misconduct == 1, "Last year, the current MP was found to have inappropriately claimed over £10,000 on expenses.",
                  "Last year, the current MP received a commendation for diligent and ethical service from a Westminster watchdog")
stopifnot(all(x$cha.sex == sexlab(x$cha.female)))
mk <- function(p) {
  inc <- p == 1L
  data.table(id = as.integer(x$id), task = as.integer(x$comparison), profile = p,
             choice = as.integer(if (inc) x$voteinc else x$votecha),
             attr_party = unname(pty[if (inc) substr(st, 1, 3) else substr(st, 4, 6)]),
             attr_age = paste(if (inc) x$mp.age else x$cha.age, "years old"),
             attr_gender = sexlab(if (inc) x$mp.female else x$cha.female),
             attr_previous_job = paste("Formerly", as.character(if (inc) x$mp.prevjob else x$cha.prevjob)),
             attr_conduct = if (inc) conduct else "(not shown)",
             cov_female = as.integer(x$resp.female), cov_agegroup = as.character(x$agegroup),
             cov_socialgrade = as.character(x$socialgrade))
}
d <- rbind(mk(1L), mk(2L))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)], !anyNA(d$attr_party))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "eggers_2018_mp_misconduct.csv"))
