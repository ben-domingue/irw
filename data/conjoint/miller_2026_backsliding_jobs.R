##Paired conjoint on state-government job attractiveness, from
##Miller, S. M., & Gilad, S. (2026). Democratic backsliding, elite polarization, and job seekers' pursuit of
##government employment. Regulation & Governance. https://doi.org/10.1111/rego.70138
##Replication data: Harvard Dataverse doi:10.7910/DVN/KCEBF9, CC0 1.0 (no terms, no restricted files).
##File read: R&G_data.tab (comma/tab text, saved here as rg.tab). No codebook or README is deposited; the paper
##(Wiley, 403 to our fetch) was not read, so question wording is a PARAPHRASE and scale anchors are unknown.
##Usage: Rscript miller_2026_backsliding_jobs.R <dir holding rg.tab> <output dir>
##
##885 US job seekers (n matches the triage estimate; paper not checked). Long file, 6 rows per respondent
##(resp_id 1..885). `state_gov` 1..6 is read as 3 tasks x 2 profiles: task = ceil(state_gov/2), profile = 1 for
##odd and 2 for even state_gov (state_gov 1,2 = task 1 profiles 1,2, etc.). This is an INFERENCE (task_source and
##profile_source = inferred), verified two ways: preferwork has exactly one 1 in every (resp_id, task) pair of
##rows (2,652 pairs; 3 pairs have preferwork NA and are dropped from the choice), and the NA pattern falls on
##state_gov pairs (1,2) and (5,6). Rows within a pair are in a fixed order, so profile numbering does not depend
##on the outcome.
##Attributes shown (text as in the file): Gov_Party (state government party: Democrat/Republican), Polarization
##(five levels, "Extremely Low Level" .. "Extremely High Level"), Salary ($60,000 .. $140,000), Workforce (Small/
##Mid-Size/Large), Job_Location (four), Backsliding (eight: Bribes, Economic Expansion, Exec Orders, Ignores Court,
##Political Firings, Redistricting, Veterans, Wasteful Contracting;).
##Outcomes: choice = preferwork (1 = the job preferred in the pair; opt-out not offered: exactly one per pair);
##rating = ratework (1-7 per job; direction presumably higher = more attractive, not documented).
##Covariate: cov_party_id = respondent party (Democrat/Independent/Republican). Dropped: Shared_Party (derived from
##party x Gov_Party). Rows with preferwork NA (6 rows, 3 pairs) dropped. Level shares are near-uniform except
##Backsliding (637-685, 8 levels) and Gov_Party; restrictions not documented; party of respondent x Gov_Party
##combinations all occur.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "rg.tab"))
stopifnot(nrow(s) == 5310, uniqueN(s$resp_id) == 885)
s[, task := (state_gov + 1L) %/% 2L]
s[, profile := 2L - state_gov %% 2L]
s[, n1 := sum(preferwork), .(resp_id, task)]
bad <- s[is.na(n1), unique(paste(resp_id, task))]
s <- s[!is.na(n1)]
stopifnot(all(s$n1 == 1L), nrow(s) == 5304)
d <- s[, .(id = resp_id, task, profile, choice = preferwork, rating = ratework,
  attr_government_party = Gov_Party, attr_polarization = Polarization, attr_salary = Salary,
  attr_workforce = Workforce, attr_job_location = Job_Location, attr_backsliding = Backsliding,
  cov_party_id = party)]
stopifnot(!anyNA(d))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "miller_2026_backsliding_jobs.csv"))
