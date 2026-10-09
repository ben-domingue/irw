##Country-profile conjoint (32 countries) from
##Neundorf, A., Dahlum, S., Frederiksen, K. V. S., & Ozturk, A. (2026). Elections without
##constraints? The appeal of electoral autocracy across the world. British Journal of
##Political Science, 56, e1. https://doi.org/10.1017/S0007123425101129
##Replication data: Harvard Dataverse doi:10.7910/DVN/MFAWCE, CC0 1.0, no restricted files,
##no terms. Files read: conjoint.dta (Dataverse "original format" download, 128 MB), the
##authors' conjoint.do and ReadMe.txt (read as text). Design facts from the article text
##(Table 1 and the Appendix B screen are images and were not read).
##Usage: Rscript neundorf_2026.R <raw dir> <output dir>
##
##Respondents recruited through Facebook/Instagram ads in 32 countries, 16 Dec 2022 - 21 May
##2023 (Turkey first). Pairs of hypothetical countries, "What kind of society would you prefer
##to live in?": 10 pairs in Turkey, 5 pairs elsewhere (cut after the Turkish fieldwork because of
##dropout). 7 binary attributes, independently randomized; attributes grouped in democracy,
##security and society blocks whose order was randomized once per respondent (not recorded in
##the file, so no attrpos_). The article analyses all countries pooled (with country subgroups),
##so this is one table with cov_nationality.
##Structure: one row per respondentid x countryprofile (_1.._20; plus one "der" row per
##Turkish respondent holding no profile, dropped). task = (k+1) %/% 2 and profile = 2 - k %% 2
##for countryprofile _k, i.e. _1/_2 = task 1 profile 1/2. Checked: in every one of the 141,369
##answered pairs exactly one profile has live == 1. Which side was profile 1 is not documented.
##ATTRIBUTE TEXT = the deposit's value labels on the authors' binary recodes (elections =
##"RECODE of elections1", etc.); the displayed sentences (Table 1) are not in the deposit, and the
##survey ran in English, Spanish and (in Turkey) a language the article does not state. The
##article says all attributes are binary, so the recodes do not merge displayed levels.
##  attr_elections       Free and fair / Not free nor fair
##  attr_checks          Constraints / No constraints          (constraints on the executive)
##  attr_free_speech     Free speech / Not free speech
##  attr_economy         Struggle / No struggle                (figure labels Hardship / Prosperity)
##  attr_crime           High crime / Low crime
##  attr_gender_equality Equal / Not equal                     (equal pay between genders)
##  attr_diversity       Diverse / Similar                     (ethnic diversity)
##Outcomes:
##  choice = live: preferred country to live in, forced choice of the pair, no opt-out.
##  rating_democracy = democ: "How would you rate the level of democracy in each country?",
##           asked 0 (very low) to 10 (very high); the deposit holds only the authors' rescaled
##           0-1 version (0, 0.1, ..., 1), stored as in the file (x 10 = the answer given).
##  rating_quality_of_life = qol: quality of life in each country (article Appendix D; wording not
##           read), also only as the 0-1 rescale.
##Respondents: 35,306 with an answered pair in the file (35,292 after the drop below) vs the article's 35,281 valid respondents
##(282,560 profiles; 282,738 answered profiles here). Partial completers are kept (2-20 profiles).
##41 tasks with a missing attribute recode are dropped whole. Rows with no outcome are omitted;
##36,261 respondents have some answer, 35,292 a choice. Spot check: choice AMCEs for elections
##(0.157) and economy (0.150) match the article's 16 and 15 points; crime has no effect (0.000),
##as the article reports.
##Covariates: cov_nationality = ccnumeric value label text as in the source (respondent
##nationality / country group used by the authors as country fixed effect; labels are the
##survey's own words, e.g. "Argentinos", "Kenyan", "turkish", with a few junk labels:
##"'+Chilenos+", "'--sanitized--", "Hong+Kongers" kept as is); cov_language = "English" /
##"Spanish" from the english/spanish indicators (NA for Turkey, not recorded); cov_age = age (years,
##as deposited); cov_birth_year; cov_gender_code = gender as coded (1 and 3 occur; no labels or
##codebook map them); cov_education = education answer text (Turkish sample only);
##cov_duration_sec = duration ("Duration (in seconds)"). Dropped: id (Qualtrics ResponseId:
##platform ID), city (Turkish province + city of residence), income/polint/urban (Turkish
##sample only), and the authors' derived scales and groupings (sd, supportdem, hardship,
##educationnumerical, democracyscale*, securityscale, conservative, general_treatment, aod,
##newold, democracystatus, hdi, macro_security, year, english/spanish/proficient flags).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "conjoint.dta"))
ccl <- attr(k$ccnumeric, "labels")
z <- as.data.table(zap_labels(k)); rm(k); gc()
z <- z[countryprofile != "der"]
z[, kk := as.integer(sub("^_", "", countryprofile))]
stopifnot(!anyNA(z$kk), z[, anyDuplicated(paste(respondentid, kk))] == 0)
z[, `:=`(task = (kk + 1L) %/% 2L, profile = 2L - kk %% 2L)]
z <- z[!(is.na(live) & is.na(democ) & is.na(qol))]
av <- c("elections", "checks", "freespeech", "economy", "crime", "genderequality", "diversity")
bad <- z[, .(b = any(!complete.cases(.SD))), .(respondentid, task), .SDcols = av][b == TRUE]
cat("tasks dropped for a missing attribute:", nrow(bad), "\n")
z <- z[!bad, on = .(respondentid, task)]
chk <- z[!is.na(live), .(s = sum(live), n = .N), .(respondentid, task)]
stopifnot(all(chk$n == 2 & chk$s == 1))
lv <- list(elections = c("Not free nor fair", "Free and fair"), checks = c("No constraints", "Constraints"),
           freespeech = c("Not free speech", "Free speech"), economy = c("Struggle", "No struggle"),
           crime = c("High crime", "Low crime"), genderequality = c("Not equal", "Equal"), diversity = c("Similar", "Diverse"))
nm <- c(elections = "elections", checks = "checks", freespeech = "free_speech", economy = "economy",
        crime = "crime", genderequality = "gender_equality", diversity = "diversity")
d <- data.table(id = as.integer(z$respondentid), task = z$task, profile = z$profile, choice = as.integer(z$live),
                rating_democracy = z$democ, rating_quality_of_life = z$qol)
for (v in av) { stopifnot(all(z[[v]] %in% 0:1)); d[, paste0("attr_", nm[[v]]) := lv[[v]][z[[v]] + 1L]] }
stopifnot(all(round(d$rating_democracy * 10, 4) %in% c(0:10, NA)), all(round(d$rating_quality_of_life * 10, 4) %in% c(0:10, NA)))
d[, `:=`(rating_democracy = round(rating_democracy, 1), rating_quality_of_life = round(rating_quality_of_life, 1))]
d[, `:=`(cov_nationality = names(ccl)[match(z$ccnumeric, ccl)],
         cov_language = fifelse(z$english %in% 1, "English", fifelse(z$spanish %in% 1, "Spanish", NA_character_)),
         cov_age = as.integer(z$age), cov_birth_year = as.integer(z$birth_year), cov_gender_code = as.integer(z$gender),
         cov_education = fifelse(z$education == "", NA_character_, z$education), cov_duration_sec = as.numeric(z$duration))]
stopifnot(!anyNA(d$cov_nationality), d[, uniqueN(cov_nationality), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "neundorf_2026_electoral_autocracy.csv"))
