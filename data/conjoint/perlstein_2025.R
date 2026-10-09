##Risk-conversation partner conjoint (Netherlands) from
##Perlstein, S., Kantorowicz, J., & Kuipers, S. (2025). Preferences for risk conversations in
##everyday life: a conjoint analysis. Journal of Risk Research.
##https://doi.org/10.1080/13669877.2025.2526479
##Replication data: Harvard Dataverse doi:10.7910/DVN/BU8VHO, CC0 1.0, no restricted files.
##Files read: data_clean.tab (Dataverse "original format" download, data_clean.csv: the
##Qualtrics export with its question-text and ImportId header rows, answers as numeric codes,
##conjoint levels as Dutch text). README.txt and conjoint_clean_main.Rmd read as text (the
##Rmd gives the authors' English translations of the levels).
##Usage: Rscript perlstein_2025.R <raw dir> <output dir>
##
##1,202 Dutch respondents (May 2024; ResponseId in the deposit is already a row number).
##Each saw pairs of hypothetical conversations, "Gesprek 1" (profile 1) and "Gesprek 2"
##(profile 2), described by 7 attributes in Dutch: Onderwerp (topic), Geslacht van de
##persoon, Relatie tot u, Band met u, Schijnbare kennis / bezorgdheid / motivatie van de
##persoon. Levels are stored as displayed (Dutch); conjoint_clean_main.Rmd gives English
##(e.g. "vriend/vriendin (platonisch)" = friend, "zeer hecht" = very close).
##Tasks: the intro screen shows a worked "Voorbeeld" (example) pair (F-1, answer
##conjoint_intro) and then "Taak 1 van 8" .. "Taak 8 van 8" (F-2 .. F-9, conjoint_1..8).
##Respondents answered the example too, and the authors' analysis (read.qualtrics with
##responses conjoint_intro, conjoint_1..8) treats it as a task, so all 9 are kept: task 1 is
##the example (trial_example = 1), tasks 2-9 are Taak 1-8.
##Outcome: choice, "In welk gesprek zou u liever willen deelnemen?" ("In which conversation
##would you rather take part?", translated), answer 1 = Gesprek 1, 2 = Gesprek 2; forced, no
##opt-out. 8-10 respondents left each task blank; those tasks are dropped (as the authors'
##drop_na(selected)).
##Attribute order was randomized once per respondent (row order F-t-j identical across all
##9 tasks for every respondent; varies between respondents): attrpos_<attr> = row position.
##Level shares are clearly unequal (e.g. "niet hecht", "niet bezorgd", "u te overtuigen om
##minder maatregelen te nemen" appear about half as often as other levels), and some
##combinations never occur within a profile: "vriend/vriendin (platonisch)" with "niet hecht";
##"niet bezorgd" with "u te overtuigen om meer maatregelen te nemen" or "zich minder ongerust
##voelen"; "u te overtuigen om minder maatregelen te nemen" with "redelijk bezorgd" or "zeer
##bezorgd". The deposit documents neither the weights nor these restrictions.
##1,195 respondents remain (7 left every task blank); 21,472 rows. The country is the
##Netherlands (Dutch questionnaire; the education question refers to "in Nederland").
##Covariates: the export holds codes and no value labels or questionnaire is deposited, so
##codes are kept: cov_gender_code (gender, "Wat is uw geslacht?"), cov_birth_year (age column,
##"Wat is uw geboortejaar?"), cov_education_code, cov_risk_talk_code, cov_information_seeking_code,
##cov_att_check, cov_att_check2, cov_att_check3 (colour attention check: pick 'paars' and
##'geel'; selected option codes as exported, comma-joined; 2 and 3 asked only after a miss),
##cov_duration_sec (whole survey). Dropped: free text gender_2_TEXT, dates, timers, the
##risk-perception grids per topic (risk_*), the conjoint_drivers ranking, display-order fields.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- fread(file.path(raw, "data_clean.csv"), colClasses = "character", na.strings = "")
r <- r[-(1:2)]
stopifnot(nrow(r) == 1202, !anyDuplicated(r$ResponseId))
id <- as.integer(r$ResponseId)
an <- c(Onderwerp = "topic", "Geslacht van de persoon" = "gender", "Relatie tot u" = "relation",
        "Band met u" = "closeness", "Schijnbare kennis van de persoon" = "knowledge",
        "Schijnbare bezorgdheid van de persoon" = "concern", "Schijnbare motivatie van de persoon" = "motivation")
resp <- c("conjoint_intro", paste0("conjoint_", 1:8))
d <- rbindlist(lapply(1:9, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = id, task = t, profile = p,
                  choice = as.integer(as.integer(r[[resp[t]]]) == p), trial_example = as.integer(t == 1))
  for (j in 1:7) {
    nm <- r[[sprintf("F-%d-%d", t, j)]]; stopifnot(all(nm %in% names(an)))
    lv <- r[[sprintf("F-%d-%d-%d", t, p, j)]]
    for (k in names(an)) { w <- nm == k
      if (j == 1) { x[, paste0("attr_", an[k]) := NA_character_]; x[, paste0("attrpos_", an[k]) := NA_integer_] }
      x[w, paste0("attr_", an[k]) := lv[w]]; x[w, paste0("attrpos_", an[k]) := j] }
  }
  x }))))
stopifnot(all(unlist(r[, lapply(resp, function(v) get(v) %in% c("1", "2", NA))])))
d <- d[!is.na(choice)]
stopifnot(d[, !anyNA(.SD), .SDcols = patterns("^attr")], d[, sum(choice), .(id, task)][, all(V1 == 1)],
          d[, uniqueN(paste(attrpos_topic, attrpos_gender, attrpos_relation)), id][, all(V1 == 1)])
cv <- data.table(id = id, cov_gender_code = as.integer(r$gender), cov_birth_year = as.integer(r$age),
  cov_education_code = as.integer(r$education), cov_risk_talk_code = as.integer(r$risk_talk),
  cov_information_seeking_code = as.integer(r$information_seeking),
  cov_att_check = r$att_check, cov_att_check2 = r$att_check2, cov_att_check3 = r$att_check3,
  cov_duration_sec = as.integer(r[["Duration (in seconds)"]]))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", grep("^attr_", names(d), value = TRUE), grep("^attrpos_", names(d), value = TRUE)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "perlstein_2025_risk_conversations.csv"))
