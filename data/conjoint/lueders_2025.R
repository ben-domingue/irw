##Destination-city conjoint ("pull experiment") among Mexican-born immigrants in the US from
##Lueders, H. (2025). Local immigration policies shape immigrants' relocation preferences
##regardless of immigration status. Political Behavior.
##https://doi.org/10.1007/s11109-025-10080-0
##Replication data: Harvard Dataverse doi:10.7910/DVN/CFPFU7, CC0 1.0, no restricted files, no
##terms. File read: LocalImmigrationPolicies_replicationdata.Rdata (objects d.full.conjoint and
##d.full). Level text = the factor labels in the deposit; outcome meanings from the authors'
##LocalImmigrationPolicies_replicationcode.R (read as text). The article (closed access) and
##the survey instrument were not available, so question wording is paraphrased.
##Usage: Rscript lueders_2025.R <raw dir> <output dir>
##
##1,165 respondents (online survey of Mexican-born immigrants in the US, taken in English or
##Spanish: cov_survey_language) did the pull experiment; this is the authors' d.full.conjoint,
##used for their main Figure 5 (d.conjoint, 1,112 complete responses, is a subset). The
##deposit's other experiment (the "push" experiment, a single-factor vignette on moving away)
##is not a conjoint and is not included.
##Each respondent saw 4 pairs of cities (deposit E2_city A-H; pairs A/B, C/D, E/F, G/H = tasks
##1-4, the first letter = profile 1; the authors' first-pair robustness check uses cities A and
##B; verified: exactly one city chosen in every answered pair). Seven attributes, row order
##randomized once per respondent (E2_*_order, constant within respondent -> attrpos_):
##jobs (No jobs / Very few jobs / Some jobs / Many jobs), rent ($800 / $1,300 / $1,800 /
##$2,300), network (Nobody (0) / A few people (1-4) / Some people (5-9) / A lot of people
##(10+)), share Mexican (0% / 10% / 20% / 30%), deportation (Deport more immigrants / No
##protections from deportation / Deportation only after serious crime / All immigrants are
##protected from deportation), healthcare access for immigrants (Never / Only in emergencies /
##Only for children and pregnant women / Always), type of community (Rural area / Small town /
##Suburban neighborhood / Neighborhood in a large city). The authors' figure labels word some
##levels differently (e.g. "Trying to deport unauthorized immigrants"); the stored text is the
##deposit's factor labels, and the Spanish version's text is not deposited.
##Outcomes:
##  choice = E2_choice, the city the respondent would rather move to (paraphrase), forced, no
##    opt-out; 67 pairs have no choice (NA on both rows).
##  rating_<x>: ten 0/1 judgements asked per city, both cities can get 1 (so ratings, not
##    choices). Respondents were randomized to one of two versions (cov_question_version, the
##    deposit's E2_comparison): version A asked econ_secure ("Be economically secure"), safe
##    ("Be safe"), gov_liberal ("Gov't is liberal"), help ("Have many people who can help"),
##    quality_life ("High quality of life"); version B asked discrimination ("Fear
##    discrimination"), gov_protects ("Gov't protects immigrants"), opportunities ("Have many
##    opportunities"), alone ("Feel alone"), trust_police ("Trust the police"). Labels are the
##    authors' figure titles; NA = not asked. 1 = respondent expects this in that city.
##Covariates (deposit factor labels): cov_gender (demo_gender Male/Female), cov_age
##(demo_age), cov_age_group, cov_education (demo_education), cov_status (cit_citizenUS_alt:
##natural-born US citizen / naturalized US citizen / lawful permanent resident / likely
##unauthorized immigrant, the authors' classification), cov_citizen_mexico, cov_years_us,
##cov_age_move_us, cov_worries_deportation, cov_agree_deportation, cov_agree_immistatus,
##cov_trust_ice, cov_family_unauthorized, cov_know_deported, cov_income_quintile, cov_hh_adults,
##cov_state (state from the zip code), cov_survey_language (english/spanish),
##cov_experiment_order (push first / pull first), cov_attention_pass (attentioncheck),
##cov_duration_sec (survey duration), cov_survey_weight (the deposit's weight; NA for 238 of
##the 1,165, as in the deposit). Dropped: Qualtrics ResponseId (re-keyed), zip-code latitude/
##longitude (PII), usa_state_id, state-government party dummies, recoded/dichotomized copies,
##E2_choice_consistent (authors' flag), push-experiment variables.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "LocalImmigrationPolicies_replicationdata.Rdata"), envir = e)
x <- as.data.table(e$d.full.conjoint); f <- as.data.table(e$d.full)
stopifnot(x[, .N, ResponseId][, all(N == 8)], x[, all(sort(E2_city) == LETTERS[1:8]), ResponseId]$V1)
x[, task := match(E2_city, LETTERS[1:8]) %/% 2L + match(E2_city, LETTERS[1:8]) %% 2L]
x[, profile := 2L - match(E2_city, LETTERS[1:8]) %% 2L]
x[, rid := match(ResponseId, f$ResponseId)]
stopifnot(!is.na(x$rid))
d <- x[, .(rid, task, profile, choice = as.integer(E2_choice))]
stopifnot(d[, .(s = sum(choice), n = sum(is.na(choice))), .(rid, task)][, all((n == 0 & s == 1) | n == 2)])
rt <- c(econsecure = "econ_secure", besafe = "safe", govliberal = "gov_liberal", help = "help", quallife = "quality_life",
        discrimination = "discrimination", govprotect = "gov_protects", opportunities = "opportunities", alone = "alone",
        trustpolice = "trust_police")
