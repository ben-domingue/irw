##Presidential-candidate conjoint (Chile, Netquest panel wave 2) from
##Argote, P., & Visconti, G. (2025). Causes and consequences of ideological persistence: The case of
##Chile. Latin American Politics and Society, 67, 80-103. https://doi.org/10.1017/lap.2025.10028
##Replication data: Harvard Dataverse doi:10.7910/DVN/KJPMMS, CC0 1.0. File read: wave2_conjoint.dta
##(datafile 12014479, ?format=original, UTF-8). Read as text only: Replication_README-1.docx,
##01_manuscript_figures.R, 02_manuscript_tables.R, 06_appendixC.R, 07_appendixD.R; also the
##article and its Supplementary Appendix (Cambridge sup001.pdf: Table A2, Appendix C, D).
##Not read: wave1, wave2_conjoint_merged, wave2_defiers, panel_long, base_issue (not the experiment,
##or larger copies of it).
##Usage: Rscript argote_2025.R <dir holding wave2_conjoint.dta> <output dir>
##
##3,075 Chilean adults (Netquest online panel, wave 2, November-December 2021; quotas on age, gender,
##region, education). Appendix: "The conjoint experiment was administred in the second wave" (the
##article text says "first wave"; the file and appendix say wave 2). 5 tasks (`set`) of two
##hypothetical presidential candidates (`posicion` 1/2 = position on screen), both RECORDED; 30,750 rows.
##6 attributes, text from the Stata value labels / the authors' a_1..a_6 copies (English short labels
##of the Spanish display; Appendix Table A2 shows fuller English wording, e.g. "Propose new entry
##restrictions"): ideology (Left/Right), gender (Woman/Man), age (40/50/60 -- the article text says
##35/45/55/65, but the data and Table A2 have 40/50/60), feminism (Feminist/Non-Feminist), immigration
##(No Restrictions/New Immigration Restrictions), crime (Harsher Punishment/No Harsher Punishment).
##Article: the six attributes are randomized simultaneously; no restriction stated. trial_design_version
##= `version` (1-20, constant within respondent; the deposit does not say what it indexes).
##Outcome: choice = `choice` ("Opción 1" / "Opción 2" / "Ninguno"; question wording not in the deposit
##or appendix). OPT-OUT: "Ninguno" (neither) in 6,184 of 15,375 tasks; both profiles 0 there (the authors'
##choice_clean2 codes those rows NA and drops them).
##Dropped: codpanelista, key, numericalid (panel ids; id re-keyed to integers in source order), access
##count, start/end times, status/type/consent; free text a51, a55 (open-ended words about Left/Right)
##and the ranked a28/a57 items; the authors' derived flags (choice_*, left/right/center, feminist,
##*_mig, atr1_mean, merge flag m); other attitude items (a1-a6f, a12 excepted) whose wording is not deposited.
##Covariates: cov_gender (sex: Mujer -> female, Hombre -> male; the authors' Table C1 reports
##Female/Male shares from it), cov_age (years), cov_age_group (agerecode as stored, e.g. "25_34"),
##cov_ses (NSE socio-economic group as stored), cov_region, cov_device, cov_left_right (a12 answer text:
##"1 Izquierda" ... "10 Derecha", "No sé/ Ninguna"; the article's 1-10 left-right self-placement),
##cov_duration_sec (duration, whole wave-2 survey in seconds; = 60 x duration_min),
##cov_survey_weight (weight_joint, the census cell post-stratification weight of Appendix C) and
##cov_weight_rake (the raking weight, Appendix C). The main text estimates are unweighted.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "wave2_conjoint.dta")))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
stopifnot(nrow(s) == 30750, uniqueN(s$numericalid) == 3075, s[, .N, numericalid][, all(N == 10)])
s[, id := match(numericalid, unique(numericalid))]
stopifnot(s[, .N, .(id, set, posicion)][, all(N == 1)], s[, uniqueN(choice), .(id, set)][, all(V1 == 1)])
stopifnot(all(s$choice %in% c("Opción 1", "Opción 2", "Ninguno")), all(s$sex %in% c("Mujer", "Hombre")))
stopifnot(all(lab(s$atr1) == s$a_1), all(lab(s$atr4) == s$a_4), all(lab(s$atr3) == s$a_3))
d <- s[, .(id, task = as.integer(set), profile = as.integer(posicion),
  choice = as.integer(choice == paste("Opción", posicion)),
  attr_ideology = lab(atr1), attr_gender = lab(atr2), attr_age = lab(atr3), attr_feminism = lab(atr4),
  attr_immigration = lab(atr5), attr_crime = lab(atr6),
  cov_gender = c(Mujer = "female", Hombre = "male")[sex], cov_age = as.integer(age), cov_age_group = agerecode,
  cov_ses = nse, cov_region = region, cov_device = device, cov_left_right = fifelse(a12 == "", NA_character_, a12),
  cov_duration_sec = as.numeric(duration), cov_survey_weight = weight_joint, cov_weight_rake = weight_rake,
  trial_design_version = as.integer(version))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, sum(choice), .(id, task)][, all(V1 <= 1)])
stopifnot(d[, sum(choice), .(id, task)][, sum(V1 == 0)] == 6184, d[, uniqueN(trial_design_version), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "argote_2025_ideology_candidates_chile.csv"))
