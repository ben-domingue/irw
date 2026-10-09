##Energy-mix conjoint (US adults, April 2022) from the deposit
##Wu, V. (2024). Replication data for: "Partisan energy mix priorities in the United States:
##Republicans prioritize price, Democrats also consider renewables" [Data set]. Harvard Dataverse.
##(No published article found; the dataset description gives the design and n = 1,862.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/9GOXGT, CC BY 4.0, no restricted files.
##File read: CCA_Data.xlsx (the raw Qualtrics export, answers as text; row 1 = question text).
##The author's "1. Data Cleaning.do", "MM and AMCE Figures.R" and "Attribute Salience.R" read as text
##(not run). "Conjoint data.dta" (760 MB, the author's reshaped file built from the same xlsx) not
##downloaded.
##Usage: Rscript wu_2024.R <raw dir> <output dir>
##
##Lucid online sample, 19 April - 1 May 2022 (StartDate). The conjoint sits inside an omnibus survey
##(other blocks: Cuomo approval/harassment and third-party experiments, a Community Choice
##Aggregation (CCA) information screen). 10 tasks ("Task t/10: Please carefully review the options
##detailed below, then please answer the questions. Which of these choices do you prefer?" Choice 1
##/ Choice 2), each a pair of energy mixes (profile 1 = Choice 1), 3 attributes, as in the author's
##code: Monthly bill ($105 / $110 / $115 / $120 / $125), Percentage of renewables (10% / 30% / 50% /
##100%), Locally produced renewables (Yes / No). Level text as in the export (F-<task>-<profile>-<row>).
##Attribute ORDER was randomized once per respondent (author's do file: "Order of attributes was
##randomized for each respondent"); the export holds only levels by row, so each level is assigned
##to its attribute by its form ($ / % / Yes-No, as the author does) and the row is kept as attrpos_.
##The attribute-name rows (F-t-k) were not exported; attribute names are the author's.
##Outcome: choice = conjoint<t> ("Choice 1" / "Choice 2"), forced, no opt-out.
##Sample (the author's final sample, do file L9-18): drop consent = No, age "Under 18", state "I do
##not reside in the United States", and check2 != "Red,Green" (non-completes / Lucid terminates),
##then respondents who failed attention check 1 ("please select - 'Somewhat disagree'"): 1,862
##respondents, the deposit's stated n. Tasks with no answer are omitted (19 tasks; one respondent
##answered none, so the table has 1,861 respondents, 18,591 tasks).
##PII in the export, dropped: IPAddress, LocationLatitude/Longitude, ResponseId, rid (Lucid ID),
##zip codes, UserAgent, free-text comment and *_TEXT fields. IDs re-keyed to integers in file order.
##Also dropped: timers, the other experiments' items, the author's derived dummies.
##trial_cca_treatment = ccatreatment (1/2): an assignment variable of the survey's CCA block, not
##documented in the deposit (kept as code; whether it changed what preceded the conjoint is unknown).
##Covariates (answer text as exported; question text from the export's first row): cov_gender (sex,
##"What is your sex?": Female/Male -> female/male), cov_age_group (age...28 "How old are you?",
##band text, e.g. "35 - 44"), cov_age (Lucid profile age in years, appended by Lucid), cov_education
##(education...93 "What is the highest level of school you have completed ..."), cov_party_id
##(partisan: Democrat / Republican / Independent / Something else), cov_party_lean (leaner),
##cov_ideology, cov_income, cov_state, cov_duration_sec (Duration (in seconds), whole survey).
##All kept respondents passed check1 and check2 (no attention covariate). No survey weight.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- suppressMessages(as.data.table(read_excel(file.path(raw, "CCA_Data.xlsx"), col_types = "text")))
r <- r[-1]   # question-text row
r <- r[!(consent %in% "No") & !(`age...28` %in% "Under 18") & !(state %in% "I do not reside in the United States") &
         check2 %in% "Red,Green" & check1 %in% "Somewhat disagree"]
stopifnot(nrow(r) == 1862)
r[, id := seq_len(.N)]
d <- rbindlist(lapply(1:10, function(t) rbindlist(lapply(1:2, function(p) {
  lv <- sapply(1:3, function(k) r[[sprintf("F-%d-%d-%d", t, p, k)]])
  kind <- ifelse(grepl("^\\$", lv), "bill", ifelse(grepl("%$", lv), "pct", ifelse(lv %in% c("Yes", "No"), "local", NA)))
  dim(kind) <- dim(lv)
  stopifnot(!anyNA(kind), all(apply(kind, 1, function(z) setequal(z, c("bill", "pct", "local")))))
  pick <- function(k) lv[cbind(seq_len(nrow(lv)), max.col(kind == k))]
  pos <- function(k) max.col(kind == k)
  ans <- r[[paste0("conjoint", t)]]
  stopifnot(all(ans %in% c(NA, "Choice 1", "Choice 2")))
  data.table(id = r$id, task = t, profile = p, choice = as.integer(ans == paste("Choice", p)),
             attr_monthly_bill = pick("bill"), attr_renewables_pct = pick("pct"), attr_local_renewables = pick("local"),
             attrpos_monthly_bill = pos("bill"), attrpos_renewables_pct = pos("pct"), attrpos_local_renewables = pos("local"))
}))))
d <- d[!is.na(choice)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)],
          d[, lapply(.SD, uniqueN), id, .SDcols = patterns("^attrpos_")][, all(unlist(.SD) == 1), .SDcols = -1])
cv <- r[, .(id, trial_cca_treatment = as.integer(ccatreatment),
            cov_gender = c(Female = "female", Male = "male")[sex], cov_age_group = `age...28`, cov_age = as.integer(`age...320`),
            cov_education = `education...93`, cov_party_id = partisan, cov_party_lean = leaner, cov_ideology = ideology,
            cov_income = income, cov_state = state, cov_duration_sec = as.integer(`Duration (in seconds)`))]
stopifnot(all(r$sex %in% c("Female", "Male", NA)))
d <- merge(d, cv, by = "id")
d[, id := match(id, sort(unique(id)))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wu_2024_energy_mix.csv"))
