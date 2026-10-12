##Paired conjoint embedded in a survey of political journalists (which candidate announcement to cover), from
##Hassell, H. J. G., Holbein, J. B., & Miles, M. R. (2020). There is no liberal media bias in which news stories
##political journalists choose to cover. Science Advances, 6(14), eaay9344. https://doi.org/10.1126/sciadv.aay9344
##Replication data: Harvard Dataverse doi:10.7910/DVN/U6EWUW, CC0 1.0 (no terms, no restricted files).
##File read: "Conjoint Anon Survey.tab" (comma/tab text saved here as conj.tab) and "Replication Code, Conjoint.do" (as
##text). The other deposited files (audit/correspondence study, Twitter ideology scripts) are not conjoint data.
##Usage: Rscript hassell_2020_journalist_coverage.R <dir holding conj.tab> <output dir>
##
##The file has 6,360 rows = 1,590 journalist-survey rows x 4 candidates (column `number` 1..4 repeats in blocks of four;
##the file has no respondent id, so id = the block index 1..1590, INFERRED from the verified block structure: age, the
##survey date, circulation and party id are constant within each block of four). Each respondent saw 2 pairs of
##hypothetical candidates announcing a run for governor: task 1 = rows number 1,2 (the file's paircomparison = 1), task 2 =
##rows 3,4; profile = position within the pair. Task and profile are INFERRED from this row order (task_source and
##profile_source = inferred); numbering does not depend on the outcome.
##Respondents: only 897 of the 1,590 blocks have an answer (3,276 candidate rows = the paper's "experimental N = 3276",
##1,638 answered pairs; covered is NA for the rest, whose rows are dropped). Of the 897, 741 answered both pairs, 156 one.
##Attributes (text as in the wide columns, suffix 1..4 = number; verified against the authors' dummies conjointDemocrat,
##CandQual, ManagerConnected/Experienced, Minority/Female and Issue, which all agree with the text): name (28 fictional
##names that signal race and gender; the authors' coding is conjointMinority / conjointFemale), occupation (11), party
##(Democrat / Republican), past experience (no previous elected office / mayor of medium sized city / state legislator),
##age (28 / 47 / 67), announcement statement (6 texts = issue: infrastructure, education, ...), campaign manager (4 combos
##of little or lots of campaign experience x well-known or not well-known in the party). Derived dummies dropped.
##The occupation text is BLANK for 141 candidates, all at position number = 2, 83 of them on answered rows (one per pair); it is not
##documented and (not shown) cannot be asserted, so the 83 answered pairs (tasks) that contain a blank attribute are dropped (1,555 pairs, 882 respondents remain).
##Outcome: choice = covered, 1 for the announcement the respondent would send a reporter to cover in person (the paper:
##"which of the two candidate announcements they would send a reporter to cover in person", given that the paper cannot
##staff both); exactly one per answered pair, no opt-out. Not kept: readerscover and editorscover (0/1 per candidate,
##question wording not documented anywhere in the deposit or the open paper text), papercoverlikely (respondent-level
##0-10, wording not documented), race/lede side randomizations (racecandidatetext, black, raceother, racecloseness,
##variedcandidatelede, nonvariedcandidatelede: a separate experiment on the story lede).
##trial_previous_publication: respondent-level randomized note shown with the story ("This story was broken yesterday by
##a ... daily / has not been published previously in a paper"), constant within a respondent; kept as the displayed text.
##Covariates: cov_age (journalist age in years as recorded; plausible whole numbers only), cov_party_id_code (pid3 codes
##1/2/3, labels not in the deposit). Dropped: IDNumber (pair index), consent/status/channel fields, dates, free-text.
##No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conj.tab"), na.strings = NULL)
stopifnot(nrow(s) == 6360, all(s$number == rep(1:4, length.out = nrow(s))))
s[, id := (seq_len(.N) - 1L) %/% 4L + 1L]
g <- function(a) mapply(function(n, i) s[[paste0(a, n)]][i], s$number, seq_len(nrow(s)))
d <- data.table(id = s$id, task = (s$number + 1L) %/% 2L, profile = (s$number - 1L) %% 2L + 1L,
  covered = s$covered, attr_name = g("name"), attr_occupation = g("occupation"), attr_party = g("party"),
  attr_past_experience = g("pastexperience"), attr_age = as.character(s$conjointage), attr_statement = g("statement"),
  attr_campaign_manager = g("cm"), trial_previous_publication = s$previouspublication,
  cov_age = suppressWarnings(as.integer(s$age)), cov_party_id_code = s$pid3)
d <- d[covered %in% c("0", "1")]
d[, choice := as.integer(covered)][, covered := NULL]
stopifnot(nrow(d) == 3276)
blank <- d[, lapply(.SD, function(x) x == ""), .SDcols = grep("^attr_", names(d), value = TRUE)]
bad <- d[rowSums(blank) > 0, unique(paste(id, task))]
d <- d[!paste(id, task) %in% bad]
d[, n := .N, .(id, task)]; stopifnot(d$n == 2L, d[, sum(choice), .(id, task)][, all(V1 == 1L)]); d[, n := NULL]
stopifnot(!any(unlist(d[, grep("^attr_", names(d), value = TRUE), with = FALSE]) == ""), !any(d$trial_previous_publication == ""))
d[cov_age < 18 | cov_age > 100, cov_age := NA]
d[cov_party_id_code %in% c("", "NA"), cov_party_id_code := NA]
d[, id := as.integer(factor(id))]
setorder(d, id, task, profile)
setcolorder(d, c("id", "task", "profile", "choice"))
message("pairs dropped for blank attribute: ", length(bad))
fwrite(d, file.path(out, "hassell_2020_journalist_coverage.csv"))
