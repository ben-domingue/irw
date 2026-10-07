##Climate-migrant admission conjoint (United States and Germany) from
##Arias, S. B., & Blair, C. W. (2022). Changing tides: Public attitudes on climate
##migration. The Journal of Politics, 84(1), 560-567. https://doi.org/10.1086/715163
##Replication data: Harvard Dataverse doi:10.7910/DVN/FDML2N, CC0 1.0. Files read (raw
##Qualtrics exports, CSV "original format" downloads; first two rows are the question text
##and ImportId):
##  "Climate Migration 2_ Conjoint- USA_September 10, 2019_08.56.csv"
##  "Climate Migration 2_ Conjoint- Germany_September 11, 2019_02.58.csv"
##  germany_state_key.csv (Qualtrics state code -> German Land name).
##Level text and restrictions: conjoint_design.dat and conjoint_design_german2.dat (the
##Conjoint Survey Design Tool files, read as text). The authors' R script was read as text,
##not run. The deposit's other files (a vignette experiment in each country and a 2020
##follow-up) are not conjoints and are not used.
##Usage: Rscript arias_2022.R <dir holding the CSVs> <output dir>
##
##One table per country: separate samples fielded separately (US 2019-09, Germany 2019-09),
##analysed separately in the article, and the German sample saw German level text.
##  arias_2022_climate_migrants_us       US adults; "your state"
##  arias_2022_climate_migrants_germany  German adults; "Ihr Land"
##Each respondent saw 9 tasks of two migrant profiles ("Migrant 1", "Migrant 2") described by
##7 attributes: gender, language fluency, occupation, origin, reason for migration, religion,
##vulnerability. Attribute ORDER was re-randomized on every task and is kept as attrpos_*
##(1 = top row). Restriction (design file): language fluency "None" never shown with origin
##"Another region in your country". Levels uniform otherwise. Germany: level text as shown
##in German, except religion, which the German design file and data show in English
##("Christian", "Muslim", "Atheist"); the German fielding showed "Atheist" where the US
##showed "Agnostic".
##Outcomes (each task asked both, ratings first):
##  rating = "On a scale from 1 to 7, where 1 indicates that your state should absolutely
##    not admit the migrant and 7 indicates that your state should definitely admit the
##    migrant, how would you rate Migrant 1/2?" (Germany: "... Ihr Land ..."), 7 = admit.
##  choice = "Now imagine that you had to choose one applicant who would be allowed to stay
##    in your state, and the other applicant would be sent back to their own location of
##    origin. Which of the two applicants would you personally prefer to be allowed to stay
##    in your state?" Forced choice, no opt-out (choice is missing when skipped).
##Kept: all non-preview responses (Status 0); tasks with any outcome. Unfinished responses
##keep the tasks they answered.
##Covariates: cov_age (years; values outside 18-99 set missing), cov_female (GENDER_resp 2;
##the authors' code treats 2 as female; code 3 = other/unspecified -> missing),
##cov_native_born (NATIVE_BORN 1 = born in the survey country, per the authors' code),
##cov_state (US: state abbreviation; Germany: Land name from germany_state_key.csv).
##Dropped: IP address, latitude/longitude, Qualtrics ResponseId, panel id (psid), city,
##timing, the free-text "which factors mattered" item (Q89), SURVEY_HISTORY, and the other
##attitude covariates, which ship as unlabelled Qualtrics codes.
##Counts: US 1,085 and Germany 1,072 respondents with at least one answered task (2,157);
##the article reports 2,160 across both countries (3 more; not traced). Nearly all (1,034
##US, 1,033 Germany) answered all 9 tasks.
##Spot-check (choice marginal means by reason for migration): persecution highest (US 0.54,
##Germany 0.58), the three climate reasons 0.48-0.51, economic opportunity lowest (0.46,
##0.42), the article's headline ordering (refugees > climate migrants > economic migrants).
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
files <- c(us = "Climate Migration 2_ Conjoint- USA_September 10, 2019_08.56.csv",
           germany = "Climate Migration 2_ Conjoint- Germany_September 11, 2019_02.58.csv")
anames <- c("Gender" = "gender", "Language Fluency" = "language_fluency", "Occupation" = "occupation", "Origin" = "origin",
            "Reason for migration" = "reason", "Religion" = "religion", "Vulnerability" = "vulnerability",
            "Geschlecht" = "gender", "Sprachkompetenz" = "language_fluency", "Beruf" = "occupation", "Herkunft" = "origin",
            "Gründe für die Migration" = "reason", "Zusätzliche Belastung" = "vulnerability")
rq <- list(c("RATE_MIG1", "RATE_MIG2", "force_choice"), c("Q168", "Q169", "Q184"), c("Q170", "Q171", "Q186"),
           c("Q172", "Q173", "Q188"), c("Q174", "Q175", "Q190"), c("Q176", "Q177", "Q192"), c("Q178", "Q179", "Q194"),
           c("Q180", "Q181", "Q196"), c("Q182", "Q183", "Q198"))
key <- fread(file.path(raw, "germany_state_key.csv"), encoding = "UTF-8")
setnames(key, 1:2, c("code", "state_name"))
for (cc in names(files)) {
  x <- fread(file.path(raw, files[[cc]]), header = TRUE, encoding = "UTF-8", colClasses = "character")[-(1:2)]
  x <- x[Status == "0"]
  x[, id := seq_len(.N)]
  num <- function(v) suppressWarnings(as.integer(v))
  age <- num(x$Age); age[!is.na(age) & (age < 18 | age > 99)] <- NA
  g <- num(x$GENDER_resp)
  cv <- data.table(id = x$id, cov_age = age, cov_female = fifelse(g == 2L, 1L, fifelse(g == 1L, 0L, NA_integer_)),
                   cov_native_born = fifelse(num(x$NATIVE_BORN) == 1L, 1L, fifelse(num(x$NATIVE_BORN) == 2L, 0L, NA_integer_)),
                   cov_state = if (cc == "us") x$state_region else key$state_name[match(num(x$state_region), key$code)])
  cv[cov_state == "", cov_state := NA]
  d <- rbindlist(lapply(1:9, function(t) rbindlist(lapply(1:2, function(p) {
    r <- data.table(id = x$id, task = t, profile = p, rating = num(x[[rq[[t]][p]]]), fc = num(x[[rq[[t]][3]]]))
    for (k in 1:7) {
      an <- anames[x[[sprintf("F-%d-%d", t, k)]]]
      stopifnot(!anyNA(an))
      lv <- x[[sprintf("F-%d-%d-%d", t, p, k)]]
      for (v in unique(an)) { w <- an == v; r[w, paste0("attr_", v) := lv[w]]; r[w, paste0("attrpos_", v) := k] }
    }
    r
  }))))
  d[, choice := fifelse(is.na(fc), NA_integer_, as.integer(fc == profile))][, fc := NULL]
  d <- d[!is.na(choice) | !is.na(rating)]
  stopifnot(d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% c(1:7, NA)))
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr")]))
  if (cc == "germany") stopifnot(d[attr_origin == "Aus einem anderen Teil Ihres Landes" & attr_language_fluency == "Keine", .N] == 0)
  d <- merge(d, cv, by = "id")
  ids <- unique(d$id); d[, id := match(id, ids)]
  ac <- sort(grep("^attr_", names(d), value = TRUE)); pc <- sort(grep("^attrpos_", names(d), value = TRUE))
  setcolorder(d, c("id", "task", "profile", "choice", "rating", ac, pc))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, sprintf("arias_2022_climate_migrants_%s.csv", cc)))
}
