##Cyberterrorism-classification conjoint (three national samples) from
##Shandler, R., Kostyuk, N., & Oppenheimer, H. (2023). Public opinion and cyberterrorism.
##Public Opinion Quarterly, 87(1), 92-119. https://doi.org/10.1093/poq/nfad006
##Replication data: Harvard Dataverse doi:10.7910/DVN/FU62PS, CC0 1.0. File read:
##"Combined Conjoint Data.csv" (Dataverse "original format" download, a wide Qualtrics
##export). The deposit has no codebook; the authors' Replication_Code.R was read as text
##(not run) for the level codes, and the article (open access, PMC10127534) for the design.
##Usage: Rscript shandler_2023.R <dir holding the .csv, saved as combined.csv> <output dir>
##
##One design fielded simultaneously on 26 August 2020 in three countries; each country is
##its own population and the Israeli version was shown in Hebrew, so it is split into
##three tables: shandler_2023_cyberterror_us (MTurk, 1,012 respondents),
##shandler_2023_cyberterror_uk (Prolific, 1,010) and shandler_2023_cyberterror_il (Midgam,
##1,014, Hebrew). Counts match the article's retained samples (respondents who completed
##all conjoint questions and passed reCAPTCHA; the deposit holds only these).
##Each respondent read 7 single scenarios (profile is always 1; task 1-7 in order shown)
##describing a cyber incident with 5 attributes: method, target, actor, motivation,
##outcome. attr_* hold the sentence fragments as displayed (English in the US and UK,
##Hebrew in Israel). The Qualtrics export had double-encoded UTF-8 (Hebrew read as
##Windows-1252 mojibake, and "a malicious" with a garbled no-break space); this is
##repaired byte-for-byte and the no-break space written as a plain space. Restriction:
##an attack on online databases never had a minor or major explosion outcome.
##Outcome: rating = 1 if the respondent classified the incident as cyberterrorism, 0 if
##not (source Scenario<k>: 1 = yes, 2 = no; the authors' TerrorBinary). The exact
##question wording is not in the deposit or the article text ("participants responded
##whether they would or would not classify the incident as cyberterrorism"). Direction:
##higher = labelled terrorism, not "more favourable". There is no choice column.
##Covariates: cov_age (2020 - year born), cov_male (1 = male; source Gender == 2, as the
##authors code it), cov_education and cov_income (country questionnaires' raw codes,
##labels not deposited), cov_political_position (1 = most liberal ... 6 = most
##conservative), cov_party_id_us (US only, 1-7 raw code, labels not deposited).
##Dropped: IP address, latitude/longitude, Qualtrics ResponseId, Prolific/Midgam ID,
##page timings, threat/exposure/COVID batteries, and attention checks. id is the row
##number of the source file (re-keyed per table to 1..n).
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
d <- rbindlist(lapply(1:7, function(k) data.table(src = s$src, task = k, profile = 1L,
  rating = as.integer(c(`1` = 1L, `2` = 0L)[as.character(s[[paste0("Scenario", k)]])]),
  attr_method = fix(s[[paste0("MethodOfAttack", k)]]), attr_target = fix(s[[paste0("TargetOfAttack", k)]]),
  attr_actor = fix(s[[paste0("ActorType", k)]]), attr_motivation = fix(s[[paste0("MotivationOfAttack", k)]]),
  attr_outcome = fix(s[[paste0("OutcomeOfAttack", k)]]),
  code_target = s[[paste0("Target", k)]], code_outcome = s[[paste0("Outcome", k)]])))
stopifnot(!anyNA(d$rating), d[code_target == 5, all(code_outcome %in% c(1, 4, 5))])
d[, c("code_target", "code_outcome") := NULL]
cv <- s[, .(src, country = CountryCode, cov_age = 2020L - as.integer(Year_Born), cov_male = as.integer(Gender == 2),
            cov_education = as.integer(Education), cov_income = as.integer(Income),
            cov_political_position = as.integer(Political_position), cov_party_id_us = as.integer(Party_ID_US))]
d <- merge(d, cv, by = "src")
for (cc in list(c(1, "us"), c(2, "uk"), c(3, "il"))) {
  x <- d[country == as.integer(cc[1])][, country := NULL]
  if (cc[2] != "us") x[, cov_party_id_us := NULL]
  x[, id := match(src, sort(unique(src)))][, src := NULL]
  setcolorder(x, c("id", "task", "profile", "rating"))
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, paste0("shandler_2023_cyberterror_", cc[2], ".csv")))
}
