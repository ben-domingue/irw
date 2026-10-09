##Public-hiring candidate conjoint (Germany), three samples, from
##Jankowski, M., Prokop, C., & Tepe, M. (2020). Representative bureaucracy and public hiring
##preferences: Evidence from a conjoint experiment among German municipal civil servants and
##private sector employees. Journal of Public Administration Research and Theory, 30(4), 596-618.
##https://doi.org/10.1093/jopart/muaa012
##Replication data: Harvard Dataverse doi:10.7910/DVN/XZJRA2, CC0 1.0, no restricted files.
##Files read: JPART_final.rds (the authors' long analysis file, all three samples, one row per
##respondent x task x profile, task/profile recorded, attribute levels as the authors' English
##factor labels) and qualtrics_raw_data_text.rds (the raw Qualtrics text export of the municipal
##civil-servant survey only: German displayed level text, attribute row order, covariate text).
##The authors' replication_jankowski_prokop_tepe_jpart.R was read as text. No codebook ships.
##Usage: Rscript jankowski_2020.R <raw dir> <output dir>
##
##Each respondent saw 6 pairs of job applicants ("Bewerber/in A", "Bewerber/in B") with 9
##attributes and chose one: "Wenn Sie sich zwischen den beiden Bewerber/innen entscheiden müssten,
##wen würden Sie in den öffentlichen Dienst einstellen?" Forced choice, no opt-out (exactly one
##chosen per task in every sample).
##THREE TABLES, one per sample: the samples are separate populations and fieldings, and the
##authors analyse them side by side (cregg `by = ~ Sample`), never pooled:
##  jankowski_2020_hiring_civil_servants: municipal public administration employees invited by
##    email (sample "Pub Adm"), 234 respondents (the authors' analysis set; the raw export holds
##    335 records, of which 7 of the 234 did not finish the survey but completed all 6 tasks).
##  jankowski_2020_hiring_students: public administration students ("NSI"), 401 respondents.
##  jankowski_2020_hiring_private: private sector employees (respondi online panel, sample label
##    "respondi: Public", the authors' "Priv. Sec. Employees"), 639 respondents.
##Attribute text. Civil-servant table: the German text displayed (raw export F-<task>-<profile>-<k>
##fields; the attribute shown in row k is F-<task>-<k>); each German level maps to exactly one of
##the authors' English labels on the same rows (checked below), and the choice agrees with the
##authors' `wahl`. Attribute ROW ORDER was randomized once per respondent (identical across that
##respondent's 6 tasks for all 234) and is kept as attrpos_* (1 = top). The raw text and order exist
##only for the civil servants, so the students and private-sector tables carry the authors' English
##labels (their typo "General certifcate" kept; their plot-ordering prefixes "x0 - ", "x1 - ",
##"x2 - " before "None" removed) and no attrpos_ columns. The questionnaire text for those two
##samples is not deposited; the covariate answer text they share with the civil-servant export is
##identical, which suggests the same instrument.
##Level weights OBSERVED in all samples: family origin Germany ~50% of profiles, Turkey/Poland/
##France ~1/6 each; physical disability "yes" ~20%; the other attributes near uniform. No source in
##the deposit documents weights or restrictions; no level pair is missing.
##Covariates (answer text as stored; refusal/blank -> NA). All samples: cov_gender (all_sex
##"Weiblich" -> female, "Männlich" -> male), cov_education (all_edu, "Welchen allgemeinbildenden
##Schulabschluss haben Sie?"), cov_migration_background (all_migr Ja/Nein), cov_leftright (all_
##leftright_1, 0 = ganz links .. 10 = ganz rechts), cov_representation_1..3 (all_repst_*),
##cov_psm_1..5 (all_psm_*, public service motivation items), cov_perceived_discrimination (perc,
##"Bei Bewerbungen im öffentlichen Dienst werden Menschen mit Migrationshintergrund benachteiligt."),
##cov_integration_measures (intgr). Students/private: cov_age (all_age, years) and cov_area
##(all_area). Civil servants (from the raw export, since the authors' file holds bare codes for this
##sample): cov_age_group (all_age bands), cov_authority_type (all_kind), cov_authority_size
##(all_size), cov_hr_responsibility (all_hrex), cov_anonymous_application_1..6 (pub_anony_*), and
##cov_duration_sec (Qualtrics "Duration (in seconds)", the whole survey).
##Dropped: Qualtrics ResponseId (re-keyed to integers within each table); the raw export's e-mail
##field all_losmail_1 (respondents' e-mail addresses), browser metadata, click timings; pub_base_1
##and pub_troff_1 (sliders whose scale ends are not recoverable); the authors' Sample factor.
##N: 1,274 respondents in the authors' file (234 + 401 + 639); the article text was not read (the 401
##students match the authors' ECPR abstract "Who Wants a Representative Bureaucracy?"). Spot check:
##share chosen by family origin, private sector: Germany 0.56, Turkey 0.41 (civil servants 0.52 / 0.48).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "JPART_final.rds")))
q <- as.data.table(readRDS(file.path(raw, "qualtrics_raw_data_text.rds")))[-(1:2)]
stopifnot(s[, .N, respondent][, all(N == 12)], s[, sum(wahl), .(respondent, task)][, all(V1 == 1)])
en <- c(note = "grade", schulabschluss = "school", berufserfahrung = "experience", englisch = "english",
        engagement = "volunteering", geschlecht = "gender", behinderung = "disability", alter = "age",
        herkunftsland = "origin")
