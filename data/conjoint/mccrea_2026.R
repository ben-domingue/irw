##Therapist-choice conjoint (symbolic representation in mental health care) from
##McCrea, A. M., & Favero, N. (2026). Preferences for symbolic representation: Identity, context,
##and selection of mental health providers. International Public Management Journal, 1-21.
##https://doi.org/10.1080/10967494.2026.2723042
##Replication data: Harvard Dataverse doi:10.7910/DVN/A9ZLUN, CC0 1.0. File read:
##mental_health_conjoint.tab (saved as data.tab; Qualtrics wide export). Read as text only:
##preferences_for_symbolic_rep.do (value labels, reshape), README.md.
##Usage: Rscript mccrea_2026.R <dir holding data.tab> <output dir>
##
##1,503 US Prolific respondents (English), 3 scenarios (tasks) x 2 therapists. Qualtrics stores per
##scenario t and attribute slot k the attribute name F_t_k and the two levels F_t_1_k / F_t_2_k,
##as displayed text. Nine attributes exist (Sex/Gender, Race/Ethnicity, Next Available Session,
##Session Format, Overall Rating, Professional Degree, Years of Experience, Specialty 1, Specialty 2),
##but each respondent is in one of three versions (trial_version, the source's `version`) that shows
##seven: no_specialty (both specialty rows omitted), no_professionalinfo (degree and experience
##omitted), no_sessioninfo (availability and format omitted). Omitted attributes are "(not shown)".
##The authors' analysis drops the no_sessioninfo version (do-file L10); it is kept here.
##Attribute row order is randomized per RESPONDENT (identical in all 3 scenarios of every
##respondent): attrpos_* = slot 1-7 of the shown attributes, NA when not shown.
##Outcomes (question wording and scale anchors are not deposited; paraphrase):
##  choice  = choice_scenario<t> (1 = therapist A/profile 1, 2 = B), forced, no opt-out.
##  rating  = rating_a/_b_scenario<t>, 1-7, stored raw. Higher = more favourable (in scenario 1 the
##            chosen therapist has the higher rating in 1,251 of 1,503 tasks, the lower in 252
##            incl. ties).
##Whether the three scenarios differed in framing is not documented in the deposit; they are tasks 1-3.
##Covariates (labels from the do-file's label define lines): cov_gender (gender: 1 Man/male -> male,
##2 Woman/female -> female, 3 Non-binary/Other and 4 (self-described; do-file folds 4 into 3) -> other,
##-9 -> NA), cov_sexual_orientation (1 Straight/heterosexual, 2 Gay/lesbian, 3 Bisexual, 4 Not listed,
##-9 -> NA), cov_insured (1 Yes, 2 No, -8 Don't know, -9 -> NA), cov_seen_therapist and
##cov_current_therapy (1 Yes, 2 No, -9 -> NA), cov_race_* (0/1 checkboxes, do-file variable labels;
##blank = unchecked -> 0), cov_age (years), cov_duration_sec (whole survey, Qualtrics duration).
##No labels in the deposit for education (1-8), employment (1-8), income (1-6), party (1-3), state,
##insurancetype: kept as *_code. attention is 3 for everyone (constant) and dropped.
##PII: the deposit README says Prolific IDs were deleted, but PROLIFIC_PID, STUDY_ID and SESSION_ID
##are present; they are dropped with ResponseId, dates and the free-text fields (gender_4_TEXT,
##race_8_TEXT, party_3_TEXT, sexualorientation_4_TEXT). id = row number of the export.
##No survey weight. Paper sample size not checked (article paywalled).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.tab"), na.strings = "")
s[, id := .I]
nm <- c("Sex/Gender" = "sex_gender", "Race/Ethnicity" = "race_ethnicity", "Next Available Session" = "next_available_session",
        "Session Format" = "session_format", "Overall Rating" = "overall_rating", "Professional Degree" = "professional_degree",
        "Years of Experience" = "years_of_experience", "Specialty 1" = "specialty_1", "Specialty 2" = "specialty_2")
