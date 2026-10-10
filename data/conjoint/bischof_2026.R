##German MP candidate conjoints (low- and high-information) from
##Bischof, D., & Senninger, R. (2026). Can simple language affect voters' political knowledge
##and their beliefs about politicians? The Journal of Politics, 88(4), 1419-1436.
##https://doi.org/10.1086/736693
##Replication data: Harvard Dataverse doi:10.7910/DVN/XT6RRU, CC0 1.0, no restricted files.
##Files read: conjoint_low_information.RData (cjointdata2, MPdesign2) and
##conjoint_high_information.RData (cjointdata1, MPdesign), each loaded into its own environment
##(the deposit ships each file twice, byte-identical). CODEBOOK.rtf and README.rtf (variable
##descriptions) and main.R (authors' code) read as text. The article is not open access and the
##deposit has no questionnaire, so the outcome wording is a paraphrase.
##Usage: Rscript bischof_2026.R <raw dir> <output dir>
##
##Respondents in Germany chose between two hypothetical members of parliament in up to 3 pairs.
##Two experiments with different attribute sets, analysed separately by the authors ("Low
##Information" and "High Information" AMCEs, main.R lines 508-517): TWO TABLES.
##  bischof_2026_simple_language_low   7,234 respondents; attributes attr_sex (male/female),
##      attr_age (26, 30, 47, 57, 64, 79), attr_party (AfD, B90/Grüne, CDU/CSU, Die Linke, FDP,
##      SPD), attr_position (for / against / neutral: the MP's stance on an issue),
##      attr_sophistication (simple / sophisticated: the language of the MP's statement)
##  bischof_2026_simple_language_high  7,024 respondents; the same five plus attr_motivation
##      (to serve the party / to represent ordinary people / to impact personally), attr_days
##      (1 day / 2 days / 3 days in the constituency per week), attr_occupation (farmer, lawyer,
##      nurse, nurturer, political scientist, teacher), attr_experience (new / incumbent)
##Attribute text = the authors' English factor labels (respondents saw German; label_language
##en). For position and sophistication the label summarises a statement the MP was shown making;
##the statement texts are not in these files (the issue and wording are not recoverable here).
##Respondent ids are the authors' integers ("respondent"); whether the two experiments share
##respondents is not documented (both number respondents from 1), so they are not linked.
##TASK AND PROFILE ARE INFERRED. The files hold one row per respondent x profile with no task
##or profile column. Rows come in six stacked blocks (the respondent id restarts at 1 in each);
##pairing block k with block k + 3 (k = 1-3) gives exactly one chosen profile in every pair for
##every respondent, and no other pairing of the blocks does (checked here). So task = k and
##profile = 1 for blocks 1-3, 2 for blocks 4-6. Which profile appeared on the left and the task
##order are inferred from the block order, not recorded (task_source = profile_source = inferred).
##Outcome: choice = selected, which of the two MPs the respondent preferred (paraphrase); forced
##choice, no opt-out. Respondents with fewer than 3 pairs (low 149, high 49) keep the pairs they
##have.
##Randomization restrictions: the authors' cjoint design objects declare party x position
##dependent and give zero probability to AfD x "for" and B90/Grüne x "against", but both
##combinations occur in the data about as often as any other (e.g. 2,309 AfD/for profiles in the
##high-information file). The design objects therefore do not describe these data; no restriction
##is observed.
##No respondent covariates are in these two files (the SI files carry a few, keyed to the same
##integers, but are not read).
##N vs paper: not checked (paywalled).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
mk <- function(file, obj, tab) {
  e <- new.env(); load(file.path(raw, file), envir = e)
  x <- as.data.table(get(obj, e))
  x[, block := cumsum(c(TRUE, diff(respondent) <= 0))]
  stopifnot(max(x$block) == 6, x[, !anyDuplicated(respondent), block]$V1)
  x[, task := (block - 1L) %% 3L + 1L][, profile := (block - 1L) %/% 3L + 1L]
  stopifnot(x[, .N, .(respondent, task)][, all(N == 2)], x[, sum(selected), .(respondent, task)][, all(V1 == 1)])
  ac <- grep("^mp_", names(x), value = TRUE)
  d <- x[, c("respondent", "task", "profile", "selected", ac), with = FALSE]
  setnames(d, c("id", "task", "profile", "choice", sub("^mp_", "attr_", ac)))
  for (v in grep("^attr_", names(d), value = TRUE)) d[, (v) := as.character(get(v))]
  stopifnot(!anyNA(d))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, tab))
}
mk("conj_low.RData", "cjointdata2", "bischof_2026_simple_language_low.csv")
mk("conj_high.RData", "cjointdata1", "bischof_2026_simple_language_high.csv")
