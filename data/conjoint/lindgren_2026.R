##Fuel- and meat-rationing policy-design conjoints (Sweden) from
##Lindgren, O., Jagers, S. C., & Lindvall, D. (2026). The impact of policy design on opposition to
##restrictive climate policies. Ecological Economics, 240. https://doi.org/10.1016/j.ecolecon.2025.108813
##Replication data: Harvard Dataverse doi:10.7910/DVN/E1FBRQ, CC0 1.0. Files read:
##conjoint_exp_DATA_LONG.dta (value labels used for all level text) and "Replication code.do" (read as
##text, not run). No codebook or questionnaire is deposited.
##Usage: Rscript lindgren_2026.R <dir holding the .dta> <output dir>
##
##3,247 Swedish adults (web panel; the Swedish variable labels are the questionnaire's), each did TWO
##paired conjoints in random block order (hidblockorder: 1 fuel block first, 2 red-meat block first):
##5 pairs of proposals to ration petrol/diesel and 5 pairs of proposals to ration red meat. The two
##experiments have different stringency levels (litres vs kg per month) and are analysed separately
##in the paper (Fig. 1 left/right), so they are TWO tables: lindgren_2026_fuel_rationing and
##lindgren_2026_meat_rationing. Each source row is one profile of round `pairing` (1-5) in BOTH
##experiments; task = pairing (labelled "Choice round"), profile = order of the two rows within the
##round (the deposit's running index `new`; left/right is not labelled, so profile is inferred).
##Attributes (English value labels of f_* / b_*; respondents saw Swedish, cf. the q11 labels
##"Hur mycket drivmedel får du konsumera?" etc.): stringency (fuel 20/30/40/50 liter/month; meat
##0.6/1/1.4/1.8 kg/month), allowance allocation (Equal / Consumption-based / Needs-based),
##tradability (No / Yes), price for consumption (Higher than / Similar as / Lower than today), nature
##of cap (Constant / Gradually declining).
##Outcomes (wording not deposited; .dta labels only):
##  choice = f_sup / b_sup "Forced choice": exactly one proposal chosen per round (checked); the
##           authors analyse its complement f_opp/b_opp as "Pr(Reject proposal)", so the question
##           probably asked which proposal the respondent would rather oppose or support; not verifiable.
##  rating = f_rating / b_rating "Rating outcome": 1 Strongly against, 2 Somewhat against, 3 Neither
##           against nor in favor, 4 Somewhat in favor, 5 Strongly in favor.
##Derived outcomes (f_opp, f_rating_neg, f_accept*, f_oppose* and b_ twins) are dropped.
##trial_block_position = 1 if this experiment's block came first, 2 if second.
##The authors drop speeders (survey time < median/3, 64 respondents) and attention-check failures
##(q9 "how many wheels does a regular bicycle have" != 2, 8 more): analytic n 3,175. All 3,247 are kept
##here with cov_attention_pass (q9 == 2) and cov_duration_sec (whole survey, surveylengthinminutes*60).
##Covariates: cov_survey_weight (Weight, "VIKT"), cov_gender (Kön: Man -> male, Kvinna -> female, value
##labels), cov_age (Ålder), cov_region (Region: Storstad/Mellanbyggd/Glesbyggd), cov_nuts2 (label
##text), cov_education (q2 answer text, "Vill ej uppge" -> NA), cov_leftright (q3 answer text, "Vill ej
##uppge" -> NA). Kept as source codes (Swedish value labels in the .dta): cov_q1 (monthly income band,
##10 = Vill ej uppge), cov_q4 (climate worry, 5 = Vet ej), cov_q5 / cov_q6 (how often red meat / petrol
##car, 1 every day ... 6 never, 7 Vet ej), cov_q7_1..4 (trust in government / parties / Riksdag /
##agencies, 1-5, 6 Vet ej), cov_q8_1 / cov_q8_2 (fuel rationing / higher fuel tax as a proposal, 0-10),
##cov_q10_1..6 (fuel/meat rationing fair, intrusive, effective; 1-4, 5 Vet ej).
##Dropped: Municipality (kommun, fine-grained location), avslut (closing free-text comments; PII: some
##comments contain respondents' names and e-mail addresses), q11*/q12 (a separate "design your own
##alternative" question), and the authors' derived groupings (female, age_groups, pinc, educ, lr, cc,
##con_*, poltrust, fair_*, intrusive_*, effective_*, *_full).
##Count check: 32,470 rows = 3,247 x 5 x 2 per table.
##Spot check: applying the authors' two exclusions to this table leaves 3,175 respondents, and an OLS
##of 1 - choice (their f_opp) on the attributes gives the expected signs (fuel: 50 vs 20 liter/month
##-0.24, needs-based vs consumption-based allocation -0.12 in Pr(reject)); the article's figure values
##were not compared.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "conjoint_exp_DATA_LONG.dta"))
s <- as.data.table(zap_labels(k))
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
stopifnot(nrow(s) == 32470, uniqueN(s$respid) == 3247, s[, .N, respid][, all(N == 10)])
setorder(s, respid, pairing, new)
s[, profile := seq_len(.N), .(respid, pairing)]
stopifnot(all(s$profile %in% 1:2), s[, sum(f_sup), .(respid, pairing)][, all(V1 == 1)], s[, sum(b_sup), .(respid, pairing)][, all(V1 == 1)])
cv <- data.table(cov_survey_weight = s$Weight, cov_gender = c("male", "female")[s$Gender], cov_age = as.integer(s$Age),
                 cov_region = lab("Region")[order(k$respid, k$pairing, k$new)], cov_nuts2 = lab("Nuts2")[order(k$respid, k$pairing, k$new)],
                 cov_education = lab("q2")[order(k$respid, k$pairing, k$new)], cov_leftright = lab("q3")[order(k$respid, k$pairing, k$new)],
                 cov_attention_pass = as.integer(s$q9 == 2), cov_duration_sec = round(s$surveylengthinminutes * 60))
cv[cov_education == "Vill ej uppge", cov_education := NA][cov_leftright == "Vill ej uppge", cov_leftright := NA]
for (v in c("q1", "q4", "q5", "q6", paste0("q7_", 1:4), "q8_1", "q8_2", paste0("q10_", 1:6))) cv[, paste0("cov_", v) := as.integer(s[[v]])]
stopifnot(all(s$Gender %in% 1:2))
build <- function(p, first) {
  o <- order(k$respid, k$pairing, k$new)
  d <- data.table(id = as.integer(s$respid), task = as.integer(s$pairing), profile = s$profile,
                  choice = as.integer(s[[paste0(p, "_sup")]]), rating = as.integer(s[[paste0(p, "_rating")]]))
  for (v in c("stringency", "allocation", "trade", "price", "cap")) d[, paste0("attr_", v) := lab(paste0(p, "_", v))[o]]
  d[, trial_block_position := fifelse(s$hidblockorder == first, 1L, 2L)]
  d <- cbind(d, cv)
  stopifnot(!anyNA(d[, .(choice, rating, attr_stringency, attr_allocation, attr_trade, attr_price, attr_cap)]), all(d$rating %in% 1:5))
  setorder(d, id, task, profile); d
}
fwrite(build("f", 1), file.path(out, "lindgren_2026_fuel_rationing.csv"))
fwrite(build("b", 2), file.path(out, "lindgren_2026_meat_rationing.csv"))
