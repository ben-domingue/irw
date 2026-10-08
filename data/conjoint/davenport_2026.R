##Racial-classification conjoint ("which person is more Black") from
##Davenport, L. D., Jefferson, H., & Rendleman, H. E. "The Politics of Black Classification:
##Sociopolitical Cues and Racial Perception." Perspectives on Politics (accepted; deposit
##released 2026-06-23; article DOI not known at build time). Deposit author order: Rendleman,
##Jefferson, Davenport; the README lists Davenport (corresponding), Jefferson, Rendleman.
##Replication data: Harvard Dataverse doi:10.7910/DVN/MRXND8, CC0 1.0, no restricted files, no
##terms. File read: replication.csv (Qualtrics export, one row per respondent; the literal string
##"NA" marks missing). README.md, 00_clean_demos.R, 01_clean.R and 02_analysis.R read as text only.
##Usage: Rscript davenport_2026.R <raw dir> <output dir>
##
##Qualtrics Panels online sample, 4 December 2020 - February 2021, quotas for non-Hispanic Black,
##non-Hispanic White and mixed Black-White Americans. Filters as the authors: gc == 1, not a
##preview, started on/after 2020-12-04, passed both attention checks ("Yes", "Green"): 2,397
##respondents. The README's analytic N of 2,385 (935 Black, 962 White, 488 mixed) leaves out 12
##respondents who fall in none of the three race groups; they are kept here (cov_race).
##5 tasks x 2 hypothetical people (Person A/B, C/D, ... I/J): task and profile RECORDED in the
##column names (traits<task>a/b; the "more Black" item per task).
##FOUR FORMS, randomized between respondents and pooled by the authors, so one table:
##  trial_ancestry_shown  yes/no: whether the parents' race attribute was in the profile ("race"
##                        vs "nr" forms); without it attr_parents is the text "(not shown)".
##  trial_skin_tone_row   top/bottom: the "bst" (bottom skin tone) forms list skin tone after
##                        discrimination, just above party; otherwise it is near the top (3rd with
##                        ancestry, 2nd without). Order of the traits string as parsed by the
##                        authors' code; otherwise fixed.
##Attributes (level text from the traits strings, split on ";" and trimmed): attr_parents (Two
##Black parents / One Black parent, one White parent), attr_gender, attr_skin_tone, attr_class,
##attr_neighborhood, attr_spouse, attr_incarceration, attr_discrimination, attr_party.
##No randomization restrictions are documented; level shares look uniform. One respondent has no
##traits string saved for 2 tasks (levels not saved): those 2 tasks are dropped (the authors'
##na.omit drops them too). 23,966 rows.
##Outcomes:
##  choice  which of the two people the respondent selected as more Black ("Person A"/"Person B";
##          wording not in the deposit, the authors label it "Profile Identified as More Black").
##          Forced choice; every kept task answered.
##  rating  how Black the respondent rated each person, 0 = "Not at all" .. 10 = "Very" (answer
##          labels in the file; question wording not in the deposit).
##Not stored: identify_person* (how the respondent thinks each person identifies: Black / Mixed
##race / White), a categorical answer that fits neither choice nor rating.
##Covariates (answer text): cov_age (years; the one value above 120, not a possible age, is set
##to NA), cov_gender (source
##sex, answer text in replication.csv: Female/Male/Non-Binary -> female/male/other), cov_race
##(respondentrace, multiple answers comma-joined), cov_mixed_black_white (1 = said "yes" to the
##mixed-race item), cov_state, cov_income, cov_education, cov_ideology, cov_party_id (source
##partyid, answer text as stored: Democratic Party, Republican Party, None or 'Independent',
##Other (Please specify)), cov_party_lean (follow-up lean, kept).
##Dropped: ResponseId/ResponseID (Qualtrics ids, re-keyed), dates, durations, page timings,
##Status, gc, race_quota, the strength-of-partisanship items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "replication.csv"), colClasses = "character", encoding = "UTF-8")
for (v in names(s)) set(s, which(s[[v]] == "NA"), v, NA_character_)
s <- s[gc == "1" & Status != "Survey Preview" & as.Date(substr(StartDate, 1, 10)) >= as.Date("2020-12-04") &
         grepl("yes", attention_1, ignore.case = TRUE) & grepl("green", attention_2, ignore.case = TRUE)]
