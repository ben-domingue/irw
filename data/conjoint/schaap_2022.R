##Expert-vs-algorithm factorial vignettes (UK Prolific) from
##Schaap, G., Bosse, T., & Hendriks Vettehen, P. (2022). How much for your agency? Users trade off
##decisional control and optimal outcomes in choosing between AI and human decision-makers. Paper
##presented at the 72nd Annual ICA Conference, Paris, 26-30 May 2022 (no DOI).
##Data: OSF project pk589 ("Part 1: direct choice trade-off"), https://osf.io/pk589/, CC BY 4.0
##(node licence), no restricted files.
##Files read: "DATA SET STUDY 1_stock market - N=211.sav" and "DATA SET STUDY 3_dating - N=210.sav".
##Level text and question wording: "QUESTIONNAIRE STUDY 1.docx", "QUESTIONNAIRE STUDY 3.docx",
##"16 conditions.docx", "Condition 1 HNL AINL.docx" (Measures & Materials) and the ICA paper pdf
##(same node). Study 2 (4 conditions) is not in this deposit.
##Usage: Rscript schaap_2022.R <raw dir> <output dir>
##
##Design (paper, "Method"): a 2 x 2 x 2 x 2 between-subjects vignette experiment. Each respondent
##read one scenario (Qualtrics block randomizer FL_12, one of 16 blocks) offering two packages:
##an expert (Option A) and an algorithm (Option B). For each the scenario stated the benefit
##(Study 1, stock investing: estimated profit 3% or 21% return; Study 3, online dating: a match of
##75% or 95%) and the kind of assistance (no control: "the decision is made for you ..." / "a date is
##selected for you ..."; control: "you have (the) final say over the decision ..."), shown as prose
##screens and then a summary table. So one profile per respondent (task 1, profile 1) with four
##randomized factors: attr_expert_benefit, attr_expert_control, attr_algorithm_benefit,
##attr_algorithm_control. Levels from the block names (H/AI x Y/N control x L/H benefit), checked
##block by block against the questionnaire screens Q*.4/Q*.5 (all 16 blocks, both studies) and
##against the authors' CONDITION and Factor_* columns. Benefit levels stored as the displayed
##percentages ("3%", "21%" / "75%", "95%"); control levels as the displayed sentences (first letter
##capitalised; on screen they followed "If you select the expert/algorithm,").
##TWO TABLES (separate studies, samples and scenario text; the paper analyses them separately):
##  schaap_2022_ai_agency_stocks (Study 1, n = 211), schaap_2022_ai_agency_dating (Study 3, n = 210).
##Outcomes (both studies):
##  rating: "Reviewing the options above, which would you choose to assist you?" 1 = Definitely the
##    expert .. 7 = Definitely the algorithm (Q*.6_1; the authors' CHOICE). Stored raw.
##  rating_agent: "If you merely had to choose between either the expert or the algorithm, which would
##    you choose?" 1 = The expert, 2 = The algorithm (Q*.8; the authors' CHOICE_BIN). Stored raw as a
##    rating because the table has one profile (the offer), not one profile per agent.
##No opt-out. Restrictions: none (full factorial, paper "16 decision scenarios"); level weights not
##stated (Qualtrics evenly-present block randomizer is not documented; cells 10-14 per study).
##trial_mc_benefit / trial_mc_control: the two manipulation checks (Q*.9 algorithm's benefit, Q*.10
##expert's control) as answer text. Paper: respondents who failed them were replaced (N = 13 in
##Study 1); the deposited files are the final samples.
##Covariates: cov_gender (1 Male / 2 Female; 3 "Other/don't want to tell" mixes other and refusal and is
##set to NA), cov_birth_year (Q18.2), cov_age (authors' Age/AGE, computed by them from year of birth),
##cov_education (value-label text), cov_background_cs, cov_background_finance (Yes/No text, Q18.7/Q18.8),
##cov_computer_1..6 (Q18.1_1..6, "How do you feel about computers?" 1 = Strongly agree .. 5 = Strongly
##disagree: confident and relaxed / the harder I work the more confused I get / too old to learn /
##"Computers don't like me" / always have problems / can solve problems by myself), cov_duration_sec
##(whole survey, Qualtrics Duration).
##Dropped: free-text reasons (Q*.7), nationality and first language (free text), Qualtrics dates and
##status, the authors' derived variables (CONDITION, Factor_*, scenario_*, CHOICE, CHOICE_BIN,
##Mancheck*, recodes, Comp_anxiety, z-scores, Rationale). No Prolific ID or IP in the files.
##No survey weight. N = 211 and 210 match the paper. Spot check in the return (cell means by AI benefit).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(file, ben, ctl, gvar, evar, agevar, name) {
  s <- read_sav(file.path(raw, file))
  fl <- grep("^FL_12_DO_Scenario", names(s), value = TRUE)
  stopifnot(length(fl) == 16, all(rowSums(!is.na(as.matrix(s[, fl]))) == 1))
  k <- apply(as.matrix(s[, fl]), 1, function(r) which(!is.na(r)))
  code <- sub(".*Scenario[0-9]+_+", "", fl)[k]               # e.g. HNLAINL
  stopifnot(all(grepl("^H[YN][LH]AI[YN][LH]_?$", code)), all(k == as.integer(s$CONDITION)))
  stopifnot(all((substr(code, 7, 7) == "H") == (as.integer(s$Factor_BENEFITS_AI) == 2)),
            all((substr(code, 6, 6) == "Y") == (as.integer(s$Factor_Control_AI) == 2)))
  q <- k + 1L                                                  # scenario k = questionnaire block Q(k+1)
  pick <- function(suffix) sapply(seq_len(nrow(s)), function(i) as.integer(s[[paste0("Q", q[i], suffix)]][i]))
  r7 <- pick(".6_1"); r2 <- pick(".8"); m1 <- pick(".9"); m2 <- pick(".10")
  stopifnot(all(r7 %in% 1:7), all(r2 %in% 1:2), all(m1 %in% 1:2), all(m2 %in% 1:2))
  d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L, rating = r7, rating_agent = r2,
                  attr_expert_benefit = ifelse(substr(code, 3, 3) == "H", ben[2], ben[1]),
                  attr_expert_control = ifelse(substr(code, 2, 2) == "Y", ctl[2], ctl[1]),
                  attr_algorithm_benefit = ifelse(substr(code, 7, 7) == "H", ben[2], ben[1]),
                  attr_algorithm_control = ifelse(substr(code, 6, 6) == "Y", ctl[2], ctl[1]))
  lab <- function(v) { x <- as_factor(s[[v]]); as.character(x) }
  d[, trial_mc_benefit := ben[m1]]
  d[, trial_mc_control := names(attr(s[["Q2.10"]], "labels"))[m2]]
  g <- as.integer(s[[gvar]]); stopifnot(all(g %in% 1:3))
  d[, cov_gender := c("male", "female", NA)[g]]
  d[, cov_birth_year := as.integer(s$Q18.2)]
  d[, cov_age := as.integer(s[[agevar]])]
  d[, cov_education := lab(evar)]
  d[, cov_background_cs := lab("Q18.7")][, cov_background_finance := lab("Q18.8")]
  for (j in 1:6) d[, paste0("cov_computer_", j) := as.integer(s[[paste0("Q18.1_", j)]])]
  d[, cov_duration_sec := as.integer(s$Duration__in_seconds_)]
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
nc <- "The decision is made for you. The choice which investments to make will be made automatically. You cannot influence the decision. The sum will automatically be transferred from your bank account."
yc <- "You have the final say over the decision. You will be advised which investments to make. You may choose to follow the advice or not. You may or may not give permission to transfer the sum from your bank account. It is up to you."
build("DATA SET STUDY 1_stock market - N=211.sav", c("3%", "21%"), c(nc, yc), "Gender", "Education", "Age",
      "schaap_2022_ai_agency_stocks")
nc3 <- "A date is selected for you. The selection will be made automatically. You cannot influence the selection. A meeting will automatically be set up for you and your date."
yc3 <- "You have final say over the decision. You will be advised which potential date matches you best. You may choose to follow this advice or not. You may or may not give permission to set up a meeting between you and your date. It is up to you."
build("DATA SET STUDY 3_dating - N=210.sav", c("75%", "95%"), c(nc3, yc3), "Q18.3", "Q18.6", "AGE",
      "schaap_2022_ai_agency_dating")
