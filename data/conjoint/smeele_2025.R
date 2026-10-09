##Two taboo-trade-off discrete choice experiments (Netherlands, July-August 2023) from
##Smeele, N. V. R., van Cranenburgh, S., Donkers, B., Schermer, M. H. N., & de Bekker-Grob, E. W.
##(2025). Taboo trade-off aversion in choice behaviors: A discrete choice model and application to
##health-related decisions. Social Science & Medicine, 386, 118606.
##https://doi.org/10.1016/j.socscimed.2025.118606
##Replication data: DataverseNL doi:10.34894/BODW30, CC BY-NC 4.0 (dataset licence and every file
##in README.txt), no restricted files. Files read: healthinsurance_dce.csv (saved as hi.csv),
##organtransplantation_dce.csv (saved as ot.csv), README.txt (the codebook: variable meanings,
##units, value codes). Read as text: design files and model code in github.com/nvrsmeele/ttoamodel.
##The article (Elsevier) and the Dutch questionnaire were not available, so the displayed wording
##of attributes and questions is not known: attribute levels are stored as the codebook values
##and units below, not as displayed text.
##Usage: Rscript smeele_2025.R <raw dir> <output dir>
##
##Two DCEs with different attributes and designs = two tables (as in the deposit and paper):
##1) smeele_2025_health_insurance: 708 adults, 14 tasks (fixed blocked design, 3 blocks x 14
##   choice sets), 2 unlabelled alternatives ("alternative 1/2"), forced choice. Policies on
##   including new medicines in the basic insurance package. Attributes (codebook):
##     attr_deaths  = A?_DEATHS, "Number of patient deaths (x 1,000 patient deaths)", stored as the
##                    deposit's signed value -15 ... 15 (thousands; negative = fewer deaths is the
##                    natural reading, not stated);
##     attr_premium = A?_PREM, "Change in basic health premium per month (x 1 Euro)", -5 ... 25.
##   choice: CHOICE (1 = alternative 1, 2 = alternative 2); wording not deposited.
##   rating_certainty: UNCERTAIN, "how uncertain the respondent is about their choice (1 = very
##     uncertain, 5 = very certain)", asked once per task; repeated on both profile rows.
##2) smeele_2025_organ_transplant: 691 adults, 10 tasks (fixed blocked design, 4 blocks x 10),
##   dual response. Funding a technique to "refurbish" lower-quality organs via the premium.
##   Profiles 1-2 = designed alternatives; profile 3 = alternative 3, the same in every task
##   (1,200 deaths, premium change 0, good condition: the current situation, by its constant
##   values; the codebook gives it attributes, so it is kept as a profile). Attributes:
##     attr_deaths  = A?_DEATHS, "Number of patient deaths (x 100 patient deaths)", 2 ... 12;
##     attr_premium = A?_PREM, change in monthly premium (x 1 Euro), 0 ... 20;
##     attr_quality = A?_QOL, quality of life after transplantation: 1 = "good condition",
##                    0 = "moderate condition" (codebook labels).
##   choice: CHOICE_STG2 (= FINAL_CHOICE), stage 2 choice among alternatives 1, 2, 3; it is
##     always the stage-1 pick or alternative 3.
##   choice_stage1: CHOICE_STG1, forced choice between alternatives 1 and 2 (profile 3 was not
##     offered at this stage and is 0).
##   trial_survey_arm: SURVEY_ARM (1/2/3, "survey arm identifier"; arm meanings not documented;
##     only arm 3 has the cheap-talk check Q_ARM, kept as cov_cheap_talk_check: 3 = correct).
##task = SCENARIO, "the choice task as it appeared in the experimental design" (design order; the
##display order is not documented). profile = alternative number.
##Dropped: the authors' derived taboo indicators (A?_TABOO*), the free-text post hoc reasons
##(T1/T2/T3_REASON; Dutch open answers). RESPID is already a 1..N integer and is kept.
##Covariates (codebook codes -> codebook labels): cov_gender (0 male, 1 female), cov_age_group
##(1 low age, 2 mid-age, 3 high age), cov_education (1 low, 2 medium, 3 high education),
##cov_religious (1 yes 0 no), cov_household_income (low/medium/high household income),
##cov_household (8 household compositions), EQ-5D items (cov_eq5d_*, 0/1 as stored, and the
##0-100 health scale), Likert items as stored (cov_altruism HI only, cov_risk_*, cov_moral_*),
##organ-donation items (OT only, 0/1; deregistered 2 = don't know).
##Counts: 708 x 14 = 9,912 and 691 x 10 = 6,910 tasks, as in README.txt.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
covs <- function(x) {
  cv <- x[, .(cov_gender = c("male", "female")[GENDER + 1L],
              cov_age_group = c("low age", "mid-age", "high age")[AGE],
              cov_education = c("low education", "medium education", "high education")[EDUC],
              cov_religious = RELIGION,
              cov_household_income = c("low household income", "medium household income", "high household income")[HH_INC],
              cov_household = c("single", "with partner", "with partner and child(ren)", "with partner, child(ren) and others",
                                "with partner and others", "single parent with child(ren)",
                                "single parent with child(ren) and others", "other")[HH_COMP],
              cov_eq5d_health_scale = EQ5D_HSCALE)]
  for (v in grep("^EQ5D_(MOB|SELF|ACTIV|PAIN|ANXI)", names(x), value = TRUE)) cv[, paste0("cov_eq5d_", tolower(sub("EQ5D_", "", v))) := x[[v]]]
  for (v in grep("^(ALTRUISM|RISKAVERS_|MORALDIM_|DONOR_)", names(x), value = TRUE))
    cv[, paste0("cov_", tolower(sub("RISKAVERS", "risk", sub("MORALDIM", "moral", v)))) := x[[v]]]
  stopifnot(all(x$GENDER %in% 0:1), all(x$AGE %in% 1:3), all(x$EDUC %in% 1:3), all(x$HH_INC %in% 1:3), all(x$HH_COMP %in% 1:8))
  cv
}
## 1) health insurance
h <- fread(file.path(raw, "hi.csv"))
stopifnot(nrow(h) == 9912, h[, .N, RESPID][, all(N == 14)], all(h$CHOICE %in% 1:2))
hc <- covs(h)
d1 <- rbindlist(lapply(1:2, function(p) data.table(
  id = h$RESPID, task = h$SCENARIO, profile = p, choice = as.integer(h$CHOICE == p),
  rating_certainty = h$UNCERTAIN,
  attr_deaths = as.character(h[[paste0("A", p, "_DEATHS")]]), attr_premium = as.character(h[[paste0("A", p, "_PREM")]]), hc)))
