##UK foreign-aid agency conjoints (YouGov omnibus, 2022) from
##Heinzel, M., Reinsberg, B., & Swedlund, H. (2024). Transparency and citizen support for public
##agencies: The case of foreign aid. Governance, 38(2), e12863. https://doi.org/10.1111/gove.12863
##Replication data: Harvard Dataverse doi:10.7910/DVN/QDQ4LU, CC0 1.0, no restricted files.
##File read: DOTRAN_experiment.dta (Dataverse "original format" download of DOTRAN_experiment.tab).
##Wording: the Stata variable labels (survey export) and the article (Section 3, Tables 2 and 4);
##the authors' DOTRAN_experiment.do (read as text) for which rating belongs to which conjoint.
##Usage: Rscript heinzel_2024_aid.R <raw dir> <output dir>
##
##2,058 UK respondents (YouGov omnibus) took three experiments; question order randomized
##(q1_q5_ord, kept as trial_question_order: the source's permutation string, not documented further).
##Experiment 1 is a monadic FCDO treatment (one factor) and is NOT a conjoint; its arm and outcome are
##kept as covariates (cov_fcdo_treatment, cov_fcdo_support). Experiments 2 and 3 are conjoints, each
##ONE task with two agencies side by side (Agency A = profile 1, Agency B = profile 2, from the
##variable names concept1/concept2 and the labels "- Agency A/B Screen 1"), each attribute a statement
##with level "Yes" or "No" ("Each item had two independently randomized levels", article). Different
##attribute sets -> TWO TABLES, same respondents and ids:
##  heinzel_2024_aid_transparency (article Experiment 2; data q_attr*_C2, rating q5_1/q5_2):
##    strategy "The agency provides information on key goals of its aid strategy and how it want[s ...]"
##    decision_making "The agency provides information on how decisions are made."
##    structure "The agency provides information on its organisational structure (like who its le[aders
##      are ...])"; operational_costs "The agency provides information on how much money it keeps for
##      operational costs [...]"; staff "The agency provides information on how many staff it has and
##      where they work."; project "The agency provides detailed information on each project (like
##      sector, recipient [country, and contractor])."
##  heinzel_2024_aid_reforms (article Experiment 3; data q_attr*_task1, rating q3_1/q3_2):
##    transparency "The agency expands transparency on its foreign aid management, policies and
##      spending."; anti_corruption "The agency includes anti-corruption as a guiding principle.";
##    allies "The agency focuses on giving foreign aid to political allies of the UK."; poverty "... to
##      the poorest countries."; human_rights "... to countries that respect human rights."; climate
##      "The agency focuses on spending foreign aid to address global problems like climate change.";
##    coordination "The agency coordinates with other donors."
##  Statements in [] are cut off in the 80-character Stata labels; the article's Tables 2 and 4 word
##  several statements differently ("focuses more on", "decision-making about where aid is allocated",
##  "spends on the day-to-day administration"); which wording respondents saw cannot be settled from
##  the deposit. Levels are the displayed "Yes"/"No" in every case.
##Intro (both, article p.10): "The UK government provides around 12 billion pounds in taxpayer money as
##foreign aid each year ... Please indicate to what extent you support giving foreign aid through each
##aid agency." rating: 1 (strongly oppose) .. 10 (strongly support), one per agency; no choice, no
##opt-out. Attribute row order not documented. No missing outcomes (2,058 x 2 rows per table;
##article Table 3 N = 4,116).
##Covariates (value-label text; "Skipped", "Not Asked", "Refused", "Prefer not to say", "Unknown"
##-> NA): cov_age, cov_gender, cov_social_grade (chief income earner), cov_region, cov_voted_ge_2019,
##cov_vote_ge_2019 (party voted for; a vote, not party ID; NA if not asked), cov_vote_euref,
##cov_house_tenure, cov_education (profile_education_level), cov_trust_uk_government,
##cov_trust_uk_civil_service (q1_1/q1_2), cov_aid_spending_good (q2), cov_fcdo_treatment (q4_split:
##"control" = plain FCDO question, "transparency" = transparency text), cov_fcdo_support (q4_1, 1-10).
##cov_survey_weight = W8 (YouGov post-stratification weight, used in the article's main models).
##Dropped: the authors' rescaled trust/aid variables (treatment, uk_govtrust, uk_civtrust,
##spending_good). Identity is a sequential case number (kept as id). No PII.
##N = 2,058 matches the article. Spot check in the return.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "DOTRAN_experiment.dta"))
stopifnot(nrow(s) == 2058, !anyDuplicated(s$Identity))
na_codes <- c("Skipped", "Not Asked", "Refused", "Prefer not to say", "Unknown")
txt <- function(v) { x <- as.character(as_factor(s[[v]], levels = "labels")); x[x %in% na_codes] <- NA; x }
cv <- data.table(id = as.integer(s$Identity))
cv[, cov_age := as.integer(s$age)]
stopifnot(all(s$profile_gender %in% 1:2), all(cv$cov_age >= 18))
cv[, cov_gender := c("male", "female")[as.integer(s$profile_gender)]]
cv[, `:=`(cov_social_grade = txt("profile_socialgrade_cie"), cov_region = txt("profile_GOR"),
          cov_voted_ge_2019 = txt("voted_ge_2019"), cov_vote_ge_2019 = txt("pastvote_ge_2019"),
          cov_vote_euref = txt("pastvote_EURef"), cov_house_tenure = txt("profile_house_tenure"),
          cov_education = txt("profile_education_level"), cov_trust_uk_government = txt("q1_1"),
          cov_trust_uk_civil_service = txt("q1_2"), cov_aid_spending_good = txt("q2"))]
stopifnot(all(s$q4_split %in% 1:2), all(s$q4_1 %in% 1:10))
cv[, cov_fcdo_treatment := c("control", "transparency")[as.integer(s$q4_split)]]
cv[, cov_fcdo_support := as.integer(s$q4_1)]
cv[, cov_survey_weight := as.numeric(s$W8)]
cv[, trial_question_order := s$q1_q5_ord]
build <- function(attrs, suffix, rv, name) {
  d <- rbindlist(lapply(1:2, function(p) {
    x <- data.table(id = cv$id, task = 1L, profile = p, rating = as.integer(s[[paste0(rv, "_", p)]]))
    for (k in seq_along(attrs)) {
      v <- as.integer(s[[sprintf("q_attr%d_concept%d_task1%s", k, p, suffix)]])
      stopifnot(all(v %in% 1:2))
      x[, paste0("attr_", attrs[k]) := c("Yes", "No")[v]]
    }
    x }))
  stopifnot(all(d$rating %in% 1:10))
  d <- merge(d, cv, by = "id")
  setcolorder(d, c("id", "task", "profile", "rating", paste0("attr_", attrs), "trial_question_order"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
build(c("strategy", "decision_making", "structure", "operational_costs", "staff", "project"), "_C2", "q5",
      "heinzel_2024_aid_transparency")
build(c("transparency", "anti_corruption", "allies", "poverty", "human_rights", "climate", "coordination"), "", "q3",
      "heinzel_2024_aid_reforms")
