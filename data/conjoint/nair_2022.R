##COVID-19 vaccine-recipient and international-agreement conjoints from
##Nair, G., & Peyton, K. (2022). Building mass support for global pandemic recovery efforts
##in the United States. PNAS Nexus, 1(4), pgac123. https://doi.org/10.1093/pnasnexus/pgac123
##Replication data: Harvard Dataverse doi:10.7910/DVN/FYYJD9, CC0 1.0. Files read:
##lucid_conjoint_person.rds, lucid_conjoint_agreement.rds, lucid_survey.rds (Survey 1, Lucid),
##norc_conjoint.rds, norc_survey.rds (Survey 2, NORC AmeriSpeak). Design and wording: SM
##sections S1.2, S1.3, S2.2 (pgac123_supplemental_file.pdf); levels as stored in the .rds factors.
##Usage: Rscript nair_2022.R <dir holding the .rds files> <output dir>
##
##Three experiments with different attribute sets/samples -> three tables:
##1. nair_2022_vaccine_recipients (Lucid, April 2021, N = 1,751; 1,747 in the file): 5 pairs of
##   people waiting for a COVID-19 vaccine; attributes sex, age group, risk of exposure, risk of
##   serious illness, occupation group, can work from home, country of origin (7). Levels drawn
##   uniformly and independently (SM S1.2). choice = "If you had to choose between them, which of
##   these two people should be given priority to receive the vaccine?" (forced, no opt-out);
##   rating = 1-7, 1 = should definitely not receive the vaccine, 7 = should definitely receive it.
##   The file holds 8,702 answered tasks (1,722 respondents with 5, 25 with fewer); absent tasks
##   were not answered. Occupation is stored as in the .rds ("Non-essential worker"; SM lists
##   "Non-essential workers").
##2. nair_2022_covax_agreement_lucid (same Lucid respondents; conjoint order randomized,
##   cov_conjoint_first): 4 pairs of international vaccine agreements, 7 attributes (participants,
##   cost to household, distribution of costs, distribution of benefits, external supply agreements
##   allowed, sharing of technology, monitoring). choice = "Which of these two agreements do you
##   prefer?" (forced; 36 tasks have no choice but keep their ratings); rating = vote "definitely
##   against (1)" to "definitely in favor (7)". 1,749 respondents after dropping rows with no outcome.
##3. nair_2022_covax_agreement_norc (NORC AmeriSpeak, Sep-Oct 2021, N = 4,214): 2 pairs, 5
##   attributes (overall cost, proportion paid by the U.S., funding use, beneficiaries, duration).
##   choice = "If you had to choose, which agreement do you favor?" (forced; 277 tasks without a
##   choice keep ratings); rating = likelihood of voting for the agreement, asked on a 5-point
##   scale Definitely against (1) ... Definitely in favor (5) but deposited ONLY as the authors'
##   0-1 rescale (0, .25, .5, .75, 1); stored as deposited (0 = definitely against). Duration
##   levels in the data are 1/3/5/7/9 years while SM S2.2 lists 1-5 years: data kept.
##   burden_ (cost x proportion, a derived quantity) and burden_prob are dropped. 4,204 respondents
##   after dropping rows with no outcome (paper 4,214).
##Rows with neither choice nor rating are omitted, so a few tasks keep only one profile.
##Spot check: in US-vs-other pairs, low-illness-risk Americans are chosen with probability 0.52,
##as the paper reports (p. 3).
##Task = the k in the source profile code (p_cand_k_j / a_cand_k_j / p_conj_k_j), profile = j.
##Covariates: cov_age (x_age, years), cov_gender (x_sex Female/Male), cov_education (Lucid
##x_education answer text; NORC x_edu, the authors' 5-category text, the only one deposited),
##cov_party_id7 (x_pid_7 / x_pid7 text), cov_survey_weight (survey_weight: Lucid raking weight
##built by the authors, NORC panel weight). Lucid cov_attention_pass = admin_acq_pass (the second
##attention check placed after the first conjoint; 92% passed, SM S1). Other cov_ keep the source
##text/codes. Qualtrics ResponseIds re-keyed to integers; derived recodes (x_female, *_binary_n,
##x_age_cat, x_hhi_n/short, x_pid_7n, x_ideo_3/7n...) and post-conjoint outcomes (y_*, Z_frame) dropped.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) as.data.table(readRDS(file.path(raw, f)))
tp <- function(d) d[, `:=`(task = as.integer(sub(".*_(\\d+)_(\\d+)$", "\\1", profile)),
                           profile = as.integer(sub(".*_(\\d+)$", "\\1", profile)))]
