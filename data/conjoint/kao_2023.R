##Female-representation committee experiment (Jordan, Morocco, Tunisia) from
##Kao, K., Lust, E., Shalaby, M., & Weiss, C. M. (2024). Female representation and legitimacy: Evidence from a
##harmonized experiment in Jordan, Morocco, and Tunisia. American Political Science Review, 118(1), 495-503.
##https://doi.org/10.1017/S0003055423000357 (online April 2023)
##Replication data: Harvard Dataverse doi:10.7910/DVN/5GP5SI, CC0 1.0, no restricted files, no terms.
##Files read: data_for_analysis.rds (a data frame, 6,104 x 53), "codebook data_for_analysis.docx", README.txt,
##"sampling overview.txt", English.doc (the English questionnaire, an HTML-as-.doc file, read as text),
##the authors' 2.replication_maintext_figure2_5.R and 3.replication_appendix_figures_tables.R (as text only).
##Not read: the WVS and V-Dem files (descriptive figure 1), the Arabic questionnaires.
##Usage: Rscript kao_2023.R <raw dir> <output dir>   (raw dir holds data.rds)
##
##Phone surveys by local providers (Elka Consulting in Tunisia, One-to-One in Morocco, NAMA in Jordan; Nov-Dec
##2021 in Tunisia and Morocco, Jan-Mar 2022 in Jordan; interviews in Arabic, English questionnaire and
##Arabic versions in the deposit). Each respondent heard ONE one-minute radio-show excerpt (an audio clip, so
##presentation = unknown) about a legislative committee deciding on a policy. The questionnaire's experiment
##table (Survey Experiment 1) lists the randomized elements: committee of "8 male" or "4 male and 4 female"
##members; decision "supported" or "rejected"; issue "increase penalties for domestic violence" (or, in
##Jordan only, a second issue). The authors' main analyses use the experiments whose issue area is domestic
##violence (d_issue_dv == 1) pooled over the three countries with country fixed effects, and this table is
##exactly that sample: 4,554 respondents (Jordan 1,654, Morocco 1,464, Tunisia 1,436), one table with
##cov_country because the authors pool them and the attribute text is shared. The 1,550 Jordanian respondents
##who heard the other issue (d_issue_dv == 0) are NOT included: the data hold only the dummy and the
##questionnaire lists two candidate issues (littering penalties, equal pay), so the second issue's level text
##cannot be recovered; they are dropped.
##  attr_committee_gender   d_gen_bal: 0 = "all-male" (8 male members), 1 = "gender-balanced" (4 male and 4
##                          female members); questionnaire answer options.
##  attr_decision           d_pro_dec: 1 = "supported" (the committee decided to increase penalties for domestic
##                          violence: the pro-women decision, d_pro_women_dec = 1 in every such row; it is NA for rejections), 0 =
##                          "rejected" (the committee decided no changes should be made at this point).
##One vignette per respondent (task = profile = 1; id = row number, no respondent id in the file).
##Outcomes (1-4, the authors' numeric y_* columns, which match the factor labels; Don't know / refuse -> NA):
##  rating_right_all   "The committee made the right decision for all citizens" 1 strongly disagree .. 4 strongly agree
##  rating_right_women "... for women" same;  rating_right_men "... for men" same
##  rating_trust       "The committee can be trusted to make future decisions that are right for all citizens" 1-4 agree
##  rating_fair        "how fair was the decision making process?" 1 very unfair, 2 somewhat unfair, 3 somewhat fair, 4 very fair
##  rating_public_accept "How likely is the general public to accept the committee's decision to ...?" 1 not at all
##                     likely, 2 not likely, 3 likely, 4 very likely
##No opt-out (ratings only). Dropped: the authors' indices (y_right_dec_ix, y_att_comittee, sexism and norms
##indices and their na flags, treatment dummies, manipulation-check and endogenous-perception columns), the
##x_* dummies duplicating other columns, vignette_real. Covariates: cov_country, cov_gender (x_male /
##x_female), cov_age (x_age, years), cov_education (x_edu as worded; Don't know/refuse -> NA), cov_marital_status
##(demo_q8; Other kept), cov_household_income (demo_q7: how well household income covers needs, as worded; DK ->
##NA), cov_enumerator_male (x_male_en, 0/1).
##Count check: 4,501 of the 4,554 DV-experiment respondents have at least one outcome (53 have none and are dropped).
##The preprint reports 4,754 respondents overall; the deposit has 6,104 (4,554 in the DV experiments,
##the authors' main-analysis sample), so the preprint number is not matched; flagged, not fixed.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "data.rds")))
stopifnot(nrow(x) == 6104)
x <- x[d_issue_dv == 1]
stopifnot(nrow(x) == 4554, x[d_pro_dec == 1, all(d_pro_women_dec == 1)], x[, all(d_gen_bal %in% 0:1)], x[, all(d_pro_dec %in% 0:1)])
cl <- function(v) { y <- as.integer(x[[v]]); stopifnot(all(is.na(y) | y %in% 1:4)); y }
lab <- function(f, y, lv) { stopifnot(identical(match(as.character(f), lv), y) || all(is.na(f) == is.na(y))); y }
chk <- function(v, lv) { y <- as.character(x[[v]]); stopifnot(all(is.na(y) | y %in% lv)); y }
# the numeric y_* match the factor labels
stopifnot(all(as.integer(factor(x$right_dec_all, levels = c("Strongly Disagree", "Disagree", "Agree", "Strongly Agree"))) == x$y_right_dec_all, na.rm = TRUE),
          all(as.integer(factor(x$fair_comit, levels = c("Very unfair", "Somewhat unfair", "Somewhat fair", "Very fair"))) == x$y_fair_comit, na.rm = TRUE),
          all(as.integer(factor(x$public_accept, levels = c("Not at all likely", "Not likely", "Likely", "Very likely"))) == x$y_public_accept, na.rm = TRUE))
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L,
  rating_right_all = cl("y_right_dec_all"), rating_right_women = cl("y_right_dec_wm"), rating_right_men = cl("y_right_dec_mn"),
  rating_trust = cl("y_trust_comit"), rating_fair = cl("y_fair_comit"), rating_public_accept = cl("y_public_accept"),
  attr_committee_gender = ifelse(x$d_gen_bal == 1, "gender-balanced", "all-male"),
  attr_decision = ifelse(x$d_pro_dec == 1, "supported", "rejected"))
stopifnot(identical(x$x_male + x$x_female, rep(1, nrow(x))) || all(is.na(x$x_male) == is.na(x$x_female)))
age <- as.integer(x$x_age); age[age < 18 | age > 100] <- NA
nr <- function(y) { y[grepl("^Don.t [Kk]now", y)] <- NA; y }
cv <- data.table(id = d$id, cov_country = as.character(x$x_cntry),
  cov_gender = ifelse(x$x_male == 1, "male", ifelse(x$x_female == 1, "female", NA)), cov_age = age,
  cov_education = nr(chk("x_edu", levels(x$x_edu))), cov_marital_status = nr(chk("demo_q8", c("Single", "Married", "Divorced", "Other"))),
  cov_household_income = nr(as.character(x$demo_q7)), cov_enumerator_male = as.integer(x$x_male_en))
d <- d[!Reduce(`&`, lapply(c("rating_right_all", "rating_right_women", "rating_right_men", "rating_trust", "rating_fair", "rating_public_accept"), function(k) is.na(d[[k]])))]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kao_2023_committee_gender.csv"))
