##Candidate conjoints with ethical positions (Canada and US) from
##Islam, M. M., & Loewen, P. (2026). Ethical distance and electoral accountability: Voters punish
##politicians whose ethical views diverge from societal consensus. (Journal and DOI not given in the
##deposit; the article could not be found online as of 2026-10-08.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/O2RSXG, CC0 1.0, no restricted files.
##Files read: ethdist-candsupport-can.dta and ethdist-candsupport-usa.dta (Dataverse "original
##format" downloads of the .tab files). Read as text only: 01-data-prep-can.do, 03-data-prep-usa.do,
##02-analysis-main-can.do, 02_1-analysis-appendix-can.do (outcome wording, recodes).
##Usage: Rscript islam_2026.R <raw dir> <output dir>
##
##TWO TABLES, one per country, as the authors prepare and analyse them in separate do files:
##islam_2026_ethical_distance_canada (2,165 respondents, English or French) and
##islam_2026_ethical_distance_us (3,612 respondents). Counts match the do files' comments
##("2165 obs") and the first author's dissertation description (3,600 Americans, 2,200 Canadians).
##Panel provider and fielding dates are not documented in the deposit (rid looks like a Lucid ID).
##Each respondent completed 6 conjoint modules, one per ethical issue (death penalty, lying,
##bribery, cheating on a spouse, homosexuality, suicide). Each module showed Candidate A (profile 1)
##and Candidate B (profile 2) with 7 attributes: age (40/45/50/55), gender, party (Canada
##Conservative/Liberal; US Democrat/Republican), race (Canada White/Black/Hispanic/Asian Canadian;
##US White/Black/Hispanic/Asian American), profession (Business owner/Doctor/Farmer/Lawyer/
##Professor), experience ("Previous experience in government" / "No previous experience in
##government") and the candidate's position on that module's issue ("<Issue> is never / rarely /
##sometimes / often / always acceptable"), stored in attr_ethical_position; trial_issue names the
##module's issue. Text is stored as the source records it for the respondent's language: the
##Canadian file has _en and _fr versions of every level and Qualtrics UserLanguage (EN 1,836,
##FR-CA 329); French-language respondents get the _fr text (cov_language).
##TASK ORDER IS NOT RECORDED: task numbers 1-6 follow the modules' column order in the deposit
##(suicide, lying, bribery, cheating, death penalty, homosexuality), which may not be the order
##shown. Attribute order is not documented.
##Outcomes:
##  choice = <issue>_vote: "If you had to choose between them, which of these two candidates would
##           you vote for?" Candidate A (1) / Candidate B (2) (01-data-prep-can.do L540-543); forced.
##  rating = <issue>_rate_a_1 / _rate_b_1 (named rank/rk/rnk for some modules): a 0-100 rating of
##           each candidate (101 values observed); the question wording is not in the deposit.
##           Stored raw (the authors rescale it to 0-1).
##No missing outcome values.
##Covariates: cov_language (Canada); cov_birth_year (omni_*_yob); cov_age (the authors' `age`, which
##equals 2021 - birth year in Canada and 2020 - birth year in the US); cov_gender from the authors'
##gender_3cat value labels (0 Male, 1 Female, 2 Other; matches source gender 1/2/3);
##cov_educ_bachelors (authors' 0 = Less than bachelors, 1 = Bachelors or higher; the full education
##item has no labels); US: cov_census_region and cov_race (race_6cat label text);
##cov_lr_scale (omni_*_lr_scale_1, 11 values; direction undocumented, codes kept);
##cov_accept_<issue>: the respondent's own view of the issue, source codes 1-5 where the authors'
##recode gives 1 = Always .. 5 = Never acceptable (lying = e_accept_1, bribery 2, suicide 3,
##death penalty 4, cheating 5, homosexuality 6); cov_rstatus: the source's respondent status
##("good_complete" / "failed_news"; meaning undocumented, the authors do not filter on it).
##Weights: cov_survey_weight = wgtnotrestr (all respondents; NA for 22 Canadian and 28 US
##respondents); Canada also has cov_weight_restricted = wgtrestr (defined only for 879
##good_complete respondents). The authors' models are unweighted.
##Dropped: responseid (Qualtrics) and rid (panel ID) - re-keyed in source order; free-text race
##and employment answers; other survey items with unlabelled codes (education detail, province/
##state, income, party ID, religion, employment, democracy/trust batteries); the authors' derived
##variables.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
mods <- data.table(task = 1:6, issue = c("suicide", "lying", "bribery", "cheating on spouse", "death penalty", "homosexuality"),
                   m = c("sui", "lie", "bri", "chw", "dp", "hsex"), pos = c("suicide", "lie", "bribery", "cheatspouse", "deathpenalty", "homosex"))
