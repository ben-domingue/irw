##Party-manifesto conjoint (Japan, 2014 House of Representatives election) from
##Horiuchi, Y., Smith, D. M., & Yamamoto, T. (2018). Measuring voters' multidimensional policy
##preferences with conjoint analysis: Application to Japan's 2014 election. Political Analysis,
##26(2), 190-209. https://doi.org/10.1017/pan.2018.2
##Replication data: Harvard Dataverse doi:10.7910/DVN/KUMMUJ, CC0 1.0, no restricted files.
##File read: ReplicationArchive.tar.gz -> 2014_Lower_House_Election_in_Japan.csv (Qualtrics
##export, two header rows, UTF-8 with BOM). codebook.pdf and HSY-makedata.R / HSY-preprocess.R
##were read as text (sample rules, English translations of levels).
##Usage: Rscript horiuchi_2018.R <dir holding the .csv> <output dir>
##
##Japanese adults (Research Now panel, December 2014, fielded before the 14 Dec election), 5 tasks
##of 2 hypothetical parties' manifestos, 9 policy attributes (consumption tax, employment,
##monetary/fiscal policy, growth strategy, nuclear restart, TPP, collective self-defense,
##constitutional revision, Diet seat reduction), 3-4 levels each; each level is a real party's
##2014 platform position. Level text is the Japanese text shown (Qualtrics F-<task>-<profile>-
##<row> fields, "<br>" line breaks removed); attribute names (F-<task>-<row>) are mapped to English
##column names. Attribute row order was randomized and is recorded (attrpos_, 1-9); in the data
##it is the same in all five tasks of a respondent, i.e. drawn once per respondent.
##The authors' English labels (HSY-preprocess.R) end with the parties holding each position in
##brackets; those brackets were not displayed and are not stored.
##Outcome: choice = "Suppose that the following two parties were nominating candidates in this
##general election. Which party would you support? Even if you are not entirely sure, please
##indicate which of the two you would dare to support." (codebook translation of B<k>a/B<k>b),
##Party 1 / Party 2, forced (no opt-out). Unanswered tasks (respondents who left) are omitted.
##Sample, as in HSY-makedata.R: end date (V9) after 2014-12-03 00:00 and before 2014-12-13 17:00 EST
##(the code filters V9 on both bounds; the codebook describes V8 for the first),
##consented (A1 == 1), and shown the conjoint; Status 8 ("possible spam", 4 rows) and
##unfinished respondents are kept, as by the authors (codebook V7, V10).
##Restrictions: not documented in the deposit (article paywalled, not read); level shares in the
##table are close to uniform. N: 1,951 respondents answer at least one task (1,928 answer all
##five); the article's N was not checked.
##Covariates: cov_age (C1 + 19 = years, as HSY-makedata.R L48; 90 = "90 or older", codebook
##C1); cov_gender (C2, codebook p5: 1 Male, 2 Female -> male/female); cov_education (C3,
##codebook English text: Middle school / High school / Polytechnic, two-year college, advanced
##vocational school / Four-year college or post-graduate school / Others (e.g., never attended
##school)); cov_party_id (D6 "which party do you usually support?", codebook p7 English text:
##Liberal Democratic Party of Japan, Democratic Party of Japan, Japan Innovation Party,
##Komeito, Party for Future Generations, Japan Communist Party, People's Life Party, Social
##Democratic Party, Other party, No party to support). The instrument was Japanese; these are
##the codebook's English translations. Codebook codes: cov_prefecture (C4, 1-47),
##cov_employment (C6), cov_income (C8, 1-14), cov_left_right (D1_1, 0-10),
##cov_turnout_history (D2), cov_smd_vote (D3), cov_pr_vote (D5), cov_abe_approval (D8). The authors' entropy-
##balancing weights are derived (computed from population margins) and are not stored.
##Dropped: Qualtrics ResponseID (re-keyed 1..n in file order), Research Now study id, dates,
##comments (E1, free text), location accuracy.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "2014_Lower_House_Election_in_Japan.csv")
h <- strsplit(sub("^﻿", "", readLines(f, n = 1, encoding = "UTF-8")), ",")[[1]]
x <- fread(f, skip = 2, header = FALSE, encoding = "UTF-8", na.strings = "", colClasses = "character")
setnames(x, seq_along(h), h)
x <- x[as.POSIXct(V9, tz = "EST") > as.POSIXct("2014-12-03 00:00:00", tz = "EST") &
       as.POSIXct(V9, tz = "EST") < as.POSIXct("2014-12-13 17:00:00", tz = "EST") & A1 == "1" & !is.na(`F-1-1`)]
x[, id := .I]
en <- c("議員定数削減" = "seat_reduction", "集団的自衛権" = "collective_self_defense", "消費再増税" = "consumption_tax",
        "雇用政策" = "employment", "成長戦略" = "growth_strategy", "金融財政政策" = "monetary_fiscal",
        "原発再稼働" = "nuclear_restart", "ＴＰＰ" = "tpp", "憲法改正" = "constitution")
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  r <- data.table(id = x$id, task = t, profile = p, sel = x[[paste0("B", t, "b")]])
  for (k in 1:9) {
    nm <- en[x[[sprintf("F-%d-%d", t, k)]]]
    stopifnot(!anyNA(nm))
    r[, paste0("n", k) := nm][, paste0("v", k) := gsub("<br>", "", x[[sprintf("F-%d-%d-%d", t, p, k)]], fixed = TRUE)]
  }
  r
}))))
d <- d[!is.na(sel)]
d[, choice := as.integer(sel == as.character(profile))]
for (nm in en) {
  d[, paste0("attr_", nm) := NA_character_][, paste0("attrpos_", nm) := NA_integer_]
  for (k in 1:9) {
    w <- which(d[[paste0("n", k)]] == nm)
    set(d, w, paste0("attr_", nm), d[[paste0("v", k)]][w]); set(d, w, paste0("attrpos_", nm), k)
  }
}
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]), d[, sum(choice), .(id, task)][, all(V1 == 1)])
d[, c("sel", paste0("n", 1:9), paste0("v", 1:9)) := NULL]
cv <- c(cov_age = "C1", cov_gender = "C2", cov_education = "C3", cov_prefecture = "C4", cov_employment = "C6",
        cov_income = "C8", cov_left_right = "D1_1", cov_turnout_history = "D2", cov_smd_vote = "D3",
        cov_pr_vote = "D5", cov_party_id = "D6", cov_abe_approval = "D8")
for (v in names(cv)) d[, (v) := as.integer(x[[cv[[v]]]])[id]]
d[, cov_age := cov_age + 19L]
d[, cov_gender := c("male", "female")[cov_gender]]
d[, cov_education := c("Middle school", "High school", "Polytechnic, two-year college, advanced vocational school",
                       "Four-year college or post-graduate school", "Others (e.g., never attended school)")[cov_education]]
d[, cov_party_id := c("Liberal Democratic Party of Japan", "Democratic Party of Japan", "Japan Innovation Party", "Komeito",
                      "Party for Future Generations", "Japan Communist Party", "People's Life Party",
                      "Social Democratic Party", "Other party", "No party to support")[cov_party_id]]
d[, id := frank(id, ties.method = "dense")]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "horiuchi_2018_japan_manifestos.csv"))
