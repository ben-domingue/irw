##Incentivized expert-vs-algorithm factorial vignette (UK Prolific) from
##Schaap, G., Bosse, T., & Hendriks Vettehen, P. (2023). How users trade off agency and benefits in
##accepting AI vs human decision-makers. Part 2: Direct choice - incentivized interaction [Data set].
##OSF component 7ft2s of project nwqgs, https://osf.io/7ft2s/ (parent https://osf.io/nwqgs/),
##CC BY 4.0 (node licence), no restricted files. No publication found for this study.
##Files read: "DATA SET STUDY 2_interaction - N=210.sav" (7ft2s Data and Syntax; the same file is in
##the nwqgs "Data and Syntax" folder). Level text and question wording from QUESTIONNAIRE.docx and
##STIMULUS MATERIAL.docx (7ft2s Measures & materials); "Syntax variable construction.sps" read as text.
##Usage: Rscript schaap_2023.R <raw dir> <output dir>
##
##RELATION TO schaap_2022_ai_agency_stocks / _dating (built from OSF pk589, the other component of
##nwqgs, by data/conjoint/schaap_2022.R): Studies 1 and 3 of nwqgs are those tables. This deposited
##"Study 2_interaction" is NOT the Study 2 of the ICA 2022 paper (that study had 4 conditions, 74%
##female, M = 3.88); this one has all 16 conditions, 50% female, M = 4.10, and was fielded on
##2023-06-09 with real money: each respondent got GBP 1 to invest in a 1-minute "scalping" stock
##trade, profit or loss added to the GBP 1.20 Prolific fee.
##Design: 2 x 2 x 2 x 2 between subjects, one scenario per respondent (Qualtrics block randomizer
##FL_28, one of 16 blocks, cells 11-15). Each scenario offered two packages, Option A = the expert,
##Option B = the algorithm, each with an estimated profit ("If you select the expert/algorithm, your
##profit is estimated at 3% / 21% return on your investment") and a control level. Levels from the
##block names (H/AI x Y/N control x L/H benefit), checked block by block against the questionnaire
##screens (all 16) and the authors' Factor_* columns. Stored as one profile per respondent (task 1,
##profile 1) with four factors, as in schaap_2022.R:
##  attr_expert_benefit, attr_algorithm_benefit: "3%" / "21%"
##  attr_expert_control, attr_algorithm_control: the displayed headline of the control bullet,
##    "No control. The investment will be made for you automatically" (continued: "If you select the
##    expert/algorithm, the investment is made for you. The investment of your £1 will be made
##    automatically. You cannot influence this decision.") or "You have control. You will be able to
##    decide whether to make the investment" (continued: "If you select the expert/algorithm, you have
##    the final say over the decision. You may choose to follow through on the investment or not. You
##    may or may not give permission to invest your £1. It is up to you.").
##Outcomes (in the order asked):
##  rating_agent: "Select your option ... Please choose your option now" 1 = Option A: Expert,
##    2 = Option B: Algorithm (the incentivized pick; authors' CHOICE_BIN). Stored raw as a rating, as
##    in schaap_2022 (one profile per respondent).
##  rating: "Reviewing the options above, please tell us how strongly you prefer one option over the
##    other for this investment." 1 = I definitely prefer the expert .. 7 = I definitely prefer the
##    algorithm (authors' CHOICE).
##  rating_invest: asked only when the picked agent offered control (108 respondents; NA otherwise):
##    "The investor predicts an 18% rise in stocks of a company called 'XPDA International Group'
##    within the next minutes. Please indicate whether you agree with making the proposed
##    investment." 1 = BUY!, 8 = ABORT! (source codes kept; authors' abortbuy).
##No opt-out. trial_mc_benefit / trial_mc_control: manipulation checks Q17.9 (algorithm's profit) and
##Q17.10 (expert's control) as answer text; all 210 answered both correctly.
##Covariates: cov_gender (Q18.3: 1 Male, 2 Female; 3 "Other/don't want to tell" mixes other and refusal
##-> NA, as in schaap_2022), cov_birth_year (Q18.2, free text: 4-digit years kept; two answers typed as
##full dates of birth are reduced to their year, the dates are not stored), cov_education (Q18.6 text),
##cov_background_cs (Q18.7), cov_background_finance (Q18.8), cov_duration_sec (Qualtrics Duration,
##whole survey).
##Dropped: PROLIFIC_PID (platform ID, present in the deposited .sav), nationality and first language
##(free text), consent, StartDate, Qualtrics randomizer and the authors' derived variables (scenario_*,
##CONDITION, Factor_*, abortbuy, CHOICE, CHOICE_BIN, z-scores). Respondent id = row order of the .sav.
##No survey weight. N = 210 = file name; no paper to compare.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_sav(file.path(raw, "DATA SET STUDY 2_interaction - N=210.sav"))
fl <- grep("^FL_28_DO_Scenario", names(s), value = TRUE)
stopifnot(length(fl) == 16, all(rowSums(!is.na(as.matrix(s[, fl]))) == 1))
k <- apply(as.matrix(s[, fl]), 1, function(r) which(!is.na(r)))
code <- sub(".*Scenario[0-9]+", "", fl)[k]                       # e.g. HNLAINL
stopifnot(all(grepl("^H[YN][LH]AI[YN][LH]$", code)), all(k == as.integer(s$CONDITION)))
stopifnot(all((substr(code, 7, 7) == "H") == (as.integer(s$Factor_BENEFITS_AI) == 2)),
          all((substr(code, 6, 6) == "Y") == (as.integer(s$Factor_Control_AI) == 2)),
          all((substr(code, 3, 3) == "H") == (as.integer(s$Factor_BENEFITS_HUMAN) == 2)),
          all((substr(code, 2, 2) == "Y") == (as.integer(s$Factor_Control_HUMAN) == 2)))
