##Political-violence sanctioning conjoint (single-profile experiment, US) from
##Phillips, J. B., Munis, B. K., Huffman, N., Memovic, A., & Ford, J. (2025). When push comes to
##shove: How Americans excuse and condemn political violence. Political Behavior, 47, 1711-1733.
##https://doi.org/10.1007/s11109-025-10009-7
##Replication data: Harvard Dataverse doi:10.7910/DVN/1FVL19, CC0 1.0, no restricted files.
##File read: Single-Profile Experiment.tab ("original format" download, saved as single.csv; 17,010
##rows, one per respondent x profile, level text as displayed). Read as text: Single-Profile PB
##Replication.R, Double Profile PB Replication.R, the article (Springer HTML) and the OSF
##preregistration osf.io/qw9ev (attribute list, task wording, outcome wording).
##Usage: Rscript phillips_2025.R <raw dir> <output dir>
##
##3,402 US adults (Dynata, quotas on age, gender, state, race, party; summer 2023), 5 tasks of one
##perpetrator profile each, as in the article (3,402 / 17,010). Task text (prereg): "Imagine that
##the individual below was arrested during a political demonstration near the [respondent's
##state] state capitol building that turned violent between protesters and counter-protesters.
##This individual is facing prosecution. Please study the information carefully and let us know,
##if convicted, what do you think would be an appropriate punishment?"
##The file has NO task column: each respondent has exactly 5 consecutive rows, and task = row order
##within respondent (INFERRED; the file is sorted by respondent and the display order is not
##verifiable). profile = 1 (one profile per task).
##9 attributes, text as stored (leading/trailing blanks trimmed): act (12 acts, 4 targets x 3
##severities), age, children, gender, race, marital status, occupation (12), party, residence.
##attr_residence is the authors' group label (Urban / Rural / Out of State); the prereg says
##respondents saw "Lives in {respondent's state}'s Capital City", "From a rural {respondent's
##state} community", "Not from {respondent's state}" with the state piped in, which was not saved.
##Randomization: independent, levels equally likely, EXCEPT perpetrator race, drawn at roughly
##Census rates with a minority oversample (article: 49.6% White, 13.0% Black, 12.6% Asian, 12.5%
##Hispanic, 12.3% Middle Eastern; prereg q7). The authors' derived columns (target, severity,
##occupation group, race x gender, congruency, ingroup flags, scales, categories) are dropped.
##Outcomes (prereg q15; stored as the answer's position in the option list):
##  rating: "Assume that this individual definitely did what they are accused of above. What
##    punishment, if any, do you think they should receive?" 1 A warning, 2 Community service but
##    no jail time, 3 1-3 days in jail, 4 4-30 days, 5 2-3 months, 6 4-6 months, 7 7 months to 1
##    year, 8 2-5 years, 9 6-10 years, 10 11-15 years, 11 16-20 years, 12 20-30 years, 13 More than
##    30 years in jail. Higher = harsher. (The deposit's choice_num is (rating - 1) / 12.)
##  rating_good_cause: "How likely do you think it is that this individual was protesting for a
##    good cause?" 1 Extremely unlikely, 2 Somewhat unlikely, 3 Neither likely nor unlikely, 4
##    Somewhat likely, 5 Extremely likely (answer text in the file).
##Covariates, answer text as stored (empty -> NA): cov_state, cov_ideology, cov_age_group (Age),
##cov_party_id (Party3: Democrat / Republican / Independent, leaners included per prereg),
##cov_party7_code (Party7, 1-7, no labels deposited, direction not documented), cov_party_lean (lean), cov_gender (Female/Male -> female/male),
##cov_native, cov_interest, cov_income ("Prefer not to say" -> NA), cov_education, cov_employment,
##cov_race (Race.Ethnicity), cov_hispanic, cov_place_importance, cov_place_identity,
##cov_place_childhood, cov_same_community, cov_urban_rural (geo_id_current), and the four 0-100
##feeling thermometers (Proud Boys, white nationalists, BLM, Antifa).
##ResponseId (Qualtrics) is replaced by a 1..N id.
##NOT BUILT: the double-profile experiment (Double-Profile Experiment.csv, 2,763 respondents x 7
##pairs, "which of two perpetrators would you let walk free"): rows within respondent are not in
##pair order (consecutive rows hold 0 or 2 choices in 46% of would-be pairs; every respondent has
##exactly 7 chosen and 7 unchosen rows), so tasks cannot be rebuilt. It also holds free-text
##explanations (verbatim).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "single.csv"), na.strings = c("", "NA"))
stopifnot(nrow(s) == 17010, s[, .N, ResponseId][, all(N == 5)], uniqueN(s$ResponseId) == 3402)
s[, task := seq_len(.N), ResponseId]
sent <- c("A warning", "Community service but no jail time", "1-3 days in jail", "4-30 days in jail",
          "2-3 months in jail", "4-6 months in jail", "7 months to 1 year in jail", "2-5 years in jail",
          "6-10 years in jail", "11-15 years in jail", "16-20 years in jail", "20-30 years in jail",
          "More than 30 years in jail")
mot <- c("Extremely unlikely", "Somewhat unlikely", "Neither likely nor unlikely", "Somewhat likely", "Extremely likely")
stopifnot(all(s$choice %in% sent), all(s$motivation %in% mot))
rt <- match(s$choice, sent)
stopifnot(all.equal((rt - 1) / 12, s$choice_num, tolerance = 1e-6))
s[, id := match(ResponseId, unique(ResponseId))]
tr <- function(x) trimws(as.character(x))
d <- s[, .(id, task, profile = 1L, rating = rt, rating_good_cause = match(motivation, mot),
           attr_act = tr(profile_act), attr_age = tr(profile_age), attr_children = tr(profile_children),
           attr_gender = tr(profile_gender), attr_race = tr(profile_race), attr_marital = tr(profile_marital),
           attr_occupation = tr(profile_occupation), attr_party = tr(profile_party),
           attr_residence = tr(profile_residence_group),
           cov_state = GEO.State..US., cov_ideology = ideology, cov_age_group = Age, cov_party_id = Party3,
           cov_party7_code = as.integer(Party7), cov_party_lean = lean,
           cov_gender = c(Female = "female", Male = "male")[Gender], cov_native = native, cov_interest = interest,
           cov_income = fifelse(income == "Prefer not to say", NA_character_, income), cov_education = education,
           cov_employment = employment, cov_race = Race.Ethnicity, cov_hispanic = hispanic,
           cov_place_importance = placeimportance, cov_place_identity = placeidentity, cov_place_childhood = placekid,
           cov_same_community = same_community, cov_urban_rural = geo_id_current,
           cov_ft_proud_boys = proud_boys_ft, cov_ft_white_nationalists = white_nat_ft, cov_ft_blm = blm_ft,
           cov_ft_antifa = antifa_ft)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, uniqueN(attr_act)] == 12, d[, uniqueN(attr_occupation)] == 12)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "phillips_2025_political_violence.csv"))