hide <- list(no_specialty = c("specialty_1", "specialty_2"), no_professionalinfo = c("professional_degree", "years_of_experience"),
             no_sessioninfo = c("next_available_session", "session_format"))
stopifnot(all(s$version %in% names(hide)))
L <- list()
for (t in 1:3) for (p in 1:2) {
  x <- s[, .(id, task = t, profile = p, trial_version = version,
             choice = as.integer(get(paste0("choice_scenario", t)) == p),
             rating = as.integer(get(paste0("rating_", c("a", "b")[p], "_scenario", t))))]
  for (v in nm) { x[, paste0("attr_", v) := "(not shown)"]; x[, paste0("attrpos_", v) := NA_integer_] }
  for (k in 1:7) {
    an <- nm[s[[sprintf("F_%d_%d", t, k)]]]
    stopifnot(!anyNA(an))
    lv <- s[[sprintf("F_%d_%d_%d", t, p, k)]]
    stopifnot(!anyNA(lv), all(lv != ""))
    for (v in unique(an)) {
      w <- which(an == v)
      set(x, w, paste0("attr_", v), lv[w]); set(x, w, paste0("attrpos_", v), k)
    }
  }
  L[[length(L) + 1]] <- x
}
d <- rbindlist(L)
##every respondent shows exactly the 7 attributes of their version
for (vv in names(hide)) for (v in nm) {
  sh <- d[trial_version == vv, get(paste0("attr_", v)) != "(not shown)"]
  stopifnot(all(sh == !(v %in% hide[[vv]])))
}
stopifnot(!anyNA(d$choice), !anyNA(d$rating), d[, sum(choice), .(id, task)][, all(V1 == 1)])
##attribute order identical across the 3 scenarios of a respondent
stopifnot(d[, uniqueN(paste(attrpos_sex_gender, attrpos_race_ethnicity, attrpos_overall_rating)), id][, all(V1 == 1)])
g <- as.integer(s$gender)
cov <- s[, .(id, cov_age = as.integer(age),
             cov_gender = c("male", "female", "other", "other")[fifelse(g %in% 1:4, g, NA_integer_)],
             cov_sexual_orientation = c("Straight/heterosexual", "Gay/lesbian", "Bisexual", "Not listed")[fifelse(sexualorientation %in% 1:4, sexualorientation, NA_integer_)],
             cov_insured = fcase(insured == 1, "Yes", insured == 2, "No", insured == -8, "Don't know", default = NA_character_),
             cov_seen_therapist = fcase(seentherapist == 1, "Yes", seentherapist == 2, "No", default = NA_character_),
             cov_current_therapy = fcase(currenttherapy == 1, "Yes", currenttherapy == 2, "No", default = NA_character_),
             cov_race_white = race_1, cov_race_black = race_2, cov_race_hispanic = race_3, cov_race_asian = race_4,
             cov_race_american_indian = race_5, cov_race_pacific_islander = race_6, cov_race_mena = race_7,
             cov_race_not_listed = race_8, cov_race_prefer_not = race__9,
             cov_education_code = education, cov_employment_code = employment, cov_income_code = income,
             cov_party_code = party, cov_state_code = state, cov_insurance_type_code = insurancetype,
             cov_duration_sec = as.integer(Duration__in_seconds_))]
stopifnot(all(s$gender %in% c(-9, 1:4)), all(s$sexualorientation %in% c(-9, 1:4)), all(s$insured %in% c(-9, -8, 1, 2)))
rc <- grep("^cov_race_", names(cov), value = TRUE)
for (v in rc) set(cov, which(is.na(cov[[v]])), v, 0L)
d <- merge(d, cov, by = "id")
stopifnot(uniqueN(d$id) == 1503, nrow(d) == 1503 * 6)
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mccrea_2026_therapist_choice.csv"))
