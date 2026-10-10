##Income equality / mobility paired-society choice experiment (US, MTurk) from
##Lara E., B., & Shores, K. A. (2024). Measuring preferences for income equality and income
##mobility. Review of Economics and Statistics, 106(6), 1542-1557.
##https://doi.org/10.1162/rest_a_01240
##Replication data: Harvard Dataverse doi:10.7910/DVN/QRQNCF, CC0 1.0, no restricted files.
##Files read: full_sampleRR_uniwts.dta and preferred_sampleRR_uniwts.dta (Dataverse "original
##format" downloads of the .tab files). Design facts, level formats and wording from README.txt,
##"replication code all tables and figures_8.3.2022.do" (read as text) and the accepted
##manuscript (UDSpace copy, CC BY 4.0: sections 3-4, Table 1 "Randomization values used").
##The survey screens themselves (appendix screenshots, bit.ly link) were not read.
##Usage: Rscript lara_2024.R <raw dir> <output dir>
##
##MTurk respondents in the US (May-July 2021, two-stage quota sample). After a training section
##each chose, four times (task = the source's `question` 1-4), between two hypothetical
##societies, Society A (profile 1) and Society B (profile 2), each described by four
##independently randomized attributes, drawn from nine values each (Table 1):
##  attr_bottom20_income "Bottom 20% income": $10,000 .. $23,000
##  attr_middle60_income "Middle 60% income": $41,000 .. $76,000
##  attr_top20_income "Top 20% income": $126,000 .. $209,000
##  attr_mobility "Income Mobility" (share of children from the bottom 20% who leave it as
##     adults): 62% .. 80%
##Level text follows the manuscript's Table 1 format ($ with thousands separator, %); the deposit
##stores thousands of dollars and percentage points. The screens also showed each society's
##average income and 90/10 income ratio, computed from the four incomes; they are not stored as
##attributes (exact display format not deposited; the deposit's avgincsoc*/iirsoc* are rounded).
##Attribute order: randomized once per respondent (mobility first or incomes first, manuscript
##3.2); not recorded in the deposit.
##choice: the society chosen; forced choice, no opt-out. SOCIETY LABELS ARE SWAPPED IN THE SOURCE:
##the README says response_q = 1 "if the respondent chose society A over society B" and that the
##predictors are log ratios "where the numerator is for society A", but in the data avginc_q,
##mob_q, p10inc_q ... equal log(socB/socA) of the columns labelled "society A"/"society B"
##(correlation -1), and where the "socA" columns dominate (higher on every attribute) response_q
##is 1 only 13% of the time. Both README statements agree with each other if the columns labelled
##"socB" hold Society A, so profile 1 (Society A) is built from the *socB* columns and choice =
##response_q on it. Which profile was chosen is certain either way (the authors' estimates
##reproduce); the left/right position is inferred (profile_source = inferred).
##Wording of the choice question is not in the deposit or the manuscript text (paraphrase:
##"choose between two hypothetical societies, A and B").
##trial_framing: each task header said "distant society" (a society you will never participate
##in; source veiled = 1, 80%) or "nearby society" (one you or someone you know might live in;
##veiled = 0), assigned per respondent (manuscript 3.2).
##Sample: the full-sample file (1,458 respondents) is the deposit's superset: the main analyses
##use the preferred sample of 1,249 (quota filled), the full sample adds 209 who responded after
##the quota was filled (README). The two files carry different respondent ids; the preferred
##respondents are identified by matching each respondent's 32 attribute values and 4 choices
##(unique in both files; all 1,249 match, durations agree): cov_preferred_sample = 1.
##Weights: cov_survey_weight = the full-sample raked weight (rakedwgt in the full file, quota
##margins, README); cov_weight_preferred = the raked weight of the main analyses (preferred file;
##NA for the extra 209).
##Covariates (from the deposit's labelled dummies and variables): cov_gender (gender_male/
##gender_female), cov_race (race_white/black/hispanic/other: White / Black / Hispanic / Other;
##the screener categories, manuscript 4), cov_party_id (party_dem/rep/ind: Democrat / Republican /
##Independent), cov_education (educ_* dummy labels: No education degree, Maximum degree is High
##School, Incomplete higher education, 2 year degree higher education, 4 year degree higher
##education, More than 4 year degree in higher education; 13 respondents with none set are NA),
##cov_age (age_alt, years), cov_household_income and cov_personal_income (dollars, bracket
##values as deposited), cov_past_mobility (past, "Has experienced income mobility", -2..2),
##cov_future_mobility (future, "Believes that will experience mobility", -2..2),
##cov_belief_mobility_common (belief_mob, 1-4), cov_diag_pctright (share of the four training
##diagnostic questions answered correctly), cov_duration_sec (survey duration). The meaning of
##the -2..2 and 1-4 codes is not documented beyond the variable labels.
##Dropped: the authors' log-ratio predictors (*_q ratios), avgincsoc*/iirsoc*, the per-row
##diag_q, the adaptive-questionnaire results (mobadapt, incineqadapt, *MRS: a separate adaptive
##staircase, not a randomized conjoint), quota group codes and age-band dummies, merge flags.
##N: 1,458 respondents x 4 tasks x 2 profiles = 11,664 rows; 1,249 preferred as in the article.
##Spot check: weighted probit of the choice on the log A/B ratios of average income, mobility and
##90/10 ratio (computed from this table, preferred sample, preferred weights, 4,996 tasks) gives
##MRS 2.738 for the income-inequality ratio and 1.224 for mobility; the article's Table 3 has 2.744
##and 1.228 (the authors' ratios use the displayed, unrounded averages).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "full_sampleRR_uniwts.dta")))
p <- as.data.table(read_dta(file.path(raw, "preferred_sampleRR_uniwts.dta")))
sig <- function(x) { x <- copy(x); setorder(x, id, question)
  x[, .(s = paste(p10socA_q, p50socA_q, p90socA_q, mobsocA_q, p10socB_q, p50socB_q, p90socB_q, mobsocB_q, response_q, collapse = "|"),
        w = rakedwgt[1], dur = durationinseconds[1]), id] }
