##Discrete choice experiment on incentives for family-based childhood-obesity treatment (US)
##from Wright, D. R., Saelens, B. E., Fontes, A., & Lavelle, T. A. (2019). Assessment of
##parents' preferences for incentives to promote engagement in family-based childhood obesity
##treatment. JAMA Network Open, 2(3), e191490. https://doi.org/10.1001/jamanetworkopen.2019.1490
##Replication data: Harvard Dataverse doi:10.7910/DVN/NR4USF, CC0 1.0, no restricted files.
##Files read: lion_dce_all_final.dta (original format of the .tab; Stata value labels give the
##attribute text), LION_Codebook_11_26_18.xlsx (question wording, answer codes, the attribute
##sentences as inserted in Q6_t), LION_DiscreteChoiceDesign.csv (original of the design xlsx:
##30 versions x 10 tasks x 2 concepts), LION_DCE.ssi (Sawtooth Lighthouse study file, read as
##text for attribute names and level text).
##Usage: Rscript wright_2019.R <raw dir> <output dir>
##
##305 parents of children aged 6-17 with obesity, nationally representative web panel survey,
##March 2018 (abstract). 10 tasks of 2 hypothetical incentive programmes ("Reward A" = profile
##1, "Reward B" = profile 2), 4 attributes. Fixed blocked design: a fractional factorial in 30
##versions of 10 tasks each. Every respondent's 20 profiles equal exactly one version of the
##design file (checked); trial_version = that design-file version. The .dta's DC_VERSION is a
##one-to-one relabelling of it (DC_VERSION 2 = version 10, 3 = 11, ...: the versions sorted as
##text), so it is not stored. Level shares in the table are near-equal (value levels 16-17%).
##Outcome: choice, Q6_t "Prefer Reward A" / "Prefer Reward B"; wording varies by task (task 1:
##"We want to know which of the two rewards would motivate you more in a family-based weight
##management program. There are no right or wrong answers."; the others in design_outcomes
##evidence). No "none" option was offered (the Lighthouse NONE text is unused); DON'T KNOW /
##SKIPPED / REFUSED codes exist but never occur. Forced choice, no opt-out.
##Attribute text (codebook = .dta value labels):
##  attr_payment_structure: "You start with nothing and earn points for each goal you meet, up
##    to [total value] worth of points" / "You start with [total value] worth of points and lose
##    points for each goal you do not meet". On screen the bracket held the profile's own value
##    (the codebook pipes [TASKt_CONCEPTmB]); it is written "[total value]" here so the
##    attribute keeps 2 levels.
##  attr_total_value ("Total value of the reward over 6 months"): $150 $220 $290 $360 $430 $500.
##  attr_goal ("Goal that is being rewarded"): "Daily calorie tracking through a food diary or
##    app like My Fitness Pal", "Weekly physical activity time, measured using a Fitbit or
##    smartwatch", "Change in weight".
##  attr_who_meets_goal ("Who has to meet goal"): Child / Parent and child.
##Covariates (codebook / .dta value-label text): cov_survey_weight (WEIGHT1, the sampling
##weight, mean 1; `WEIGHT` in the .dta is the child's weight in pounds and is dropped),
##cov_gender (parent_gender Male/Female -> male/female), cov_age (AGE, parent's age in years),
##cov_education (EDUC label text), cov_race_ethnicity (RACETHNICITY), cov_marital, cov_employment,
##cov_income, cov_state (postal code), cov_metro (METRO), cov_household_size (HHSIZE),
##cov_device (Device), cov_duration_sec (duration, minutes in the codebook, x 60), cov_child_age
##(Q1_AGE, years), cov_child_sex (Q1_SEX "What sex was this child assigned at birth?"),
##cov_child_weight_perceived (Q8), cov_feeding_responsibility (Q13), cov_cfq_a..h (Q9A-H,
##1 = Disagree .. 5 = Agree; 98 SKIPPED -> NA; statements in the codebook).
##Dropped: CaseId (panel case ID; re-keyed 1-305 in file order), free text Q10_6OE / Q11_5OE,
##child height and weight (Q2A/Q2B, HEIGHT, WEIGHT, BMI; BMI_PCTL is 1 for all), the warm-up
##choices Q3/Q4 (their profiles are not in the data), the lottery questions Q7 and the authors'
##derived variables (frame_*, value*, goal_*, target_*, importance_*, cfq, certain*, rlh,
##parent_bmi*, *_tx, child_race, parent_race, income, AGE7, EDUC4, parent_age, region codes).
##N: 305 respondents in the deposit; the article reports 304 completes (89.7% of 339).
##Spot check: with cov_survey_weight, 53% are White non-Hispanic and 28% hold a bachelor's
##degree or more (article: 53.3%, 28.3%); 45% report household income under $50,000 (42.6%).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "lion_dce_all_final.dta"))
dz <- fread(file.path(raw, "LION_DiscreteChoiceDesign.csv"))
setnames(dz, c("version", "task", "concept", "A", "B", "C", "D"))
stopifnot(nrow(k) == 305, nrow(dz) == 600)
lt <- function(x) as.character(as_factor(x, levels = "labels"))
k$id <- seq_len(nrow(k))
rows <- list()
for (t in 1:10) for (p in 1:2) {
  v <- function(x) k[[sprintf("TASK%d_CONCEPT%d%s", t, p, x)]]
  ch <- as.integer(zap_labels(k[[sprintf("Q6_%d", t)]]))
  stopifnot(all(ch %in% 1:2))
  rows[[length(rows) + 1]] <- data.table(id = k$id, task = t, profile = p, choice = as.integer(ch == p),
                  attr_payment_structure = sub("\\[TASK[0-9]+_CONCEPT[12]B\\]", "[total value]", lt(v("A"))),
                  attr_total_value = lt(v("B")), attr_goal = lt(v("C")), attr_who_meets_goal = lt(v("D")),
                  sig = paste(as.integer(v("A")), as.integer(v("B")), as.integer(v("C")), as.integer(v("D"))))
}
d <- rbindlist(rows)
# each respondent's 20 profiles equal exactly one version of the design file
dsig <- dz[order(version, task, concept), .(s = paste(paste(A, B, C, D), collapse = "|")), version]
rsig <- d[order(id, task, profile), .(s = paste(sig, collapse = "|")), id]
rsig[, version := dsig$version[match(s, dsig$s)]]
stopifnot(!anyNA(rsig$version), rsig[, uniqueN(as.integer(k$DC_VERSION)[id]), version][, all(V1 == 1)])
d <- merge(d, rsig[, .(id, trial_version = version)], by = "id")
d[, sig := NULL]
for (x in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[x]]))
stopifnot(uniqueN(d$attr_payment_structure) == 2, d[, sum(choice), .(id, task)][, all(V1 == 1)])
na_codes <- function(x, bad) { x <- as.integer(zap_labels(x)); x[x %in% bad] <- NA; x }
txt <- function(x, bad = c(77, 98, 99)) { y <- lt(x); y[as.integer(zap_labels(x)) %in% bad] <- NA; y }
stopifnot(all(k$parent_gender %in% 1:2))
cv <- data.table(id = k$id, cov_survey_weight = as.numeric(k$WEIGHT1),
  cov_gender = c("male", "female")[as.integer(k$parent_gender)], cov_age = as.integer(k$AGE),
  cov_education = lt(k$EDUC), cov_race_ethnicity = lt(k$RACETHNICITY), cov_marital = lt(k$MARITAL),
  cov_employment = lt(k$EMPLOY), cov_income = lt(k$INCOME), cov_state = lt(k$STATE), cov_metro = lt(k$METRO),
  cov_household_size = as.integer(k$HHSIZE), cov_device = lt(k$Device), cov_duration_sec = as.numeric(k$duration) * 60,
  cov_child_age = na_codes(k$Q1_AGE, c(77, 98, 99)), cov_child_sex = txt(k$child_gender),
  cov_child_weight_perceived = txt(k$Q8), cov_feeding_responsibility = txt(k$Q13))
for (q in LETTERS[1:8]) cv[, paste0("cov_cfq_", tolower(q)) := na_codes(k[[paste0("Q9", q)]], 98)]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wright_2019_obesity_incentives.csv"))