stopifnot(d1[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d1$rating_certainty))
setorder(d1, id, task, profile)
fwrite(d1, file.path(out, "smeele_2025_health_insurance.csv"))
## 2) organ transplantation
o <- fread(file.path(raw, "ot.csv"))
stopifnot(nrow(o) == 6910, o[, .N, RESPID][, all(N == 10)], all(o$CHOICE_STG2 == o$FINAL_CHOICE),
          all(o$CHOICE_STG2 == o$CHOICE_STG1 | o$CHOICE_STG2 == 3), all(o$A3_DEATHS == 12), all(o$A3_PREM == 0), all(o$A3_QOL == 1))
oc <- covs(o)
d2 <- rbindlist(lapply(1:3, function(p) data.table(
  id = o$RESPID, task = o$SCENARIO, profile = p, choice = as.integer(o$CHOICE_STG2 == p),
  choice_stage1 = as.integer(o$CHOICE_STG1 == p),
  attr_deaths = as.character(o[[paste0("A", p, "_DEATHS")]]), attr_premium = as.character(o[[paste0("A", p, "_PREM")]]),
  attr_quality = c("moderate condition", "good condition")[o[[paste0("A", p, "_QOL")]] + 1L],
  trial_survey_arm = o$SURVEY_ARM, cov_cheap_talk_check = fifelse(o$SURVEY_ARM == 3, o$Q_ARM, NA_integer_), oc)))
stopifnot(d2[, sum(choice), .(id, task)][, all(V1 == 1)], d2[, sum(choice_stage1), .(id, task)][, all(V1 == 1)], !anyNA(d2$attr_quality))
setorder(d2, id, task, profile)
fwrite(d2, file.path(out, "smeele_2025_organ_transplant.csv"))
