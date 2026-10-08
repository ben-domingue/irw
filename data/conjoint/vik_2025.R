##Unelected-representative (activist Twitter profile) conjoint, Germany/Italy/Romania/Sweden, from
##Vik, A., de Wilde, P., Treib, O., & Aaroe, L. (2025). Venturing beyond the vote: Routes to
##feeling represented through unelected representation. British Journal of Political Science, 55,
##e102. https://doi.org/10.1017/S0007123425000080
##Replication data: Harvard Dataverse doi:10.7910/DVN/IHJVAM, CC0 1.0, no restricted files.
##File read: wideconjointdata.csv (one row per respondent). README.pdf and the authors'
##preprocessing script (read as text, not run) give the attribute codes; design facts and
##outcome wording from the article. longconjointdata.csv is NOT used: it is derived and has
##covariate NAs replaced by medians.
##Usage: Rscript vik_2025.R <raw dir> <output dir>
##
##8,279 Kantar panel respondents, July 2022: Germany 2,073, Italy 2,097, Romania 2,019, Sweden
##2,090 (quotas on gender, age, education); N matches the article. ONE TABLE with cov_country:
##the authors pool the countries (country-split models are robustness checks) and the
##attribute codes are common to all four. Each respondent saw 4 pairs (task 1-4, profile 1 =
##A, 2 = B) of fictitious activist Twitter profiles. Attributes:
##  gender, age: conveyed by a name (John/Mary Smith) and an edited face photo, not by text;
##  issue claim: a tweet taking a pro or anti position on climate, immigration or taxation;
##  personality: a self-description signalling high/low narcissism or agreeableness.
##The deposit holds only the authors' codes; attr_ values are the authors' level names from
##the preprocessing script (male/female; GenZ/Millenial/GenX/Boomer = shown aged 20/35/55/70;
##proclimate .. antitax; highnarcissism .. lowagreeableness). They are NOT the displayed text
##(the tweets, in each country's language, are in the article's appendix, not read).
##Outcomes (article wording, paraphrased): choice = which of the two profiles made the
##respondent feel more represented (forced, no opt-out; FFTRandom<t>_response 1 = A, 2 = B);
##rating = how represented the respondent felt by each profile, 1-7 (FFTRandom<t>_rankA/B;
##higher = more represented: chosen profiles average 4.7 vs 2.8). The article calls the scale
##7-point in Methods and six-point in Results; the data run 1-7.
##Randomization: the article says fully randomized with all combinations checked for realism;
##respondents were assigned one of 100 pre-drawn design versions (trial_version), and level
##shares are far from uniform and attributes are not independent (e.g. task 1 profile A:
##male 57%; GenZ 24% vs Boomer 29%; issue x personality cells from 74 to 736), so treat the
##design as restricted (observed). Pooled over tasks and profiles the level shares are uniform
##(each within 1.01x) and no attribute combination is absent; the dependence comes from the 100
##fixed versions (issue x personality cells 1,926-3,414; the two profiles of a pair share a
##gender in 32% of tasks).
##trial_version = source Version (1-100); trial_tweet_order = source TweetOrder (1/2; which tweet
##came first, not documented).
##Covariates (source codes; documented by the authors' script and the article only):
##cov_country 1=DE 2=IT 3=RO 4=SE; cov_age years; cov_gender text: source gender 1 = "male",
##2 = "female", 3 = "other" (analysis_routestorepresentation_forpub.R, Appendix C.3.5:
##recode_factor(Fgender, "1" = "male", "2" = "female", "3" = "other")); cov_education_code 1-3
##(codes kept: no labels in the deposit; low..high order assumed, not documented);
##cov_social_class 0-10; cov_ideology 1-10 (Q2_1, left-right); cov_political_interest 1-6
##(Q2_3); cov_tax_position, cov_immigration_position, cov_climate_position 1-10 (Q2_2a-c; the
##authors' comment: 1 = pro, 10 = anti); cov_social_trust (Q3_1); cov_personality_1..12 (Q1_1_*,
##short Big-Five items for agreeableness/openness/conscientiousness, keyed as in the authors'
##script) and cov_narcissism_1..4 (Q1_2_*); cov_efficacy_1..4 (Q4_1_*; 2 and 4 external, 1 and
##3 internal); cov_media_1..6 (Q4_5_*: radio, newspapers, TV, Facebook, YouTube, Twitter);
##cov_duration (as deposited; the unit is not documented in the deposit, values 5-5,235 with
##median 12 suggest minutes, so it is NOT converted to cov_duration_sec); cov_survey_weight
##(`weight`). No attention check is deposited (compcheck is constant 1); no repeated task.
##Spot check: rating on gender congruence (respondent gender = profile gender), SEs clustered by
##id: 0.052 (SE 0.015); the article reports 0.05 (SE 0.02) with controls.
##Dropped: Kantar Respondent_Serial (re-keyed to 1..N in file order), the other Q2/Q3/Q4 items
##(no wording in the deposit), compcheck (constant 1), pFAKT* weighting factors, the authors'
##derived scales and congruence variables.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
w <- fread(file.path(raw, "wideconjointdata.csv"))
stopifnot(!anyDuplicated(w$Respondent_Serial), nrow(w) == 8279, all(w$gender %in% 1:3))
w[, rid := .I]
L <- list(gender = c("male", "female"), age = c("GenZ", "Millenial", "GenX", "Boomer"),
          personality = c("highnarcissism", "lownarcissism", "highagreeableness", "lowagreeableness"),
          issue = c("proclimate", "anticlimate", "proimmigration", "antiimmigration", "protax", "antitax"))
an <- c(gender = "a1", age = "a2", personality = "a3", issue = "a4")
res <- list()
for (t in 1:4) for (p in 1:2) {
  ch <- w[[sprintf("FFTRandom%d_response", t)]]; rt <- w[[sprintf("FFTRandom%d_rank%s", t, c("A", "B")[p])]]
  stopifnot(all(ch %in% 1:2), all(rt %in% 1:7))
  d <- data.table(id = w$rid, task = t, profile = p, choice = as.integer(ch == p), rating = as.integer(rt))
  for (v in names(an)) { x <- w[[sprintf("%s_t%d_c%d", an[[v]], t, p)]]; stopifnot(all(x %in% seq_along(L[[v]]))); d[, paste0("attr_", v) := L[[v]][x]] }
  res[[length(res) + 1]] <- d
}
d <- rbindlist(res)
r <- data.table(id = w$rid, trial_version = w$Version, trial_tweet_order = w$TweetOrder, cov_country = w$country, cov_age = w$age,
                cov_gender = c("male", "female", "other")[w$gender], cov_education_code = w$education, cov_social_class = w$socialclass, cov_ideology = w$Q2_1,
                cov_political_interest = w$Q2_3, cov_tax_position = w$Q2_2_Q2_2a, cov_immigration_position = w$Q2_2_Q2_2b,
                cov_climate_position = w$Q2_2_Q2_2c, cov_social_trust = w$Q3_1)
for (i in 1:12) r[, paste0("cov_personality_", i) := w[[paste0("Q1_1_", i)]]]
for (i in 1:4) r[, paste0("cov_narcissism_", i) := w[[paste0("Q1_2_", i)]]]
for (i in 1:4) r[, paste0("cov_efficacy_", i) := w[[paste0("Q4_1_", i)]]]
for (i in 1:6) r[, paste0("cov_media_", i) := w[[paste0("Q4_5_", i)]]]
r[, cov_duration := w$duration][, cov_survey_weight := w$weight]
d <- merge(d, r, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating", "trial_version", "trial_tweet_order"))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vik_2025_unelected_representation.csv"))
