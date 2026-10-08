##Supreme Court nominee conjoint (US, December 2022) from
##Wu, V. Y., & Horiuchi, Y. (2026). The Supreme Court's partisan composition affects how Americans
##evaluate nominees: Evidence from a conjoint experiment. Journal of Law and Courts, 1-24.
##https://doi.org/10.1017/jlc.2026.10029
##Replication data: Harvard Dataverse doi:10.7910/DVN/C7T9S3, CC0 1.0. Files read:
##EV_SCOTUS_Jan6_December+14,+2022_11.11.csv (the raw Qualtrics/Lucid export) and
##attributes_and_levels.csv (Dataverse "original format"). README.md, EVSCOTUSJan6.docx and the
##authors' scripts/logs (01_prepare_data.R, 08_audit_reported_values.log) were read as text, not run.
##Usage: Rscript wu_2026.R <dir holding the two files> <output dir>
##
##Lucid sample fielded through Qualtrics, December 2022. 5 tasks x 2 nominees ("Nominee 1"/"Nominee 2"),
##8 attributes (age, gender, current position, partisanship, race/ethnicity, religion, law school,
##law clerk experience). Respondent filters follow 01_prepare_data.R exactly: conjoint completers
##(gc == 1), consent "Yes", age not "Under 18", resides in the US, passed both attention checks
##(check1 "Somewhat disagree", check2 "Red,Green"), and respondent IDs that occur more than once
##removed entirely. The filters leave 9,895 respondents = the manuscript's final sample (audit log
##line 34, which also counts 98,950 = 9,895 x 10 profile rows), but 536 of them did not finish the
##survey (gc blank; 301 have no conjoint answer at all, most others stop before task 5). The authors'
##conjoint data keep only completers (gc == 1): 9,359 respondents here. Their main models further drop
##2 respondents with missing partisanship (93,570 rows = 9,357); those 2 are kept (cov_partisan blank).
##Between-respondent arm (trial_court): nom_treatment_group 1-2 = "Control", 3-4 = "Split 4-4",
##5 = "Republican 6-2 majority", 6 = "Democratic 6-2 majority" (01_prepare_data.R). The question
##wording follows the arm (from the export's question-text row):
##  Control: "Which nominee do you prefer to fill a vacancy on the Supreme Court?"
##  Split:   "Assuming the Supreme Court is split 4-4, which nominee do you prefer ..."
##  Rep./Dem.: "Assuming the Supreme Court is composed of a 6-2 Republican [Democrat] majority, which
##           nominee do you prefer ..."
##choice = 1 for the nominee picked ("Nominee 1"/"Nominee 2"; forced choice, no opt-out; exactly one
##per task, checked). task and profile come from the Qualtrics F-<task>-<profile>-<row> fields
##(recorded).
##Randomization is not uniform (attributes_and_levels / Table C.1): partisanship Independent 10%,
##each other partisanship level 22.5%; race White 50%, Black and Hispanic 20% each, Asian American
##10%. The attribute-name fields (F-t-r) were not exported, but every level text belongs to exactly one
##attribute, so attrpos_<attr> = the row r the attribute was shown in (1-8), recovered from the level
##text. Attribute order varies across respondents and is constant within a respondent (checked).
##Attribute text as displayed (the export's level strings, which match attributes_and_levels.csv).
##Covariates (respondent answers as text, as exported; question text from EVSCOTUSJan6.docx):
##cov_age_group (age "How old are you?", band text as exported, e.g. "35 - 44"), cov_education
##("What is the highest level of school you have completed ...", answer text), cov_ethnicity
##(Hispanic), cov_race, cov_gender (sex "What is your sex?" Male/Female -> male/female),
##cov_state, cov_party_id (partisan "Generally speaking, do you usually think of yourself as a
##Republican, a Democrat, an Independent, or something else?", answer text), cov_republican_strength,
##cov_democrat_strength, cov_leaner, cov_ideology, cov_political_interest, cov_voted (electionvote),
##cov_income, cov_court_knowledge_composition (realcomp) and cov_court_conservatives (currentconservative,
##the number of conservative justices the respondent believes are on the Court, 0-9). These are the
##survey's own items; the authors' columns age...32 etc. are used, not Lucid-supplied demographics.
##PII in the export, not kept: IPAddress, LocationLatitude/Longitude, ResponseId, rid (Lucid respondent
##ID), zip code, timing and browser metadata. Attention checks: every respondent kept passed both
##(filter above), so no cov_attention_pass column is stored. Duration not kept. No survey weight in
##the deposit. No repeated task. IDs are re-keyed to integers in file order. The survey's
##other experiments (electric vehicles, January 6 items) are not part of this table.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "EV_SCOTUS_Jan6_December+14,+2022_11.11.csv"), header = TRUE, colClasses = "character")
s <- s[-(1:2)]  # Qualtrics question-text and ImportId rows
# columns named as in the authors' read_csv (duplicated names get ...<position>)
nm <- names(s); dup <- nm %in% nm[duplicated(nm)]; nm[dup] <- paste0(nm[dup], "...", which(dup)); setnames(s, nm)
r <- s[consent == "Yes" & `age...32` != "Under 18" & state != "I do not reside in the United States" &
         check1 %chin% "Somewhat disagree" & check2 %chin% "Red,Green"]
