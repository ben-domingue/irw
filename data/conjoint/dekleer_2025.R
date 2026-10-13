##Protest-vignette experiment (Netherlands) from
##De Kleer, D., De Vries, C. E., & van Teutem, S. (2025). Public support for pro-environment
##and environment-critical movements. British Journal of Political Science, 55, e161.
##https://doi.org/10.1017/S0007123425101063
##Replication data: Harvard Dataverse doi:10.7910/DVN/SLC5YO, CC0 1.0. Files read from
##dekleeretal2025bjps_replication_package.zip: data/survey/survey_data.csv and
##data/survey/survey_data_codebook.xls (variable descriptions, Dutch and English question
##wording and answer options). code/survey/prepare_survey_data.R and main.R were read as
##text for the outcome coding and the attribute labels.
##Usage: Rscript dekleer_2025.R <dir holding survey_data.csv> <output dir>
##
##IPSOS online sample, the Netherlands, 5-20 June 2023, 2,528 respondents. Each respondent
##read two protest vignettes (iteration v1, v2 = task 1, 2; one profile per task) whose
##features were randomized: protest group (klimaatactivisten / boeren), protest action (op
##Malieveld geprotesteerd / snelweg geblokkeerd / vernieling van overheidsgebouw) and use of
##violence (geen geweld / politie aangevallen / politie aangevallen en opgepakt). The group is
##randomized per vignette (1,280 respondents saw both groups, 1,248 the same group twice).
##The levels are stored as the Dutch fragments in the data file (these are the inserted
##vignette texts; the authors' English labels: Pro-Environment / Environment-Critical, Legal
##Protest / Blocked Highway / Vandalized State Property, Non-Violent / Attacked Police /
##Attacked Police, Arrested). The codebook lists "Politie aangevallen en gearresteerd" for the
##third violence level where the data hold "politie aangevallen en opgepakt"; the data text
##is kept. The full vignette template (the sentence around the fragments) is not in the
##deposit (online appendix, not read). Restrictions, level weights: not documented; the
##group x violence and group x action cells are all filled and near-equal.
##Outcomes (codebook wording; [protestgroep] is the vignette's group):
##  rating          support: "Steunt u de protestacties van de [protestgroep] of keurt u deze
##                  af?" 1 = Keur ze sterk af, 2 = Keur ze af, 3 = Neutraal, 4 = Steun ze,
##                  5 = Steun ze in sterke mate (order of the authors' 0-1 recode,
##                  prepare_survey_data.R; higher = more support). 2 tasks have neither outcome and are omitted.
##  rating_prosecute "Vindt u dat de [protestgroep] vervolgd moeten worden?" 1 = Ja, 0 = Nee
##                  (4 tasks hold a whitespace-only answer: NA).
##Covariates: cov_age (years), cov_gender (gender: Man -> male, Vrouw -> female, Non-binair
##and "Anders, namelijk:" -> other; codebook values), cov_education (Dutch answer text),
##cov_region (Dutch answer text), cov_attention_answer (answer to 7+6) and cov_attention_pass
##(1 if it is 13), cov_duration_sec (duration_in_seconds: whole survey), cov_survey_weight
##(region_weight, "Region weights to correct for oversampling"), thermometers, left-right,
##trust items, rurality, Randstad, region-resentment items, climate concern, income
##sufficiency, vote intention 2024 and vote_choice / vote_choice_v2 (the authors' already
##coarsened right-wing-populist summaries), the manipulation check (man_check_conjoint), all
##as answer text. Dropped: V1 (row number), the open-letter variables (letter_yesno,
##letter_count and the authors' sentiment codings of the withheld open answers). The source
##id is a random string; it is re-keyed to integers in file order. Respondents flagged as
##speeders by the authors (prepare_survey_data.R) are kept. N = 2,528, as in the README.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "survey_data.csv"), colClasses = list(character = "id"), na.strings = c("", "NA"))
stopifnot(nrow(s) == 5056, uniqueN(s$id) == 2528, s[, .N, id][, all(N == 2)], all(s$iteration %in% c("v1", "v2")),
          s[, uniqueN(iteration), id][, all(V1 == 2)])
s[, nid := match(id, unique(id))]
sup <- c("Keur ze sterk af", "Keur ze af", "Neutraal", "Steun ze", "Steun ze in sterke mate")
blank <- !is.na(s$prosecuted) & trimws(s$prosecuted, whitespace = "[\\h\\v]") == ""   # 4 whitespace-only answers
s[blank, prosecuted := NA_character_]
stopifnot(sum(blank) == 4, all(na.omit(s$support) %in% sup), all(na.omit(s$prosecuted) %in% c("Ja", "Nee")))
gmap <- c("Man" = "male", "Vrouw" = "female", "Non-binair" = "other", "Anders, namelijk:" = "other")
stopifnot(all(s$gender %in% names(gmap)))
d <- s[, .(id = nid, task = as.integer(sub("v", "", iteration)), profile = 1L,
           rating = match(support, sup), rating_prosecute = fifelse(prosecuted == "Ja", 1L, 0L),
           attr_group = protest_group, attr_action = protest_action, attr_violence = protest_violence,
           cov_age = as.integer(age), cov_gender = unname(gmap[gender]), cov_education = education, cov_region = region,
           cov_attention_answer = attention_check, cov_attention_pass = as.integer(attention_check == 13),
           cov_duration_sec = duration_in_seconds, cov_survey_weight = region_weight,
           cov_thermometer_climate_activists = thermometer_climate_activists, cov_thermometer_farmers = thermometer_farmers,
           cov_left_right = left_right, cov_trust_dutch_parliament = trust_dutch_parliament,
           cov_trust_politicians = trust_politicians, cov_trust_political_parties = trust_political_parties,
           cov_trust_scientists = trust_scientists, cov_place_rural_urban = place_rural_urban, cov_randstad = randstad,
           cov_feel_urban_rural = feel_urban_rural, cov_services_urban_rural = services_urban_rural,
           cov_natpol_region = natpol_region, cov_vote_general_elections_2024 = vote_general_elections_2024,
           cov_vote_choice = vote_choice, cov_vote_choice_v2 = vote_choice_v2, cov_climate_concern = climate_concern,
           cov_income_suffic = income_suffic, cov_man_check_conjoint = man_check_conjoint)]
d <- d[!(is.na(rating) & is.na(rating_prosecute))]
stopifnot(!anyNA(d[, .(attr_group, attr_action, attr_violence)]), uniqueN(d$id) == 2528)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dekleer_2025_protest_support.csv"))
