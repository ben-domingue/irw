##Hypothetical-neighbour survey experiment (social value of political participation, US) from
##Anoll, A. P. (2018). What makes a good neighbor? Race, place, and norms of political participation. American
##Political Science Review, 112(3), 494-508. https://doi.org/10.1017/S0003055418000175
##Replication data: Harvard Dataverse doi:10.7910/DVN/SJI4IA, CC0 1.0, no restricted files. Files read:
##2National_Slim.csv (n = 2,000), 2Black_Slim.csv (1,201), 2Latino_Slim.csv (500), 2.SocialIncentivesSurvey.R (as
##text, for the variable meanings), ReadMe.rtf. Usage: Rscript anoll_2018.R <dir> <out dir>, the three csv files
##renamed national.csv black.csv latino.csv. The article's corrigendum (APSR 112(4), 1125) gives the control text and
##the randomization statement.
##
##3,701 US adults in three samples (national, Black oversample, Latino oversample), pooled by the authors (rbind in
##the .R file): cov_sample. Each saw FOUR hypothetical neighbours, one table of information per survey page (task 1,
##profiles 1-4 in the order shown), with attributes name (David/Anthony/Louis/Martin), age (34/35/37/38),
##occupation (Physical Therapist/Legal Assistant/High School Teacher/X-Ray Technician) and community involvement.
##Community involvement: profiles 1-3 show one of "Annually attends charitable events", "Annually attends political
##rallies", "Votes in every presidential election" (one each, random order); profile 4 is always the control
##"Annually attends neighborhood potluck dinners" (corrigendum: "appeared last for all respondents"; the deposit
##stores no text for it, so the string is from the corrigendum). Randomization restriction: each respondent sees each
##name, age, occupation and the three actions exactly once (levels drawn without repetition across the four profiles);
##all values except the control are random in order.
##Outcomes (rating, 1-7, same coding as the source; the instrument is not in the deposit, the .R file calls them
##"Likability" and "Respectability score" and the question wording and scale anchors are not available):
##  rating_like    = APA002 (profile 2), APA004 (profile 1), APA007 (profile 3), APA010 (profile 4)
##  rating_respect = APA003 (profile 2), APA005 (profile 1), APA008 (profile 3), APA011 (profile 4)
##The APA-number to profile mapping is the authors' (.R file lines 79-158: p2act <-> APA002/003, p1act <-> APA004/005,
##p3act <-> APA007/008, control <-> APA010/011). Direction (7 = most) is presumed, not documented.
##Covariates: cov_gender (Female/Male), cov_birth_year, cov_race (national: text; Black/Latino samples: the sample
##label), cov_party_id (pid3 text; "Not sure" kept), cov_state, cov_education_code (edu1 1-6) and cov_income_code (inc
##1-12) -- codes, no labels in the deposit. Dropped: zip code, case ids, region, ideology, nativity, the CPS/ACS
##neighbourhood files (not read). No survey weight in the survey files.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f, smp) { x <- fread(file.path(raw, f)); x[, cov_sample := smp]; x[, key := paste(smp, caseid)]; x }
s <- rbindlist(list(rd("national.csv", "national"), rd("black.csv", "black"), rd("latino.csv", "latino")), fill = TRUE)
stopifnot(nrow(s) == 3701, !anyDuplicated(s$key))
s[, id := .I]
ctl <- "Annually attends neighborhood potluck dinners"
L <- list()
for (p in 1:4) {
  lk <- c("APA004", "APA002", "APA007", "APA010")[p]; rs <- c("APA005", "APA003", "APA008", "APA011")[p]
  L[[p]] <- data.table(id = s$id, task = 1L, profile = p, rating_like = as.integer(s[[lk]]), rating_respect = as.integer(s[[rs]]),
    attr_name = trimws(s[[paste0("apa_name", p)]]), attr_age = as.character(s[[paste0("apa_age", p)]]),
    attr_occupation = trimws(s[[paste0("apa_occ", p)]]),
    attr_community_involvement = if (p < 4) trimws(s[[paste0("apa_comact", p)]]) else ctl)
}
d <- rbindlist(L)
cv <- s[, .(id, cov_sample, cov_gender = tolower(gender), cov_birth_year = as.integer(birthyr),
  cov_race = fifelse(cov_sample == "national", race, fifelse(cov_sample == "black", "Black", "Hispanic")),
  cov_party_id = trimws(pid3), cov_state = state2, cov_education_code = as.integer(edu1), cov_income_code = as.integer(inc))]
cv[cov_party_id == "Not Sure", cov_party_id := "Not sure"]
d <- merge(d, cv, by = "id")
stopifnot(!anyNA(d[, grep("^(attr_|rating_)", names(d)), with = FALSE]), d[, uniqueN(attr_name), by = id]$V1 == 4,
          d[, uniqueN(attr_occupation), by = id]$V1 == 4)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "anoll_2018_good_neighbor.csv"))
