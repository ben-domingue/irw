##Three factorial police-encounter vignette experiments from
##Vaughn, P. E., & Huber, G. A. (2025). Seeing the state in action: Public preferences about and judgments of
##common police-civilian interactions. Criminology. (preprint https://doi.org/10.31235/osf.io/hxv8z)
##Replication data: Harvard Dataverse doi:10.7910/DVN/AKGL3N, CC0 1.0. Files read: Study1data_publicdatafile_cleaned.tab,
##Study2data_publicdatafile_cleaned.tab, StudyR1data_publicdatafile_cleaned.tab (anonymised by the authors);
##level labels from the authors' cleaning code 00_01/00_02/00_03 (read as text: Stata `label define`s for
##demeanor, weapon, punishment, education, income, party id), displayed vignette text in Study 1 from the cop_text_*/civ_text_*/outcome_text_* columns.
##Usage: Rscript vaughn_2025.R <dir holding s1.tab, s2.tab, r1.tab (the three .tab files)> <output dir>
##
##Three experiments, three tables (different attribute sets, populations and fieldings; the authors analyse them separately):
##  vaughn_2025_police_park_s1   Study 1 (Apr-May 2021, US online sample), 2,017 respondents. Park vignette: a civilian
##      lighting fireworks (neighbours report gunshots) is confronted by an officer in two exchanges. Attributes: officer race
##      (Black/White), demeanor (five officer/civilian polite or hostile pairs; z_interaction AP:AP, AP:AH, BH:AH, AH:AH, AH:AP;
##      "AP" polite, "AH" hostile, "BH" hostile on the first exchange only (civilian first); exact dialogue is in the data), and the officer's
##      decision (escorted from the park / written a ticket for disorderly conduct).
##  vaughn_2025_police_weapon_s2 Study 2 (Lucid, July 2021), 2,147 respondents: officer race, demeanor (4 officer-by-civilian
##      polite/hostile pairs), whether the civilian has a weapon (unarmed / baseball bat) and the punishment (ticketed / arrested).
##      The vignette text of Study 2 is NOT in the deposit; level text is the authors' Stata labels.
##  vaughn_2025_police_park_r1   Study R1 (replication of Study 1, May 2024), 1,546 rows (1,509 finished): civilian race added
##      as a factor, four demeanor pairs, officer race, officer decision (escort / ticket). Outcome N varies by item.
##One vignette per respondent; each respondent is one row (task 1, profile 1); no respondent id is deposited, id = row number.
##The outcome questions are asked at two stages of the one vignette: the "before punishment" items (expected punishment,
##fairness to the civilian, threat) follow the first part of the vignette, which does not yet reveal the officer's
##decision / punishment; the rest follow the decision. Both stages are columns of the one table; the stage is in the
##design_outcomes wording. The decision/punishment attribute is therefore not yet shown when the early items were answered.
##Ratings are stored raw as coded by the authors from the answer text (their .do: 1 = lowest, e.g. 1 Unfair ... 5 Fair; R1 0-4).
##Question wording is not deposited (only answer categories); design_outcomes carries paraphrases from the authors' variable labels.
##Covariates: cov_gender (x_female; Study R1 gender with 3 = non-binary -> other), cov_age, cov_education (answer text,
##authors' recode categories), cov_party_id (authors' 3-category pid from party id + leaners; R1 cov_party_id7 text from
##the 7-point item, 4 includes "other"/no preference per the authors' recode), cov_race / cov_region (authors' x_race / x_region),
##cov_duration_sec (survey duration), R1 cov_attention_pass (harder attention check, "about $1,500"), cov_income text (R1).
##Dropped: dates, device, text fields, Study 2's W* post-stratification-type columns (undocumented), the authors' interactions,
##hostile/polite dummies, Study 1's respondent_pid (a party label), political ideology codes.
##Count checks: 2,017 and 2,147 equal the rows of the public files; Study R1 has 1,546 rows, 1,529 with at least one outcome (17 dropped). The preprint's N was not read.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) fread(file.path(raw, f), na.strings = c("", "NA"))
rating <- function(x) as.integer(x)
fin <- function(r, nm) { setorder(r, id, task, profile); fwrite(r, file.path(out, paste0(nm, ".csv"))); cat(nm, nrow(r), "\n") }

## ---- Study 1
d <- rd("s1.tab")
dem1 <- c("Both Polite", "Hostile Civilian, Polite Officer", "Both Hostile (Civilian first)", "Both Hostile (Officer first)", "Polite Civilian, Hostile Officer")
stopifnot(all(d$S1treat_demeanor %in% 1:5), all(d$treat_officerwhite %in% 0:1), all(d$treat_ticket %in% 0:1))
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
  rating_expected_punishment = rating(d$S1out_expectedpunish_vig1), rating_fairness_before_punishment = rating(d$S1out_fairness_cit_vig1),
  rating_fairness_punishment = rating(d$S1out_fair_pun_vig2), rating_preferred_punishment = rating(d$S1out_prefpunish_vig2),
  rating_fairness_overall = rating(d$S1out_fair_global_vig2),
  attr_officer_race = c("Black", "White")[d$treat_officerwhite + 1L], attr_demeanor = dem1[d$S1treat_demeanor],
  attr_officer_decision = c("Escorted from park", "Ticketed")[d$treat_ticket + 1L],
  cov_gender = c("male", "female")[d$x_female + 1L], cov_age = as.integer(d$x_age), cov_education = d$x_education,
  cov_party_id = d$x_pid_3, cov_race = d$x_race, cov_region = d$x_region, cov_duration_sec = d$durationinseconds)
