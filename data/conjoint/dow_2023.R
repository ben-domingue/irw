##Vigilantism conjoint (Guatemala household survey) from
##Dow, D., Levy, G., Romero, D., & Tellez, J. (2023). State absence, vengeance, and the logic of
##vigilantism in Guatemala. Comparative Political Studies, 57(1), 147-181.
##https://doi.org/10.1177/00104140231169026 (closed access; not read beyond the abstract)
##Replication data: Harvard Dataverse doi:10.7910/DVN/M9WUK8, CC0 1.0. Files read: tidy-cjt.rds
##(one tibble, 4 rows per respondent), "Dow, Levy, Romero, Tellez Codebook.xlsx", conjoint-results.R
##(read as text, not run).
##Usage: Rscript dow_2023.R <dir holding tidy-cjt.rds> <output dir>
##
##9,365 respondents (face-to-face household survey across 14 departments; abstract: "a conjoint
##experiment presented to over 9000 households across Guatemala"), 2 tasks of 2 crime scenarios
##("Case 1" / "Case 2"), 5 attributes. task = task_number, profile = profile (codebook: "top = A,
##bottom = B"; Case 1 = A). Both questions were asked of the same pair, so both are in one table:
##  choice        = prof_chosen: "Of the two scenarios, in which case do you think it would be better
##                  for someone in the community rather than the police to punish the perpetrator
##                  directly? Even if you aren't completely sure, choose one of the two cases."
##                  Forced choice (codebook), no opt-out.
##  choice_punish = punish_chosen: "And of the two scenarios, which case do you think should be
##                  punished more severely?" Forced choice, no opt-out.
##Every task has exactly one chosen profile on both questions (stopifnot below).
##Attribute text is the authors' English factor labels in the .rds (the survey was in Spanish; the
##Spanish attribute wording is not deposited). The codebook's English labels differ slightly for the
##perpetrator ("Police affiliate", "Gang affiliate", "Regular citizen"; the data: "Police", "Gang
##member", "Common person"); the data labels are kept. perp_gender's "perp_" prefix is stripped
##(codebook levels: Man, Woman). Attribute order, presentation and randomization restrictions are
##not documented in the deposit.
##Covariates (codebook mappings): cov_gender from `woman` (0 Man = male, 1 Woman = female);
##cov_age (age, "How old are you?"); cov_education (codebook "Variable in R" mapping: 1 None,
##2 Primary (1-6), 3 Secondary (7-9), 4 Diversified (10-12), 5 Technical/vocational, 6 University,
##7 Post-graduate, 8 Masters, 9 Doctorate); cov_department (departamento, mis-encoded UTF-8 repaired);
##cov_mano_dura (1 strongly disagree .. 5 strongly agree), cov_basic_expenses (1 multiple times each
##month .. 5 never has trouble paying), cov_sexual_assault (likelihood, 1 not at all .. 4 very likely),
##cov_war_victim and cov_war_pac (0 No, 1 Yes), cov_women_leaders and cov_rape_change (answer text as
##stored), cov_enumerator_gender (enum_gender f/m -> female/male).
##Dropped: municipality, community and km_to_cabecera (small-area location), the authors' derived
##indices and dummies (police_latent, police_fct, broken_windows, broken_windows_neigh, severe_dum,
##crime_problem, crime_better, asset_count, chosen_dummy, punish_dummy), indigenous_lang (codebook
##question "Is Spanish your mother tongue?" No=0/Yes=1 contradicts the variable name) and
##vigilante_assault (stored as codes 1-3; the codebook gives only answer text, no mapping).
##No survey weight in the deposit. Source ids "r_<n>" re-keyed to <n>.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "tidy-cjt.rds")))
stopifnot(nrow(s) == 37460, s[, .N, r_id][, all(N == 4)])
d <- data.table(id = as.integer(sub("^r_", "", s$r_id)), task = as.integer(as.character(s$task_number)),
                profile = match(as.character(s$profile), c("A", "B")),
                choice = as.integer(as.character(s$prof_chosen) == as.character(s$profile)),
                choice_punish = as.integer(as.character(s$punish_chosen) == as.character(s$profile)))
stopifnot(!anyNA(d$id), d[, .N, .(id, task, profile)][, all(N == 1)],
          d[, .(a = sum(choice), b = sum(choice_punish)), .(id, task)][, all(a == 1 & b == 1)],
          all(d$choice == s$chosen_dummy), all(d$choice_punish == s$punish_dummy))
d[, attr_victim_gender := as.character(s$victim_gender)]
d[, attr_crime := as.character(s$crime)]
d[, attr_perpetrator := as.character(s$perp)]
d[, attr_social_distance := as.character(s$social_distance)]
d[, attr_perpetrator_gender := sub("^perp_", "", as.character(s$perp_gender))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
fixenc <- function(x) { y <- iconv(x, "UTF-8", "latin1"); Encoding(y) <- "UTF-8"; stopifnot(!anyNA(y), validUTF8(y)); y }
stopifnot(all(s$woman %in% 0:1))
d[, cov_gender := c("male", "female")[s$woman + 1L]]
d[, cov_age := as.integer(s$age)]
edu <- c("None", "Primary (1-6)", "Secondary (7-9)", "Diversified (10-12)", "Technical/vocational",
         "University", "Post-graduate", "Masters", "Doctorate")
stopifnot(all(s$education %in% c(1:9, NA)))
d[, cov_education := edu[s$education]]
d[, cov_department := gsub("-", " ", fixenc(s$departamento))]
d[, cov_mano_dura := as.integer(s$mano_dura)]
d[, cov_basic_expenses := as.integer(s$basic_expenses)]
d[, cov_sexual_assault := as.integer(s$sexual_assault)]
d[, cov_war_victim := as.integer(s$war_victim)]
d[, cov_war_pac := as.integer(s$war_pac)]
d[, cov_women_leaders := as.character(s$women_leaders)]
d[, cov_rape_change := s$rape_change]
stopifnot(all(s$enum_gender %in% c("f", "m")))
d[, cov_enumerator_gender := c(f = "female", m = "male")[s$enum_gender]]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dow_2023_vigilantism.csv"))
