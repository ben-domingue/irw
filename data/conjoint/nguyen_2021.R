##Agricultural-subsidy proposal conjoints (US and Switzerland) from
##Nguyen, Q., Spilker, G., & Bernauer, T. (2021). The (still) mysterious case of agricultural
##protectionism. International Interactions, 47(3), 391-416.
##https://doi.org/10.1080/03050629.2021.1898957
##Replication data: Harvard Dataverse doi:10.7910/DVN/APJPKV, CC0 1.0, no restricted files, no terms.
##File read: agrardata_rep.dta (Dataverse "original format" download of agrardata_rep.tab).
##Level text, question wording and design from the article (Table 1, Table 2, "Conjoint
##Experiment" section, pp. 400-402); the authors' replication script
##(Agrar_Replicationscript_conjoint.R, read as text) for which variables are outcomes.
##Usage: Rscript nguyen_2021.R <raw dir> <output dir>
##
##IPSOS online panels, November 2017, quota samples aged 18-65: 2,854 US and 2,843 Swiss
##respondents in the deposit, every one with all 6 tasks of 2 proposals (12 rows each). Each
##proposal for how direct payments to farmers are spent varies 6 goals (environmentally
##friendly farming, support for small farms, food security, protection of countryside, animal
##welfare, food quality), each at "Large", "Moderate" or "None". The deposit codes the levels
##0/1/2 with value labels none/medium/high; the article's Table 1-2 show the displayed text
##None/Moderate/Large, so 0 = None, 1 = Moderate, 2 = Large (the authors' script names the
##levels None/Medium/High in its plots). Respondents saw the US or Swiss questionnaire
##(Swiss language(s) not stated; German answer labels survive in Q21_CH); text here is the
##article's English. Row order of the goals was randomized (article p. 401) but not recorded.
##Outcomes:
##  choice = accept, "Which proposal do you prefer?" (Table 2), forced choice, no opt-out.
##  rating = like, each proposal rated on a seven-point scale (article p. 401; .dta label
##           "like this proposal 1-7 (1 not like)"), 1 = not like .. 7; stored raw.
##TASK AND PROFILE ARE INFERRED: the source column `conjoint` runs 1-12 within respondent.
##Pairing rows (c, c+1) gives 0 or 2 chosen profiles in 8,796 x 2 tasks, while pairing
##(c, c+6) gives exactly one chosen profile in all 34,182 tasks, so conjoint 1-6 are profile 1
##of tasks 1-6 and 7-12 are profile 2 (task = conjoint mod 6, profile = 1 + (conjoint > 6)).
##That tasks 1-6 are in display order and which proposal was on the left are assumed.
##Before the conjoint, half of each sample saw a cost prime (the subsidy total and per-taxpayer
##cost; article p. 400): trial_cost_frame 1 = prime shown, 0 = not.
##TWO TABLES, nguyen_2021_farm_subsidies_us and _ch: the authors analyse each country
##separately (Figures 2-5, A1-A22) and never pool.
##Covariates (text as deposited; mojibake apostrophes/ellipses repaired):
##  cov_age (Q1_recode_age, years, as deposited); cov_gender (Q2 Male/Female); cov_education_group
##  (the deposit's country-specific recodes only: US NO COL/SOME COL/COLL+, CH Low/Medium/High;
##  the raw education question is not deposited, so not cov_education); cov_ideology (Q21_USA
##  text; Q21_CH 1-7 with ends "Links"/"Rechts" as deposited); cov_income (Q22 monthly
##  household income band, "Prefer not to say" -> NA); cov_employed (Q23), cov_knows_farmer (Q26),
##  cov_worked_on_farm (Q28) Yes/No; cov_subsidies_too_low (agrarsubtoolow, the post-prime
##  question "is the amount of direct payments too high ... too low", value-label text, 1.Too high
##  .. 5.Too low); attitude items as answer text: cov_food_self_sufficiency (Part3_Q5_1),
##  cov_tradition_1..4 (Part3_Q6_1..4), cov_equality (Part3_Q7, 1 = income should be distributed
##  equally .. 7), cov_econ_insecurity (Part3_Q8), cov_climate_when (Part3_Q10), cov_climate_concern
##  (Part3_Q11), cov_climate_vs_growth (Part3_Q12), cov_nationalism_1..5 (Part3_Q14_1..5). The item
##  wordings are not deposited (the article names the constructs). "Don't know / refuse" stays as
##  text (refusal and don't know are one option). No survey weight is deposited.
##N: the article reports "valid answers for our main outcome" from 2,605 US / 2,310 Swiss
##respondents; the deposit holds 2,854 / 2,843 conjoint respondents, all with complete conjoint
##answers and the subsidy question. The cause of the gap is not documented; nothing is dropped.
##Q22 income bands read "US-$" in both samples, as deposited.
##Spot check: choice AMCEs (lm, SEs clustered by id) are positive for Moderate and Large on all
##six goals in both countries (0.08-0.23), Large vs Moderate differences small, as in Figures 2-3
##(the article reports no exact AMCE values in text).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "agrardata_rep.dta"))
fix <- function(x) { x <- as.character(x); x[x == ""] <- NA
  x <- gsub("â€™", "’", x, fixed = TRUE); gsub("â€¦", "…", x, fixed = TRUE) }
