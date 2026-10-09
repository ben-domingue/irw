##Climate-migration conjoint (Federated States of Micronesia) from
##Gest, J., Núñez, L., Drinkall, S., & Micky, K. (2025). The effect of slow-onset climate change
##on migration decisions. International Migration Review. https://doi.org/10.1177/01979183251343879
##Replication data: Harvard Dataverse doi:10.7910/DVN/6EOCPF (Nunez, Gest, Drinkall), CC0 1.0, no
##restricted files, no terms. File read: "Micronesia Study_September 18, 2023_10.18.csv" (the only
##file; Qualtrics export with 3 header rows: names, question text, ImportIds). No codebook,
##questionnaire or code ships; wording is the export's question-text row. Article not read.
##Usage: Rscript gest_2025.R <dir holding the csv> <output dir>
##
##Sample: 648 interviews recorded offline (Qualtrics Status "Offline", 3 Jan - 13 Sep 2023; one
##"Survey Preview" row dropped); interviewers read the scenarios ("Listen closely as I read their
##full descriptions to you"); interview language English (253) or "Other" (392), as recorded.
##Design: 5 paired tasks. Each scenario has 5 binary attributes (level text from the embedded
##fields c<task>_<slot><scenario>, HTML <b> tags stripped):
##  health: "You develop a serious health problem needing treatment" / "Your health remains the same"
##  family: "Your family remains in FSM" / "A family member moves to the US"
##  job: "You are offered a job in the US" / "You don't know what kind of job you'll find in the US"
##  climate: "FSM expects typical weather events" / "More natural disasters are expected to hit FSM"
##  money: "You earn your usual money in Micronesia" / "You start earning less money in Micronesia"
##The five slots (named money, job, health, family, climate in the export but holding any
##attribute) are shown in the order money, job, health, family, climate ([Field-1..10] in the
##question text); the attribute in each slot is shuffled per TASK (both scenarios of a task share
##it, checked), so attrpos_* = slot position 1-5. The attribute name is read from the level text.
##Outcomes:
##  choice: "The following describes two scenarios. ... Please select the scenario in which you
##    would be more likely to migrate to the United States." Scenario 1 / Scenario 2; no opt-out
##    (1 respondent with no choices at all is omitted).
##  rating: "On a scale from 1 (highly unlikely) to 7 (highly likely), how likely would you be to
##    migrate to the US, based on the scenario Scenario <k>?" asked of both scenarios after the
##    choice. The export splits it into _cscale1a/2a (asked when Scenario 2 was chosen) and
##    _cscale1b/2b (Scenario 1 chosen); the piped fields ([Field-12] = scenario 2's fields 2,4,..)
##    give 1a = Scenario 2, 2a = Scenario 1, 1b = Scenario 1, 2b = Scenario 2, i.e. the "1"
##    question is always about the chosen scenario (mean 5.4 vs 2.8-3.1 for the other), which
##    confirms the mapping. Raw 1-7.
##trial_prime = `prime` (0/1, experiment arm; an attention question Q46 refers to "the article
##you just reviewed", i.e. a climate-risk article; what the arm showed is not documented here).
##Covariates as answer text: cov_gender (Female/Male -> female/male), cov_age (years; age 0 -> NA),
##cov_education (educ text), cov_marital_status, cov_religion, cov_remittances, cov_family_income,
##cov_lives_where (selflocation), cov_lives_terrain (the first `location` column), cov_plan_move
##(move), cov_passport, cov_internet, cov_family_us, cov_pers_risk_1..3 (0-10: sea level/tides,
##typhoons, heat/drought), cov_climate_perception_1..3, cov_risk_taking (1-7 as stored; anchors not in the export),
##cov_interview_language, cov_interview_place (the second `location` column), cov_duration_sec.
##PII FOUND and dropped: IPAddress (648), LocationLatitude/Longitude (511), Q38_4 e-mail (38) and
##Q38_5 phone number (118) left for recontact, ResponseId (ids re-keyed to row numbers).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "^Micronesia.*\\.csv$", full.names = TRUE)
stopifnot(length(f) == 1)
s <- read.csv(f, colClasses = "character", check.names = TRUE, encoding = "UTF-8")
s <- as.data.table(s[-(1:2), ])
s <- s[Status == "Offline"]
stopifnot(nrow(s) == 648)
s[, rid := seq_len(.N)]
slots <- c("money", "job", "health", "family", "climate")
key <- c(health = "health", family = "family", job = "job", weather = "climate", money = "money")
attname <- function(x) { x <- tolower(x); k <- names(key)[vapply(names(key), function(k) grepl(k, x, fixed = TRUE), TRUE)]
  ifelse(grepl("natural disasters", x), "climate", key[k[1]]) }