stopifnot(nrow(s) == 2397, !anyDuplicated(s$ResponseId))
s[, id := .I]
L <- letters[1:10]
mb <- list(race = c("personabra_moreblack", "personcdrace_morebla", "personefrace_morebla", "personghrace_morebla", "personijrace_morebla"),
           racebst = c("personabracebst_more", "personcdracebst_more", "personefracebst_more", "personghracebst_more", "personijracebst_more"),
           nr = c("personabnr_moreblack", "personcdnr_moreblack", "personefnr_moreblack", "personghnr_moreblack", "personijnr_moreblack"),
           nrbst = c("personabnrbst_more", "personcdnrbst_more", "personefnrbst_more", "personghnrbst_more", "personijnrbst_more"))
s[, form := NA_character_]
for (f in names(mb)) s[!is.na(get(mb[[f]][1])), form := f]
stopifnot(!anyNA(s$form), s[, sum(!is.na(.SD)) == 5, by = id, .SDcols = unlist(mb)][, all(V1)])
cols <- list(race = c("parents", "gender", "skin_tone", "class", "neighborhood", "spouse", "incarceration", "discrimination", "party"),
             racebst = c("parents", "gender", "class", "neighborhood", "spouse", "incarceration", "discrimination", "skin_tone", "party"),
             nr = c("gender", "skin_tone", "class", "neighborhood", "spouse", "incarceration", "discrimination", "party"),
             nrbst = c("gender", "class", "neighborhood", "spouse", "incarceration", "discrimination", "skin_tone", "party"))
setnames(s, "idnetify_personi", "identify_personi")
an <- c("parents", "gender", "skin_tone", "class", "neighborhood", "spouse", "incarceration", "discrimination", "party")
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  lt <- L[2 * (t - 1) + p]
  ans <- s[, fcoalesce(get(mb$race[t]), get(mb$racebst[t]), get(mb$nr[t]), get(mb$nrbst[t]))]
  x <- data.table(id = s$id, task = t, profile = p, form = s$form,
                  choice = as.integer(ans == paste("Person", toupper(L[2 * (t - 1) + 1:2])[p])),
                  rating = as.integer(sub(" = .*", "", s[[paste0("howblack_person", lt)]])),
                  tr = s[[sprintf("traits%d%s", t, c("a", "b")[p])]])
  for (n in an) x[, paste0("attr_", n) := "(not shown)"]
  for (f in names(cols)) { w <- which(x$form == f); parts <- lapply(tstrsplit(x$tr[w], ";", fixed = TRUE), trimws, whitespace = "[\\h\\v]")
    stopifnot(length(parts) == length(cols[[f]]))
    for (k in seq_along(cols[[f]])) set(x, w, paste0("attr_", cols[[f]][k]), parts[[k]]) }
  x[, tr := NULL]
}))))
d[, bad := any(is.na(attr_gender)), .(id, task)]
stopifnot(d[bad == TRUE, .N] == 4)
d <- d[bad == FALSE][, bad := NULL]
stopifnot(!anyNA(d$choice), d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d$rating), d[, all(rating %in% 0:10)],
          d[form %in% c("race", "racebst"), all(attr_parents %in% c("Two Black parents", "One Black parent, one White parent"))],
          d[form %in% c("nr", "nrbst"), all(attr_parents == "(not shown)")], !d[, any(.SD == "" | is.na(.SD)), .SDcols = paste0("attr_", an)],
          d[, all(attr_gender %in% c("Female", "Male"))], d[, all(attr_skin_tone %in% c("Dark-skinned", "Light-skinned"))])
d[, trial_ancestry_shown := fifelse(form %in% c("race", "racebst"), "yes", "no")]
d[, trial_skin_tone_row := fifelse(form %in% c("racebst", "nrbst"), "bottom", "top")][, form := NULL]
stopifnot(all(s$sex %in% c("Female", "Male", "Non-Binary", NA)))
cv <- s[, .(id, cov_age = suppressWarnings(as.integer(age)), cov_gender = unname(c(Female = "female", Male = "male", `Non-Binary` = "other")[sex]), cov_race = respondentrace,
            cov_mixed_black_white = as.integer(!is.na(mixed) & mixed == "yes"), cov_state = state, cov_income = income,
            cov_education = education, cov_ideology = ideology, cov_party_id = partyid, cov_party_lean = partylean)]
stopifnot(cv[cov_age > 120, .N] == 1)
cv[cov_age > 120, cov_age := NA]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating", paste0("attr_", an)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "davenport_2026_black_classification.csv"))
