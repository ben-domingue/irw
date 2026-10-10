##Immigrant-profile conjoint (Greece) from
##Kyrkopoulou, E., & Sambanis, N. (2026). O Xenos: Racial difference, colorism, and attitudes toward
##immigrants in Greece. Political Behavior. https://doi.org/10.1007/s11109-026-10204-0
##Replication data: Harvard Dataverse doi:10.7910/DVN/CPDFPQ, CC0 1.0, no restricted files.
##Files read: conjointGR_ICL.xlsx (Qualtrics export, one row per respondent, with the conjoint
##loop fields F<task><position> = attribute name and F<task><profile><position> = level shown) and
##conjointGR_ICL.dta (Dataverse "original format"; same respondents in the same order, used for the
##survey weight weight_new and the authors' AGE and NUTS1_string). Read as text, not run:
##01_conjoint_profiledata.R, 02_conjoint_prep.do, 03_Study1.do, 06_Study2.R. The article was not
##accessible; design facts below come from the deposit only.
##Usage: Rscript kyrkopoulou_2026.R <raw dir> <output dir>
##
##This is the paper's Study 2: 2,007 Greek adults (Cint panel per the CintID field, Qualtrics, UserLanguage = EL for all), 5 tasks of
##two hypothetical immigrants ("Individual A" / "Individual B"), 8 attributes, forced choice (cj_y<t>,
##no missing, no opt-out); task and profile are RECORDED in the loop field names. The question wording
##is not in the deposit (Qualtrics labels 1_Q2 ... 9_Q2 only).
##Attributes, in the fixed order of the F<t>1..F<t>8 fields (identical for every respondent and task):
##gender, skin, ethnicity, work, language, religion, marital, residence. Six are stored in the Greek
##text the export records (the authors' 02_conjoint_prep.do translates them: ethnicity = region of
##origin Αφρική / Μέση Ανατολή / Νότια Ασία = Africa / Middle East / South Asia; work Γιατρός doctor,
##Προγραμματιστής υπολογιστών computer programmer, Νοσηλευτική φροντίδα/ καθαριότητα home health
##aide/cleaning, Γεωργία/ κτηνοτροφία agriculture/farming, Σερβιτόρα/Σερβιτόρος waiter; language
##Καθόλου ελληνικά & πολύ λίγα αγγλικά no Greek & very basic English, Μέτρια ελληνικά & καλά αγγλικά
##basic Greek & good English, Πολύ καλά ελληνικά & αγγλικά very good Greek & English; religion
##Μουσουλμάνα/Μουσουλμάνος Muslim, Χριστιανή/Χριστιανός Christian; marital Άγαμη/Άγαμος single,
##Παντρεμένη/Παντρεμένος, χωρίς παιδιά married without kids, ..., 2 παιδιά married with 2 kids;
##residence Στη χώρα της/του in home country, Στην Ελλάδα, χωρίς άδεια in Greece without a permit).
##The Greek words agree in grammatical gender with the profile's gender, so the feminine and masculine
##forms are separate stored levels (the authors pool them). One trailing space is trimmed.
##attr_gender (Female/Male) and attr_skin (Darker/Lighter) are stored in English in the export while
##every displayed text level is Greek, and each profile has a photo (conjoint1choice<t>_pictureLink<p>,
##Qualtrics image URLs, dropped): gender and skin tone were most likely conveyed by the photograph,
##whose authors' coding these are (INFERRED from the deposit, not documented; Ben to confirm). The
##export also has a profile nationality (Cameroonian, Nigerian / Egyptian, Syrian / Indian, Pakistani,
##nested in region) that is NOT among the eight loop fields and is not used in the authors' analysis;
##it is dropped because nothing shows it was displayed.
##Restrictions OBSERVED (none documented): "Πολύ καλά ελληνικά & αγγλικά" (very good Greek & English)
##never occurs with "in home country" (only with "in Greece without a permit"); apart from that, the
##only never-seen pairs are the grammatical-gender agreement between gender and the Greek forms.
##Level weights OBSERVED unequal: language "very good" 16.5% vs 42% and 41.5% for the other two
##(consistent with the restriction); residence 50/50 pooled over the two gendered forms; the other
##attributes about equal (pooled over gendered forms).
##Covariates: cov_gender (sex_respondent Female/Male), cov_birth_year (yearborn), cov_age (AGE in the
##.dta, the authors' age variable), cov_education (answer text; "Prefer not to answer" -> NA),
##cov_vote_choice (partychoice, vote intention text, not party ID), cov_religion (relig_respondent),
##cov_parents_greek, cov_region (NUTS1_string), cov_income (income_1 text), cov_egalitarianism,
##cov_security, cov_rulesmatter (agree/disagree text), cov_immatwork, cov_duration_sec (Qualtrics
##Duration (in seconds), whole survey), cov_survey_weight (weight_new: the deposit's raking weight on
##gender, age group and NUTS1, 3 respondents NA). The Study 2 analysis uses weight_cj, recomputed in
##02_conjoint_prep.do with the same targets and not deposited, and drops the 3 respondents with no
##weight; all 2,007 are kept here.
##Dropped: ResponseId (re-keyed 1..2007 in file order), CintID (panel id), Qualtrics metadata, free-text
##fields (gender_6_TEXT, partychoice_22_TEXT, immemploy_1_TEXT), prefecture, picture links and IDs,
##attention-check answers, the other experiments in the file (Study 1 photo thermometer
##thermometerchoice*, therm_y*; policy questions bilateral_pref/permit_pref/policy_choice; Sniderman
##items), derived dummies.
##Study 1 (5 photos per respondent rated 0-100, nationality x skin tone x gender) is NOT built: the
##deposit has no question wording and does not show whether nationality or the name was displayed.
##Spot check (printed): share chosen by attr_skin and by pooled religion.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readxl::read_excel(file.path(raw, "conjointGR_ICL.xlsx")))
y <- haven::read_dta(file.path(raw, "conjointGR_ICL.dta"))
stopifnot(nrow(x) == 2007, all(x$ResponseId == as.character(y$ResponseId)), !anyDuplicated(x$ResponseId))
x[, rid := .I]
nm <- unique(unlist(x[, paste0("F1", 1:8), with = FALSE]))
for (t in 1:5) stopifnot(identical(unique(unlist(x[, paste0("F", t, 1:8), with = FALSE])), nm),
                         all(sapply(1:8, function(k) uniqueN(x[[paste0("F", t, k)]]) == 1)))