strip <- function(x) trimws(gsub("<[^>]+>", "", x))
nz <- function(x) fifelse(x == "", NA_character_, x)
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  ch <- s[[paste0("X", t, "_cchoice")]]
  r <- if (p == 1) fifelse(ch == "Scenario 1", s[[paste0("X", t, "_cscale1b_6")]], s[[paste0("X", t, "_cscale2a_6")]]) else
                   fifelse(ch == "Scenario 2", s[[paste0("X", t, "_cscale1a_6")]], s[[paste0("X", t, "_cscale2b_6")]])
  o <- data.table(id = s$rid, task = t, profile = p, ch = ch, rating = suppressWarnings(as.integer(r)))
  for (k in 1:5) {
    lv <- strip(s[[sprintf("c%d_%s%d", t, slots[k], p)]])
    other <- strip(s[[sprintf("c%d_%s%d", t, slots[k], 3 - p)]])
    an <- vapply(lv, attname, "")
    stopifnot(identical(unname(an), unname(vapply(other, attname, ""))))
    for (at in unique(an)) { o[an == at, paste0("attr_", at) := lv[an == at]]; o[an == at, paste0("attrpos_", at) := k] }
  }
  o
}), use.names = TRUE)), use.names = TRUE)
d <- d[ch %in% c("Scenario 1", "Scenario 2")]
d[, choice := as.integer(ch == paste("Scenario", profile))][, ch := NULL]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, !anyNA(.SD), .SDcols = patterns("^attr")],
          d[, all(sapply(.SD, uniqueN) == 2), .SDcols = patterns("^attr_")])
cv <- s[, .(id = rid, trial_prime = as.integer(prime),
            cov_gender = c(Female = "female", Male = "male")[gender], cov_age = {x <- as.integer(age); fifelse(x == 0L, NA_integer_, x)},
            cov_education = nz(educ), cov_marital_status = nz(marstat), cov_religion = nz(religion), cov_remittances = nz(remit),
            cov_family_income = nz(faminc), cov_lives_where = nz(selflocation), cov_lives_terrain = nz(location), cov_plan_move = nz(move),
            cov_passport = nz(passport), cov_internet = nz(internet), cov_family_us = nz(familyus),
            cov_pers_risk_1 = as.integer(nz(persrisk_1)), cov_pers_risk_2 = as.integer(nz(persrisk_2)), cov_pers_risk_3 = as.integer(nz(persrisk_3)),
            cov_climate_perception_1 = nz(climate_perception_1), cov_climate_perception_2 = nz(climate_perception_2),
            cov_climate_perception_3 = nz(climate_perception_3), cov_risk_taking = as.integer(nz(Riskaversion_1)),
            cov_interview_language = nz(language), cov_interview_place = nz(location.1), cov_duration_sec = as.integer(Duration..in.seconds.))]
d <- merge(d, cv, by = "id")
ac <- c("health", "family", "job", "climate", "money")
setcolorder(d, c("id", "task", "profile", "choice", "rating", paste0("attr_", ac), paste0("attrpos_", ac)))
setorder(d, id, task, profile)
cat(nrow(d), uniqueN(d$id), "\n")
fwrite(d, file.path(out, "gest_2025_climate_migration.csv"))