# questionnaire variable names per scenario block 1..16: pick, 7-point, buy/abort
pickv <- c("Q33", "Q37", "Q41", "Q7", "Q45", "Q49", "Q53", "Q57", "Q61", "Q65", "Q69", "Q73", "Q77", "Q81", "Q85", "Q89.0")
ratev <- c("Q34_1", "Q38_1", "Q42_1", "Q8_1", "Q46_1", "Q50_1", "Q54_1", "Q58_1", "Q62_1", "Q66_1", "Q70_1", "Q74_1",
           "Q78_1", "Q82_1", "Q86_1", "Q90_1")
buyv <- c(NA, NA, "Q10", "Q86", NA, NA, "Q87", "Q88", "Q89", "Q90", "Q92", "Q93", "Q94", "Q95", "Q96", "Q97")
get <- function(vars) sapply(seq_len(nrow(s)), function(i) if (is.na(vars[k[i]])) NA_integer_ else as.integer(s[[vars[k[i]]]][i]))
r2 <- get(pickv); r7 <- get(ratev); rb <- get(buyv)
stopifnot(all(r2 %in% 1:2), all(r7 %in% 1:7), all(rb %in% c(1L, 8L, NA)),
          all(r2 == as.integer(s$CHOICE_BIN)), all(r7 == as.integer(s$CHOICE)),
          identical(is.na(rb), is.na(s$abortbuy)))
ben <- c("3%", "21%")
ctl <- c("No control. The investment will be made for you automatically",
         "You have control. You will be able to decide whether to make the investment")
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L, rating = r7, rating_agent = r2, rating_invest = rb,
                attr_expert_benefit = ifelse(substr(code, 3, 3) == "H", ben[2], ben[1]),
                attr_expert_control = ifelse(substr(code, 2, 2) == "Y", ctl[2], ctl[1]),
                attr_algorithm_benefit = ifelse(substr(code, 7, 7) == "H", ben[2], ben[1]),
                attr_algorithm_control = ifelse(substr(code, 6, 6) == "Y", ctl[2], ctl[1]))
lab <- function(v) as.character(as_factor(s[[v]]))
m1 <- as.integer(s$Q17.9); m2 <- as.integer(s$Q17.10); stopifnot(all(m1 %in% 1:2), all(m2 %in% 1:2))
d[, trial_mc_benefit := ben[m1]]
d[, trial_mc_control := c("No control over the investment", "Control over the investment")[m2]]
g <- as.integer(s$Q18.3); stopifnot(all(g %in% 1:3))
d[, cov_gender := c("male", "female", NA)[g]]
by <- as.integer(sub(".*([12][0-9]{3})$", "\\1", trimws(as.character(s$Q18.2))))
by[!(by %in% 1900:2010)] <- NA
d[, cov_birth_year := by]
d[, cov_education := lab("Q18.6")]
d[, cov_background_cs := lab("Q18.7")][, cov_background_finance := lab("Q18.8")]
d[, cov_duration_sec := as.integer(s$Duration__in_seconds_)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "schaap_2023_ai_agency_incentivized.csv"))
