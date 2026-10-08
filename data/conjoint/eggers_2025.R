##City-council office vignette conjoint (US) from
##Eggers, A., Fowler, A., Howell, W., & Offer-Westort, M. (2025). Opportunities to govern: How to
##increase the supply of moderate and qualified candidates. Political Science Research and
##Methods, advance online publication (YouGov project UCHI0012). https://doi.org/10.1017/psrm.2025.10076
##(citation from Crossref; the article itself was not read).
##Replication data: Harvard Dataverse doi:10.7910/DVN/BQAHGZ, CC0 1.0, no restricted files.
##Files read (from PSRM.zip): data/UCHI0012_OUTPUT.sav (YouGov SPSS export, value labels used),
##UCHI0012_codebook.pdf. Read as text, not run: README.md, cleaning.do, tables.do,
##logs/master_replication.log. CCES22_Common_OUTPUT_vv_topost.dta (878 MB, CES 2022, external
##validation only) not extracted.
##Usage: Rscript eggers_2025.R <dir holding UCHI0012_OUTPUT.sav> <output dir>
##
##3,000 news-engaged US registered voters (YouGov, matched sample, January 16-30, 2024), each
##read 8 descriptions of a city-council seat and rated their interest in running for it.
##Single-profile text vignette: 7 sentences, each carrying one randomized feature (campaign
##funds to raise, chances of winning, salary, local news appearances, majority needed to pass
##a policy, powers of the city manager, staff size). attr_ holds each sentence as displayed,
##with the <b></b> bold tags of the export removed (e.g. "Your chances of winning are slim.").
##The order of the 7 sentences was randomized once per respondent (item position is constant
##within respondent for all 3,000; checked): attrpos_ = position 1-7. task = vignette number
##(1-8), profile = 1. 3,000 respondents and 24,000 ratings, as in the replication log (Table 1).
##Outcome: rating = conjoint_office_t, 1 "No interest whatsoever" to 10 "Highest possible
##interest" (codebook value labels); higher = more interested; stored raw (the authors rescale
##to 0-1). The question wording and vignette introduction are not in the deposit (codebook
##label: "Vignette t scale"). No missing ratings. Level probabilities and any restrictions are
##not stated; within each feature the level shares are near-equal (e.g. fundraising 4,740-4,835
##of 24,000 per level).
##Covariates: cov_survey_weight (weight, YouGov registered-voter weight), cov_age (age_client,
##years), cov_gender (gender4 value labels: Woman -> female, Man -> male, Non-binary and
##Other -> other), cov_education (educ label text), cov_party_id (pid3 label text),
##cov_party_id7 (pid7 label text; "Not sure" kept), cov_race (race label), cov_ideology7
##(cv_ideology label), cov_state (inputstate label), cov_duration_sec (endtime - starttime,
##whole questionnaire). Dropped: caseid (YouGov case id; respondents re-keyed 1..3000 in
##caseid order), free-text political-knowledge answers (cv_know_*), the authors' other survey
##items (direct_* ratings, CRT, earnings, attitudes) and industrynaics. No task is repeated.
##Spot check: lm(rating ~ features + factor(id) + factor(task)) on the authors' 0-1 codings
##reproduces Table 1 exactly (replication log L1521-1545: fundraising -.0456, winning .0776,
##pay .0602, authority .0386).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "UCHI0012_OUTPUT.sav")))
stopifnot(nrow(s) == 3000, !anyDuplicated(s$caseid))
setorder(s, caseid); s[, id := .I]
lab <- function(x) as.character(as_factor(x))
cv <- s[, .(id, cov_survey_weight = as.numeric(weight), cov_age = as.integer(age_client),
            cov_gender = unname(c(Woman = "female", Man = "male", "Non-binary" = "other", Other = "other")[lab(gender4)]),
            cov_education = lab(educ), cov_party_id = lab(pid3), cov_party_id7 = lab(pid7), cov_race = lab(race),
            cov_ideology7 = lab(cv_ideology), cov_state = lab(inputstate),
            cov_duration_sec = as.numeric(difftime(endtime, starttime, units = "secs")))]
stopifnot(!anyNA(cv$cov_gender))
for (v in c("cov_education", "cov_party_id", "cov_party_id7", "cov_race", "cov_ideology7", "cov_state"))
  stopifnot(!any(cv[[v]] %in% c("skipped", "not asked")))
m <- melt(s[, c("id", grep("^vignette[1-8]_item[1-7]$", names(s), value = TRUE)), with = FALSE],
          id.vars = "id", variable.factor = FALSE)
m[, `:=`(task = as.integer(sub("^vignette(\\d)_item\\d$", "\\1", variable)),
         pos = as.integer(sub("^vignette\\d_item(\\d)$", "\\1", variable)))]
stem <- c("To run for the office, you will need to raise" = "fundraising", "Your chances of winning are" = "winning",
          "Should you win, your annual salary will be" = "salary",
          "Typically, members of the city council appear on the local news" = "local_news",
          "To pass a policy on the council, sponsors of a bill must convince" = "majority",
          "There is a city manager who has very" = "city_manager", "Council members will have a staff of" = "staff")
m[, att := unname(stem[trimws(sub("<b>.*$", "", value))])]
m[, text := trimws(gsub("</?b>", "", value))]
stopifnot(!anyNA(m$att), m[, .N, .(id, task, att)][, all(N == 1)], m[, uniqueN(pos), .(id, att)][, all(V1 == 1)])
w <- dcast(m, id + task ~ att, value.var = c("text", "pos"))
setnames(w, sub("^text_", "attr_", sub("^pos_", "attrpos_", names(w))))
r <- melt(s[, c("id", paste0("conjoint_office_", 1:8)), with = FALSE], id.vars = "id", variable.factor = FALSE)
r[, task := as.integer(sub("conjoint_office_", "", variable))]
stopifnot(all(r$value %in% 1:10))
d <- merge(w, r[, .(id, task, rating = as.integer(value))], by = c("id", "task"))
d[, profile := 1L]
d <- merge(d, cv, by = "id")
a7 <- unname(stem)
setcolorder(d, c("id", "task", "profile", "rating", paste0("attr_", a7), paste0("attrpos_", a7)))
stopifnot(nrow(d) == 24000)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "eggers_2025_council_office.csv"))