## ---- Lucid ----
ls <- rd("lucid_survey.rds")
ls[, id := seq_len(.N)]
lcov <- ls[, .(admin_ResponseId, id, cov_age = as.integer(x_age), cov_gender = c(Female = "female", Male = "male")[x_sex],
               cov_education = x_education, cov_party_id7 = x_pid_7, cov_ideology7 = x_ideo_7n,
               cov_race = x_race, cov_ethnicity = x_ethnicity, cov_hispanic_origin = x_hispanic_full,
               cov_region = x_region, cov_income = as.character(x_hhi), cov_political_attention = x_pol_atn_n,
               cov_attention_pass = as.integer(admin_acq_pass), cov_conjoint_first = Z_display_first,
               cov_covid_vaccinated = covid_vaxed_binary_n,
               cov_vnat_1 = vnat_1_n, cov_vnat_2 = vnat_2_n, cov_vnat_3 = vnat_3_n, cov_vnat_4 = vnat_4_n, cov_vnat_5 = vnat_5_n,
               cov_nationalism = national_n, cov_cosmopolitanism = cosmop_n, cov_altruism_willing = altruism_willing_n,
               cov_altruism_donate = altruism_donate_n, cov_recip_neg_own = recip_neg_own_n, cov_recip_neg_oth = recip_neg_oth_n,
               cov_recip_neg_rev = recip_neg_rev_n, cov_recip_pos_fav = recip_pos_fav_n, cov_recip_pos_gift = recip_pos_gift_n,
               cov_survey_weight = survey_weight)]
stopifnot(!anyNA(lcov$cov_gender), uniqueN(lcov$admin_ResponseId) == nrow(lcov))
lcov[cov_education == "Prefer not to answer", cov_education := NA]
fin <- function(d, nm) {
  d <- merge(d, lcov, by = "admin_ResponseId"); d[, admin_ResponseId := NULL]
  d <- d[!(is.na(choice) & is.na(rating))]
  stopifnot(d[, .N, .(id, task)][, all(N <= 2)], d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)])
  setcolorder(d, c("id", "task", "profile", "choice", "rating")); setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(nm, ".csv")))
  cat(nm, nrow(d), uniqueN(d$id), "\n")
}
p <- tp(rd("lucid_conjoint_person.rds"))
p <- p[, .(admin_ResponseId, task, profile, choice = as.integer(conjoint_chosen), rating = as.integer(conjoint_rating),
           attr_sex = as.character(sex_), attr_age_group = as.character(age_), attr_exposure_risk = as.character(exposure_),
           attr_illness_risk = as.character(harm_), attr_occupation = as.character(occupation_),
           attr_work_from_home = as.character(work_), attr_country = as.character(country_))]
fin(p, "nair_2022_vaccine_recipients")
g <- tp(rd("lucid_conjoint_agreement.rds"))
g <- g[, .(admin_ResponseId, task, profile, choice = as.integer(conjoint_chosen), rating = as.integer(conjoint_rating),
           attr_participants = as.character(participants_), attr_household_cost = as.character(price_),
           attr_cost_distribution = as.character(costs_), attr_benefit_distribution = as.character(benefits_),
           attr_external_supply = as.character(supply_), attr_tech_sharing = as.character(sharing_),
           attr_monitoring = as.character(monitoring_))]
fin(g, "nair_2022_covax_agreement_lucid")
## ---- NORC ----
ns <- rd("norc_survey.rds")
ns[, id := seq_len(.N)]
ncov <- ns[, .(CaseId, id, cov_age = as.integer(x_age), cov_gender = c(Female = "female", Male = "male")[x_sex],
               cov_education = as.character(x_edu), cov_party_id7 = as.character(x_pid7), cov_ideology7 = as.character(x_ideo_7),
               cov_race = x_race, cov_religion = x_relig_cat, cov_religious_attendance = as.character(x_relig_attend),
               cov_marital = x_marital, cov_employment = x_employ_long, cov_income = as.character(x_hhi),
               cov_state = x_state, cov_region = x_region_long, cov_metro = x_metro, cov_home = x_home_long, cov_home_type = x_home_type,
               cov_altruism = as.character(x_altruism), cov_vaccine_nationalism = as.character(x_vaxnat),
               cov_patriotism_nationalism1 = as.character(x_patnat1), cov_patriotism_nationalism2 = as.character(x_patnat2),
               cov_survey_weight = survey_weight)]
stopifnot(!anyNA(ncov$cov_gender), uniqueN(ncov$CaseId) == nrow(ncov))
n <- tp(rd("norc_conjoint.rds"))
n <- n[, .(CaseId, task, profile, choice = as.integer(conjoint_chosen), rating = conjoint_vote,
           attr_overall_cost = as.character(cost_), attr_us_share = as.character(prop_), attr_funding_use = as.character(purpose_),
           attr_beneficiaries = as.character(benefit_), attr_duration = as.character(duration_))]
n <- merge(n, ncov, by = "CaseId"); n[, CaseId := NULL]
n <- n[!(is.na(choice) & is.na(rating))]
stopifnot(n[, .N, .(id, task)][, all(N <= 2)], n[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)],
          all(n$rating %in% c(0, .25, .5, .75, 1, NA)))
setcolorder(n, c("id", "task", "profile", "choice", "rating")); setorder(n, id, task, profile)
fwrite(n, file.path(out, "nair_2022_covax_agreement_norc.csv"))
cat("norc", nrow(n), uniqueN(n$id), "\n")
