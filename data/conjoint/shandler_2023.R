##Cyberterrorism-classification conjoint (three national samples) from
##Shandler, R., Kostyuk, N., & Oppenheimer, H. (2023). Public opinion and cyberterrorism.
##Public Opinion Quarterly, 87(1), 92-119. https://doi.org/10.1093/poq/nfad006
##Replication data: Harvard Dataverse doi:10.7910/DVN/FU62PS, CC0 1.0. File read:
##"Combined Conjoint Data.csv" (Dataverse "original format" download, a wide Qualtrics
##export). The deposit has no codebook; the authors' Replication_Code.R was read as text
##(not run) for the level codes, and the article (open access, PMC10127534) for the design.
##Usage: Rscript shandler_2023.R <dir holding the .csv, saved as combined.csv> <output dir>
##
##One design fielded simultaneously on 26 August 2020 in three countries: US (MTurk, 1,012
##respondents), UK (Prolific, 1,010) and Israel (Midgam, 1,014, shown in Hebrew). ONE table,
##shandler_2023_cyberterror, with cov_country, because the authors analyse the three
##samples together (Replication_Code.R reads one combined file, fits a pooled AMCE, then
##country interactions), and they work with the English level labels for all three; this
##follows the IRW rule of keeping a design together where the researchers did (Ben,
##2026-10-07). Until 2026-10-07 this was three tables (_us, _uk, _il, irw_conjoint v1.1).
##Counts match the article's retained samples (respondents who completed all conjoint
##questions and passed reCAPTCHA; the deposit holds only these).
##Each respondent read 7 single scenarios (profile is always 1; task 1-7 in order shown)
##describing a cyber incident with 5 attributes: method, target, actor, motivation,
##outcome. attr_* hold the ENGLISH sentence fragments as displayed in the US and UK. For
##Israel each level is mapped through its level code (Method<k>, Target<k>, Agent<k>,
##Motivation<k>, Outcome<k>) to the same English fragment; Israeli respondents saw the
##Hebrew version, which is not kept. The code -> text map is checked to be one-to-one in
##the US and UK rows. The Qualtrics export had double-encoded UTF-8 (a garbled no-break
##space in "a malicious"); this is repaired and written as a plain space. Restriction:
##an attack on online databases never had a minor or major explosion outcome.
##Outcome: rating = 1 if the respondent classified the incident as cyberterrorism, 0 if
##not (source Scenario<k>: 1 = yes, 2 = no; the authors' TerrorBinary). The exact
##question wording is not in the deposit or the article text ("participants responded
##whether they would or would not classify the incident as cyberterrorism"). Direction:
##higher = labelled terrorism, not "more favourable". There is no choice column.
##Covariates: cov_age (2020 - year born), cov_male (1 = male; source Gender == 2, as the
##authors code it), cov_education and cov_income (country questionnaires' raw codes,
##labels not deposited; codes differ by country), cov_political_position (1 = most liberal
##... 6 = most conservative), cov_party_id_us (US only, 1-7 raw code, labels not deposited).
##Dropped: IP address, latitude/longitude, Qualtrics ResponseId, Prolific/Midgam ID,
##page timings, threat/exposure/COVID batteries, and attention checks. id is the row
##number of the source file (re-keyed to 1..n across all three countries).
##Count note: 3,036 x 7 = 21,252 classifications are in the deposit; the article reports
##21,238 (14 fewer). Not reconciled.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "combined.csv"), encoding = "UTF-8")
## undo UTF-8 -> Windows-1252 -> UTF-8 double encoding
cp <- 128:159; cpchar <- iconv(rawToChar(as.raw(cp), multiple = TRUE), "CP1252", "UTF-8")
rev_map <- setNames(cp, sapply(cpchar, function(z) if (is.na(z)) NA_integer_ else utf8ToInt(z)))
fix <- function(x) vapply(x, function(z) {
  u <- utf8ToInt(z); if (all(u < 128)) return(z)
  b <- ifelse(u < 256, u, rev_map[as.character(u)]); stopifnot(!anyNA(b))
  r <- rawToChar(as.raw(b)); Encoding(r) <- "UTF-8"; stopifnot(validUTF8(r)); gsub(" ", " ", r)
}, "", USE.NAMES = FALSE)
names(s)[87:91] <- paste0(c("MethodOfAttack", "TargetOfAttack", "ActorType", "MotivationOfAttack", "OutcomeOfAttack"), 1)
s[, src := .I]
attrs <- c(method = "MethodOfAttack", target = "TargetOfAttack", actor = "ActorType",
           motivation = "MotivationOfAttack", outcome = "OutcomeOfAttack")
codes <- c(method = "Method", target = "Target", actor = "Agent", motivation = "Motivation", outcome = "Outcome")
d <- rbindlist(lapply(1:7, function(k) {
  x <- data.table(src = s$src, country = s$CountryCode, task = k, profile = 1L,
                  rating = as.integer(c(`1` = 1L, `2` = 0L)[as.character(s[[paste0("Scenario", k)]])]))
  for (a in names(attrs)) {
    x[, paste0("code_", a) := s[[paste0(codes[[a]], k)]]]
    x[, paste0("txt_", a) := s[[paste0(attrs[[a]], k)]]]
  }
  x
}))
stopifnot(!anyNA(d$rating), d[code_target == 5, all(code_outcome %in% c(1, 4, 5))])
## English text per level code, from the US and UK rows; must be one-to-one
for (a in names(attrs)) {
  en <- unique(d[country != 3, .(code = get(paste0("code_", a)), txt = fix(get(paste0("txt_", a))))])
  stopifnot(!anyDuplicated(en$code), !anyDuplicated(en$txt), all(d[[paste0("code_", a)]] %in% en$code))
  d[, paste0("attr_", a) := en$txt[match(get(paste0("code_", a)), en$code)]]
}
d[, (grep("^(code|txt)_", names(d), value = TRUE)) := NULL]
cv <- s[, .(src, cov_country = c("United States", "United Kingdom", "Israel")[CountryCode],
            cov_age = 2020L - as.integer(Year_Born), cov_male = as.integer(Gender == 2),
            cov_education = as.integer(Education), cov_income = as.integer(Income),
            cov_political_position = as.integer(Political_position), cov_party_id_us = as.integer(Party_ID_US))]
d <- merge(d[, country := NULL], cv, by = "src")
d[, id := match(src, sort(unique(src)))][, src := NULL]
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "shandler_2023_cyberterror.csv"))
