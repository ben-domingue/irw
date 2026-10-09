##Constituent-feedback conjoint among US local elected officials from
##Lee, N. R., Chen, K., Marble, W., & Bram, C. (2025). Voice and value: How elected officials
##evaluate online and offline constituent feedback. Public Opinion Quarterly, 89(1), 31-48.
##https://doi.org/10.1093/poq/nfaf006
##Replication data: Harvard Dataverse doi:10.7910/DVN/VU01FS, CC0 1.0, no restricted files, no
##terms. Files read: cleaned_conjoint.rds (the authors' processed conjoint data) and
##cleaned_survey.rds (respondent survey). Design facts from the authors' Analysis.R and
##memo.rtf (read as text). The article (closed access) and the instrument were not available:
##question wording is paraphrased from the variable names and response labels.
##Usage: Rscript lee_2025.R <raw dir> <output dir>
##
##Respondents are US local elected officials. Each evaluated hypothetical constituent feedback
##on three local issues (trial_issue: park, dev [retail development], tax [school property
##tax]), two messages per issue (profile = the deposit's profile_id 1/2), 6 profiles in all.
##task = issue (1 park, 2 dev, 3 tax): the order in which the issues were shown is NOT in the
##deposit, and whether the two messages of an issue appeared side by side is not documented.
##Attributes (text as in the deposit): attr_mode (commtype: Visit in office / Social media),
##attr_number (numconst: 5 / 15 / 30 people), attr_constituents (typeconst, issue-specific, e.g.
##"Neighborhood residents", "Business owners and homeowners"), attr_argument (typearg, issue-
##and position-specific sentence, e.g. "Personal stories about the difficulty of paying high
##property taxes in this economy"), attr_position (Support / Oppose). Restriction: the position
##is the same for both messages of an issue (all respondents), and constituent types and
##arguments are drawn from issue-specific (and, for arguments, position-specific) lists. The
##authors analyse coarsened versions (typeconst_comb natural allies / natural opponents / both;
##typearg_comb objective studies / personal story / questioning motives), dropped here as derived.
##Outcomes (both asked of every message; trial_info_first = cj_info_first, 1 if the
##informativeness question came first, as the variable name suggests):
##  rating_informative: how informative the feedback is, 1 Not informative, 2 Somewhat
##    informative, 3 Moderately informative, 4 Very informative (deposit text; the authors'
##    informative_num coding, checked).
##  rating_influential: how influential it would be, 1 Not influential .. 4 Very influential.
##Dropped: 149 respondents whose profiles have no attributes in the deposit (all but one of them
##also have no ratings; that one rated every message "Not" and is dropped as the levels were not
##saved), messages with neither rating (202 rows).
##Covariates (cleaned_survey.rds, linked by Qualtrics ResponseId; 96 conjoint respondents are
##not in the survey file and have NA): cov_age, cov_gender (Male/Female/Other), cov_education
##(educ text), cov_party_id (pid5 text: Democrat .. Republican, incl. leaners), cov_salary
##(salary for the office), cov_job_exp, cov_gov_exp (years, as deposited), cov_progress.
##Dropped: ResponseId (re-keyed), PersonID (sample-frame id), county, state, fips, dates,
##open-ended text. No survey weight.
##N: 573 officials with at least one rated message (598 with attributes; 747 rows of ids in the
##conjoint file). Spot check in the return.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "cleaned_conjoint.rds")))
s <- as.data.table(readRDS(file.path(raw, "cleaned_survey.rds")))
stopifnot(x[, .N, responseid][, all(N == 6)], x[, .N, .(responseid, conjoint_id, profile_id)][, all(N == 1)])
inf <- c("Not informative", "Somewhat informative", "Moderately informative", "Very informative")
ifl <- c("Not influential", "Somewhat influential", "Moderately influential", "Very influential")
x[, ri := match(informative, inf)][, rf := match(influential, ifl)]
stopifnot(x[!is.na(ri), all(ri == informative_num)], x[!is.na(rf), all(rf == influential_num)],
          all(x$informative %in% c("", inf)), all(x$influential %in% c("", ifl)))
x <- x[typeconst != "" & !(is.na(ri) & is.na(rf))]
stopifnot(!is.na(x$commtype), !is.na(x$numconst), x$typearg != "", x$position %in% c("Support", "Oppose"))
stopifnot(x[, uniqueN(position), .(responseid, conjoint_id)][, all(V1 == 1)])
ids <- sort(unique(x$responseid))
d <- x[, .(id = match(responseid, ids), task = match(conjoint_id, c("park", "dev", "tax")), profile = as.integer(profile_id),
           rating_informative = ri, rating_influential = rf,
           attr_mode = as.character(commtype), attr_number = as.character(numconst), attr_constituents = typeconst,
           attr_argument = typearg, attr_position = position, trial_issue = conjoint_id,
           trial_info_first = as.integer(cj_info_first), rid = responseid)]
stopifnot(!is.na(d$task), d$profile %in% 1:2)
sv <- s[, .(rid = ResponseId, cov_age = as.integer(age), cov_gender = tolower(as.character(gender)),
            cov_education = as.character(educ), cov_party_id = as.character(pid5), cov_salary = as.character(salary),
            cov_job_exp = job_exp, cov_gov_exp = gov_exp, cov_progress = as.numeric(Progress))]
d <- merge(d, sv, by = "rid", all.x = TRUE)
d[, rid := NULL]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lee_2025_constituent_feedback.csv"))