outv <- list(can = list(vote = c("omni_can_sui_vote", "omni_can_lie_vote", "omni_can_e_brb_vo", "omni_can_cht_vote", "omni_can_dp_vote", "omni_can_hsx_vote"),
                        ra = c("omni_can_sui_rate_a_1", "omni_can_lie_rate_a_1", "omni_can_e_brb_rk_a_1", "omni_can_cht_rnk_a_1", "omni_can_dp_rank_a_1", "omni_can_hsx_rank_a_1"),
                        rb = c("omni_can_sui_rate_b_1", "omni_can_lie_rate_b_1", "omni_can_e_brb_rk_ab_1", "omni_can_cht_rnk_b_1", "omni_can_dp_rank_b_1", "omni_can_hsx_rank_b_1")),
             usa = list(vote = c("omni_us_sui_vote", "omni_us_lie_vote", "omni_us_e_brb_vo", "omni_us_cht_vote", "omni_us_dp_vote", "omni_us_hsx_vote"),
                        ra = c("omni_us_sui_rate_a_1", "omni_us_lie_rate_a_1", "omni_us_e_brb_rk_a_1", "omni_us_cht_rnk_a_1", "omni_us_dp_rank_a_1", "omni_us_hsx_rank_a_1"),
                        rb = c("omni_us_sui_rate_b_1", "omni_us_lie_rate_b_1", "omni_us_e_brb_rk_ab_1", "omni_us_cht_rnk_b_1", "omni_us_dp_rank_b_1", "omni_us_hsx_rank_b_1")))
lab <- function(x) { l <- attr(x, "labels"); unname(setNames(names(l), l)[as.character(zap_labels(x))]) }
for (f in c("can", "usa")) {
  k <- read_dta(file.path(raw, sprintf("ethdist-candsupport-%s.dta", f)))
  p <- if (f == "can") "omni_can_" else "omni_us_"
  n <- nrow(k); fr <- if (f == "can") k$userlanguage == "FR-CA" else rep(FALSE, n)
  stopifnot(!anyDuplicated(k$rid), all(k$finished == 1))
  rows <- list()
  for (t in 1:6) for (pr in 1:2) {
    ab <- c("a", "b")[pr]; m <- mods$m[t]
    g <- function(att) {
      en <- k[[paste0(ab, "_", m, "_", att, if (f == "can") "_en" else "")]]
      if (f == "can") { frv <- k[[paste0(ab, "_", m, "_", att, "_fr")]]; en <- ifelse(fr, frv, en) }
      stopifnot(!anyNA(en), all(en != "")); as.character(en)
    }
    vote <- as.integer(zap_labels(k[[outv[[f]]$vote[t]]])); stopifnot(all(vote %in% 1:2))
    rows[[length(rows) + 1]] <- data.table(rid = seq_len(n), task = t, profile = pr, choice = as.integer(vote == pr),
      rating = as.integer(zap_labels(k[[outv[[f]][[c("ra", "rb")[pr]]][t]]])),
      attr_age = g("age"), attr_gender = g("gender"), attr_party = g("party"), attr_race = g("race"),
      attr_profession = g("profession"), attr_experience = g("experience"), attr_ethical_position = g(mods$pos[t]),
      trial_issue = mods$issue[t])
  }
  d <- rbindlist(rows)
  stopifnot(all(d$rating %between% c(0, 100)), d[, sum(choice), .(rid, task)][, all(V1 == 1)])
  ## the issue attribute matches its module (English text)
  if (f == "usa") stopifnot(d[, all(mapply(grepl, c("Suicide", "Lying", "Bribery", "cheating on their spouse", "Death penalty", "Homosexuality")[task], attr_ethical_position))])
  cv <- data.table(rid = seq_len(n))
  if (f == "can") cv[, cov_language := k$userlanguage]
  cv[, cov_birth_year := as.integer(k[[paste0(p, "yob")]])]
  cv[, cov_age := as.integer(k$age)]
  stopifnot(all(zap_labels(k$gender_3cat) %in% 0:2), identical(names(attr(k$gender_3cat, "labels")), c("Male", "Female", "Other")))
  cv[, cov_gender := c("male", "female", "other")[as.integer(zap_labels(k$gender_3cat)) + 1L]]
  cv[, cov_educ_bachelors := as.integer(zap_labels(k$educ_bachelors))]
  if (f == "usa") { cv[, cov_census_region := lab(k$census_region)]; cv[, cov_race := lab(k$race_6cat)] }
  cv[, cov_lr_scale := as.integer(zap_labels(k[[paste0(p, "lr_scale_1")]]))]
  for (it in list(c("lying", 1), c("bribery", 2), c("suicide", 3), c("death_penalty", 4), c("cheating", 5), c("homosexuality", 6)))
    cv[, paste0("cov_accept_", it[1]) := as.integer(zap_labels(k[[paste0(p, "e_accept_", it[2])]]))]
  cv[, cov_rstatus := k$rstatus]
  cv[, cov_survey_weight := as.numeric(k$wgtnotrestr)]
  if (f == "can") cv[, cov_weight_restricted := as.numeric(k$wgtrestr)]
  d <- cv[d, on = "rid"]
  setnames(d, "rid", "id")
  setcolorder(d, c("id", "task", "profile", "choice", "rating", grep("^attr_", names(d), value = TRUE), "trial_issue"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, sprintf("islam_2026_ethical_distance_%s.csv", c(can = "canada", usa = "us")[f])))
}