for (v in grep("^cov_(education|party_id|race|region)$", names(r), value = TRUE)) r[get(v) == "", (v) := NA]
fin(r, "vaughn_2025_police_park_s1")

## ---- Study 2
d <- rd("s2.tab")
dem2 <- c("Both Polite", "Hostile Civilian, Polite Officer", "Both Hostile (Officer first)", "Polite Civilian, Hostile Officer")
stopifnot(all(d$S2treat_demeanor %in% 1:4), all(d$treat_weapon %in% 0:1), all(d$treat_arrest %in% 0:1), all(d$x_gender %in% c("Female", "Male")))
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
  rating_fairness_before_punishment = rating(d$s2_out_fairnessb4p), rating_threat_to_victim = rating(d$s2_out_threat_vic),
  rating_threat_to_police = rating(d$s2_out_threat_cop), rating_threat_to_civilian = rating(d$out_threat_tociv_vig1),
  rating_expected_punishment = rating(d$s2_out_expectedpun), rating_fairness_punishment = rating(d$s2_out_fairnesspun),
  rating_fairness_punishment_victim = rating(d$out_fairness_pun_vic_vig2), rating_preferred_punishment = rating(d$s2_out_preferpun),
  rating_fairness_overall = rating(d$s2_out_fairnesglob),
  attr_officer_race = c("Black", "White")[d$treat_officerwhite + 1L], attr_demeanor = dem2[d$S2treat_demeanor],
  attr_civilian_weapon = c("Unarmed", "Baseball bat")[d$treat_weapon + 1L], attr_punishment = c("Ticketed", "Arrested")[d$treat_arrest + 1L],
  cov_gender = tolower(d$x_gender), cov_age = as.integer(d$x_age), cov_education = d$x_education, cov_party_id = d$x_pid_3,
  cov_race = d$x_race, cov_region = d$x_region)
for (v in grep("^cov_(education|party_id)$", names(r), value = TRUE)) r[get(v) == "", (v) := NA]
fin(r, "vaughn_2025_police_weapon_s2")

## ---- Study R1
d <- rd("r1.tab")
dem3 <- c("Both polite", "Hostile Civilian, Polite Officer", "Both Hostile (Officer First)", "Polite Civilian, Hostile Officer")
edu <- c("HS or less", "Some college, trade, associates", "BA", "Post-BA")
inc <- c("<$25,000", "$25,000 to $34,999", "$35,000 to $49,999", "$50,000 to $74,999", "$75,000 to $99,999", "$100,000 to $124,999",
         "$125,000 to $149,999", "$150,000 to $174,999", "$175,000 to $199,999", "$200,000 to $249,999", "$250,000 or more", NA)
pid <- c("Strong Democrat", "Democrat", "Independent, close to Democrat", "Independent", "Independent, close to Republican", "Republican", "Strong Republican")
stopifnot(all(d$T_demeanor %in% 0:3), all(d$T_civilianwhite %in% 0:1), all(d$T_officerwhite %in% 0:1), all(d$T_officerdecision %in% 0:1),
          all(d$d_educ %in% 1:4), all(d$d_income %in% 1:12), all(d$d_pid7 %in% 1:7))
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
  rating_preferred_punishment = rating(d$SR1_out_preferredpunish), rating_fairness_civilian = rating(d$SR1_out_fairciv),
  rating_fairness_officer = rating(d$SR1_out_faircop), rating_fairness_punishment = rating(d$SR1_out_fairpun),
  attr_civilian_race = c("Black", "White")[d$T_civilianwhite + 1L], attr_officer_race = c("Black", "White")[d$T_officerwhite + 1L],
  attr_demeanor = dem3[d$T_demeanor + 1L], attr_officer_decision = c("Escort", "Ticket")[d$T_officerdecision + 1L],
  cov_gender = ifelse(d$d_gender_nonbinary == 1, "other", ifelse(d$d_gender_female == 1, "female", "male")),
  cov_age = as.integer(d$d_age), cov_education = edu[d$d_educ], cov_income = inc[d$d_income], cov_party_id7 = pid[d$d_pid7],
  cov_attention_pass = as.integer(d$got_hard_acq), cov_duration_sec = d$durationinseconds)
## respondents with no outcome at all are omitted
r <- r[!(is.na(rating_preferred_punishment) & is.na(rating_fairness_civilian) & is.na(rating_fairness_officer) & is.na(rating_fairness_punishment))]
fin(r, "vaughn_2025_police_park_r1")
