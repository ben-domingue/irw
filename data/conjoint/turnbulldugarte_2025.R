##Single-profile dating-app conjoints (Spain, UK) on party labels and far-right normalization, from
##Turnbull-Dugarte, S. J., & Lopez-Ortega, A. (2025). Far right normalization and centrifugal affect: Evidence from the
##dating market. Journal of Politics. https://doi.org/10.1086/736698
##Replication data: Harvard Dataverse doi:10.7910/DVN/FYZANZ, CC0 1.0 (no terms, no restricted files).
##Files read: conjoint_ES.rds, conjoint_UK.rds, subscript1_datawrangling.R and subscript2_mainanalysis.R (as text; the
##authors' factor labels), replication_script_README.R. Other deposit files (BES waves, E-DEM, observational .tab, figures,
##RStudio state) are not conjoint data and were not read.
##Usage: Rscript turnbulldugarte_2025.R <dir holding es.rds and uk.rds> <output dir>
##
##TWO TABLES (two samples, different attribute wording and language, different attribute sets):
##  turnbulldugarte_2025_dating_spain  (ES, Spanish profile text, 1,949 respondents in the file)
##  turnbulldugarte_2025_dating_uk     (UK, English, Prolific, 2,023 respondents in the file)
##Design: each respondent saw 10 fake dating-app profiles ONE AT A TIME (the triage doubt "rival profiles missing" is
##resolved: it is a single-profile design, one row per round) and responded with a code 1/2/4 (`choice` in the file).
##The deposit documents no question text or code labels. The authors' binary outcome `selected` is 0 for code 1 and 1 for
##codes 2 and 4 (verified in both files); it is stored as `choice` (a single-profile accept/reject, opt_out = yes); the raw
##code is kept as trial_response_code (its 2-vs-4 meaning is undocumented). task = round 1..10, profile = 1.
##Profile attributes (per the authors' AMCE formulas, text of the displayed fields): flag (nationality/EU flag emoji,
##stored as the authors' description: ES "No flag/Spanish flag [sic: 'Spansish flag']/EU flag/Spanish & EU flag"; UK
##6 levels), orientation (BISEXUAL: authors' labels "Hetero." / "Bi."), trans (authors' "Cis." / "Trans."), gender
##congruence of the photo (authors' "Less/More gender congruent"), ethnicity and emotion of the photo (photo-derived
##authors' codes: Asian/Black/Latinx/White; Smiling/Not smiling), relationship goal text, distance, education (school or
##university name as displayed), job (as displayed), age, hobbies (three hobbies with emoji, a JSON string as stored),
##and the political party hashtag (#Vota... / #Vote...). ES also has a vegan marker (field PRONOUNS holds "Vegana" /
##"Vegano"); UK has pronouns (field PRONOUNS "He/Him" / "She/Her"). The photo id (PERSON) and the derived scales/dummies
##(PROS, VEG, BI, FLAG factors, *_SLIM class collapses, CONGRUENCE x respondent flags) are dropped.
##"(not shown)" is INFERRED, not documented, from where the field is empty: PARTY is empty exactly in the arm
##"Without party labels" (9,638 ES / 9,629 UK rows; by design, a randomized arm: kept as trial_party_labels);
##education empty = ES 3,284 rows that the authors code "No education specified" (UK 3,753 rows; the authors also give 887
##UK rows with an education name the SLIM label "No education specified", the text is kept); the vegan marker (ES) and
##pronouns (UK) are empty for about 70% of profiles. Profile gender (GENDER, Man/Woman) is set by the respondent's gender
##and sex preference, NOT randomized: kept as trial_profile_gender, not as an attribute (no crosswalk).
##Restrictions/level probabilities are not documented. The authors' main models use only the "With party labels" arm;
##both arms are kept.
##Rows with all profile fields missing (71 ES rows of 62 respondents, 168 UK rows of 117; unfinished round) are dropped.
##Covariates: cov_gender (respondent gender: "a man"/"a woman" -> male/female; others NA), cov_party_id (`party_id` text,
##blank -> NA); ES only: cov_age (`age`, whole years) and cov_education_code (`educ` codes, labels not in the deposit); the
##UK file holds no respondent age or education. PII FOUND and dropped: Prolific IDs (UK PROLIFIC_PID), Qualtrics ResponseId, start/end/
##recorded dates, free-text relationship fields. id = integer re-key of ResponseId.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(f, lang) {
  d <- as.data.table(readRDS(file.path(raw, f)))
  d <- d[!is.na(ResponseId)]
  stopifnot(all(d$selected == as.integer(d$choice > 1)))
  d <- d[!is.na(BISEXUAL)]
  d[, id := as.integer(factor(ResponseId, levels = unique(ResponseId)))]
  ns <- "(not shown)"
  nz <- function(x) fifelse(is.na(x) | x == "", ns, as.character(x))
  r <- d[, .(id, task = as.integer(round), profile = 1L, choice = as.integer(selected),
    attr_flag = NATIONALITY,
    attr_orientation = fifelse(as.logical(BISEXUAL), "Bi.", "Hetero."), attr_trans = fifelse(as.logical(TRANS), "Trans.", "Cis."),
    attr_gender_congruence = fifelse(CONGRUENCE == "yes", "More gender congruent", "Less gender congruent"),
    attr_ethnicity = ETHNICITY, attr_emotion = EMOTION, attr_relationship = RELATIONSHIP, attr_distance = DISTANCE,
    attr_education = nz(EDUCATION), attr_job = JOB, attr_age = as.character(AGE), attr_hobbies = HOBBIES,
    attr_party = nz(PARTY),
    trial_response_code = as.integer(choice), trial_party_labels = experimental_group, trial_profile_gender = GENDER,
    cov_gender = c("a man" = "male", "a woman" = "female")[gender],
    cov_party_id = fifelse(party_id %in% c("", NA), NA_character_, party_id))]
  if (lang == "es") r[, `:=`(cov_age = as.integer(d$age), cov_education_code = as.integer(d$educ))]
  if (lang == "es") r[, attr_vegan := nz(d$PRONOUNS)] else r[, attr_pronouns := nz(d$PRONOUNS)]
  stopifnot(r[, .N, .(id, task)][, all(N == 1L)], !anyNA(r[, c("id", "task", "choice", grep("^attr_", names(r), value = TRUE)), with = FALSE]))
  setorder(r, id, task, profile); r
}
for (z in list(c("es.rds", "es", "turnbulldugarte_2025_dating_spain"), c("uk.rds", "uk", "turnbulldugarte_2025_dating_uk"))) {
  r <- build(z[1], z[2]); fwrite(r, file.path(out, paste0(z[3], ".csv")))
  message(z[3], ": ", nrow(r), " rows, ", uniqueN(r$id), " respondents")
}
