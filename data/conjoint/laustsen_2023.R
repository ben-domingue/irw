##Candidate name (sex x ethnicity) vignette experiment (Denmark) from
##Laustsen, L., & Gothreau, C. (2023). Diskriminerer danske vælgere kvindelige og etniske
##minoritetskandidater? Resultater fra et surveyeksperiment. Politica, 55(4), 349-369.
##https://doi.org/10.7146/politica.v55i4.141535 (open access; read)
##Replication data: Harvard Dataverse doi:10.7910/DVN/UD0LDQ, CC0 1.0. File read:
##Politica_Datasæt.dta (original Stata file, value labels). Read as text only: Politica Dofile.do.
##Usage: Rscript laustsen_2023.R <dir holding the .dta> <output dir>
##
##1,116 Danes aged 18-65 (YouGov Danmark, 21 Dec 2021 - 7 Jan 2022, representative on gender, age,
##education, region; article n = 1,116, matches) each read ONE randomly assigned description of a
##fictitious candidate for the coming Folketing election (task = 1, profile = 1). No respondent id in
##the deposit: id = row number. The four versions differ only in the name and the pronoun (article
##pp. 354-355, Danish text there): "Fatima/Susanne/Mohammed/Søren bor med sin familie i en forstad
##til Aarhus. Hun/Han er et engageret menneske, ... er kandidat til det kommende folketingsvalg for
##[Respondentens foretrukne parti] ...". The authors treat the names as a 2 x 2 design, candidate sex
##(Susanne, Fatima = female) x ethnicity (Fatima, Mohammed = ethnic minority); splitgroup value
##labels give the names. Stored as the displayed text: attr_name (the name) and attr_pronoun
##("Hun"/"Han", which follows the name). RESTRICTION: the pronoun is fixed by the name (sex and
##ethnicity are carried by one name, so an ethnicity effect is within these four names).
##The candidate's party was piped from the respondent's vote intention (q1), not randomized, and is
##not stored as an attribute (cov_vote_intention holds q1; what was piped for respondents with no
##party, e.g. "Ved ikke", is not documented).
##Outcome: rating = q7 "Vi vil nu bede dig angive, hvad du synes om [navn] som politiker. Du bedes
##angive dette på en skala fra 0 til 10, hvor 0 indikerer, at du 'synes meget dårligt om
##[kandidaten]', mens 10 indikerer, at du 'synes virkelig godt om [kandidaten]'." 0-10 stored raw
##(the authors rescale to 0-1). Higher = more favourable.
##Covariates (answer text from the value labels unless noted): cov_gender (Kvinde/Mand ->
##female/male), cov_age_group (profile_age2 band), cov_education (profile_education; "Ønsker ikke at
##oplyse" -> NA), cov_region, cov_vote_intention (q1, Folketing vote intention; "Vil ikke svare" ->
##NA), cov_left_right (q2, 0 = most left, 10 = most right), cov_sdo7_1..8 (q3_1-q3_8, SDO-7 items,
##1 = Helt uenig ... 7 = Helt enig, as stored before the authors' reversals), cov_rwa_1..8 (q4_1-q4_8,
##same scale), cov_survey_weight (weight; the authors' models are unweighted), cov_duration_sec
##(tot_time, total interview seconds).
##Dropped: the separate single-factor tattoo-applicant experiment (splitgroup2, q8, q9_*), trust
##items q5/q6, incomes, free-text comments, completion timestamp, page timings, device.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(list.files(raw, pattern = "^Politica_Datas.*\\.dta$", full.names = TRUE)))
stopifnot(nrow(s) == 1116L, !anyNA(s$splitgroup), !anyNA(s$q7))
lab <- function(x, na = character()) { v <- trimws(as.character(as_factor(x, levels = "labels"))); v[v %in% na] <- NA; v }
nm <- lab(s$splitgroup)
stopifnot(all(nm %in% c("Søren", "Susanne", "Mohammed", "Fatima")))
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L, rating = as.integer(s$q7),
                attr_name = nm, attr_pronoun = fifelse(nm %in% c("Susanne", "Fatima"), "Hun", "Han"),
                cov_gender = c(Kvinde = "female", Mand = "male")[lab(s$gender)],
                cov_age_group = lab(s$profile_age2), cov_education = lab(s$profile_education, "Ønsker ikke at oplyse"),
                cov_region = lab(s$region), cov_vote_intention = lab(s$q1, "Vil ikke svare"),
                cov_left_right = as.integer(s$q2))
for (k in 1:8) d[, paste0("cov_sdo7_", k) := as.integer(s[[paste0("q3_", k)]])]
for (k in 1:8) d[, paste0("cov_rwa_", k) := as.integer(s[[paste0("q4_", k)]])]
d[, cov_survey_weight := as.numeric(s$weight)][, cov_duration_sec := as.numeric(s$tot_time)]
stopifnot(!anyNA(d$cov_gender), d$rating %in% 0:10)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "laustsen_2023_candidate_names.csv"))
