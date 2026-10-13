##Immigrant-admission paired conjoint with an expected-location attribute (US, July 2024) from
##Lee, J., & Muttram, H. G. (2025). American immigration attitudes and NIMBYism: Do immigration
##preferences vary by spatial scale? PS: Political Science & Politics, 59(2), 320-328.
##https://doi.org/10.1017/S1049096525101467
##Replication data: Harvard Dataverse doi:10.7910/DVN/6TSZXR, CC0 1.0. File read:
##NIMBY_Immigration_Conjoint.tab (profile_id, case_id, pid3, weight, 10 attributes, selected).
##Usage: Rscript lee_2025_immigration_nimby.R <dir holding the .tab> <output dir>
##
##Verasight, US citizens 18+, July 16-21 2024. 1,313 recruited; the article and the authors'
##script report 20,954 profiles from 1,311 respondents, which is what the file holds (1,303
##respondents with 8 pairs, 8 with 5-7 pairs). Paired forced choice, 8 pairs per respondent:
##  choice = selected, "If you had to choose between them, which of these two immigrants should be
##           given priority to come to the United States to live?" (article); no neither option.
##task and profile are INFERRED from row order: the file has no task column, profile_id runs
##consecutively within case_id, and pairing consecutive rows (1-2, 3-4, ...) gives exactly one
##selected profile in every one of the 10,477 pairs (checked below). Profile position (left/right)
##is not recorded, so profile = order within the pair as stored.
##Attributes are level text as in the data (= the authors' factor levels; appendix C):
##education, gender, country, location (expected place of residence: The United States / Your
##state / Your city / Your neighborhood), fluency, reason, job, experience, plans, priorvisit.
##Restrictions: the authors' script fits "the model formula with restrictions" Education*Job and
##Reason*Country; the data confirm the Hainmueller-Hopkins (2015) rules: Computer programmer,
##Doctor, Financial analyst and Research scientist only with two years of college or more, and
##"Escape political/religious persecution" only for Iraq, Somalia and Sudan. Attribute order fixed
##(article). cov_party_id = pid3 (text; the string "NA" -> NA), cov_survey_weight = weight (the
##article's survey weight). ds_data.tab (age, income, education, race, homeowner) is NOT used: it
##has no respondent id and 1,313 rows, and its weights are not unique, so it cannot be linked.
##case_id is already a generated integer and is kept as id.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- fread(file.path(raw, "NIMBY_Immigration_Conjoint.tab"))
setorder(k, case_id, profile_id)
stopifnot(k[, all(diff(profile_id) > 0)], k[, .N, case_id][, all(N %% 2 == 0)])
k[, r := seq_len(.N), case_id]
d <- k[, .(id = as.integer(case_id), task = as.integer((r + 1L) %/% 2L), profile = as.integer(2L - r %% 2L),
           choice = as.integer(selected))]
src <- c(education = "Education", gender = "Gender", country = "Country", location = "Location", fluency = "Fluency",
         reason = "Reason", job = "Job", experience = "Experience", plans = "Plans", priorvisit = "PriorVisit")
for (v in names(src)) d[, paste0("attr_", v) := as.character(k[[src[[v]]]])]
d[, cov_party_id := fifelse(k$pid3 == "NA", NA_character_, k$pid3)]
d[, cov_survey_weight := as.numeric(k$weight)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1L)], d[, .N, .(id, task)][, all(N == 2L)],
          d[, uniqueN(cov_survey_weight), id][, all(V1 == 1L)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          uniqueN(d$id) == 1311L, nrow(d) == 20954L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lee_2025_immigration_nimby.csv"))
