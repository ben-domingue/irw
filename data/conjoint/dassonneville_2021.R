##Representation-style vignette experiment (Canada) from
##Dassonneville, R., Blais, A., Sevi, S., & Daoust, J.-F. (2021). How citizens want their legislator
##to vote. Legislative Studies Quarterly, 46(2), 297-321. https://doi.org/10.1111/lsq.12275
##(open access; read, including the vignette in Figure 1)
##Replication data: Harvard Dataverse doi:10.7910/DVN/DQLTVJ, CC0 1.0. File read: representation.dta
##(original Stata file, value labels). Read as text only: representation.do.
##Usage: Rscript dassonneville_2021.R <dir holding the .dta> <output dir>
##
##2,001 Canadians eligible to vote (Ipsos online omnibus, 15-18 June 2018, representative on age,
##sex, region; article n = 2,001, matches) each read ONE vignette (task = 1, profile = 1); id = the
##Ipsos serial number re-keyed to the row number. Vignette (article Figure 1): an introduction on
##what MPs should do, then "Suppose the following situation. Please read the full vignette
##carefully:" and three bullets, each FOR or AGAINST (full 2 x 2 x 2, scenarios 1-8 each shown to
##249-251 respondents). Level text is the full bullet sentence as displayed:
##  attr_mp_view    "Your Member of Parliament is personally FOR / AGAINST reducing the number of
##                  immigrants by 10%."
##  attr_majority   "The majority of citizens in your riding are FOR / AGAINST reducing the number of
##                  immigrants by 10%."
##  attr_promise    "In the previous election, your Member of Parliament promised to vote FOR /
##                  AGAINST reducing the number of immigrants by 10%."
##Scenario -> levels from the authors' do-file (pos_dep, pos_maj, promise recodes of
##ROT_SCENARIO_YQ_1-8). The order of the three bullets was randomized per respondent (ROT_ORDER_YQ_1-6,
##"Marker to rotate the question texts A, B and C"; the deposit does not say which bullet is A, B or
##C), so the order is kept as text in trial_bullet_order ("ABC", "ACB", ...) rather than as attrpos_.
##Outcome: rating = YQ1 "Suppose the following situation. Please read the full vignette carefully.
##..." (label truncated in the source) asking how the MP should vote; 1 = "For reducing the number of
##immigrants", 2 = "Against reducing the number of immigrants", stored raw (the authors recode to
##vote_for = 1/0). Not a choice: one profile, and the answer is a position, not acceptance.
##Dropped: YQ2, a 0-10 follow-up whose wording survives only as "You just indicated that you feel your
##Member of Parliament should vote ..." (meaning not recoverable).
##Covariates (answer text from the value labels): cov_gender (Male/Female -> male/female), cov_age
##(resp_age, years), cov_education (CAEDU2), cov_province (HCAL_Region1_CA), cov_household_income
##(USHHI3; "Prefer not to answer" -> NA), cov_immigration_view (YQ3, the respondent's own view, asked
##after the vignette), cov_vote_intention (YQ4, federal vote intention), cov_survey_weight (Weightvar;
##the article's analyses are weighted). Dropped: ethnic-origin dummies, household, marital and
##employment items, derived variables.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "representation.dta")))
stopifnot(nrow(s) == 2001L, uniqueN(s$Respondent_Serial) == 2001L)
sc <- as.matrix(s[, paste0("ROT_SCENARIO_YQ_", 1:8), with = FALSE]); stopifnot(all(rowSums(sc) == 1))
ro <- as.matrix(s[, paste0("ROT_ORDER_YQ_", 1:6), with = FALSE]); stopifnot(all(rowSums(ro) == 1))
scen <- max.col(sc); ord <- c("ABC", "ACB", "BAC", "BCA", "CAB", "CBA")[max.col(ro)]
fa <- function(x) fifelse(x, "FOR", "AGAINST")
lab <- function(x, na = character()) { v <- trimws(as.character(as_factor(x, levels = "labels"))); v[v %in% na] <- NA; v }
stopifnot(s$YQ1 %in% 1:2)
d <- data.table(id = seq_len(nrow(s)), task = 1L, profile = 1L, rating = as.integer(s$YQ1),
  attr_mp_view = paste("Your Member of Parliament is personally", fa(scen %in% c(1, 3, 4, 6)), "reducing the number of immigrants by 10%."),
  attr_majority = paste("The majority of citizens in your riding are", fa(scen %in% c(1, 2, 4, 7)), "reducing the number of immigrants by 10%."),
  attr_promise = paste("In the previous election, your Member of Parliament promised to vote", fa(scen %in% c(1, 2, 3, 5)), "reducing the number of immigrants by 10%."),
  trial_bullet_order = ord,
  cov_gender = c(Male = "male", Female = "female")[lab(s$resp_gender)], cov_age = as.integer(s$resp_age),
  cov_education = lab(s$CAEDU2), cov_province = lab(s$HCAL_Region1_CA),
  cov_household_income = lab(s$USHHI3, "Prefer not to answer"), cov_immigration_view = lab(s$YQ3),
  cov_vote_intention = lab(s$YQ4), cov_survey_weight = as.numeric(s$Weightvar))
stopifnot(!anyNA(d$cov_gender), uniqueN(d[, .(attr_mp_view, attr_majority, attr_promise)]) == 8L, d$cov_age %in% 18:105)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dassonneville_2021_mp_vote.csv"))