lv <- c("None", "Moderate", "Large")
cj <- as.integer(k$conjoint); stopifnot(all(cj %in% 1:12))
d <- data.table(id = as.integer(k$respondent), task = (cj - 1L) %% 6L + 1L, profile = 1L + (cj > 6L),
                choice = as.integer(k$accept), rating = as.integer(k$like))
at <- c(environment_friendly_farming = "env_farming", small_farms = "small_farmers", food_security = "food_security",
        countryside = "countryside", animal_welfare = "animal_care", food_quality = "food_quality")
for (v in names(at)) { x <- as.integer(zap_labels(k[[at[[v]]]])); stopifnot(all(x %in% 0:2))
  stopifnot(identical(names(attr(k[[at[[v]]]], "labels")), c("none", "medium", "high")))
  d[, paste0("attr_", v) := lv[x + 1L]] }
d[, trial_cost_frame := as.integer(k$costframe)]
d[, cov_country := fix(k$QCountry)]
d[, cov_age := as.integer(k$Q1_recode_age)]
stopifnot(all(k$Q2 %in% c("Male", "Female")))
d[, cov_gender := tolower(k$Q2)]
d[, cov_education_group := fifelse(k$QCountry == "USA", fix(k$Q4_USA_recoded), fix(k$Q4_CH_recoded))]
d[, cov_ideology := fifelse(k$QCountry == "USA", fix(k$Q21_USA), fix(k$Q21_CH))]
d[, cov_income := fix(k$Q22)][cov_income == "Prefer not to say", cov_income := NA]
d[, `:=`(cov_employed = fix(k$Q23), cov_knows_farmer = fix(k$Q26), cov_worked_on_farm = fix(k$Q28))]
d[, cov_subsidies_too_low := fix(as_factor(k$agrarsubtoolow, levels = "labels"))]
cm <- c(Part3_Q5_1_scale = "food_self_sufficiency", Part3_Q6_1_scale = "tradition_1", Part3_Q6_2_scale = "tradition_2",
        Part3_Q6_3_scale = "tradition_3", Part3_Q6_4_scale = "tradition_4", Part3_Q7 = "equality", Part3_Q8 = "econ_insecurity",
        Part3_Q10 = "climate_when", Part3_Q11 = "climate_concern", Part3_Q12 = "climate_vs_growth",
        Part3_Q14_1_scale = "nationalism_1", Part3_Q14_2_scale = "nationalism_2", Part3_Q14_3_scale = "nationalism_3",
        Part3_Q14_4_scale = "nationalism_4", Part3_Q14_5_scale = "nationalism_5")
for (v in names(cm)) d[, paste0("cov_", cm[[v]]) := fix(k[[v]])]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7))
setorder(d, id, task, profile)
for (cc in list(c("USA", "us"), c("Switzerland", "ch"))) {
  s <- d[cov_country == cc[1]][, cov_country := NULL]
  fwrite(s, file.path(out, paste0("nguyen_2021_farm_subsidies_", cc[2], ".csv")))
}
