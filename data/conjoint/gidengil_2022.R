##Candidate-choice conjoint on executive aggrandizement during COVID-19 (Canada, May 2020) from
##Gidengil, E., Stolle, D., & Bergeron-Boutin, O. (2022). COVID-19 and support for executive
##aggrandizement. Canadian Journal of Political Science, 55(2), 342-372.
##https://doi.org/10.1017/S0008423922000117 (open access; design facts below from its "Data and
##Methods" section).
##Replication data: Harvard Dataverse doi:10.7910/DVN/7TMQQN, CC0 1.0, no restricted files.
##File read: can_covid_raw.RData (object survey_raw, the Qualtrics export; loaded into a new
##environment). The authors' data_manipulation.Rmd was read as text for the column layout
##(traits<t><a|b> = "|"-joined level text of candidate A/B in task t; order1-3 = which feature
##sat in rows 5-7). can_covid_clean.RData (the authors' filtered, recoded version) is not used.
##Usage: Rscript gidengil_2022.R <dir holding can_covid_raw.RData> <output dir>
##
##Dynata online panel, Canadian provinces outside Quebec, 16-28 May 2020, quotas on education,
##age, sex and region. Respondents saw six profile tables (task 1-6) of two candidates "competing
##for a seat in Parliament" (profile 1 = Candidate A, 2 = Candidate B) and were "asked to select
##their preferred candidate in each pair" (article; exact wording not deposited); forced choice,
##no opt-out. choice = outcome_<arm>_<t> ("Candidate A"/"Candidate B").
##Attributes (level text as displayed, from the traits strings): attr_gender (Male/Female),
##attr_age (37-75), attr_experience, attr_party (Conservative/Liberal/New Democrat), attr_aid
##("Says economic aid to address the COVID-19 crisis should ..."), attr_lockdown ("Says lockdowns
##should ..."), attr_checks, the executive-aggrandizement attribute. Its version was randomized
##across respondents (trial_checks_version): "parliament" ("Says that a prime minister should
##work with / shut down Parliament ...") or "courts" ("... comply with / ignore court decisions
##..."; one instrument string reads "comply with with", kept as displayed). The authors analyse
##the two versions separately; they are one design with one attribute whose text differs by
##arm, so ONE table. Rows 1-4 (age, sex, experience, party) were always first; the order of
##rows 5-7 (aid, lockdown, checks) was randomized per respondent and fixed across the six tables:
##attrpos_aid / attrpos_lockdown / attrpos_checks = 5-7 from order1-3 (the JavaScript 0-based
##feature index 4/5/6 shown in rows 5/6/7, per the authors' Rmd). Levels fully randomized
##(article): restrictions none; level probabilities not stated.
##trial_task_time_sec = time_<arm>_<t> (Qualtrics page time); the article drops tasks under
##5 seconds (2,438 observations) - kept here.
##Respondents: all 2,830 Qualtrics records with at least one conjoint answer (1,417 parliament
##arm, 1,413 courts arm, from which outcome block was answered; every task's checks text matches
##the arm, checked; tasks without an answer omitted, 2,778 respondents answered all six). The article's analysis sample is 2,322 after excluding failed attention checks,
##durations < 300 s or > 3,600 s, straightliners and non-citizens; those flags are kept as
##cov_attention_pass (attn_check "Blue" = 1), cov_duration_sec, cov_canadian_citizen (Yes = 1);
##straightlining is not reproduced.
##Covariates (answer text as exported): cov_birth_year, cov_gender (Female/Male/Other ->
##female/male/other), cov_province, cov_education, cov_party_id (partyid: Liberal, Conservative,
##NDP, Green, Other, None of these), cov_lockdown_preference (covid_lockdowns),
##cov_anxious_think / cov_anxious_activities (Never/Rarely/Sometimes/Often).
##Dropped: ResponseId (re-keyed to integers in export order), Recorded/Start/End dates, consent,
##the other survey items (vignette experiment, worry/support/social/backslide batteries,
##authority, deprivation), and conjoint_recall.
##N check: 2,830 here vs 2,322 in the article (exclusions above). No weight in the deposit.
##Spot check: the article reports 43% (Parliament) / 44% (courts) choosing the norm-violating
##candidate when one candidate violates; with the attention/duration/citizenship filters (2,365
##respondents; no straightliner or 5-second filter) the table gives 44% / 44%.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "can_covid_raw.RData"), envir = e)
s <- as.data.table(e$survey_raw)[-1]               # row 1 is Qualtrics import metadata
s <- s[!is.na(traits1a)]
# arm = which outcome block the respondent answered (outcome_parliament_* or outcome_courts_*)
op <- s[, rowSums(!is.na(.SD)) > 0, .SDcols = patterns("^outcome_parliament_")]
oc <- s[, rowSums(!is.na(.SD)) > 0, .SDcols = patterns("^outcome_courts_")]
stopifnot(!any(op & oc))
s <- s[op | oc][, arm := fifelse(op[op | oc], "parliament", "courts")]
s[, rid := .I]
ord <- s[, .(rid, o1 = as.integer(order1), o2 = as.integer(order2), o3 = as.integer(order3))]
stopifnot(ord[, all(sort(c(o1, o2, o3)) == 4:6), rid][, all(V1)])
pos <- function(f) with(ord, ifelse(o1 == f, 5L, ifelse(o2 == f, 6L, 7L)))
nm <- c("gender", "age", "experience", "party", "aid", "lockdown", "checks")
rows <- list()
for (t in 1:6) for (p in 1:2) {
  tr <- s[[sprintf("traits%d%s", t, c("a", "b")[p])]]
  sp <- strsplit(tr, "|", fixed = TRUE)
  stopifnot(all(lengths(sp[!is.na(tr)]) == 7))
  sp[is.na(tr)] <- list(rep(NA_character_, 7))
  oc <- ifelse(s$arm == "parliament", s[[paste0("outcome_parliament_", t)]], s[[paste0("outcome_courts_", t)]])
  tm <- ifelse(s$arm == "parliament", s[[paste0("time_parliament_", t)]], s[[paste0("time_courts_", t)]])
  stopifnot(all(oc %in% c("Candidate A", "Candidate B", NA)), all(is.na(oc[is.na(tr)])))
  d <- data.table(rid = s$rid, task = t, profile = p, choice = as.integer(oc == c("Candidate A", "Candidate B")[p]))
  for (k in 1:7) set(d, j = paste0("attr_", nm[k]), value = vapply(sp, `[`, "", k))
  d[, `:=`(attrpos_aid = pos(4L), attrpos_lockdown = pos(5L), attrpos_checks = pos(6L),
           trial_checks_version = s$arm, trial_task_time_sec = suppressWarnings(as.numeric(tm)))]
  rows[[length(rows) + 1]] <- d
}
d <- rbindlist(rows)[!is.na(choice)]
# keep only tasks whose checks text matches the respondent's arm (see header)
d[, ok := all(grepl(if (trial_checks_version[1] == "parliament") "Parliament" else "court decisions", attr_checks)), .(rid, task)]
message("tasks dropped (checks text not of the arm): ", d[ok == FALSE, uniqueN(paste(rid, task))],
        "; parliament-arm: ", d[ok == FALSE & trial_checks_version == "parliament", uniqueN(paste(rid, task))])
