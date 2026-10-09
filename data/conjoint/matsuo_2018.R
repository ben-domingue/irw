##Party policy-package conjoint, 2015 UK general election, from
##Matsuo, A., & Lee, S. (2018). Multi-dimensional policy preferences in the 2015 British general
##election: A conjoint analysis. Electoral Studies, 55, 89-98. https://doi.org/10.1016/j.electstud.2018.07.005
##Replication data: Harvard Dataverse doi:10.7910/DVN/CGHY3L, CC0 1.0, no restricted files, no terms.
##File read: data_all.rda (objects data_all, qual.data, ukdesign; loaded into its own environment).
##Read as text only: README.md, 01_analysis_main_model.R, 01_sub1_process_results.R,
##01_sub2_process_het_model.R. Question wording and design facts from the accepted manuscript
##(repository.essex.ac.uk/22775), section 4 and Figure 1 (screenshot of the task).
##Usage: Rscript matsuo_2018.R <raw dir> <output dir>
##
##SSI online panel, UK, 30 April - 4 May 2015, quotas on gender and age. Each respondent saw 4
##pairs ("Party A" / "Party B") of hypothetical party policy packages, 5 attributes taken from the
##2015 manifestos: Economy ("Deficit and the economy" in the screenshot), Jobs, Immigration, EU,
##Education. Level text in the data matches the screenshot. Levels were drawn uniformly and
##independently (the deposited cjoint design object ukdesign gives every one of the 2x3x5x3x4 =
##360 combinations probability 1/360; the paper says the treatment is fully randomized).
##Attribute order randomized per respondent (paper), not recorded.
##Outcome: choice (Chosen_party). "Suppose that two parties with the issue positions described
##below had nominated candidates in the general election. Which of these two candidates would you
##be most likely to vote for? Even if you are not entirely sure, please choose the one that you
##most prefer." / "Which candidate would you support?" Candidate from Party A / Party B. Forced
##choice, no opt-out.
##Task = contest_number (1-4, recorded). Profile is INFERRED: rows are numbered (rowid) in pairs
##within each contest and the lower rowid is taken as Party A (profile 1); not verifiable.
##The source has 1,658 respondent IDs; tasks with Chosen_party missing (2,090 rows) are dropped,
##as in the authors' code; 1,404 IDs answered at least one task. One ID holds two complete
##answered sessions (each of its 4 contests stored twice with different profiles and choices,
##rowids 937-944 and 5025-5032): two people or one person taking it twice cannot be told apart,
##so that ID is dropped (the authors keep both). Result: 1,403 respondents, 5,607 tasks. The paper
##reports N = 1,394 (9 more here; not resolved). Platform IDs (ID / psid) re-keyed to integers in order of first appearance.
##trial_time_spend = Time_spend, constant within a task (time on the task; unit not documented).
##Covariates: cov_pid1_code (pid.1, codes 1-15; 01_sub2 defines a 15-party list that may be its
##labels, but no code applies it, so the codes are kept), cov_country_code (country.code: E, S, W,
##N as stored, blank = NA; presumably England/Scotland/Wales/Northern Ireland, not documented),
##cov_vote_intention (qual.data voteint, text from the authors' recode in 01_sub2: voteint - 99,
##wrapped, indexes vote.levels, e.g. 101 = "Conservative", 98 = "Not intend to vote", 99 = "I have
##not made up my mind yet"; a vote intention, not party identification), cov_education_code
##(qual.data edu, codes 1-6, no labels). qual.data repeats a few psids (rows that disagree): those
##respondents get NA for the two qual.data covariates; pid.1/country.code set NA where they vary
##within a respondent. qual.data point (undocumented) is dropped. The paper's
##post-stratification weight is not in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "data_all.rda"), envir = e)
s <- as.data.table(e$data_all); q <- as.data.table(e$qual.data)
stopifnot(isTRUE(all.equal(as.numeric(e$ukdesign$J), rep(1/360, 360))), nrow(s) == 13320L)
s <- s[!is.na(Chosen_party)]
dup <- s[, .N, .(ID, contest_number)][N > 2, unique(ID)]
stopifnot(length(dup) == 1L)
s <- s[ID != dup]
setorder(s, rowid)
stopifnot(s[, .N, .(ID, contest_number)][, all(N == 2)], s[, sum(Chosen_party), .(ID, contest_number)][, all(V1 == 1)])
s[, profile := frank(rowid), .(ID, contest_number)]
ids <- unique(s$ID); s[, id := match(ID, ids)]
vote.levels <- c("Democratic Unionist Party (DUP)", "Conservative", "Labour", "Liberal Democrats",
                 "Social Democratic and Labour Party (SDLP)", "Scottish National Party", "Plaid Cymru",
                 "UK Independence Party", "Greens", "Sinn Fein", "Ulster Unionist Party (UUP)",
                 "Alliance Party of Northern Ireland", "Not intend to vote", "I have not made up my mind yet")
q[, v2 := voteint - 99L][v2 <= 0, v2 := v2 + 14L]
stopifnot(all(q$v2 %in% c(1:14, NA)))
q <- q[, .(v2 = if (.N == 1L) v2 else NA_integer_, edu = if (.N == 1L) edu else NA_integer_), psid]
s <- merge(s, q[, .(ID = psid, v2, edu)], by = "ID", all.x = TRUE)
d <- s[, .(id = as.integer(id), task = as.integer(contest_number), profile = as.integer(profile),
           choice = as.integer(Chosen_party),
           attr_economy = as.character(Economy), attr_jobs = as.character(Jobs),
           attr_immigration = as.character(Immigration), attr_eu = as.character(EU),
           attr_education = as.character(Education),
           trial_time_spend = Time_spend,
           cov_pid1_code = as.integer(pid.1), cov_country_code = fifelse(country.code == "", NA_character_, country.code),
           cov_vote_intention = vote.levels[v2], cov_education_code = as.integer(edu))]
for (v in c("cov_pid1_code", "cov_country_code")) d[, (v) := if (uniqueN(get(v)) == 1L) get(v) else NA, id]
stopifnot(uniqueN(d$id) == 1403L, nrow(d) == 11214L)
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "matsuo_2018_uk_policy_packages.csv"))