de <- c("Abschlussnote Ausbildung (Schulnoten 1 bis 6)" = "grade", "Höchster Schulabschluss" = "school",
        "Einschlägige Berufserfahrung" = "experience", "Englischkenntnisse" = "english",
        "Gesellschaftliches Engagement" = "volunteering", "Geschlecht" = "gender",
        "Körperliche Behinderung" = "disability", "Alter" = "age", "(Familiäres) Herkunftsland" = "origin")
blank <- function(x) { x <- trimws(as.character(x)); x[x == ""] <- NA; x }
sex <- function(x) unname(c("Weiblich" = "female", "Männlich" = "male")[blank(x)])
likert <- function(d, src, pre) for (i in seq_along(src)) d[, paste0(pre, i) := blank(src[[i]])]

## ---- civil servants: German text + attribute order from the raw export ----
pub <- s[sample == "Pub Adm"]
q <- q[ResponseId %in% pub$respondent]
stopifnot(nrow(q) == 234, uniqueN(pub$respondent) == 234)
L <- rbindlist(lapply(1:6, function(t) rbindlist(lapply(1:2, function(p) rbindlist(lapply(1:9, function(k)
  data.table(respondent = q$ResponseId, task = t, profile = p, pos = k,
             attr = de[q[[paste0("F-", t, "-", k)]]], lev = q[[paste0("F-", t, "-", p, "-", k)]])))))))
stopifnot(!anyNA(L$attr), !anyNA(L$lev), all(L$lev != ""))
# order fixed within respondent across tasks
stopifnot(L[profile == 1][order(respondent, task, pos)][, .(o = paste(attr, collapse = "|")), .(respondent, task)][, uniqueN(o), respondent][, all(V1 == 1)])
W <- dcast(L, respondent + task + profile ~ attr, value.var = "lev")
P <- dcast(L[profile == 1], respondent + task ~ attr, value.var = "pos")
setnames(W, unname(en), paste0("attr_", unname(en)))
setnames(P, unname(en), paste0("attrpos_", unname(en)))
m <- merge(pub, W, by = c("respondent", "task", "profile"))
stopifnot(nrow(m) == nrow(pub))
# every German level maps to one English label and back
for (k in names(en)) stopifnot(m[, uniqueN(get(k)), get(paste0("attr_", en[[k]]))][, all(V1 == 1)],
                               m[, uniqueN(get(paste0("attr_", en[[k]]))), get(k)][, all(V1 == 1)])
qc <- data.table(respondent = q$ResponseId, chosen = c("Bewerber/in A" = 1L, "Bewerber/in B" = 2L)[q$pub_cj1f])
stopifnot(all(m[task == 1 & wahl == 1][qc, on = "respondent"][, profile == chosen]))
m <- merge(m, P, by = c("respondent", "task"))
setkey(q, ResponseId)
qq <- q[m$respondent]
d <- m[, c(list(respondent = respondent, task = as.integer(task), profile = as.integer(profile), choice = as.integer(wahl)),
           .SD), .SDcols = c(paste0("attr_", unname(en)), paste0("attrpos_", unname(en)))]
d[, `:=`(cov_gender = sex(qq$all_sex), cov_age_group = blank(qq$all_age), cov_education = blank(qq$all_edu),
         cov_migration_background = blank(qq$all_migr), cov_leftright = as.integer(blank(qq$all_leftright_1)),
         cov_perceived_discrimination = blank(qq$pub_perc), cov_integration_measures = blank(qq$pub_intgr),
         cov_authority_type = blank(qq$all_kind), cov_authority_size = blank(qq$all_size),
         cov_hr_responsibility = blank(qq$all_hrex), cov_duration_sec = as.integer(qq$`Duration (in seconds)`))]
likert(d, qq[, paste0("all_repst_", 1:3), with = FALSE], "cov_representation_")
likert(d, qq[, paste0("all_psm_", 1:5), with = FALSE], "cov_psm_")
likert(d, qq[, paste0("pub_anony_", 1:6), with = FALSE], "cov_anonymous_application_")
stopifnot(all(d$cov_gender %in% c("female", "male", NA)))
tabs <- list(jankowski_2020_hiring_civil_servants = d)

## ---- students and private sector: the authors' English labels ----
smps <- c(students = "NSI", private = "respondi: Public")
for (smp in names(smps)) {
  x <- s[sample == smps[[smp]]]
  d <- x[, .(respondent, task = as.integer(task), profile = as.integer(profile), choice = as.integer(wahl))]
  for (k in names(en)) d[, paste0("attr_", en[[k]]) := sub("^x[0-9] - ", "", as.character(x[[k]]))]
  stopifnot(all(x$all_sex %in% c("Weiblich", "Männlich")))
  d[, `:=`(cov_gender = sex(x$all_sex), cov_age = as.integer(x$all_age), cov_education = blank(x$all_edu),
           cov_migration_background = blank(x$all_migr), cov_leftright = as.integer(blank(x$all_leftright_1)),
           cov_perceived_discrimination = blank(x$perc), cov_integration_measures = blank(x$intgr),
           cov_area = blank(x$all_area))]
  likert(d, x[, paste0("all_repst_", 1:3), with = FALSE], "cov_representation_")
  likert(d, x[, paste0("all_psm_", 1:5), with = FALSE], "cov_psm_")
  tabs[[paste0("jankowski_2020_hiring_", smp)]] <- d
}
stopifnot(sapply(tabs, function(d) uniqueN(d$respondent)) == c(234, 401, 639), all(sapply(tabs, nrow) == c(234, 401, 639) * 12))
for (nm in names(tabs)) {
  d <- tabs[[nm]]
  ids <- sort(unique(d$respondent)); d[, id := match(respondent, ids)][, respondent := NULL]
  setcolorder(d, c("id", "task", "profile", "choice"))
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(nm, ".csv")))
}