stopifnot(identical(nm, c("gender", "skin", "ethnicity", "work", "language", "religion", "marital", "residence")))
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  r <- data.table(id = x$rid, task = t, profile = p,
                  choice = as.integer(x[[paste0("cj_y", t)]] == c("Individual A", "Individual B")[p]))
  for (k in 1:8) r[, paste0("attr_", nm[k]) := trimws(x[[paste0("F", t, p, k)]])]
  r
}))))
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)])
cv <- data.table(id = x$rid,
  cov_gender = c(Female = "female", Male = "male")[x$sex_respondent],
  cov_birth_year = as.integer(x$yearborn), cov_age = as.integer(y$AGE),
  cov_education = fifelse(x$education == "Prefer not to answer", NA_character_, x$education),
  cov_vote_choice = x$partychoice, cov_religion = x$relig_respondent, cov_parents_greek = x$parentsgreek,
  cov_region = as.character(y$NUTS1_string), cov_income = x$income_1, cov_egalitarianism = x$egalitarianism,
  cov_security = x$security, cov_rulesmatter = x$rulesmatter, cov_immatwork = x$immatwork,
  cov_duration_sec = as.integer(x$Durationinseconds), cov_survey_weight = as.numeric(y$weight_new))
stopifnot(!anyNA(cv$cov_gender))
cv[cov_region == "", cov_region := NA]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kyrkopoulou_2026_immigrants_greece.csv"))
print(d[, .(share = mean(choice)), attr_skin])
print(d[, .(share = mean(choice)), .(muslim = attr_religion %like% "^Μουσουλμ")])