d <- d[ok == TRUE][, ok := NULL]
stopifnot(d[, sum(choice), .(rid, task)][, all(V1 == 1)], d[, .N, .(rid, task)][, all(N == 2)])
stopifnot(all(d$attr_gender %in% c("Male", "Female")), all(d$attr_party %in% c("Conservative", "Liberal", "New Democrat")),
          d[trial_checks_version == "parliament", all(grepl("Parliament", attr_checks))],
          d[trial_checks_version == "courts", all(grepl("court decisions", attr_checks))])
cov <- s[, .(rid, cov_birth_year = as.integer(birth_year),
             cov_gender = c(Female = "female", Male = "male", Other = "other")[gender],
             cov_province = province, cov_education = education, cov_party_id = partyid,
             cov_lockdown_preference = covid_lockdowns, cov_anxious_think = anxious1_think,
             cov_anxious_activities = anxious2_activities,
             cov_attention_pass = fifelse(is.na(attn_check), NA_integer_, as.integer(attn_check == "Blue")),
             cov_canadian_citizen = fifelse(is.na(can_citizen), NA_integer_, as.integer(can_citizen == "Yes")),
             cov_duration_sec = as.numeric(`Duration (in seconds)`))]
d <- merge(d, cov, by = "rid")
d[, id := match(rid, sort(unique(rid)))][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "gidengil_2022_executive_aggrandizement.csv"))