for (v in names(rt)) { y <- x[[paste0("E2_", v)]]; stopifnot(all(y %in% c(0, 1, NA))); d[, paste0("rating_", rt[[v]]) := as.integer(y)] }
at <- c(jobs = "jobs", rent = "rent", netw = "network", immi = "share_mexican", deport = "deportation", health = "healthcare",
        type = "community")
for (v in names(at)) {
  y <- as.character(x[[paste0("E2_", v)]]); stopifnot(!is.na(y))
  d[, paste0("attr_", at[[v]]) := y][, paste0("attrpos_", at[[v]]) := as.integer(x[[paste0("E2_", v, "_order")]])]
}
stopifnot(d[, uniqueN(attrpos_jobs), rid][, all(V1 == 1)])
fc <- function(v) as.character(f[[v]])[d$rid]
d[, `:=`(cov_question_version = f$E2_comparison[rid],
         cov_gender = c(Male = "male", Female = "female")[fc("demo_gender")], cov_age = as.integer(f$demo_age[rid]),
         cov_age_group = fc("demo_agegroupALT"), cov_education = fc("demo_education"), cov_status = fc("cit_citizenUS_alt"),
         cov_citizen_mexico = f$cit_citizenMexico[rid], cov_years_us = f$cit_yearsUS[rid], cov_age_move_us = f$cit_age_moveUS[rid],
         cov_worries_deportation = fc("cit_worries_deportation"), cov_agree_deportation = fc("bl_agree_deportation"),
         cov_agree_immistatus = fc("bl_agree_immistatus"), cov_trust_ice = fc("bl_trust_ICE"),
         cov_family_unauthorized = f$cit_family_unauthorized[rid], cov_know_deported = f$cit_know_deported[rid],
         cov_income_quintile = fc("demo_income_quintile"), cov_hh_adults = f$demo_nHH_adults[rid], cov_state = f$demo_zipcode_state[rid],
         cov_survey_language = fifelse(f$language_spanish[rid] == 1, "spanish", "english"),
         cov_experiment_order = fc("first"), cov_attention_pass = as.integer(f$attentioncheck[rid]),
         cov_duration_sec = f$duration[rid], cov_survey_weight = f$weight[rid])]
stopifnot(all(f$language_spanish + f$language_english == 1), all(d$cov_question_version %in% c("A", "B")))
# version A/B asks disjoint rating sets
stopifnot(d[cov_question_version == "B", all(is.na(rating_econ_secure))], d[cov_question_version == "A", all(is.na(rating_discrimination))])
rc <- grep("^(choice|rating_)", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..rc])) > 0]
d[, id := rid][, rid := NULL]
setcolorder(d, c("id", "task", "profile", rc))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lueders_2025_relocation.csv"))
