##Paired conjoint of candidates for Congress differing in religion, from
##Madrid, R., Merolla, J. L., Yanez Ruiz, A., & Schroedel, J. R. (2022). The relevance of religion for political office:
##Voter bias toward candidates from different religious backgrounds. Political Behavior, 44, 981-1001.
##https://doi.org/10.1007/s11109-022-09782-6
##Replication data: Harvard Dataverse doi:10.7910/DVN/XV8GCK, CC0 1.0 (no terms, no restricted files; authors from Crossref).
##Files read: "Conjoint Experiment Data.tab" (Qualtrics export saved here as conj.tab: row 1 = question ids, row 2 = question
##text, 538 respondent rows) and "Conjoint Experiment R Script (2-3-2022) (1).R" (as text). Not read: RELIG_BIASES.tab and
##relig_biases_final.do (a different survey file).
##Usage: Rscript madrid_2022_religious_candidates.R <dir holding conj.tab> <output dir>
##
##538 MTurk respondents (2016-08), of whom 508 answered the choice questions (30 rows are blank on all tasks and are dropped), saw 10 tasks, each two candidates for Congress described by six attributes: Political
##Party, Political Ideology, Occupation, Race, Religion, Sex. Question (Q4 etc., truncated in the export): "Which of these
##two candidates would you prefer to see as your congressional [representative]" -> choice = 1 for the candidate chosen
##(value 1 or 2 in the response column), exactly one per task, no opt-out. The columns QID4, QID9, QID13, QID17, QID21,
##QID48, QID52, QID56, QID60, QID64 are tasks 1..10 in the order the authors' R script lists them (read.qualtrics
##responses=); this order is the AUTHORS' mapping, not verified independently (Qualtrics column order lists QID64 before
##QID60).
##Layout: F-t-k is the NAME of the attribute shown at row k of task t, F-t-1-k the level of candidate 1 at row k, F-t-2-k
##of candidate 2 (levels are the displayed text). The row order of attributes is randomized per respondent and task and
##recorded, so attrpos_* (1 = first row) is kept. Levels (text): party Democrat/Republican/Independent; ideology
##Liberal/Moderate/Conservative; occupation 14 (Lawyer, Medical Doctor, ...); race American Indian/Asian/Black/Hispanic/
##White; religion Atheist/Catholic/Evangelical/Jewish/Mormon/Muslim/Protestant; sex Female/Male. Restrictions and level
##probabilities are not documented.
##Covariates: cov_age (free-typed age, QID24_TEXT, free-typed; plausible whole numbers 18-100 only), cov_gender_code (Q1 sex, codes 1/2 without a
##codebook), cov_party_id_code (Q45 / QID37 party id codes; the authors' script treats 1 = Democrat, 2 = Republican).
##PII FOUND and dropped: IP address, recipient first/last name and email, external reference, MTurk ID (Q57), recorded
##dates, all free-text fields, location. id = row number of the respondent. No weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
h <- names(fread(file.path(raw, "conj.tab"), nrows = 0))
s <- fread(file.path(raw, "conj.tab"), na.strings = NULL, skip = 2, header = FALSE, quote = "")
setnames(s, h)
# quote = "" because one free-text field contains embedded quotes; strip the enclosing quotes by hand
for (j in names(s)) set(s, j = j, value = sub('^"(.*)"$', "\\1", s[[j]]))
stopifnot(nrow(s) == 538)
s[, id := .I]
qs <- c("QID4", "QID9", "QID13", "QID17", "QID21", "QID48", "QID52", "QID56", "QID60", "QID64")
L <- list()
for (t in 1:10) for (p in 1:2) {
  nm <- sapply(1:6, function(k) s[[sprintf("F-%d-%d", t, k)]])
  lv <- sapply(1:6, function(k) s[[sprintf("F-%d-%d-%d", t, p, k)]])
  stopifnot(all(nm %in% c("Political Party", "Political Ideology", "Occupation", "Race", "Religion", "Sex")))
  pos <- function(a) max.col(nm == a, ties.method = "first")
  val <- function(a) lv[cbind(seq_len(nrow(s)), pos(a))]
  r <- s[[qs[t]]]
  L[[length(L) + 1]] <- data.table(id = s$id, task = t, profile = p,
    choice = as.integer(r == as.character(p)), resp = r,
    attr_party = val("Political Party"), attr_ideology = val("Political Ideology"), attr_occupation = val("Occupation"),
    attr_race = val("Race"), attr_religion = val("Religion"), attr_sex = val("Sex"),
    attrpos_party = pos("Political Party"), attrpos_ideology = pos("Political Ideology"),
    attrpos_occupation = pos("Occupation"), attrpos_race = pos("Race"), attrpos_religion = pos("Religion"),
    attrpos_sex = pos("Sex"))
}
d <- rbindlist(L)
stopifnot(all(d$resp %in% c("1", "2", "")))
d <- d[resp %in% c("1", "2")][, resp := NULL]
stopifnot(!any(unlist(d[, grep("^attr_", names(d)), with = FALSE]) == ""))
d[, n := .N, .(id, task)]; stopifnot(d$n == 2L); d[, n := NULL]
age <- suppressWarnings(as.integer(s[["QID24_TEXT"]]))
age[!is.na(age) & (age < 18 | age > 100)] <- NA
cov <- data.table(id = s$id, cov_age = age,
  cov_gender_code = fifelse(s$QID1 %in% c("", "NA"), NA_character_, s$QID1),
  cov_party_id_code = fifelse(s$QID37 %in% c("", "NA"), NA_character_, s$QID37))
d <- merge(d, cov, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "madrid_2022_religious_candidates.csv"))