r <- r[!rid %in% r$rid[duplicated(r$rid)]]
k <- s[gc == "1" & rid %in% r$rid]
stopifnot(nrow(r) == 9895L, !anyDuplicated(k$rid), nrow(k) == 9359L)
lv <- fread(file.path(raw, "attributes_and_levels.csv"), colClasses = "character")
for (i in seq_len(nrow(lv))) if (lv$attribute[i] == "") lv$attribute[i] <- lv$attribute[i - 1]
key <- c("Age" = "age", "Gender" = "gender", "Current position" = "position", "Partisanship" = "partisanship",
         "Race/ethnicity" = "race", "Religion" = "religion", "Education" = "law_school",
         "Law clerk experience" = "law_clerk")
lv[, a := key[attribute]]; stopifnot(!anyNA(lv$a), !anyDuplicated(lv$level))
arm <- c("Control", "Control", "Split 4-4", "Split 4-4", "Republican 6-2 majority", "Democratic 6-2 majority")
qcol <- c(1, 1, 2, 2, 3, 4)
ids <- k$rid; g <- as.integer(k$nom_treatment_group)
rows <- list()
for (t in 1:5) {
  cm <- sapply(1:4, function(j) k[[paste0("conjoint", t, "_", j)]])
  ch <- as.integer(sub("Nominee ", "", cm[cbind(seq_len(nrow(k)), qcol[g])]))
  for (p in 1:2) {
    d <- data.table(id = seq_along(ids), task = t, profile = p, choice = as.integer(ch == p), trial_court = arm[g])
    for (row in 1:8) {
      x <- k[[sprintf("F-%d-%d-%d", t, p, row)]]; at <- lv$a[match(x, lv$level)]; stopifnot(!anyNA(at))
      for (v in unique(at)) { w <- at == v; d[w, paste0("attr_", v) := x[w]]; d[w, paste0("attrpos_", v) := row] }
    }
    rows[[length(rows) + 1]] <- d
  }
}
d <- rbindlist(rows, use.names = TRUE)
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)],
          d[, uniqueN(paste(attrpos_age, attrpos_gender, attrpos_position, attrpos_partisanship, attrpos_race,
                            attrpos_religion, attrpos_law_school, attrpos_law_clerk)), id][, all(V1 == 1)])
cv <- c(cov_age_group = "age...32", cov_education = "education...131", cov_ethnicity = "ethnicity...132", cov_race = "race",
        cov_gender = "sex", cov_state = "state", cov_party_id = "partisan", cov_republican_strength = "republicanstrength",
        cov_democrat_strength = "democratstrength", cov_leaner = "leaner", cov_ideology = "ideology",
        cov_political_interest = "polint", cov_voted = "electionvote", cov_income = "income",
        cov_court_knowledge_composition = "realcomp", cov_court_conservatives = "currentconservative")
cvd <- data.table(id = seq_along(ids)); for (v in names(cv)) cvd[, (v) := { y <- k[[cv[[v]]]]; y[y == ""] <- NA; y }]
cvd[, cov_court_conservatives := as.integer(cov_court_conservatives)]
stopifnot(all(cvd$cov_gender %in% c("Male", "Female", NA)))
cvd[, cov_gender := tolower(cov_gender)]
d <- merge(d, cvd, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", sort(grep("^attr_", names(d), value = TRUE)),
                 sort(grep("^attrpos_", names(d), value = TRUE)), "trial_court"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wu_2026_scotus_nominees.csv"))