sk <- sig(k); sp <- sig(p)
stopifnot(!anyDuplicated(sk$s), !anyDuplicated(sp$s), all(sp$s %in% sk$s))
mm <- merge(sk, sp[, .(s, wp = w, durp = dur)], by = "s", all.x = TRUE)
stopifnot(mm[!is.na(durp), all(dur == durp)])
stopifnot(k[, .N, id][, all(N == 4)], !anyDuplicated(k[, .(id, question)]), all(k$response_q %in% 0:1))
k[, rid := as.integer(factor(id, levels = unique(id)))]
usd <- function(x) paste0("$", formatC(as.numeric(x) * 1000, format = "d", big.mark = ","))
# Society A (profile 1) is held in the *socB* columns and Society B in *socA* (see header)
stopifnot(cor(k$mob_q, log(k$mobsocB_q / k$mobsocA_q)) > 0.999, cor(k$p50inc_q, log(k$p50socB_q / k$p50socA_q)) > 0.999)
side <- function(s) {
  data.table(id = k$rid, task = as.integer(k$question), profile = if (s == "B") 1L else 2L,
             choice = if (s == "B") as.integer(k$response_q) else 1L - as.integer(k$response_q),
             attr_bottom20_income = usd(k[[paste0("p10soc", s, "_q")]]), attr_middle60_income = usd(k[[paste0("p50soc", s, "_q")]]),
             attr_top20_income = usd(k[[paste0("p90soc", s, "_q")]]), attr_mobility = paste0(k[[paste0("mobsoc", s, "_q")]], "%"),
             src = k$id)
}
d <- rbind(side("B"), side("A"))
lev <- list(attr_bottom20_income = usd(c(10, 11, 13, 14, 15, 16, 17, 19, 23)), attr_middle60_income = usd(c(41, 48, 52, 56, 59, 62, 66, 70, 76)),
            attr_top20_income = usd(c(126, 138, 148, 156, 163, 170, 182, 196, 209)), attr_mobility = paste0(c(62, 64, 65, 67, 68, 70, 72, 75, 80), "%"))
for (v in names(lev)) stopifnot(setequal(unique(d[[v]]), lev[[v]]))
r <- k[match(d$src, k$id)]
oh <- function(cols, labs) { m <- as.matrix(r[, cols, with = FALSE]); stopifnot(all(rowSums(m) <= 1))
  out <- rep(NA_character_, nrow(m)); for (j in seq_along(cols)) out[m[, j] == 1] <- labs[j]; out }
d[, `:=`(trial_framing = fifelse(r$veiled == 1, "distant society", "nearby society"),
         cov_preferred_sample = as.integer(d$src %in% mm[!is.na(durp), id]),
         cov_survey_weight = as.numeric(r$rakedwgt),
         cov_weight_preferred = mm$wp[match(d$src, mm$id)],
         cov_gender = oh(c("gender_male", "gender_female"), c("male", "female")),
         cov_race = oh(c("race_white", "race_black", "race_hispanic", "race_other"), c("White", "Black", "Hispanic", "Other")),
         cov_party_id = oh(c("party_dem", "party_rep", "party_ind"), c("Democrat", "Republican", "Independent")),
         cov_education = oh(c("educ_none", "educ_hs", "educ_somecoll", "educ_2yr", "educ_4yr", "educ_4yrplus"),
                            c("No education degree", "Maximum degree is High School", "Incomplete higher education",
                              "2 year degree higher education", "4 year degree higher education", "More than 4 year degree in higher education")),
         cov_age = as.integer(r$age_alt), cov_household_income = as.numeric(r$inc), cov_personal_income = as.numeric(r$personalinc),
         cov_past_mobility = as.integer(r$past), cov_future_mobility = as.integer(r$future),
         cov_belief_mobility_common = as.integer(r$belief_mob), cov_diag_pctright = as.numeric(r$diag_pctright),
         cov_duration_sec = as.numeric(r$durationinseconds))]
stopifnot(sum(d[, .N, cov_preferred_sample][cov_preferred_sample == 1, N]) == 1249 * 8,
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, uniqueN(trial_framing), id][, all(V1 == 1)])
d[, src := NULL]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lara_2024_equality_mobility.csv"))
