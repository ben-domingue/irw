##Mock local-election candidate experiment (plurality vs ranked-choice voting, US) from
##Crowder-Meyer, M., Gadarian, S. K., & Trounstine, J. (2023). Ranking candidates in local
##elections: Neither panacea nor catastrophe for candidates of color. Journal of Experimental
##Political Science, 11(2), 117-134. https://doi.org/10.1017/XPS.2023.6
##Replication data: Harvard Dataverse doi:10.7910/DVN/30EYIE, CC0 1.0. Files read:
##JEPS_replication.dta (original format; Stata value labels) and README.docx.
##JEPS_replication_Final.do read as text, not run.
##Usage: Rscript crowdermeyer_2023.R <dir holding JEPS_replication.dta> <output dir>
##
##Qualtrics sample, fall 2020. Each respondent voted in three mock local elections, one screen
##each (mayor, district council, at-large council), each with 4 candidates shown by NAME only;
##half of the respondents also saw each candidate's party (trial_partisan). The name signals
##race (Black, Latino, Asian American, White) and gender; race, gender and party were randomized
##independently (article). Voting rule (trial_rcv): plurality (choose 1; at-large choose 2) or
##ranked-choice (rank all 4). Wave 2 (trial_wave = 2): 530 wave-1 respondents recontacted six
##weeks later, all under RCV, with new candidates; the authors pool both waves. The file gives
##wave-2 responses their own ResponseId and no link to wave 1, so those 530 people appear twice
##under different ids (2,948 ids = 2,418 wave-1 + 530 wave-2).
##Layout: source `election` = <R if wave 2><office>C<k>; k = candList = ballot position
##(profile, recorded). task = office in the order mayor (1), district (2), at-large (3); the
##display order of the three screens is not recorded (task INFERRED; trial_office names it).
##Outcomes (question wording not in the deposit; article description):
##  choice  = top choice in the single-winner races (mayor, district): the plurality vote or the
##            RCV first rank (the authors' VotedFor2); NA on the at-large task (two winners).
##            No abstention was possible (every ballot complete).
##  rating_vote = plurality ballot mark (VotedFor, 1 = voted for; at-large: 2 marks), NA under RCV.
##  rating_rank = RCV rank (Rank, 1 = first preference ... 4 = last; LOWER = MORE preferred),
##            NA under plurality.
##Attributes: attr_name (80 names, as stored), attr_party (candPID value label: Democrat /
##Republican / Independent; "(not shown)" in the non-partisan arm). The authors' race and gender
##coding of each name (candRace, candGend) is not kept as an attribute (not displayed); gender
##goes to crosswalk.csv (signal name). Level shares near-equal; no restriction documented.
##Covariates (.dta value-label text): cov_gender (male/female/nonbinary -> male/female/other),
##cov_latino, cov_race2 (White, Black/AfAm, Asian, Latino, Other), cov_education (educ),
##cov_party_id7 (pid7), cov_ideology3 (ideo3), cov_duration_sec (survey duration).
##Dropped: Qualtrics ResponseId (re-keyed to 1..n), Outcome (whether the R's first choice won:
##post-treatment), page-submit timings, the derived atlarge flag.
##Counts: wave 1 = 2,418, wave 2 = 530 (article: wave 2 N = 530; wave-1 N not given in the text).
##Spot check: the authors' Figure 3 plurality model (regress VotedFor2 i.candRace if Partisan==0 &
##RCV==0, all three offices) on the source gives White 0.420, Black -0.133, Asian -0.125, Latino
##-0.091; in this table that is rating_vote by the authors' name coding (not kept) in the
##non-partisan plurality arm. Numbers not compared with the article's figure.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "JEPS_replication.dta"))
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
s <- data.table(rid = k$responseid, election = k$election, name = k$candName, pid = lab("candPID"),
                race = as.integer(k$candRace), gend = as.integer(k$candGend), pos = as.integer(k$candList),
                partisan = as.integer(k$Partisan), rcv = as.integer(k$RCV), vf = as.integer(k$VotedFor),
                rank = as.integer(k$Rank), vf2 = as.integer(k$VotedFor2),
                cov_gender = c(male = "male", female = "female", nonbinary = "other")[lab("gender")],
                cov_latino = lab("latino"), cov_race2 = lab("race2"), cov_education = lab("educ"),
                cov_party_id7 = lab("pid7"), cov_ideology3 = lab("ideo3"), cov_duration_sec = as.integer(k$durationinseconds))
stopifnot(nrow(s) == 35376, s[, .N, rid][, all(N == 12)])
s[, wave := fifelse(substr(election, 1, 1) == "R", 2L, 1L)]
s[, office := sub("C[1-4]$", "", sub("^R", "", election))]
stopifnot(s[, all(office %in% c("mayor", "district", "atlarge"))], s[, all(as.integer(sub(".*C", "", election)) == pos)],
          s[, uniqueN(wave), rid][, all(V1 == 1)], s[wave == 2, all(rcv == 1)])
s[, task := match(office, c("mayor", "district", "atlarge"))]
## ballots complete: plurality 1 mark (at-large 2), RCV ranks 1-4
stopifnot(s[rcv == 0, sum(vf), .(rid, task)][, all(V1 == fifelse(task == 3, 2, 1))],
          s[rcv == 1, all(sort(rank) == 1:4), .(rid, task)][, all(V1)], s[, all(partisan == 1 | is.na(pid))])
s[, id := match(rid, unique(rid))]
d <- s[, .(id, task, profile = pos, choice = fifelse(task < 3, vf2, NA_integer_),
           rating_vote = fifelse(rcv == 0, vf, NA_integer_), rating_rank = fifelse(rcv == 1, rank, NA_integer_),
           attr_name = trimws(name), attr_party = fifelse(partisan == 1, pid, "(not shown)"),
           trial_office = c("mayor", "district council", "at-large council")[task], trial_rcv = rcv,
           trial_partisan = partisan, trial_wave = wave,
           cov_gender, cov_latino, cov_race2, cov_education, cov_party_id7, cov_ideology3, cov_duration_sec)]
stopifnot(d[task < 3, sum(choice), .(id, task)][, all(V1 == 1)], d[, all(attr_party %in% c("Democrat", "Republican", "Independent", "(not shown)"))],
          uniqueN(d$attr_name) == 80, s[, uniqueN(paste(race, gend)), name][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "crowdermeyer_2023_rcv_candidates.csv"))
